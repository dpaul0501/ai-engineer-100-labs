# Fill @@SRC file name[,name...]@@ markers with exact, HTML-escaped source of top-level defs/classes.
import ast, re, sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[2] / "code" / "day_2"
TPL = Path(sys.argv[1])
OUT = Path(__file__).resolve().parents[1] / "day_2.body.html"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def src(fname, names):
    text = (CODE / fname).read_text()
    tree = ast.parse(text)
    lines = text.splitlines()
    parts = []
    for name in names:
        node = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)
        parts.append("\n".join(lines[node.lineno - 1:node.end_lineno]))
    return esc("\n\n\n".join(parts))


def lines_of(fname, a, b):
    return esc("\n".join((CODE / fname).read_text().splitlines()[a - 1:b]))


t = TPL.read_text()
t = re.sub(r"@@SRC (\S+) (\S+)@@", lambda m: src(m.group(1), m.group(2).split(",")), t)
t = re.sub(r"@@LINES (\S+) (\d+)-(\d+)@@", lambda m: lines_of(m.group(1), int(m.group(2)), int(m.group(3))), t)
assert "@@" not in t
OUT.write_text(t)
print("wrote", OUT, len(t), "chars")
