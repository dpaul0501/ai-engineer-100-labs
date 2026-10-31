"""Write one page per dimension: its study sources and units, week by week.

Generated from the weekly pages (guide/docs/weeks/week_NN.md), so it stays in
sync. Run after editing a weekly page:

    python scripts/write_tracks.py
"""

import re
from pathlib import Path

from markdown.extensions.toc import slugify

GUIDE = Path(__file__).resolve().parent.parent / "guide"
LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")

DIMENSIONS = {
    "dsa": ("DSA", "Every LeetCode pattern, each placed in the week whose project uses it. Each problem: try it first, code it yourself, solve 1–2 variations, and write tests and corner cases."),
    "ml": ("ML", "Statistics and core ML: probability, linear algebra, calculus, optimization and measurement, each learned where the build needs it. Each unit: derive it, check it numerically, and vary it."),
    "ai": ("AI", "LLMs from the inside out: tokens and decoding, prompts, context and memory, retrieval, agents and skills, then the models themselves. Each unit: study it, build it, vary it, test it, and cover its corner cases."),
    "system-design": ("System Design", "Two design reps a week (◆ = timed mock) covering the Google and Meta product, infrastructure, ML and LLM rounds. Each one: requirements with numbers, estimates, API, data model, deep dives, bottlenecks."),
    "software-delivery": ("Software Delivery", "Spec → contract → test → code, every week. Each week adds one technique: properties, golden tests, planted bugs, CI, release, security, operations."),
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
    for slug, (name, intro) in DIMENSIONS.items():
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

            if not any(line.startswith("### ") for line in body):
                table = [line for line in body if line.startswith("|")]
                page += [*table, ""] if table else []
                continue
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
