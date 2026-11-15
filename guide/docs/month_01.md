# Month 1 · AI Engineer + FDE

Every week is built around **one hard design problem** of the kind top companies ask in interviews. The week reading poses it and solves it end to end; each day goes deeper on one part of the design, in ML, algorithms and system design; the weekend build ships a small, tested version.

Every build goes spec → contract → test → code, with your failing tests committed first.

| Week | Days | The problem | Build |
|---|---|---|---|
| 1 | 1–7 | **[Design People You May Know](week_01/index.html)** | Friends-of-friends recommendations on a 10,000-user graph: exact counting, scale and skew, sharding, approximate candidates, an ML ranker, serving |
| 2 | 8–14 | **Representation learning** (next) | From word embeddings to user embeddings: learned representations that replace hand-made features |
| 3 | 15–21 | **[Tokenization](week_03/index.html)** | Byte-level BPE from first principles, with a tested tokenizer of your own |

The weeks after Week 3 are being reordered; their topics are listed below.

## Week 1 · People You May Know

Start at the [week reading](week_01/index.html), then work through [Day 1](week_01/day_1.html) to [Day 5](week_01/day_5.html) and finish with the [worksheet and learning checks](week_01/worksheet.html). The problem grows each day: count mutual friends exactly, see why popular people make it slow, read less with sampling, MinHash and LSH, learn who connects with a model, then take it to a billion users as a system and a product. The [talk](week_01/talk.html) presents the whole design as slides.

- **DSA:** graph representations, traversal, hash counting, set intersection, top-k, triangle counting, consistent hashing, MinHash and LSH, Bloom filters, personalized PageRank, k-way merge
- **ML:** triadic closure, heavy-tailed degrees and the friendship paradox, percentiles with error bars, sampling estimators and recall@K, link prediction with logistic regression, AUC
- **System Design:** back-of-envelope estimation, tail latency at scale, sharding and graph stores, precompute vs online, incremental updates, the serving architecture, A/B tests
- **Software Delivery:** the function contract, golden, property and differential tests against a brute-force baseline

## Week 3 · Tokenization

Start at the [week reading](week_03/index.html), then work through [Day 1](week_03/day_1.html) to [Day 5](week_03/day_5.html) and finish with the [worksheet and learning checks](week_03/worksheet.html).

- **DSA:** hash maps and sliding windows, greedy vs optimal, Huffman, heaps with lazy deletion, inverted index, linked lists, LRU cache, heavy hitters and sketches
- **ML:** Zipf's law, the length / vocabulary / learnability trade-off, entropy and bits per byte, sufficient statistics, BPE-dropout
- **AI:** the token tax, production split patterns, glitch tokens and other tokenizer-caused failures
- **System Design:** the vocabulary budget, training on terabytes (MapReduce), serving and versioning a tokenizer
- **Software Delivery:** contracts and invariants, golden, property and differential tests, a versioned file format

## Later in Month 1 (order to be decided)

### Prompt, context and memory engineering

- **DSA:** sliding window, LRU/LFU caches, intervals, priority queues
- **ML:** entropy, cosine similarity, position effects ("lost in the middle")
- **AI:** system prompts, few-shot selection, compaction, episodic and semantic memory, prompt caching
- **System Design:** ◆ rate limiter · distributed cache
- **Software Delivery:** prompt versioning, contract tests for prompts
- **Practice:** replicate "lost in the middle": accuracy vs where a fact sits in the context, with binomial confidence intervals · Kaggle [LLM Prompt Recovery](https://www.kaggle.com/competitions/llm-prompt-recovery) (recover the rewrite prompt; a cubed cosine-similarity metric)

### RAG and search

- **DSA:** inverted index, top-K heaps, k-way merge, HNSW graphs, MinHash and union-find
- **ML:** TF-IDF and BM25, embeddings, contrastive loss, nDCG
- **AI:** chunking, rank fusion, reranking, access-controlled retrieval, retrieved text as untrusted input
- **System Design:** ◆ web search · autocomplete
- **Software Delivery:** ingestion pipeline, data contracts, freshness and deletes
- **Practice:** evaluate your search on a public benchmark with nDCG and bootstrap intervals · Kaggle [LLM Science Exam](https://www.kaggle.com/competitions/kaggle-llm-science-exam) (RAG over Wikipedia, MAP@3)

### The agentic harness (month project)

- **DSA:** state machines, backtracking, DAGs and topological sort
- **ML:** pass@k, bootstrap intervals, variance across seeds
- **AI:** tool schemas with constrained decoding; the memory and search builds as tools; skills, MCP, subagents
- **System Design:** ◆ chat · job scheduler
- **Software Delivery:** sandboxing, tracing, prompt-injection tests, release
- **Practice:** the unbiased pass@k estimator, and how often majority voting is right as samples grow · Kaggle [AI Mathematical Olympiad](https://www.kaggle.com/competitions/ai-mathematical-olympiad-prize) (an agent that writes and runs code)
