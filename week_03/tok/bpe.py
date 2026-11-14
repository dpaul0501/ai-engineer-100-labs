"""Byte-level BPE. Read SPEC.md first: the tie-break and stopping rules are part of the contract."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

FORMAT_VERSION = 1

# GPT-2's pre-tokenization pattern (use the `regex` package, not `re`: it needs \p{L}).
# Merges never cross the chunks it produces.
GPT2_PATTERN = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""


def merge(ids: list[int], pair: tuple[int, int], new_id: int) -> list[int]:
    """Replace every non-overlapping occurrence of pair with new_id, scanning left to right.

    merge([97, 97, 97], (97, 97), 256) == [256, 97]
    """
    raise NotImplementedError


class BPE:
    """ids 0-255 are raw bytes. Merge i creates id 256 + i, whose bytes are the pair's bytes joined."""

    def __init__(self, merges: Sequence[tuple[int, int]] = (), pattern: str = GPT2_PATTERN):
        self.merges = [tuple(p) for p in merges]
        self.pattern = pattern
        self.vocab: dict[int, bytes] = {}  # id -> bytes, for all ids
        raise NotImplementedError

    @property
    def vocab_size(self) -> int:
        raise NotImplementedError

    @classmethod
    def train(cls, texts: Iterable[str], vocab_size: int, pattern: str = GPT2_PATTERN) -> BPE:
        """Learn merges until vocab_size is reached or no pair occurs at least twice.

        Each step merges the most frequent adjacent pair; ties go to the smallest (left, right).
        Must not re-count every pair after every merge: keep pair counts and a heap, and update
        only the words that contain the merged pair.
        """
        raise NotImplementedError

    def encode(self, text: str) -> list[int]:
        """Split with the pattern, then in each chunk repeatedly apply the lowest-ranked merge present."""
        raise NotImplementedError

    def decode(self, ids: Sequence[int]) -> str:
        """Join the bytes, then decode UTF-8 with errors='replace'. Unknown ids raise ValueError."""
        raise NotImplementedError

    def save(self, path: str | Path) -> None:
        """JSON: {"format_version": FORMAT_VERSION, "pattern": ..., "merges": [[left, right], ...]}"""
        raise NotImplementedError

    @classmethod
    def load(cls, path: str | Path) -> BPE:
        """Raise ValueError if format_version is not FORMAT_VERSION."""
        raise NotImplementedError

    @classmethod
    def from_tiktoken(cls, name: str = "gpt2") -> BPE:
        """Stretch: rebuild the pair merges behind a tiktoken encoding from its mergeable ranks."""
        raise NotImplementedError
