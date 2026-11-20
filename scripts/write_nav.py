"""Write the guide's nav: start page, the released weeks, then one page per dimension.

    python scripts/write_nav.py
"""

from pathlib import Path

import yaml

GUIDE = Path(__file__).resolve().parent.parent / "guide"
DIMENSIONS = [
    {"DSA": "tracks/dsa.md"},
    {"ML": "tracks/ml.md"},
    {"AI": "tracks/ai.md"},
    {"System Design": "tracks/system-design.md"},
    {"Software Delivery": "tracks/software-delivery.md"},
]
# Released weeks, in program order. Each has a landing page (the week reading), one page per day, and a worksheet.
WEEKS = [
    ("Week 1: People You May Know", [
        {"Week reading": "week_01/index.html"},
        {"Day 1: Common friends": "week_01/day_1.html"},
        {"Day 2: The top k": "week_01/day_2.html"},
        {"Day 3: It is a graph": "week_01/day_3.html"},
        {"Day 4: Learn what engagement means": "week_01/day_4.html"},
        {"Day 5: A billion users": "week_01/day_5.html"},
        {"Worksheet and learning checks": "week_01/worksheet.html"},
        {"The talk (slides)": "week_01/talk.html"},
    ]),
    ("Week 3: Tokenization", [
        {"Week reading": "week_03/index.html"},
        {"Day 1: Text as data": "week_03/day_1.html"},
        {"Day 2: Greedy and the objective": "week_03/day_2.html"},
        {"Day 3: Information": "week_03/day_3.html"},
        {"Day 4: Fast training": "week_03/day_4.html"},
        {"Day 5: Encoding and serving": "week_03/day_5.html"},
        {"Worksheet and learning checks": "week_03/worksheet.html"},
    ]),
]


def main() -> None:
    weeks = [{title: pages} for title, pages in WEEKS]
    config_path = GUIDE / "mkdocs.yml"
    config = yaml.safe_load(config_path.read_text())
    config["nav"] = [{"Start here": "index.md"}, {"Month 1 plan": "month_01.md"}, {"Weeks": weeks}, {"By dimension": DIMENSIONS}]
    config_path.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True))
    print(f"nav: {len(weeks)} weeks")


if __name__ == "__main__":
    main()
