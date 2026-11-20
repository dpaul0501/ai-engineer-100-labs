# Shared helpers for Day 2's measurements: read the week's friendships, count candidates.
import csv
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "edges.csv"


def load_edges(path=DATA):
    """Friendships (u, v) in the order they formed (column t)."""
    with open(path) as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: int(r["t"]))
    return [(int(r["u"]), int(r["v"])) for r in rows]


def friend_lists(edges):
    friends = defaultdict(set)
    for u, v in edges:
        friends[u].add(v)
        friends[v].add(u)
    return friends


def candidate_counts(friends, u):
    """Day 1's dict: candidate -> number of mutual friends with u (not u, not a friend already)."""
    mine = friends[u]
    count = {}
    for f in mine:
        for v in friends[f]:
            if v != u and v not in mine:
                count[v] = count.get(v, 0) + 1
    return count
