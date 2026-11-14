"""Decoding loops: sample one token at a time, optionally under a constraint, or search with a beam."""

from __future__ import annotations

import random
from typing import Sequence

from .contracts import Constraint, LanguageModel
from .sample import Sampler


def generate(
    model: LanguageModel,
    prompt: Sequence[int],
    max_new_tokens: int,
    sampler: Sampler,
    rng: random.Random,
    constraint: Constraint | None = None,
) -> list[int]:
    """Return up to max_new_tokens new token ids (the prompt is not included).

    With a constraint: start from constraint.start(); before each step, stop if the state is done;
    otherwise set every logit outside constraint.allowed(state) to -inf, sample, and advance the state.
    Every prefix of the output is then inside the constraint's language.
    """
    raise NotImplementedError


def greedy(model: LanguageModel, prompt: Sequence[int], max_new_tokens: int) -> list[int]:
    """Always take the argmax. Exactly max_new_tokens new ids."""
    raise NotImplementedError


def beam_search(
    model: LanguageModel, prompt: Sequence[int], beam_width: int, max_new_tokens: int
) -> list[tuple[float, list[int]]]:
    """The beam_width best continuations of exactly max_new_tokens tokens, as (total log-prob, ids).

    Sorted best first; ties go to the lexicographically smaller ids. beam_width < 1: ValueError.
    Keep only beam_width candidates per step (a heap), so cost is O(steps * width * V log width).
    """
    raise NotImplementedError
