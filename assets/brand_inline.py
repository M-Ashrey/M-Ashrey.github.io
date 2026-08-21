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

One caveat this script learned the hard way. Finding the id is not proof that
the block holds brand.css. Five posts arrived carrying page-specific CSS under
the canonical id, and an earlier run read that as a stale stamp, replaced it,
and deleted every rule those pages depended on. --check then passed, because by
that point the block really was byte identical to brand.css. So the overwrite is
gated on the existing block looking like an older brand.css: it has to share at
least half of the current file's class selectors. A real previous version shares
about 96 percent of them. Those five private stylesheets shared 4 to 13 percent.
The gap is wide enough that the test is not delicate.

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

SELECTOR_RE = re.compile(r"(?<![\w-])(\.[A-Za-z][\w-]*)")

# A block sharing less than this fraction of brand.css's class selectors is not
# a previous version of brand.css. It is somebody else's stylesheet.
MIN_OVERLAP = 0.5


def surfaces() -> list[Path]:
    out = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        if OPEN in path.read_text(encoding="utf-8"):
            out.append(path)
    return out


def looks_like_brand(block: str, wanted: set[str]) -> float:
    """How much of brand.css's vocabulary this block already defines."""
    return len(set(SELECTOR_RE.findall(block)) & wanted) / len(wanted)


def main() -> int:
    if not BRAND.is_file():
        print(f"missing {BRAND}", file=sys.stderr)
        return 2
    css = BRAND.read_text(encoding="utf-8").rstrip("\n")
    block = f"{OPEN}\n{css}\n{CLOSE}"
    wanted = set(SELECTOR_RE.findall(css))
    check = "--check" in sys.argv

    stale = 0
    foreign = []
    for path in surfaces():
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()

        found = BLOCK_RE.search(text)
        share = looks_like_brand(found.group(0), wanted) if found else 1.0
        if share < MIN_OVERLAP:
            foreign.append((rel, share))
            print(f"FOREIGN {rel}  shares {share:.0%} of brand.css")
            continue

        new = BLOCK_RE.sub(lambda _m: block, text, count=1)
        if new == text:
            print(f"ok      {rel}")
            continue
        stale += 1
        if check:
            print(f"STALE   {rel}")
        else:
            path.write_text(new, encoding="utf-8")
            print(f"wrote   {rel}")

    if foreign:
        print(
            f"\n{len(foreign)} page(s) carry a foreign stylesheet under "
            f'id="brand-core" and were left alone. Move that CSS out of the '
            "canonical block, or move the page onto the shell, before stamping."
        )
        return 1
    if check and stale:
        print(f"\n{stale} page(s) out of sync with assets/brand.css")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
