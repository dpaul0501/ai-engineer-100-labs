"""Day 5 · how stale does a nightly top-10 get?  Precompute every sampled user's top 10 on
last night's graph (first 80,000 friendships), replay the next friendships from the week's
stream without refreshing, and compare the stored lists with fresh ones."""
import random
from collections import Counter
from common import load_edges, build_adj, PAST, TOY_EDGES


def mutual_counts(adj, u):
    """Day 1's count for one user: candidate -> number of mutual friends."""
    c = Counter()
    for f in adj[u]:
        for y in adj[f]:
            if y != u and y not in adj[u]:
                c[y] += 1
    return c


def top_k(counts, k=10):
    """Day 2's top k, ties broken by smaller id."""
    return [y for y, _ in sorted(counts.items(), key=lambda t: (-t[1], t[0]))[:k]]


def compare(stored, adj, u, k=10):
    """One user's stored list against the live graph."""
    live = mutual_counts(adj, u)
    fresh = top_k(live, k)
    kth = live[fresh[-1]] if len(fresh) == k else 0
    friend_shown = sum(y in adj[u] for y in stored)
    # tie-aware: a stored pick is still fine if it is not a friend and as good as the live k-th
    still_ok = all(y not in adj[u] and live[y] >= kth for y in stored) and len(stored) >= len(fresh)
    return {
        "changed": set(stored) != set(fresh),
        "slots_changed": len(set(fresh) - set(stored)),
        "friend_shown": friend_shown > 0,
        "materially_stale": not still_ok,
    }


def test_toy():
    adj = build_adj(TOY_EDGES, 6)
    assert top_k(mutual_counts(adj, 0)) == [4, 3, 5]        # Esha 2, Dev 1, Farid 1
    stored = top_k(mutual_counts(adj, 0))
    adj[0].add(4); adj[4].add(0)                             # You and Esha connect
    r = compare(stored, adj, 0)
    assert r["friend_shown"] and r["changed"] and r["materially_stale"]


if __name__ == "__main__":
    test_toy()
    edges = load_edges()
    adj = build_adj(edges[:PAST])
    rng = random.Random(0)
    users = rng.sample([u for u in range(len(adj)) if adj[u]], 2000)
    stored = {u: top_k(mutual_counts(adj, u)) for u in users}
    stored_counts = {u: mutual_counts(adj, u) for u in users}
    users_set = set(users)
    touched = set()
    checkpoints = [100, 500, 1000, 2000, 5000, 10000, 20000]
    done = 0
    print("new_edges  growth  touched  changed  slots_changed  friend_shown  materially_stale  feature_drift")
    for x in checkpoints:
        for u, v in edges[PAST + done:PAST + x]:
            touched |= {u, v} | adj[u] | adj[v]   # endpoints and their friends: counts change
            adj[u].add(v); adj[v].add(u)
        done = x
        rs = [compare(stored[u], adj, u) for u in users]
        # training-serving skew: the mutual-count feature of a stored candidate, as stored vs live
        pairs = drift = 0
        for u in users:
            live = mutual_counts(adj, u)
            for y in stored[u]:
                pairs += 1
                drift += live.get(y, 0) != stored_counts[u][y]
        n = len(users)
        print(f"{x:>9}  {x / PAST:6.1%}  {len(touched & users_set) / n:7.3f}"
              f"  {sum(r['changed'] for r in rs) / n:7.3f}"
              f"  {sum(r['slots_changed'] for r in rs) / n:13.2f}"
              f"  {sum(r['friend_shown'] for r in rs) / n:12.3f}"
              f"  {sum(r['materially_stale'] for r in rs) / n:16.3f}"
              f"  {drift / pairs:13.3f}")
    print("asserts passed")
