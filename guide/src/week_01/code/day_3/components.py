# Islands in the graph: union-find (disjoint-set union), fed one friendship at a time.
from common import load_edges, SIX, N_USERS

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))       # everyone starts as their own island
        self.rank = [0] * n                # an upper bound on each tree's height
        self.count = n                     # number of islands

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:      # path compression: point everyone on the way at the root
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        """Join a's island and b's island. False if they were already one."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra                # union by rank: hang the shorter tree under the taller
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.count -= 1
        return True

uf = UnionFind(6)
for a, b in SIX:
    uf.union(a, b)
assert uf.count == 1 and len({uf.find(x) for x in range(6)}) == 1
uf = UnionFind(8)                          # the six people, plus two strangers who know each other
for a, b in SIX + [(6, 7)]:
    uf.union(a, b)
assert uf.count == 2 and uf.find(6) == uf.find(7) != uf.find(0)

# Merging duplicate accounts: two accounts are the same person if they share an email or phone.
def merge_accounts(accounts):
    """accounts[i] = set of contact strings. Returns groups of account ids that belong together."""
    uf, owner = UnionFind(len(accounts)), {}
    for i, contacts in enumerate(accounts):
        for c in contacts:
            if c in owner:
                uf.union(i, owner[c])      # shared contact: same person
            else:
                owner[c] = i
    groups = {}
    for i in range(len(accounts)):
        groups.setdefault(uf.find(i), []).append(i)
    return sorted(groups.values())

assert merge_accounts([{"a@x", "555-1"}, {"b@y"}, {"555-1", "c@z"}, {"c@z"}, {"d@w"}]) == [[0, 2, 3], [1], [4]]

# LeetCode 547 · Number of Provinces (adjacency matrix in)
def findCircleNum(isConnected):
    n = len(isConnected)
    uf = UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j]:
                uf.union(i, j)
    return uf.count

assert findCircleNum([[1, 1, 0], [1, 1, 0], [0, 0, 1]]) == 2
assert findCircleNum([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) == 3

# LeetCode 684 · Redundant Connection: the first edge whose ends are already joined
def findRedundantConnection(edges):
    uf = UnionFind(len(edges) + 1)
    for a, b in edges:
        if not uf.union(a, b):
            return [a, b]

assert findRedundantConnection([[1, 2], [1, 3], [2, 3]]) == [2, 3]
assert findRedundantConnection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]) == [1, 4]

if __name__ == "__main__":
    edges = load_edges()
    uf = UnionFind(N_USERS)
    seen = set()
    checkpoints = {1_000, 5_000, 10_000, 20_000, 50_000, 80_000, 100_000}
    print("friendships so far | islands (incl. users with no friend yet) | users with no friend yet | largest island")
    redundant = 0
    for t, (u, v, _) in enumerate(edges, 1):
        seen.update((u, v))
        redundant += not uf.union(u, v)
        if t in checkpoints:
            sizes = {}
            for x in range(N_USERS):
                r = uf.find(x); sizes[r] = sizes.get(r, 0) + 1
            print(t, "|", uf.count, "|", N_USERS - len(seen), "|", max(sizes.values()))
    print("friendships that joined two different islands", len(edges) - redundant,
          "; inside an island already (they close a cycle)", redundant)
