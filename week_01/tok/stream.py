"""Read documents lazily, so memory stays flat as the corpus grows."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

SEPARATOR = "<|endoftext|>"


def iter_documents(path: str | Path) -> Iterator[str]:
    """Yield stripped, non-empty documents.

    .jsonl: one JSON object per line, text in the "text" field.
    Anything else: documents separated by a line that is exactly SEPARATOR (TinyStories' format).
    Never read the whole file into memory.
    """
    raise NotImplementedError
