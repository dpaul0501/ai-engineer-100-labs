# Degrees, the cost of a two-step walk, and capping hubs.
from collections import Counter
import heapq, math
from common import (load_edges, adjacency, time_split, recall_at_k, six,
                    YOU, BEN, CHLOE, DEV, ESHA, FARID)

def pct(values, q):
    """Nearest-rank percentile: the smallest value that at least q% of the values are <= to."""
    s = sorted(values)
    return s[max(0, math.ceil(q / 100 * len(s)) - 1)]

def work(adj, u):
    """List entries a two-step walk from u reads: the sum of u's friends' degrees."""
    return sum(len(adj[f]) for f in adj[u])

def suggest_capped(adj, u, k=10, cap=None):
    """Top k by mutual friends, but skip any friend with more than `cap` friends.
    Returns (top k, entries read). Ties: smaller id first."""
    count, read = Counter(), 0
    for f in adj[u]:
        if cap is not None and len(adj[f]) > cap:
            continue                          # a hub: the longest list, the weakest hint
        read += len(adj[f])
        for v in adj[f]:
            if v != u and v not in adj[u]:
                count[v] += 1
    return heapq.nsmallest(k, count, key=lambda v: (-count[v], v)), read

deg = [len(s) for s in six]
assert deg == [2, 4, 4, 1, 2, 1] and sum(deg) == 2 * 7                 # handshake: 2 x 7 lines
assert work(six, YOU) == 8                                             # Ben 4 + Chloe 4
assert sum(work(six, u) for u in range(6)) == sum(d * d for d in deg)  # 42 both ways
assert suggest_capped(six, YOU, cap=3) == ([], 0)                      # Ben and Chloe both skipped

# LeetCode 997 · Find the Town Judge: in-degree n - 1, out-degree 0
def findJudge(n, trust):
    score = [0] * (n + 1)
    for a, b in trust:
        score[a] -= 1                         # an arrow out disqualifies a
        score[b] += 1                         # an arrow in counts for b
    return next((p for p in range(1, n + 1) if score[p] == n - 1), -1)

assert findJudge(2, [[1, 2]]) == 2
assert findJudge(3, [[1, 3], [2, 3]]) == 3
assert findJudge(3, [[1, 3], [2, 3], [3, 1]]) == -1

if __name__ == "__main__":
    edges = load_edges()
    G = adjacency(edges)
    n = len(G)
    d = [len(s) for s in G]
    print("degree: mean %.1f median %d p90 %d p99 %d max %d min %d" %
          (sum(d) / n, pct(d, 50), pct(d, 90), pct(d, 99), max(d), min(d)))
    print("share of users below the mean: %.1f%%" % (100 * sum(x < sum(d) / n for x in d) / n))
    W = [work(G, u) for u in range(n)]
    sq = sum(x * x for x in d)
    assert sum(W) == sq
    print("work per request: mean %.0f median %d p99 %d max %d; sum of deg^2 %d; 20*20 = 400" %
          (sum(W) / n, pct(W, 50), pct(W, 99), max(W), sq))
    print("friend-of-a-random-friend degree (sum d^2 / sum d): %.1f" % (sq / sum(d)))
    top = sorted(range(n), key=lambda v: -d[v])
    for share in (0.001, 0.01, 0.10):
        t = top[:int(share * n)]
        print("top %.1f%% (%d users, degree >= %d): %.1f%% of friend ends, %.1f%% of all two-step work" %
              (100 * share, len(t), d[t[-1]], 100 * sum(d[v] for v in t) / sum(d), 100 * sum(d[v] ** 2 for v in t) / sq))
    print("largest hub alone: degree %d, %.1f%% of the work" % (d[top[0]], 100 * d[top[0]] ** 2 / sq))
    # capping hubs: cost on the week's graph, quality on the time split
    past, future, truth = time_split(edges)
    P = adjacency(past)
    print("evaluated users", len(truth))
    print("cap | users skipped | mean work | p99 work | max work | recall@10 (time split)")
    for cap in (None, 1000, 500, 200, 100, 50):
        reads = [suggest_capped(G, u, cap=cap)[1] for u in range(n)]
        ranked = {u: suggest_capped(P, u, cap=cap)[0] for u in truth}
        skipped = sum(x > cap for x in d) if cap else 0
        print("%s | %d | %.0f | %d | %d | %.4f" % (cap, skipped, sum(reads) / n, pct(reads, 99), max(reads),
                                                  recall_at_k(ranked, truth)))
