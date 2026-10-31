"""The Week 1 contracts. The acceptance tests depend on these signatures: do not change them."""

from typing import Hashable, Protocol, Sequence, runtime_checkable


@runtime_checkable
class Tokenizer(Protocol):
    """Turns text into token ids and back.

    Invariant: decode(encode(text)) == text for every str that UTF-8 can encode.
    """

    @property
    def vocab_size(self) -> int: ...

    def encode(self, text: str) -> list[int]: ...

    def decode(self, ids: Sequence[int]) -> str: ...


@runtime_checkable
class LanguageModel(Protocol):
    """Scores the next token given the tokens before it.

    Invariant: for any context, exp(logprobs(context)) has length vocab_size and sums to 1.
    """

    vocab_size: int

    def logprobs(self, context: Sequence[int]) -> list[float]: ...


@runtime_checkable
class Constraint(Protocol):
    """Decides which tokens may come next, so the output always stays inside a language.

    States are immutable and hashable, so allowed() can be cached per state.
    Invariants:
      - advance(s, t) is None exactly when t is not in allowed(s)
      - allowed(s) is empty exactly when is_done(s)
    """

    def start(self) -> Hashable: ...

    def advance(self, state: Hashable, token: int) -> Hashable | None: ...

    def allowed(self, state: Hashable) -> list[int]: ...

    def is_done(self, state: Hashable) -> bool: ...
