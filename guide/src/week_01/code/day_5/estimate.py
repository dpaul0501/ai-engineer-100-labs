"""Day 5 · back-of-envelope estimate for People You May Know at a billion users.
Every input is a labelled hypothetical, except `skew`, which is measured on the week's graph."""
import math
from common import load_edges, build_adj


def skew_of(adj):
    """E[d^2] / E[d]^2: how much more a two-hop scan reads than 'degree x degree' suggests."""
    d = [len(a) for a in adj]
    m1 = sum(d) / len(d)
    m2 = sum(x * x for x in d) / len(d)
    return m1, m2, m2 / m1 ** 2


def estimate(users=1_000_000_000,   # HYPOTHETICAL: given by the interviewer
             mean_deg=200,          # HYPOTHETICAL: mean friends per user
             id_bytes=8,            # one 64-bit id per stored friend
             active_share=0.5,      # HYPOTHETICAL: share of users who open the app on a day
             loads_per_day=2,       # HYPOTHETICAL: PYMK loads per active user per day
             peak_factor=3,         # HYPOTHETICAL: busiest hour / average hour
             skew=3.69,             # MEASURED on the week's graph: E[d^2] / E[d]^2
             top_n=100,             # HYPOTHETICAL: suggestions stored per user
             shards=1_000):         # HYPOTHETICAL: graph-store shards
    friendships = users * mean_deg // 2
    entries = 2 * friendships                       # each friendship is in two lists
    requests_day = users * active_share * loads_per_day
    qps_avg = requests_day / 86_400
    qps_peak = qps_avg * peak_factor
    reads = mean_deg * mean_deg * skew              # ids read by one two-hop request
    return {
        "friendships": friendships,
        "graph_TB": entries * id_bytes / 1e12,
        "qps_avg": qps_avg,
        "qps_peak": qps_peak,
        "reads_per_request": reads,
        "peak_GB_per_s": qps_peak * reads * id_bytes / 1e9,
        "shards_touched": shards * (1 - (1 - 1 / shards) ** mean_deg),
        "online_reads_per_day": requests_day * reads,
        "batch_join_rows": users * reads,           # sum over middle users of d(d-1) ~ n E[d^2]
        "store_TB": users * top_n * (8 + 4) / 1e12, # (id, score) pairs
    }


if __name__ == "__main__":
    m1, m2, s = skew_of(build_adj(load_edges()))
    print(f"week's graph: E[d] = {m1:.1f}, E[d^2] = {m2:.1f}, skew = {s:.3f}")
    e = estimate(skew=round(s, 2))
    for k, v in e.items():
        print(f"{k:>22}: {v:,.1f}" if v < 1e9 else f"{k:>22}: {v:.3e}")
    assert e["friendships"] == 100_000_000_000
    assert abs(e["graph_TB"] - 1.6) < 1e-9
    assert round(e["qps_peak"]) == 34_722
    assert abs(e["store_TB"] - 1.2) < 1e-9
    assert 180 < e["shards_touched"] < 182
    print("asserts passed")
