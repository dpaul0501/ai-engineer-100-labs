import argparse


def main(argv: list[str] | None = None) -> int:
    """`pocket index DIR`, `pocket search QUERY -k N`, `pocket ask QUESTION`."""
    parser = argparse.ArgumentParser(prog="pocket")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("index").add_argument("folder")
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("-k", type=int, default=5)
    sub.add_parser("ask").add_argument("question")
    args = parser.parse_args(argv)
    raise NotImplementedError(f"wire up `{args.command}`")


if __name__ == "__main__":
    raise SystemExit(main())
