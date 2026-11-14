"""The week's graph: loading, adjacency sets, the temporal split, and work per request.

An edge is a tuple (u, v, t) with u < v and t the order in which the friendship formed (0 = first).
Users are the integers 0 .. n-1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

Edge = tuple[int, int, int]


def load_edges(path: str | Path) -> list[Edge]:
    """Read data/edges.csv (header u,v,t) into a list of (u, v, t), in file order, with u < v."""
    raise NotImplementedError


def load_users(path: str | Path) -> tuple[list[int], list[list[int]]]:
    """Read data/users.csv (header user,city,groups) into (city, groups).

    city[u] is an int; groups[u] is a sorted list of distinct group ids (the column is space-separated).
    """
    raise NotImplementedError


def adjacency(edges: Iterable[Sequence[int]], n: int) -> list[set[int]]:
    """adj[u] = N(u), the set of u's friends. Undirected: v in adj[u] exactly when u in adj[v].

    Only the first two fields of each edge are used. Duplicate edges collapse.
    A self-loop (u == v) or an id outside 0..n-1: ValueError.
    """
    raise NotImplementedError


def temporal_split(edges: Sequence[Edge], frac: float = 0.8) -> tuple[list[Edge], list[Edge]]:
    """Sort by t, then return (past, future): the first int(len * frac) edges and the rest.

    The split is by time, never by position in the input, so shuffled input gives the same result.
    frac outside the open interval (0, 1): ValueError.
    """
    raise NotImplementedError


def work(adj: Sequence[set[int]], u: int) -> int:
    """W(u) = sum of deg(f) over u's friends f: the adjacency entries the exact baseline reads for u."""
    raise NotImplementedError
