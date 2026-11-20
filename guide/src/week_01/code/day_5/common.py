"""Shared helpers for Day 5: load the week's graph and build friend lists."""
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
N_USERS = 10_000
PAST = 80_000                     # the first 80,000 friendships are "last night's" graph


def load_edges():
    with open(DATA / "edges.csv") as f:
        r = csv.reader(f)
        next(r)
        return [(int(u), int(v)) for u, v, _t in r]


def load_groups():
    with open(DATA / "users.csv") as f:
        r = csv.reader(f)
        next(r)
        return {int(u): set(map(int, g.split())) for u, _c, g in r}


def build_adj(edges, n=N_USERS):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


# the running example: You 0, Ben 1, Chloe 2, Dev 3, Esha 4, Farid 5
TOY_EDGES = [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 4), (2, 5)]
