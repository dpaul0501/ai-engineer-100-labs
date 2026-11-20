# Friends of friends as a two-step walk, and breadth-first search in general.
from collections import Counter, deque
import random
from common import load_edges, adjacency, six, YOU, BEN, CHLOE, DEV, ESHA, FARID

def friends_of_friends(adj, u):
    """Walk two steps from u. Count how many routes reach each person who is
    not u and not already u's friend: that count is the number of mutual friends."""
    count = Counter()
    for f in adj[u]:                 # step 1: a friend
        for v in adj[f]:             # step 2: a friend of that friend
            if v != u and v not in adj[u]:
                count[v] += 1
    return count

def bfs(adj, s, max_depth=None):
    """dist[v] = fewest steps from s to v, for everyone reachable (within max_depth)."""
    dist = {s: 0}
    queue = deque([s])
    while queue:
        x = queue.popleft()
        if max_depth is not None and dist[x] == max_depth:
            continue                 # at the limit: do not look further out
        for y in adj[x]:
            if y not in dist:        # mark on first sight, so y enters the queue once
                dist[y] = dist[x] + 1
                queue.append(y)
    return dist

# the six people
assert friends_of_friends(six, YOU) == {DEV: 1, ESHA: 2, FARID: 1}
d = bfs(six, YOU)
assert d == {YOU: 0, BEN: 1, CHLOE: 1, DEV: 2, ESHA: 2, FARID: 2}
assert {v for v, k in bfs(six, YOU, max_depth=2).items() if k == 2} == set(friends_of_friends(six, YOU))
assert bfs(six, DEV)[FARID] == 3     # Dev -> Ben -> Chloe -> Farid

# LeetCode 1971 · Find if Path Exists in Graph
def validPath(n, edges, source, destination):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b); adj[b].append(a)
    return destination in bfs(adj, source)

assert validPath(3, [[0, 1], [1, 2], [2, 0]], 0, 2)
assert not validPath(6, [[0, 1], [0, 2], [3, 5], [5, 4], [4, 3]], 0, 5)

# LeetCode 841 · Keys and Rooms: rooms[i] lists the rooms room i unlocks (arrows, not lines)
def canVisitAllRooms(rooms):
    return len(bfs(rooms, 0)) == len(rooms)

assert canVisitAllRooms([[1], [2], [3], []])
assert not canVisitAllRooms([[1, 3], [3, 0, 1], [2], [0]])

if __name__ == "__main__":
    G = adjacency(load_edges())
    rng = random.Random(0)
    starts = rng.sample(range(len(G)), 1000)
    within = Counter(); total_dist = 0; far = 0; reached_all = 0
    for s in starts:
        dist = bfs(G, s)
        reached_all += len(dist) == len(G)
        for k in dist.values():
            within[k] += 1
        total_dist += sum(dist.values()); far = max(far, max(dist.values()))
    print("starts", len(starts), "reached everyone from every start", reached_all == len(starts))
    cum = 0                                         # the start itself (distance 0) is not counted
    for k in sorted(within)[1:]:
        cum += within[k]
        print("within %d steps: mean %.0f other users, %.2f%% of the others" % (k, cum / 1000, 100 * cum / 1000 / (len(G) - 1)))
    print("mean distance to others %.2f, largest seen %d" % (total_dist / (1000 * (len(G) - 1)), far))
    # one typical (median-degree) user: friends of friends vs distance-2 ring
    u = 8604
    c = friends_of_friends(G, u)
    ring2 = [v for v, k in bfs(G, u, 2).items() if k == 2]
    assert set(c) == set(ring2)
    print("user", u, "friends", len(G[u]), "friends of friends", len(c), "routes walked", sum(len(G[f]) for f in G[u]))
    print("full BFS reads", sum(len(s) for s in G), "list entries")
