# DSA

Algorithms and data structures taught as subjects: each one posed as a question, derived, proved, costed, then practised on LeetCode problems and variations, in the week whose design problem needs it.

## Week 1: People You May Know

- **[Day 5: A billion users](../week_01/day_5.html):** 3 · sharding by user id: mod N, consistent hashing, hot keys
    - The situation
    - The obvious attempt: hash mod N
    - The idea: consistent hashing
    - Hot keys: hub users
- **[Day 5: A billion users](../week_01/day_5.html):** 4 · an LRU cache for hot users' suggestions
    - The situation
    - The idea: least recently used
    - Measured: hit rate on a skewed request stream
- **[Day 5: A billion users](../week_01/day_5.html):** 11 · practice
    - Practice: [146. LRU Cache](https://leetcode.com/problems/lru-cache/) · [460. LFU Cache](https://leetcode.com/problems/lfu-cache/) · [981. Time Based Key-Value Store](https://leetcode.com/problems/time-based-key-value-store/) · [1146. Snapshot Array](https://leetcode.com/problems/snapshot-array/) · [380. Insert Delete GetRandom O(1)](https://leetcode.com/problems/insert-delete-getrandom-o1/) · [355. Design Twitter](https://leetcode.com/problems/design-twitter/)

## Week 3: Tokenization

- **[Day 1: Text as data](../week_03/day_1.html):** counting and hashing, top-k, sliding windows, UTF-8
    - 1. Counting with a hash map
    - 2. Top-k: the k largest counts
    - 3. Fixed-size sliding windows
    - 4. UTF-8: a variable-length prefix code
    - Practice: [692 Top K Frequent Words](https://leetcode.com/problems/top-k-frequent-words/) · [643 Maximum Average Subarray I](https://leetcode.com/problems/maximum-average-subarray-i/) · [187 Repeated DNA Sequences](https://leetcode.com/problems/repeated-dna-sequences/) · [393 UTF-8 Validation](https://leetcode.com/problems/utf-8-validation/) · [347 Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) · [451 Sort Characters By Frequency](https://leetcode.com/problems/sort-characters-by-frequency/) · [215 Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) · [1456 Maximum Number of Vowels in a Substring of Given Length](https://leetcode.com/problems/maximum-number-of-vowels-in-a-substring-of-given-length/)
- **[Day 2: Greedy and the objective](../week_03/day_2.html):** greedy, in full
    - 1 · The question: BPE's objective, and its greedy rule
    - 2 · What a greedy algorithm is
    - 3 · The two properties, and why you need both
    - 4 · Proof technique 1: the exchange argument, on interval scheduling
    - 5 · Proof technique 2: greedy stays ahead
    - 6 · Fractional knapsack works; 0/1 knapsack does not
    - 7 · Matroids: the structures where greedy always works
    - 8 · When greedy fails
    - 9 · When greedy fails, (a): exact answers by dynamic programming
    - 10 · When greedy fails, (b): approximation algorithms
    - 11 · When greedy fails, (c): why BPE uses greedy anyway
    - Practice: [435 Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) · [452 Minimum Number of Arrows to Burst Balloons](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/) · [55 Jump Game](https://leetcode.com/problems/jump-game/) · [45 Jump Game II](https://leetcode.com/problems/jump-game-ii/) · [322](https://leetcode.com/problems/coin-change/) · [139](https://leetcode.com/problems/word-break/) · [455 Assign Cookies](https://leetcode.com/problems/assign-cookies/) · [646 Maximum Length of Pair Chain](https://leetcode.com/problems/maximum-length-of-pair-chain/) · [1584 Min Cost to Connect All Points](https://leetcode.com/problems/min-cost-to-connect-all-points/)
- **[Day 3: Information](../week_03/day_3.html):** optimal prefix codes
    - 1 · Prefix codes: decoding without separators
    - 2 · The Kraft inequality: short codewords are scarce
    - 3 · Both halves of the source coding theorem
    - 4 · Huffman's algorithm
    - 5 · Why Huffman is optimal
    - 6 · Cost
    - 7 · Confirm by measuring
    - 8 · Where BPE uses it, and where BPE differs
    - Practice: [1046 Last Stone Weight](https://leetcode.com/problems/last-stone-weight/) · [1167 Minimum Cost to Connect Sticks](https://leetcode.com/problems/minimum-cost-to-connect-sticks/)
- **[Day 4: Fast training](../week_03/day_4.html):** the maximum of a changing set
    - 1 · The question
    - First attempts
    - 2 · The binary heap, from first principles
    - 3 · Changing priorities: four designs
    - 4 · The inverted index: visit only what changes
    - 5 · Putting it together: the fast trainer
    - 6 · The same pattern in other problems
    - Practice: [703](https://leetcode.com/problems/kth-largest-element-in-a-stream/) · [295](https://leetcode.com/problems/find-median-from-data-stream/) · [239](https://leetcode.com/problems/sliding-window-maximum/) · [2034](https://leetcode.com/problems/stock-price-fluctuation/) · [1845](https://leetcode.com/problems/seat-reservation-manager/) · [692 Top K Frequent Words](https://leetcode.com/problems/top-k-frequent-words/) · [23 Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) · [480 Sliding Window Median](https://leetcode.com/problems/sliding-window-median/) · [432 All O`one Data Structure](https://leetcode.com/problems/all-oone-data-structure/) · [355 Design Twitter](https://leetcode.com/problems/design-twitter/)
- **[Day 5: Encoding and serving](../week_03/day_5.html):** the fast encoder and the LRU cache
    - The question
    - First attempt: replay the merges, O(L · R)
    - The key idea: a linked list to splice, a heap to choose
    - Worked example
    - Why it gives the same output as the simple encoder
    - Cost
    - Confirm by measuring
    - The LRU cache (146)
    - Practice: [146 LRU Cache](https://leetcode.com/problems/lru-cache/) · [23 Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) · [460 LFU Cache](https://leetcode.com/problems/lfu-cache/)
- **[Day 5: Encoding and serving](../week_03/day_5.html):** streams and scale: counting what you cannot store
    - The question
    - (a) Majority vote: Boyer–Moore (169) and its n/3 version (229)
    - (b) Misra–Gries: the same cancellation with k − 1 counters
    - (c) Space-Saving: overestimate instead of underestimate
    - (d) Count-Min sketch: hashing, with a probabilistic bound
    - (e) Reservoir sampling: a uniform sample from a stream of unknown length
    - Confirm by measuring on Alice
    - Does an approximate top pair pick the same merge?
    - Where BPE uses it
    - Practice: [382 Linked List Random Node](https://leetcode.com/problems/linked-list-random-node/) · [398 Random Pick Index](https://leetcode.com/problems/random-pick-index/) · [169 Majority Element](https://leetcode.com/problems/majority-element/) · [229 Majority Element II](https://leetcode.com/problems/majority-element-ii/) · [528 Random Pick with Weight](https://leetcode.com/problems/random-pick-with-weight/)
