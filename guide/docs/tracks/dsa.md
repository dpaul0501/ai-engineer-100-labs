# DSA

100 problems grouped by pattern. Each one: study the pattern, code it yourself, create and solve 1–2 variations, and write tests and corner cases for the original.

## Week 1 · Lookups, Vectors, and Your First LLM Call

**[Arrays and hashing](../weeks/week_01.md#dsa-arrays-and-hashing)**

Study sources:

- [NeetCode](https://www.youtube.com/@NeetCode) on YouTube: search the problem name for a walkthrough. His [roadmap](https://neetcode.io/roadmap) groups problems by pattern.
- [take U forward](https://www.youtube.com/@takeUforward) (Striver) on YouTube, for a second explanation.
- [Hashing](https://mldsa.github.io/docs/part1/chapter01-hashing/) and [Top-K](https://mldsa.github.io/docs/part1/chapter02-topk/) in *From LeetCode to Learning Systems*.
- [TimeComplexity](https://wiki.python.org/moin/TimeComplexity) on the Python wiki, for what dict and set operations cost.

| Unit | Study |
|---|---|
| [1. Two Sum (LeetCode 1)](../weeks/week_01.md#1-two-sum-leetcode-1) | The complement-lookup idea, in the hashing chapter or a walkthrough. |
| [2. Contains Duplicate (LeetCode 217)](../weeks/week_01.md#2-contains-duplicate-leetcode-217) | Set membership, and what a set costs in memory. |
| [3. Valid Anagram (LeetCode 242)](../weeks/week_01.md#3-valid-anagram-leetcode-242) | Counting, then comparing counts. |
| [4. Group Anagrams (LeetCode 49)](../weeks/week_01.md#4-group-anagrams-leetcode-49) | A canonical key turns grouping into a lookup. |
| [5. Top K Frequent Elements (LeetCode 347)](../weeks/week_01.md#5-top-k-frequent-elements-leetcode-347) | The Top-K chapter: heap vs sort vs bucket sort. |
| [6. Product of Array Except Self (LeetCode 238)](../weeks/week_01.md#6-product-of-array-except-self-leetcode-238) | Prefix and suffix scans. |
| [7. Longest Consecutive Sequence (LeetCode 128)](../weeks/week_01.md#7-longest-consecutive-sequence-leetcode-128) | Start counting only where the predecessor is missing. |
| [8. Valid Sudoku (LeetCode 36)](../weeks/week_01.md#8-valid-sudoku-leetcode-36) | One set per constraint. |

## Week 2 · Pointers, Matrices, and Structured Output

**[Two pointers and sliding window](../weeks/week_02.md#dsa-two-pointers-and-sliding-window)**

Study sources:

- [NeetCode](https://www.youtube.com/@NeetCode) on YouTube: search the problem name for a walkthrough. His [roadmap](https://neetcode.io/roadmap) groups problems by pattern.
- [take U forward](https://www.youtube.com/@takeUforward) (Striver) on YouTube, for a second explanation.
- The [Algo Depth Track](https://mldsa.github.io/docs/track-algo-depth/) in *From LeetCode to Learning Systems*, for where two pointers sits among the foundation patterns.
- The [Sorting HOW TO](https://docs.python.org/3/howto/sorting.html) in the Python docs (stability and `key`), since two pointers usually starts from sorted input.
- [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque) in the Python docs, for which operations are O(1) at both ends.

| Unit | Study |
|---|---|
| [1. Valid Palindrome (LeetCode 125)](../weeks/week_02.md#1-valid-palindrome-leetcode-125) | One pointer at each end, moving inward. |
| [2. Two Sum II - Input Array Is Sorted (LeetCode 167)](../weeks/week_02.md#2-two-sum-ii-input-array-is-sorted-leetcode-167) | Compare with Week 1's dict. Two pointers use O(1) extra memory but need sorted input. |
| [3. 3Sum (LeetCode 15)](../weeks/week_02.md#3-3sum-leetcode-15) | Sort once, fix one element, and run two pointers on the rest. [Set types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset) explains why a tuple can go in a set and a list cannot. |
| [4. Container With Most Water (LeetCode 11)](../weeks/week_02.md#4-container-with-most-water-leetcode-11) | Start with the widest container and move the shorter wall. The trick is the proof. |
| [5. Longest Substring Without Repeating Characters (LeetCode 3)](../weeks/week_02.md#5-longest-substring-without-repeating-characters-leetcode-3) | The sliding window, and `Counter` and `defaultdict` in the [`collections` module](https://docs.python.org/3/library/collections.html). |
| [6. Minimum Window Substring (LeetCode 76)](../weeks/week_02.md#6-minimum-window-substring-leetcode-76) | A variable window that expands until valid, then shrinks. |
| [7. Sliding Window Maximum (LeetCode 239)](../weeks/week_02.md#7-sliding-window-maximum-leetcode-239) | The monotonic deque. |
