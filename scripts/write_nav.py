"""Write the guide's nav: start page, one page per pillar, then the released weeks.

    python scripts/write_nav.py
"""

from pathlib import Path

import yaml

GUIDE = Path(__file__).resolve().parent.parent / "guide"
PILLARS = [
    {"DSA": "tracks/dsa.md"},
    {"ML/DL": "tracks/ml-dl.md"},
    {"AI Engineering": "tracks/ai-engineering.md"},
    {"System Design & Engineering Practice": "tracks/system-design.md"},
]


def main() -> None:
    weeks = []
    for page in sorted((GUIDE / "docs" / "weeks").glob("week_*.md")):
        title = page.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").replace(" · ", ": ", 1)
        weeks.append({title: f"weeks/{page.name}"})
    config_path = GUIDE / "mkdocs.yml"
    config = yaml.safe_load(config_path.read_text())
    config["nav"] = [{"Start here": "index.md"}, {"By pillar": PILLARS}, {"Weeks": weeks}]
    config_path.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True))
    print(f"nav: {len(weeks)} weeks")


if __name__ == "__main__":
    main()
