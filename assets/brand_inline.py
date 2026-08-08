#!/usr/bin/env python3
"""brand_inline.py - push assets/brand.css into every public surface.

Why this exists instead of a <link> tag.

automation/brand_check.py reads <style> blocks and inline style="" attributes.
Linked stylesheets are invisible to it, so a page that moves its CSS into an
external file passes by having nothing to check. That is a false green, and the
brand-compiler skill names it as a known limit. So the shared system lives in
one file, assets/brand.css, and this script stamps that file verbatim into the
<style id="brand-core"> block of every page. The stylesheet stays the single
source of truth and the checker still grades real CSS.

Run it after any edit to assets/brand.css. Never hand-edit a brand-core block.

    python assets/brand_inline.py            # rewrite every page
    python assets/brand_inline.py --check    # exit 1 if any page is stale

Stdlib only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "assets" / "brand.css"

OPEN = '<style id="brand-core">'
CLOSE = "</style>"

BLOCK_RE = re.compile(
    re.escape(OPEN) + r".*?" + re.escape(CLOSE), re.S)


def surfaces() -> list[Path]:
    out = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        if OPEN in path.read_text(encoding="utf-8"):
            out.append(path)
    return out


def main() -> int:
    if not BRAND.is_file():
        print(f"missing {BRAND}", file=sys.stderr)
        return 2
    css = BRAND.read_text(encoding="utf-8").rstrip("\n")
    block = f"{OPEN}\n{css}\n{CLOSE}"
    check = "--check" in sys.argv

    stale = 0
    for path in surfaces():
        text = path.read_text(encoding="utf-8")
        new = BLOCK_RE.sub(lambda _m: block, text, count=1)
        rel = path.relative_to(ROOT).as_posix()
        if new == text:
            print(f"ok      {rel}")
            continue
        stale += 1
        if check:
            print(f"STALE   {rel}")
        else:
            path.write_text(new, encoding="utf-8")
            print(f"wrote   {rel}")

    if check and stale:
        print(f"\n{stale} page(s) out of sync with assets/brand.css")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
