# Triangles, clustering, and triadic closure measured from the order friendships formed.
import math, random
from common import load_edges, adjacency, six, YOU, BEN, CHLOE, DEV, ESHA, FARID

def count_triangles(adj):
    """Each triangle once, at its least popular corner (rank by degree, ties by id)."""
    rank = {v: (len(adj[v]), v) for v in range(len(adj))}
    up = [{w for w in adj[v] if rank[w] > rank[v]} for v in range(len(adj))]
    return sum(len(up[u] & up[v]) for u in range(len(adj)) for v in up[u])

def clustering(adj):
    """Average local clustering (over users with >= 2 friends) and the pooled share
    of closed wedges (transitivity). A wedge x - v - y is closed if x and y are friends."""
    local, closed, wedges = [], 0, 0
    for v, nv in enumerate(adj):
        d = len(nv)
        if d < 2:
            continue
        t = sum(len(nv & adj[x]) for x in nv) // 2      # friend-friend pairs among v's friends
        local.append(t / (d * (d - 1) / 2))
        closed += t; wedges += d * (d - 1) // 2
    return sum(local) / len(local), closed / wedges

def closed_at_birth(edges, n):
    """For each friendship in formation order: how many mutual friends its two people
    had just before it formed (each one is a triangle the new line closes)."""
    adj, out = [set() for _ in range(n)], []
    for u, v, _ in edges:
        out.append(len(adj[u] & adj[v]))
        adj[u].add(v); adj[v].add(u)
    return out

assert count_triangles(six) == 2                         # {You, Ben, Chloe}, {Ben, Chloe, Esha}
avg, pooled = clustering(six)
assert abs(avg - (1 + 1/3 + 1/3 + 1) / 4) < 1e-12 and abs(pooled - 6 / 14) < 1e-12
from common import SIX
assert sum(closed_at_birth([(a, b, t) for t, (a, b) in enumerate(SIX)], 6)) == 2

# LeetCode 1761 · Minimum Degree of a Connected Trio
def minTrioDegree(n, edges):
    adj = [set() for _ in range(n + 1)]
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    deg = [len(s) for s in adj]
    up = [[w for w in adj[v] if (deg[w], w) > (deg[v], v)] for v in range(n + 1)]
    best = math.inf
    for u in range(1, n + 1):
        for v in up[u]:
            for w in up[v]:
                if w in adj[u]:                           # u, v, w is a trio, found once
                    best = min(best, deg[u] + deg[v] + deg[w] - 6)
    return -1 if best == math.inf else best

assert minTrioDegree(6, [[1, 2], [1, 3], [3, 2], [4, 1], [5, 2], [3, 6]]) == 3
assert minTrioDegree(7, [[1, 3], [4, 1], [4, 3], [2, 5], [5, 6], [6, 7], [7, 5], [2, 6]]) == 0

if __name__ == "__main__":
    edges = load_edges()
    n = 10_000
    G = adjacency(edges)
    T = count_triangles(G)
    avg, pooled = clustering(G)
    m = len(edges)
    p = m / (n * (n - 1) / 2)
    print("triangles", T, "average clustering %.4f pooled %.4f; random graph same density %.4f" % (avg, pooled, p))
    print("average clustering / random: %.0fx" % (avg / p))
    born = closed_at_birth(edges, n)
    assert sum(born) == T                                 # every triangle is closed by its last line
    print("friendships that closed >= 1 triangle when they formed: %.1f%%" % (100 * sum(b > 0 for b in born) / m))
    # by tenth of the history, against random non-friend pairs at the start of that tenth
    rng = random.Random(0)
    adj = [set() for _ in range(n)]
    print("tenth | new friendships closing a triangle | random non-friend pairs with a mutual friend | ratio")
    for k in range(10):
        lo, hi = k * m // 10, (k + 1) * m // 10
        hits = tries = 0
        while tries < 100_000:                            # random pairs, judged on the graph so far
            a, b = rng.randrange(n), rng.randrange(n)
            if a == b or b in adj[a]:
                continue
            tries += 1; hits += bool(adj[a] & adj[b])
        closing = sum(x > 0 for x in born[lo:hi]) / (hi - lo)
        base = hits / tries
        print("%d | %.1f%% | %.2f%% | %s" % (k + 1, 100 * closing, 100 * base, "%.0fx" % (closing / base) if base else "-"))
        for u, v, _ in edges[lo:hi]:
            adj[u].add(v); adj[v].add(u)
