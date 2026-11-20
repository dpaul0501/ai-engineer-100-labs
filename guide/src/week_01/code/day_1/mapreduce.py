# Mutual-friend counts for ALL pairs as a MapReduce-style job, simulated in one process.
# Map: each user's friend list -> every pair of those friends, with a 1 ("u is a mutual friend of x and y").
# Shuffle: route each pair to the reducer that owns it (hash of the pair).
# Reduce: add up the 1s per pair = the number of mutual friends.
from itertools import combinations

def map_user(u, friend_list):
    for x, y in combinations(sorted(friend_list), 2):
        yield (x, y), 1

def shuffle(records, reducers):
    parts = [{} for _ in range(reducers)]
    for key, val in records:
        parts[hash(key) % reducers].setdefault(key, []).append(val)
    return parts

def reduce_sum(part):
    return {key: sum(vals) for key, vals in part.items()}

def run_job(friends, reducers=4, mapper=map_user):
    emitted = []
    for u, fl in friends.items():
        emitted.extend(mapper(u, fl))
    out = {}
    for part in shuffle(emitted, reducers):
        out.update(reduce_sum(part))
    return out, len(emitted)

if __name__ == "__main__":
    from friends import EXAMPLE, NAMES
    counts, emitted = run_job(EXAMPLE)
    assert counts[(0, 4)] == 2                      # You and Esha: Ben and Chloe
    assert counts[(0, 3)] == 1 and counts[(0, 5)] == 1
    assert counts[(1, 2)] == 2                      # Ben and Chloe (already friends) share You, Esha
    assert emitted == sum(len(f) * (len(f) - 1) // 2 for f in EXAMPLE.values()) == 14
    for u, fl in EXAMPLE.items():
        print(f"map {NAMES[u]:5s} -> {[tuple(NAMES[i] for i in k) for k, _ in map_user(u, fl)]}")
    print("emitted", emitted, "distinct pairs", len(counts))
    show = {tuple(NAMES[i] for i in k): c for k, c in sorted(counts.items())
            if k[1] not in EXAMPLE[k[0]]}
    print("pairs not yet friends:", show)
