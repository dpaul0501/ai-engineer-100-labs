# Day 2 · top k when the data keeps arriving.
# KthLargest (LeetCode 703), MedianFinder (295), Misra-Gries, Space-Saving, Count-Min, a sliding window.
import heapq
import math
import random
from collections import Counter, deque


class KthLargest:
    """703: a size-k min-heap; its root is the k-th largest number seen so far."""

    def __init__(self, k, nums):
        self.k, self.heap = k, []
        for x in nums:
            self.add(x)

    def add(self, val):
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, val)
        elif val > self.heap[0]:
            heapq.heapreplace(self.heap, val)
        return self.heap[0]


class MedianFinder:
    """295: lower half in a max-heap (stored negated), upper half in a min-heap; len(lo) - len(hi) is 0 or 1."""

    def __init__(self):
        self.lo, self.hi = [], []

    def addNum(self, num):
        heapq.heappush(self.lo, -num)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))   # the largest of the lower half moves up
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def findMedian(self):
        if len(self.lo) > len(self.hi):
            return float(-self.lo[0])
        return (-self.lo[0] + self.hi[0]) / 2


class QuantileFinder:
    """Any running percentile with the same two heaps: lo keeps the ceil(q*n) smallest numbers,
    so its largest one is the nearest-rank q-quantile. q = 0.5 gives the lower median."""

    def __init__(self, q):
        self.q, self.n, self.lo, self.hi = q, 0, [], []

    def add(self, num):
        self.n += 1
        heapq.heappush(self.lo, -num)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))
        while len(self.lo) < math.ceil(self.q * self.n):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def value(self):
        return -self.lo[0]


class MisraGries:
    """m counters. Each estimate is an undercount by at most N/(m+1) after N arrivals."""

    def __init__(self, m):
        self.m, self.c = m, {}

    def add(self, x):
        if x in self.c:
            self.c[x] += 1
        elif len(self.c) < self.m:
            self.c[x] = 1
        else:                                   # no room: every counter pays one, x included
            for y in list(self.c):
                self.c[y] -= 1
                if self.c[y] == 0:
                    del self.c[y]

    def estimate(self, x):
        return self.c.get(x, 0)


class SpaceSaving:
    """m counters. A new item takes over the smallest counter and inherits its count + 1,
    so each estimate is an overcount by at most N/m; the item's error is stored with it."""

    def __init__(self, m):
        self.m, self.c, self.err = m, {}, {}
        self.heap = []                          # (count, item), with stale entries skipped lazily

    def add(self, x):
        if x in self.c:
            self.c[x] += 1
        elif len(self.c) < self.m:
            self.c[x], self.err[x] = 1, 0
        else:
            while True:                         # find the current smallest counter
                cnt, y = heapq.heappop(self.heap)
                if self.c.get(y) == cnt:
                    break
            del self.c[y], self.err[y]
            self.c[x], self.err[x] = cnt + 1, cnt   # x may have been seen up to cnt times before
        heapq.heappush(self.heap, (self.c[x], x))
        if len(self.heap) > 4 * self.m:         # drop stale entries now and then
            self.heap = [(c, y) for y, c in self.c.items()]
            heapq.heapify(self.heap)

    def estimate(self, x):
        return self.c.get(x, 0)

    def top(self, k):
        return heapq.nsmallest(k, self.c, key=lambda y: (-self.c[y], y))


class CountMin:
    """d rows of w counters. An estimate never undercounts, and overcounts by more than
    (e/w)·N with probability at most e^-d. It stores no ids, so a size-k heap keeps the candidates."""

    P = (1 << 61) - 1

    def __init__(self, w, d, k, seed=0):
        rng = random.Random(seed)
        self.w, self.k = w, k
        self.ab = [(rng.randrange(1, self.P), rng.randrange(self.P)) for _ in range(d)]
        self.rows = [[0] * w for _ in range(d)]
        self.best = {}                          # the k items with the largest estimates so far

    def _cells(self, x):
        return [((a * x + b) % self.P) % self.w for a, b in self.ab]

    def add(self, x):
        est = None
        for row, j in zip(self.rows, self._cells(x)):
            row[j] += 1
            est = row[j] if est is None else min(est, row[j])
        if x in self.best or len(self.best) < self.k:
            self.best[x] = est
        else:
            worst = min(self.best, key=lambda y: (self.best[y], -y))
            if (est, -x) > (self.best[worst], -worst):
                del self.best[worst]
                self.best[x] = est

    def estimate(self, x):
        return min(row[j] for row, j in zip(self.rows, self._cells(x)))

    def top(self, k):
        return sorted(self.best, key=lambda y: (-self.estimate(y), y))[:k]


class WindowCounts:
    """Exact counts over the last W arrivals: add the newcomer, forget the one that fell out."""

    def __init__(self, W):
        self.W, self.q, self.c = W, deque(), Counter()

    def add(self, x):
        self.q.append(x)
        self.c[x] += 1
        if len(self.q) > self.W:
            old = self.q.popleft()
            self.c[old] -= 1
            if self.c[old] == 0:
                del self.c[old]


# ---- tests
kl = KthLargest(3, [4, 5, 8, 2])                # LeetCode 703's example
assert [kl.add(x) for x in [3, 5, 10, 9, 4]] == [4, 5, 5, 8, 8]

mf = MedianFinder()
seen = []
rng = random.Random(0)
for _ in range(500):
    x = rng.randint(-50, 50)
    mf.addNum(x); seen.append(x)
    s = sorted(seen); n = len(s)
    assert mf.findMedian() == (s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2)

for q in (0.5, 0.9, 0.99):
    qf, seen = QuantileFinder(q), []
    for _ in range(400):
        x = rng.randint(0, 30)
        qf.add(x); seen.append(x)
        assert qf.value() == sorted(seen)[math.ceil(q * len(seen)) - 1]

for trial in range(30):
    rng = random.Random(trial)
    N, m = 3000, rng.choice([5, 20, 60])
    stream = [int(rng.paretovariate(1.2)) % 400 for _ in range(N)]
    true = Counter(stream)
    mg, ss, cm = MisraGries(m), SpaceSaving(m), CountMin(w=64, d=4, k=10, seed=trial)
    for x in stream:
        mg.add(x); ss.add(x); cm.add(x)
    for x in true:
        assert true[x] - N / (m + 1) <= mg.estimate(x) <= true[x]               # undercount, bounded
        if x in ss.c:
            assert true[x] <= ss.estimate(x) <= true[x] + ss.err[x] <= true[x] + N / m   # overcount, bounded
        else:
            assert true[x] <= N / m                                              # dropped items were small
        assert cm.estimate(x) >= true[x]                                         # never undercounts
    for x, c in true.items():                   # heavy hitters are never lost
        if c > N / m:
            assert x in ss.c
        if c > N / (m + 1):
            assert x in mg.c

wc = WindowCounts(3)
for x in "aabca":
    wc.add(x)
assert dict(wc.c) == {"b": 1, "c": 1, "a": 1}   # the last three: b, c, a

if __name__ == "__main__":
    print("703 example:", [4, 5, 5, 8, 8])
    print("median and quantiles match sorting; Misra-Gries, Space-Saving and Count-Min bounds hold on 30 random skewed streams")
