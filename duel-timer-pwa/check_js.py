"""Extract the inline <script> blocks from index.html so Node can syntax-check them."""
import re
from pathlib import Path

root = Path(__file__).resolve().parent
html = (root / "index.html").read_text(encoding="utf-8")
blocks = re.findall(r"<script[^>]*>(.*?)</script>", html, flags=re.S | re.I)
out = "\n;\n".join(blocks)
(root / ".tmp-inline.js").write_text(out, encoding="utf-8")
print(f"extracted {len(blocks)} inline script block(s), {len(out)} chars")
