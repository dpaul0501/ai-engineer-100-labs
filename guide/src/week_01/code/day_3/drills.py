# Two graph-traversal drills: LeetCode 785 and 133.
from collections import deque

# LeetCode 785 · Is Graph Bipartite? Colour by BFS layer; an edge inside a layer breaks it.
def isBipartite(graph):
    colour = [-1] * len(graph)
    for s in range(len(graph)):              # the graph may have several islands
        if colour[s] != -1:
            continue
        colour[s] = 0
        queue = deque([s])
        while queue:
            x = queue.popleft()
            for y in graph[x]:
                if colour[y] == -1:
                    colour[y] = 1 - colour[x]
                    queue.append(y)
                elif colour[y] == colour[x]:
                    return False             # an odd cycle, for example a triangle
    return True

assert not isBipartite([[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]])
assert isBipartite([[1, 3], [0, 2], [1, 3], [0, 2]])
# the six people contain triangles, so they cannot be split into two sides
assert not isBipartite([[1, 2], [0, 2, 3, 4], [0, 1, 4, 5], [1], [1, 2], [2]])

# LeetCode 133 · Clone Graph: BFS with a map from old node to its copy (the "seen" set).
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def cloneGraph(node):
    if node is None:
        return None
    copy = {node: Node(node.val)}
    queue = deque([node])
    while queue:
        x = queue.popleft()
        for y in x.neighbors:
            if y not in copy:                # first sight: make the copy, visit later
                copy[y] = Node(y.val)
                queue.append(y)
            copy[x].neighbors.append(copy[y])
    return copy[node]

nodes = [Node(i) for i in range(1, 5)]
for i, nb in enumerate([[2, 4], [1, 3], [2, 4], [1, 3]]):
    nodes[i].neighbors = [nodes[j - 1] for j in nb]
c = cloneGraph(nodes[0])
assert c is not nodes[0] and [y.val for y in c.neighbors] == [2, 4]
assert c.neighbors[0].neighbors[0] is c      # the copy points at copies, never at the original
