from pathlib import Path

import numpy as np


def build_vocab(docs: list[list[str]]) -> dict[str, int]:
    """Map each distinct word to a column index, in order of first appearance."""
    raise NotImplementedError


def idf(docs: list[list[str]], vocab: dict[str, int]) -> np.ndarray:
    """Inverse document frequency per vocabulary word: log((1 + N) / (1 + df)) + 1.

    N is the number of documents and df the number of documents containing the word.
    Shape: (len(vocab),).
    """
    raise NotImplementedError


def tfidf_matrix(docs: list[list[str]], vocab: dict[str, int], idf_weights: np.ndarray) -> np.ndarray:
    """One row per document: raw term counts times IDF, then L2-normalized per row.

    An empty document must produce a row of zeros, not NaN.
    Shape: (len(docs), len(vocab)).
    """
    raise NotImplementedError


def vectorize_query(tokens: list[str], vocab: dict[str, int], idf_weights: np.ndarray) -> np.ndarray:
    """Same weighting as tfidf_matrix for a single query. Unknown words are ignored."""
    raise NotImplementedError


def save_index(path: Path, names: list[str], vocab: dict[str, int], idf_weights: np.ndarray, matrix: np.ndarray) -> None:
    """Write the index to disk so `pocket search` does not re-read the corpus."""
    raise NotImplementedError


def load_index(path: Path) -> tuple[list[str], dict[str, int], np.ndarray, np.ndarray]:
    """Read back exactly what save_index wrote."""
    raise NotImplementedError
