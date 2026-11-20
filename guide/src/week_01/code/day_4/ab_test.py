# Day 4, data science: an A/B test simulated on the week's graph. Control shows each user the top 10 by
# mutual friends, treatment the top 10 by logistic regression. A user "converts" if at least one of
# the ten they were shown became their friend in the test window. Then: the z-test by hand, sample
# size and minimum detectable effect, peeking, and network interference with cluster randomisation.
import hashlib
import math
from statistics import NormalDist

import numpy as np

from common import (TEST_CUT, TRAIN_CUT, END, bootstrap_ci, build, fit_lr_ranker, load_edges, load_users,
                    per_user_recall, sample_negatives, top_k_per_user)

Z = NormalDist()


def arm(user_id, experiment, treatment_share=0.5):
    """Sticky assignment: the same user and experiment always give the same arm, on every request
    and device; different experiments hash independently."""
    h = hashlib.blake2b(f"{experiment}:{user_id}".encode(), digest_size=8).digest()
    return "treatment" if int.from_bytes(h, "big") < treatment_share * 2 ** 64 else "control"


def two_proportion_z(x1, n1, x2, n2):
    """z and two-sided p-value for H0: both arms have the same rate (pooled standard error)."""
    p1, p2, p = x1 / n1, x2 / n2, (x1 + x2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se
    return z, 2 * (1 - Z.cdf(abs(z))), se


def users_per_arm(p, q, alpha=0.05, power=0.8):
    """Users per arm to detect a change from rate p to rate q (two-sided two-proportion z-test)."""
    za, zb = Z.inv_cdf(1 - alpha / 2), Z.inv_cdf(power)
    pbar = (p + q) / 2
    n = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p * (1 - p) + q * (1 - q))) ** 2 / (q - p) ** 2
    return math.ceil(n)


def mde(p, n, alpha=0.05, power=0.8):
    """Smallest absolute lift detectable with n users per arm (normal approximation)."""
    return (Z.inv_cdf(1 - alpha / 2) + Z.inv_cdf(power)) * math.sqrt(2 * p * (1 - p) / n)


def peeking(p, n, looks, sims=20_000, seed=0):
    """A/A tests (no real difference). Share declared 'significant' when we look once at the end,
    versus when we look after every batch and stop at the first p < 0.05."""
    rng = np.random.default_rng(seed)
    per = n // looks
    a = rng.binomial(per, p, size=(sims, looks)).cumsum(1)
    b = rng.binomial(per, p, size=(sims, looks)).cumsum(1)
    m = per * np.arange(1, looks + 1)
    pool = (a + b) / (2 * m)
    z = (b - a) / m / np.sqrt(pool * (1 - pool) * 2 / m)
    sig = np.abs(z) > Z.inv_cdf(0.975)
    return sig[:, -1].mean(), sig.any(1).mean()


def percentile(xs, p):
    """Nearest rank: the value at position ceil(p * n) of the sorted list, counting from 1."""
    s = sorted(xs)
    return s[max(1, math.ceil(p * len(s))) - 1]


def main():
    E = load_edges(); city, G = load_users()
    tr = build(E, city, G, TRAIN_CUT, TRAIN_CUT, TEST_CUT)
    te = build(E, city, G, TEST_CUT, TEST_CUT, END)
    _, _, lr = fit_lr_ranker(*sample_negatives(tr))
    tops = {"control": top_k_per_user(te, te["cn"].astype(float)), "treatment": top_k_per_user(te, lr(te["X"]))}
    users = te["users"]
    rec, _ = per_user_recall(te, lr(te["X"]))
    print("per-user recall@10 of the LR ranker: mean {:.4f}; p50 {:.3f}, p75 {:.3f}, p90 {:.3f}, p99 {:.3f}; "
          "{:.1%} of users get no future friend in their ten".format(
              rec.mean(), *(percentile(rec, p) for p in (0.5, 0.75, 0.9, 0.99)), np.mean(rec == 0)))
    for B in (200, 1000, 5000):
        m, lo, hi = bootstrap_ci(rec, B=B)
        print(f"  bootstrap over users, B={B}: mean {m:.4f}, 95% interval [{lo:.4f}, {hi:.4f}]")
    print(f"  normal approximation: {rec.mean():.4f} ± {1.96 * rec.std(ddof=1) / math.sqrt(len(rec)):.4f}")
    conv = {arm: np.array([len(te["truth"][int(u)].intersection(t.get(int(u), np.empty(0)).tolist())) > 0
                           for u in users]) for arm, t in tops.items()}
    p0, p1 = conv["control"].mean(), conv["treatment"].mean()
    print(f"if everyone saw control: {p0:.4f} of {len(users):,} users convert; treatment: {p1:.4f} "
          f"(true lift {p1 - p0:+.4f}, {p1 / p0 - 1:+.1%} relative)")

    # ---- one randomised experiment, analysed by hand
    rng = np.random.default_rng(0)
    arm = rng.random(len(users)) < 0.5
    n1, n2 = int((~arm).sum()), int(arm.sum())
    x1, x2 = int(conv["control"][~arm].sum()), int(conv["treatment"][arm].sum())
    z, pv, se = two_proportion_z(x1, n1, x2, n2)
    print(f"A/B: control {x1}/{n1} = {x1 / n1:.4f}, treatment {x2}/{n2} = {x2 / n2:.4f}, "
          f"pooled {(x1 + x2) / (n1 + n2):.4f}, SE {se:.5f}, z {z:.2f}, p-value {pv:.2g}")
    lo, hi = (x2 / n2 - x1 / n1) + np.array([-1, 1]) * 1.96 * math.sqrt(
        x1 / n1 * (1 - x1 / n1) / n1 + x2 / n2 * (1 - x2 / n2) / n2)
    print(f"   95% CI for the lift: [{lo:+.4f}, {hi:+.4f}]")

    # ---- sample size and minimum detectable effect
    n_meas = users_per_arm(p0, p1)
    print(f"users per arm to detect {p0:.4f} -> {p1:.4f}: {n_meas:,}")
    for rel in (0.02, 0.05, 0.10):
        print(f"users per arm for a {rel:.0%} relative lift on {p0:.4f}: {users_per_arm(p0, p0 * (1 + rel)):,}")
    m = mde(p0, n1)
    print(f"MDE with {n1:,} users per arm at baseline {p0:.4f}: {m:.4f} absolute ({m / p0:.1%} relative)")

    # ---- peeking
    for looks in (1, 5, 20, 100):
        once, any_ = peeking(p0, 5000, looks)
        print(f"A/A, 5,000 users per arm, {looks:3d} looks: false positives looking once {once:.3f}, "
              f"stopping at first p<0.05 {any_:.3f}")

    # ---- network interference: a friendship forms if either person was shown the other
    fut = E[TEST_CUT:END]
    idx = {int(u): i for i, u in enumerate(users)}
    shows = {a: {(int(u), int(v)) for u, t in tops[a].items() for v in t} for a in tops}
    shown_by = {a: np.array([[(int(u), int(v)) in shows[a], (int(v), int(u)) in shows[a]] for u, v in fut])
                for a in tops}
    iu = np.array([idx[int(u)] for u in fut[:, 0]]); iv = np.array([idx[int(v)] for v in fut[:, 1]])

    def outcomes(treated):
        """1 if the user made at least one connection, when `treated[i]` users see the treatment ranker."""
        tu, tv = treated[iu], treated[iv]
        su = np.where(tu, shown_by["treatment"][:, 0], shown_by["control"][:, 0])
        sv = np.where(tv, shown_by["treatment"][:, 1], shown_by["control"][:, 1])
        happen = (su | sv).astype(float)
        return (np.bincount(iu, happen, len(users)) + np.bincount(iv, happen, len(users)) > 0).astype(float)

    y_all0, y_all1 = outcomes(np.zeros(len(users), bool)), outcomes(np.ones(len(users), bool))
    gte = y_all1.mean() - y_all0.mean()
    print(f"\ninterference: share of users with a connection, all control {y_all0.mean():.4f}, all treatment "
          f"{y_all1.mean():.4f}; true global effect {gte:+.4f}")
    grp = np.argmax(G[users], 1)                         # cluster = the user's first group
    within = np.mean(grp[iu] == grp[iv])
    print(f"clusters: {len(np.unique(grp))} groups, largest {np.bincount(grp).max():,} users; "
          f"{within:.1%} of the window's friendships fall inside one cluster")
    est = {"user-level": [], "cluster-level": []}
    for s in range(300):
        r = np.random.default_rng(1000 + s)
        t = r.random(len(users)) < 0.5
        y = outcomes(t); est["user-level"].append(y[t].mean() - y[~t].mean())
        tc = (r.random(200) < 0.5)[grp]
        y = outcomes(tc); est["cluster-level"].append(y[tc].mean() - y[~tc].mean())
    for k, v in est.items():
        v = np.array(v)
        print(f"  {k:14s} randomisation: mean estimate {v.mean():+.4f} ({v.mean() / gte:.0%} of the true effect), "
              f"SD across 300 re-randomisations {v.std():.4f}")
    return p0, p1, pv, gte, est


if __name__ == "__main__":
    p0, p1, pv, gte, est = main()
    assert p1 > p0 and pv < 0.05
    assert users_per_arm(0.10, 0.102) == 356_335
    a = [arm(u, "ranker-v2") == "treatment" for u in range(100_000)]
    b = [arm(u, "new-copy") == "treatment" for u in range(100_000)]
    both = sum(x and y for x, y in zip(a, b))
    print(f"sticky hash: {sum(a):,} of 100,000 users in treatment; {both:,} in both of two experiments")
    assert abs(sum(a) - 50_000) < 1_000 and abs(both - 25_000) < 1_000
    assert all(arm(7, "ranker-v2") == arm(7, "ranker-v2") for _ in range(3))         # matches the hand computation in the math block
    assert np.mean(est["user-level"]) < gte              # interference dilutes the user-level estimate
