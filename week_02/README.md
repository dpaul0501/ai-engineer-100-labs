# Week 2 lab: Extraction tool with an eval set

The week's tasks are in the guide: [Week 2](../guide/docs/weeks/week_02.md). This file has the spec and the acceptance tests. There is no starter code this week: you design the package yourself, starting from the design doc.

## Spec

```bash
extract run INPUT.txt [--variant plain|fewshot|schema] [--window 4000] [--overlap 400]
extract eval data/eval.jsonl [--variant schema] [--seed 0] [--resamples 2000] [--fake recordings/]
extract compare data/eval.jsonl [--fake recordings/]
extract validate-data data/eval.jsonl
```

- `run` prints one JSON object to stdout: the extracted fields, an `evidence` map from field name to quote, and a `meta` block with `schema_version`, variant, window count, retries, stop reason, and input and output tokens.
- `eval` prints a table: per-field accuracy, invented-value rate per field, parse-failure rate, schema-failure rate, and overall field accuracy with a 95% bootstrap interval. It also writes `results/<variant>.json`.
- `compare` runs all three variants and prints one row per variant.
- `validate-data` checks every gold label in the eval file against the Pydantic schema and exits non-zero on the first bad row, naming its `id`.
- `--fake DIR` replays recorded responses instead of calling the API. All tests use it.

### Design doc first

`docs/design.md` is committed before any file in the package. One or two pages:

- **Requirements:** functional (the four commands) and non-functional (offline tests, reproducible numbers, a time budget per input).
- **Estimates:** tokens and cost for one full `compare` run (40 examples × 3 variants, plus retries), wall time for that run, and the expected width of the 95% interval at n = 40 from the standard-error formula.
- **Interface (API design):** the CLI contract above, one Python entry point the CLI calls, the error contract (each failure named, with its exit code), and the versioning rule for `schema_version`: which changes are breaking.
- **Data model:** the eval record (`id`, raw input, gold fields, labeling time, labeler), how "absent from the text" is stored, and the canonical form of each field (numbers, ISO 4217 currency codes, ISO 8601 dates, lists as sets or in order).
- **Decisions:** window size and overlap, the merge rule when windows disagree, and how an unverified quote is scored. A reason for each.
- **Risks:** labels contaminated by model output, few-shot examples leaking into the eval set, and how each is detected.

### Required behavior in detail

- **Schema (AI Engineering, Engineering Practice).** A single Pydantic model is the source of truth. It has at least six fields, including one enum, one number, one list, and one nullable field. The JSON schema sent to the model comes from `model_json_schema()`.
- **Variants (AI Engineering).** `plain`: instructions only. `fewshot`: instructions, schema in the prompt, two examples that are not in the eval set. `schema`: the provider's structured-output mode. Untrusted input sits inside delimiters in every variant.
- **Validation and retry (AI Engineering).** Parse, then validate. On failure, send one retry that includes the validation error. A second failure is recorded as a failure for that example; the run continues. A response whose stop reason is max tokens is treated as a failure before parsing.
- **Evidence (DSA).** Each non-null field needs a quote. The quote is checked against the input with a hand-written two-pointer matcher after lowercasing and collapsing whitespace. No regex. A field whose quote is not found is reported as `unsupported` in `meta`, and counts as wrong in the eval.
- **Windows (DSA).** Inputs longer than `--window` characters are split into windows of that size, each overlapping the previous one by `--overlap`. Results are merged by the rule in the design doc (for example: first non-null value with a verified quote wins; list fields are unioned and deduplicated).
- **Scoring (ML/DL, Engineering Practice).** Written test-first. Normalize to the canonical forms in the design doc before comparing. Null vs null is correct. Value vs null gold is an **invented value**, reported separately and counted as wrong. Null vs value gold is a **miss**.
- **Interval (ML/DL).** Bootstrap resamples **examples**, not fields, with a seeded `np.random.default_rng`. Same seed, same numbers.
- **Data (System Design).** At least 40 examples, labeled before any model output was seen. At least 8 examples have one or more fields absent from the text. Every record has a stable `id`.
- **Engineering Practice.** Type hints throughout, `mypy --strict` clean, and a README with setup steps, an example run, and the results table. The PR description lists what AI explained and how it was verified.

## Acceptance tests

- **Design first.** `git log --diff-filter=A --format=%H -- docs/design.md` names a commit that is an ancestor of the first commit adding any file under the package directory.
- `extract eval data/eval.jsonl --fake recordings/ --seed 0` exits 0, prints all required metrics, and prints byte-identical output on a second run.
- `extract validate-data data/eval.jsonl` passes, the file has at least 40 rows with unique `id`s, and at least 8 rows contain a null gold field. A copy of the file with one enum value misspelled exits non-zero and names that row's `id`.
- **Interface.** `run` output includes `meta.schema_version`. Each failure in the error contract (unreadable input, LLM failure, unparseable output, invalid output) returns the exit code the design doc names.
- **Retry.** With a fake client that returns invalid JSON and then valid JSON, `run` succeeds with exactly 2 calls. With one that returns invalid JSON twice, `eval` completes without an exception and the parse-failure rate counts that example.
- **Truncation.** A recorded response whose stop reason is max tokens is counted as a failure even when its text happens to parse.
- **Windows.** A 20,000-character input whose only salary mention sits across the boundary between window 2 and window 3 is still extracted with the default overlap. Setting `--overlap 0` makes this test fail.
- **Evidence matcher.** A quote that differs from the source only in case and line breaks is found. A quote with one changed word is not found. A unit test compares the matcher against `in` on 1,000 random normalized strings.
- **Seeded bug (must fail).** Change the scorer so that any predicted value is marked correct when the gold label is null. At least one scorer test fails, and the invented-value rate for the fake recordings changes.
- **Seeded bug (must fail).** Change the bootstrap to resample fields instead of examples. A test that checks the interval against a known small case fails.
- `mypy --strict` exits 0, and `git log --follow tests/test_scorer.py` shows the first scorer test committed before `scorer.py` existed.

## Defense

At the end of the week, defend your build to a moderator and your peers. They pick lines in your code and ask what breaks if each one changes. See [the defense](https://dpaul0501.github.io/ai-engineer-100/how-it-works/#the-defense).
