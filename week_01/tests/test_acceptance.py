"""Week 1 acceptance tests for `pymk`. They fail on the starter code and pass when SPEC.md is met.

Run:      pytest -q
Stretch:  PYMK_STRETCH=1 pytest -q -k stretch

The first run generates data/edges.csv and data/users.csv with data/make_graph.py (seed 0).
"""

import math
import os
import random
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from pymk import exact, graph, metrics, minhash, rank, sample, serve

DATA = Path(__file__).resolve().parent.parent / "data"
N_USERS, N_EDGES = 10_000, 100_000
stretch = pytest.mark.skipif(not os.environ.get("PYMK_STRETCH"), reason="stretch: set PYMK_STRETCH=1")


# --- Fixtures ----------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def data_dir():
    if not (DATA / "edges.csv").exists() or not (DATA / "users.csv").exists():
        subprocess.run([sys.executable, str(DATA / "make_graph.py"), str(DATA)], check=True)
    return DATA


@pytest.fixture(scope="session")
def edges(data_dir):
    return graph.load_edges(data_dir / "edges.csv")


@pytest.fixture(scope="session")
def users(data_dir):
    return graph.load_users(data_dir / "users.csv")


@pytest.fixture(scope="session")
def adj(edges):
    return graph.adjacency(edges, N_USERS)


@pytest.fixture(scope="session")
def sample_users():
    return random.Random(0).sample(range(N_USERS), 300)


def tiny():
    """The 6-person graph of the week reading: YOU=0, friends B=1 and C=2; candidates D=3, E=4, F=5.

    E is a friend of both B and C (2 mutual friends); D and F have one each.
    """
    return graph.adjacency([(0, 1, 0), (0, 2, 1), (1, 3, 2), (1, 4, 3), (2, 4, 4), (2, 5, 5)], 6)


def naive_mutual(adj, u, blocked=frozenset()):
    """The definition, written as plainly as possible: |N(u) ∩ N(v)| for every eligible v."""
    out = {}
    for v in range(len(adj)):
        if v != u and v not in adj[u] and v not in blocked:
            m = len(adj[u] & adj[v])
            if m:
                out[v] = m
    return out


@st.composite
def small_graphs(draw):
    n = draw(st.integers(2, 12))
    pairs = draw(st.lists(st.tuples(st.integers(0, n - 1), st.integers(0, n - 1)), max_size=40))
    es = [(min(a, b), max(a, b), t) for t, (a, b) in enumerate(pairs) if a != b]
    return n, es


# --- graph.py ----------------------------------------------------------------------------------

def test_load_edges_and_users(edges, users):
    assert len(edges) == N_EDGES
    assert all(u < v for u, v, _ in edges)
    assert [t for _, _, t in edges] == list(range(N_EDGES))
    city, groups = users
    assert len(city) == len(groups) == N_USERS
    assert all(1 <= len(g) <= 3 and g == sorted(set(g)) for g in groups)


def test_adjacency_matches_the_week_numbers(adj):
    deg = [len(a) for a in adj]
    assert sum(deg) == 2 * N_EDGES                      # each friendship is stored twice
    assert min(deg) >= 1 and max(deg) == 1480
    assert all(u not in adj[u] for u in range(N_USERS))
    assert all(u in adj[v] for u in range(N_USERS) for v in adj[u])


def test_adjacency_rejects_bad_edges():
    with pytest.raises(ValueError):
        graph.adjacency([(3, 3, 0)], 5)
    with pytest.raises(ValueError):
        graph.adjacency([(0, 5, 0)], 5)
    assert graph.adjacency([(0, 1, 0), (0, 1, 1)], 2) == [{1}, {0}]   # duplicates collapse


def test_temporal_split_cuts_by_time_not_by_position(edges):
    shuffled = edges[:]
    random.Random(0).shuffle(shuffled)
    past, future = graph.temporal_split(shuffled, 0.8)
    assert len(past) == 80_000 and len(future) == 20_000
    assert max(t for *_, t in past) < min(t for *_, t in future)
    assert (past, future) == graph.temporal_split(edges, 0.8)
    for bad in (0, 1, -0.1, 1.5):
        with pytest.raises(ValueError):
            graph.temporal_split(edges, bad)


def test_work_is_the_sum_of_friend_degrees(adj):
    W = [graph.work(adj, u) for u in range(N_USERS)]
    assert W[0] == sum(len(adj[f]) for f in adj[0])
    # Σ_u W(u) = Σ_f deg(f)²: each f is counted once by each of its deg(f) friends (Day 2).
    assert sum(W) == sum(len(a) ** 2 for a in adj)
    assert max(W) == 51_806 and round(sum(W) / N_USERS) == 1477


# --- exact.py ----------------------------------------------------------------------------------

def test_golden_six_person_graph():
    assert exact.suggest(tiny(), 0, 3) == [(4, 2), (3, 1), (5, 1)]
    assert exact.mutual_counts(tiny(), 0) == {3: 1, 4: 2, 5: 1}


def test_ties_go_to_the_smaller_id_and_k_is_respected():
    adj = tiny()
    assert exact.suggest(adj, 0, 2) == [(4, 2), (3, 1)]
    assert exact.suggest(adj, 0, 0) == []
    assert exact.suggest(adj, 0, 100) == [(4, 2), (3, 1), (5, 1)]
    with pytest.raises(ValueError):
        exact.suggest(adj, 0, -1)
    with pytest.raises(ValueError):
        exact.suggest(adj, 6, 3)


def test_never_self_friends_or_blocked():
    adj = tiny()
    assert exact.suggest(adj, 0, 10, blocked={4}) == [(3, 1), (5, 1)]
    for u in range(6):
        got = {v for v, _ in exact.suggest(adj, u, 10)}
        assert u not in got and not (got & adj[u])


@settings(max_examples=200, deadline=None)
@given(small_graphs())
def test_mutual_counts_equal_the_matrix_square(g):
    n, es = g
    adj = graph.adjacency(es, n)
    A = np.zeros((n, n), dtype=int)
    for u, v, _ in es:
        A[u, v] = A[v, u] = 1
    A2 = A @ A                                           # (A²)_uv = number of length-2 paths = |N(u) ∩ N(v)|
    for u in range(n):
        want = {v: int(A2[u, v]) for v in range(n) if v != u and not A[u, v] and A2[u, v]}
        assert exact.mutual_counts(adj, u) == want


@settings(max_examples=100, deadline=None)
@given(small_graphs())
def test_mutual_counts_are_symmetric(g):
    n, es = g
    adj = graph.adjacency(es, n)
    counts = [exact.mutual_counts(adj, u) for u in range(n)]
    for u in range(n):
        for v, m in counts[u].items():
            assert counts[v][u] == m


@settings(max_examples=200, deadline=None)
@given(st.dictionaries(st.integers(0, 50), st.integers(-5, 5)), st.integers(0, 60))
def test_top_k_matches_a_full_sort(scores, k):
    assert exact.top_k(scores, k) == sorted(scores, key=lambda v: (-scores[v], v))[:k]


def test_suggest_matches_the_definition_on_the_week_graph(adj, sample_users):
    for u in sample_users[:60]:
        want = naive_mutual(adj, u)
        ranked = sorted(want, key=lambda v: (-want[v], v))[:10]
        assert exact.suggest(adj, u, 10) == [(v, want[v]) for v in ranked]


# --- sample.py ---------------------------------------------------------------------------------

def star_graph():
    """User 0 has 10 friends (1..10); friends 1..4 are also friends with 11, so m(0, 11) = 4."""
    es = [(0, f, f) for f in range(1, 11)] + [(f, 11, 10 + f) for f in range(1, 5)]
    return graph.adjacency(es, 12)


def test_full_sample_is_exact(adj, sample_users):
    for u in sample_users[:30]:
        est = sample.sample_counts(adj, u, len(adj[u]), seed=3)
        assert est == pytest.approx({v: float(m) for v, m in exact.mutual_counts(adj, u).items()})


def test_sampled_estimate_is_unbiased_with_hypergeometric_variance():
    adj, trials = star_graph(), 4000
    est = [sample.sample_counts(adj, 0, 3, seed=s).get(11, 0.0) for s in range(trials)]
    # count ~ Hypergeometric(N=10, K=4, s=3); m̂ = (10/3)·count, so E[m̂] = 4 and
    # Var(m̂) = (10/3)² · 3·(4/10)·(6/10)·(7/9) ≈ 6.22
    assert abs(np.mean(est) - 4) < 0.2
    assert abs(np.var(est) - 6.22) < 0.8
    assert len(set(est)) > 1, "different seeds must give different samples"


def test_sampling_is_deterministic_and_checks_s():
    adj = star_graph()
    assert sample.sample_counts(adj, 0, 5, seed=7) == sample.sample_counts(adj, 0, 5, seed=7)
    for s in (0, 11):
        with pytest.raises(ValueError):
            sample.sample_counts(adj, 0, s)


def test_budget_is_never_exceeded(adj, sample_users):
    for u in sample_users[:100]:
        for budget in (0, 100, 1000, 5000):
            counts, reads = sample.budgeted_candidates(adj, u, budget, seed=0)
            assert reads <= budget
            assert set(counts) <= set(exact.mutual_counts(adj, u))
            assert sample.budgeted_candidates(adj, u, budget, seed=0) == (counts, reads)
    with pytest.raises(ValueError):
        sample.budgeted_candidates(adj, 0, -1)


def test_ample_budget_gives_exact_counts_and_cap_skips_hubs(adj, sample_users):
    for u in sample_users[:50]:
        W = graph.work(adj, u)
        counts, reads = sample.budgeted_candidates(adj, u, W, seed=0)
        assert counts == exact.mutual_counts(adj, u) and reads == W
        capped, reads = sample.budgeted_candidates(adj, u, W, cap=50, seed=0)
        small = [f for f in adj[u] if len(adj[f]) <= 50]
        assert reads == sum(len(adj[f]) for f in small)
        want = Counter(v for f in small for v in adj[f] if v != u and v not in adj[u])
        assert capped == dict(want)


def test_recall_rises_with_budget_and_hub_cap_costs_recall(adj, sample_users):
    def mean_recall(budget, cap):
        out = []
        for u in sample_users:
            truth = exact.top_k(exact.mutual_counts(adj, u), 10)
            if truth:
                c, _ = sample.budgeted_candidates(adj, u, budget, cap=cap, seed=0)
                out.append(metrics.recall_at_k(exact.top_k(c, 10), truth, 10))
        return np.mean(out)
    low, mid, high = mean_recall(250, None), mean_recall(2000, None), mean_recall(8000, None)
    assert low < mid < high and mid >= 0.85 and high >= 0.95
    assert mean_recall(8000, 200) < high - 0.1, "skipping hubs loses candidates that only hubs reach"


# --- minhash.py --------------------------------------------------------------------------------

def test_jaccard_definition():
    assert minhash.jaccard({1, 2, 3}, {2, 3, 4}) == 0.5
    assert minhash.jaccard(set(), set()) == 0.0


def test_signature_shape_and_determinism():
    mh = minhash.MinHash(64, seed=1)
    a = mh.signature([5, 1, 9])
    assert a.shape == (64,) and a.dtype == np.uint64
    assert np.array_equal(a, mh.signature([9, 5, 1, 1]))
    assert np.array_equal(a, minhash.MinHash(64, seed=1).signature([1, 5, 9]))
    assert minhash.estimate_jaccard(a, a) == 1.0
    with pytest.raises(ValueError):
        mh.signature([])
    with pytest.raises(ValueError):
        minhash.estimate_jaccard(a, minhash.MinHash(32).signature([1]))


def test_minhash_agreement_estimates_jaccard():
    ids = random.Random(0).sample(range(10**6), 150)        # user ids are scattered, not contiguous
    a, b = set(ids[:100]), set(ids[50:])                     # J = 50 / 150 = 1/3
    ests = []
    for seed in range(50):
        mh = minhash.MinHash(256, seed=seed)
        ests.append(minhash.estimate_jaccard(mh.signature(a), mh.signature(b)))
    sd = math.sqrt((1 / 3) * (2 / 3) / 256)                   # standard error J(1-J)/k, square-rooted
    assert all(abs(e - 1 / 3) < 5 * sd for e in ests)
    assert abs(np.mean(ests) - 1 / 3) < 0.01


def test_lsh_follows_the_s_curve():
    ids = random.Random(1).sample(range(10**6), 80)
    a, b = set(ids[:60]), set(ids[20:])                      # J = 40 / 80 = 0.5
    bands, rows, hits, trials = 16, 4, 0, 300
    for seed in range(trials):
        mh = minhash.MinHash(bands * rows, seed=seed)
        idx = minhash.LSHIndex(bands, rows)
        idx.add(1, mh.signature(a))
        hits += 1 in idx.query(mh.signature(b))
    want = minhash.collision_probability(0.5, bands, rows)
    assert want == pytest.approx(1 - (1 - 0.5 ** 4) ** 16)
    assert abs(hits / trials - want) < 0.1


def test_lsh_index_contract():
    mh = minhash.MinHash(12, seed=0)
    idx = minhash.LSHIndex(bands=3, rows=4)
    idx.add(7, mh.signature([1, 2, 3]))
    assert idx.query(mh.signature([1, 2, 3])) == {7}
    with pytest.raises(ValueError):
        idx.add(8, minhash.MinHash(10).signature([1]))


# --- metrics.py --------------------------------------------------------------------------------

def test_recall_at_k():
    assert metrics.recall_at_k([1, 2, 3, 4], {2, 4, 9}, 2) == pytest.approx(1 / 3)
    assert metrics.recall_at_k([1, 2, 3, 4], {2, 4, 9}, 4) == pytest.approx(2 / 3)
    with pytest.raises(ValueError):
        metrics.recall_at_k([1], set(), 1)


@settings(max_examples=200, deadline=None)
@given(st.lists(st.tuples(st.integers(-3, 3), st.integers(0, 1)), min_size=2, max_size=40))
def test_auc_is_the_mann_whitney_probability(rows):
    scores, labels = [s for s, _ in rows], [y for _, y in rows]
    pos = [s for s, y in rows if y == 1]
    neg = [s for s, y in rows if y == 0]
    if not pos or not neg:
        with pytest.raises(ValueError):
            metrics.auc(scores, labels)
        return
    want = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg) / (len(pos) * len(neg))
    assert metrics.auc(scores, labels) == pytest.approx(want)


def test_bootstrap_ci_brackets_the_mean_and_shrinks_with_data():
    rng = np.random.default_rng(0)
    small, big = rng.normal(size=100), rng.normal(size=10_000)
    lo, hi = metrics.bootstrap_ci(small, n_boot=500, seed=1)
    assert lo < small.mean() < hi
    assert (lo, hi) == metrics.bootstrap_ci(small, n_boot=500, seed=1)
    blo, bhi = metrics.bootstrap_ci(big, n_boot=500, seed=1)
    assert bhi - blo < (hi - lo) / 5                       # width ∝ 1/√n: 100× data, 10× narrower


def test_percentile_is_nearest_rank():
    xs = list(range(1, 101))
    assert metrics.percentile(xs, 50) == 50
    assert metrics.percentile(xs, 95) == 95
    assert metrics.percentile(xs, 100) == 100
    assert metrics.percentile([3.0], 99) == 3.0
    with pytest.raises(ValueError):
        metrics.percentile([], 50)
    with pytest.raises(ValueError):
        metrics.percentile(xs, 0)


# --- rank.py -----------------------------------------------------------------------------------

def test_features_by_hand_on_the_tiny_graph():
    adj = tiny()
    city = [0, 1, 2, 3, 0, 5]
    groups = [[1, 2], [], [], [], [2, 3], []]
    f = dict(zip(rank.FEATURES, rank.features(adj, 0, 4, city, groups)))
    # N(0) = N(4) = {1, 2}; deg(1) = deg(2) = 3.
    assert f["common_neighbors"] == 2 and f["jaccard"] == 1.0
    assert f["adamic_adar"] == pytest.approx(2 / math.log(3))
    assert f["resource_allocation"] == pytest.approx(2 / 3)
    assert f["shared_groups"] == 1 and f["same_city"] == 1.0
    assert f["log_deg_u"] == pytest.approx(math.log(3)) and f["log_deg_v"] == pytest.approx(math.log(3))


def test_pair_features_are_symmetric(adj, users, sample_users):
    city, groups = users
    sym = [i for i, n in enumerate(rank.FEATURES) if not n.startswith("log_deg")]
    for u in sample_users[:40]:
        for v in list(exact.mutual_counts(adj, u))[:5]:
            assert np.allclose(rank.features(adj, u, v, city, groups)[sym],
                               rank.features(adj, v, u, city, groups)[sym])


def test_gradient_matches_finite_differences():
    rng = np.random.default_rng(0)
    X, y = rng.normal(size=(50, 4)), rng.integers(0, 2, 50)
    w, b = rng.normal(size=4), 0.3
    loss, gw, gb = rank.log_loss_and_grad(w, b, X, y, l2=0.1)
    eps = 1e-6
    for i in range(4):
        e = np.zeros(4); e[i] = eps
        num = (rank.log_loss_and_grad(w + e, b, X, y, 0.1)[0] - rank.log_loss_and_grad(w - e, b, X, y, 0.1)[0]) / (2 * eps)
        assert num == pytest.approx(gw[i], rel=1e-4, abs=1e-8)
    num_b = (rank.log_loss_and_grad(w, b + eps, X, y, 0.1)[0] - rank.log_loss_and_grad(w, b - eps, X, y, 0.1)[0]) / (2 * eps)
    assert num_b == pytest.approx(gb, rel=1e-4)


def test_log_loss_is_stable_for_huge_logits():
    X = np.array([[1000.0], [-1000.0]])
    loss, gw, gb = rank.log_loss_and_grad(np.array([1.0]), 0.0, X, np.array([0, 1]))
    assert loss == pytest.approx(1000.0) and np.isfinite(gw).all() and math.isfinite(gb)


def test_logistic_regression_learns_a_known_rule():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(2000, 3)) * [1.0, 10.0, 0.1]        # very different scales
    p = 1 / (1 + np.exp(-(2 * X[:, 0] - 0.3 * X[:, 1])))
    y = (rng.random(2000) < p).astype(int)
    m = rank.LogisticRegression().fit(X, y)
    assert m.losses[-1] < m.losses[0] and m.losses[-1] < 0.5
    prob = m.predict_proba(X)
    assert ((prob > 0) & (prob < 1)).all()
    assert metrics.auc(prob, y) > 0.85
    assert np.array_equal(m.predict_proba(X), rank.LogisticRegression().fit(X, y).predict_proba(X))
    with pytest.raises(ValueError):
        rank.LogisticRegression().fit(X, y + 2)


@pytest.fixture(scope="session")
def ranking_data(edges, users):
    city, groups = users
    s = sorted(edges, key=lambda e: e[2])
    n = len(s)
    adj_tr = graph.adjacency(s[: int(.6 * n)], N_USERS)
    adj_te = graph.adjacency(s[: int(.8 * n)], N_USERS)
    tr = rank.build_dataset(adj_tr, s[int(.6 * n): int(.8 * n)], city, groups, neg_per_pos=1, seed=0)
    te = rank.build_dataset(adj_te, s[int(.8 * n):], city, groups, neg_per_pos=1, seed=1)
    return adj_tr, adj_te, s, tr, te


def test_dataset_follows_the_rules(ranking_data):
    adj_tr, _, s, (X, y, pairs), _ = ranking_data
    n = len(s)
    future = {(u, v) for u, v, _ in s[int(.6 * n): int(.8 * n)]}
    assert X.shape == (len(y), len(rank.FEATURES)) and len(pairs) == len(y)
    assert len(set(pairs)) == len(pairs) and all(u < v for u, v in pairs)
    for (u, v), lab in zip(pairs, y):
        assert v not in adj_tr[u], "a past friendship is not a prediction"
        assert adj_tr[u] & adj_tr[v], "every pair is a two-hop candidate"
        assert (lab == 1) == ((u, v) in future)
    assert 0.9 <= y.mean() * 2 <= 1.1                       # about one negative per positive


def test_dataset_is_deterministic(ranking_data, users):
    adj_tr, _, s, (X, y, pairs), _ = ranking_data
    city, groups = users
    n = len(s)
    X2, y2, p2 = rank.build_dataset(adj_tr, s[int(.6 * n): int(.8 * n)], city, groups, neg_per_pos=1, seed=0)
    assert p2 == pairs and np.array_equal(X2, X) and np.array_equal(y2, y)


def test_ranker_beats_common_neighbours_on_the_future(ranking_data):
    *_, (Xtr, ytr, _), (Xte, yte, _) = ranking_data
    model = rank.LogisticRegression().fit(Xtr, ytr)
    cn = metrics.auc(Xte[:, rank.FEATURES.index("common_neighbors")], yte)
    aa = metrics.auc(Xte[:, rank.FEATURES.index("adamic_adar")], yte)
    lr = metrics.auc(model.decision_function(Xte), yte)
    assert aa > cn + 0.05, "a mutual friend with many friends is weak evidence"
    assert lr >= 0.70 and lr > cn + 0.08


# --- serve.py ----------------------------------------------------------------------------------

def test_lru_cache_evicts_the_least_recently_used():
    c = serve.LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    assert c.get("a") == 1                                  # "a" is now the most recent
    c.put("c", 3)                                           # evicts "b"
    assert c.get("b") is None and c.get("a") == 1 and c.get("c") == 3 and len(c) == 2
    c.put("a", 9)
    assert c.get("a") == 9 and len(c) == 2
    with pytest.raises(ValueError):
        serve.LRUCache(0)


def test_service_matches_the_exact_baseline(adj, sample_users):
    svc = serve.PYMKService(adj)
    for u in sample_users[:50]:
        assert svc.recommend(u, 10) == [v for v, _ in exact.suggest(adj, u, 10)]


def test_final_filter_runs_on_every_response_even_from_cache(adj, sample_users):
    u = sample_users[0]
    svc = serve.PYMKService(adj)
    first = svc.recommend(u, 10)
    assert svc.recommend(u, 10) == first and svc.stats()["hits"] == 1
    svc.block(u, first[0])                                  # u blocks the top suggestion
    svc.block(first[1], u)                                  # the second one blocked u
    svc.hide(first[2])                                      # the third opted out of PYMK
    again = svc.recommend(u, 10)
    assert not {first[0], first[1], first[2]} & set(again)
    assert again == [v for v in [w for w, _ in exact.suggest(adj, u, 13)] if v not in first[:3]][:10]
    assert svc.recommend(first[0], 50).count(u) == 0        # a block works in both directions


def test_new_friendship_invalidates_exactly_the_affected_users(adj):
    svc = serve.PYMKService(adj)
    u, v = 0, next(x for x in range(1, N_USERS) if x not in adj[0])
    w = next(iter(adj[u]))                                  # a friend of u
    far = next(x for x in range(N_USERS) if x not in {u, v} | adj[u] | adj[v])
    for x in (u, v, w, far):
        svc.recommend(x)
    affected = svc.add_friendship(u, v)
    assert affected == {u, v} | svc.adj[u] | svc.adj[v]
    assert v not in svc.recommend(u, 50) and u not in svc.recommend(v, 50)
    new_adj = [set(s) for s in adj]
    new_adj[u].add(v); new_adj[v].add(u)
    assert svc.recommend(w) == [x for x, _ in exact.suggest(new_adj, w, 10)]
    hits = svc.stats()["hits"]
    svc.recommend(far)
    assert svc.stats()["hits"] == hits + 1, "an unaffected user stays cached"
    assert v not in adj[u], "the service copies the graph; the input is not mutated"


def test_service_with_the_learned_ranker(adj, users, ranking_data):
    city, groups = users
    *_, (Xtr, ytr, _), _ = ranking_data
    model = rank.LogisticRegression().fit(Xtr, ytr)
    svc = serve.PYMKService(adj, scorer=rank.make_scorer(model, city, groups))
    for u in random.Random(5).sample(range(N_USERS), 20):
        got = svc.recommend(u, 10)
        assert len(got) == len(set(got)) <= 10
        assert u not in got and not set(got) & adj[u]
        assert set(got) <= set(exact.mutual_counts(adj, u))


# --- shard.py (stretch) ------------------------------------------------------------------------

@stretch
def test_stretch_consistent_hashing_moves_about_one_in_n_keys(adj):
    from pymk import shard
    ring = shard.ConsistentHashRing([f"s{i}" for i in range(16)], vnodes=100)
    before = [ring.node_for(u) for u in range(N_USERS)]
    assert before == [shard.ConsistentHashRing([f"s{i}" for i in range(16)], vnodes=100).node_for(u)
                      for u in range(N_USERS)], "the ring must not depend on Python's per-process hash()"
    load = Counter(before)
    assert max(load.values()) < 1.5 * N_USERS / 16
    ring.add_node("s16")
    after = [ring.node_for(u) for u in range(N_USERS)]
    moved = [a != b for a, b in zip(before, after)]
    assert 0.03 < np.mean(moved) < 0.10                     # expected 1/17 ≈ 0.059
    assert all(b == "s16" for a, b, m in zip(before, after, moved) if m), "keys move only to the new node"


@stretch
def test_stretch_shards_touched_per_request(adj):
    from pymk import shard
    for S in (16, 256):
        ring = shard.ConsistentHashRing([f"s{i}" for i in range(S)])
        for u in range(0, N_USERS, 97):
            t = shard.shards_touched(adj, u, ring)
            assert 1 <= t <= min(S, len(adj[u]))
            assert t == len({ring.node_for(f) for f in adj[u]})
