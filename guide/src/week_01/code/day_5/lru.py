"""Day 5 · LRU cache (LeetCode 146) in front of the suggestion store, and its hit rate on a
skewed request stream: each request comes from a user with probability proportional to activity."""
import random
from collections import OrderedDict
from itertools import accumulate
from common import load_edges, build_adj


class LRUCache:
    """LeetCode 146: get and put in O(1). A hash map plus a recency order."""
    def __init__(self, capacity):
        self.cap = capacity
        self.d = OrderedDict()                   # least recently used first

    def get(self, key):
        if key not in self.d:
            return -1
        self.d.move_to_end(key)                  # now the most recent
        return self.d[key]

    def put(self, key, value):
        if key in self.d:
            self.d.move_to_end(key)
        self.d[key] = value
        if len(self.d) > self.cap:
            self.d.popitem(last=False)           # evict the least recent


class Node:
    __slots__ = ("key", "val", "prev", "next")
    def __init__(self, key=0, val=0):
        self.key, self.val, self.prev, self.next = key, val, None, None


class LRUFromScratch:
    """The same cache with the doubly linked list written out; two sentinels avoid edge cases."""
    def __init__(self, capacity):
        self.cap, self.map = capacity, {}
        self.head, self.tail = Node(), Node()    # head.next = most recent, tail.prev = least
        self.head.next, self.tail.prev = self.tail, self.head

    def _unlink(self, x):
        x.prev.next, x.next.prev = x.next, x.prev

    def _push_front(self, x):
        x.prev, x.next = self.head, self.head.next
        self.head.next.prev = x
        self.head.next = x

    def get(self, key):
        x = self.map.get(key)
        if x is None:
            return -1
        self._unlink(x); self._push_front(x)
        return x.val

    def put(self, key, value):
        x = self.map.get(key)
        if x:
            x.val = value
            self._unlink(x); self._push_front(x)
            return
        if len(self.map) == self.cap:
            lru = self.tail.prev
            self._unlink(lru); del self.map[lru.key]
        x = Node(key, value)
        self.map[key] = x; self._push_front(x)


def hit_rate(stream, capacity):
    cache, hits = LRUCache(capacity), 0
    for u in stream:
        if cache.get(u) != -1:
            hits += 1
        else:
            cache.put(u, f"top-10 of {u}")       # a miss reads the store, then fills the cache
    return hits / len(stream)


def tests():
    for C in (LRUCache, LRUFromScratch):         # LeetCode 146's example
        c = C(2)
        c.put(1, 1); c.put(2, 2)
        assert c.get(1) == 1
        c.put(3, 3)                              # evicts 2
        assert c.get(2) == -1
        c.put(4, 4)                              # evicts 1
        assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4
    rng = random.Random(1)                       # the two versions agree on a random workload
    a, b = LRUCache(5), LRUFromScratch(5)
    for _ in range(5000):
        k = rng.randrange(12)
        if rng.random() < 0.5:
            assert a.get(k) == b.get(k)
        else:
            a.put(k, k * 7); b.put(k, k * 7)


if __name__ == "__main__":
    tests()
    adj = build_adj(load_edges())
    n = len(adj)
    activity = [len(a) + 1 for a in adj]         # requests proportional to activity (degree + 1)
    rng = random.Random(0)
    R = 200_000
    skewed = rng.choices(range(n), cum_weights=list(accumulate(activity)), k=R)
    uniform = [rng.randrange(n) for _ in range(R)]
    # HYPOTHETICAL sessions: half the requests repeat one of the last 100 requesters (a reload)
    session = []
    for u in skewed:
        session.append(rng.choice(session[-100:]) if session and rng.random() < 0.5 else u)
    total = sum(activity)
    ranked = sorted(activity, reverse=True)
    print(f"{R:,} requests over {n:,} users; top 1% of users send {sum(ranked[:n // 100]) / total:.3f}"
          f" of requests, top 10% send {sum(ranked[:n // 10]) / total:.3f}")
    print("cache size (share of users)   LRU hit, skewed   LRU hit, uniform   best fixed set, skewed   LRU hit, skewed + reloads")
    for frac in [0.01, 0.05, 0.10, 0.20]:
        c = int(n * frac)
        print(f"  {c:>6} ({frac:4.0%})             {hit_rate(skewed, c):8.3f}"
              f"         {hit_rate(uniform, c):8.3f}         {sum(ranked[:c]) / total:8.3f}"
              f"                 {hit_rate(session, c):8.3f}")
    print("asserts passed")
