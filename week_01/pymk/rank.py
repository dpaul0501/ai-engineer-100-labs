"""Ranking: features of a pair (u, v), the temporal training set, and logistic regression in NumPy.

No scikit-learn. Everything is plain NumPy so you can see every step of the derivation.
"""

from __future__ import annotations

from typing import Callable, Sequence

import numpy as np

FEATURES = ("common_neighbors", "jaccard", "adamic_adar", "resource_allocation",
            "shared_groups", "same_city", "log_deg_u", "log_deg_v")


def features(adj: Sequence[set[int]], u: int, v: int, city: Sequence[int],
             groups: Sequence[Sequence[int]]) -> np.ndarray:
    """A float64 vector in the order of FEATURES. With Z = N(u) ∩ N(v):

    common_neighbors     |Z|
    jaccard              |Z| / |N(u) ∪ N(v)|, 0.0 if the union is empty
    adamic_adar          sum over w in Z of 1 / ln deg(w)   (deg(w) >= 2, since w knows both u and v)
    resource_allocation  sum over w in Z of 1 / deg(w)
    shared_groups        |groups[u] ∩ groups[v]|
    same_city            1.0 if city[u] == city[v] else 0.0
    log_deg_u, log_deg_v ln(1 + deg(u)), ln(1 + deg(v))
    All but the last two are symmetric in (u, v).
    """
    raise NotImplementedError


def build_dataset(past_adj: Sequence[set[int]], future_edges: Sequence[Sequence[int]],
                  city: Sequence[int], groups: Sequence[Sequence[int]],
                  neg_per_pos: int = 1, seed: int = 0) -> tuple[np.ndarray, np.ndarray, list[tuple[int, int]]]:
    """(X, y, pairs) for link prediction. Features come from past_adj only; labels from future_edges.

    Positives: each future edge (u, v), u < v, that is not a past friendship and has at least one
    mutual friend in the past (the ranker only ever sees two-hop candidates). Duplicates once.
    Negatives: for each positive, up to neg_per_pos users x drawn uniformly from u's past two-hop
    candidates C(u), excluding u's future friends and pairs already in the dataset.
    pairs[i] = (min, max); X[i] = features(past_adj, *pairs[i], city, groups); y[i] in {0, 1}.
    Deterministic for a given seed. neg_per_pos < 0: ValueError.
    """
    raise NotImplementedError


def sigmoid(z) -> np.ndarray:
    """1 / (1 + e^-z), without overflow for any finite z (hint: 0.5 * (1 + tanh(z / 2)))."""
    raise NotImplementedError


def log_loss_and_grad(w: np.ndarray, b: float, X: np.ndarray, y: np.ndarray,
                      l2: float = 0.0) -> tuple[float, np.ndarray, float]:
    """Mean cross-entropy plus (l2 / 2)·||w||², and its gradient (dL/dw, dL/db).

    With z = Xw + b, per example: log(1 + e^z) - y z (use np.logaddexp, stable for |z| = 1000).
    dL/dw = Xᵀ(σ(z) - y) / n + l2·w,  dL/db = mean(σ(z) - y).
    """
    raise NotImplementedError


class LogisticRegression:
    """Full-batch gradient descent on standardized features.

    fit: store each column's mean and standard deviation (a zero sd becomes 1), standardize,
    start from w = 0, b = 0, run `epochs` steps of size lr, and record the loss before each step
    in self.losses. Deterministic. lr <= 0, epochs < 1 or l2 < 0: ValueError.
    """

    def __init__(self, lr: float = 0.5, epochs: int = 500, l2: float = 1e-4):
        raise NotImplementedError

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LogisticRegression":
        """Returns self. Mismatched shapes, no rows, or labels other than 0/1: ValueError."""
        raise NotImplementedError

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """z = standardized(X) @ w + b. Before fit: RuntimeError."""
        raise NotImplementedError

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """σ(decision_function(X)): the probability that each pair becomes a friendship."""
        raise NotImplementedError


def make_scorer(model: LogisticRegression, city: Sequence[int],
                groups: Sequence[Sequence[int]]) -> Callable[[Sequence[set[int]], int], dict[int, float]]:
    """A scorer for serve.PYMKService: scorer(adj, u) = {v: model score} for every v in C(u)."""
    raise NotImplementedError
