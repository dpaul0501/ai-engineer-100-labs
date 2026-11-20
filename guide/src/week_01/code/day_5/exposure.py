"""Day 5 · fair exposure and cold start on the week's graph.
Exposure: rank every user's top 10 by mutual friends on last night's graph and measure who gets the
slots; then cap how often any one person can be shown per refresh. Cold start: where do the future
friends of users with almost no friends come from?"""
import random
from collections import Counter
from common import load_edges, load_groups, build_adj, PAST, N_USERS
from staleness import mutual_counts


def capped_lists(cands, order, cap, k=10):
    """Fill lists in `order`; a person already shown `cap` times this round is skipped."""
    shown, out = Counter(), {}
    for u in order:
        lst = []
        for v in cands[u]:
            if shown[v] < cap:
                lst.append(v); shown[v] += 1
                if len(lst) == k:
                    break
        out[u] = lst
    return out, shown


def test():
    cands = {0: [9, 8, 7], 1: [9, 8, 7], 2: [9, 8, 7]}
    out, shown = capped_lists(cands, [0, 1, 2], cap=2, k=2)
    assert out == {0: [9, 8], 1: [9, 8], 2: [7]} and shown[9] == 2


if __name__ == "__main__":
    test()
    edges = load_edges()
    adj = build_adj(edges[:PAST])
    future = {(min(u, v), max(u, v)) for u, v in edges[PAST:]}
    deg = [len(a) for a in adj]
    top1 = set(sorted(range(N_USERS), key=lambda x: -deg[x])[:N_USERS // 100])
    users = [u for u in range(N_USERS) if adj[u]]
    cands = {}
    for u in users:
        c = mutual_counts(adj, u)
        cands[u] = [y for y, _ in sorted(c.items(), key=lambda t: (-t[1], t[0]))[:50]]
    order = users[:]
    random.Random(0).shuffle(order)
    fut_top1 = sum((a in top1) + (b in top1) for a, b in future) / (2 * len(future))
    print(f"top 1% of users by degree are {fut_top1:.3f} of the endpoints of future friendships")
    print("cap per person   slots to top 1%   people shown at least once   hits@10 (future friendships)")
    for cap in [None, 200, 50, 20]:
        out, shown = capped_lists(cands, order, cap or 10**9)
        slots = sum(len(l) for l in out.values())
        hits = sum((min(u, v), max(u, v)) in future for u, l in out.items() for v in l)
        print(f"  {str(cap or 'none'):>12}   {sum(shown[v] for v in top1) / slots:15.3f}"
              f"   {len(shown) / N_USERS:26.3f}   {hits / slots:.4f}")
    # cold start: users with at most 2 friends last night who made new friends in the stream
    groups = load_groups()
    new = [(u, v) for a, b in future for u, v in ((a, b), (b, a)) if deg[u] <= 2]
    two_hop = sum(any(v in adj[f] for f in adj[u]) for u, v in new)
    grp = sum(bool(groups[u] & groups[v]) for u, v in new)
    either = sum(any(v in adj[f] for f in adj[u]) or bool(groups[u] & groups[v]) for u, v in new)
    few = sorted(len(mutual_counts(adj, u)) for u in range(N_USERS) if deg[u] <= 2)
    print(f"cold start: {sum(d <= 2 for d in deg):,} users with <= 2 friends; median two-hop candidates"
          f" {few[len(few) // 2]}; of their {len(new):,} future friendships, two-hop finds"
          f" {two_hop / len(new):.3f}, shared group {grp / len(new):.3f}, either {either / len(new):.3f}")
    print("asserts passed")
