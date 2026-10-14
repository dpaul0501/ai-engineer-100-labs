# Week 1 lab: Pocket search CLI

The week's tasks are in the guide: [Week 1](../guide/docs/weeks/week_01.md). This folder has what you build with: the spec, starter code, and acceptance tests.

## Setup

```bash
cd week_01
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q        # every test fails until you implement the stubs
```

## Spec

```bash
python -m pocket.cli index ./docs          # build an index of a folder of .md files
python -m pocket.cli search "rotary position" -k 5
python -m pocket.cli ask "why does softmax subtract the max?"
```

| File | What you implement |
|---|---|
| `pocket/text.py` | Nothing. `tokenize` is given so everyone agrees on what a word is. |
| `pocket/index.py` | Vocabulary, IDF, the TF-IDF matrix, query vectors, and saving and loading the index |
| `pocket/search.py` | Vectorized cosine similarity and top-k |
| `pocket/ask.py` | The prompt, the model call through `LLMClient`, and truncation handling |
| `pocket/cli.py` | Wiring the three commands together |

For `ask`, write a small adapter from your provider's SDK to the `LLMClient` interface in `pocket/ask.py`. The tests use a fake client, so they run without an API key.

The docstrings are the contract. Read every one before you start.

## Acceptance tests

`tests/test_acceptance.py` must pass in full:

- An exact phrase from one document returns that document first.
- A query with no known words returns an empty result, not an error and not NaN.
- An empty document becomes a row of zeros, not NaN.
- Cosine scores fall in [−1, 1], and non-empty rows have unit length.
- IDF matches the formula in the docstring, and a rare word outweighs a common one.
- Top-k returns the best first and breaks ties by the lower index.
- Results match a slow pure-Python reference on a random corpus.
- The index survives a save and load unchanged.
- `ask` flags truncation, includes every source in the prompt, and does not call the model when there are no snippets.

## Seeded bugs: prove your tests work

Passing the acceptance tests is not enough. Add your own tests in `tests/test_mine.py`, then plant each bug below in your working code, one at a time. For each bug, record which of your tests fails.

1. Skip the IDF multiplication in `tfidf_matrix`.
2. Normalize over `axis=0` instead of per row.
3. Return documents with a score of 0.0 from `top_k`.
4. Use `np.argsort(-scores)` in `top_k` without `kind="stable"`.

**Bug 4 passes every acceptance test.** NumPy's default sort does not keep equal elements in their original order, but on a 5-element array it happens to. Write a test that exposes it. Hint: try a few hundred tied scores.

## Defense

At the end of the week, defend your build to a moderator and your peers. They pick lines in your code and ask what breaks if each one changes. See [the defense](https://dpaul0501.github.io/ai-engineer-100/how-it-works/#the-defense).
