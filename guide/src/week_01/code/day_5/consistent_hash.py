"""Day 5 · sharding by user id: hash mod N, a consistent-hash ring with virtual nodes,
and hot keys with replication. Measured on the week's 10,000 users."""
import bisect
import math
import statistics
from common import load_edges, build_adj

MASK = (1 << 64) - 1


def h64(x):
    """splitmix64: a fast, well-mixed 64-bit hash of a non-negative integer."""
    z = (x + 0x9E3779B97F4A7C15) & MASK
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return z ^ (z >> 31)


def mod_shard(key, n):
    return h64(key) % n


class Ring:
    """Consistent hashing: each server owns v points; a key belongs to the next point clockwise."""
    def __init__(self, servers, v=100, salt=0):
        self.v, self.salt = v, salt
        self.points = []                                  # sorted (position, server)
        for s in servers:
            self.add(s)

    def _positions(self, s):
        base = h64(s ^ (self.salt << 32) ^ 0x632BE59BD9B4E019)   # never hash a server like a key
        return [h64((base + i) & MASK) for i in range(self.v)]

    def add(self, s):
        for p in self._positions(s):
            bisect.insort(self.points, (p, s))

    def remove(self, s):
        self.points = [(p, t) for p, t in self.points if t != s]

    def lookup(self, key):
        i = bisect.bisect_left(self.points, (h64(key), -1))
        return self.points[i % len(self.points)][1]       # wrap past the end

    def replicas(self, key, r):
        """The first r distinct servers clockwise: where copies of a hot key live."""
        i = bisect.bisect_left(self.points, (h64(key), -1))
        out = []
        while len(out) < r:
            s = self.points[i % len(self.points)][1]
            if s not in out:
                out.append(s)
            i += 1
        return out

    def arc_shares(self):
        share = {}
        pts = self.points
        for j, (p, s) in enumerate(pts):
            prev = pts[j - 1][0] if j else pts[-1][0] - (1 << 64)
            share[s] = share.get(s, 0) + (p - prev) / (1 << 64)
        return share


def moved(keys, before, after):
    return [k for k in keys if before(k) != after(k)]


def tests():
    keys = range(10_000)
    ring = Ring(range(4), v=50)
    old = {k: ring.lookup(k) for k in keys}
    ring.add(4)
    assert all(ring.lookup(k) in (old[k], 4) for k in keys)   # every mover goes to the new server
    ring.remove(4)
    assert all(ring.lookup(k) == old[k] for k in keys)        # removing it restores everything
    assert abs(sum(ring.arc_shares().values()) - 1) < 1e-9
    assert len(set(ring.replicas(7, 3))) == 3 and ring.replicas(7, 3)[0] == ring.lookup(7)
    assert not {h64(k) for k in keys} & {p for p, _ in ring.points}   # no key sits on a point


if __name__ == "__main__":
    tests()
    adj = build_adj(load_edges())
    users = range(len(adj))
    n = len(adj)

    print("mod N: share of users moved")
    for a, b in [(16, 17), (64, 65), (16, 32)]:
        m = len(moved(users, lambda k: mod_shard(k, a), lambda k: mod_shard(k, b)))
        pred = a / (a + 1) if b == a + 1 else 1 - a / b
        print(f"  {a} -> {b}: {m / n:.4f}   (predicted {pred:.4f})")
    cnt = [0] * 16
    for k in users:
        cnt[mod_shard(k, 16)] += 1
    print(f"  mod 16 balance: fullest / mean = {max(cnt) / (n / 16):.2f}")

    ring = Ring(range(16), v=100)
    before = {k: ring.lookup(k) for k in users}
    ring.add(16)
    mv = [k for k in users if ring.lookup(k) != before[k]]
    assert all(ring.lookup(k) == 16 for k in mv)
    print(f"ring v=100, 16 -> 17: moved {len(mv) / n:.4f}, all to the new server (ideal 1/17 = {1 / 17:.4f})")

    print("balance vs virtual nodes, 16 servers, averaged over 20 ring layouts")
    print("  v      points  arc std/mean  predicted  fullest server / mean (users)")
    for v in [1, 10, 100, 1000]:
        cv, full = [], []
        for salt in range(20):
            r = Ring(range(16), v=v, salt=salt)
            sh = list(r.arc_shares().values())
            cv.append(statistics.pstdev(sh) / statistics.mean(sh))
            cnt = [0] * 16
            for k in users:
                cnt[r.lookup(k)] += 1
            full.append(max(cnt) / (n / 16))
        pred = math.sqrt(15 / (16 * v + 1))
        print(f"  {v:<6} {16 * v:>6}  {statistics.mean(cv):12.3f}"
              f"  {pred:9.3f}  {statistics.mean(full):8.2f}")

    print("moving users when a 17th server joins, 100 random layouts")
    for v in [1, 100]:
        fr = []
        for salt in range(100):
            r = Ring(range(16), v=v, salt=salt)
            b = [r.lookup(k) for k in users]
            r.add(16)
            fr.append(sum(r.lookup(k) != b[k] for k in users) / n)
        print(f"  v={v:<4} mean {statistics.mean(fr):.4f}  worst {max(fr):.4f}")

    # hot keys: if every user ran one online two-hop scan, list f is read deg(f) times, deg(f) ids each
    deg = [len(a) for a in adj]
    order = sorted(users, key=lambda k: -deg[k])
    top = order[: n // 100]
    reads, bytes_ = sum(deg), sum(d * d for d in deg)
    print(f"hot keys: top 1% of lists get {sum(deg[k] for k in top) / reads:.3f} of reads,"
          f" {sum(deg[k] ** 2 for k in top) / bytes_:.3f} of ids read;"
          f" hottest list read {deg[order[0]]} times, median {sorted(deg)[n // 2]}")
    ring = Ring(range(16), v=100)
    def shard_load(copies):
        load = [0.0] * 16
        for k in users:
            reps = ring.replicas(k, copies if k in hot else 1)
            for s in reps:
                load[s] += deg[k] ** 2 / len(reps)        # reads spread evenly over the copies
        return max(load) / (sum(load) / 16)
    hot = set(top)
    for r in [1, 2, 4, 16]:
        print(f"  graph store, ids read per shard, top 1% on {r:>2} replicas: fullest / mean = {shard_load(r):.2f}")
    sug = [0.0] * 16                                      # suggestion store: one key per request
    for k in users:
        sug[ring.lookup(k)] += deg[k]                     # requests proportional to activity
    print(f"  suggestion store, requests per shard: fullest / mean = {max(sug) / (sum(sug) / 16):.2f}")
    print("asserts passed")
