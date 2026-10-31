# Month 1 · AI Engineer + FDE

Four builds, each one used by the next. By Day 30 you have an agent that runs on parts you wrote yourself: your tokenizer and decoder, your context and memory library, and your search engine.

Every week has the same shape: **use** the real thing, **measure** it, then **rebuild** its core. Every build goes spec → contract → test → code, with your failing tests committed first.

| Week | Days | Build |
|---|---|---|
| 1 | 1–7 | **[Tokens and decoding](weeks/week_01.md):** a BPE tokenizer, samplers, and a decoder that can only output valid JSON |
| 2 | 8–14 | **Prompt, context and memory engineering:** context within a token budget, compaction, short- and long-term memory |
| 3 | 15–21 | **RAG and search:** inverted index, BM25, HNSW, hybrid retrieval, reranking, GraphRAG |
| 4 | 22–30 | **Month project, the agentic harness:** agent loop, tools, skills, MCP, subagents, permissions |

## Week 1 · Tokens and decoding

- **DSA:** hashing, heaps with lazy deletion, tries, stacks and automata, prefix sums
- **ML:** maximum likelihood, perplexity, softmax and temperature, top-k and top-p
- **AI:** tokenization and the token tax, beam search, structured output
- **System Design:** ◆ web crawler · unique IDs · capstone: a structured-output service
- **Software Delivery:** golden and property tests, planted bugs, CI
- **Kaggle:** Titanic

## Week 2 · Prompt, context and memory engineering

- **DSA:** sliding window, LRU/LFU caches, intervals, priority queues
- **ML:** entropy, cosine similarity, position effects ("lost in the middle")
- **AI:** system prompts, few-shot selection, compaction, episodic and semantic memory, prompt caching
- **System Design:** ◆ rate limiter · distributed cache
- **Software Delivery:** prompt versioning, contract tests for prompts
- **Kaggle:** House Prices

## Week 3 · RAG and search

- **DSA:** inverted index, top-K heaps, k-way merge, HNSW graphs, MinHash and union-find
- **ML:** TF-IDF and BM25, embeddings, contrastive loss, nDCG
- **AI:** chunking, rank fusion, reranking, access-controlled retrieval, retrieved text as untrusted input
- **System Design:** ◆ web search · autocomplete
- **Software Delivery:** ingestion pipeline, data contracts, freshness and deletes
- **Kaggle:** LLM Science Exam

## Week 4 · Month project: the agentic harness

- **DSA:** state machines, backtracking, DAGs and topological sort
- **ML:** pass@k, bootstrap intervals, variance across seeds
- **AI:** tool schemas using Week 1's constrained decoding; Week 2 memory and Week 3 search as tools; skills, MCP, subagents
- **System Design:** ◆ chat · job scheduler
- **Software Delivery:** sandboxing, tracing, prompt-injection tests, release
- **Kaggle:** AI Mathematical Olympiad

## How the weeks connect

- Week 1's constrained decoder is how Week 4's agent produces valid tool calls.
- Week 2's memory and Week 3's search become tools the Week 4 agent can call.
- Each week ends with a capstone design: the week's build as a service, defended with numbers.

**Day 30:** the month project defense, the idea review, and choosing your major (Systems, Models, Agents, or Architecture). Weeks 2–4 open here as they are released.
