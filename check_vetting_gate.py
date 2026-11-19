import ast, re, py_compile
from pathlib import Path

py_compile.compile("app.py", doraise=True)
ast.parse(Path("app.py").read_text(encoding="utf-8"))

app_txt = Path("app.py").read_text(encoding="utf-8")
assert "/api/tab-picks" in app_txt
assert "threshold_passed" in app_txt

js_txt = Path("static/gem_polish.js").read_text(encoding="utf-8")
m = re.search(r"(?:async\s+)?function\s+showTab\s*\(key\)\s*\{.*?\n  \}", js_txt, re.DOTALL)
assert m and "CATALOG" not in m.group(0) and "threshold_passed === true" in m.group(0)
print("PERMANENT GATE CHECK PASSED")
