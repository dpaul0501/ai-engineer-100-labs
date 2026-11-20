"""Fill @@CODE file|names|caption@@ placeholders with exact, HTML-escaped excerpts."""
import ast, html, re, sys
from pathlib import Path

W1 = Path(__file__).resolve().parents[2]
CODE = W1 / "code" / "day_5"
tpl = Path(sys.argv[1]).read_text()

def excerpt(fname, names):
    src = (CODE / fname).read_text()
    if names == "*":
        return src.rstrip("\n")
    tree = ast.parse(src)
    want = names.split(",")
    found = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in want:
            found[node.name] = ast.get_source_segment(src, node)
    missing = [n for n in want if n not in found]
    assert not missing, (fname, missing)
    return "\n\n\n".join(found[n] for n in want)

def card(m):
    fname, names, cap = m.group(1), m.group(2), m.group(3)
    code = excerpt(fname, names)
    return (f'<div class="code"><div class="ch"><span>code/day_5/{fname} · {cap}</span>'
            f'<button class="copy" type="button">Copy</button></div>'
            f'<pre><code class="language-python">{html.escape(code, quote=False)}</code></pre></div>')

out = re.sub(r"@@CODE ([^|]+)\|([^|]+)\|([^@]+)@@", card, tpl)
assert "@@" not in out
(W1 / "pages" / "day_5.body.html").write_text(out)
print("wrote", len(out), "chars")
