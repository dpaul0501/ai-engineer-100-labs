# Fill @@CODE file a-b@@ markers with HTML-escaped exact excerpts of the tested code.
# Usage: python3 assemble.py day_1.tpl.html  (writes ../day_1.body.html)
import html, re, sys
from pathlib import Path
W = Path(__file__).resolve().parents[2]
src = Path(sys.argv[1]).read_text()
def sub(m):
    f, a, b = m.group(1), int(m.group(2)), int(m.group(3))
    lines = (W / "code" / "day_1" / f).read_text().splitlines()[a - 1:b]
    while lines and not lines[-1].strip():
        lines.pop()
    return html.escape("\n".join(lines), quote=False)
out = re.sub(r"@@CODE (\S+) (\d+)-(\d+)@@", sub, src)
assert "@@" not in out
(W / "pages" / "day_1.body.html").write_text(out)
print("written", len(out))
