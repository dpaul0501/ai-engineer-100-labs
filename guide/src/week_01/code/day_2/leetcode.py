# Day 2 practice: 347, 215, 692, 973, 703, 295, 23, 373. Each solution is checked on the
# problem's examples and, where cheap, against a brute force.
import heapq
import random
from collections import Counter

from stream import KthLargest, MedianFinder          # 703 and 295 live with the stream code


def topKFrequent(nums, k):                           # 347: bucket by count, O(n)
    count = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]      # a count is at most n
    for x, c in count.items():
        buckets[c].append(x)
    out = []
    for c in range(len(nums), 0, -1):
        for x in buckets[c]:
            out.append(x)
            if len(out) == k:
                return out
    return out


def findKthLargest(nums, k, seed=0):                  # 215: quickselect, O(n) expected
    rng = random.Random(seed)
    while True:
        p = rng.choice(nums)
        hi = [x for x in nums if x > p]
        eq = sum(1 for x in nums if x == p)
        if k <= len(hi):
            nums = hi
        elif k <= len(hi) + eq:
            return p
        else:
            k -= len(hi) + eq
            nums = [x for x in nums if x < p]


def topKFrequentWords(words, k):                      # 692: ties broken alphabetically, O(n log k)
    count = Counter(words)
    return heapq.nsmallest(k, count, key=lambda w: (-count[w], w))


def kClosest(points, k):                              # 973: keep the k closest in a max-heap of size k
    heap = []
    for x, y in points:
        d = -(x * x + y * y)                          # negated: heapq is a min-heap
        if len(heap) < k:
            heapq.heappush(heap, (d, x, y))
        elif d > heap[0][0]:
            heapq.heapreplace(heap, (d, x, y))
    return [[x, y] for _, x, y in heap]


class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next


def mergeKLists(lists):                               # 23: heap of heads, O(N log k)
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    heapq.heapify(heap)
    dummy = tail = ListNode()
    while heap:
        _, i, node = heapq.heappop(heap)              # i breaks ties: nodes are not comparable
        tail.next = tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next


def kSmallestPairs(nums1, nums2, k):                  # 373: a merge of lists that are never built
    if not nums1 or not nums2:
        return []
    heap = [(nums1[i] + nums2[0], i, 0) for i in range(min(k, len(nums1)))]
    heapq.heapify(heap)
    out = []
    while heap and len(out) < k:
        _, i, j = heapq.heappop(heap)
        out.append([nums1[i], nums2[j]])
        if j + 1 < len(nums2):
            heapq.heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))
    return out


def linked(xs):
    head = None
    for x in reversed(xs):
        head = ListNode(x, head)
    return head


def unlinked(node):
    out = []
    while node:
        out.append(node.val); node = node.next
    return out


assert sorted(topKFrequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2] and topKFrequent([1], 1) == [1]
assert findKthLargest([3, 2, 1, 5, 6, 4], 2) == 5 and findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
assert topKFrequentWords(["i", "love", "leetcode", "i", "love", "coding"], 2) == ["i", "love"]
assert topKFrequentWords(["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4) == \
    ["the", "is", "sunny", "day"]
assert kClosest([[1, 3], [-2, 2]], 1) == [[-2, 2]]
assert sorted(kClosest([[3, 3], [5, -1], [-2, 4]], 2)) == [[-2, 4], [3, 3]]
kl = KthLargest(3, [4, 5, 8, 2])
assert [kl.add(x) for x in [3, 5, 10, 9, 4]] == [4, 5, 5, 8, 8]
mf = MedianFinder(); mf.addNum(1); mf.addNum(2)
assert mf.findMedian() == 1.5
mf.addNum(3)
assert mf.findMedian() == 2.0
assert unlinked(mergeKLists([linked([1, 4, 5]), linked([1, 3, 4]), linked([2, 6])])) == [1, 1, 2, 3, 4, 4, 5, 6]
assert mergeKLists([]) is None and mergeKLists([None]) is None
assert kSmallestPairs([1, 7, 11], [2, 4, 6], 3) == [[1, 2], [1, 4], [1, 6]]
assert kSmallestPairs([1, 1, 2], [1, 2, 3], 2) == [[1, 1], [1, 1]]

rng = random.Random(0)
for _ in range(300):
    nums = [rng.randint(-20, 20) for _ in range(rng.randint(1, 40))]
    k = rng.randint(1, len(nums))
    assert findKthLargest(nums, k) == sorted(nums, reverse=True)[k - 1]
    a = sorted(rng.randint(0, 30) for _ in range(rng.randint(1, 8)))
    b = sorted(rng.randint(0, 30) for _ in range(rng.randint(1, 8)))
    sums = sorted(x + y for x in a for y in b)[:k]
    assert [x + y for x, y in kSmallestPairs(a, b, k)] == sums

if __name__ == "__main__":
    print("347, 215, 692, 973, 703, 295, 23, 373: examples and random checks pass")
