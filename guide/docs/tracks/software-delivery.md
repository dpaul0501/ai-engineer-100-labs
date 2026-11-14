# Software Delivery

Spec → contract → test → code, every week: function contracts, golden, property and differential tests, and the lab's acceptance tests.

## Week 1: People You May Know

- **[Week reading](../week_01/index.html):** checkpoint
    - Write and run the differential test: suggest against the masked row of A² on 100 random small graphs.
- **[Day 1: Graphs and counting](../week_01/day_1.html):** the contract and its tests
    - The question
    - First attempt
    - The key idea: a contract, then one test per kind of oracle
    - Why it works: plant bugs and see which tests fail
    - Cost
    - Confirm by measuring
    - Where PYMK uses it
- **[Day 1: Graphs and counting](../week_01/day_1.html):** checkpoint
    - Write the contract and the golden, property and differential tests for the exact baseline; catch all four planted bugs.
- **[Day 4: Approximation and candidates](../week_01/day_4.html):** the candidate-budget contract
    - The question
    - First attempt: one source, best effort
    - The key idea: a contract with before and after promises
    - What is approximate and what must stay exact
    - Confirm by measuring
    - Where PYMK uses it
- **[Day 5: Ranking with ML](../week_01/day_5.html):** the full architecture, and testing it on users
    - 1 · The question: what is the whole system?
    - 2 · Training–serving skew, and point-in-time features
    - 3 · Online experiments: A/B testing a new ranker
    - 4 · Week 2 teaser: from hand-made features to learned representations
- **[Worksheet and learning checks](../week_01/worksheet.html):** checkpoint
    - WI-1 Spec and failing tests
    - WI-7 Serving: the final filter and the cache
    - 12. Why does the eligibility filter run on every response, and why must the ranker be tested on a temporal split rather than a random one? (Days 3 and 5)

## Week 3: Tokenization

- **[Week reading](../week_03/index.html):** checkpoint
    - Train on alice.txt at vocab 1,000 and check decode(encode(x)) == x on every line.
- **[Day 4: Fast training](../week_03/day_4.html):** contracts and tests
    - The question
    - First attempt
    - The key idea: every test needs an oracle
    - Where BPE uses it
- **[Day 4: Fast training](../week_03/day_4.html):** checkpoint
    - Golden, property and differential tests; three planted bugs caught.
- **[Worksheet and learning checks](../week_03/worksheet.html):** checkpoint
    - WI-1 Spec and failing tests
    - WI-4 Encode, decode, save, load
    - Name four kinds of test for a tokenizer and the bug each catches. (Day 4)
