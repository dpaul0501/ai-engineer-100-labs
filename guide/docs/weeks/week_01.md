# Week 1 · Lookups, Vectors, and Your First LLM Call

**Month 1: Foundations** · Self-paced · AI rule: **AI explains, you type.** Ask AI to explain or review. Do not paste code it writes.

## This week

**Goal:** by the end of the week you can build a small, tested search tool from scratch, explain its design with numbers, and defend every line.

| Pillar | Units this week |
|---|---|
| DSA | 8 problems: arrays and hashing |
| ML/DL | 3 concepts: arrays and broadcasting, vectors and similarity, stable softmax |
| AI Engineering | 3 experiments: the API call, temperature, grounded answers |
| System Design & Engineering Practice | 1 design (requirements and estimates) + 3 practices (git, pytest, code review) |
| Weekly build | A pocket search CLI, defended live |

### Every unit follows the same cycle

1. **Study** the suggested source. For DSA, try the problem first and study after.
2. **Do** it yourself: no AI, no peeking.
3. **Variations:** make 1–2 changes of your own and solve or run them.
4. **Tests** for the original.
5. **Corner cases** for the original.

Commit each unit to your repo. Post one finding a day as **Day N/100**.

## DSA: arrays and hashing

**Focus.** A hash table answers "have I seen this?" in O(1) on average. Scanning a list costs O(n) per question, so you store what you have seen and look it up instead.

**Study sources this week:**

- [NeetCode](https://www.youtube.com/@NeetCode) on YouTube: search the problem name for a walkthrough. His [roadmap](https://neetcode.io/roadmap) groups problems by pattern.
- [take U forward](https://www.youtube.com/@takeUforward) (Striver) on YouTube, for a second explanation.
- [Hashing](https://mldsa.github.io/docs/part1/chapter01-hashing/) and [Top-K](https://mldsa.github.io/docs/part1/chapter02-topk/) in *From LeetCode to Learning Systems*.
- [TimeComplexity](https://wiki.python.org/moin/TimeComplexity) on the Python wiki, for what dict and set operations cost.

**Evidence per problem:** `solution.py`, one or two `variation_N.py` files with the changed problem written at the top, and `test_solution.py` with the corner cases marked.

### 1. [Two Sum](https://leetcode.com/problems/two-sum/) (LeetCode 1)

- **Study:** the complement-lookup idea, in the hashing chapter or a walkthrough.
- **Do:** one pass with a dict from value to index. State the time and space complexity.
- **Variations:** sorted input, solved with two pointers in O(1) extra space; return *all* pairs without repeats.
- **Tests:** the examples from the problem, plus a target that needs the last element.
- **Corner cases:** `target = 2 * x` with `x` appearing once (no self-pairing); negative numbers; duplicates that are the answer; floats (`0.1 + 0.2 == 0.3` is `False`).
- **Go further:** PostgreSQL's hash join (`src/backend/executor/nodeHashjoin.c`) is Two Sum with `=` in place of `+`.

### 2. [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) (LeetCode 217)

- **Study:** set membership, and what a set costs in memory.
- **Do:** one pass with a set.
- **Variations:** duplicates within distance k (LeetCode 219); 10 billion URLs with only a few hundred MB of memory.
- **Tests:** with and without a duplicate.
- **Corner cases:** an empty list, one element, all elements equal.
- **Go further:** duplicate rows shared by train and test splits leak labels. A Bloom filter answers "definitely not seen" in fixed memory.

### 3. [Valid Anagram](https://leetcode.com/problems/valid-anagram/) (LeetCode 242)

- **Study:** counting, then comparing counts.
- **Do:** a count dict or `Counter`, compared once.
- **Variations:** ignore case and spaces; allow any Unicode text.
- **Tests:** an anagram, a non-anagram, and different lengths.
- **Corner cases:** empty strings; `"é"` as one code point vs `e` plus a combining accent (fix with `unicodedata.normalize("NFC", s)`).

### 4. [Group Anagrams](https://leetcode.com/problems/group-anagrams/) (LeetCode 49)

- **Study:** a canonical key turns grouping into a lookup.
- **Do:** a dict from key to list, keyed by `sorted(s)`.
- **Variations:** key by a 26-count tuple instead, and time both on long and short words; group words that are anagrams after removing one letter.
- **Tests:** the example, and a list where every word is its own group.
- **Corner cases:** an empty string in the list; repeated words; uppercase letters.
- **Go further:** pretraining pipelines dedupe text the same way, with exact hashes and MinHash (`MinHashLSH` in the `datasketch` library).

### 5. [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) (LeetCode 347)

- **Study:** the Top-K chapter: heap vs sort vs bucket sort.
- **Do:** count, then select the k most frequent.
- **Variations:** solve it three ways (heap, bucket sort, `np.argpartition`) and benchmark at n = 10⁶; the input is an endless stream.
- **Tests:** the examples, and k equal to the number of distinct values.
- **Corner cases:** ties at the k-th place (is your output deterministic?); k = 1; every element distinct.
- **Go further:** top-k sampling in LLM decoding; `Counter.most_common` calls `heapq.nlargest` in `Lib/collections/__init__.py`.

### 6. [Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/) (LeetCode 238)

- **Study:** prefix and suffix scans.
- **Do:** one prefix pass and one suffix pass, without division.
- **Variations:** O(1) extra space, not counting the output; the same idea for sums instead of products.
- **Tests:** the examples, and an array of all ones.
- **Corner cases:** one zero; two zeros; negative numbers; products that overflow int64 in NumPy (fix by summing logs).
- **Go further:** top-p sampling uses a cumulative sum to find its cutoff; causal attention gives each token only its prefix.

### 7. [Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) (LeetCode 128)

- **Study:** start counting only where the predecessor is missing.
- **Do:** a set, and a count from each run's start. Explain why this is O(n), not O(n²).
- **Variations:** return the sequence itself, not its length; the same with pandas, `s.diff().ne(1).cumsum()`.
- **Tests:** the examples, and one long run.
- **Corner cases:** an empty list; duplicates inside the run; negative numbers.

### 8. [Valid Sudoku](https://leetcode.com/problems/valid-sudoku/) (LeetCode 36)

- **Study:** one set per constraint.
- **Do:** sets for rows, columns, and boxes in a single pass.
- **Variations:** a 16×16 board; report *which* rule is broken, not just whether one is.
- **Tests:** a valid board and an invalid one for each rule.
- **Corner cases:** an empty board; a board with only one digit.
- **Go further:** the same idea is data validation before training. Write three uniqueness or range checks for a CSV.

## ML/DL: NumPy and vectors

**Study sources this week:**

- [Python NumPy tutorial](https://cs231n.github.io/python-numpy-tutorial/) from Stanford CS231n.
- [Data manipulation](https://d2l.ai/chapter_preliminaries/ndarray.html) and [linear algebra](https://d2l.ai/chapter_preliminaries/linear-algebra.html) in *Dive into Deep Learning*.
- [3Blue1Brown](https://www.youtube.com/@3blue1brown): *Essence of Linear Algebra*, the dot product chapter.
- The [foundation chapter](https://dpaul0501.github.io/llm-agent-reads/module_01_foundations/) of *LLM Foundations from Scratch*.

**Evidence per concept:** `impl.py`, `variation_N.py` with a plot or numbers, `test_impl.py` comparing against the library with `numpy.testing.assert_allclose`, and a parameter table in your notes.

### 1. Arrays, dtype, and broadcasting

- **Study:** [Broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) and [copies and views](https://numpy.org/doc/stable/user/basics.copies.html) in the NumPy docs.
- **Do:** write your own `broadcast_shape(a, b)` that returns the result shape, or raises when the shapes are incompatible.
- **Variations:** support three or more shapes; show a slice that is a view and one that is a copy, and prove it by changing the original.
- **Tests:** match `np.broadcast_shapes` on 20 random shape pairs.
- **Corner cases:** zero-length dimensions; scalars; mixing `float32` with `float64` (what is the result's dtype, and its memory at 10⁸ elements?).

### 2. Vectors: dot product, norms, and similarity

- **Study:** the dot product chapter (3Blue1Brown), and [pairwise metrics](https://scikit-learn.org/stable/modules/metrics.html) in the scikit-learn user guide.
- **Do:** cosine similarity and Euclidean distance for a matrix of vectors against one query, with no Python loop.
- **Variations:** find two vectors where cosine and Euclidean disagree about the nearest neighbor, then normalize them and show they agree; time a loop, `np.dot`, and `@` at 10⁶ elements.
- **Tests:** match scikit-learn's `cosine_similarity` and `euclidean_distances`.
- **Corner cases:** a zero vector (no NaN); identical vectors; float32 precision. Read `euclidean_distances` in `sklearn/metrics/pairwise.py` and find where it clips negative results to zero.
- **Parameters:**

| Function | Parameter | Default | What it controls | What goes wrong at the extremes |
|---|---|---|---|---|
| `np.linalg.norm` | `ord` | `None` (L2) | Which norm | L1, L2, and ∞ rank neighbors differently |
| `np.linalg.norm` | `axis`, `keepdims` | `None`, `False` | Per-row or whole-array norm | Without `keepdims`, dividing by the norm broadcasts wrongly |
| `euclidean_distances` | `squared` | `False` | Skip the square root | Ranking is unchanged, but the values are not distances |
| `cosine_similarity` | `dense_output` | `True` | Sparse or dense result | A dense n×n result on 10⁶ rows exhausts memory |

### 3. A numerically stable softmax

- **Study:** the masking section of the [attention chapter](https://dpaul0501.github.io/llm-agent-reads/part_03_attention/), and [`math_utils.py`](https://github.com/dpaul0501/llm-agent-reads/blob/main/llm_foundations/math_utils.py) in llm-agent-reads.
- **Do:** write `softmax(x, axis=-1)` from scratch, and explain why it subtracts the max.
- **Variations:** add a temperature; add a boolean mask that blocks some positions.
- **Tests:** match `scipy.special.softmax`; rows sum to 1.
- **Corner cases:** logits of 1000 (`np.exp(1000.0)` overflows); a fully masked row (with `-1e9` you get a silent uniform average, and with `-np.inf` you get NaN; decide which you want); a float32 input.
- **Parameters:** `axis`. The wrong axis gives rows that do not sum to 1, yet shape-only tests still pass.

## AI Engineering: the LLM API call

**Study sources this week:**

- Your LLM provider's official quickstart and API reference.
- [Building LLM applications for production](https://huyenchip.com/2023/04/11/llm-engineering.html) by Chip Huyen.
- [Patterns for building LLM-based systems](https://eugeneyan.com/writing/llm-patterns/) by Eugene Yan.

**Evidence per experiment:** `tool.py`, a results table (variant vs baseline), a small eval set, and a log of tokens, cost, and latency.

### 1. The API call and what comes back

- **Study:** your provider's quickstart: messages and roles, and the fields of the response.
- **Do:** make one call with the key in an environment variable, never in code. Print the whole response object and write down what every field is for.
- **Variations:** add a system prompt; set max output tokens to 10.
- **Tests:** your wrapper returns the text, the **stop reason**, and the token usage.
- **Corner cases:** a truncated answer (does your code notice the stop reason?); a missing API key; an empty prompt.
- **Cost:** log input and output tokens and compute the cost from your provider's current price page.

### 2. Temperature

- **Study:** the temperature section of the [inference chapter](https://dpaul0501.github.io/llm-agent-reads/part_06_inference_and_tricks/). Temperature divides the logits before the softmax you wrote above.
- **Do:** send the same prompt 20 times at temperature 0 and 20 times at temperature 1. Count distinct answers.
- **Variations:** a factual question vs a creative one; a third temperature.
- **Tests:** your script reports the count of distinct answers and their frequencies.
- **Corner cases:** temperature 0 is often not bit-for-bit deterministic. Did your 20 runs agree exactly?

### 3. Grounded answers, retries, and failures

- **Study:** the retrieval section of Eugene Yan's patterns post, and [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) on the AWS Architecture Blog.
- **Do:** a prompt that gives three snippets and a question, answers only from the snippets, and cites which one it used. Wrap the call so timeouts and rate limits are retried with backoff, and bad requests fail at once.
- **Variations:** five snippets instead of three; ask for the answer as JSON.
- **Tests:** an eval set of 10 questions with known answers and sources. Report how many come back correct and cited.
- **Corner cases:** a question the snippets cannot answer (does the model say so?); contradictory snippets; a simulated timeout.
- **Go further:** find the retry logic in your provider's official Python SDK (search for `max_retries`). Which errors does it retry?

## System Design & Engineering Practice: requirements, estimates, and proof

**Study sources this week:**

- [*Pro Git*](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository), chapter 2.
- [pytest: get started](https://docs.pytest.org/en/stable/getting-started.html) and [parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html).
- The [System Design Primer](https://github.com/donnemartin/system-design-primer#back-of-the-envelope-calculations), back-of-the-envelope calculations, and the [latency numbers](https://gist.github.com/jboner/2841832) table.
- [ByteByteGo](https://www.youtube.com/@ByteByteGo) on YouTube, for system design basics.
- [The reviewer guide](https://google.github.io/eng-practices/review/reviewer/) in Google's engineering practices.

**Evidence:** `docs/design.md`, your commit history, the tests, and the review thread.

### Design: requirements and estimates for pocket search

- **Study:** back-of-the-envelope calculations and the latency numbers.
- **Do:** write five functional requirements ("search a folder of markdown files") and five non-functional ones ("results in under 100 ms for 10,000 files"). Then estimate:
    - **Storage:** a dense TF-IDF matrix for 100,000 documents and a 50,000-word vocabulary in float64 is 10⁵ × 5×10⁴ × 8 bytes. Compare it with a sparse matrix at about 200 distinct words per document.
    - **Latency:** loading a 50 MB index from disk on every query, vs keeping it in memory.
    - **Throughput:** time one matrix-vector product at 10,000 documents. How many queries per second can one process serve?
- **Variations:** 100× the documents; 100× the queries.
- **Tests:** after the build, measure each estimate and write estimate vs measured in `design.md`.
- **Corner cases:** the index does not fit in memory; the folder changes while the index is being built.

### Practice 1: git and a clean repo

- **Do:** one public repo for the 100 days, with a `venv`, `requirements.txt`, a README stating your goal, and `.env` in `.gitignore` before the first commit.
- **Corner cases:** check that your API key appears nowhere in the git history.

### Practice 2: tests that prove something

- **Do:** write pytest tests with `@pytest.mark.parametrize` for your DSA solutions.
- **Seeded bugs:** clone [llm-agent-reads](https://github.com/dpaul0501/llm-agent-reads), delete the max subtraction in `softmax`, and run `pytest`. **The tests still pass.** Write a test that fails on the broken version. Do the same for two more planted bugs: ignore `mask` in `scaled_dot_product_attention`, and change `softmax`'s default `axis` to `0`.
- **Corner cases:** a test that passes on every input proves nothing. For each test, record the bug it catches.

### Practice 3: code review

- **Do:** write a ten-item review checklist. Review one peer's code with it, and leave comments on their repo.
- **Variations:** have a peer review yours, and address every comment.

## Weekly build: pocket search CLI

Combine the week into one tool. The spec, starter code, and acceptance tests are in [`week_01/`](https://github.com/dpaul0501/ai-engineer-100-labs/tree/main/week_01) of this repo.

```bash
pocket index ./docs
pocket search "rotary position" -k 5
pocket ask "why does softmax subtract the max?"
```

1. **Design doc first:** requirements, estimates, components, decisions (dense or sparse, heap or `argpartition`), and risks.
2. **Build:** lowercase word tokens, a vocabulary dict, TF-IDF vectors, vectorized cosine similarity, top-k, and an `ask` command that answers only from the top 3 snippets and checks the stop reason.
3. **Prove it:** the acceptance tests pass, and your own tests catch the seeded bugs in the lab README.
4. **Open a PR** into your own `main` that lists what AI explained and how you verified your code.

Use the `docs/` folder of [llm-agent-reads](https://github.com/dpaul0501/llm-agent-reads) as the corpus.

## End of the week

- **Defend** the build to a moderator and your peers: they pick lines, and you say what breaks if each one changes. See [the defense](https://dpaul0501.github.io/ai-engineer-100/how-it-works/#the-defense).
- **Peer mock interview:** 45 minutes in pairs on a problem from this week that your partner has not solved. See [the format](https://dpaul0501.github.io/ai-engineer-100/how-it-works/#peer-mock-interviews-every-week).
- **Publish** a README write-up that a stranger can follow.
- **Choose your two paths.** See [Choose your paths](https://dpaul0501.github.io/ai-engineer-100/paths/).
- **Value-creation step:** write down three problems people around you struggle with, where search, data, or an AI assistant could help, and one person you could ask about each.

## Suggested order

| Day | DSA | ML/DL | AI Engineering | System Design & Engineering Practice | Post idea |
|---|---|---|---|---|---|
| 1 | Two Sum, Contains Duplicate | Arrays and broadcasting | The API call | Git and a clean repo · requirements | Two Sum is a database hash join |
| 2 | Valid Anagram, Group Anagrams | Vectors and similarity | Temperature | Tests · latency estimate | Two strings that look equal but are not |
| 3 | Top K Frequent | Vectors (parameters) | Temperature (results) | Storage estimate | Why Euclidean distance can go negative |
| 4 | Product Except Self | Stable softmax | Grounded answers and retries | Seeded bugs · throughput | I broke softmax and the tests still passed |
| 5 | Longest Consecutive, Valid Sudoku | Softmax (corner cases) | Grounded answers (eval) | Code review · mock interview | The question my snippets could not answer |
| 6 | Weekly build | | | Design doc first | My search tool on a real folder |
| 7 | Defense, write-up, paths | | | | What the defense exposed |

## Done when

- [ ] 8 DSA problems, each with a solution, 1–2 variations, tests, and corner cases
- [ ] 3 ML/DL concepts, each matched against the library, with corner cases and a parameter table
- [ ] 3 AI experiments, each with results, an eval or count, and a cost log
- [ ] `design.md` with requirements, estimates, and estimate vs measured
- [ ] The pocket search PR passes the acceptance tests and was defended
- [ ] Your two paths are chosen
- [ ] A post for every day you worked
