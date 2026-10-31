# SPEC: `tok`, tokens and decoding

Write this file **before any code**. Commit it together with your own failing tests (`tests/test_mine.py`): that commit is Milestone 1. The sections marked **Fixed** are the contract the acceptance tests check, so do not change them. Fill in everything marked **You write**.

## 1. Problem and users · *You write*

A language model only ever does one thing: given token ids, it scores every possible next token. Everything else — the text you see, its cost, whether it parses — is decided by the tokenizer and the decoding loop around the model.

Who needs each part, and what goes wrong for them without it? Give two concrete users, for example "an app that must get valid JSON back on every call" or "a team paying per token for Hindi text".

## 2. Non-goals · *You write*

List at least three things `tok` will not do, for example special tokens, JSON with whitespace between tokens, full JSON Schema, a neural model, or speed comparable to Rust.

## 3. Interfaces · *Fixed*

The Python contracts are in `tok/contracts.py` and the stubs' docstrings. The CLI is specified in `tok/cli.py`.

| Interface | Contract |
|---|---|
| `Tokenizer` | `encode(str) -> list[int]`, `decode(ids) -> str`, `vocab_size`. **Invariant:** `decode(encode(x)) == x` for every string |
| `BPE.train` | Ids 0–255 are raw bytes. Merge *i* creates id 256 + *i*. Pre-tokenize with `GPT2_PATTERN`, never merge across chunks. Each step merges the most frequent pair; **ties go to the smallest (left, right)**. Stop at `vocab_size` or when no pair occurs at least twice. `vocab_size < 256` raises `ValueError` |
| `BPE.encode` / `decode` | Encode: in each chunk, apply the lowest-ranked merge present, repeatedly. Decode: join the bytes, then decode with `errors="replace"`. Unknown ids raise `ValueError` |
| `save` / `load` | JSON with `format_version`. `load` raises `ValueError` on any other version |
| `iter_documents` | Lazy. Reads `.jsonl` (`"text"` field) or text separated by a line `<\|endoftext\|>`. Memory stays flat |
| `LanguageModel` | `vocab_size` and `logprobs(context) -> list[float]` of length `vocab_size`. **Invariant:** the exponentials sum to 1 |
| `NGramLM` | Add-k smoothing, BOS padding, `prob`, `logprobs` in O(V), perplexity = exp(mean negative log-probability) |
| `log_softmax` / `softmax` | Stable for any finite logits (subtract the max). `-inf` means masked. All `-inf` raises `ValueError` |
| `argmax`, `top_k_filter` | Ties go to the lowest id. Top-k keeps exactly k |
| `top_p_filter` | The **smallest** set of most likely tokens whose mass is at least p |
| `categorical` | Prefix sums plus binary search. Zero-probability ids are never drawn |
| `Sampler` | **temperature → top-k → top-p → draw**. Temperature 0 is greedy |
| `generate` | Returns new ids only. With a constraint, logits outside `allowed(state)` become `-inf` before sampling, and generation stops when the state is done |
| `beam_search` | The `beam_width` best continuations of exactly n tokens by total log-probability, best first |
| `Constraint` | Immutable, hashable states. `advance(s, t) is None` exactly when `t` is not in `allowed(s)`; `allowed(s)` is empty exactly when `is_done(s)` |
| `JsonConstraint` | Compact JSON (no whitespace outside strings), top level an object or array, depth ≤ 32, valid UTF-8 in strings, RFC 8259 numbers and escapes. Masks with a **vocabulary trie** and caches masks per state |

## 4. Acceptance criteria · *Fixed + You write*

- **Fixed:** every test in `tests/test_acceptance.py` passes.
- **You write:** at least one test of your own per module in `tests/test_mine.py`, each named after the bug it catches. Mentors run your tests against planted bugs at the defense.

## 5. Budgets and estimates · *You write, before coding*

Estimate first, then measure after the build. Fill in both columns.

| Quantity | Estimate | Measured | Why the difference |
|---|---|---|---|
| Training time, `alice.txt`, vocab 2,000 | | | |
| Bytes per token on `records.txt`, English vs Hindi records, vocab 512 | | | |
| Perplexity on held-out records for n = 1, 2, 3, 4 | | | |
| Share of **unconstrained** samples whose first value is valid JSON (n = 3, T = 1.0) | | | |
| Share of **constrained** samples that finish within 300 tokens (n = 3, T = 1.0 and 0.7) | | | |
| Mask time per state: brute force vs trie, at vocab 512 and 4,096 | | | |
| Mask cache hit rate during generation | | | |

## 6. Decisions · *You write*

For each decision, write the choice, the alternative, and why. At minimum cover:
- the heap with lazy deletion vs re-counting
- how you represent automaton states (and why they must be hashable)
- how a number ends (it has no closing character)
- what the cache keeps, and how it is bounded
- what happens when generation hits `max_new_tokens` before the JSON closes

## 7. Risks · *You write*

What could make your numbers wrong, or your output wrong? For example: held-out records leaking into training, a mask that is "almost" right (one missing token is a silent quality loss, one extra token is a broken guarantee), smoothing mass that lets the model wander inside strings, a cache that grows without bound.
