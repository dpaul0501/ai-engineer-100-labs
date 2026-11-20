"""Day 5 · versioned keys and snapshots for the suggestion store.
TimeMap is LeetCode 981, SnapshotArray is LeetCode 1146; SuggestionStore uses the same idea to
publish a nightly batch atomically and roll it back."""
import bisect
from collections import defaultdict


class TimeMap:
    """LeetCode 981. Timestamps arrive increasing per key, so each key's list stays sorted."""
    def __init__(self):
        self.times, self.vals = defaultdict(list), defaultdict(list)

    def set(self, key, value, timestamp):
        self.times[key].append(timestamp)
        self.vals[key].append(value)

    def get(self, key, timestamp):
        i = bisect.bisect_right(self.times[key], timestamp)   # first time > timestamp
        return self.vals[key][i - 1] if i else ""


class SnapshotArray:
    """LeetCode 1146. Each index keeps (snap_id, value) pairs; a snapshot costs O(1)."""
    def __init__(self, length):
        self.hist = [[(-1, 0)] for _ in range(length)]
        self.snap_id = 0

    def set(self, index, val):
        h = self.hist[index]
        if h[-1][0] == self.snap_id:
            h[-1] = (self.snap_id, val)                       # overwrite within the same snapshot
        else:
            h.append((self.snap_id, val))

    def snap(self):
        self.snap_id += 1
        return self.snap_id - 1

    def get(self, index, snap_id):
        h = self.hist[index]
        i = bisect.bisect_right(h, (snap_id, float("inf")))
        return h[i - 1][1]


class SuggestionStore:
    """Keys are (version, user). A batch writes a whole new version, then one pointer flip makes
    it live; readers never see half a batch, and a bad batch is undone by flipping back."""
    def __init__(self, keep=3):
        self.data, self.live, self.keep = {}, None, keep
        self.versions = []

    def write_batch(self, version, lists):
        for user, top in lists.items():
            self.data[(version, user)] = top
        self.versions.append(version)

    def publish(self, version):
        assert version in self.versions
        self.live = version                                   # the atomic step
        old = self.versions[:-self.keep]                      # garbage-collect old versions
        self.versions = self.versions[-self.keep:]
        self.data = {k: v for k, v in self.data.items() if k[0] not in old}

    def rollback(self):
        i = self.versions.index(self.live)
        assert i > 0, "no older version kept"
        self.live = self.versions[i - 1]

    def get(self, user):
        return self.data.get((self.live, user), [])


if __name__ == "__main__":
    tm = TimeMap()                                            # LeetCode 981's example
    tm.set("foo", "bar", 1)
    assert tm.get("foo", 1) == "bar" and tm.get("foo", 3) == "bar"
    tm.set("foo", "bar2", 4)
    assert tm.get("foo", 4) == "bar2" and tm.get("foo", 5) == "bar2" and tm.get("foo", 0) == ""

    sa = SnapshotArray(3)                                     # LeetCode 1146's example
    sa.set(0, 5)
    assert sa.snap() == 0
    sa.set(0, 6)
    assert sa.get(0, 0) == 5 and sa.get(0, 1) == 6 and sa.get(2, 0) == 0

    st = SuggestionStore(keep=2)                              # You = 0: Esha, Dev, Farid
    st.write_batch("night-1", {0: [4, 3, 5]})
    st.publish("night-1")
    st.write_batch("night-2", {0: [9, 9, 9]})                 # a broken batch, written but not live
    assert st.get(0) == [4, 3, 5]                             # readers still see night-1
    st.publish("night-2")
    assert st.get(0) == [9, 9, 9]
    st.rollback()                                             # one flip undoes the bad batch
    assert st.get(0) == [4, 3, 5]
    st.write_batch("night-3", {0: [4, 3]})
    st.publish("night-3")
    assert ("night-1", 0) not in st.data                      # only the last two versions kept
    print("asserts passed")
