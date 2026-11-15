# ML

Statistics and core ML: each idea derived from first principles, checked by measuring it on the week's data, then tied back to the week's design problem.

## Week 1: People You May Know

- **[Day 1: Count it exactly](../week_01/day_1.html):** does a mutual friend predict a friendship?
    - 1 · More mutual friends, more likely friends?
    - 2 · Why it works: friendships close triangles
    - 3 · Why sorting by mutual friends is the right first rule
- **[Day 2: Popular people](../week_01/day_2.html):** most people have few friends, a few have very many
    - The obvious estimate: 20 × 20
    - Who has how many friends
    - Where the popular people come from: the rich get richer
    - Your friends have more friends than you
    - So what does one request cost?
- **[Day 2: Popular people](../week_01/day_2.html):** how slow is slow: percentiles and p99
    - The situation: one number for "fast enough"
    - Percentiles, in plain words
    - How sure is a p99 from a sample?
    - Practice: [295. Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/)
- **[Day 3: Read less](../week_01/day_3.html):** read some friends, and scale up
    - Try the obvious thing: read the first lists that fit
    - The idea: a random handful of friends, scaled up
    - Use it
    - When it is enough, and what to say in an interview
- **[Day 3: Read less](../week_01/day_3.html):** the yardstick: recall@10 against the exact answer
    - What "almost the same people" means
    - Ties need a rule
    - How much do we lose at each budget?
    - Skipping popular friends: a trade
- **[Day 4: Learn who connects](../week_01/day_4.html):** link prediction as a learning problem
    - 1 · Learn from the past: freeze the graph, see who connects next
    - 2 · Negatives, and why the choice biases you
    - 3 · Features: what makes a friend of a friend likely
    - 4 · Logistic regression: a weighted vote turned into a probability
    - 5 · How to judge it: AUC
    - 6 · Two ways to compute AUC: pooled, or within each user
    - 7 · What the user sees: recall@10, with error bars over users
    - 8 · Calibration: does a 2% prediction mean 2%?
    - 9 · Feedback loops: the model changes the data it learns from
- **[Day 5: A billion users](../week_01/day_5.html):** proving it helps: A/B tests
    - The situation
    - Try the obvious thing
    - The idea: randomize by user
    - How many users?
    - Two ways the result can mislead

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
