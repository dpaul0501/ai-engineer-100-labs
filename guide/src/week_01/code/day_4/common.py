# Shared helpers for Day 4: the time split, candidates and pair features, logistic regression,
# boosted trees and the ranking metrics. NumPy only.
import csv
import math
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data"
N_USERS = 10_000
TRAIN_CUT, TEST_CUT, END = 60_000, 80_000, 100_000   # train: look 0-59,999, predict 60,000-79,999
                                                     # test:  look 0-79,999, predict 80,000-99,999
FEATURES = ["log_cn", "jaccard", "log_aa", "log_ra", "shared_groups", "same_city", "log_du", "log_dv"]


# ---------------------------------------------------------------- data
def load_edges():
    with open(DATA / "edges.csv") as f:
        rows = list(csv.reader(f))[1:]
    e = np.array([[int(u), int(v), int(t)] for u, v, t in rows], dtype=np.int64)
    assert (e[:, 2] == np.arange(len(e))).all()
    return e[:, :2]

def load_users():
    city, G = np.zeros(N_USERS, np.int64), np.zeros((N_USERS, 200), np.float32)
    with open(DATA / "users.csv") as f:
        for user, c, g in list(csv.reader(f))[1:]:
            city[int(user)] = int(c)
            G[int(user), [int(x) for x in g.split()]] = 1
    return city, G

class Graph:
    """Friend lists of the first `cut` friendships, as sorted arrays (CSR)."""
    def __init__(self, edges, cut, n=N_USERS):
        e = edges[:cut]
        both = np.r_[e, e[:, ::-1]]
        both = both[np.lexsort((both[:, 1], both[:, 0]))]
        self.n = n
        self.deg = np.bincount(both[:, 0], minlength=n)
        self.indptr = np.r_[0, np.cumsum(self.deg)]
        self.indices = both[:, 1]
        d = self.deg.astype(float)
        self.w_aa = np.where(d >= 2, 1 / np.log(np.maximum(d, 2)), 0.0)   # z with one friend reaches only u
        self.w_ra = np.where(d >= 1, 1 / np.maximum(d, 1), 0.0)

    def nbrs(self, u):
        return self.indices[self.indptr[u]:self.indptr[u + 1]]

    def two_hop(self, u):
        """Candidates of u (friends of friends, minus u and u's friends) with mutual, AA and RA counts."""
        F = self.nbrs(u)
        if len(F) == 0:
            return np.empty(0, np.int64), np.empty(0), np.empty(0), np.empty(0)
        reach = np.concatenate([self.nbrs(z) for z in F])
        via = np.repeat(F, self.deg[F])
        cn = np.bincount(reach, minlength=self.n).astype(float)
        aa = np.bincount(reach, weights=self.w_aa[via], minlength=self.n)
        ra = np.bincount(reach, weights=self.w_ra[via], minlength=self.n)
        cn[u] = 0; cn[F] = 0
        c = np.flatnonzero(cn)                       # sorted ids
        return c, cn[c], aa[c], ra[c]

def future_friends(edges, start, stop):
    truth = {}
    for u, v in edges[start:stop]:
        truth.setdefault(int(u), set()).add(int(v)); truth.setdefault(int(v), set()).add(int(u))
    return truth

def pair_features(g, city, G, u, c, cn, aa, ra):
    du, dv = g.deg[u], g.deg[c]
    X = np.empty((len(c), len(FEATURES)), np.float32)
    X[:, 0] = np.log1p(cn)
    X[:, 1] = cn / (du + dv - cn)                    # |N(u) ∪ N(v)| = du + dv - cn
    X[:, 2] = np.log1p(aa)
    X[:, 3] = np.log1p(ra)
    X[:, 4] = G[c] @ G[u]
    X[:, 5] = city[c] == city[u]
    X[:, 6] = np.log1p(du)
    X[:, 7] = np.log1p(dv)
    return X

def build(edges, city, G, look, start, stop):
    """Every candidate pair of every user who gains a friend in [start, stop), with features from the
    first `look` friendships and label 1 if the pair became friends in the window."""
    g = Graph(edges, look)
    truth = future_friends(edges, start, stop)
    users = np.array(sorted(truth))
    Xs, ys, us, vs, cns = [], [], [], [], []
    for u in users:
        c, cn, aa, ra = g.two_hop(u)
        Xs.append(pair_features(g, city, G, u, c, cn, aa, ra))
        ys.append(np.isin(c, list(truth[u])))
        us.append(np.full(len(c), u)); vs.append(c); cns.append(cn)
    return dict(g=g, truth=truth, users=users, X=np.concatenate(Xs), y=np.concatenate(ys),
                u=np.concatenate(us), v=np.concatenate(vs), cn=np.concatenate(cns))

def sample_negatives(D, r=0.05, seed=0):
    """Keep every positive and each negative with probability r."""
    keep = D["y"] | (np.random.default_rng(seed).random(len(D["y"])) < r)
    return D["X"][keep], D["y"][keep].astype(float)

def fit_lr_ranker(Xtr, ytr, lam=1e-3, iters=3000):
    """Standardise with training statistics, fit, and return a scoring function (logit)."""
    s = fit_scaler(Xtr)
    w = train_logreg(scale(Xtr, s), ytr, lam, iters)
    return w, s, (lambda X: logit_lr(w, scale(X, s)))


# ---------------------------------------------------------------- logistic regression
def sigmoid(z):
    return 0.5 * (1.0 + np.tanh(0.5 * z))           # = 1/(1+e^-z), no overflow

def log_loss(p, y, eps=1e-12):
    return float(-np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps)))

def loss_grad(w, X, y, lam):
    """Mean log loss + (lam/2)|w|^2 (bias excluded) and its gradient. X has a leading column of 1s."""
    p = sigmoid(X @ w)
    reg = np.r_[0.0, w[1:]]
    return log_loss(p, y) + 0.5 * lam * reg @ reg, X.T @ (p - y) / len(y) + lam * reg

def train_logreg(X, y, lam=1e-3, iters=3000):
    """Full-batch gradient descent, step 1/L with L = ||X||^2/(4n) + lam: every step goes downhill."""
    X = np.c_[np.ones(len(X)), X]
    L = np.linalg.norm(X, 2) ** 2 / (4 * len(y)) + lam
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        w -= loss_grad(w, X, y, lam)[1] / L
    return w

def fit_scaler(X):
    mu, sd = X.mean(0), X.std(0)
    return mu, np.where(sd > 0, sd, 1.0)

def scale(X, s):
    return (X - s[0]) / s[1]

def logit_lr(w, X):
    return w[0] + X @ w[1:]


# ---------------------------------------------------------------- boosted trees (histogram, depth-limited)
def make_bins(X, nb=32):
    """Quantile edges per feature (from training data), reused unchanged at serving time."""
    return [np.unique(np.quantile(X[:, j], np.linspace(0, 1, nb + 1)[1:-1])) for j in range(X.shape[1])]

def apply_bins(X, edges):
    return np.stack([np.searchsorted(e, X[:, j], side="right") for j, e in enumerate(edges)], 1).astype(np.int32)

def train_gbdt(B, y, n_trees=200, depth=3, lr=0.1, lam=1.0, nb=33, min_h=10.0):
    """Gradient boosting on log loss with Newton leaves. B: binned features. Returns (base, trees).
    A tree is (feat, thr, leaf): level-order split arrays and 2**depth leaf values."""
    n, d = B.shape
    base = math.log(y.mean() / (1 - y.mean()))
    F = np.full(n, base)
    trees = []
    for _ in range(n_trees):
        p = sigmoid(F); gr, he = p - y, p * (1 - p)
        node = np.zeros(n, np.int64)
        feat, thr = [], []
        for lev in range(depth):
            m = 2 ** lev
            bf, bt = np.zeros(m, np.int64), np.full(m, nb)       # thr = nb: everything goes left
            best = np.zeros(m)
            for j in range(d):
                key = node * nb + B[:, j]
                Gh = np.bincount(key, gr, m * nb).reshape(m, nb).cumsum(1)
                Hh = np.bincount(key, he, m * nb).reshape(m, nb).cumsum(1)
                Gt, Ht = Gh[:, -1:], Hh[:, -1:]
                GR, HR = Gt - Gh, Ht - Hh
                gain = Gh ** 2 / (Hh + lam) + GR ** 2 / (HR + lam) - Gt ** 2 / (Ht + lam)
                gain[(Hh < min_h) | (HR < min_h)] = 0
                k = gain.argmax(1); gk = gain[np.arange(m), k]
                better = gk > best
                best[better], bf[better], bt[better] = gk[better], j, k[better]
            feat.append(bf); thr.append(bt)
            node = 2 * node + (B[np.arange(n), bf[node]] > bt[node])
        L = 2 ** depth
        leaf = -lr * np.bincount(node, gr, L) / (np.bincount(node, he, L) + lam)
        F += leaf[node]
        trees.append((feat, thr, leaf))
    return base, trees

def gbdt_logit(model, B):
    base, trees = model
    out = np.full(len(B), base)
    rows = np.arange(len(B))
    for feat, thr, leaf in trees:
        node = np.zeros(len(B), np.int64)
        for bf, bt in zip(feat, thr):
            node = 2 * node + (B[rows, bf[node]] > bt[node])
        out += leaf[node]
    return out


# ---------------------------------------------------------------- metrics
def top_k_per_user(D, scores, k=10):
    """For each user, the k best candidates; ties go to the smaller id (candidates are sorted by id)."""
    out = {}
    bounds = np.r_[0, np.flatnonzero(np.diff(D["u"])) + 1, len(D["u"])]
    for a, b in zip(bounds[:-1], bounds[1:]):
        order = np.argsort(-scores[a:b], kind="stable")[:k]
        out[int(D["u"][a])] = D["v"][a:b][order]
    return out

def per_user_recall(D, scores, k=10):
    """recall@k for every evaluated user (in D['users'] order); future friends who were never
    candidates count as misses. Also hits per user (for precision@k = hits / k)."""
    top = top_k_per_user(D, scores, k)
    rec, hits = np.zeros(len(D["users"])), np.zeros(len(D["users"]))
    for i, u in enumerate(D["users"]):
        fut = D["truth"][int(u)]
        h = len(fut.intersection(top.get(int(u), np.empty(0)).tolist()))
        rec[i], hits[i] = h / len(fut), h
    return rec, hits

def roc_auc(scores, labels):
    """P(random positive outranks random negative), ties count 1/2. One sort (Mann-Whitney)."""
    s, y = np.asarray(scores, float), np.asarray(labels, bool)
    order = np.argsort(s, kind="mergesort")
    s, y = s[order], y[order]
    starts = np.r_[0, np.flatnonzero(np.diff(s)) + 1]
    pos = np.add.reduceat(y.astype(float), starts)
    neg = np.add.reduceat((~y).astype(float), starts)
    neg_below = np.cumsum(neg) - neg
    return float((pos * (neg_below + 0.5 * neg)).sum() / (pos.sum() * neg.sum()))

def average_precision(scores, labels):
    """PR-AUC as average precision: the mean, over positives, of precision at that positive's rank."""
    y = np.asarray(labels, bool)[np.argsort(-np.asarray(scores, float), kind="stable")]
    hits = np.cumsum(y)
    return float((hits[y] / (np.flatnonzero(y) + 1)).mean())

def bootstrap_ci(x, B=1000, seed=0, alpha=0.05):
    """Mean of a per-user metric and a percentile interval from resampling users with replacement."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    means = np.array([x[rng.integers(0, len(x), len(x))].mean() for _ in range(B)])
    return x.mean(), np.quantile(means, alpha / 2), np.quantile(means, 1 - alpha / 2)

def paired_ci(a, b, B=1000, seed=0):
    """Interval for mean(a - b), resampling the same users for both rankers."""
    return bootstrap_ci(np.asarray(a) - np.asarray(b), B, seed)

def reliability(p, y, bins=10):
    """Equal-count bins by predicted probability: (mean predicted, observed rate, n); and the ECE."""
    order = np.argsort(p)
    rows = [(p[c].mean(), y[c].mean(), len(c)) for c in np.array_split(order, bins)]
    return rows, sum(n * abs(a - b) for a, b, n in rows) / len(p)


# ---------------------------------------------------------------- self-test
if __name__ == "__main__":
    assert abs(roc_auc([3, 2, 2, 1], [1, 1, 0, 0]) - 0.875) < 1e-12
    assert abs(average_precision([4, 3, 2, 1], [1, 0, 1, 0]) - (1 + 2 / 3) / 2) < 1e-12
    rng = np.random.default_rng(1)
    s, y = rng.integers(0, 5, 300), rng.random(300) < 0.3
    slow = np.mean([(a > b) + 0.5 * (a == b) for a in s[y] for b in s[~y]])
    assert abs(roc_auc(s, y) - slow) < 1e-12
    # gradient check
    X = np.c_[np.ones(50), rng.normal(size=(50, 3))]; yy = (rng.random(50) < 0.4).astype(float)
    w = rng.normal(size=4); _, gr = loss_grad(w, X, yy, 0.1)
    num = [(loss_grad(w + e, X, yy, 0.1)[0] - loss_grad(w - e, X, yy, 0.1)[0]) / 2e-6 for e in np.eye(4) * 1e-6]
    assert np.allclose(gr, num, atol=1e-6)
    # two-hop counts on the six people: You 0, Ben 1, Chloe 2, Dev 3, Esha 4, Farid 5
    six = np.array([[0, 1], [0, 2], [1, 2], [1, 3], [1, 4], [2, 4], [2, 5]])
    g6 = Graph(six, 7, n=6)
    c, cn, aa, ra = g6.two_hop(0)
    assert c.tolist() == [3, 4, 5] and cn.tolist() == [1, 2, 1]
    assert abs(aa[1] - 2 / math.log(4)) < 1e-12
    # a GBDT learns an interaction a line cannot (XOR of two binary features)
    Xb = rng.integers(0, 2, size=(4000, 2)); yb = ((Xb[:, 0] ^ Xb[:, 1]) == 1).astype(float)
    flip = rng.random(4000) < 0.1; yb[flip] = 1 - yb[flip]
    m = train_gbdt(Xb.astype(np.int32), yb, n_trees=50, depth=2, nb=2)
    assert roc_auc(gbdt_logit(m, Xb.astype(np.int32)), yb) > 0.85
    print("common.py self-test passed")
