"""Approximate candidate generation: read fewer adjacency lists.

Two tools. sample_counts is the estimator from Day 4: unbiased, with hypergeometric variance.
budgeted_candidates is the serving policy: never read more than `budget` adjacency entries,
and optionally never read a hub's list at all.
"""

from __future__ import annotations

from typing import Sequence


def sample_counts(adj: Sequence[set[int]], u: int, s: int, seed: int = 0) -> dict[int, float]:
    """Pick s of u's d friends uniformly at random without replacement; return {v: (d / s) * count(v)}.

    count(v) = how many sampled friends are friends with v; v is never u or a friend of u.
    E[estimate] = m(u, v) exactly. s = d gives the exact counts (as floats).
    Deterministic: the same (adj, u, s, seed) gives the same result; different seeds, different samples.
    s outside 1..d: ValueError.
    """
    raise NotImplementedError


def budgeted_candidates(adj: Sequence[set[int]], u: int, budget: int, cap: int | None = None,
                        seed: int = 0) -> tuple[dict[int, int], int]:
    """Partial mutual counts under a read budget. Returns (counts, reads).

    Visit u's friends in a random order fixed by (seed, u). For each friend f:
      - if cap is not None and deg(f) > cap, skip f (a hub);
      - if reads + deg(f) > budget, skip f and go on to the next friend;
      - otherwise read adj[f]: reads += deg(f), and count every v that is not u and not a friend of u.
    Invariants: reads <= budget; counts[v] <= m(u, v); budget >= W(u) and cap None give the exact counts.
    budget < 0 or cap < 1: ValueError. Deterministic.
    """
    raise NotImplementedError
