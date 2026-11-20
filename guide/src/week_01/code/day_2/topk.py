# Day 2 · the static top k: four ways to pick the k best candidates from a dict
# count = {candidate id: mutual-friend count}. "Best" = most mutual friends; ties go to the smaller id.
import heapq
import random


def topk_sort(count, k):
    """O(n log n): sort every candidate, keep the first k."""
    return sorted(count, key=lambda v: (-count[v], v))[:k]


def topk_heap(count, k):
    """O(n log k) time, O(k) memory: keep the k best seen so far; the worst of them sits on top."""
    if k <= 0:
        return []
    heap = []                                   # items (m, -v): the root is the worst one kept
    for v, m in count.items():
        item = (m, -v)                          # bigger is better: more friends, then smaller id
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:                    # beats the worst kept: replace it
            heapq.heapreplace(heap, item)
    return [-nv for m, nv in sorted(heap, reverse=True)]


def topk_quickselect(count, k, seed=0):
    """O(n) on average: split around a random pivot, keep only the side that holds the answer."""
    rng = random.Random(seed)
    keys = [(-m, v) for v, m in count.items()]  # distinct keys; smaller is better
    best = []
    while k > 0 and keys:
        p = rng.choice(keys)
        better = [x for x in keys if x < p]
        if len(better) >= k:
            keys = better                       # all k answers are better than the pivot
        else:
            best += better + [p]                # all of these are answers
            k -= len(better) + 1
            keys = [x for x in keys if x > p]
    return [v for _, v in sorted(best)]


def topk_bucket(count, k):
    """O(n + max count): counts are small whole numbers, so drop each candidate in the bucket of
    its count and walk the buckets from the top. Only the last bucket touched needs ordering."""
    if not count:
        return []
    buckets = [[] for _ in range(max(count.values()) + 1)]
    for v, m in count.items():
        buckets[m].append(v)
    out = []
    for m in range(len(buckets) - 1, 0, -1):
        need = k - len(out)
        if need == 0:
            break
        out += heapq.nsmallest(need, buckets[m])   # smallest ids first inside a bucket
    return out


METHODS = {"sort": topk_sort, "heap": topk_heap, "quickselect": topk_quickselect, "bucket": topk_bucket}

# The running example: You's candidates. Esha 2, Dev 1, Farid 1.
DEV, ESHA, FARID = 3, 4, 5
you = {DEV: 1, ESHA: 2, FARID: 1}
for name, f in METHODS.items():
    assert f(you, 2) == [ESHA, DEV], name        # Dev beats Farid on the tie: smaller id
    assert f(you, 10) == [ESHA, DEV, FARID], name
    assert f(you, 0) == [] and f({}, 3) == [], name

# Random tests against sorting, with many ties (counts drawn from a small range).
rng = random.Random(1)
for trial in range(2000):
    n = rng.randint(0, 60)
    ids = rng.sample(range(1000), n)
    count = {v: rng.randint(1, rng.choice([2, 5, 40])) for v in ids}
    k = rng.randint(0, 15)
    want = topk_sort(count, k)
    for name, f in METHODS.items():
        assert f(count, k) == want, (name, count, k)

if __name__ == "__main__":
    print("top 2 for You:", topk_heap(you, 2), "(Esha, Dev)")
    print("all four methods agree on 2,000 random dicts")
