"""Check whether each page's markup actually uses the design system.

assets/brand_inline.py --check only proves the <style id="brand-core"> block is
byte identical to brand.css. It says nothing about whether the page's markup
targets the classes in it. A page can pass that check and still be styled almost
entirely by its own inline block, because the shell it authored uses names the
system never defined.

That is exactly what happened to five posts written outside the shell. So this
reads the markup instead: does the page open with the canonical nav, does it
close with the canonical footer, and what does it wrap its prose in.

  shell=Y   canonical .nav-bar and .footer-inner
  shell=P   partial, one of the two
  shell=N   neither, the page carries its own chrome

Two things this checker got wrong the first time, both worth keeping in mind:

  It searched the whole file, so a class name mentioned in a CSS comment inside
  the stamped brand-core block counted as markup. It reads only the body now.

  It tested the footer on `class="footer-social"`, which the OJCP post happened
  to use for one div inside an otherwise entirely bespoke footer. That scored a
  false Y. `.footer-inner` is the canonical footer's own layout row and no
  bespoke footer used it.

`own` counts the bytes of non brand-core <style> the page ships, which is the
size of the private stylesheet holding it together.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = (".cejel", ".playwright-mcp", ".git", "node_modules")

CORE = re.compile(r'<style id="brand-core">.*?</style>', re.S)
STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S)

# Every container a page has used for article prose. Only the first is canonical.
BODIES = ("prose", "article-body", "article-content")


def main() -> int:
    rows = []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if any(p in SKIP for p in rel.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        body = text.split("</head>", 1)[-1]

        nav = 'class="nav-bar"' in body
        foot = 'class="footer-inner' in body
        shell = "Y" if nav and foot else ("N" if not nav and not foot else "P")

        own = sum(len(m) for m in STYLE.findall(CORE.sub("", text)))
        head = (
            "article-head" if 'class="article-head"' in body
            else "hero" if 'class="hero' in body
            else "other"
        )
        wrap = next((b for b in BODIES if f'class="{b}"' in body), "-")
        rows.append((rel.as_posix(), shell, nav, foot, own, head, wrap))

    off_system = [r for r in rows if r[1] != "Y" or r[6] not in ("prose", "-")]
    print(f"{len(rows)} page(s), {len(rows) - len(off_system)} fully on the system\n")
    print(f"{'page':66} shell nav foot  own-css  head          body")
    for rel, shell, nav, foot, own, head, wrap in off_system:
        print(
            f"{rel:66} {shell:5} {'Y' if nav else 'N':3} {'Y' if foot else 'N':4}"
            f" {own:8} {head:13} {wrap}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
