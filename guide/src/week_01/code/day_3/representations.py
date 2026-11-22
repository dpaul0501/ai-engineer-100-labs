# Three ways to hold the same graph, and what each costs in memory.
import sys
import numpy as np
from common import load_edges, adjacency, six, SIX, YOU, BEN, CHLOE, DEV, ESHA, FARID

def edge_list(adj):
    """Every friendship once, as (smaller id, larger id)."""
    return [(u, v) for u in range(len(adj)) for v in sorted(adj[u]) if u < v]

def matrix(adj):
    """n x n table of 0/1: A[u, v] = 1 when u and v are friends."""
    n = len(adj)
    A = np.zeros((n, n), dtype=np.uint8)
    for u in range(n):
        for v in adj[u]:
            A[u, v] = 1
    return A

def dict_of_dicts(pairs):
    """u -> {friend: when they became friends}, with pairs given in the order they formed."""
    G = {}
    for t, (u, v, *_) in enumerate(pairs):
        G.setdefault(u, {})[v] = t      # each friendship is written twice,
        G.setdefault(v, {})[u] = t      # once in each person's dict
    return G

def csr(n, pairs):
    """Adjacency lists packed into two arrays: u's friends are indices[indptr[u]:indptr[u+1]]."""
    deg = np.zeros(n, dtype=np.int64)
    for u, v in pairs:
        deg[u] += 1; deg[v] += 1
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(deg, out=indptr[1:])                  # where each list starts
    fill, indices = indptr[:-1].copy(), np.empty(indptr[-1], dtype=np.int32)
    for u, v in pairs:                              # write each friendship into both lists
        indices[fill[u]] = v; fill[u] += 1
        indices[fill[v]] = u; fill[v] += 1
    for u in range(n):
        indices[indptr[u]:indptr[u + 1]].sort()
    return indptr, indices

def python_bytes(obj, seen=None):
    """Bytes Python spends on obj and everything inside it (each object counted once)."""
    seen = set() if seen is None else seen
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(python_bytes(k, seen) + python_bytes(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, set)):
        size += sum(python_bytes(x, seen) for x in obj)
    return size

# the six people, three ways
assert edge_list(six) == SIX[:3] + [(1, 3), (1, 4), (2, 4), (2, 5)]
A = matrix(six)
assert A.sum() == 14 and (A == A.T).all()           # each friendship ticked twice
assert list(np.flatnonzero(A[CHLOE])) == [YOU, BEN, ESHA, FARID]
D = dict_of_dicts(edge_list(six))
assert D[BEN] == {YOU: 0, CHLOE: 2, DEV: 3, ESHA: 4}   # Ben's friends, and when each friendship arrived
assert ESHA in D[BEN] and DEV not in D[CHLOE]           # one hash lookup each
assert sum(len(f) for f in D.values()) == 14
indptr, indices = csr(6, edge_list(six))
assert list(indptr) == [0, 2, 6, 10, 11, 13, 14]
assert list(indices) == [1, 2, 0, 2, 3, 4, 0, 1, 4, 5, 1, 1, 2, 2]
assert list(indices[indptr[BEN]:indptr[BEN + 1]]) == [YOU, CHLOE, DEV, ESHA]

if __name__ == "__main__":
    G = adjacency(load_edges())
    n, m = len(G), sum(len(s) for s in G) // 2
    print("users", n, "friendships", m, "list entries", 2 * m)
    ip, ix = csr(n, edge_list(G))
    print("adjacency list (CSR): indptr bytes", ip.nbytes, "indices bytes", ix.nbytes, "total", ip.nbytes + ix.nbytes)
    sets = python_bytes(G)                                   # list of sets: what adjacency() returns
    dod = python_bytes(dict_of_dicts(load_edges()))         # dict of dicts, value = formation order
    print("hash sets (list of sets) bytes", sets, "ratio to CSR %.1f" % (sets / (ip.nbytes + ix.nbytes)))
    print("dict of dicts bytes", dod, "ratio to CSR %.1f" % (dod / (ip.nbytes + ix.nbytes)))
    assert sets > 10 * (ip.nbytes + ix.nbytes) and dod > 10 * (ip.nbytes + ix.nbytes)
    el = np.array(edge_list(G), dtype=np.int32)
    print("edge list bytes (two 4-byte ids)", el.nbytes)
    print("matrix cells", n * n, "bytes at 1 bit", n * n // 8, "bytes at 1 byte", n * n)
    print("share of matrix cells that are 1: %.4f%%" % (100 * 2 * m / (n * n)))
    print("mean cells scanned per friend found in a matrix row: %.0f" % (n / (2 * m / n)))
    # hypothetical: a billion users with 300 friends each
    N, d = 10**9, 300
    M = N * d // 2
    print("billion: friendships", M, "list entries", 2 * M)
    print("billion: matrix bytes at 1 bit", N * N // 8)
    print("billion: CSR bytes, 4-byte ids", 2 * M * 4 + 8 * (N + 1), "8-byte ids", 2 * M * 8 + 8 * (N + 1))
    print("billion: edge list bytes, 8-byte ids", M * 16)
    print("2^32 =", 2**32)
