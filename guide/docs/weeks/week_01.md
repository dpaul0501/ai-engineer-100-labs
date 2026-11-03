# Week 1 · Tokens and Decoding

**Month 1: AI Engineer + FDE** · Self-paced · AI rule: **AI explains, you type.** Ask AI to explain or review. Do not paste code it writes.

## This week

A language model does exactly one thing: given token ids, it scores every possible next token. Everything around that is engineering, and this week you build it:

- **in front of the model:** a byte-level **BPE tokenizer**, which decides what a "token" is, and so what text costs
- **after the model:** the **decoding loop**: softmax, temperature, top-k, top-p, beam search
- **a guarantee:** a **grammar-constrained decoder** that makes invalid JSON impossible, not just unlikely
- **the model in the middle:** an **n-gram model**, the baseline every later model must beat

### The problem

A support team wants every incoming ticket turned into a JSON record by a language model, in English and Hindi. Two things go wrong at once: **some answers do not parse**, and **Hindi costs several times more tokens** for the same meaning. Neither is the model's fault. Both are decided by the tokenizer before the model and the decoder after it, and you build both this week, ending with output that is valid *by construction*.

### What you will be able to do

| Dimension | Learning objectives |
|---|---|
| **DSA** | Count with hash maps and keep the best item under updates with a heap and lazy deletion. Store shared prefixes in a trie and prune whole subtrees. Recognise nested structure with a stack and an automaton. Sample with prefix sums and binary search |
| **ML** | Derive why counting is maximum likelihood, and smooth it. Measure a model with cross-entropy and perplexity. Compute softmax stably and explain temperature as entropy. Explain masking as conditioning |
| **AI** | Train and use a byte-level BPE tokenizer and measure the token tax. Choose between greedy, sampling, top-k, top-p and beam search. Guarantee structured output the way production engines do |
| **System Design** | Estimate and design a web crawler and a unique ID generator. Design an end-to-end structured-output service with numbers (the capstone) |
| **Software Delivery** | Work spec → contract → test → code. Write property tests and catch planted bugs. Ship a package with CI |

The [Week 1 tutorial](../tutorials/week_01.html) teaches each concept with its code, a live demo, the DSA and ML fundamentals underneath, and the LeetCode problems that practise it.

The tokenizer has its own week-long chapter, [BPE from first principles](../week_01/index.html): a main reading with the problem, the formulation, the algorithm, the code and a worked example; then five days, each with an ML, an algorithms and a design block (reading, practice, variations, solutions, further reading); then a weekend build. Its checkpoints fill a coverage tracker by dimension.

**Pre-read (one page each, before Day 1):** calling an LLM API with JSON output; running a small open model locally with [Ollama](https://ollama.com/). These are background, not the week.

**Real-world deliverable:**
- your package on **TestPyPI**
- a post with two tables: **bytes per token** for English vs Hindi (yours vs GPT-2's), and the **valid-JSON rate**, free vs constrained

| Block | Time | What |
|---|---|---|
| Lecture | 75 min | The [Week 1 tutorial](../tutorials/week_01.html), one segment per dimension |
| Project | ~20 h | Seven milestones, in the order spec → contract → test → code |
| DSA reps | 45 min/day | 13 problems: hashing, heaps, tries, stacks and automata, sampling |
| System design | ~3 h | ◆ Web crawler (timed mock) and a unique ID generator |
| Practice projects | ~4 h | A token-tax study with confidence intervals, and Kaggle's *LLM - Detect AI Generated Text* with your own tokenizer |

### Every unit follows the same cycle

1. **Study** the suggested source. For DSA, try the problem first and study after.
2. **Do** it yourself: no AI, no peeking.
3. **Variations:** make 1–2 changes of your own and solve or run them.
4. **Tests** for the original.
5. **Corner cases** for the original.

Commit each unit to your repo. Post one finding a day as **Day N/100**.

## The lecture (75 min)

| Segment | Content |
|---|---|
| The problem (10 min) | Ask a model for JSON 50 times: some answers do not parse. Ask in Hindi: it costs more tokens for the same meaning. Both come from the code around the model, not the model |
| AI (15 min) | Bytes and UTF-8, BPE training, encoding by merge rank. Live: train on `aaabdaaabac` by hand, then in code |
| ML (15 min) | Counting is maximum likelihood; perplexity; softmax, temperature, top-k, top-p as operations on one probability vector. Live: the same logits at T = 0.5, 1, 2 |
| DSA (15 min) | The merge heap with lazy deletion; JSON as a pushdown automaton (a state machine with a stack); a vocabulary trie that prunes thousands of tokens at once. Live: brute-force mask vs trie mask on GPT-2's vocabulary |
| Software Delivery (15 min) | Spec → contract → test → code. Protocols, golden tests, property tests that generate thousands of JSON values, planted bugs. Live: Hypothesis finds a round-trip bug |
| Done looks like (5 min) | The milestones, the experiment table, and the defense |

## The project: `tok`

The spec, contracts, starter code, and 50 acceptance tests are in [`week_01/`](https://github.com/dpaul0501/ai-engineer-100-labs/tree/main/week_01).

### The five dimensions

| Dimension | The constraint | You learn |
|---|---|---|
| **AI** | The tokenizer **round-trips any Unicode text**, and its compression is **within 10% of Hugging Face `tokenizers`**. **Every** constrained sample is valid JSON so far, and every finished one parses | What a token is, what decoding does, and how structured output is guaranteed |
| **ML** | **Probabilities sum to 1** for every context. An untrained model's **perplexity equals the vocabulary size**. Sampling frequencies match **softmax(logits / T)** | Maximum likelihood, smoothing, perplexity, softmax, temperature, nucleus sampling |
| **DSA** | Training gives **the naive spec's merges in under 3 seconds**. The mask **equals brute force** on every state, and the trie is **over 4× faster** where few tokens fit | Hash maps, heaps with lazy deletion, tries, finite and pushdown automata |
| **System Design** | Two one-page designs with numbers, one of them a timed mock | Estimation, frontier and dedup design, ID layouts |
| **Software Delivery** | `SPEC.md` and failing tests are committed **before any code**. Streaming stays **under 5 MB of peak memory**. Your tests catch the planted bugs | Spec-first development, contracts, property and golden tests, mutation testing, CI |

### Milestones

1. **Spec and red tests.** Fill in `SPEC.md`, including your estimates, and write `tests/test_mine.py`. Commit with everything red. *Check: the commit exists before any implementation.*
2. **BPE.** `merge`, a naive `train`, then the heap version. *Check: the golden, naive-spec and speed tests pass.*
3. **Encode, decode, save, load, stream.** *Check: the round-trip property test passes on 300 random strings; streaming stays flat.*
4. **The n-gram model and samplers.** `logprobs`, `log_softmax`, `top_k_filter`, `top_p_filter`, `categorical`, `Sampler`. *Check: the n-gram and sampling tests pass.*
5. **Decoding loops.** `generate`, `greedy`, `beam_search`. *Check: width 1 equals greedy; a wide beam finds the exact best.*
6. **The JSON automaton and the constraint.** `step`, `is_valid_json`, `TokenTrie`, `JsonConstraint`. *Check: every grammar test passes, and the mask matches brute force.*
7. **Ship.**
    - The CLI, and the experiment table (free vs constrained, across n and temperature).
    - GitHub Actions running `pytest`.
    - The package on TestPyPI.
    - The post, and estimated vs measured numbers filled in `SPEC.md`.

### Depth extensions (try one)

| Major | Extension |
|---|---|
| Systems | Profile `allowed()` on GPT-2's vocabulary. Precompute, per automaton mode, the tokens whose validity does not depend on the stack (XGrammar's idea), and measure the speedup |
| Models | Add **min-p** sampling and a repetition penalty. Measure how each changes the valid-JSON rate and the diversity of the samples |
| Agents | Extend the grammar to a **schema**: a fixed set of keys with types (`"priority"` must be one of three strings). This is what "structured outputs" in an API does |
| Architecture | Design a structured-output service for 10,000 requests a second: where masks are computed, what is cached, and what a schema change costs |

## AI: tokens and decoding

**Study sources this week:**

- Andrej Karpathy, [Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE) (video) and [minbpe](https://github.com/karpathy/minbpe) (code).
- Imad Dabbura, [Byte Pair Encoding from Scratch](https://imaddabbura.github.io/posts/nlp/BPE-Tokenizer.html): a short, code-first walkthrough.
- Patrick von Platen, [How to generate text](https://huggingface.co/blog/how-to-generate) (Hugging Face blog): greedy, beam, top-k, top-p, side by side.
- Chip Huyen, [Generation configurations: temperature, top-k, top-p, and test time compute](https://huyenchip.com/2024/01/16/sampling.html), including structured outputs.
- MLC, [Structured generation with XGrammar](https://blog.mlc.ai/2024/11/22/achieving-efficient-flexible-portable-structured-generation-with-xgrammar): pushdown automata and why most of a mask can be precomputed.
- Papers: Sennrich et al., [BPE for NMT](https://arxiv.org/abs/1508.07909); Holtzman et al., [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751) (top-p); Willard and Louf, [Efficient Guided Generation](https://arxiv.org/abs/2307.09702) (Outlines).

### 1. Bytes, UTF-8, and BPE

- **Study:** how UTF-8 encodes a code point in 1–4 bytes; the merge loop in minbpe's `basic.py`; why encoding applies merges by **rank**, not frequency.
- **Do:** Milestones 2–3.
- **Variations:** train without pre-tokenization and show the merges that cross word boundaries; break ties by first occurrence and diff the merges.
- **Tests:** the golden example; your heap trainer against your naive trainer on random texts.
- **Corner cases:** overlapping pairs (`aaaa`); decoding one byte of a multi-byte character (gives `�`).

### 2. From logits to one token

- **Study:** the Hugging Face and Chip Huyen posts above.
- **Do:** Milestones 4–5.
- **Variations:** add min-p; implement beam search with a length penalty and show when it changes the winner.
- **Tests:** frequency tests for temperature; width 1 beam equals greedy.
- **Corner cases:** every logit `-inf`; logits of 1,000 (overflow without the max shift); ties at the k-th place.

### 3. Structured output by construction

- **Study:** the XGrammar post; [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259), sections 2–7 (JSON's grammar is two pages); llama.cpp's [GBNF grammars](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md).
- **Do:** Milestone 6, then run the experiment.
- **Variations:** allow one space after `:` and `,`; restrict keys to a fixed list.
- **Tests:** every value `json.dumps` writes is accepted; anything you accept, `json.loads` parses; the mask equals brute force.
- **Corner cases:** a number has no closing character (`[12` could continue); a token that closes the object *and* starts something else; a string that never ends before `max_new_tokens`.

## ML: probability and sampling

**Study sources this week:**

- Chapter 3, "N-gram Language Models", of Jurafsky and Martin, [Speech and Language Processing](https://web.stanford.edu/~jurafsky/slp3/).
- Sebastian Raschka, [temperature, top-k and top-p](https://sebastianraschka.com/faq/docs/temperature-topk-topp-sampling.html) (short FAQ).
- [3Blue1Brown](https://www.youtube.com/@3blue1brown), *Solving Wordle using information theory*, for entropy.

### 1. Counting is maximum likelihood

- **Do:** derive count(ctx, w) / count(ctx) with a Lagrange multiplier on one page, and check it numerically.
- **Variations:** add-k smoothing as a Dirichlet prior.
- **Corner cases:** an unseen context gives 0/0. What does your model return?

### 2. Perplexity

- **Do:** show that a uniform model over V tokens has perplexity V (an acceptance test). Fill the perplexity table for n = 1–4 on held-out records.
- **Variations:** convert to **bits per byte**, so tokenizers with different vocabularies can be compared.

### 3. Softmax, temperature, and entropy

- **Do:** prove softmax(x + c) = softmax(x). Plot the entropy of softmax(x / T) as T goes from 0.1 to 10. What are the limits?
- **Variations:** show that temperature never changes which tokens are top-k, but does change which are top-p. (This is why one of your planted bugs cannot be caught.)

### 4. What a mask does to the distribution

- **Do:** masking then renormalizing is the same as conditioning on "the next token is valid". Show it, and measure how much probability your model puts on invalid tokens at each step.
- **Corner cases:** why can constrained output still be *wrong* (valid JSON, wrong values)?

## DSA: hashing, heaps, tries, stacks and automata, sampling

**Focus.** A hash map counts pairs; a heap finds the best one; a trie shares prefixes; a stack remembers what is open. Every one of them is inside `tok`.

**Study sources this week:**

- [NeetCode roadmap](https://neetcode.io/roadmap): problems grouped by pattern, each with a video.
- [take U forward](https://www.youtube.com/@takeUforward) (Striver) on YouTube, for a second explanation.
- [Hashing](https://mldsa.github.io/docs/part1/chapter01-hashing/) and [Top-K](https://mldsa.github.io/docs/part1/chapter02-topk/) in *From LeetCode to Learning Systems*.

**Evidence per problem:** `solution.py`; one or two `variation_N.py` files with the changed problem at the top; and `test_solution.py` with the corner cases marked.

| # | Problem | Pattern | Where it is in `tok` |
|---|---|---|---|
| 1 | [Two Sum](https://leetcode.com/problems/two-sum/) (1) | Hash map | Pair counts |
| 2 | [Group Anagrams](https://leetcode.com/problems/group-anagrams/) (49) | Canonical key | The mask cache keys on a hashable state |
| 3 | [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) (347) | Count + heap | BPE's best pair; top-k sampling |
| 4 | [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) (215) | Heap of size k / quickselect | `top_k_filter` in O(V log k) |
| 5 | [Find K Pairs with Smallest Sums](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/) (373) | Heap over candidate frontiers | Beam search |
| 6 | [Implement Trie](https://leetcode.com/problems/implement-trie-prefix-tree/) (208) | Trie | `TokenTrie` |
| 7 | [Design Add and Search Words](https://leetcode.com/problems/design-add-and-search-words-data-structure/) (211) | Trie + DFS | Walking the trie with a state |
| 8 | ★ [Word Search II](https://leetcode.com/problems/word-search-ii/) (212) | Trie + pruned DFS | Pruning a subtree on the first invalid byte |
| 9 | [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) (20) | Stack | The automaton's stack of open `{` and `[` |
| 10 | [Decode String](https://leetcode.com/problems/decode-string/) (394) | Stack of contexts | Nested objects and arrays |
| 11 | ★ [Valid Number](https://leetcode.com/problems/valid-number/) (65) | Finite automaton | The number DFA inside the grammar |
| 12 | [Random Pick with Weight](https://leetcode.com/problems/random-pick-with-weight/) (528) | Prefix sums + binary search | `categorical` |
| 13 | ★ [Linked List Random Node](https://leetcode.com/problems/linked-list-random-node/) (382) | Reservoir sampling | The held-out split |

For each: **Variations** (two per problem, of your own), **Corner cases** (empty input, ties, one element), and one line on where it shows up in `tok`.

## System Design: web crawler and unique IDs

Write each design as a one-page doc: requirements with numbers, estimates (QPS, storage, bandwidth), the API, the data model, a diagram, two deep dives, the bottlenecks, and the failure you do *not* handle.

Sources: Alex Xu, *System Design Interview* Vol. 1, chapters 7 and 9; [Bloom filters](https://en.wikipedia.org/wiki/Bloom_filter).

### ◆ Web crawler (45-minute timed mock with a peer and a moderator)

**Prompt:** crawl 1 billion pages a month for a search engine.

- **Numbers to produce:** pages per second (average and peak), storage per month and over 5 years, and bandwidth.
- **Deep dives:** the URL frontier, with priority and politeness per host; "seen URL" with a Bloom filter and "seen content" with hashes.
- **Also cover:** robots.txt, DNS caching, spider traps, and recrawl freshness.

### Unique ID generator

**Prompt:** 64-bit IDs, roughly sortable by time, more than 10,000 per second on each machine, across data centres, with no coordination on each request.

- **Compare:** UUIDv4, UUIDv7, a ticket server, multi-master auto-increment, and Snowflake.
- **Deep dives:** the Snowflake bit layout (how many years the timestamp lasts, and IDs per millisecond per machine), and what happens when the clock goes backwards.

## Capstone: design `tok-serve`

Put the week together as one system and defend it with numbers: a service that takes a ticket and a JSON shape and returns a record that always parses, at 10,000 requests a second.

- **Requirements:** `POST /extract {ticket, grammar}`; English and Hindi; about 150 output tokens per request, so **1.5 million masked steps a second**; the mask adds at most 1 ms per step at p99; a retried request never creates a second record.
- **Components:** API → tokenizer with a chunk cache → model server → mask service → sampler → record store.
- **Deep dives, using your own measurements:** can the mask keep up (brute force vs trie vs precomputing per mode)? What does the mask cache key on, and how is it bounded? How does the Hindi share change capacity? How do idempotency keys work (reuse your unique ID design)? What happens at the token limit?
- **Principles to name in the defense, each tied to your code:** contracts at every boundary; make invalid states unrepresentable; immutable, hashable state; precompute what does not change and cache what repeats; incremental over recompute; determinism (tie-breaks, seeds, versions); bound everything; measure before optimizing.

**Deliverable:** a one-page design doc with a diagram, a number on every arrow, and the principle each component follows. Present it at the defense.

## Software Delivery: spec, contracts, tests

**Study sources this week:**

- [Hypothesis](https://hypothesis.readthedocs.io/en/latest/quickstart.html) quickstart: property-based testing.
- [typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol) and [PEP 544](https://peps.python.org/pep-0544/): structural contracts.
- [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/), including TestPyPI.
- [Building and testing Python](https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python) with GitHub Actions.

### Practice 1: spec first, tests red

- **Do:** Milestone 1. Name each of your tests after the bug it catches, for example `test_top_p_keeps_the_token_that_crosses_p`.
- **Corner cases:** a test that passes on the stub proves nothing. Run your tests on the stubs first.

### Practice 2: properties, not examples

- **Do:** write three properties of your own: round trip for any text; every `json.dumps` output is accepted; the trie mask equals brute force.
- **Variations:** a golden test that freezes your tokenizer's ids on 20 sentences.

### Practice 3: planted bugs

- **Do:** plant five bugs in your own code (an off-by-one in top-p, a missing max shift, a trailing comma the grammar accepts). Does your suite catch each? Then find a bug no test *can* catch, and explain why it is harmless.

### Practice 4: package, CLI, CI

- **Do:** `pip install -e .` and `tok --help` work. GitHub Actions runs `pytest` on push. Publish to TestPyPI as `tok-<your-handle>`.

## Practice projects: use what you built on real data

Both projects reuse `tok` and practise this week's probability and statistics on real data.

### 1. The token tax, with error bars (~1.5 h)

**Question:** how many more tokens does the same sentence cost in Indian languages, and how sure are you?

- **Data:** [FLORES+](https://huggingface.co/datasets/openlanguagedata/flores_plus) `devtest`: the same 1,012 sentences translated into 200+ languages, so every comparison is paired. It is gated: accept the terms on Hugging Face, and use it only for evaluation, as its card asks.
- **Do:** for English, Hindi, Tamil, Bengali and one more language, count tokens per sentence with `gpt2`, `cl100k_base`, `o200k_base` (tiktoken) and your own tokenizer trained on TinyStories.
- **Statistics:**
    - Use the **paired** ratio per sentence (language tokens / English tokens), not the ratio of two averages. Report both, and explain why they differ.
    - A **bootstrap 95% confidence interval** for the mean ratio: resample sentences with replacement 10,000 times.
    - Is `o200k_base` better than `cl100k_base` for Hindi? Bootstrap the paired *difference* and say whether the interval excludes 0.
- **Deliverable:** one table and one chart with error bars, used in your post.

### 2. Kaggle: [LLM - Detect AI Generated Text](https://www.kaggle.com/competitions/llm-detect-ai-generated-text) (~2.5 h)

**Question:** was this essay written by a student or by an LLM? The metric is ROC AUC. The competition has ended, but late submissions are scored.

- **Why this one:** strong public solutions trained their own **BPE tokenizer**, then counted **token n-grams**. That is exactly `tok`.
- **Do:**
    1. Write a **data contract** for the CSVs (columns, types, label values), run as a test.
    2. Train your `BPE` on the essays; encode everything.
    3. **Model A, two language models:** fit one `NGramLM` on human essays and one on generated essays (the competition's train set has few generated essays; add a public generated-essay dataset and cite it). Score an essay by the **log-likelihood ratio** log P(essay | AI) − log P(essay | human). This is naive Bayes with an n-gram model, and it uses your perplexity code directly.
    4. **Model B:** TF-IDF over your token n-grams, then logistic regression.
    5. Validate with stratified 5-fold cross-validation; report mean ± standard deviation of AUC, then submit.
- **Probability and statistics:**
    - Bayes' rule: why the likelihood ratio is the optimal score when the two models are right, and what the prior P(AI) changes (nothing, for AUC).
    - **AUC is a probability:** the chance that a random AI essay scores above a random human one. Compute it from that definition with pairs, and check it matches `sklearn`.
    - Which n gives the best likelihood ratio? Relate it to the perplexity table from the lab.
- **Deliverable:** a public notebook, your CV and leaderboard scores, and one paragraph on the gap.

## End of the week

- **Defend** `tok` to a moderator and your peers. Expect questions like:
  - "Why is your merge loop not O(merges × corpus)?"
  - "How does your automaton know a number has ended?"
  - "Why can't any test catch temperature applied after top-k?"
  - "Show me the commit where this test was red."
- **Peer mock interview:** 45 minutes on a problem from this week's DSA reps.
- **Publish** the post with both tables.

## Practical question

A constrained decoder guarantees the JSON parses. What does it *not* guarantee, and how would you find out how often that happens?

## Suggested order

| Day | DSA | Project | ML | Software Delivery | Other |
|---|---|---|---|---|---|
| 1 | Two Sum, Group Anagrams | Read the starter; write `SPEC.md` | Counting is MLE | Practice 1 (red tests) | Lecture |
| 2 | Top K Frequent, Kth Largest | Milestone 2 (BPE) | — | Practice 2 | Token tax: FLORES+ counts |
| 3 | Random Pick with Weight, Random Node | Milestone 3 (round trip, streaming) | Perplexity | — | Design: unique ID generator |
| 4 | Find K Pairs | Milestones 4–5 (samplers, decoding) | Softmax and temperature | — | Token tax: bootstrap intervals |
| 5 | Implement Trie, Add and Search Words | Milestone 6 (automaton) | — | Practice 3 | ◆ Design mock: web crawler · Kaggle: data contract, baseline |
| 6 | Valid Parentheses, Decode String, Valid Number | Milestone 6 (constraint), the experiment | What a mask does | Practice 4 | Kaggle: tokenizer, two n-gram models, submit |
| 7 | Word Search II, peer mock | Milestone 7 (ship) | — | — | Capstone design, defense, post |

## Done when

- [ ] `SPEC.md` filled in, with estimated vs measured numbers
- [ ] The commit with red tests comes before any implementation
- [ ] All 50 acceptance tests pass, and your own tests catch the planted bugs at the defense
- [ ] `tok` on TestPyPI, and CI green
- [ ] The experiment table: free vs constrained, across n and temperature
- [ ] 13 DSA problems, each with a solution, 1–2 variations, tests and corner cases
- [ ] 4 ML units, with the perplexity table
- [ ] Two design docs, one of them mocked, and the `tok-serve` capstone design
- [ ] The token-tax table with bootstrap intervals, and a Kaggle submission with a public notebook
- [ ] The post
