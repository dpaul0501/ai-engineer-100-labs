# AI

Every week is built around one design problem of the kind top companies ask. These are the problems, and the AI-specific skills each week checks.

## Week 1: People You May Know

**The problem:** [People You May Knowfrom two hops to a billion users](../week_01/index.html)

- **[Week reading](../week_01/index.html):** checkpoint
    - Explain why the raw count shows the same popular people to almost everyone (one user in 66% of all top-10 lists), and why learning from who actually connected can do better.
- **[Day 4: Learn who connects](../week_01/day_4.html):** checkpoint
    - Set up link prediction as a learning problem with two time cuts, say what counts as a positive and a miss, and explain why a random edge split inflated recall 2.7×.
    - Explain how a live recommender's feedback loop creates exposure bias, using the measured hub exposure, and how exploration with inverse propensity weighting corrects it.
- **[Day 5: A billion users](../week_01/day_5.html):** checkpoint
    - Explain training–serving skew and point-in-time features, why the impression log is needed to learn from behaviour without a feedback loop, and how learned user embeddings would replace hand-made features.
- **[Worksheet and learning checks](../week_01/worksheet.html):** checkpoint
    - 10. Why must the ranker be tested on a time split rather than a random one, and how can its own suggestions mislead the next model you train?

## Week 3: Tokenization

**The problem:** [Byte pair encoding, from first principles](../week_03/index.html)

- **[Week reading](../week_03/index.html):** checkpoint
    - Explain to a friend why encoding uses merge order and not frequency, using the abaa example.
- **[Day 1: Text as data](../week_03/day_1.html):** checkpoint
    - Write the Hindi-safe pattern, and explain the 90-vs-22 gap partly in terms of it.
- **[Day 3: Information](../week_03/day_3.html):** checkpoint
    - Run the paired document bootstrap for BPE 1,000 against 2,000 and explain why tokens are the wrong unit.
    - Write the one-page tokenizer evaluation plan, with paired intervals.
- **[Day 5: Encoding and serving](../week_03/day_5.html):** checkpoint
    - Explain the mechanism of three tokenizer-caused failures (for example token tax, glitch tokens, streaming �), one example each.
- **[Worksheet and learning checks](../week_03/worksheet.html):** checkpoint
    - WI-7 The token tax, with error bars
    - WI-8 Stretch: match tiktoken
    - Why does encoding replay merges by rank instead of using frequencies or longest match? (Reading, Day 5)
    - Why does GPT-2 cut most Hindi words in two, and what fixes it? (Day 1)
