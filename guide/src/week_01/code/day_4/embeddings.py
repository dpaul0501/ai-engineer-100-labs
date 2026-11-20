# Day 4, last section: from features to representations. Factorise what each user did up to the
# cut (whom they befriended, which groups they joined) into one short vector per user, score pairs
# by a dot product, and measure against mutual friends.
import numpy as np

from common import (N_USERS, TEST_CUT, TRAIN_CUT, END, build, fit_lr_ranker, load_edges, load_users,
                    paired_ci, per_user_recall, sample_negatives)


def adjacency_matrix(edges, cut, n=N_USERS):
    A = np.zeros((n, n), np.float32)
    e = edges[:cut]
    A[e[:, 0], e[:, 1]] = 1; A[e[:, 1], e[:, 0]] = 1
    return A


def embed(M, k, seed=0, power=4):
    """Truncated SVD M ≈ U S Vᵀ (randomised: find the top-k row space, then an exact small SVD).
    User i's vector is U[i] * S, so z_u · z_v ≈ (M Mᵀ)[u, v]. For M = A that is A², the
    mutual-friend count; for M = [A | a·G] it is mutual friends + a² · shared groups."""
    rng = np.random.default_rng(seed)
    Q = np.linalg.qr(M @ rng.normal(size=(M.shape[1], 2 * k)).astype(np.float32))[0]
    for _ in range(power):                            # power iterations sharpen the top directions
        Q = np.linalg.qr(M @ (M.T @ Q))[0]
    Ub, S, _ = np.linalg.svd(Q.T @ M, full_matrices=False)
    return (Q @ Ub[:, :k]) * S[:k]


def rank_all(Z, A, users, k=10, chunk=1000):
    """Top k over ALL users (not just friends of friends), excluding the user and current friends."""
    out = {}
    for a in range(0, len(users), chunk):
        u = users[a:a + chunk]
        S = Z[u] @ Z.T
        S[A[u] > 0] = -np.inf
        S[np.arange(len(u)), u] = -np.inf
        top = np.argpartition(-S, k, axis=1)[:, :k]
        for i, uu in enumerate(u):
            out[int(uu)] = top[i][np.argsort(-S[i, top[i]], kind="stable")]
    return out


def recall_from_top(te, top, k=10):
    return np.array([len(te["truth"][int(u)].intersection(top[int(u)][:k].tolist())) / len(te["truth"][int(u)])
                     for u in te["users"]])


def main():
    # ---- the six people. You and Esha have the same friends {Ben, Chloe}: same row, same vector.
    six = np.array([[0, 1], [0, 2], [1, 2], [1, 3], [1, 4], [2, 4], [2, 5]])
    A6 = adjacency_matrix(six, 7, 6)
    names = ["You", "Ben", "Chloe", "Dev", "Esha", "Farid"]
    for k in (2, 3):
        Z6 = embed(A6, k)
        print(f"six people, k={k}: You's scores z_You · z_v  (exact mutual friends: Dev 1, Esha 2, Farid 1)")
        print("   " + ", ".join(f"{names[v]} {Z6[0] @ Z6[v]:.2f}" for v in (3, 4, 5)))
        assert np.allclose(Z6[0], Z6[4], atol=1e-5)   # same friend list -> same vector
    Z6 = embed(A6, 2)
    Z6 = Z6 * np.sign(Z6[1])                          # each direction's sign is arbitrary; fix Ben's positive
    print("two numbers per person (k=2):")
    for nme, z in zip(names, Z6):
        print(f"  {nme:6s} " + " ".join(f"{x:+.2f}" for x in z))

    # ---- the week's graph
    E = load_edges(); city, G = load_users()
    te = build(E, city, G, TEST_CUT, TEST_CUT, END)
    A = adjacency_matrix(E, TEST_CUT)
    users = te["users"]
    deg = te["g"].deg[users]
    low = (deg >= 1) & (deg <= 5)
    mf, _ = per_user_recall(te, te["cn"].astype(float))
    print(f"\nrecall@10, {len(users):,} users: mutual friends {mf.mean():.4f}; users with 1-5 friends "
          f"({low.sum()}): {mf[low].mean():.4f}")
    fof = set(zip(te["u"][te["y"]].tolist(), te["v"][te["y"]].tolist()))
    outside = sum(1 for u in users for v in te["truth"][int(u)] if (int(u), v) not in fof)
    print(f"future (user, friend) pairs with no mutual friend at the cut: {outside:,} (mutual friends can never rank them)")
    res = {}
    for name, M in [("friends only", A), ("friends + groups", np.c_[A, 2.0 * G])]:
        for k in (16, 64, 256):
            top = rank_all(embed(M, k), A, users)
            r = recall_from_top(te, top)
            beyond = sum(1 for u in users for v in te["truth"][int(u)]
                         if (int(u), v) not in fof and v in set(top[int(u)].tolist()))
            res[(name, k)] = r
            print(f"  {name:16s} k={k:3d}: recall@10 {r.mean():.4f}; 1-5 friends {r[low].mean():.4f}; "
                  f"hits beyond two hops {beyond}")
    for key in [("friends only", 256), ("friends + groups", 256)]:
        r = res[key]
        m, lo, hi = paired_ci(r, mf); print(f"{key[0]}, k=256 vs mutual friends, all: {m:+.4f} [{lo:+.4f}, {hi:+.4f}]")
        m, lo, hi = paired_ci(r[low], mf[low]); print(f"   1-5 friends: {m:+.4f} [{lo:+.4f}, {hi:+.4f}]")

    # ---- the dot product as one more feature for the ranker (vectors from each cut's own data)
    tr = build(E, city, G, TRAIN_CUT, TRAIN_CUT, TEST_CUT)
    Ztr = embed(np.c_[adjacency_matrix(E, TRAIN_CUT), 2.0 * G], 256)
    Zte = embed(np.c_[A, 2.0 * G], 256)
    dot = lambda Z, D: np.einsum("ij,ij->i", Z[D["u"]], Z[D["v"]]).astype(np.float32)
    Xs, ys = sample_negatives(dict(tr, X=np.c_[tr["X"], dot(Ztr, tr)]))
    _, _, lr9 = fit_lr_ranker(Xs, ys)
    _, _, lr8 = fit_lr_ranker(Xs[:, :8], ys)
    r8, _ = per_user_recall(te, lr8(te["X"]))
    r9, _ = per_user_recall(te, lr9(np.c_[te["X"], dot(Zte, te)]))
    m, lo, hi = paired_ci(r9, r8)
    print(f"\nLR, 8 hand features {r8.mean():.4f}; + embedding dot product {r9.mean():.4f}; "
          f"difference {m:+.4f} [{lo:+.4f}, {hi:+.4f}]; 1-5 friends {r8[low].mean():.4f} -> {r9[low].mean():.4f}")
    print(f"storage: {N_USERS:,} users x 256 floats x 4 bytes = {N_USERS * 256 * 4 / 1e6:.2f} MB")
    return mf, res, r8, r9


if __name__ == "__main__":
    mf, res, r8, r9 = main()
    assert res[("friends + groups", 256)].mean() > 0
