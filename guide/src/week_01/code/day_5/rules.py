"""Day 5 · product rules applied to every response, after ranking, on fresh data.
The policies (age rule, notification cap) are illustrative choices, not any company's rules."""
from dataclasses import dataclass, field


@dataclass
class World:
    friends: dict                                  # user -> set of friends
    blocked: dict = field(default_factory=dict)    # user -> people they blocked
    dismissed: dict = field(default_factory=dict)  # user -> people they hid from their list
    requested: set = field(default_factory=set)    # pending requests (from, to)
    opted_out: set = field(default_factory=set)    # "don't suggest me to people"
    minors: set = field(default_factory=set)
    schools: dict = field(default_factory=dict)    # user -> set of school groups
    contacts_consent: set = field(default_factory=set)
    hides_list: set = field(default_factory=set)   # people who hide their friend list


def eligible(w, u, v, source):
    """Every rule is a hard filter; returns the reason v is dropped, or None if v may be shown."""
    g = lambda d, x: d.get(x, set())
    if v == u or v in g(w.friends, u):
        return "self or friend"
    if v in g(w.blocked, u) or u in g(w.blocked, v):
        return "blocked (either direction)"
    if v in g(w.dismissed, u):
        return "hidden by the viewer"
    if (u, v) in w.requested or (v, u) in w.requested:
        return "request already pending"
    if v in w.opted_out:
        return "opted out of suggestions"
    if (u in w.minors) != (v in w.minors) and not (g(w.schools, u) & g(w.schools, v)):
        return "minor and adult with no shared school"
    if source == "contacts" and u not in w.contacts_consent:
        return "contact import without consent"
    return None


def final_check(w, u, ranked, k=10):
    """ranked: (candidate, source) pairs from the store, best first. Keeps the first k eligible."""
    return [v for v, src in ranked if eligible(w, u, v, src) is None][:k]


def reason(w, u, v):
    """'Ben and Chloe are mutual friends': naming f reveals the friendship f-v, so only name
    people who do not hide their list, and say nothing if v hides theirs."""
    if v in w.hides_list:
        return ""
    names = sorted(f for f in w.friends[u] & w.friends[v] if f not in w.hides_list)
    hidden = len(w.friends[u] & w.friends[v]) - len(names)
    if not names:
        return f"{hidden} mutual friends" if hidden else ""
    return ", ".join(map(str, names)) + (f" and {hidden} more" if hidden else "")


class NotificationCap:
    """At most `cap` suggestion notifications per user per window, never the same person twice."""
    def __init__(self, cap=2):
        self.cap, self.sent = cap, {}

    def allow(self, u, v, window):
        seen = self.sent.setdefault(u, {})
        if v in seen or sum(1 for t in seen.values() if t == window) >= self.cap:
            return False
        seen[v] = window
        return True


if __name__ == "__main__":
    # You 0, Ben 1, Chloe 2, Dev 3, Esha 4, Farid 5
    fr = {0: {1, 2}, 1: {0, 2, 3, 4}, 2: {0, 1, 4, 5}, 3: {1}, 4: {1, 2}, 5: {2}}
    w = World(friends=fr)
    ranked = [(4, "fof"), (3, "fof"), (5, "fof"), (1, "fof")]
    assert final_check(w, 0, ranked) == [4, 3, 5]                 # Ben is a friend: dropped
    w.blocked = {5: {0}}                                          # Farid blocks You
    assert final_check(w, 0, ranked) == [4, 3]
    w.requested = {(0, 3)}                                        # You already asked Dev
    assert final_check(w, 0, ranked) == [4]
    w.minors, w.schools = {4}, {4: {"school-7"}}                  # Esha is a minor, no shared school
    assert final_check(w, 0, ranked) == []
    w.schools[0] = {"school-7"}
    assert final_check(w, 0, ranked) == [4]
    assert final_check(w, 0, [(9, "contacts")]) == []             # no consent to use contacts
    w.contacts_consent = {0}
    assert final_check(w, 0, [(9, "contacts")]) == [9]
    assert reason(w, 0, 4) == "1, 2"                              # Ben and Chloe
    w.hides_list = {2}                                            # Chloe hides her friend list
    assert reason(w, 0, 4) == "1 and 1 more"
    w.hides_list = {4}
    assert reason(w, 0, 4) == ""
    cap = NotificationCap(cap=2)
    assert [cap.allow(0, v, "wk1") for v in (4, 3, 5)] == [True, True, False]
    assert cap.allow(0, 5, "wk2") and not cap.allow(0, 4, "wk2")  # never re-notify Esha
    print("asserts passed")
