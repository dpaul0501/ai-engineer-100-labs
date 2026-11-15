# Software Delivery

Spec → contract → test → code, every week: function contracts, golden, property and differential tests, and the lab's acceptance tests.

## Week 1: People You May Know

- **[Week reading](../week_01/index.html):** checkpoint
    - Write and run the test that checks suggest against the masked row of \(A^2\) on 100 random small graphs.
- **[Day 1: Count it exactly](../week_01/day_1.html):** the contract and its tests
    - The situation
    - The obvious thing
    - The idea: write down the promises, then test each one
    - Three kinds of test, three kinds of oracle
    - Do the tests work? Plant bugs and see
- **[Day 1: Count it exactly](../week_01/day_1.html):** checkpoint
    - Write the contract of suggest and its golden, property and differential tests, and show which tests catch each of the four planted bugs.
- **[Day 3: Read less](../week_01/day_3.html):** the candidate contract and its tests
- **[Day 3: Read less](../week_01/day_3.html):** checkpoint
    - Write the candidate contract and turn each of its rows into a test.
- **[Worksheet and learning checks](../week_01/worksheet.html):** checkpoint
    - WI-1 Spec and failing tests
    - WI-7 Serving: the final filter and the cache
    - 13. When u and v become friends, whose suggestions can change? Prove it. And why does the eligibility filter still run on every response?

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
