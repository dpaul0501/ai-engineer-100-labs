# MinHash error against signature length on real pairs, and LSH banding on the week's data.
# Same hash and signature as minhash.py, vectorised with NumPy (checked equal below).
import numpy as np
from friends import load_friends
from minhash import mix64, make_seeds, signature, s_curve

fr = load_friends()
N = len(fr)
deg = np.array([len(fr[u]) for u in range(N)])
indptr = np.concatenate([[0], np.cumsum(deg)])
indices = np.concatenate([np.array(sorted(fr[u]), dtype=np.uint64) for u in range(N)])

def mix64_np(x):
    x = x + np.uint64(0x9E3779B97F4A7C15)
    x = (x ^ (x >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    x = (x ^ (x >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return x ^ (x >> np.uint64(31))

def signatures(seeds):
    sig = np.empty((N, len(seeds)), dtype=np.uint64)
    for i, s in enumerate(seeds):
        h = mix64_np(indices ^ np.uint64(s))
        sig[:, i] = np.minimum.reduceat(h, indptr[:-1])
    return sig

seeds = make_seeds(8, seed=99)
S = signatures(seeds)
for u in (0, 1781, 4242):
    assert [int(x) for x in S[u]] == signature(fr[u], seeds)

# true mutual counts and Jaccard for every pair two steps apart (as in measure_mapreduce.py)
keys = []
for u in range(N):
    f = indices[indptr[u]:indptr[u + 1]].astype(np.int64)
    i, j = np.triu_indices(len(f), 1)
    keys.append(f[i] * N + f[j])
pairs, mutual = np.unique(np.concatenate(keys), return_counts=True)
friend_key = np.array(sorted(min(u, v) * N + max(u, v) for u in fr for v in fr[u] if u < v))
nf = ~np.isin(pairs, friend_key)
pairs, mutual = pairs[nf], mutual[nf]
x, y = pairs // N, pairs % N
J = mutual / (deg[x] + deg[y] - mutual)
print(f"non-friend pairs two steps apart {len(pairs):,}; mean Jaccard {J.mean():.4f}; "
      f"J >= 0.1: {int((J >= 0.1).sum()):,}; J >= 0.2: {int((J >= 0.2).sum()):,}")

rng = np.random.default_rng(0)
typ = rng.choice(len(pairs), 2000, replace=False)
hi_all = np.flatnonzero(J >= 0.1)
hi = rng.choice(hi_all, 2000, replace=False)
print(f"typical sample: mean J {J[typ].mean():.4f}, mean mutual {mutual[typ].mean():.2f}; "
      f"high-overlap sample: mean J {J[hi].mean():.3f}, mean mutual {mutual[hi].mean():.2f}, "
      f"mean list sizes {deg[x[hi]].mean():.1f} and {deg[y[hi]].mean():.1f}")
print("k, group, RMSE of J estimate (measured over 5 seed sets), predicted sqrt(mean J(1-J)/k), "
      "mutual-count mean abs error")
for k in (16, 64, 256):
    for name, idx in (("typical", typ), ("high", hi)):
        se, ae = [], []
        for rep in range(5):
            Sk = signatures(make_seeds(k, seed=1000 * k + rep))
            est = (Sk[x[idx]] == Sk[y[idx]]).mean(axis=1)
            se.append(((est - J[idx]) ** 2).mean())
            m_est = est * (deg[x[idx]] + deg[y[idx]]) / (1 + est)
            ae.append(np.abs(m_est - mutual[idx]).mean())
        pred = np.sqrt((J[idx] * (1 - J[idx])).mean() / k)
        print(f"  k={k:3d} {name:8s} rmse {np.sqrt(np.mean(se)):.4f}  predicted {pred:.4f}  "
              f"mutual abs err {np.mean(ae):.2f}")

print(f"signature memory at k=128: {N * 128 * 8:,} bytes; friend lists as int32: {4 * int(deg.sum()):,}")

# LSH banding
wanted = pairs[J >= 0.1]
Jw = J[J >= 0.1]
exact_emit = int((deg * (deg - 1) // 2).sum())
def band_pairs(sig, r, b):
    out, emitted, biggest = [], 0, 0
    for band in range(b):
        key = sig[:, band * r]
        for c in range(band * r + 1, (band + 1) * r):
            key = mix64_np(key ^ sig[:, c])
        order = np.argsort(key, kind="stable")
        ks = key[order]
        cut = np.flatnonzero(np.diff(ks)) + 1
        for g in np.split(order, cut):
            if len(g) > 1:
                g = np.sort(g)
                i, j = np.triu_indices(len(g), 1)
                out.append(g[i] * N + g[j])
                emitted += len(i)
                biggest = max(biggest, len(g))
    cand = np.unique(np.concatenate(out)) if out else np.array([], dtype=np.int64)
    return cand, emitted, biggest
print(f"LSH: wanted = non-friend pairs with J >= 0.1 ({len(wanted):,}); exact job emits {exact_emit:,}")
print("r, b, step (1/b)^(1/r), recall predicted, recall measured (min-max of 3), emitted (mean), "
      "share of candidates wanted, biggest bucket")
for r, b in ((1, 10), (2, 50), (2, 100), (3, 50)):
    rec, em, share, big = [], [], [], []
    for rep in range(3):
        cand, e, bg = band_pairs(signatures(make_seeds(r * b, seed=7000 + 10 * r + b + rep)), r, b)
        hit = np.isin(wanted, cand)
        rec.append(hit.mean()); em.append(e); share.append(hit.sum() / len(cand)); big.append(bg)
    pred = s_curve(Jw, r, b).mean()
    print(f"  r={r} b={b:3d} step {(1/b)**(1/r):.3f} pred {pred:.3f} measured {np.mean(rec):.3f} "
          f"[{min(rec):.3f}, {max(rec):.3f}] emitted {np.mean(em):,.0f} ({np.mean(em)/exact_emit:.1%} of exact) "
          f"wanted share {np.mean(share):.1%} biggest bucket {max(big)}")
