"""Serving: an LRU cache of ranked candidates, and the final eligibility filter on every response.

The cache holds rankings; it never decides eligibility. Blocks, opt-outs and new friendships
must take effect on the very next response, even when the ranking comes from the cache.
"""

from __future__ import annotations

from typing import Callable, Mapping, Sequence


class LRUCache:
    """A fixed-capacity map that evicts the least recently used key. get and put are O(1).

    get(key) and put(key, value) both make key the most recently used.
    """

    def __init__(self, capacity: int):
        """capacity < 1: ValueError."""
        raise NotImplementedError

    def get(self, key, default=None):
        raise NotImplementedError

    def put(self, key, value) -> None:
        raise NotImplementedError

    def pop(self, key, default=None):
        """Remove key (used for invalidation) and return its value, or default."""
        raise NotImplementedError

    def __contains__(self, key) -> bool:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class PYMKService:
    """recommend(u) = the first k eligible users of u's cached ranking.

    scorer(adj, u) -> {v: score}; the default is exact.mutual_counts. The ranking is every scored
    candidate ordered by score descending, then id ascending, and that whole list is cached per user.
    Eligible v: v != u, v not a friend of u, v not hidden, u has not blocked v, v has not blocked u.
    The service keeps its own copy of adj; the caller's graph is never mutated.
    """

    def __init__(self, adj: Sequence[set[int]], *, scorer: Callable | None = None,
                 blocked: Mapping[int, set[int]] | None = None, hidden=None, cache_size: int = 1024):
        raise NotImplementedError

    def recommend(self, u: int, k: int = 10) -> list[int]:
        """Up to k user ids. A cache hit or miss is counted in stats(). Unknown u or k < 0: ValueError."""
        raise NotImplementedError

    def block(self, u: int, v: int) -> None:
        """u blocks v. From now on neither is ever suggested to the other."""
        raise NotImplementedError

    def hide(self, v: int) -> None:
        """v opts out of being suggested to anyone."""
        raise NotImplementedError

    def add_friendship(self, u: int, v: int) -> set[int]:
        """Add u–v to the graph, invalidate every user whose candidate counts can change, and return
        that set: {u, v} ∪ N(u) ∪ N(v) (after the update). Nobody else is invalidated. u == v: ValueError."""
        raise NotImplementedError

    def stats(self) -> dict[str, int]:
        """{"hits": ..., "misses": ...} since construction."""
        raise NotImplementedError
