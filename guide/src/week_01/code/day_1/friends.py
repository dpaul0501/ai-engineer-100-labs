# Load the week's friend lists, and the six-person running example.
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

# The running example: You (0), Ben (1), Chloe (2), Dev (3), Esha (4), Farid (5).
NAMES = ["You", "Ben", "Chloe", "Dev", "Esha", "Farid"]
EXAMPLE = {
    0: {1, 2},          # You: Ben, Chloe
    1: {0, 2, 3, 4},    # Ben: You, Chloe, Dev, Esha
    2: {0, 1, 4, 5},    # Chloe: You, Ben, Esha, Farid
    3: {1},             # Dev: Ben
    4: {1, 2},          # Esha: Ben, Chloe
    5: {2},             # Farid: Chloe
}

def load_friends(path=DATA / "edges.csv"):
    """friends[u] = set of u's friends, from the u,v,t rows (each friendship once)."""
    friends = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            u, v = int(row["u"]), int(row["v"])
            friends.setdefault(u, set()).add(v)
            friends.setdefault(v, set()).add(u)
    return friends

if __name__ == "__main__":
    fr = load_friends()
    sizes = sorted(len(s) for s in fr.values())
    assert len(fr) == 10_000 and sum(sizes) == 200_000
    print("users", len(fr), "list entries", sum(sizes))
    print("mean list", sum(sizes) / len(sizes), "median", sizes[len(sizes) // 2], "largest", sizes[-1])
    print("five largest", sizes[-5:])
