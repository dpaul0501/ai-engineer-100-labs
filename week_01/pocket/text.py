import re

_WORD = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Lowercase the text and return its words, in order.

    Implemented for you so the tests agree on what a word is.
    """
    return _WORD.findall(text.lower())
