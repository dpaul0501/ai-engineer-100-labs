# Day 2 · measure the four static top-k methods on the week's friendships.
# 1) how many candidates n each user has, and how big the counts get;
# 2) comparisons made by sort / heap / quickselect, and bucket steps (sample of users);
# 3) time per user for all 10,000 users, as a ratio to sorting;
# 4) how often the 10th and 11th candidates tie (why a tie rule is needed).
import heapq
import random
import statistics
import time

from common import load_edges, friend_lists, candidate_counts
from topk import topk_sort, topk_heap, topk_quickselect, topk_bucket

K = 10
edges = load_edges()
friends = friend_lists(edges)
users = sorted(friends)
counts = {u: candidate_counts(friends, u) for u in users}


def pct(xs, p):                                  # nearest-rank percentile
    xs = sorted(xs)
    return xs[max(0, -(-int(p * len(xs) * 1000) // 1000) - 1)]


ns = [len(counts[u]) for u in users]
mx = [max(counts[u].values()) for u in users if counts[u]]
print(f"users {len(users)}, friendships {len(edges)}")
print(f"candidates per user n: min {min(ns)}, median {statistics.median(ns):.0f}, mean {statistics.mean(ns):.0f}, "
      f"p90 {pct(ns, .9)}, p99 {pct(ns, .99)}, max {max(ns)}")
print(f"users with fewer than {K} candidates: {sum(n < K for n in ns)}")
allc = [m for u in users for m in counts[u].values()]
print(f"all (user, candidate) counts: {len(allc)}; share equal to 1: {sum(m == 1 for m in allc) / len(allc):.1%}; "
      f"share <= 3: {sum(m <= 3 for m in allc) / len(allc):.1%}; largest count anywhere: {max(allc)}")
print(f"largest count per user: median {statistics.median(mx):.0f}, p99 {pct(mx, .99)}, max {max(mx)}")
ties = sum(1 for u in users if len(counts[u]) > K and
           sorted(counts[u].values(), reverse=True)[K - 1] == sorted(counts[u].values(), reverse=True)[K])
eligible = sum(1 for u in users if len(counts[u]) > K)
print(f"users whose 10th and 11th candidates tie on count: {ties} of {eligible} ({ties / eligible:.1%})")


# ---- comparisons, counted with a key that counts its own '<' calls
class Key:
    n = 0
    __slots__ = ("k",)

    def __init__(self, k):
        self.k = k

    def __lt__(self, other):
        Key.n += 1
        return self.k < other.k

    def __gt__(self, other):
        Key.n += 1
        return self.k > other.k


def cmp_sort(count):
    Key.n = 0
    sorted((Key((-m, v)) for v, m in count.items()))
    return Key.n


def cmp_heap(count, k=K):
    Key.n = 0
    heap = []
    for v, m in count.items():
        item = Key((m, -v))
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)
    sorted(heap)
    return Key.n


def cmp_quickselect(count, k=K, seed=0):
    rng = random.Random(seed)
    keys = [(-m, v) for v, m in count.items()]
    c, best = 0, []
    while k > 0 and keys:
        p = rng.choice(keys)
        better = [x for x in keys if x < p]
        c += len(keys)
        if len(better) >= k:
            keys = better
        else:
            best += better + [p]
            k -= len(better) + 1
            c += len(keys)
            keys = [x for x in keys if x > p]
    Key.n = 0
    sorted(Key(x) for x in best)
    return c + Key.n


def steps_bucket(count, k=K):
    """one step to drop each candidate in its bucket, one per bucket visited, plus comparisons
    inside heapq.nsmallest on the buckets taken from (counted separately)."""
    top = max(count.values())
    buckets = [[] for _ in range(top + 1)]
    for v, m in count.items():
        buckets[m].append(v)
    steps, out = len(count), 0
    Key.n = 0
    for m in range(top, 0, -1):
        steps += 1
        need = k - out
        if need == 0:
            break
        got = heapq.nsmallest(need, (Key(v) for v in buckets[m]))
        out += len(got)
    return steps + Key.n


rng = random.Random(0)
sample = [u for u in rng.sample(users, 1000) if len(counts[u]) >= K]
tot = {"sort": 0, "heap": 0, "quickselect": 0, "bucket": 0}
nsum = 0
for u in sample:
    c = counts[u]
    items = list(c.items())
    rng.shuffle(items)                            # the arrival order of candidates is arbitrary
    c = dict(items)
    nsum += len(c)
    tot["sort"] += cmp_sort(c)
    tot["heap"] += cmp_heap(c)
    tot["quickselect"] += cmp_quickselect(c)
    tot["bucket"] += steps_bucket(c)
print(f"\ncomparisons (bucket: steps) per candidate, {len(sample)} sampled users with >= {K} candidates, "
      f"mean n {nsum / len(sample):.0f}:")
for name, t in tot.items():
    print(f"  {name:12s} {t / nsum:6.2f}")

# heap replacements for one big user, against k(1 + ln(n/k))
import math
big = max(users, key=lambda u: len(counts[u]))
reps = []
for s in range(20):
    items = list(counts[big].items())
    random.Random(s).shuffle(items)
    heap, r = [], 0
    for v, m in items:
        it = (m, -v)
        if len(heap) < K:
            heapq.heappush(heap, it); r += 1
        elif it > heap[0]:
            heapq.heapreplace(heap, it); r += 1
    reps.append(r)
nb = len(counts[big])
print(f"largest user n = {nb}: heap insertions mean {statistics.mean(reps):.1f} over 20 shuffles; "
      f"k(1 + ln(n/k)) = {K * (1 + math.log(nb / K)):.1f}")

# ---- wall-clock on all users, as a ratio to sorting
print("\ntime for all 10,000 users (one laptop core), best of 3:")
base = None
for name, f in [("sort", topk_sort), ("heap", topk_heap), ("quickselect", topk_quickselect), ("bucket", topk_bucket),
                ("heapq.nsmallest", lambda c, k: heapq.nsmallest(k, c, key=lambda v: (-c[v], v)))]:
    best = 1e9
    for rep in range(3):
        t0 = time.perf_counter()
        for u in users:
            f(counts[u], K)
        best = min(best, time.perf_counter() - t0)
    base = base or best
    print(f"  {name:16s} {best * 1e6 / len(users):7.1f} us/user   {base / best:4.2f}x faster than sort")

for u in users:
    want = topk_sort(counts[u], K)
    assert topk_heap(counts[u], K) == want == topk_quickselect(counts[u], K) == topk_bucket(counts[u], K)
print("all four methods returned identical top-10 lists for every user")
