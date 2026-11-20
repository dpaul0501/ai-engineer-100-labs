# System Design

Each week's design problem taken to production: estimates with stated assumptions, storage and sharding, caching, tail latency, and the serving architecture.

## Week 1: People You May Know

- **[Day 5: A billion users](../week_01/day_5.html):** 1 · estimate before you draw
    - The situation
    - The obvious attempt
    - The conclusion the numbers force
- **[Day 5: A billion users](../week_01/day_5.html):** 2 · batch precompute, online re-rank, and how stale is too stale
    - The situation
    - The obvious worry, measured: staleness
    - The trade-off
- **[Day 5: A billion users](../week_01/day_5.html):** 5 · incremental updates from the stream of new friendships
    - The situation
    - Work it by hand
    - Measured on the week's edge stream
    - Versioned keys and snapshots
- **[Day 5: A billion users](../week_01/day_5.html):** 6 · fan-out, tail latency, hedged requests and Little's law
    - The situation
    - The obvious answer, and why it is wrong
    - Hedged requests
    - Little's law: how many requests are in flight
- **[Day 5: A billion users](../week_01/day_5.html):** 8 · the architecture end to end
- **[Day 5: A billion users](../week_01/day_5.html):** 9 · rules on every response
    - The situation
    - Explaining a suggestion, and its privacy risk
    - Fatigue and notifications
    - Fair exposure
    - Cold start
- **[Day 5: A billion users](../week_01/day_5.html):** 10 · the same design in other products

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
