"""The exact baseline: rank friends of friends by the number of mutual friends.

m(u, v) = |N(u) ∩ N(v)| = (A²)_uv. Candidates C(u) = N(N(u)) minus N(u) minus {u}.
Cost: O(W(u) + |C(u)| log k) with W(u) = sum of friends' degrees.
"""

from __future__ import annotations

from typing import Collection, Mapping, Sequence


def mutual_counts(adj: Sequence[set[int]], u: int, blocked: Collection[int] = frozenset()) -> dict[int, int]:
    """{v: m(u, v)} for every candidate v with m(u, v) >= 1.

    Never contains u, a friend of u, or a user in `blocked`. u outside 0..len(adj)-1: ValueError.
    Do not touch any adjacency list except u's and its friends'.
    """
    raise NotImplementedError


def top_k(scores: Mapping[int, float], k: int) -> list[int]:
    """The k keys with the highest score, best first; ties go to the smaller id.

    Fewer than k keys: all of them. k < 0: ValueError. Use a size-k heap: O(n log k), not a full sort.
    """
    raise NotImplementedError


def suggest(adj: Sequence[set[int]], u: int, k: int = 10,
            blocked: Collection[int] = frozenset()) -> list[tuple[int, int]]:
    """The top k candidates as (v, m(u, v)), ordered by m descending, then v ascending.

    Same eligibility rules as mutual_counts. k < 0 or an unknown u: ValueError. Deterministic.
    """
    raise NotImplementedError
