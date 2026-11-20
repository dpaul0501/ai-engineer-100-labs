# Day 2 · top k across shards.
# merge_topk: each shard sends its own top k, sorted; a heap of list heads merges them (LeetCode 23's idea).
# split_topk: the same plan when one candidate's count is split across shards (it can be wrong).
# shuffle_topk: aggregate by candidate first, then pick (always right, ships everything).
# tput_topk: a three-round threshold algorithm (always right, ships far less).
import heapq
import math
import random
from collections import Counter

from topk import topk_sort


def local_top(count, k):
    """What one shard sends: its k best (count, id) pairs, best first."""
    return [(v, count[v]) for v in topk_sort(count, k)]


def merge_topk(lists, k):
    """lists: one best-first list of (id, count) per shard. Returns the k best ids overall.
    Exact when every id lives on exactly one shard. O(s + k log s) for s shards."""
    heap = [(-lst[0][1], lst[0][0], s, 0) for s, lst in enumerate(lists) if lst]
    heapq.heapify(heap)                          # one entry per shard: its best unsent item
    out = []
    while heap and len(out) < k:
        _, v, s, i = heapq.heappop(heap)         # the best head is the best item left anywhere
        out.append(v)
        if i + 1 < len(lists[s]):
            w, c = lists[s][i + 1]
            heapq.heappush(heap, (-c, w, s, i + 1))
    return out


def split_topk(partials, k):
    """partials: one dict per shard, candidate -> partial count. Each shard sends its local
    top k; the coordinator adds up what it received. Ships at most s*k pairs; can miss the winner."""
    got = Counter()
    for p in partials:
        for v, c in local_top(p, k):
            got[v] += c
    return topk_sort(got, k), sum(min(k, len(p)) for p in partials)


def shuffle_topk(partials, k):
    """Send every partial count to the candidate's owner, add, then pick: exact, ships everything."""
    total = Counter()
    for p in partials:
        total.update(p)
    return topk_sort(total, k), sum(len(p) for p in partials)


def tput_topk(partials, k):
    """Three rounds, exact. Round 1: each shard sends its top k; tau1 = the k-th best partial sum.
    Round 2: each shard sends every candidate whose partial count is >= tau1/s. A candidate it does
    not send has a partial below tau1/s there, which bounds its total from above. Round 3: fetch the
    missing partials of the candidates whose upper bound still reaches the k-th best lower bound."""
    s = len(partials)
    known = [dict() for _ in range(s)]           # what the coordinator has received from each shard
    for j, p in enumerate(partials):
        for v, c in local_top(p, k):
            known[j][v] = c
    shipped = sum(len(x) for x in known)

    def lower():
        lo = Counter()
        for x in known:
            lo.update(x)
        return lo

    lo = lower()
    tau1 = sorted(lo.values(), reverse=True)[k - 1] if len(lo) >= k else 0
    cut = math.ceil(tau1 / s)                    # a shard sends every partial >= tau1/s
    for j, p in enumerate(partials):
        for v, c in p.items():
            if c >= cut and v not in known[j]:
                known[j][v] = c
                shipped += 1
    lo = lower()
    tau2 = sorted(lo.values(), reverse=True)[k - 1] if len(lo) >= k else 0
    hidden = max(cut - 1, 0)                     # the most an unsent partial can be
    keep = [v for v in lo if lo[v] + hidden * sum(v not in x for x in known) >= tau2]
    total = {}
    for v in keep:                               # round 3: exact totals for the survivors
        for j, p in enumerate(partials):
            if v not in known[j] and v in p:
                shipped += 1
        total[v] = sum(p.get(v, 0) for p in partials)
    return topk_sort(total, k), shipped


# ---- the running example, one item per shard: exact
DEV, ESHA, FARID = 3, 4, 5
shards = [{ESHA: 2}, {DEV: 1, FARID: 1}]
assert merge_topk([local_top(c, 2) for c in shards], 2) == [ESHA, DEV]

# ---- the trap: Esha's mutual friends are split between two shards (hypothetical counts)
split = [{DEV: 3, ESHA: 2}, {FARID: 3, ESHA: 2}]   # truth: Esha 4, Dev 3, Farid 3
assert split_topk(split, 1)[0] == [DEV]             # each shard's top 1 hides Esha
assert shuffle_topk(split, 1)[0] == [ESHA]
assert tput_topk(split, 1)[0] == [ESHA]

# ---- random tests against the brute force
rng = random.Random(0)
for trial in range(3000):
    s, k = rng.randint(1, 6), rng.randint(1, 8)
    ids = range(rng.randint(0, 40))
    partials = [{v: rng.randint(1, rng.choice([2, 4, 9])) for v in ids if rng.random() < 0.5} for _ in range(s)]
    want = shuffle_topk(partials, k)[0]
    assert tput_topk(partials, k)[0] == want, (partials, k)
    total = sum(map(Counter, partials), Counter())
    owner = [{v: c for v, c in total.items() if v % s == j} for j in range(s)]   # each id on one shard
    assert merge_topk([local_top(o, k) for o in owner], k) == want

if __name__ == "__main__":
    print("one shard per item: merge is exact; split counts: local top 1 returns Dev, the truth is Esha")
    print("TPUT and shuffle agree with brute force on 3,000 random cases")
