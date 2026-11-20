# Intersect real pairs of friend lists from the week's data, five ways: count the work and time it.
import random, sys, timeit
import numpy as np
from friends import load_friends
from intersect import (intersect_nested, intersect_hash, intersect_merge, intersect_binary,
                       intersect_gallop, to_bits, count_bits)

fr = load_friends()
N = len(fr)
srt = {u: sorted(s) for u, s in fr.items()}
bits = {u: to_bits(s) for u, s in fr.items()}
deg = {u: len(s) for u, s in fr.items()}
rng = random.Random(0)

def two_steps(u):
    """People two steps from u: friends of u's friends, not u, not already u's friends."""
    out = set()
    for f in fr[u]:
        out |= fr[f]
    return out - fr[u] - {u}

# Group 1: typical pairs. A random user and a random person two steps away.
users = list(fr)
typical = []
while len(typical) < 2000:
    u = rng.choice(users)
    cand = sorted(two_steps(u))
    if cand:
        typical.append((u, rng.choice(cand)))
# Group 2: skewed. A user with at most 20 friends and a hub (500+ friends) two steps away.
hubs = [u for u in fr if deg[u] >= 500]
skewed = []
while len(skewed) < 2000:
    u = rng.choice(users)
    if deg[u] > 20:
        continue
    near = sorted(two_steps(u) & set(hubs))
    if near:
        skewed.append((u, rng.choice(near)))
# Group 3: hub against hub, all pairs of the ten largest lists.
top10 = sorted(fr, key=lambda u: -deg[u])[:10]
hubpairs = [(x, y) for i, x in enumerate(top10) for y in top10[i + 1:]]

def run(pairs):
    sm = [min(deg[u], deg[v]) for u, v in pairs]
    lg = [max(deg[u], deg[v]) for u, v in pairs]
    def order(u, v):
        return (u, v) if deg[u] <= deg[v] else (v, u)
    ops = {k: 0 for k in ("nested", "hash", "merge", "binary", "gallop")}
    for u, v in pairs:
        s, l = order(u, v)
        r = [intersect_nested(srt[s], srt[l]), intersect_hash(srt[s], fr[l]),
             intersect_merge(srt[s], srt[l]), intersect_binary(srt[s], srt[l]),
             intersect_gallop(srt[s], srt[l])]
        assert all(x[0] == r[0][0] for x in r) and len(r[0][0]) == count_bits(bits[u], bits[v])
        for k, x in zip(ops, r):
            ops[k] += x[1]
    n = len(pairs)
    sp = [order(u, v) for u, v in pairs]
    t = {
        "nested": lambda: [intersect_nested(srt[s], srt[l]) for s, l in sp],
        "hash": lambda: [intersect_hash(srt[s], fr[l]) for s, l in sp],
        "merge": lambda: [intersect_merge(srt[s], srt[l]) for s, l in sp],
        "binary": lambda: [intersect_binary(srt[s], srt[l]) for s, l in sp],
        "gallop": lambda: [intersect_gallop(srt[s], srt[l]) for s, l in sp],
        "bits": lambda: [count_bits(bits[s], bits[l]) for s, l in sp],
        "set&set (C)": lambda: [len(fr[s] & fr[l]) for s, l in sp],
    }
    times = {k: min(timeit.repeat(f, number=1, repeat=3)) / n * 1e6 for k, f in t.items()}
    mutual = sum(len(fr[u] & fr[v]) for u, v in pairs) / n
    print(f"  pairs {n}, shorter list {sum(sm)/n:.1f}, longer list {sum(lg)/n:.1f}, mutual friends {mutual:.2f}")
    print("  operations per pair: " + " · ".join(f"{k} {ops[k]/n:.1f}" for k in ops) + f" · bits {(N+63)//64}")
    print("  microseconds per pair: " + " · ".join(f"{k} {v:.2f}" for k, v in times.items()))
    return ops, times

print(f"hubs (500+ friends): {len(hubs)}; ten largest lists: {[deg[u] for u in top10]}")
for name, pairs in (("typical two-step pairs", typical), ("skewed: small list vs hub", skewed),
                    ("hub vs hub (10 largest)", hubpairs)):
    print(name)
    run(pairs)

# Memory for the largest list, three ways
h = top10[0]
print("largest list", deg[h], "ids")
print("  as a Python set (bytes, table only)", sys.getsizeof(fr[h]))
print("  as a sorted int32 array (bytes)", np.array(srt[h], dtype=np.int32).nbytes)
print("  as a bitset over", N, "ids (bytes)", (N + 7) // 8)
print("all lists: int32 arrays", 4 * sum(deg.values()), "bytes; bitsets", N * ((N + 7) // 8), "bytes")
