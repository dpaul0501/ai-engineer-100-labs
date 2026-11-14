"""Write one page per dimension: what each released week teaches in it, day by day.

Generated from the week pages (guide/docs/week_NN/*.html), in the order of WEEKS in
write_nav.py, so it stays in sync. Run after changing a week:

    python scripts/write_tracks.py
"""

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from write_nav import WEEKS  # noqa: E402

DOCS = Path(__file__).resolve().parent.parent / "guide" / "docs"

DIMENSIONS = {
    "dsa": ("DSA", "Algorithms and data structures taught as subjects: each one posed as a question, derived, proved, costed, then practised on LeetCode problems and variations, in the week whose design problem needs it."),
    "ml": ("ML", "Statistics and core ML: each idea derived from first principles, checked by measuring it on the week's data, then tied back to the week's design problem."),
    "ai": ("AI", "Every week is built around one design problem of the kind top companies ask. These are the problems, and the AI-specific skills each week checks."),
    "system-design": ("System Design", "Each week's design problem taken to production: estimates with stated assumptions, storage and sharding, caching, tail latency, and the serving architecture."),
    "software-delivery": ("Software Delivery", "Spec → contract → test → code, every week: function contracts, golden, property and differential tests, and the lab's acceptance tests."),
}
DELIVERY = re.compile(r"contract|test", re.I)


def text(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", fragment)).split())


def blocks(page: str):
    """Yield (class, kind, sub-topics, LeetCode links) for each block on a page."""
    starts = list(re.finditer(r'<div class="blk (\w+)"[^>]*>\s*<div class="bh"><span class="kind">(.*?)</span>', page, re.S))
    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else page.find('<div class="check"', m.end())
        body = page[m.end():end] if end > 0 else page[m.end():]
        subs = [text(h) for h in re.findall(r"<h4[^>]*>(.*?)</h4>", body, re.S)]
        problems = {}
        for href, label in re.findall(r'<a [^>]*href="(https://leetcode\.com/problems/[^"]+)"[^>]*>(.*?)</a>', body, re.S):
            problems.setdefault(href, text(label))
        yield m.group(1), text(m.group(2)), subs, problems


def checks(page: str, dim: str) -> list[str]:
    return [text(t) for t in re.findall(r'data-dim="%s"><span class="tx">(.*?)</span>' % dim, page, re.S)]


def main() -> None:
    pages = {slug: [f"# {name}", "", intro, ""] for slug, (name, intro) in DIMENSIONS.items()}
    for week_title, entries in WEEKS:
        days = []
        for entry in entries:
            (label, path), = entry.items()
            f = DOCS / path
            if f.exists() and "talk" not in f.name:
                days.append((label, path, f.read_text(encoding="utf-8")))
        start = {slug: len(lines) for slug, lines in pages.items()}
        for slug in pages:
            pages[slug] += [f"## {week_title}", ""]
        reading = next((d for d in days if d[0] == "Week reading"), None)
        if reading:
            h1 = re.search(r"<h1[^>]*>(.*?)</h1>", reading[2], re.S)
            pages["ai"] += [f"**The problem:** [{text(h1.group(1)) if h1 else week_title}](../{reading[1]})", ""]
        for label, path, page in days:
            link = f"../{path}"
            for cls, kind, subs, problems in blocks(page):
                slug = {"alg": "dsa", "ml": "ml", "des": "system-design"}.get(cls)
                if cls == "des" and DELIVERY.search(kind):
                    slug = "software-delivery"
                if not slug:
                    continue
                topic = kind.split("·", 1)[-1].strip()
                pages[slug].append(f"- **[{label}]({link}):** {topic}")
                pages[slug] += [f"    - {s}" for s in subs]
                if problems:
                    pages[slug].append("    - Practice: " + " · ".join(f"[{t}]({h})" for h, t in problems.items()))
            for slug, dim in (("ai", "ai"), ("software-delivery", "del")):
                items = checks(page, dim)
                if items:
                    pages[slug].append(f"- **[{label}]({link}):** checkpoint")
                    pages[slug] += [f"    - {c}" for c in items]
        for slug, lines in pages.items():
            if len(lines) == start[slug] + 2:
                lines.append("The pages for this week are still being written.")
            lines.append("")

    for slug, lines in pages.items():
        out = DOCS / "tracks" / f"{slug}.md"
        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"{out.name}: {sum(l.startswith('- ') for l in lines)} entries")


if __name__ == "__main__":
    main()
