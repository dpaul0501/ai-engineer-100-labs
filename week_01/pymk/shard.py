"""Stretch: simulated sharding of adjacency lists with consistent hashing.

Use a stable hash (hashlib.blake2b with digest_size=8, read as a big-endian int), never Python's
hash(), which changes between processes for strings.
"""

from __future__ import annotations

from typing import Iterable, Sequence


def stable_hash(s: str) -> int:
    raise NotImplementedError


class ConsistentHashRing:
    """Each node owns `vnodes` points stable_hash(f"{node}#{i}") on a ring of 64-bit integers.
    A key belongs to the first point clockwise from stable_hash(str(key)), wrapping around."""

    def __init__(self, nodes: Iterable[str] = (), vnodes: int = 100):
        """vnodes < 1: ValueError."""
        raise NotImplementedError

    def add_node(self, node: str) -> None:
        """Adding a node moves only keys that now belong to it: about K / (N + 1) of K keys. Present: ValueError."""
        raise NotImplementedError

    def remove_node(self, node: str) -> None:
        """Unknown node: ValueError."""
        raise NotImplementedError

    def node_for(self, key: int) -> str:
        """Empty ring: ValueError."""
        raise NotImplementedError


def shards_touched(adj: Sequence[set[int]], u: int, ring: ConsistentHashRing) -> int:
    """How many distinct shards hold the adjacency lists of u's friends: the RPCs one request fans out to."""
    raise NotImplementedError
