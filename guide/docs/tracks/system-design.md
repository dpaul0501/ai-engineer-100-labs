# System Design

Each week's design problem taken to production: estimates with stated assumptions, storage and sharding, caching, tail latency, and the serving architecture.

## Week 1: People You May Know

- **[Day 2: Scale and skew](../week_01/day_2.html):** estimating load and the tail
    - 1 · Back-of-envelope estimation as a skill
    - 2 · Latency percentiles, defined
    - 3 · The tail at scale: fan-out
    - 4 · Hot keys
    - 5 · Little's law
    - Where PYMK uses it
- **[Day 3: The distributed graph](../week_01/day_3.html):** the graph store, precompute, incremental updates
    - The question
    - A graph store, as a published design describes it
    - First attempt: compute on request
    - The key idea: precompute as a self-join
    - Incremental updates: whose candidates change when u and v connect
    - Consistency: why the final check runs on every response
    - Where PYMK uses it

## Week 3: Tokenization

- **[Day 1: Text as data](../week_03/day_1.html):** the pre-tokenization pattern
    - Marks, and why GPT-2 cuts Hindi words
    - Digits
- **[Day 2: Greedy and the objective](../week_03/day_2.html):** choosing the vocabulary budget
- **[Day 3: Information](../week_03/day_3.html):** evaluating a tokenizer, with error bars
    - 1 · What to measure
    - 2 · Error bars: the question
    - 3 · The bootstrap, from first principles
    - 4 · Paired comparison of two tokenizers
- **[Day 5: Encoding and serving](../week_03/day_5.html):** training on terabytes, serving at scale
    - Training: what parallelizes and what does not
    - Where sketches and sampling fit
    - Serving a tokenizer
