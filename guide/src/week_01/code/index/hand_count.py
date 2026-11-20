# The hand count from "The problem", as code: six people, friend lists in, suggestions out.
NAMES = ["You", "Ben", "Chloe", "Dev", "Esha", "Farid"]
friends = {
    0: {1, 2},          # You: Ben, Chloe
    1: {0, 2, 3, 4},    # Ben: You, Chloe, Dev, Esha
    2: {0, 1, 4, 5},    # Chloe: You, Ben, Esha, Farid
    3: {1},             # Dev: Ben
    4: {1, 2},          # Esha: Ben, Chloe
    5: {2},             # Farid: Chloe
}

def mutual_friends(friends, u):
    """For everyone who is not u and not already u's friend,
    count the overlap of their friend list with u's."""
    counts = {}
    for v in friends:
        if v == u or v in friends[u]:
            continue                      # never suggest yourself or a friend
        shared = friends[u] & friends[v]  # the friends you have in common
        if shared:
            counts[v] = len(shared)
    return counts

def suggest(friends, u, k=10):
    """The k people with the most mutual friends; ties go to the smaller id."""
    counts = mutual_friends(friends, u)
    return sorted(counts, key=lambda v: (-counts[v], v))[:k]

# every friendship is written in both lists
assert all(u in friends[v] for u in friends for v in friends[u])
assert mutual_friends(friends, 0) == {3: 1, 4: 2, 5: 1}   # Dev 1, Esha 2, Farid 1
assert suggest(friends, 0) == [4, 3, 5]                    # Esha, then Dev before Farid
assert suggest(friends, 0, k=2) == [4, 3]

if __name__ == "__main__":
    c = mutual_friends(friends, 0)
    for v in suggest(friends, 0):
        print(NAMES[v], c[v], sorted(NAMES[f] for f in friends[0] & friends[v]))
    # scale arithmetic shown on the page (hypothetical inputs)
    users, per = 10**9, 300
    print("friendships", users * per // 2)
    print("list entries", users * per)
    print("bytes at 8 per id", users * per * 8)
    print("entries read per request", per * per)
    print("people scanned if compared with everyone", users - 1)
    print("ratio", (users - 1) // (per * per))
