# Month 1 · AI Engineer + FDE

Four builds, each one used by the next. By Day 30 you have an agent that runs on parts you wrote yourself: your tokenizer and decoder, your context and memory library, and your search engine.

Every week has the same shape: **use** the real thing, **measure** it, then **rebuild** its core. Every build goes spec → contract → test → code, with your failing tests committed first.

| Wk | Days | Build | DSA | ML | AI | System Design | Software Delivery |
|---|---|---|---|---|---|---|---|
| 1 | 1–7 | **[Tokens and decoding](weeks/week_01.md):** a BPE tokenizer, samplers, and a decoder that can only output valid JSON | Hashing, heaps with lazy deletion, tries, stacks and automata, prefix sums | Maximum likelihood, perplexity, softmax and temperature, top-k and top-p | Tokenization and the token tax, beam search, structured output | ◆ Web crawler · Unique IDs | Golden and property tests, planted bugs, CI |
| 2 | 8–14 | **Prompt, context and memory engineering:** context within a token budget, compaction, short- and long-term memory | Sliding window, LRU/LFU caches, intervals, priority queues | Entropy, cosine similarity, position effects | System prompts, few-shot selection, compaction, episodic and semantic memory, prompt caching | ◆ Rate limiter · Distributed cache | Prompt versioning, contract tests for prompts |
| 3 | 15–21 | **RAG and search:** inverted index, BM25, HNSW, hybrid retrieval, reranking, GraphRAG | Inverted index, top-K heaps, k-way merge, HNSW graphs, MinHash and union-find | TF-IDF and BM25, embeddings, contrastive loss, nDCG | Chunking, rank fusion, reranking, access-controlled retrieval, untrusted text | ◆ Web search · Autocomplete | Ingestion pipeline, data contracts, freshness |
| 4 | 22–30 | **Month project: the agentic harness:** agent loop, tools, skills, MCP, subagents, permissions | State machines, backtracking, DAGs and topological sort | pass@k, bootstrap intervals, variance across seeds | Tool schemas with Week 1's constrained decoding; Week 2 memory and Week 3 search as tools | ◆ Chat · Job scheduler | Sandboxing, tracing, prompt-injection tests, release |

**Kaggle reps:** Titanic · House Prices · LLM Science Exam · AI Mathematical Olympiad.

**How the weeks connect:**

- Week 1's constrained decoder is how Week 4's agent produces valid tool calls.
- Week 2's memory and Week 3's search become tools the Week 4 agent can call.
- Each week ends with a capstone design: the week's build as a service, defended with numbers.

**Day 30:** the month project defense, the idea review, and choosing your major (Systems, Models, Agents, or Architecture). Weeks 2–4 open here as they are released.
