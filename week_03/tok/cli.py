"""The `tok` command line.

tok train CORPUS --vocab-size N --out tok.json
tok encode --model tok.json TEXT          prints a JSON list of ids
tok decode --model tok.json IDS           IDS is a JSON list; prints the text with no trailing newline
tok ppl --model tok.json --train A --eval B [--n 2] [--k 0.1]
                                          prints {"n": n, "perplexity": p}
tok generate --model tok.json --train A [--n 3] [--k 0.01] [--temperature 1.0] [--top-k K] [--top-p P]
             [--max-new-tokens 200] [--samples 10] [--seed 0] [--json]
                                          fits an n-gram on A, samples; --json constrains output to JSON.
                                          prints {"samples": [text, ...], "valid_rate": r}, where r is the
                                          share of samples that json.loads parses to a dict or list
"""

from __future__ import annotations


def main(argv: list[str] | None = None) -> int:
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
