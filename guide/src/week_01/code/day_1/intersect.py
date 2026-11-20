# Mutual friends of one pair = the intersection of two friend lists, five ways.
# Each function returns (common ids in increasing order, operations used),
# so the measurements can count work as well as time it.

def intersect_nested(a, b):
    """Any two lists. Compare every x in a with the members of b: up to |a|*|b| comparisons."""
    out, ops = [], 0
    for x in a:
        for y in b:
            ops += 1
            if x == y:
                out.append(x)
                break                      # ids are distinct: x cannot match again
    return sorted(out), ops

def intersect_hash(a, b_set):
    """a: any list; b_set: the other list, already a hash set. One lookup per x in a.
    Call it with the SHORTER list as a."""
    out = [x for x in a if x in b_set]
    return sorted(out), len(a)

def intersect_merge(a, b):
    """a, b sorted, no repeats. Two pointers; each step moves at least one: <= |a| + |b| steps."""
    i = j = ops = 0
    out = []
    while i < len(a) and j < len(b):
        ops += 1
        if a[i] < b[j]:
            i += 1                         # a[i] is below everything left in b: not shared
        elif a[i] > b[j]:
            j += 1
        else:
            out.append(a[i]); i += 1; j += 1
    return out, ops

def lower_bound(b, x, lo, hi):
    """Smallest i in [lo, hi) with b[i] >= x (hi if none), and the comparisons used."""
    ops = 0
    while lo < hi:
        mid = (lo + hi) // 2
        ops += 1
        if b[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo, ops

def intersect_binary(a, b):
    """a short and sorted, b long and sorted. Binary-search each x of a in all of b:
    about |a| * log2|b| comparisons."""
    out, ops = [], 0
    for x in a:
        i, c = lower_bound(b, x, 0, len(b))
        ops += c + 1
        if i < len(b) and b[i] == x:
            out.append(x)
    return out, ops

def intersect_gallop(a, b):
    """a short and sorted, b long and sorted. From where the last search stopped, leap
    1, 2, 4, 8 ... places until past x, then binary-search that last leap:
    about |a| * log2(|b| / |a|) comparisons."""
    out, ops, j = [], 0, 0
    for x in a:
        lo, step = j, 1
        hi = j
        while hi < len(b):
            ops += 1
            if b[hi] >= x:
                break
            lo = hi + 1                    # b[hi] < x: the answer lies beyond hi
            hi += step
            step *= 2
        j, c = lower_bound(b, x, lo, min(hi, len(b)))
        ops += c + 1
        if j == len(b):
            break                          # everything left in a is bigger than all of b
        if b[j] == x:
            out.append(x); j += 1
    return out, ops

def to_bits(ids):
    """A friend list as one big integer: bit x is 1 when x is a friend."""
    bits = 0
    for x in ids:
        bits |= 1 << x
    return bits

def intersect_bits(a_bits, b_bits, n):
    """Ids 0..n-1. AND the two bitsets, then count the 1s (popcount): n/64 machine words."""
    both = a_bits & b_bits
    out = [x for x in range(n) if both >> x & 1] if both else []
    return out, (n + 63) // 64

def count_bits(a_bits, b_bits):
    """Only the number of mutual friends: AND, then popcount."""
    return (a_bits & b_bits).bit_count()


if __name__ == "__main__":
    import random
    from friends import EXAMPLE, NAMES
    you, esha = sorted(EXAMPLE[0]), sorted(EXAMPLE[4])
    for got in (intersect_nested(you, esha), intersect_hash(you, EXAMPLE[4]),
                intersect_merge(you, esha), intersect_binary(you, esha),
                intersect_gallop(you, esha), intersect_bits(to_bits(you), to_bits(esha), 6)):
        assert got[0] == [1, 2]                         # Ben and Chloe
    assert count_bits(to_bits(EXAMPLE[0]), to_bits(EXAMPLE[1])) == 1   # You and Ben share Chloe
    print("You and Esha share", [NAMES[x] for x in intersect_merge(you, esha)[0]])

    A = [3, 9, 14, 20]
    B = [1, 3, 4, 7, 9, 12, 15, 20, 22, 30]
    for f in (intersect_nested, intersect_merge, intersect_binary, intersect_gallop):
        print(f"{f.__name__:18s} common={f(A, B)[0]} ops={f(A, B)[1]}")
    print(f"{'intersect_hash':18s} ops={intersect_hash(A, set(B))[1]}")

    rng = random.Random(1)                              # random tests against Python's own sets
    for _ in range(3000):
        n = rng.choice([8, 64, 200, 5000])
        a = sorted(rng.sample(range(n), rng.randint(0, min(n, 40))))
        b = sorted(rng.sample(range(n), rng.randint(0, min(n, 400))))
        want = sorted(set(a) & set(b))
        s, l = (a, b) if len(a) <= len(b) else (b, a)
        assert intersect_nested(a, b)[0] == want
        assert intersect_hash(s, set(l))[0] == want
        assert intersect_merge(a, b)[0] == want and intersect_merge(a, b)[1] <= len(a) + len(b)
        assert intersect_binary(s, l)[0] == want
        assert intersect_gallop(s, l)[0] == want
        assert intersect_bits(to_bits(a), to_bits(b), n)[0] == want
        assert count_bits(to_bits(a), to_bits(b)) == len(want)
    print("3000 random tests passed")
