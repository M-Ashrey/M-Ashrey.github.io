#!/usr/bin/env python3
"""Fix the sign-off line on the two bespoke posts.

Both of the hand-built posts close with an inline styled hr and a paragraph
carrying a hardcoded #888 and a rem font size. automation/brand_check.py reads
inline style attributes, so those two lines are graded, and they fail: neither
value is a token and neither matches the tertiary text colour the rest of the
site uses. Replaced with .fine.endnote, which now carries the rule.

The anthropic-ipo post also still asks for Ko-fi money in the first person
singular. Donations were pulled from the footer and the nav, so leaving the ask
buried at the end of one post is the sort of thing that survives a rebrand and
then embarrasses you later.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HR = '    <hr style="margin:2.5rem 0 1.5rem;border:none;border-top:1px solid #222">\n'

EDITS = {
    "blog/2026-08-21-anthropic-ipo-agent-ecosystem/index.html": (
        HR
        + '    <p style="font-size:0.95rem;color:#888">If this was useful, you can '
        '<a href="https://ko-fi.com/ashrey122">support my open-source work on Ko-fi</a> '
        'or check out <a href="https://theagentlab.site/services/">my services</a>.</p>\n',
        '    <p class="fine endnote">Written by Ashrey, Co-Founder of The Agent Lab. '
        "We build live AI quoting engines for home service contractors, and we write up "
        'the infrastructure work along the way. <a href="/services/">The engine spec is '
        "here</a>.</p>\n",
    ),
    "blog/2026-08-12-ojcp-open-job-context-protocol/index.html": (
        HR
        + '    <p style="font-size:0.95rem;color:#888">Everything the lab builds in '
        'public stays in public. The source is on <a href="https://github.com/M-Ashrey">'
        'GitHub</a>, and the current build is a <a href="https://theagentlab.site/">live '
        "AI quoting engine</a> for home service contractors.</p>\n",
        '    <p class="fine endnote">Everything the lab builds in public stays in public. '
        'The source is on <a href="https://github.com/M-Ashrey">GitHub</a>, and the '
        'current build is a <a href="/">live AI quoting engine</a> for home service '
        "contractors.</p>\n",
    ),
}

# The icon comment on the OJCP page still describes a Ko-fi mark that is no
# longer in the markup, which reads as a leftover rather than a note.
COMMENT_OLD = """      <!-- Two marks, both drawn inside the 24 viewBox with real padding. The
           previous set was authored with geometry that ran off canvas, so the
           YouTube frame opened at x=2, ran h20 and then arced past 24 while
           its play wedge sat at x=23, and the Ko-fi cup carried an h-28 run
           inside a 24-unit box. Both rendered clipped. -->
"""
COMMENT_NEW = """      <!-- Both marks are drawn inside the 24 viewBox with real padding. The
           previous set ran off canvas: the YouTube frame opened at x=2, ran
           h20 and arced past 24 while its play wedge sat at x=23, so it
           rendered clipped. -->
"""


def main() -> int:
    for rel, (old, new) in EDITS.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        if new.strip() in text:
            print(f"  {rel}: already done")
            continue
        if old not in text:
            sys.exit(f"{rel}: sign-off block did not match")
        text = text.replace(old, new, 1)
        if "ko-fi" in text.lower() and "ojcp" not in rel:
            sys.exit(f"{rel}: ko-fi survived")
        path.write_text(text, encoding="utf-8")
        print(f"  {rel}: sign-off rewritten")

    ojcp = ROOT / "blog" / "2026-08-12-ojcp-open-job-context-protocol" / "index.html"
    text = ojcp.read_text(encoding="utf-8")
    if COMMENT_OLD in text:
        ojcp.write_text(text.replace(COMMENT_OLD, COMMENT_NEW, 1), encoding="utf-8")
        print("  ojcp: icon comment trimmed")

    hits = sorted(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*.html")
        if "ko-fi" in p.read_text(encoding="utf-8").lower()
    )
    print("ko-fi still present in:" if hits else "no ko-fi anywhere")
    for name in hits:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
