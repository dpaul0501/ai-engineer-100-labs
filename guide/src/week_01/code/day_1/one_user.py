# From one pair to one user: mutual-friend counts with everyone two steps away, in one pass.
import time
from friends import EXAMPLE, NAMES, load_friends

def mutual_counts(friends, u):
    """For every friend of a friend of u (not u, not already a friend): how many mutual friends.
    Reads each friend's list once, so the cost is the sum of u's friends' list lengths."""
    counts = {}
    for f in friends[u]:                   # each friend f of u ...
        for v in friends[f]:               # ... vouches for each of f's friends
            if v != u and v not in friends[u]:
                counts[v] = counts.get(v, 0) + 1
    return counts

def cost(friends, u):
    """Entries read by mutual_counts: the sum of the friends' list lengths."""
    return sum(len(friends[f]) for f in friends[u])

c = mutual_counts(EXAMPLE, 0)
assert c == {3: 1, 4: 2, 5: 1}                       # Dev 1, Esha 2 (Ben, Chloe), Farid 1
assert cost(EXAMPLE, 0) == 8                         # Ben's 4 entries + Chloe's 4

if __name__ == "__main__":
    print("You:", {NAMES[v]: n for v, n in sorted(c.items())}, "entries read", cost(EXAMPLE, 0))
    fr = load_friends()
    users = sorted(fr)
    for u in users[:300]:                            # same answer as one intersection per candidate
        mc = mutual_counts(fr, u)
        assert all(len(fr[u] & fr[v]) == n for v, n in mc.items())
    reads = {u: cost(fr, u) for u in users}
    cands = {}
    t0 = time.perf_counter()
    for u in users:
        cands[u] = len(mutual_counts(fr, u))
    secs = time.perf_counter() - t0
    # what one intersection per two-step person would cost: one hash lookup per id of the shorter list
    per_pair = {u: 0 for u in users}
    for u in users:
        for v in mutual_counts(fr, u):
            per_pair[u] += min(len(fr[u]), len(fr[v]))
    n = len(users)
    s = sorted(reads.values())
    worst = max(users, key=reads.get)
    print(f"entries read per user: mean {sum(s)/n:.0f}, median {s[n//2]}, worst {s[-1]} (user {worst}, {len(fr[worst])} friends)")
    print(f"two-step people per user: mean {sum(cands.values())/n:.0f}, worst user's {cands[worst]}")
    print(f"sum over all users of entries read {sum(s)} (= sum of squared list lengths)")
    print(f"one intersection per two-step person: mean {sum(per_pair.values())/n:.0f} lookups per user, "
          f"{sum(per_pair.values())/sum(s):.1f}x the counting pass")
    print(f"comparing with all {n-1} others (the reading's loop): {n-1} intersections per user")
    top = sorted(fr[worst], key=lambda f: -len(fr[f]))[:3]
    print(f"worst user's three largest friends' lists: {[len(fr[f]) for f in top]}, "
          f"{sum(len(fr[f]) for f in top)/reads[worst]:.0%} of what it reads")
    print(f"all {n} users counted in {secs:.2f} s on one laptop core ({secs/n*1e3:.2f} ms per user)")
    t0 = time.perf_counter(); mutual_counts(fr, worst); tw = time.perf_counter() - t0
    print(f"worst user alone: {tw*1e3:.2f} ms")
