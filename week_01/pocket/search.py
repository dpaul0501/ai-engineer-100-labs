import numpy as np


def cosine_scores(matrix: np.ndarray, query: np.ndarray) -> np.ndarray:
    """Cosine similarity of the query against every row. No Python loop over rows.

    Rows or a query that are all zeros score 0.0, never NaN. Shape: (n_docs,).
    """
    raise NotImplementedError


def top_k(scores: np.ndarray, k: int) -> list[int]:
    """Indices of the k highest scores, best first. Ties go to the lower index.

    Documents with a score of 0.0 are not returned. k larger than the number
    of matches returns all matches.
    """
    raise NotImplementedError
