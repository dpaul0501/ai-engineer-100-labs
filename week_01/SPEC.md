# SPEC: `pymk`, People You May Know

Write this file **before any code**. Commit it together with your own failing tests (`tests/test_mine.py`): that commit is WI-1. The sections marked **Fixed** are the contract the acceptance tests check, so do not change them. Fill in everything marked **You write**.

## 1. Problem and users · *You write*

A user opens a social app. Within the latency budget, the app must show up to 10 people that user may want to connect with. The hard rules are never broken: never the user, never someone already a friend, never someone either side has blocked, never someone who opted out. Within those rules the list should be relevant (people the user would accept), fresh, fast and cheap.

Who is hurt when each part is wrong? Give two concrete cases, for example "a user who blocked someone and sees them suggested anyway" or "a user with a celebrity friend whose request times out".

## 2. Non-goals · *You write*

List at least three things `pymk` will not do, for example a real distributed store, learned embeddings (Week 2), online A/B tests, or the privacy rules of any real product.

## 3. Data · *Fixed*

| File | Contents |
|---|---|
| `data/edges.csv` | `u,v,t`: 100,000 friendships among users 0..9,999, with u < v and t the order of formation (0..99,999) |
| `data/users.csv` | `user,city,groups`: a city id and 1–3 group ids, space-separated |

`data/make_graph.py` (seed 0) rebuilds both. Each new friendship is a friend of a friend (45%), a member of a shared group (35%) or a random popular user (20%); sociability is Pareto-distributed, so degrees are heavy-tailed.

## 4. Interfaces · *Fixed*

Types: a user is an `int` in `0..n-1`; `adj` is a `list[set[int]]` with `adj[u] = N(u)`; an edge is `(u, v, t)`. The stubs' docstrings are part of this contract.

| Function | Contract |
|---|---|
| `graph.load_edges(path)` | `list[(u, v, t)]` in file order, u < v |
| `graph.load_users(path)` | `(city, groups)`: `city[u]` an int, `groups[u]` a sorted list of distinct ids |
| `graph.adjacency(edges, n)` | Undirected sets; duplicates collapse. Self-loop or id outside `0..n-1`: `ValueError` |
| `graph.temporal_split(edges, frac=0.8)` | Sort by t; first `int(len·frac)` are the past, the rest the future. Independent of input order. `frac` outside (0, 1): `ValueError` |
| `graph.work(adj, u)` | W(u) = Σ<sub>f∈N(u)</sub> deg(f) |
| `exact.mutual_counts(adj, u, blocked)` | `{v: m(u,v)}` for m ≥ 1, m(u,v) = \|N(u) ∩ N(v)\|. **Never** u, a friend of u, or a blocked user. Unknown u: `ValueError` |
| `exact.top_k(scores, k)` | k best keys, score descending, **ties to the smaller id**; size-k heap. k < 0: `ValueError` |
| `exact.suggest(adj, u, k=10, blocked)` | `[(v, m)]`, the top k by (−m, v). Deterministic |
| `sample.sample_counts(adj, u, s, seed)` | s friends uniformly without replacement; estimate (d/s)·count. **Unbiased**. s outside 1..d: `ValueError` |
| `sample.budgeted_candidates(adj, u, budget, cap, seed)` | `(counts, reads)`. Friends in a random order fixed by (seed, u); skip hubs with deg > cap; skip a friend whose list does not fit the remaining budget; **reads ≤ budget**. budget ≥ W(u), no cap: exact counts |
| `minhash.MinHash(num_perm, seed).signature(items)` | `uint64[num_perm]`, h<sub>i</sub>(x) = (a<sub>i</sub>x + b<sub>i</sub>) mod (2<sup>31</sup>−1), a, b from `np.random.default_rng(seed)`. Empty: `ValueError` |
| `minhash.estimate_jaccard(a, b)` | Share of agreeing positions. Different shapes: `ValueError` |
| `minhash.LSHIndex(bands, rows)` | `add(key, sig)`, `query(sig) -> set`. Signature length must be bands·rows |
| `minhash.collision_probability(s, b, r)` | 1 − (1 − s<sup>r</sup>)<sup>b</sup> |
| `rank.features(adj, u, v, city, groups)` | float64 vector in the order of `rank.FEATURES` (definitions in the docstring) |
| `rank.build_dataset(past_adj, future_edges, city, groups, neg_per_pos, seed)` | `(X, y, pairs)`. Positives: future pairs, not past friends, with ≥ 1 past mutual friend. Negatives: sampled from u's past two-hop candidates, not future friends. No duplicates. Deterministic |
| `rank.log_loss_and_grad(w, b, X, y, l2)` | Mean cross-entropy + (l2/2)‖w‖², and its exact gradient. Stable for \|z\| = 1000 |
| `rank.LogisticRegression(lr, epochs, l2)` | `fit` (standardize, full-batch gradient descent from zero, `losses` recorded), `decision_function`, `predict_proba`. Deterministic |
| `rank.make_scorer(model, city, groups)` | `scorer(adj, u) -> {v: score}` over u's two-hop candidates |
| `serve.LRUCache(capacity)` | O(1) `get`/`put`; evicts the least recently used |
| `serve.PYMKService(adj, scorer, blocked, hidden, cache_size)` | `recommend(u, k)`: the first k **eligible** users of the cached ranking. The eligibility filter runs on **every** response, cached or not. `block`, `hide`, `add_friendship` (invalidates exactly {u, v} ∪ N(u) ∪ N(v)), `stats` |
| `metrics.recall_at_k(rec, relevant, k)` | \|rec[:k] ∩ relevant\| / \|relevant\| |
| `metrics.auc(scores, labels)` | Mann–Whitney: P(pos > neg), ties ½, O(n log n) |
| `metrics.bootstrap_ci(values, stat, n_boot, alpha, seed)` | Percentile bootstrap, deterministic for a seed |
| `metrics.percentile(samples, q)` | Nearest rank |
| `shard.*` (stretch) | Stable hashing (blake2b), a ring with virtual nodes, `shards_touched` |

**Determinism.** Every function that draws random numbers takes a `seed` and gives the same output for the same inputs. No function depends on Python's `hash()` of strings, set iteration order, or the wall clock.

**Eligibility.** Self, existing friends, blocks in either direction and opt-outs are hard constraints: approximate candidate generation may miss good candidates, but nothing ineligible is ever returned.

## 5. Acceptance criteria · *Fixed + You write*

- **Fixed:** every test in `tests/test_acceptance.py` passes (`PYMK_STRETCH=1` adds the WI-8 tests).
- **You write:** at least one test of your own per module in `tests/test_mine.py`, each named after the bug it catches (for example `test_blocked_user_not_returned_from_cache`). Mentors run your tests against planted bugs at the defense.

## 6. Budgets and estimates · *You write, before coding*

Estimate first, then measure after the build. Fill in both columns.

| Quantity | Estimate | Measured | Why the difference |
|---|---|---|---|
| Mean, median and p99 of W(u) | | | |
| p50 / p95 / p99 time of `exact.suggest`, and the user with the slowest request | | | |
| Mean recall@10 against the exact top 10 at read budgets 500, 2,000 and 8,000 | | | |
| The same with a hub cap of 200 | | | |
| Share of future friendships that have at least one mutual friend in the past | | | |
| AUC of common neighbours vs Adamic–Adar vs logistic regression | | | |
| p95 of `recommend`, cold cache vs warm cache | | | |

## 7. Decisions · *You write*

For each decision, write the choice, the alternative, and why. At minimum cover:
- what the cache stores (a ranking, not a final answer) and why the filter runs after it
- which users a new friendship invalidates, and the proof that nobody else's counts change
- how you pick negatives for training, and the bias that choice introduces
- what you do when a hub's adjacency list does not fit the read budget
- how ties are broken everywhere, and why that matters for tests

## 8. Risks · *You write*

What could make your numbers wrong, or your output wrong? For example: future friendships leaking into the features, a bootstrap that resamples pairs when it should resample users, a timing measured on a warm cache only, an LRU that grows without bound, a blocked user returned from a stale cache.
