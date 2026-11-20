# At scale: split the graph across p machines. How many two-step reads leave the machine?
# Then: "think like a vertex" (Pregel-style rounds) for BFS and personalised PageRank.
from collections import Counter
import math, random
import numpy as np
from common import load_edges, adjacency, six, YOU, DEV, FARID
from bfs import bfs
from ppr import ppr, edge_arrays

def hash_partition(n, p):
    """Machine of user u: a hash of the id, so users spread evenly and at random."""
    return [(u * 2654435761 % 2**32) * p >> 32 for u in range(n)]   # multiplicative hash, top bits

def edge_cut(adj, part):
    """Share of friendships whose two people live on different machines."""
    cut = sum(1 for u in range(len(adj)) for v in adj[u] if u < v and part[u] != part[v])
    return cut / (sum(len(s) for s in adj) // 2)

def remote_read_share(adj, part, replicated=frozenset()):
    """A two-step walk for u runs on u's machine and reads each friend f's list (deg f entries).
    Share of those entries that live on another machine. Lists in `replicated` are on every machine."""
    remote = total = 0
    for u in range(len(adj)):
        for f in adj[u]:
            total += len(adj[f])
            if part[f] != part[u] and f not in replicated:
                remote += len(adj[f])
    return remote / total

def locality_partition(adj, p, rounds=10, slack=1.03, seed=0):
    """Start from the hash partition; repeatedly move each user to the machine where most
    of their friends live, if that machine is not full (balanced label propagation)."""
    n, rng = len(adj), random.Random(seed)
    part = hash_partition(n, p)
    size, cap = Counter(part), math.ceil(slack * n / p)
    for _ in range(rounds):
        for u in rng.sample(range(n), n):
            c = Counter(part[v] for v in adj[u])
            best = max(c, key=lambda q: (c[q], -q)) if c else part[u]
            if c[best] > c[part[u]] and size[best] < cap:
                size[part[u]] -= 1; size[best] += 1; part[u] = best
    return part

# --- Pregel-style rounds: every vertex runs the same small program, talking only to neighbours.
def pregel_bfs(adj, s, part=None):
    """Round r: vertices reached in round r - 1 message their friends; a vertex that hears
    for the first time sets dist = r. Returns dist, rounds, messages, cross-machine messages."""
    dist, frontier, r, msgs, cross = {s: 0}, [s], 0, 0, 0
    while frontier:
        r += 1
        inbox = set()
        for x in frontier:                          # each active vertex sends to all its friends
            for y in adj[x]:
                msgs += 1
                cross += part is not None and part[x] != part[y]
                inbox.add(y)
        frontier = [y for y in inbox if y not in dist]
        for y in frontier:
            dist[y] = r
    return dist, r - 1, msgs, cross

def pregel_ppr(adj, u, alpha=0.3, rounds=30):
    """Each round every vertex sends value / degree to each friend, then sets
    value = alpha * [it is u] + (1 - alpha) * (sum of what it received)."""
    n = len(adj)
    val = [1.0 if v == u else 0.0 for v in range(n)]
    for _ in range(rounds):
        inbox = [0.0] * n
        for x in range(n):                          # "send" phase, one message per friendship end
            if adj[x]:
                share = val[x] / len(adj[x])
                for y in adj[x]:
                    inbox[y] += share
        val = [alpha * (v == u) + (1 - alpha) * inbox[v] for v in range(n)]   # "compute" phase
    return val

d, rounds, msgs, _ = pregel_bfs(six, YOU)
assert d == bfs(six, YOU) and rounds == 2 and msgs == 14
assert np.allclose(pregel_ppr(six, YOU), ppr(*edge_arrays(six), YOU))
assert edge_cut(six, [0, 0, 0, 0, 0, 0]) == 0 and remote_read_share(six, [0] * 6) == 0
assert edge_cut(six, [0, 0, 1, 0, 0, 1]) == 3 / 7      # You-Chloe, Ben-Chloe, Chloe-Esha cross

if __name__ == "__main__":
    G = adjacency(load_edges())
    n = len(G)
    deg = [len(s) for s in G]
    hubs = frozenset(sorted(range(n), key=lambda v: -deg[v])[:100])     # the top 1%
    print("p | hash: edge cut, remote reads, remote reads with top-1% lists copied everywhere"
          " | locality: edge cut, remote reads, largest machine / average")
    for p in (2, 4, 8, 16, 32):
        h = hash_partition(n, p)
        loc = locality_partition(G, p)
        print("%d | %.3f %.3f %.3f | %.3f %.3f %.3f | (p-1)/p = %.3f" % (
            p, edge_cut(G, h), remote_read_share(G, h), remote_read_share(G, h, hubs),
            edge_cut(G, loc), remote_read_share(G, loc), max(Counter(loc).values()) / (n / p), (p - 1) / p))
    hub_entries = sum(deg[v] for v in hubs)
    print("top-1%% lists: %d of %d entries (%.1f%%); copying them to all 8 machines adds %.0f%% storage" %
          (hub_entries, sum(deg), 100 * hub_entries / sum(deg), 100 * 7 * hub_entries / sum(deg)))
    h8 = hash_partition(n, 8)
    print("hash p=8 users per machine: min %d max %d" % (min(Counter(h8).values()), max(Counter(h8).values())))
    load = [sum(deg[u] for u in range(n) if h8[u] == q) for q in range(8)]
    print("hash p=8 friend-list entries per machine: min %d max %d" % (min(load), max(load)))
    dist, rounds, msgs, cross = pregel_bfs(G, 8604, h8)
    print("pregel BFS from 8604: rounds %d, messages %d (= 2 x friendships), cross-machine at p=8: %d (%.3f)" %
          (rounds, msgs, cross, cross / msgs))
    assert dist == bfs(G, 8604) and msgs == sum(deg)
    print("pregel PageRank: messages per round", sum(deg), "; 30 rounds", 30 * sum(deg))
