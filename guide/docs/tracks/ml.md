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
- **[Day 4: Approximation and candidates](../week_01/day_4.html):** sampling estimators and recall against the exact answer
    - 1 · The question
    - 2 · First attempt: read the first lists that fit
    - 3 · The key idea, derived: a uniform sample of friends, scaled up
    - 4 · Why it is correct: unbiasedness and the variance, proved
    - 5 · The budgeted version, and its cost
    - 6 · The fidelity metric: recall@10 against the exact answer
    - 7 · Hub capping as a bias–variance trade-off
    - 8 · Confirm by measuring
    - 9 · Where PYMK uses it
- **[Day 5: Ranking with ML](../week_01/day_5.html):** link prediction, from first principles
    - 1 · The question: predicting friendships that do not exist yet
    - 2 · The key idea: two time cuts, and a precise population
    - 3 · Negatives, and their bias
    - 4 · Features: four ways to score a mutual friend
    - 5 · Why a mutual friend with many friends is weak evidence
    - 6 · The other features, and one that hurts
    - 7 · Logistic regression, derived
    - 8 · Evaluation 1: AUC is the Mann–Whitney statistic
    - 9 · Evaluation 2: what the user sees, recall@10, and error bars over users
    - 10 · The measured comparison
    - 11 · Calibration: is a 2% prediction really 2%?
    - 12 · Feedback loops and exposure bias
    - 13 · Privacy and fairness are constraints, not features

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
