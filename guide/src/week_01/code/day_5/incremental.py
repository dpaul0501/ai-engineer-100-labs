"""Day 5 · incremental updates. When u and v become friends, which stored mutual counts change?
Replay the week's last 20,000 friendships on top of last night's graph and count the work."""
import random
from collections import Counter, defaultdict
from common import load_edges, build_adj, PAST, TOY_EDGES


def all_counts(adj):
    """The batch job (Day 1's self-join): m[x][y] = |N(x) & N(y)| for every pair with a mutual friend."""
    m = defaultdict(Counter)
    for w in range(len(adj)):                   # w is the mutual friend
        for x in adj[w]:
            for y in adj[w]:
                if x != y:
                    m[x][y] += 1
    return m


def add_friendship(adj, m, u, v, owned=None):
    """Update counts in place when u and v become friends. Returns the (row, column) pairs changed.
    If `owned` is given, only those rows are stored here (one shard's users)."""
    changed = []
    for x in adj[u]:                            # new two-hop paths x - u - v
        changed += [(x, v), (v, x)]
    for y in adj[v]:                            # new two-hop paths u - v - y
        changed += [(u, y), (y, u)]
    for a, b in changed:
        if owned is None or a in owned:
            m[a][b] += 1
    adj[u].add(v); adj[v].add(u)
    return changed


def top10(row, friends, me):
    return sorted((y for y in row if y != me and y not in friends), key=lambda y: (-row[y], y))[:10]


def tests():
    adj = build_adj(TOY_EDGES, 6)               # Dev (3) and Farid (5) become friends
    m = all_counts(adj)
    ch = add_friendship(adj, m, 3, 5)
    assert sorted(ch) == [(1, 5), (2, 3), (3, 2), (5, 1)]   # Ben-Farid and Chloe-Dev gain one
    assert m[1][5] == 2 and m[2][3] == 2 and m[0][4] == 2   # You and Esha unchanged
    rng = random.Random(0)
    for _ in range(30):                         # random graphs: incremental == recompute
        n = 30
        es = {tuple(sorted(rng.sample(range(n), 2))) for _ in range(80)}
        es = list(es)
        adj = build_adj(es[:50], n)
        m = all_counts(adj)
        for u, v in es[50:]:
            add_friendship(adj, m, u, v)
        fresh = all_counts(adj)
        assert {(x, y): c for x in m for y, c in m[x].items() if c} == \
               {(x, y): c for x in fresh for y, c in fresh[x].items()}


if __name__ == "__main__":
    tests()
    edges = load_edges()
    adj = build_adj(edges[:PAST])
    deg = [len(a) for a in adj]
    join_rows = sum(d * (d - 1) for d in deg)
    # keep full rows for a sample of 500 users (one shard's worth) to check exactness and top-10 churn
    rng = random.Random(0)
    S = set(rng.sample(range(len(adj)), 500))
    m = {x: Counter() for x in S}
    for x in S:
        for f in adj[x]:
            for y in adj[f]:
                if y != x:
                    m[x][y] += 1
    tops = {x: top10(m[x], adj[x], x) for x in S}
    touched, changed_counts, recompute = [], [], []
    row_updates = top_changes = 0
    for i, (u, v) in enumerate(edges[PAST:]):
        users = {u, v} | adj[u] | adj[v]
        touched.append(len(users))
        if i % 20 == 0:                         # cost of recomputing every touched user's row instead
            recompute.append(sum(sum(len(adj[f]) for f in adj[x]) for x in users))
        ch = add_friendship(adj, m, u, v, owned=S)
        changed_counts.append(len(ch) // 2)     # pairs, each stored in both directions
        rows = {}                               # sampled rows this friendship touched
        for a, b in ch:
            if a in S:
                rows.setdefault(a, set()).add(b)
        for a, bs in rows.items():
            old = tops[a]
            if a in (u, v):                     # a new friend leaves the list: full re-sort
                new = top10(m[a], adj[a], a)
            else:                               # counts only rose: only an incremented b can enter
                pool = set(old) | {b for b in bs if b not in adj[a]}
                new = sorted(pool, key=lambda y: (-m[a][y], y))[:10]
            row_updates += 1
            top_changes += new != old
            tops[a] = new
    for x in S:                                 # exactness: maintained rows == recompute
        fresh = Counter(y for f in adj[x] for y in adj[f] if y != x)
        assert +m[x] == fresh, x
        assert tops[x] == top10(fresh, adj[x], x)
    E = len(changed_counts)
    t = sorted(touched); c = sorted(changed_counts); r = sorted(recompute)
    print(f"replayed {E:,} new friendships on a graph of {PAST:,}")
    print(f"users touched per new friendship: mean {sum(t) / E:.1f}, median {t[E // 2]},"
          f" p99 {t[int(E * 0.99)]}, max {t[-1]} of {len(adj):,}")
    print(f"pairs whose count changes: mean {sum(c) / E:.1f}, p99 {c[int(E * 0.99)]}, max {c[-1]}")
    print(f"total pairs changed by all updates: {sum(c):,}; one batch join emits {join_rows:,} rows")
    print(f"recomputing every touched user's row instead: mean {sum(r) / len(r):,.0f} reads per new"
          f" friendship ({sum(r) / len(r) / (sum(c) / E):.0f}x the incremental update)")
    print(f"sampled users: {row_updates:,} times a new friendship changed their counts,"
          f" {top_changes:,} of them changed their top 10 ({top_changes / row_updates:.3f});"
          f" rows and top 10s match a full recompute")
    print("asserts passed")
