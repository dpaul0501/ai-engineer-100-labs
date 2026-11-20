# AI

Every week is built around one design problem of the kind top companies ask. These are the problems, and the AI-specific skills each week checks.

## Week 1: People You May Know

**The problem:** [People You May Knowfrom two friend lists to a billion users](../week_01/index.html)

- **[Day 4: Learn what engagement means](../week_01/day_4.html):** checkpoint
    - Explain exposure bias with the simulation (−28% on the log, +31% in truth), derive why 1/π weighting is unbiased and why it is noisy, list the four defences, and solve 528, 382 and 398.
    - Explain why rankers drop raw ids, factorise the friendship matrix into user vectors, and say what they bought (+0.0238 for users with few friends, reach beyond two hops) and cost on the week's graph.
- **[Worksheet and learning checks](../week_01/worksheet.html):** checkpoint
    - 14. On the old ranker's impression log the new ranker looks 28% worse. On the truth it is 31% better. Explain, fix the evaluation, and name the defences.
    - 15. Why did the ranker never see a user id, and what does a learned vector per user buy and cost on the week's graph?

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
