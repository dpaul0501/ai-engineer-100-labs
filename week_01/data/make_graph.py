"""Generate the Week 1 synthetic social graph: users, groups, cities, and timestamped friendships.

Deterministic (seed 0). Edges form one at a time; each new friendship is either
triadic closure (a friend of a friend), a shared group, or a random popular user,
so the graph has heavy-tailed degrees, clustering, and a learnable signal.
"""
import csv
import random
import sys
from pathlib import Path

N_USERS, N_EDGES, N_GROUPS, N_CITIES = 10_000, 100_000, 200, 20
P_CLOSE, P_GROUP = 0.45, 0.35          # the rest is a random popular user


def make(seed=0):
    rng = random.Random(seed)
    social = [rng.paretovariate(1.6) for _ in range(N_USERS)]     # heavy-tailed sociability
    gsize = [1.0 / (g + 1) for g in range(N_GROUPS)]                # Zipf-sized groups
    city_w = [1.0 / (c + 1) for c in range(N_CITIES)]
    groups = [rng.choices(range(N_GROUPS), gsize, k=rng.randint(1, 3)) for _ in range(N_USERS)]
    groups = [sorted(set(g)) for g in groups]
    city = rng.choices(range(N_CITIES), city_w, k=N_USERS)
    members = [[] for _ in range(N_GROUPS)]
    for u, gs in enumerate(groups):
        for g in gs:
            members[g].append(u)
    adj = [set() for _ in range(N_USERS)]
    adjl = [[] for _ in range(N_USERS)]                              # list copy for O(1) random choice
    cum = []
    total = 0.0
    for s in social:
        total += s; cum.append(total)
    import bisect
    def popular():
        return bisect.bisect(cum, rng.random() * total)
    edges, t = [], 0
    while len(edges) < N_EDGES:
        u = popular()
        r = rng.random()
        if r < P_CLOSE and adjl[u]:
            f = rng.choice(adjl[u])
            if not adjl[f]:
                continue
            v = rng.choice(adjl[f])
        elif r < P_CLOSE + P_GROUP:
            v = rng.choice(members[rng.choice(groups[u])])
        else:
            v = popular()
        if v == u or v in adj[u] or v >= N_USERS:
            continue
        adj[u].add(v); adj[v].add(u); adjl[u].append(v); adjl[v].append(u)
        edges.append((min(u, v), max(u, v), t)); t += 1
    return edges, groups, city


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
    out.mkdir(parents=True, exist_ok=True)
    edges, groups, city = make()
    with open(out / "edges.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["u", "v", "t"]); w.writerows(edges)
    with open(out / "users.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["user", "city", "groups"])
        for u in range(N_USERS):
            w.writerow([u, city[u], " ".join(map(str, groups[u]))])
    print(len(edges), "edges written to", out)
