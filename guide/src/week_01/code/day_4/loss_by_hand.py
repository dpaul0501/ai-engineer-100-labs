# Day 4, §6 and §9: log loss by hand, why it rewards honesty, and the small metric examples.
import math

import numpy as np

from common import average_precision, roc_auc


def log_loss_one(y, p):
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


# §6: three predictions, read in plain words
for y, p in [(1, 0.9), (1, 0.1), (0, 0.9)]:
    print(f"y={y}, p={p}: loss {log_loss_one(y, p):.2f}")
print(f"confidently wrong / confidently right: {log_loss_one(1, 0.1) / log_loss_one(1, 0.9):.1f}x")

# Proper scoring: if pairs like this connect 20% of the time, which reported q has the lowest
# expected loss? Log loss: q = 0.2 exactly. Absolute error |y - q|: q = 0, a dishonest answer.
p_true = 0.2
qs = np.linspace(0.01, 0.99, 99)
exp_log = -(p_true * np.log(qs) + (1 - p_true) * np.log(1 - qs))
exp_abs = p_true * (1 - qs) + (1 - p_true) * qs
print(f"true rate {p_true}: best q under log loss {qs[exp_log.argmin()]:.2f}, "
      f"under absolute error {qs[exp_abs.argmin()]:.2f}")
for q in (0.1, 0.2, 0.3):
    print(f"  report q={q}: expected log loss {-(p_true * math.log(q) + (1 - p_true) * math.log(1 - q)):.4f}")
assert abs(qs[exp_log.argmin()] - 0.2) < 1e-9 and qs[exp_abs.argmin()] == qs[0]

# Accuracy is a staircase: moving one prediction from 0.40 to 0.49 changes nothing
y = np.array([1, 0, 0, 1]); p = np.array([0.40, 0.30, 0.20, 0.80])
acc = lambda p: np.mean((p >= 0.5) == y)
p2 = p.copy(); p2[0] = 0.49
ll = lambda p: -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
print(f"accuracy {acc(p):.2f} -> {acc(p2):.2f}; log loss {ll(p):.4f} -> {ll(p2):.4f}")
assert acc(p) == acc(p2) and ll(p2) < ll(p)

# §9: 10,000 impressions, 100 positives; "no for everyone"
print(f"accuracy of 'no' with 100 positives in 10,000: {(10_000 - 100) / 10_000:.0%}")

# AUC and average precision by hand
print(f"AUC of scores (3, 2, 2, 1) for labels (1, 1, 0, 0): {roc_auc([3, 2, 2, 1], [1, 1, 0, 0]):.3f}")
print(f"average precision of scores (4, 3, 2, 1), labels (1, 0, 1, 0): {average_precision([4, 3, 2, 1], [1, 0, 1, 0]):.3f}")

# Sampling negatives with r = 0.05 multiplies the odds by 20: 2 vs 998 becomes 2 vs 49.9
print(f"odds before {2 / 998:.5f}, after {2 / (998 * 0.05):.5f}, ratio {(2 / 49.9) / (2 / 998):.0f}; log r = {math.log(0.05):.2f}")
