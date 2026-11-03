# Month 1 · AI Engineer + FDE

Four builds, each one used by the next. By Day 30 you have an agent that runs on parts you wrote yourself: your tokenizer and decoder, your context and memory library, and your search engine.

Every week has the same shape: **use** the real thing, **measure** it, then **rebuild** its core. Every build goes spec → contract → test → code, with your failing tests committed first. Each week's **practice projects** apply the build to real data; a Kaggle competition is used only when it exercises that week's probability and statistics.

| Week | Days | Build |
|---|---|---|
| 1 | 1–7 | **[Tokenization](week_01/index.html):** byte-level BPE from first principles: the week reading, five days of ML, algorithms and design, and a weekend build |
| 2 | 8–14 | **Prompt, context and memory engineering:** context within a token budget, compaction, short- and long-term memory |
| 3 | 15–21 | **RAG and search:** inverted index, BM25, HNSW, hybrid retrieval, reranking, GraphRAG |
| 4 | 22–30 | **Month project, the agentic harness:** agent loop, tools, skills, MCP, subagents, permissions |

## Week 1 · Tokenization

Start at the [week reading](week_01/index.html), then work through [Day 1](week_01/day_1.html) to [Day 5](week_01/day_5.html) and finish with the [worksheet and learning checks](week_01/worksheet.html).

- **DSA:** hash maps and sliding windows, greedy vs optimal, Huffman, heaps with lazy deletion, inverted index, linked lists, LRU cache
- **ML:** Zipf's law, the length / vocabulary / learnability trade-off, entropy and bits per byte, sufficient statistics, BPE-dropout
- **AI:** the token tax, production split patterns, glitch tokens and other tokenizer-caused failures
- **System Design:** the vocabulary budget, training on terabytes (MapReduce), serving and versioning a tokenizer
- **Software Delivery:** contracts and invariants, golden, property and differential tests, a versioned file format
- **Practice:** a token-tax study on FLORES+ with bootstrap intervals, and a vocabulary sweep on held-out text

## Week 2 · Prompt, context and memory engineering

- **DSA:** sliding window, LRU/LFU caches, intervals, priority queues
- **ML:** entropy, cosine similarity, position effects ("lost in the middle")
- **AI:** system prompts, few-shot selection, compaction, episodic and semantic memory, prompt caching
- **System Design:** ◆ rate limiter · distributed cache
- **Software Delivery:** prompt versioning, contract tests for prompts
- **Practice:** replicate "lost in the middle": accuracy vs where a fact sits in the context, with binomial confidence intervals · Kaggle [LLM Prompt Recovery](https://www.kaggle.com/competitions/llm-prompt-recovery) (recover the rewrite prompt; a cubed cosine-similarity metric)

## Week 3 · RAG and search

- **DSA:** inverted index, top-K heaps, k-way merge, HNSW graphs, MinHash and union-find
- **ML:** TF-IDF and BM25, embeddings, contrastive loss, nDCG
- **AI:** chunking, rank fusion, reranking, access-controlled retrieval, retrieved text as untrusted input
- **System Design:** ◆ web search · autocomplete
- **Software Delivery:** ingestion pipeline, data contracts, freshness and deletes
- **Practice:** evaluate your search on a public benchmark with nDCG and bootstrap intervals · Kaggle [LLM Science Exam](https://www.kaggle.com/competitions/kaggle-llm-science-exam) (RAG over Wikipedia, MAP@3)

## Week 4 · Month project: the agentic harness

- **DSA:** state machines, backtracking, DAGs and topological sort
- **ML:** pass@k, bootstrap intervals, variance across seeds
- **AI:** tool schemas using Week 1's constrained decoding; Week 2 memory and Week 3 search as tools; skills, MCP, subagents
- **System Design:** ◆ chat · job scheduler
- **Software Delivery:** sandboxing, tracing, prompt-injection tests, release
- **Practice:** the unbiased pass@k estimator, and how often majority voting is right as samples grow · Kaggle [AI Mathematical Olympiad](https://www.kaggle.com/competitions/ai-mathematical-olympiad-prize) (an agent that writes and runs code)

## How the weeks connect

- Week 1's constrained decoder is how Week 4's agent produces valid tool calls.
- Week 2's memory and Week 3's search become tools the Week 4 agent can call.
- Each week ends with a capstone design: the week's build as a service, defended with numbers.

**Day 30:** the month project defense, the idea review, and choosing your major (Systems, Models, Agents, or Architecture). Weeks 2–4 open here as they are released.
