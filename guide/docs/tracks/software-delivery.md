# Software Delivery

Spec → contract → test → code, every week: function contracts, golden, property and differential tests, and the lab's acceptance tests.

## Week 1: People You May Know

- **[Day 4: Learn what engagement means](../week_01/day_4.html):** checkpoint
    - Design an A/B test: sticky hash, primary metric, guardrails, users per arm and MDE from the formula, the z-test by hand (z = 5.17), the p-value in plain words, and the ship rule; solve 470.
- **[Day 5: A billion users](../week_01/day_5.html):** checkpoint
    - Publish a batch as a version with one pointer flip and roll it back (LeetCode 981, 1146), and plan a rollout: shadow, ramp by sticky hash, guardrails, previous version one flip away.
- **[Worksheet and learning checks](../week_01/worksheet.html):** checkpoint
    - WI-1 Spec and failing tests
    - WI-7 Serving: the final filter and the cache
    - 13. Run the A/B test by hand: 853 of 4,689 control users and 1,050 of 4,668 treatment users converted. What is z, what does the p-value mean, and what can this test size not see? Why may you not stop on a peek, and why is the lift an underestimate?
    - 18. When u and v become friends, whose suggestions can change? Prove it. What does the cache store, and why does the eligibility filter still run on every response?

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
