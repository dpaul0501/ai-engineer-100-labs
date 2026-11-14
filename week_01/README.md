# Week 1 Lab: `pymk`

You'll build **People You May Know** end to end on a 10,000-user social graph: when a user opens the app, return the 10 people they are most likely to want to connect with.

- **the exact baseline:** friends of friends, ranked by mutual-friend count
- **approximation:** sampled and budgeted candidates with hub capping, and MinHash/LSH as a second candidate source
- **ranking:** pair features and logistic regression, trained on the past and tested on the future
- **serving:** an API with an LRU cache and a final eligibility filter that runs on every response

The week's pages (reading, Days 1–5 and the worksheet) teach every piece. The worksheet lists the work items WI-1 to WI-8 and what "done" means for each.

## Setup

```bash
cd week_01
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q          # all red at the start: that is the point
```

The first test run writes `data/edges.csv` and `data/users.csv` by running `data/make_graph.py` (seed 0). You can also run it yourself: `python data/make_graph.py data`.

## Work in this order: spec → contract → test → code

1. **Spec.** Fill in the *You write* sections of [`SPEC.md`](SPEC.md), including your estimates.
2. **Contract.** Read the *Fixed* sections of `SPEC.md` and the stubs' docstrings. They are what the acceptance tests check.
3. **Tests first.** Write `tests/test_mine.py` with at least one test per module, each named after the bug it catches. Commit with every test red. **This commit is WI-1.**
4. **Code.** Make the tests pass module by module: `graph`, `exact`, `metrics`, `sample`, `minhash`, `rank`, `serve`.

**AI rule for Days 1–20: AI explains, you type.** You may ask AI to explain concepts or review your code. Do not paste code it writes.

## Layout

```
pymk/graph.py      load_edges, load_users, adjacency, temporal_split, work
pymk/exact.py      mutual_counts, top_k, suggest
pymk/sample.py     sample_counts (unbiased estimator), budgeted_candidates (read budget, hub cap)
pymk/minhash.py    jaccard, MinHash, estimate_jaccard, LSHIndex, collision_probability
pymk/rank.py       FEATURES, features, build_dataset, sigmoid, log_loss_and_grad, LogisticRegression, make_scorer
pymk/serve.py      LRUCache, PYMKService (recommend, block, hide, add_friendship, stats)
pymk/metrics.py    recall_at_k, auc, bootstrap_ci, percentile
pymk/shard.py      stretch: stable_hash, ConsistentHashRing, shards_touched
data/make_graph.py rebuilds the week's graph deterministically
tests/             acceptance tests (fixed) and your own tests
```

## Running the tests

```bash
pytest -q                                  # everything except the stretch tests
pytest -q -k "exact or golden"             # one area at a time
PYMK_STRETCH=1 pytest -q -k stretch        # WI-8, simulated sharding
```

## The experiments

Write each as a small script under `experiments/` that imports `pymk` and prints a table. Put the tables in your post.

- **Workload (WI-3):** the distribution of W(u) and the p50/p95/p99 time of `exact.suggest`.
- **Budget curve (WI-4):** mean recall@10 against the exact top 10, for several read budgets, with and without a hub cap, with bootstrap intervals over users.
- **LSH (WI-5):** for several (bands, rows), the share of the exact top 10 that LSH finds and how many candidates it returns.
- **Ranker (WI-6):** train on features from the first 60% of friendships and labels from the next 20%; test on features from the first 80% and labels from the last 20%. AUC of common neighbours, Jaccard, Adamic–Adar, resource allocation and logistic regression, and recall@10 of future friends, all with bootstrap intervals.
- **Serving (WI-7):** p50/p95 of `recommend` with a cold and a warm cache.

## Deliverable

- **The package**, installable with `pip install -e .`, every acceptance test green.
- **A post** with the budget curve, the AUC table with intervals, and the serving percentiles, each with one sentence on what it means for the design.
- **CI:** GitHub Actions runs `pytest` on every push.

## License

Code and text: CC BY 4.0. The graph is synthetic, made by `data/make_graph.py`.
