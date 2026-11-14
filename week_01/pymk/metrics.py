"""Measuring: candidate fidelity, ranking quality, uncertainty, latency."""

from __future__ import annotations

from typing import Callable, Collection, Sequence

import numpy as np


def recall_at_k(recommended: Sequence[int], relevant: Collection[int], k: int) -> float:
    """|recommended[:k] ∩ relevant| / |relevant|.

    Against the exact top-10 it measures candidate fidelity; against future friends, ranking quality.
    Empty relevant or k < 1: ValueError.
    """
    raise NotImplementedError


def auc(scores: Sequence[float], labels: Sequence[int]) -> float:
    """P(score of a random positive > score of a random negative), ties counting 1/2 (Mann–Whitney U).

    O(n log n) with average ranks, not the O(P·N) double loop. Labels must be 0/1 with both present,
    and the lengths must match: else ValueError.
    """
    raise NotImplementedError


def bootstrap_ci(values: Sequence[float], stat: Callable = np.mean, n_boot: int = 1000,
                 alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    """Percentile bootstrap: resample `values` with replacement n_boot times (np.random.default_rng(seed)),
    compute stat on each, return the alpha/2 and 1 - alpha/2 quantiles. Resample users, not pairs,
    when values are per-user. Empty values or alpha outside (0, 1): ValueError. Deterministic."""
    raise NotImplementedError


def percentile(samples: Sequence[float], q: float) -> float:
    """Nearest rank: the smallest sample x such that at least q% of samples are <= x,
    i.e. sorted(samples)[ceil(q/100 * n) - 1]. Empty samples or q outside (0, 100]: ValueError."""
    raise NotImplementedError
