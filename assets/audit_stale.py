"""Survey every page for stale brand markers and shell state.

Run after any merge that brings in pages authored against the old shell. The
markers are the things the pivot removed: donation links, the old title, the
old CTA, retired lead magnets and the dead checkout. `core` is whether the page
carries a <style id="brand-core"> block at all, which is how assets/brand_inline.py
decides a page is on the shared design system rather than hand-styled.
"""
import pathlib
import sys

MARKS = [
    "ko-fi",
    "github.com/sponsors",
    "Chief Architect",
    "Book an Audit",
    "ai-readiness-scorecard",
    "AI Automation",
    "onrender.com",
    "payhip",
    "paddle",
]

SKIP_PREFIXES = (".cejel/", ".playwright-mcp/", ".git/")


def main() -> int:
    rows = []
    total = 0
    for path in sorted(pathlib.Path(".").rglob("*.html")):
        rel = path.as_posix()
        if rel.startswith(SKIP_PREFIXES):
            continue
        total += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        low = text.lower()
        hits = {m: low.count(m.lower()) for m in MARKS}
        hits = {k: v for k, v in hits.items() if v}
        core = "brand-core" in text
        if hits or not core:
            rows.append((rel, len(text), core, hits))

    for rel, size, core, hits in rows:
        flag = "Y" if core else "N"
        print(f"{rel:66} {size:7} core={flag} {hits if hits else ''}")
    print(f"\n{len(rows)} of {total} page(s) need attention")
    return 0


if __name__ == "__main__":
    sys.exit(main())
