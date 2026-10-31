# DSA

Every LeetCode pattern, each placed in the week whose project uses it. Each problem: try it first, code it yourself, solve 1–2 variations, and write tests and corner cases.

## Week 1 · Tokens and Decoding

**[Hashing, heaps, tries, stacks and automata, sampling](../weeks/week_01.md#dsa-hashing-heaps-tries-stacks-and-automata-sampling)**

Study sources:

- [NeetCode roadmap](https://neetcode.io/roadmap): problems grouped by pattern, each with a video.
- [take U forward](https://www.youtube.com/@takeUforward) (Striver) on YouTube, for a second explanation.
- [Hashing](https://mldsa.github.io/docs/part1/chapter01-hashing/) and [Top-K](https://mldsa.github.io/docs/part1/chapter02-topk/) in *From LeetCode to Learning Systems*.

| # | Problem | Pattern | Where it is in `tok` |
|---|---|---|---|
| 1 | [Two Sum](https://leetcode.com/problems/two-sum/) (1) | Hash map | Pair counts |
| 2 | [Group Anagrams](https://leetcode.com/problems/group-anagrams/) (49) | Canonical key | The mask cache keys on a hashable state |
| 3 | [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) (347) | Count + heap | BPE's best pair; top-k sampling |
| 4 | [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) (215) | Heap of size k / quickselect | `top_k_filter` in O(V log k) |
| 5 | [Find K Pairs with Smallest Sums](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/) (373) | Heap over candidate frontiers | Beam search |
| 6 | [Implement Trie](https://leetcode.com/problems/implement-trie-prefix-tree/) (208) | Trie | `TokenTrie` |
| 7 | [Design Add and Search Words](https://leetcode.com/problems/design-add-and-search-words-data-structure/) (211) | Trie + DFS | Walking the trie with a state |
| 8 | ★ [Word Search II](https://leetcode.com/problems/word-search-ii/) (212) | Trie + pruned DFS | Pruning a subtree on the first invalid byte |
| 9 | [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) (20) | Stack | The automaton's stack of open `{` and `[` |
| 10 | [Decode String](https://leetcode.com/problems/decode-string/) (394) | Stack of contexts | Nested objects and arrays |
| 11 | ★ [Valid Number](https://leetcode.com/problems/valid-number/) (65) | Finite automaton | The number DFA inside the grammar |
| 12 | [Random Pick with Weight](https://leetcode.com/problems/random-pick-with-weight/) (528) | Prefix sums + binary search | `categorical` |
| 13 | ★ [Linked List Random Node](https://leetcode.com/problems/linked-list-random-node/) (382) | Reservoir sampling | The held-out split |
