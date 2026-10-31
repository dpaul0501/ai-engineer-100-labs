"""Write the guide's nav: start page, one page per dimension, then the released weeks.

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


def main() -> None:
    weeks = []
    for page in sorted((GUIDE / "docs" / "weeks").glob("week_*.md")):
        title = page.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").replace(" · ", ": ", 1)
        weeks.append({title: f"weeks/{page.name}"})
    config_path = GUIDE / "mkdocs.yml"
    config = yaml.safe_load(config_path.read_text())
    config["nav"] = [{"Start here": "index.md"}, {"Month 1 plan": "month_01.md"}, {"Weeks": weeks}, {"By dimension": DIMENSIONS}]
    config_path.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True))
    print(f"nav: {len(weeks)} weeks")


if __name__ == "__main__":
    main()
