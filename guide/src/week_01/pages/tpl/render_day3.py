"""Fill {{CODE:file.py:name1,name2}} markers with exact, HTML-escaped source excerpts."""
# Usage (from this folder): python3 render_day3.py day_3.tpl.html ../day_3.body.html BRIDGE_TABLE=day_3_bridge_table.html PPR_RESULTS=day_3_ppr_results.html
import ast, html, re, sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[2] / "code" / "day_3"
tpl, out = Path(sys.argv[1]), Path(sys.argv[2])
extra = dict(a.split("=", 1) for a in sys.argv[3:])   # NAME=path-to-html-fragment

def excerpt(fname, names):
    src = (CODE / fname).read_text()
    lines = src.splitlines()
    tree = ast.parse(src)
    parts = []
    for name in names:
        node = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)
        start = node.lineno - 1
        # include a comment line directly above (e.g. "# LeetCode 1971 · ...")
        while start > 0 and lines[start - 1].startswith("#"):
            start -= 1
        parts.append("\n".join(lines[start:node.end_lineno]))
    body = "\n\n".join(parts)
    assert all(p in src for p in parts)
    label = "code/day_3/" + fname
    return ('<div class="code"><div class="ch"><span>%s</span><button class="copy" type="button">Copy</button></div>'
            '<pre><code class="language-python">%s</code></pre></div>' % (label, html.escape(body, quote=False)))

s = tpl.read_text()
s = re.sub(r"\{\{CODE:([\w.]+):([\w,]+)\}\}", lambda m: excerpt(m.group(1), m.group(2).split(",")), s)
for k, v in extra.items():
    s = s.replace("{{%s}}" % k, Path(v).read_text())
assert "{{" not in s, re.findall(r"\{\{[^}]*\}\}", s)
out.write_text(s)
print("wrote", out, len(s), "bytes")
