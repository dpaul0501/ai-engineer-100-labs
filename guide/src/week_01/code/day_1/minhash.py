# MinHash: a short signature per friend list whose agreements estimate the Jaccard overlap.
# LSH banding: find high-overlap pairs by bucketing signatures, without comparing all pairs.
import random
from collections import defaultdict

MASK = (1 << 64) - 1

def mix64(x):
    """splitmix64 finalizer: nearby ids get unrelated 64-bit values (stands in for a random order)."""
    x = (x + 0x9E3779B97F4A7C15) & MASK
    x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & MASK
    return x ^ (x >> 31)

def make_seeds(k, seed=0):
    rng = random.Random(seed)
    return [rng.getrandbits(64) for _ in range(k)]

def signature(friend_list, seeds):
    """For each of the k random orders, the friend that comes first (its hash value)."""
    return [min(mix64(x ^ s) for x in friend_list) for s in seeds]

def jaccard(a, b):
    """Shared friends / everyone either knows."""
    return len(a & b) / len(a | b)

def estimate_jaccard(sig_a, sig_b):
    return sum(x == y for x, y in zip(sig_a, sig_b)) / len(sig_a)

def estimate_mutual(j, len_a, len_b):
    """|A & B| from J: J = m / (|A| + |B| - m)  =>  m = J (|A| + |B|) / (1 + J)."""
    return j * (len_a + len_b) / (1 + j)

def lsh_candidates(sigs, r, b):
    """Cut each signature into b bands of r values. Two users are a candidate pair if they agree
    on a whole band. Returns (candidate pairs, pairs emitted by the buckets before de-duplication)."""
    pairs, emitted = set(), 0
    for band in range(b):
        buckets = defaultdict(list)
        for u, sig in sigs.items():
            buckets[tuple(sig[band * r:(band + 1) * r])].append(u)
        for members in buckets.values():
            emitted += len(members) * (len(members) - 1) // 2
            for i, x in enumerate(members):
                for y in members[i + 1:]:
                    pairs.add((min(x, y), max(x, y)))
    return pairs, emitted

def s_curve(j, r, b):
    """P(a pair with Jaccard j becomes a candidate) = 1 - (1 - j^r)^b."""
    return 1 - (1 - j ** r) ** b


if __name__ == "__main__":
    from friends import EXAMPLE
    assert jaccard(EXAMPLE[0], EXAMPLE[4]) == 1.0          # You and Esha: both {Ben, Chloe}
    assert jaccard(EXAMPLE[0], EXAMPLE[3]) == 0.5          # You {Ben, Chloe}, Dev {Ben}
    seeds = make_seeds(4000, seed=1)
    sy, sd, se = (signature(EXAMPLE[u], seeds) for u in (0, 3, 4))
    assert estimate_jaccard(sy, se) == 1.0                 # identical lists, identical signatures
    jd = estimate_jaccard(sy, sd)
    assert abs(jd - 0.5) < 3 * (0.25 / 4000) ** 0.5        # within 3 standard errors of 1/2
    print(f"You vs Dev, 4000 orders: estimate {jd:.3f} (true 0.5)")
    A, B = set(range(0, 60)), set(range(30, 90))           # J = 30 / 90 = 1/3
    est = estimate_jaccard(signature(A, seeds[:400]), signature(B, seeds[:400]))
    assert abs(est - 1 / 3) < 3 * ((1 / 3) * (2 / 3) / 400) ** 0.5
    assert abs(estimate_mutual(1 / 3, 60, 60) - 30) < 1e-9
    print(f"ids 0-59 vs 30-89, 400 orders: estimate {est:.3f} (true 0.333)")
    sigs = {u: signature(EXAMPLE[u], seeds[:20]) for u in EXAMPLE}
    pairs, _ = lsh_candidates(sigs, r=4, b=5)
    assert (0, 4) in pairs                                 # identical lists always collide
    assert abs(s_curve(0.1, 2, 50) - (1 - 0.99 ** 50)) < 1e-12
    print("S-curve r=2 b=50:", ", ".join(f"J={j}: {s_curve(j, 2, 50):.3f}" for j in (0.02, 0.05, 0.1, 0.15, 0.2, 0.3)))
    print("tests passed")
