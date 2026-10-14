"""Write one page per pillar: its study sources and units, week by week.

Generated from the weekly pages (guide/docs/weeks/week_NN.md), so it stays in
sync. Run after editing a weekly page:

    python scripts/write_tracks.py
"""

import re
from pathlib import Path

from markdown.extensions.toc import slugify

GUIDE = Path(__file__).resolve().parent.parent / "guide"
LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")

PILLARS = {
    "dsa": ("DSA", "100 problems grouped by pattern. Each one: study the pattern, code it yourself, create and solve 1–2 variations, and write tests and corner cases for the original."),
    "ml-dl": ("ML/DL", "From NumPy to training a small GPT. Each concept: study it, implement it from scratch, vary it, test it against the library, and cover its numerical corner cases and parameters."),
    "ai-engineering": ("AI Engineering", "From one LLM call to production agents. Each experiment: study the technique, build it without a framework, measure variants, and test it with an eval set and edge cases."),
    "system-design": ("System Design & Engineering Practice", "How systems are designed and how industry builds and ships them. Each week: one design (requirements, estimates, variations, failure modes) and the practices applied in your own repo."),
}


def anchor(heading: str) -> str:
    return slugify(LINK.sub(r"\1", heading).replace("`", ""), "-")


def sections(text: str) -> dict[str, list[str]]:
    """Split a weekly page into its '## ' sections."""
    out, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:]
            out[current] = []
        elif current:
            out[current].append(line)
    return out


def main() -> None:
    weeks = sorted((GUIDE / "docs" / "weeks").glob("week_*.md"))
    for slug, (name, intro) in PILLARS.items():
        page = [f"# {name}", "", intro, ""]
        for week in weeks:
            text = week.read_text(encoding="utf-8")
            title = text.splitlines()[0].lstrip("# ")
            heading, body = next(((h, b) for h, b in sections(text).items() if h.startswith(f"{name}: ")), (None, None))
            if heading is None:
                continue
            link = f"../weeks/{week.name}"
            topic = heading[len(name) + 2:]
            page += [f"## {title}", "", f"**[{topic[:1].upper() + topic[1:]}]({link}#{anchor(heading)})**", ""]

            sources, in_sources = [], False
            for line in body:
                if line.startswith("**Study sources this week:**"):
                    in_sources = True
                elif in_sources and line.startswith("- "):
                    sources.append(line)
                elif in_sources and line.strip() and not line.startswith("- "):
                    break
            if sources:
                page += ["Study sources:", "", *sources, ""]

            page += ["| Unit | Study |", "|---|---|"]
            unit = None
            for line in body:
                if line.startswith("### "):
                    unit = line[4:]
                    label = LINK.sub(r"\1", unit)
                    page.append(f"| [{label}]({link}#{anchor(unit)}) | |")
                elif unit and line.startswith("- **Study:**"):
                    study = line[len("- **Study:** "):]
                    page[-1] = page[-1][:-3] + f"| {study[:1].upper() + study[1:]} |"
                    unit = None
            page.append("")

        out = GUIDE / "docs" / "tracks" / f"{slug}.md"
        out.parent.mkdir(exist_ok=True)
        out.write_text("\n".join(page), encoding="utf-8")
        print(f"{out.name}: {len(weeks)} weeks")


if __name__ == "__main__":
    main()
