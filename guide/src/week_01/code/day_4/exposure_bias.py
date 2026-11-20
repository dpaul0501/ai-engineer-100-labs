# Day 4, §11: exposure bias, simulated. The week's graph has no impression log, so we invent one:
# an old system shows each user the 9 candidates with most mutual friends plus 1 candidate drawn at
# random from the rest (the exploration slot), and we only "see" outcomes for pairs it showed.
# Assumption of the simulation: a shown pair connects exactly when it connected in the real window.
import numpy as np

from common import (TEST_CUT, TRAIN_CUT, END, build, fit_scaler, load_edges, load_users, logit_lr, paired_ci,
                    per_user_recall, sample_negatives, scale, sigmoid, fit_lr_ranker)

TOP, SLOTS = 9, 10


def log_impressions(D, seed=0):
    """shown[i] for every candidate pair, and its propensity pi[i] = P(shown) under the old policy."""
    rng = np.random.default_rng(seed)
    shown, pi = np.zeros(len(D["u"]), bool), np.zeros(len(D["u"]))
    bounds = np.r_[0, np.flatnonzero(np.diff(D["u"])) + 1, len(D["u"])]
    for a, b in zip(bounds[:-1], bounds[1:]):
        order = a + np.argsort(-D["cn"][a:b], kind="stable")   # most mutual friends first, ties by id
        top, rest = order[:TOP], order[TOP:]
        shown[top], pi[top] = True, 1.0
        if len(rest):
            shown[rng.choice(rest)] = True
            pi[rest] = 1.0 / len(rest)                        # the exploration slot is uniform
    return shown, pi


def hits_at_10(D, scores, weight):
    """Per-user sum of weight over the ranker's top 10 (weight = label, or a logged estimate of it)."""
    out = np.zeros(len(D["users"]))
    bounds = np.r_[0, np.flatnonzero(np.diff(D["u"])) + 1, len(D["u"])]
    pos = {int(u): i for i, u in enumerate(D["users"])}
    for a, b in zip(bounds[:-1], bounds[1:]):
        top = a + np.argsort(-scores[a:b], kind="stable")[:SLOTS]
        out[pos[int(D["u"][a])]] = weight[top].sum()
    return out


def train_weighted_lr(X, y, wt, lam=1e-3, iters=3000):
    """Logistic regression minimising the weighted mean log loss (weights = 1/propensity)."""
    s = fit_scaler(X)
    Z = np.c_[np.ones(len(X)), scale(X, s)]
    wt = wt / wt.mean()
    L = np.linalg.norm(Z * np.sqrt(wt)[:, None], 2) ** 2 / (4 * len(y)) + lam
    w = np.zeros(Z.shape[1])
    for _ in range(iters):
        p = sigmoid(Z @ w)
        w -= (Z.T @ (wt * (p - y)) / len(y) + lam * np.r_[0.0, w[1:]]) / L
    return lambda Xn: logit_lr(w, scale(Xn, s))


def main():
    E = load_edges(); city, G = load_users()
    tr = build(E, city, G, TRAIN_CUT, TRAIN_CUT, TEST_CUT)
    te = build(E, city, G, TEST_CUT, TEST_CUT, END)

    # ---- 1. Evaluating a new ranker on the old ranker's logs
    _, _, lr = fit_lr_ranker(*sample_negatives(tr))
    shown, pi = log_impressions(te)
    y = te["y"].astype(float)
    print(f"test window: {shown.sum():,} impressions logged; they contain {int(y[shown].sum()):,} of the "
          f"{int(y.sum()):,} pairs that connected ({y[shown].sum() / y.sum():.1%})")
    logged = np.where(shown, y, 0.0)                         # what the log says: unseen = 0
    ipw = np.where(shown, y / np.maximum(pi, 1e-12), 0.0)    # each logged outcome stands in for 1/pi pairs
    print("hits in the top 10 per user: naive from logs | IPW from logs | truth (all labels)")
    res = {}
    for name, sc in [("mutual friends (old)", te["cn"].astype(float)), ("logistic regression (new)", lr(te["X"]))]:
        res[name] = [hits_at_10(te, sc, w).mean() for w in (logged, ipw, y)]
        print(f"  {name:26s} {res[name][0]:.4f} | {res[name][1]:.4f} | {res[name][2]:.4f}")
    old, new = res["mutual friends (old)"], res["logistic regression (new)"]
    print(f"  verdict, new vs old: naive {new[0] / old[0] - 1:+.1%}, IPW {new[1] / old[1] - 1:+.1%}, "
          f"truth {new[2] / old[2] - 1:+.1%}")
    # IPW noise: repeat the logging with different random exploration draws
    reps = []
    for seed in range(1, 21):
        sh, p_ = log_impressions(te, seed)
        w = np.where(sh, y / np.maximum(p_, 1e-12), 0.0)
        reps.append([hits_at_10(te, sc, w).mean() for sc in (te["cn"].astype(float), lr(te["X"]))])
    reps = np.array(reps)
    print(f"  IPW over 20 different exploration draws: old {reps[:, 0].mean():.4f} ± {reps[:, 0].std():.4f}, "
          f"new {reps[:, 1].mean():.4f} ± {reps[:, 1].std():.4f}")

    # ---- 2. Training a new ranker on the old ranker's logs
    sh, p_ = log_impressions(tr)
    ytr = tr["y"].astype(float)
    print(f"\ntrain window: {sh.sum():,} impressions, {int(ytr[sh].sum()):,} logged positives "
          f"of {int(ytr.sum()):,} that happened")
    models = {}
    # (a) never shown = negative: every candidate is a row, label 1 only if shown and connected
    neg_r = np.random.default_rng(0).random(len(ytr)) < 0.05
    lab = (sh & (ytr == 1)).astype(float)
    keep = (lab == 1) | neg_r
    _, _, models["never shown = negative"] = fit_lr_ranker(tr["X"][keep], lab[keep])
    # (b) shown pairs only, unweighted
    _, _, models["shown only"] = fit_lr_ranker(tr["X"][sh], ytr[sh])
    # (c) shown pairs only, weighted by 1/propensity
    models["shown only, IPW"] = train_weighted_lr(tr["X"][sh], ytr[sh], 1.0 / p_[sh])
    # (d) every label (only possible in this simulation)
    models["all labels (oracle)"] = lr
    base, _ = per_user_recall(te, te["cn"].astype(float))
    print(f"recall@10 on the real test window: mutual friends {base.mean():.4f}")
    out, per = {}, {}
    for name, f in models.items():
        r, _ = per_user_recall(te, f(te["X"]))
        out[name], per[name] = r.mean(), r
    for name in models:
        m, lo, hi = paired_ci(per[name], per["all labels (oracle)"])
        print(f"  LR trained on {name:24s} {out[name]:.4f}   vs oracle {m:+.4f} [{lo:+.4f}, {hi:+.4f}]")
    return res, out


if __name__ == "__main__":
    res, out = main()
    old, new = res["mutual friends (old)"], res["logistic regression (new)"]
    assert new[0] < old[0] and new[2] > old[2]          # the logs pick the wrong winner; the truth does not
    assert abs(new[1] - new[2]) < abs(new[0] - new[2])  # IPW lands closer to the truth than the naive count
