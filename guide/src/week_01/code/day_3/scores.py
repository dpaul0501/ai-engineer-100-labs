# Pair scores from the graph: mutual friends, Jaccard, Adamic-Adar, resource allocation.
# Measured on the time split: score with the first 80,000 friendships, check the next 20,000.
from collections import Counter
import math
from common import load_edges, adjacency, time_split, recall_at_k

def two_hop_scores(adj, u):
    """One two-step walk from u fills all four scores for every candidate v.
    z is a mutual friend of u and v; its degree d_z sets its weight."""
    cn, aa, ra = Counter(), Counter(), Counter()
    for z in adj[u]:
        dz = len(adj[z])                   # dz >= 2: z knows u and v
        for v in adj[z]:
            if v != u and v not in adj[u]:
                cn[v] += 1                 # mutual friends: every z votes 1
                aa[v] += 1 / math.log(dz)  # Adamic-Adar: a popular z votes less
                ra[v] += 1 / dz            # resource allocation: much less
    du = len(adj[u])
    jac = {v: c / (du + len(adj[v]) - c) for v, c in cn.items()}   # |N(u) ∪ N(v)| = du + dv - cn
    return {"mutual": cn, "jaccard": jac, "adamic_adar": aa, "resource": ra}

def top_k(score, k=10):
    """Highest score first; ties go to the smaller id."""
    return sorted(score, key=lambda v: (-score[v], v))[:k]

# The hub example: You know A (2 friends), B (3 friends) and H (6 friends).
# X is reached through A and B; Y through B and H; Z, P, Q, R only through H.
You, A, B, H, X, Y, Z, P, Q, R = range(10)
hub = adjacency([(You, A), (You, B), (You, H), (A, X), (B, X), (B, Y),
                 (H, Y), (H, Z), (H, P), (H, Q), (H, R)], 10)
s = two_hop_scores(hub, You)
assert s["mutual"][X] == s["mutual"][Y] == 2                          # counting ties X and Y
assert abs(s["adamic_adar"][X] - (1 / math.log(2) + 1 / math.log(3))) < 1e-12
assert round(s["adamic_adar"][X], 2) == 2.35 and round(s["adamic_adar"][Y], 2) == 1.47
assert round(s["resource"][X], 2) == 0.83 and round(s["resource"][Y], 2) == 0.50
assert s["jaccard"][X] == 2 / 3 and s["jaccard"][Y] == 2 / 3          # X: {A,B} vs {A,B,H}; Y: {B,H} vs {A,B,H}
assert round(s["jaccard"][Z], 2) == 0.33                               # {H} vs {A,B,H}
assert top_k(s["adamic_adar"], 2) == [X, Y] and top_k(s["mutual"], 2) == [X, Y]
assert top_k(s["resource"]) == [X, Y, Z, P, Q, R]

if __name__ == "__main__":
    edges = load_edges()
    past, future, truth = time_split(edges)
    Pg = adjacency(past)
    pairs = sum(len(f) for f in truth.values())
    print("past friendships", len(past), "future friendships", len(future))
    print("evaluated users", len(truth), "(user, future friend) pairs", pairs)
    print("evaluated users with no past friend (always score 0):", sum(1 for u in truth if not Pg[u]))
    print("future friends per evaluated user: mean %.2f" % (pairs / len(truth)))
    names = ["mutual", "jaccard", "adamic_adar", "resource"]
    ranked = {name: {} for name in names}
    reach = reach10 = 0.0
    ncand = []
    for u in truth:
        sc = two_hop_scores(Pg, u)
        ncand.append(len(sc["mutual"]))
        for name in names:
            ranked[name][u] = top_k(sc[name])
        found = len(truth[u].intersection(sc["mutual"]))
        reach += found / len(truth[u]); reach10 += min(found, 10) / len(truth[u])
    print("candidates per evaluated user: mean %.0f" % (sum(ncand) / len(ncand)))
    print("ceiling: future friends two steps away at the cut, mean per user %.4f; best possible recall@10 %.4f" %
          (reach / len(truth), reach10 / len(truth)))
    per_user = {}
    for name in names:
        r = recall_at_k(ranked[name], truth)
        per_user[name] = [len(truth[u].intersection(ranked[name][u])) / len(truth[u]) for u in truth]
        print("recall@10 %-12s %.4f" % (name, r))
    for name in ("adamic_adar", "resource", "jaccard"):
        d = [a - b for a, b in zip(per_user[name], per_user["mutual"])]
        mean = sum(d) / len(d); sd = math.sqrt(sum((x - mean) ** 2 for x in d) / (len(d) - 1))
        print("%s minus mutual: %+.4f (paired standard error %.4f); users better %d, worse %d" %
              (name, mean, sd / math.sqrt(len(d)), sum(x > 0 for x in d), sum(x < 0 for x in d)))
    # how popular are the people each score puts in the top 10 (past degree)?
    for name in names:
        ds = [len(Pg[v]) for u in truth for v in ranked[name][u]]
        ds.sort()
        print("median past degree of suggested people, %-12s %d" % (name, ds[len(ds) // 2]))
    # signals the graph cannot see: users.csv
    import random
    from common import load_users
    city, groups = load_users()
    fut = [(u, v) for u, v, _ in future]
    rng = random.Random(0)
    rnd = []
    while len(rnd) < 100_000:
        a, b = rng.randrange(len(Pg)), rng.randrange(len(Pg))
        if a != b and b not in Pg[a]:
            rnd.append((a, b))
    for label, pairs_ in (("future friendships", fut), ("random non-friend pairs", rnd)):
        g = sum(bool(groups[a] & groups[b]) for a, b in pairs_) / len(pairs_)
        c = sum(city[a] == city[b] for a, b in pairs_) / len(pairs_)
        m0 = sum(not (Pg[a] & Pg[b]) for a, b in pairs_) / len(pairs_)
        print("%s: share a group %.1f%%, same city %.1f%%, no mutual friend at the cut %.1f%%" %
              (label, 100 * g, 100 * c, 100 * m0))
