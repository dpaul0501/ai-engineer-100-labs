"""Week 1: People You May Know, from two hops to a billion users.

graph    load the week's graph, adjacency sets, the temporal split, work per request
exact    the exact friends-of-friends baseline (mutual-friend counts, top-k)
sample   sampled estimates and budgeted, hub-capped candidate generation
minhash  Jaccard, MinHash signatures, LSH banding (a second candidate source)
rank     pair features, the temporal training set, logistic regression in NumPy
serve    the API: LRU cache, the final eligibility filter, cache invalidation
metrics  recall@k, AUC, bootstrap confidence intervals, percentiles
shard    stretch: consistent hashing and shards touched per request
"""

__version__ = "0.1.0"
