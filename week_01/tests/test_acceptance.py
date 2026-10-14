"""Acceptance tests for the pocket search lab. All of these must pass before Sunday."""

import math

import numpy as np
import pytest

from pocket.ask import Completion, answer, build_prompt
from pocket.index import build_vocab, idf, load_index, save_index, tfidf_matrix, vectorize_query
from pocket.search import cosine_scores, top_k
from pocket.text import tokenize

CORPUS = {
    "rope.md": "Rotary position embeddings rotate query and key vectors by position.",
    "softmax.md": "Softmax subtracts the max before exp so large logits do not overflow.",
    "bpe.md": "Byte pair encoding merges the most frequent pair of tokens.",
    "empty.md": "",
}


@pytest.fixture
def index():
    names = list(CORPUS)
    docs = [tokenize(CORPUS[n]) for n in names]
    vocab = build_vocab(docs)
    weights = idf(docs, vocab)
    matrix = tfidf_matrix(docs, vocab, weights)
    return names, vocab, weights, matrix


def search(index, query, k=5):
    names, vocab, weights, matrix = index
    q = vectorize_query(tokenize(query), vocab, weights)
    return [names[i] for i in top_k(cosine_scores(matrix, q), k)]


def test_exact_phrase_returns_its_document_first(index):
    assert search(index, "subtracts the max before exp")[0] == "softmax.md"


def test_unknown_words_return_empty_not_nan(index):
    assert search(index, "zebra quokka") == []


def test_empty_document_is_zeros_not_nan(index):
    _, _, _, matrix = index
    assert np.all(np.isfinite(matrix))
    assert np.allclose(matrix[3], 0.0)


def test_scores_are_bounded(index):
    names, vocab, weights, matrix = index
    q = vectorize_query(tokenize("position of the max token"), vocab, weights)
    scores = cosine_scores(matrix, q)
    assert scores.shape == (len(names),)
    assert np.all(scores >= -1.0 - 1e-9) and np.all(scores <= 1.0 + 1e-9)


def test_rows_are_unit_length_or_zero(index):
    _, _, _, matrix = index
    norms = np.linalg.norm(matrix, axis=1)
    assert np.allclose(norms[:3], 1.0)


def test_idf_matches_formula():
    docs = [["a", "b"], ["a"], ["c"]]
    vocab = build_vocab(docs)
    assert vocab == {"a": 0, "b": 1, "c": 2}
    expected = [math.log(4 / 3) + 1, math.log(4 / 2) + 1, math.log(4 / 2) + 1]
    assert np.allclose(idf(docs, vocab), expected)


def test_rare_word_outweighs_common_word():
    docs = [["the", "cat"], ["the", "dog"], ["the", "eel"]]
    vocab = build_vocab(docs)
    row = tfidf_matrix(docs, vocab, idf(docs, vocab))[0]
    assert row[vocab["cat"]] > row[vocab["the"]]


def test_top_k_orders_and_breaks_ties_by_index():
    scores = np.array([0.2, 0.9, 0.0, 0.9, 0.5])
    assert top_k(scores, 3) == [1, 3, 4]
    assert top_k(scores, 10) == [1, 3, 4, 0]


def test_matches_slow_reference_on_random_corpus():
    rng = np.random.default_rng(0)
    words = [f"w{i}" for i in range(30)]
    docs = [list(rng.choice(words, size=rng.integers(1, 12))) for _ in range(40)]
    vocab = build_vocab(docs)
    weights = idf(docs, vocab)
    matrix = tfidf_matrix(docs, vocab, weights)
    query = list(rng.choice(words, size=4))
    fast = cosine_scores(matrix, vectorize_query(query, vocab, weights))

    def slow_vec(tokens):
        v = [0.0] * len(vocab)
        for t in tokens:
            if t in vocab:
                v[vocab[t]] += weights[vocab[t]]
        n = math.sqrt(sum(x * x for x in v))
        return [x / n for x in v] if n else v

    q = slow_vec(query)
    slow = [sum(a * b for a, b in zip(slow_vec(d), q)) for d in docs]
    assert np.allclose(fast, slow)


def test_index_round_trips(index, tmp_path):
    names, vocab, weights, matrix = index
    save_index(tmp_path / "index", names, vocab, weights, matrix)
    names2, vocab2, weights2, matrix2 = load_index(tmp_path / "index")
    assert names2 == names and vocab2 == vocab
    assert np.array_equal(weights2, weights) and np.array_equal(matrix2, matrix)


class FakeClient:
    def __init__(self, stop_reason="end"):
        self.stop_reason = stop_reason
        self.calls = []

    def complete(self, system, user, max_tokens):
        self.calls.append((system, user, max_tokens))
        return Completion("Softmax subtracts the max [softmax.md].", self.stop_reason, 120, 12)


def test_prompt_contains_every_source():
    snippets = [("softmax.md", CORPUS["softmax.md"]), ("rope.md", CORPUS["rope.md"])]
    system, user = build_prompt("why subtract the max?", snippets)
    assert "softmax.md" in user and "rope.md" in user
    assert "why subtract the max?" in user


def test_truncated_answer_is_flagged():
    result = answer(FakeClient("max_tokens"), "q", [("softmax.md", CORPUS["softmax.md"])])
    assert result.truncated


def test_complete_answer_is_not_flagged():
    result = answer(FakeClient("end"), "q", [("softmax.md", CORPUS["softmax.md"])])
    assert not result.truncated and result.sources == ["softmax.md"]


def test_no_snippets_does_not_call_the_model():
    client = FakeClient()
    answer(client, "q", [])
    assert client.calls == []
