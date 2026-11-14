"""Turning logits into one token: softmax, temperature, top-k, top-p, and a categorical draw.

Masked tokens are represented by a logit of -inf. Every filter returns a new list of the same length.
"""

from __future__ import annotations

import random
from typing import Iterable, Sequence, TypeVar

T = TypeVar("T")
NEG_INF = float("-inf")


def log_softmax(logits: Sequence[float]) -> list[float]:
    """x_i - logsumexp(x), computed stably (subtract the max first). -inf stays -inf.

    Every logit -inf: ValueError. Must not overflow for logits like [1000.0, 1000.0].
    """
    raise NotImplementedError


def softmax(logits: Sequence[float]) -> list[float]:
    raise NotImplementedError


def argmax(logits: Sequence[float]) -> int:
    """The index of the largest logit; ties go to the lowest index."""
    raise NotImplementedError


def top_k_filter(logits: Sequence[float], k: int) -> list[float]:
    """Keep the k largest logits (ties to the lower index) and set the rest to -inf. k < 1: ValueError.

    Use a heap of size k: O(V log k), not a full sort.
    """
    raise NotImplementedError


def top_p_filter(logits: Sequence[float], p: float) -> list[float]:
    """Keep the smallest set of most likely tokens whose total probability is at least p (nucleus sampling).

    Order by probability, then by lower index. p outside (0, 1]: ValueError.
    """
    raise NotImplementedError


def categorical(probs: Sequence[float], rng: random.Random) -> int:
    """Draw index i with probability probs[i] / sum(probs): prefix sums plus binary search.

    Zero-probability indices are never drawn. A non-positive sum: ValueError.
    """
    raise NotImplementedError


class Sampler:
    """Temperature, then top-k, then top-p, then one categorical draw. Temperature 0 means argmax.

    The order matters: temperature changes the probabilities that top-p reads.
    """

    def __init__(self, temperature: float = 1.0, top_k: int | None = None, top_p: float | None = None):
        """temperature < 0: ValueError."""
        raise NotImplementedError

    def __call__(self, logits: Sequence[float], rng: random.Random) -> int:
        raise NotImplementedError


def reservoir_sample(stream: Iterable[T], k: int, rng: random.Random) -> list[T]:
    """k items chosen uniformly from a stream of unknown length, in one pass (Algorithm R).

    Fewer than k items: return them all. k < 0: ValueError. Use it to take a held-out split.
    """
    raise NotImplementedError
