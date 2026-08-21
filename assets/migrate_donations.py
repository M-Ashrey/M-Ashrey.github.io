#!/usr/bin/env python3
"""Strip the donation asks out of the blog archive.

Eleven older posts ended on a variant of "support my open-source work on
Ko-fi". A lab that quotes ten thousand dollars an install does not also pass
the hat, so every one of those paragraphs is replaced with a pointer at the
work itself.

The paragraphs were all hand-written and none of them match, so the match is
"any <p> containing a ko-fi.com link" rather than a literal string. Inline
style attributes on the old markup are preserved where they exist, because two
of these posts predate the brand system and their paragraph would otherwise
jump from grey to body colour.

The <p follows a negative lookahead. Without it the pattern also opens on
<path>, which on the one page carrying an SVG social icon meant the match ran
from a path element through the Ko-fi icon and swallowed the whole footer.

Idempotent.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BODY = (
    'Everything the lab builds in public stays in public. The source is on '
    '<a href="https://github.com/M-Ashrey">GitHub</a>, and the current build is '
    'a <a href="https://theagentlab.site/">live AI quoting engine</a> for home '
    'service contractors.'
)

PARA = re.compile(
    r'<p(?![a-zA-Z])(?P<attrs>[^>]*)>(?:(?!</p>).){0,1200}?ko-fi\.com'
    r'(?:(?!</p>).){0,1200}?</p>',
    re.S,
)

NAV_KOFI = re.compile(
    r'<a href="https://ko-fi\.com/[^"]*" class="nav-cta"[^>]*>[^<]*</a>'
)


def main() -> int:
    touched = []
    for path in sorted(ROOT.rglob("*.html")):
        text = original = path.read_text(encoding="utf-8")
        hits = []

        n_nav = len(NAV_KOFI.findall(text))
        if n_nav:
            text = NAV_KOFI.sub(
                '<a href="/#founding" class="nav-cta">Review The Math</a>', text
            )
            hits.append(f"nav-cta x{n_nav}")

        def repl(m: re.Match) -> str:
            return f'<p{m.group("attrs")}>{BODY}</p>'

        text, n_para = PARA.subn(repl, text)
        if n_para:
            hits.append(f"cta-para x{n_para}")

        if text != original:
            path.write_text(text, encoding="utf-8")
            touched.append((path.relative_to(ROOT).as_posix(), hits))

    for name, hits in touched:
        print(f"  {name}: {', '.join(hits)}")
    print(f"{len(touched)} file(s) updated")

    left = [
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*.html")
        if "ko-fi.com" in p.read_text(encoding="utf-8")
    ]
    if left:
        print("still referencing ko-fi (needs a hand pass):")
        for name in left:
            print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
