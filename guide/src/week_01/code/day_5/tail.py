"""Day 5 · fan-out and tail latency, hedged requests, and Little's law.
The latency model is a stated HYPOTHETICAL: each shard call takes a lognormal time with median
2 ms, and 1% of calls hit a 50 ms stall (a pause, a busy disk). Calls are independent."""
import numpy as np

rng = np.random.default_rng(0)
P_SLOW, STALL = 0.01, 50.0


def call_times(size):
    t = 2.0 * np.exp(0.3 * rng.standard_normal(size))
    return t + STALL * (rng.random(size) < P_SLOW)


def request_times(s, n=100_000, hedge_at=None):
    """A request waits for all s calls. With hedging, a call not back by `hedge_at` ms gets a
    second copy sent to another replica; the first answer wins."""
    t = call_times((n, s))
    extra = 0.0
    if hedge_at is not None:
        late = t > hedge_at
        backup = hedge_at + call_times((n, s))
        t = np.where(late, np.minimum(t, backup), t)
        extra = late.mean()                      # share of calls that sent a second copy
    return t.max(axis=1), extra


def p_any_slow(p, s):
    return 1 - (1 - p) ** s


def mm1_check(lam=0.8, mu=1.0, n=200_000):
    """Little's law on a simulated single-server queue: time-average number inside vs lambda * W."""
    arrive = np.cumsum(rng.exponential(1 / lam, n))
    service = rng.exponential(1 / mu, n)
    done = np.empty(n)
    free = 0.0
    for i in range(n):
        free = max(free, arrive[i]) + service[i]
        done[i] = free
    W = (done - arrive).mean()
    T = arrive[-1]
    probes = rng.uniform(0, T, 200_000)          # look inside at random moments
    L = (np.searchsorted(arrive, probes) - np.searchsorted(done, probes)).mean()
    return n / T, W, L


if __name__ == "__main__":
    one = call_times(1_000_000)
    p95 = float(np.percentile(one, 95))
    print(f"one call: p50 {np.percentile(one, 50):.2f} ms, p95 {p95:.2f}, p99 {np.percentile(one, 99):.2f}"
          f", p99.9 {np.percentile(one, 99.9):.2f}")
    print("shards  p50 ms  p99 ms  slow (>20 ms)  predicted 1-(1-p)^s  | hedged at p95: p99 ms  slow  extra calls")
    for s in [1, 10, 100, 181]:
        t, _ = request_times(s)
        h, extra = request_times(s, hedge_at=p95)
        print(f"{s:>6}  {np.percentile(t, 50):6.2f}  {np.percentile(t, 99):6.2f}  {(t > 20).mean():13.3f}"
              f"  {p_any_slow(P_SLOW, s):19.3f}  |  {np.percentile(h, 99):20.2f}  {(h > 20).mean():.4f}"
              f"  {extra:.3f}")
    assert abs(p_any_slow(0.01, 100) - 0.634) < 1e-3
    lam, W, L = mm1_check()
    print(f"Little's law, simulated queue: arrival rate {lam:.4f}, mean time inside {W:.3f},"
          f" lambda*W {lam * W:.3f}, measured L {L:.3f}")
    assert abs(L - lam * W) / L < 0.03
    print(f"peak example: 34,722 req/s x 0.050 s = {34_722 * 0.050:,.0f} requests in flight")
    print("asserts passed")
