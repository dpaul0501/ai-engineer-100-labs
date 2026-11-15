# System Design

Each week's design problem taken to production: estimates with stated assumptions, storage and sharding, caching, tail latency, and the serving architecture.

## Week 1: People You May Know

- **[Day 3: Read less](../week_01/day_3.html):** several sources under one budget
    - The situation
    - Try the obvious thing: one source, best effort
    - The next idea: give each source a fixed share
    - Measure it: fixed shares against pooling
    - What may be approximate, and what must stay exact
    - The whole path
- **[Day 5: A billion users](../week_01/day_5.html):** how big is a billion users?
    - The situation
    - Try the obvious thing
    - The idea: estimate on paper, with every assumption labelled
- **[Day 5: A billion users](../week_01/day_5.html):** fast at the tail, fresh, and consistent enough
    - 1 · Fast: fan-out makes the slow machine everyone's problem
    - 2 · Hot keys
    - 3 · Little's law: how many requests are in flight
    - 4 · Fresh: precompute, or compute on request?
    - 5 · Incremental updates: when two people connect, whose suggestions change?
    - 6 · Consistent enough: why the final check runs on every response
- **[Day 5: A billion users](../week_01/day_5.html):** the product: rules people trust, goals traded off, the whole architecture
    - 1 · The rules people must be able to trust
    - 2 · The goals traded off against each other
    - 3 · The whole architecture, where every box answers a problem from the week
    - 4 · Training–serving skew, and point-in-time features
- **[Day 5: A billion users](../week_01/day_5.html):** how to walk an interviewer through it

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
