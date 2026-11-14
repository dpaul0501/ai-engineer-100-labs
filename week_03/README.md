# Week 1 Lab: `tok`

You'll build the two halves around every language model:
- **in front of it:** a byte-level BPE tokenizer
- **after it:** the decoding loop — softmax, temperature, top-k, top-p, beam search, and a **grammar-constrained decoder** that can only produce valid JSON

The model in the middle is an n-gram model you also write. It is the baseline every later model has to beat, and it is enough to see why sampled JSON breaks and how a mask fixes it.

The full week is in the [Week 1 guide](../guide/docs/weeks/week_01.md).

## Setup

```bash
cd week_01
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q          # all red at the start: that is the point
```

## Work in this order: spec → contract → test → code

1. **Spec.** Fill in the *You write* sections of [`SPEC.md`](SPEC.md), including your estimates.
2. **Contract.** Read [`tok/contracts.py`](tok/contracts.py) and the stubs' docstrings. They are fixed.
3. **Tests first.** Write `tests/test_mine.py` with at least one test per module, each named after the bug it catches. Commit with every test red. **This commit is Milestone 1.**
4. **Code.** Make the tests pass, module by module, in the order of the milestones in the guide.

**AI rule for Days 1–20: AI explains, you type.** You may ask AI to explain concepts or review your code. Do not paste code it writes.

## Layout

```
tok/contracts.py   Tokenizer, LanguageModel and Constraint protocols (fixed)
tok/bpe.py         merge, BPE.train / encode / decode / save / load
tok/stream.py      iter_documents
tok/ngram.py       NGramLM (prob, logprobs, perplexity)
tok/sample.py      log_softmax, softmax, argmax, top_k_filter, top_p_filter, categorical, Sampler, reservoir_sample
tok/decode.py      generate (with an optional constraint), greedy, beam_search
tok/grammar.py     the JSON pushdown automaton, TokenTrie, JsonConstraint
tok/cli.py         the `tok` command
data/alice.txt     prose corpus (Alice's Adventures in Wonderland, public domain, 723 documents)
data/records.txt   2,000 synthetic support tickets as compact JSON, English and Hindi
data/make_records.py   rebuilds records.txt deterministically
tests/             acceptance tests (fixed) and your own tests
```

## The experiment

```bash
tok train data/records.txt --vocab-size 512 --out rec.json
tok generate --model rec.json --train data/records.txt --samples 50            # free sampling
tok generate --model rec.json --train data/records.txt --samples 50 --json     # constrained
```

Compare the two `valid_rate`s, then sweep `--n`, `--temperature` and `--top-p`. Put the table in your post. Use `reservoir_sample` to hold out records **before** training the tokenizer and the n-gram, and say in your write-up why the order matters.

## Stretch

```bash
pip install -e ".[stretch]" && TOK_STRETCH=1 pytest -q -k stretch
```

- `BPE.from_tiktoken("gpt2")` rebuilds GPT-2's merges and must encode exactly as tiktoken does.
- `JsonConstraint` over GPT-2's 50,000-token vocabulary must mask fast enough to use.
- Optional, outside the tests: run your `JsonConstraint` on top of a real model's logits (GPT-2 small through `transformers`, on CPU).

## Deliverable

- **The package on TestPyPI**, as `tok-<your-github-handle>`.
- **A post** with two tables: bytes per token for English vs Hindi records (yours vs GPT-2's), and valid-JSON rate free vs constrained across n and temperature.
- **CI:** GitHub Actions runs `pytest` on every push.
