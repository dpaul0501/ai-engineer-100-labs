# Personalised PageRank (random walk with restart) by power iteration, on the time split.
import numpy as np
from common import load_edges, adjacency, time_split, recall_at_k, six, YOU, BEN, CHLOE, DEV, ESHA, FARID
from scores import two_hop_scores, top_k

def edge_arrays(adj):
    """Both directions of every friendship as two arrays, plus everyone's degree."""
    src = np.array([f for f in range(len(adj)) for _ in adj[f]], dtype=np.int64)
    dst = np.array([v for f in range(len(adj)) for v in adj[f]], dtype=np.int64)
    deg = np.array([len(s) for s in adj], dtype=np.float64)
    return src, dst, deg

def ppr(src, dst, deg, u, alpha=0.3, rounds=30):
    """Share of time a walker spends at each person when, at every step, it goes
    home to u with probability alpha and otherwise moves to a random friend."""
    n = len(deg)
    home = np.zeros(n); home[u] = 1.0
    share = np.divide(1.0, deg, out=np.zeros(n), where=deg > 0)   # 1 / degree
    x = home.copy()
    for _ in range(rounds):
        moved = np.bincount(dst, weights=x[src] * share[src], minlength=n)  # one step for everyone
        x = alpha * home + (1 - alpha) * moved
    return x

def ppr_top_k(adj, x, u, k=10):
    """Best k non-friends by walk share; ties go to the smaller id."""
    x = x.copy()
    x[u] = -1.0
    x[list(adj[u])] = -1.0                       # yourself and your friends are not candidates
    order = np.lexsort((np.arange(len(x)), -x))  # by -share, then by id
    return [int(v) for v in order[:k] if x[v] > 0]

# the six people, alpha = 0.3
s6 = edge_arrays(six)
x = ppr(*s6, YOU, rounds=200)
assert abs(x.sum() - 1) < 1e-12
assert [round(v, 3) for v in x] == [0.380, 0.230, 0.230, 0.040, 0.080, 0.040]
assert ppr_top_k(six, x, YOU) == [ESHA, DEV, FARID]
# Ben gains 20 more friends (ids 6..25): Dev's only mutual friend is now a hub, Farid's is not
big = adjacency([(a, b) for a, b in [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 4), (2, 5)]] +
                [(BEN, w) for w in range(6, 26)], 26)
xb = ppr(*edge_arrays(big), YOU, rounds=200)
assert round(xb[DEV], 3) == 0.008 and round(xb[FARID], 3) == 0.028 and round(xb[ESHA], 3) == 0.036
assert ppr_top_k(big, xb, YOU, 3) == [ESHA, FARID, DEV]

if __name__ == "__main__":
    edges = load_edges()
    past, future, truth = time_split(edges)
    P = adjacency(past)
    src, dst, deg = edge_arrays(P)
    print("directed entries per round", len(src))
    # convergence on one user, against 300 rounds
    u0 = next(iter(truth))
    ref = ppr(src, dst, deg, u0, rounds=300)
    for t in (1, 5, 10, 20, 30):
        print("rounds %2d: total error %.2e, guaranteed at most %.2e" %
              (t, np.abs(ppr(src, dst, deg, u0, rounds=t) - ref).sum(), 2 * 0.7 ** t))
    users = list(truth)
    base = {u: top_k(two_hop_scores(P, u)["mutual"]) for u in users}
    for alpha in (0.15, 0.3, 0.5):
        ranked, beyond = {}, 0
        for u in users:
            ranked[u] = ppr_top_k(P, ppr(src, dst, deg, u, alpha=alpha), u)
            two = set().union(*(P[f] for f in P[u])) if P[u] else set()
            beyond += sum(1 for v in ranked[u] if v in truth[u] and v not in two)
        r = recall_at_k(ranked, truth)
        print("alpha %.2f: recall@10 %.4f; future friends found beyond two steps %d" % (alpha, r, beyond))
        if alpha == 0.3:
            pu = [len(truth[u].intersection(ranked[u])) / len(truth[u]) for u in users]
            pb = [len(truth[u].intersection(base[u])) / len(truth[u]) for u in users]
            d = np.array(pu) - np.array(pb)
            print("ppr(0.3) minus mutual: %+.4f (paired standard error %.4f)" % (d.mean(), d.std(ddof=1) / np.sqrt(len(d))))
            hits = sum(len(truth[u].intersection(ranked[u])) for u in users)
            print("ppr(0.3) hits in top 10:", hits)
    print("mutual recall@10 %.4f" % recall_at_k(base, truth))
    print("updates per user, 30 rounds:", 30 * len(src))
