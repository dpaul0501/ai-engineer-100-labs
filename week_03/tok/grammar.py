"""Grammar-constrained decoding for JSON: a byte-level pushdown automaton plus a vocabulary trie.

The language: compact JSON (no whitespace outside strings), top level an object or an array,
nesting depth at most max_depth, strings valid UTF-8, the escapes \\" \\\\ \\/ \\b \\f \\n \\r \\t \\uXXXX,
numbers as in RFC 8259 (no leading zeros, no NaN or Infinity).

Design rules (the tests rely on them):
  - A state is immutable and hashable, for example a tuple (mode, aux, stack) with stack a tuple.
  - step() reads one byte and returns the next state, or None if the byte cannot come next.
"""

from __future__ import annotations

from typing import Hashable, Mapping

State = Hashable


def step(state: State, b: int, max_depth: int = 32) -> State | None:
    """The state after reading byte b, or None. Hint: a number only ends when the next byte is , ] or }."""
    raise NotImplementedError


def is_valid_json(data: bytes) -> bool:
    """True when data is one complete value of the language above."""
    raise NotImplementedError


class TokenTrie:
    """Every token's bytes in one trie. A token can end at an inner node: 'a' and 'ab' share a path."""

    def __init__(self, vocab: Mapping[int, bytes]):
        raise NotImplementedError


class JsonConstraint:
    """Implements contracts.Constraint for the language above, over a byte-level vocabulary {id: bytes}.

    allowed(state) walks the trie once, feeding bytes to the automaton and pruning a subtree as soon as
    a byte is rejected. Results are cached per state, keeping at most cache_size entries (0 disables it).
    allowed() returns ids in increasing order.
    """

    def __init__(self, vocab: Mapping[int, bytes], max_depth: int = 32, cache_size: int = 4096):
        raise NotImplementedError

    def start(self) -> State:
        raise NotImplementedError

    def advance(self, state: State, token: int) -> State | None:
        raise NotImplementedError

    def allowed(self, state: State) -> list[int]:
        raise NotImplementedError

    def is_done(self, state: State) -> bool:
        raise NotImplementedError
