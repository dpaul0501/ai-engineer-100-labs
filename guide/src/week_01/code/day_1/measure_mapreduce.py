# The all-pairs mutual-friend job on the week's data: how much the map step emits, where it comes
# from, and what three fixes (skip hubs, sample hubs, emit only for wanted users) save and cost.
# Same job as mapreduce.py, written with NumPy arrays so the full run fits in memory.
import numpy as np
from friends import DATA, load_friends
from mapreduce import run_job

fr = load_friends()
N = len(fr)
lists = {u: np.array(sorted(s), dtype=np.int64) for u, s in fr.items()}
deg = np.array([len(fr[u]) for u in range(N)])
rng = np.random.default_rng(0)
friend_key = np.array(sorted(min(u, v) * N + max(u, v) for u in fr for v in fr[u] if u < v))

def emit_pairs(f):
    i, j = np.triu_indices(len(f), 1)
    return f[i] * N + f[j]                      # pair (x, y), x < y, as one integer

def job(cap=None, sample=None):
    keys = []
    for u in range(N):
        f = lists[u]
        if cap is not None and len(f) > cap:
            continue                            # fix 1: hubs emit nothing
        if sample is not None and len(f) > sample:
            f = np.sort(rng.choice(f, sample, replace=False))   # fix 2: a random sample of a hub's friends
        keys.append(emit_pairs(f))
    keys = np.concatenate(keys)
    pairs, counts = np.unique(keys, return_counts=True)
    return keys, pairs, counts

def top10(pairs, counts):
    """Each user's ten best non-friends by count, ties to the smaller id: arrays (user, other, count)."""
    keep = ~np.isin(pairs, friend_key)
    p, c = pairs[keep], counts[keep]
    x, y = p // N, p % N
    u = np.concatenate([x, y]); v = np.concatenate([y, x]); cc = np.concatenate([c, c])
    o = np.lexsort((v, -cc, u))
    u, v, cc = u[o], v[o], cc[o]
    start = np.searchsorted(u, np.arange(N))
    rank = np.arange(len(u)) - start[u]
    k = rank < 10
    return u[k], v[k]

# cross-check against the plain-Python job on the first 10,000 friendships
import csv
small = {}
with open(DATA / "edges.csv") as fh:
    for row in list(csv.DictReader(fh))[:10_000]:
        a, b = int(row["u"]), int(row["v"])
        small.setdefault(a, set()).add(b); small.setdefault(b, set()).add(a)
py, py_emitted = run_job(small, reducers=8)
sk = np.concatenate([emit_pairs(np.array(sorted(s), dtype=np.int64)) for s in small.values()])
sp, sc = np.unique(sk, return_counts=True)
assert py_emitted == len(sk) and {(int(k) // N, int(k) % N): int(c) for k, c in zip(sp, sc)} == py

keys, pairs, counts = job()
emitted = len(keys)
assert emitted == int((deg * (deg - 1) // 2).sum())
is_friend = np.isin(pairs, friend_key)
print(f"emitted records {emitted:,} (sum of d(d-1)/2; sum of d^2 = {int((deg**2).sum()):,})")
print(f"distinct pairs after reduce {len(pairs):,}: already friends {int(is_friend.sum()):,}, "
      f"not yet friends {int((~is_friend).sum()):,}")
print(f"  of the non-friend pairs, 2+ mutual friends: {int(((~is_friend) & (counts >= 2)).sum()):,}")
eu, ev = top10(pairs, counts)
print(f"rows actually shown (top 10 per user): {len(eu):,}; emitted per row shown: {emitted/len(eu):.0f}")
per_user = deg * (deg - 1) // 2
order = np.argsort(-deg)
print(f"largest list {deg[order[0]]} friends emits {per_user[order[0]]:,} = {per_user[order[0]]/emitted:.1%} of all")
h = deg >= 500
print(f"{int(h.sum())} users with 500+ friends ({h.mean():.2%} of users) emit {per_user[h].sum()/emitted:.1%}")
print(f"median user emits {int(np.median(per_user))}; largest map task / median = {per_user.max()/np.median(per_user):,.0f}")
R = 100
part = ((keys.astype(np.uint64) * np.uint64(0x9E3779B97F4A7C15)) >> np.uint64(40)) % np.uint64(R)
load = np.bincount(part.astype(np.int64), minlength=R)
print(f"{R} reducers by hash of pair: busiest / average load = {load.max()/load.mean():.3f}")
reducer_by_user = np.bincount((keys // N) % R, minlength=R)
print(f"{R} reducers by first user of the pair: busiest / average = {reducer_by_user.max()/reducer_by_user.mean():.2f}")

exact = {}
for a, b in zip(eu, ev):
    exact.setdefault(int(a), []).append(int(b))
pair_count = dict(zip(pairs.tolist(), counts.tolist()))
def kept(u_arr, v_arr):
    """Mutual friends (exact counts) of the shown lists, as a share of the exact top-10's total."""
    got = {}
    for a, b in zip(u_arr.tolist(), v_arr.tolist()):
        got[a] = got.get(a, 0) + pair_count[min(a, b) * N + max(a, b)]
    want = {a: sum(pair_count[min(a, b) * N + max(a, b)] for b in bs) for a, bs in exact.items()}
    return sum(got.get(a, 0) for a in want) / sum(want.values())

print("fix, emitted, share of exact emit, top-10 mutual friends kept")
for c in (1000, 500, 200):
    k2, p2, c2 = job(cap=c)
    print(f"  skip lists over {c}: {len(k2):,}  {len(k2)/emitted:.1%}  {kept(*top10(p2, c2)):.1%}")
for s in (500, 200, 100):
    k2, p2, c2 = job(sample=s)
    print(f"  sample {s} friends of larger lists: {len(k2):,}  {len(k2)/emitted:.1%}  {kept(*top10(p2, c2)):.1%}")
for share in (0.10, 0.01):
    T = np.zeros(N, bool); T[rng.choice(N, int(share * N), replace=False)] = True
    # mapper of u emits (x, y) for x in T among u's friends and every other friend y: exact for T
    em = sum(int(T[lists[u]].sum()) * (deg[u] - 1) for u in range(N))
    print(f"  emit only for {share:.0%} of users: {em:,}  {em/emitted:.1%}  100.0% (exact for them)")
