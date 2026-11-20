# LeetCode 349, Intersection of Two Arrays: the distinct values present in both arrays.

def intersection(nums1, nums2):
    """Hash set: build a set from one array, probe it with the distinct values of the other.
    O(n + m) time, O(min(n, m)) extra space if we build the set from the shorter one."""
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    small = set(nums1)
    return [x for x in set(nums2) if x in small]

def intersection_sorted(nums1, nums2):
    """Follow-up "what if both are sorted?": two pointers, O(1) extra space besides the answer."""
    i = j = 0
    out = []
    while i < len(nums1) and j < len(nums2):
        if nums1[i] < nums2[j]:
            i += 1
        elif nums1[i] > nums2[j]:
            j += 1
        else:
            if not out or out[-1] != nums1[i]:   # skip repeats: each value once
                out.append(nums1[i])
            i += 1; j += 1
    return out

assert sorted(intersection([1, 2, 2, 1], [2, 2])) == [2]
assert sorted(intersection([4, 9, 5], [9, 4, 9, 8, 4])) == [4, 9]
assert intersection([1], [2]) == []
assert intersection_sorted([1, 1, 2, 2], [2, 2]) == [2]
assert intersection_sorted([4, 5, 9], [4, 4, 8, 9, 9]) == [4, 9]
import random
rng = random.Random(0)
for _ in range(2000):
    a = [rng.randrange(30) for _ in range(rng.randrange(20))]
    b = [rng.randrange(30) for _ in range(rng.randrange(20))]
    want = sorted(set(a) & set(b))
    assert sorted(intersection(a, b)) == want == intersection_sorted(sorted(a), sorted(b))
print("349: all tests passed")
