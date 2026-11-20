# Day 2 · top 10 on s shards, measured on the week's friendships, for every user.
# Shard by candidate: every candidate's whole count is on one shard, so local top 10 + merge is exact.
# Shard by middle friend: friend f's list lives on shard f mod s, so each shard sees only part of
# each candidate's mutual friends. Local top 10 + add-up can now be wrong; shuffle and TPUT are exact.
import statistics

from common import load_edges, friend_lists, candidate_counts
from distributed import local_top, merge_topk, split_topk, shuffle_topk, tput_topk
from topk import topk_sort

K = 10
friends = friend_lists(load_edges())
users = sorted(friends)


def partial_counts(u, s):
    """shard j counts only the mutual friends f of u with f mod s == j."""
    mine = friends[u]
    parts = [dict() for _ in range(s)]
    for f in mine:
        p = parts[f % s]
        for v in friends[f]:
            if v != u and v not in mine:
                p[v] = p.get(v, 0) + 1
    return parts


tenth = {u: sorted(candidate_counts(friends, u).values(), reverse=True)[K - 1]
         for u in users if len(candidate_counts(friends, u)) >= K}
big = {u for u, c in tenth.items() if c >= 8}
print(f"10th-best mutual count per user: median {statistics.median(tenth.values())}, "
      f"users with a 10th-best count >= 8: {len(big)}")
print(f"{'s':>3} | by candidate: exact | by middle friend, local top 10 + add up: lists differing, lists worse,"
      f" share of best total, pairs sent | shuffle: pairs sent | TPUT: pairs sent (all users; users with 10th >= 8)")
for s in (2, 4, 8, 16):
    wrong, worse, share, sent_split, sent_shuffle, sent_tput, tput_big, n_all = 0, 0, [], [], [], [], [], []
    for u in users:
        count = candidate_counts(friends, u)
        want = topk_sort(count, K)
        owned = [{v: c for v, c in count.items() if v % s == j} for j in range(s)]
        assert merge_topk([local_top(o, K) for o in owned], K) == want
        parts = partial_counts(u, s)
        got, sent = split_topk(parts, K)
        wrong += got != want                     # a different list, ties included
        best = sorted((count[v] for v in want), reverse=True)
        mine = sorted((count[v] for v in got), reverse=True)
        worse += mine != best                    # shows someone with fewer mutual friends than one left out
        share.append(sum(mine) / sum(best))
        sent_split.append(sent)
        exact, sent = shuffle_topk(parts, K)
        assert exact == want
        sent_shuffle.append(sent)
        t, sent = tput_topk(parts, K)
        assert t == want
        sent_tput.append(sent)
        if u in big:
            tput_big.append(sent / sent_shuffle[-1])
        n_all.append(len(count))
    print(f"{s:>3} | yes | {wrong / len(users):6.1%}, {worse / len(users):6.1%}, {statistics.mean(share):.3f},"
          f" {statistics.mean(sent_split):6.1f} | {statistics.mean(sent_shuffle):7.1f} | {statistics.mean(sent_tput):7.1f};"
          f" TPUT/shuffle for big users {statistics.mean(tput_big):.2f}")
print(f"mean candidates per user (what one machine would hold): {statistics.mean(n_all):.1f}")
