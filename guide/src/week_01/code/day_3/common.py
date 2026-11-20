# Shared helpers for Day 3: load the week's graph, the six people, and the time split.
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
N_USERS = 10_000
TRAIN_EDGES = 80_000          # the time split: the first 80,000 friendships are "the past"
TEST_EDGES = 20_000           # the next 20,000 are "the future" we try to predict

def load_edges():
    """The week's friendships as (u, v, t), in the order they formed (t = 0, 1, 2, ...)."""
    with open(DATA / "edges.csv") as f:
        rows = list(csv.reader(f))[1:]
    edges = [(int(u), int(v), int(t)) for u, v, t in rows]
    assert [t for _, _, t in edges] == list(range(len(edges)))
    return edges

def load_users():
    """city[u] and groups[u] (a set) for every user."""
    city, groups = [], []
    with open(DATA / "users.csv") as f:
        for user, c, g in list(csv.reader(f))[1:]:
            assert int(user) == len(city)
            city.append(int(c)); groups.append({int(x) for x in g.split()})
    return city, groups

def adjacency(edges, n=N_USERS):
    """Friend lists: adj[u] is the set of u's friends. Each friendship is written twice."""
    adj = [set() for _ in range(n)]
    for u, v, *_ in edges:
        adj[u].add(v); adj[v].add(u)
    return adj

def time_split(edges):
    """Past = first TRAIN_EDGES friendships; future = the next TEST_EDGES.
    Evaluated users = everyone who gains at least one future friend."""
    past, future = edges[:TRAIN_EDGES], edges[TRAIN_EDGES:TRAIN_EDGES + TEST_EDGES]
    truth = {}
    for u, v, _ in future:
        truth.setdefault(u, set()).add(v); truth.setdefault(v, set()).add(u)
    return past, future, truth

def recall_at_k(ranked, truth, k=10):
    """Mean over evaluated users of |top k ∩ future friends| / |future friends|.
    ranked[u] is u's list (best first); a user with no list scores 0."""
    total = 0.0
    for u, fut in truth.items():
        top = ranked.get(u, [])[:k]
        total += len(fut.intersection(top)) / len(fut)
    return total / len(truth)

# The six people: You = 0, Ben = 1, Chloe = 2, Dev = 3, Esha = 4, Farid = 5
YOU, BEN, CHLOE, DEV, ESHA, FARID = range(6)
SIX = [(YOU, BEN), (YOU, CHLOE), (BEN, CHLOE), (BEN, DEV), (BEN, ESHA), (CHLOE, ESHA), (CHLOE, FARID)]
six = adjacency(SIX, 6)
assert six[YOU] == {BEN, CHLOE} and six[BEN] == {YOU, CHLOE, DEV, ESHA}
