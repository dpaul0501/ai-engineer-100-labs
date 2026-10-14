from dataclasses import dataclass
from typing import Protocol


@dataclass
class Completion:
    text: str
    stop_reason: str  # "end" when the model finished, "max_tokens" when it was cut off
    input_tokens: int
    output_tokens: int


class LLMClient(Protocol):
    """Write a small adapter from your provider's SDK to this interface."""

    def complete(self, system: str, user: str, max_tokens: int) -> Completion: ...


@dataclass
class Answer:
    text: str
    sources: list[str]
    truncated: bool


def build_prompt(question: str, snippets: list[tuple[str, str]]) -> tuple[str, str]:
    """Return (system, user) prompts.

    snippets is a list of (file_name, text). The system prompt must tell the model
    to answer only from the snippets and to cite file names. Every file name must
    appear in the user prompt.
    """
    raise NotImplementedError


def answer(client: LLMClient, question: str, snippets: list[tuple[str, str]], max_tokens: int = 500) -> Answer:
    """Ask the model, and flag the answer as truncated when the stop reason says so.

    With no snippets, do not call the model: return an answer that says nothing was found.
    """
    raise NotImplementedError
