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
# A week with its own pages (a landing page, one page per day, a worksheet) replaces weeks/week_NN.md in the nav.
WEEK_PAGES = {
    "week_01": ("Week 1: Tokenization", [
        {"Week reading": "week_01/index.html"},
        {"Day 1: Text as data": "week_01/day_1.html"},
        {"Day 2: The objective": "week_01/day_2.html"},
        {"Day 3: Information": "week_01/day_3.html"},
        {"Day 4: Fast training": "week_01/day_4.html"},
        {"Day 5: Encoding and serving": "week_01/day_5.html"},
        {"Worksheet and learning checks": "week_01/worksheet.html"},
    ]),
}


def main() -> None:
    weeks = []
    for page in sorted((GUIDE / "docs" / "weeks").glob("week_*.md")):
        if page.stem in WEEK_PAGES:
            title, pages = WEEK_PAGES[page.stem]
            weeks.append({title: pages})
            continue
        title = page.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").replace(" · ", ": ", 1)
        weeks.append({title: f"weeks/{page.name}"})
    config_path = GUIDE / "mkdocs.yml"
    config = yaml.safe_load(config_path.read_text())
    config["nav"] = [{"Start here": "index.md"}, {"Month 1 plan": "month_01.md"}, {"Weeks": weeks}, {"By dimension": DIMENSIONS}]
    config_path.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True))
    print(f"nav: {len(weeks)} weeks")


if __name__ == "__main__":
    main()
