# Day 2 · replay the week's 100,000 friendships in the order they formed.
# A) per hour: median and p90 of "mutual friends at the moment a friendship forms" (two heaps);
# B) keeping every user's top 10 fresh: how many counts change per new friendship, and how
#    many of those changes reach a top 10;
# C) "who gained the most friends in the last hour": exact vs Misra-Gries, Space-Saving, Count-Min.
import statistics
from collections import Counter

from common import load_edges, candidate_counts
from stream import QuantileFinder, MisraGries, SpaceSaving, CountMin
from topk import topk_sort
from fresh import FreshTopK

K = 10
edges = load_edges()
assert len(set(map(frozenset, edges))) == len(edges)          # no friendship twice

# ---- A and B in one pass
fresh = FreshTopK(K)             # every user's counts and top 10, kept exact (fresh.py)
HOUR = 10_000                    # treat each block of 10,000 friendships as one 'hour'
hours, per_edge = [], []
for t, (a, b) in enumerate(edges, 1):
    if (t - 1) % HOUR == 0:                      # a new hour: fresh heaps (a tumbling window)
        p50, p90, some = QuantileFinder(0.5), QuantileFinder(0.9), 0
    m = len(fresh.friends[a] & fresh.friends[b])  # mutual friends when the friendship forms
    p50.add(m); p90.add(m); some += m > 0
    if t % HOUR == 0:
        hours.append((p50.value(), p90.value(), some / HOUR))
    before = fresh.changes
    fresh.add_friendship(a, b)
    per_edge.append(fresh.changes - before)

friends, count = fresh.friends, fresh.count
incs, changed, recomputes = fresh.changes, fresh.top_changes, fresh.recomputes
for u in friends:                                # the incremental state equals a fresh recount
    assert count[u] == candidate_counts(friends, u)
    assert fresh.suggest(u) == topk_sort(count[u], K)

print("A) mutual friends at the moment a friendship forms, per hour (two heaps, reset each hour):")
for h, (a50, a90, share) in enumerate(hours, 1):
    print(f"   hour {h:2d}: median {a50}, p90 {a90}, share with at least one {share:.0%}")
print("B) keeping every top 10 fresh as friendships arrive:")
print(f"   count changes: {incs:,} in all, {statistics.mean(per_edge):.0f} per new friendship on average, "
      f"max {max(per_edge):,}")
print(f"   changes that altered some top 10: {changed:,} ({changed / incs:.1%})")
print(f"   removals that forced a top-10 recompute: {recomputes:,} ({100 * recomputes / len(edges):.1f} per 100 friendships)")
print("   final state checked against a fresh recount for every user")

# ---- C) trending: who gained the most friends in the last hour
last = edges[-HOUR:]
arrivals = [x for e in last for x in e]          # a user appears once per new friend
N = len(arrivals)
true = Counter(arrivals)
exact = topk_sort(true, K)
print(f"\nC) last hour = the last {HOUR:,} friendships: {N:,} arrivals, {len(true):,} distinct users")
print(f"   exact top 10 gains: {[true[x] for x in exact]}")


def report(name, top_ids, est, mem):
    rec = len(set(top_ids[:K]) & set(exact)) / K
    err = statistics.mean(abs(est(x) - true[x]) for x in exact)
    print(f"   {name:13s} memory {mem:5,}: recall@10 {rec:.1f}, mean |error| on the true top 10 {err:5.2f}")


for m in (20, 50, 100, 200, 500):
    mg, ss = MisraGries(m), SpaceSaving(m)
    for x in arrivals:
        mg.add(x); ss.add(x)
    report("Misra-Gries", sorted(mg.c, key=lambda y: (-mg.c[y], y)), mg.estimate, m)
    report("Space-Saving", ss.top(K), ss.estimate, m)
    print(f"   {'':13s} bounds: N/(m+1) = {N / (m + 1):.0f}, N/m = {N / m:.0f}")
for w in (50, 100, 200, 500):
    cm = CountMin(w=w, d=4, k=K, seed=0)
    for x in arrivals:
        cm.add(x)
    worst = max(cm.estimate(x) - true[x] for x in true)
    report("Count-Min", cm.top(K), cm.estimate, 4 * w + K)
    print(f"   {'':13s} w={w}, d=4: largest overcount over all users {worst}; e/w*N = {2.718281828 / w * N:.0f}")
