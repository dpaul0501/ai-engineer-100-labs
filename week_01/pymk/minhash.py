"""MinHash and LSH: find users whose friend sets overlap, without comparing every pair.

Hash family (fixed so results are reproducible): with p = 2**31 - 1 and NumPy's
default_rng(seed), draw a_i in [1, p) and b_i in [0, p) for i < num_perm; h_i(x) = (a_i x + b_i) mod p.
Items must be ints in [0, p). Compute in uint64: a_i x + b_i < 2**62 cannot overflow.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np

PRIME = (1 << 31) - 1


def jaccard(a: Iterable[int], b: Iterable[int]) -> float:
    """|A ∩ B| / |A ∪ B|, and 0.0 when both are empty."""
    raise NotImplementedError


class MinHash:
    def __init__(self, num_perm: int = 128, seed: int = 0):
        """num_perm < 1: ValueError."""
        raise NotImplementedError

    def signature(self, items: Iterable[int]) -> np.ndarray:
        """Array of shape (num_perm,), dtype uint64: entry i is min over x in items of h_i(x).

        Vectorize over the hash functions. Empty items, or an item outside [0, p): ValueError.
        """
        raise NotImplementedError


def estimate_jaccard(sig_a: np.ndarray, sig_b: np.ndarray) -> float:
    """The share of positions where the signatures agree. P[agree at i] = J, so this is unbiased,
    with variance J(1 - J) / num_perm. Different shapes: ValueError."""
    raise NotImplementedError


class LSHIndex:
    """Banding: split a signature of length bands * rows into `bands` bands of `rows` values.
    Two keys are candidates when at least one band is identical: P = 1 - (1 - s**rows)**bands."""

    def __init__(self, bands: int, rows: int):
        """bands < 1 or rows < 1: ValueError."""
        raise NotImplementedError

    def add(self, key: int, sig: np.ndarray) -> None:
        """Index key under each of its band values. Signature length != bands * rows: ValueError."""
        raise NotImplementedError

    def query(self, sig: np.ndarray) -> set[int]:
        """Every key that shares at least one band with sig (may include the querying key itself)."""
        raise NotImplementedError


def collision_probability(s: float, bands: int, rows: int) -> float:
    """1 - (1 - s**rows)**bands: the chance that two sets with Jaccard s become candidates."""
    raise NotImplementedError
