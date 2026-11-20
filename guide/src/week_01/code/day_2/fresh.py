# Day 2 · keep every user's top k exact while friendships arrive one at a time.
import heapq
from collections import defaultdict


class FreshTopK:
    def __init__(self, k=10):
        self.k = k
        self.friends = defaultdict(set)
        self.count = defaultdict(dict)   # user -> {candidate: mutual friends}, always exact
        self.top = defaultdict(list)     # user -> sorted (-count, id), at most k long
        self.changes = self.top_changes = self.recomputes = 0

    def bump(self, x, y):
        """y gained one mutual friend with x. Counts only grow here, so x's top k changes
        only if y is already in it or now beats the worst of it."""
        self.changes += 1
        c = self.count[x][y] = self.count[x].get(y, 0) + 1
        t = self.top[x]
        for i, (_, v) in enumerate(t):
            if v == y:
                t[i] = (-c, y)
                if i > 0 and t[i] < t[i - 1]:
                    t.sort(); self.top_changes += 1
                return
        if len(t) < self.k or (-c, y) < t[-1]:
            t.append((-c, y)); t.sort(); del t[self.k:]; self.top_changes += 1

    def unlink(self, x, y):
        """x and y just became friends, so y stops being x's candidate. If y was in x's top k,
        the next best must be found again from the full dict."""
        if self.count[x].pop(y, None) is not None and any(v == y for _, v in self.top[x]):
            self.recomputes += 1
            self.top[x] = sorted(heapq.nsmallest(self.k, ((-c, v) for v, c in self.count[x].items())))

    def add_friendship(self, a, b):
        self.unlink(a, b); self.unlink(b, a)
        for f in self.friends[b]:            # b becomes a mutual friend of a and each f
            if f != a and f not in self.friends[a]:
                self.bump(a, f); self.bump(f, a)
        for f in self.friends[a]:            # a becomes a mutual friend of b and each f
            if f != b and f not in self.friends[b]:
                self.bump(b, f); self.bump(f, b)
        self.friends[a].add(b); self.friends[b].add(a)

    def suggest(self, u):
        return [v for _, v in self.top[u]]


# The running example, built one friendship at a time.
YOU, BEN, CHLOE, DEV, ESHA, FARID = range(6)
s = FreshTopK(k=2)
for a, b in [(YOU, BEN), (YOU, CHLOE), (BEN, CHLOE), (BEN, DEV), (BEN, ESHA), (CHLOE, ESHA), (CHLOE, FARID)]:
    s.add_friendship(a, b)
assert s.count[YOU] == {DEV: 1, ESHA: 2, FARID: 1} and s.suggest(YOU) == [ESHA, DEV]
before = s.changes
s.add_friendship(DEV, CHLOE)                 # Chloe now vouches for Dev with You, Esha and Farid
assert s.changes - before == 6               # Dev-You, Dev-Esha, Dev-Farid, both directions
assert CHLOE not in s.count[DEV]             # a friend is no longer a candidate
assert s.count[YOU] == {DEV: 2, ESHA: 2, FARID: 1}
assert s.suggest(YOU) == [DEV, ESHA]         # a tie at 2; Dev has the smaller id

if __name__ == "__main__":
    print("You's top 2 before Dev-Chloe: Esha, Dev; after: Dev, Esha (6 count changes)")
