# ML

Statistics and core ML: each idea derived from first principles, checked by measuring it on the week's data, then tied back to the week's design problem.

## Week 1: People You May Know

- **[Day 1: Graphs and counting](../week_01/day_1.html):** triadic closure
    - 1 · Do friendships close triangles? The clustering coefficient
    - 2 · Does a mutual friend predict a future friendship?
    - 3 · Why ranking by mutual friends is a sensible first score
- **[Day 2: Scale and skew](../week_01/day_2.html):** heavy tails and the friendship paradox
    - 1 · The question
    - 2 · First attempt: plug in the average
    - 3 · The degree distribution, and why averages mislead
    - 4 · Where heavy tails come from: preferential attachment, derived
    - 5 · The friendship paradox, proved
    - 6 · Expected work per request
    - 7 · Where PYMK uses it
- **[Day 3: The distributed graph](../week_01/day_3.html):** measuring latency: percentiles and a confidence interval for p99
    - The question
    - First attempt: report the mean
    - Definitions: quantiles and order statistics
    - Why the estimator works, and how far off it can be
    - The bootstrap
    - Confirm by measuring
    - Where PYMK uses it
    - Practice: [295 · Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/)

## Week 3: Tokenization

- **[Day 1: Text as data](../week_03/day_1.html):** Zipf's law, fitting it, and Heaps' law
    - 1. How does frequency depend on rank?
    - 2. Fitting the exponent
    - 3. Heaps' law: does the vocabulary ever close?
- **[Day 2: Greedy and the objective](../week_03/day_2.html):** length vs learnability
    - The question
    - First attempt: let the objective choose
    - The key idea, derived: a vector learned from n occurrences has noise ∝ 1/√n
    - Vocabulary size as model selection
    - Confirm by measuring
    - Leakage: split before training the tokenizer
- **[Day 3: Information](../week_03/day_3.html):** information from first principles
    - 1 · Surprise: how much does one outcome tell you?
    - 2 · Entropy: the average surprise
    - 3 · Shannon's source coding theorem: entropy is the price of a lossless code
    - 4 · Cross-entropy: what a model's loss measures
    - 5 · Bits per byte: the number that survives a change of tokenizer
    - 6 · Estimating entropy from a sample
- **[Day 4: Fast training](../week_03/day_4.html):** sufficient statistics
    - The question
    - First attempt
    - Definitions
    - The claim and its proof
    - Cost
    - Confirm by measuring
    - Where BPE uses it
- **[Day 5: Encoding and serving](../week_03/day_5.html):** failure modes and their mechanisms
    - The question
    - The first principle behind most of them
    - The failure modes
    - BPE-dropout: making the model see more than one split
    - Other tokenizer families
