"""An n-gram language model with add-k smoothing: the baseline every later model must beat."""

from __future__ import annotations

from typing import Iterable, Sequence


class NGramLM:
    """P(w | ctx) = (count(ctx, w) + k) / (count(ctx) + k * vocab_size)

    ctx is the last n - 1 tokens, left-padded with a BOS id equal to vocab_size (never predicted).
    Satisfies contracts.LanguageModel.
    """

    def __init__(self, n: int, vocab_size: int, k: float = 0.1):
        """ValueError unless n >= 1, vocab_size >= 1 and k > 0."""
        raise NotImplementedError

    def fit(self, sequences: Iterable[Sequence[int]]) -> NGramLM:
        """Count every position of every sequence. Tokens outside range(vocab_size): ValueError."""
        raise NotImplementedError

    def prob(self, token: int, context: Sequence[int] = ()) -> float:
        raise NotImplementedError

    def logprobs(self, context: Sequence[int]) -> list[float]:
        """log P(t | context) for every t in range(vocab_size). Must cost O(vocab_size), not O(V) calls to prob."""
        raise NotImplementedError

    def perplexity(self, sequences: Iterable[Sequence[int]]) -> float:
        """exp(mean negative log-probability over every token). No tokens: ValueError."""
        raise NotImplementedError
