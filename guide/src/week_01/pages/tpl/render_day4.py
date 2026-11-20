# Render the Day 4 body from a template: <!--CODE file.py name1 name2--> becomes a code card holding the
# exact source of those functions from guide/src/week_01/code/day_4/file.py.
import ast, html, re, sys, textwrap
from pathlib import Path

W1 = Path(__file__).resolve().parents[2]
CODE = W1 / "code" / "day_4"
tpl = Path(sys.argv[1]).read_text()


def extract(fname, name):
    src = (CODE / fname).read_text()
    lines = src.splitlines()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name:
            seg = "\n".join(lines[node.lineno - 1:node.end_lineno])
            return textwrap.dedent(seg)
    raise KeyError(f"{fname}:{name}")


def card(m):
    fname, *names = m.group(1).split()
    body = "\n\n".join(extract(fname, n) for n in names)
    label = f"code/day_4/{fname} · " + ", ".join(names)
    return ('<div class="code"><div class="ch"><span>' + html.escape(label) +
            '</span><button class="copy" type="button">Copy</button></div><pre><code class="language-python">' +
            html.escape(body, quote=False) + "</code></pre></div>")


out = re.sub(r"<!--CODE ([^>]*?)-->", card, tpl)
(W1 / "pages" / "day_4.body.html").write_text(out)
print("written", len(out), "chars")
