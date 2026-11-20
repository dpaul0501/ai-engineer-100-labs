# Day 4, §4-§9: the mutual-friends rule, logistic regression, feature crosses and boosted trees,
# trained on one time cut and judged on the next. Prints every number in the evaluation tables.
import math
import time

import numpy as np

from common import (FEATURES, TEST_CUT, TRAIN_CUT, END, apply_bins, average_precision, bootstrap_ci,
                    build, fit_lr_ranker, gbdt_logit, load_edges, load_users, log_loss, make_bins,
                    paired_ci, per_user_recall, reliability, roc_auc, sample_negatives, sigmoid, train_gbdt)

R = 0.05                                             # each negative kept with probability r


def crosses(X):
    """Hand-made interactions for a linear model: 'mutual friends matter more if v is sociable', ..."""
    i = {f: k for k, f in enumerate(FEATURES)}
    c = lambda a, b: X[:, i[a]] * X[:, i[b]]
    return np.c_[X, c("log_cn", "log_dv"), c("log_aa", "log_dv"), c("log_aa", "log_du"),
                 c("shared_groups", "log_aa"), c("log_du", "log_dv"),
                 X[:, i["log_cn"]] ** 2, X[:, i["log_aa"]] ** 2, X[:, i["log_dv"]] ** 2]


def main():
    E = load_edges(); city, G = load_users()
    tr = build(E, city, G, TRAIN_CUT, TRAIN_CUT, TEST_CUT)
    te = build(E, city, G, TEST_CUT, TEST_CUT, END)
    y = te["y"]
    print(f"train window: {len(tr['y']):,} candidate pairs, {int(tr['y'].sum()):,} positives, "
          f"base rate {tr['y'].mean():.4%}")
    print(f"test window: {len(te['users']):,} users, {len(y):,} candidate pairs, {int(y.sum()):,} positives, "
          f"base rate {y.mean():.4%} (1 in {1 / y.mean():.0f})")
    future_pairs = sum(len(s) for s in te["truth"].values())
    print(f"future (user, friend) pairs: {future_pairs:,}; among candidates: {int(y.sum()):,} "
          f"= {y.sum() / future_pairs:.1%}")
    print(f"accuracy of 'nobody connects' on test candidates: {1 - y.mean():.4%}")

    Xtr, ytr = sample_negatives(tr, R)
    print(f"training rows after sampling: {len(ytr):,}, {ytr.mean():.1%} positive")

    scores = {"mutual friends": te["cn"], "Adamic-Adar": te["X"][:, 2].astype(float)}
    t = time.time()
    w, s, lr = fit_lr_ranker(Xtr, ytr)
    print(f"LR trained in {time.time() - t:.1f} s on one laptop core")
    scores["logistic regression"] = lr(te["X"])
    print("LR weights (standardised features):")
    print(f"  {'bias':14s} {w[0]:+.3f}")
    for f, wj in zip(FEATURES, w[1:]):
        print(f"  {f:14s} {wj:+.3f}")
    graph_only = [0, 1, 2, 3, 6, 7]                  # drop shared_groups and same_city
    _, _, lr_g = fit_lr_ranker(Xtr[:, graph_only], ytr)
    scores["LR, graph features only"] = lr_g(te["X"][:, graph_only])
    w2, s2, lr2 = fit_lr_ranker(crosses(Xtr), ytr)
    scores["LR + 8 crosses"] = lr2(crosses(te["X"]))

    t = time.time()
    edges = make_bins(Xtr)
    gb = train_gbdt(apply_bins(Xtr, edges), ytr, n_trees=200, depth=3, lr=0.1)
    print(f"GBDT (200 trees, depth 3) trained in {time.time() - t:.1f} s on one laptop core")
    scores["boosted trees"] = gbdt_logit(gb, apply_bins(te["X"], edges))

    print("\nranker | ROC-AUC | PR-AUC | recall@10 [95% CI] | precision@10")
    rec = {}
    for name, sc in scores.items():
        r, h = per_user_recall(te, sc)
        rec[name] = r
        m, lo, hi = bootstrap_ci(r)
        print(f"{name:20s} {roc_auc(sc, y):.3f} {average_precision(sc, y):.4f} "
              f"{m:.4f} [{lo:.4f}, {hi:.4f}] {h.mean() / 10:.4f}")
    print(f"random order PR-AUC baseline = prevalence = {y.mean():.4f}")
    r_ceil, _ = per_user_recall(te, y.astype(float), k=10 ** 6)
    m, lo, hi = bootstrap_ci(r_ceil)
    print(f"ceiling (every candidate who connected is found): {m:.3f} [{lo:.3f}, {hi:.3f}]")

    print("\npaired differences in recall@10 (same resampled users):")
    for a, b in [("Adamic-Adar", "mutual friends"), ("logistic regression", "Adamic-Adar"),
                 ("logistic regression", "mutual friends"),
                 ("logistic regression", "LR, graph features only"), ("LR, graph features only", "Adamic-Adar"),
                 ("LR + 8 crosses", "logistic regression"),
                 ("boosted trees", "logistic regression")]:
        m, lo, hi = paired_ci(rec[a], rec[b])
        print(f"  {a} - {b}: {m:+.4f} [{lo:+.4f}, {hi:+.4f}]  ({m / rec[b].mean():+.1%})")

    # Slices: users with few friends at the cut
    du = te["g"].deg[te["users"]]
    for lo_, hi_ in [(0, 0), (1, 5), (6, 20), (21, 10 ** 9)]:
        msk = (du >= lo_) & (du <= hi_)
        print(f"slice deg {lo_}-{hi_ if hi_ < 10 ** 9 else 'inf'}: {msk.sum():,} users; recall@10 "
              f"MF {rec['mutual friends'][msk].mean():.4f}, LR {rec['logistic regression'][msk].mean():.4f}, "
              f"GBDT {rec['boosted trees'][msk].mean():.4f}")

    # Log loss and calibration on the test pairs
    print("\nlog loss on all test pairs:")
    for name in ["logistic regression", "boosted trees"]:
        z = scores[name]
        print(f"  {name}: raw {log_loss(sigmoid(z), y):.4f}, + log r {log_loss(sigmoid(z + math.log(R)), y):.4f}")
    print(f"  constant base rate {y.mean():.5f}: {log_loss(np.full(len(y), y.mean()), y):.4f}")
    p_raw, p_cor = sigmoid(scores["logistic regression"]), sigmoid(scores["logistic regression"] + math.log(R))
    rows_raw, ece_raw = reliability(p_raw, y)
    rows_cor, ece_cor = reliability(p_cor, y)
    print("calibration, LR, ten equal-count bins: predicted raw | predicted + log r | observed")
    for i, ((a, o, n), (b, _, _)) in enumerate(zip(rows_raw, rows_cor)):
        print(f"  bin {i + 1}: {a:.3%} {b:.3%} {o:.3%}  (n={n:,})")
    print(f"  ECE raw {ece_raw:.5f}, corrected {ece_cor:.5f}, ratio {ece_raw / ece_cor:.0f}x")
    print(f"  mean predicted (corrected) {p_cor.mean():.3%} vs observed {y.mean():.3%}; "
          f"train-window base rate {tr['y'].mean():.3%}")

    msk = (du >= 1) & (du <= 5)
    m, lo, hi = paired_ci(rec["boosted trees"][msk], rec["logistic regression"][msk])
    print(f"slice deg 1-5, boosted trees - LR: {m:+.4f} [{lo:+.4f}, {hi:+.4f}]")
    m, lo, hi = paired_ci(rec["logistic regression"][msk], rec["mutual friends"][msk])
    print(f"slice deg 1-5, LR - mutual friends: {m:+.4f} [{lo:+.4f}, {hi:+.4f}]")

    figure(y, scores["logistic regression"])
    return te, scores, rec


def curves(scores, y):
    """ROC (false-positive rate, true-positive rate) and PR (recall, precision), one point per pair."""
    yy = y[np.argsort(-scores, kind="stable")]
    tp, fp = np.cumsum(yy), np.cumsum(~yy)
    return fp / fp[-1], tp / tp[-1], tp / tp[-1], tp / np.arange(1, len(yy) + 1)


def figure(y, z, path="../../img/roc-vs-pr.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fpr, tpr, rec, prec = curves(z, y)
    auc, ap, base = roc_auc(z, y), average_precision(z, y), y.mean()
    for k in (100, 1000, 10000):
        print(f"pooled precision in the top {k:,} pairs: {prec[k - 1]:.3f}")
    i = np.unique(np.r_[np.geomspace(1, len(y), 4000).astype(int) - 1, len(y) - 1])
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.3), dpi=200)
    ax[0].plot(fpr[i], tpr[i], color="#1f6feb", lw=2.5, label=f"Logistic regression  AUC = {auc:.2f}")
    ax[0].plot([0, 1], [0, 1], "--", color="#6b7280", lw=1.3, label="Random  AUC = 0.50")
    ax[0].set(xlabel="False-positive rate", ylabel="True-positive rate", title="ROC: looks great")
    ax[1].plot(rec[i], prec[i], color="#e8590c", lw=2.5, label=f"Logistic regression  PR-AUC = {ap:.3f}")
    ax[1].axhline(base, ls="--", color="#6b7280", lw=1.3, label=f"Random = prevalence = {base:.4f}")
    ax[1].set(xlabel="Recall", ylabel="Precision", title="Precision-recall: the honest view", ylim=(0, 0.3))
    for a in ax:
        a.grid(alpha=.3)
    ax[0].legend(loc="lower right", fontsize=8.5, framealpha=.95)
    ax[1].legend(loc="upper right", fontsize=8.5, framealpha=.95)
    for a in ax:
        a.title.set_fontweight("bold")
    fig.suptitle(f"The same model on 7.76 million test pairs, 1 positive in {1 / base:.0f}", fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    print("figure written:", path)


if __name__ == "__main__":
    te, scores, rec = main()
    assert rec["logistic regression"].mean() > rec["mutual friends"].mean()
    assert roc_auc(scores["logistic regression"], te["y"]) > 0.8
