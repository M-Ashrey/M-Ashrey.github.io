#!/usr/bin/env python3
"""One shape for the foot of every post: the closing note, then the back link.

Twenty-two posts, written over four weeks, ended four different ways. The
closing note appeared as a bare `<p>` after a bare `<hr>` on nine of them, as
`<p style="font-size:0.95rem;color:#888">` after an `<hr>` with a hardcoded
`#222` top border on two, and as the system's own `<p class="fine endnote">` on
three. The back link had eight spellings across eighteen pages and was missing
from four. So the last thing a reader saw was different on almost every post.

Both components already exist in assets/brand.css and neither needed inventing:

  .fine.endnote   13.5px tertiary text, 68ch measure, and its own 1px subtle
                  top rule with 20px of padding above it. That rule is the <hr>,
                  which is why the <hr> goes: two separators stacked.

  .prose .backBottom   48px top margin, its own top rule, 14px secondary link.

The `#222` and `#888` pairs were the last hardcoded colours in body prose. Both
sat a little brighter than the tokens they were standing in for.

Every note also linked the phrase "live AI quoting engine" at
https://theagentlab.site/, an absolute link to the site's own root, which sent
the reader to the landing page rather than the engine spec. It is /services/ now
and it stays a relative route, so it works the same on a local server.

Two exceptions, both deliberate:

  blog/2026-08-13-claude-code-auto-mode-default and
  blog/2026-08-13-managed-agents-multiagent carry no brand-core block, so
  `.fine` and `.backBottom` would resolve to nothing there. They get the link
  fix only. They need rebuilding onto the shell before they can take the rest.

  blog/2026-08-21-anthropic-ipo-agent-ecosystem writes its own closing note
  rather than the shared one. Only its back link is missing, so that is all this
  adds.

Idempotent. Reruns find nothing to do.

    python assets/post_foot.py
    python assets/post_foot.py --check    # exit 1 if any post is off shape
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = '<style id="brand-core">'

# The one closing note, and the one back link. Both single line, because that is
# how the seven posts under blog/posts/ already spell them.
NOTE = (
    '<p class="fine endnote">Everything the lab builds in public stays in public.'
    ' The source is on <a href="https://github.com/M-Ashrey">GitHub</a>, and the'
    ' current build is a <a href="/services/">live AI quoting engine</a> for home'
    " service contractors.</p>"
)
BACK = '<div class="backBottom"><a href="/blog/">&larr; All posts</a></div>'

# `&larr;` rather than a literal U+2190. The same reason assets/rewrite_cta.py
# gives for its own arrows: the glyph is invisible in a terminal diff, it is one
# bad save away from mojibake, and half these files already had it entity
# encoded. The entity is what renders either way.

# The note, in every shape it was written in, plus the separator above it. The
# <hr> is optional because two posts never had one.
NOTE_RE = re.compile(
    r"(?:[ \t]*<hr[^>]*>[ \t]*\n)?"
    r"([ \t]*)<p[^>]*>Everything the lab builds in public[\s\S]*?</p>"
)

# Every spelling of the back link, collapsed. The label varied, the route never
# did, so the route is the anchor for the match.
BACK_RE = re.compile(
    r"[ \t]*<div class=\"backBottom\">\s*<a href=\"/blog/\">.*?</a>\s*</div>", re.S
)

LINK_OLD = '<a href="https://theagentlab.site/">live AI quoting engine</a>'
LINK_NEW = '<a href="/services/">live AI quoting engine</a>'

# Where the back link goes when a post has none: last child of the prose. The
# indent matches the seventeen posts that already carry one.
CLOSE = "\n  </article>"
INDENT = "    "

# Posts that are not on the shell. See the docstring.
BESPOKE = (
    "blog/2026-08-13-claude-code-auto-mode-default/index.html",
    "blog/2026-08-13-managed-agents-multiagent/index.html",
)


def posts() -> list[Path]:
    """Every blog post. Not the index, and not the pages that only look like it.

    `.prose` is on thirty-five pages, including the legal pages and the waitlist
    confirmation. An "All posts" link belongs on none of those.
    """
    out = []
    for path in sorted((ROOT / "blog").rglob("*.html")):
        if path.name == "index.html" and path.parent == ROOT / "blog":
            continue
        out.append(path)
    return out


def fix(path: Path) -> str | None:
    text = original = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    head, sep, body = text.partition("</head>")

    if rel in BESPOKE:
        body = body.replace(LINK_OLD, LINK_NEW)
        return None if head + sep + body == original else _write(path, head + sep + body)

    if CORE not in head:
        return None

    body = NOTE_RE.sub(lambda m: m.group(1) + NOTE, body, count=1)

    if BACK_RE.search(body):
        body = BACK_RE.sub(INDENT + BACK, body, count=1)
    elif CLOSE in body:
        # Straight before the tag that closes the prose, so it lands inside the
        # scope its rules need.
        before, _, after = body.rpartition(CLOSE)
        body = before + "\n\n" + INDENT + BACK + CLOSE + after

    text = head + sep + body
    return None if text == original else _write(path, text)


def _write(path: Path, text: str) -> str:
    path.write_text(text, encoding="utf-8")
    return path.relative_to(ROOT).as_posix()


def audit() -> list[str]:
    """What is still off shape, said in the terms the docstring uses."""
    bad = []
    for path in posts():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        body = text.partition("</head>")[2]
        if LINK_OLD in body:
            bad.append(f"{rel}: still links the site root")
        if rel in BESPOKE or CORE not in text:
            continue
        if "Everything the lab builds in public" in body and NOTE not in body:
            bad.append(f"{rel}: closing note is not .fine.endnote")
        if BACK not in body:
            bad.append(f"{rel}: back link missing or off label")
    return bad


def main() -> int:
    check = "--check" in sys.argv
    if not check:
        for path in posts():
            done = fix(path)
            if done:
                print(f"wrote   {done}")

    bad = audit()
    for line in bad:
        print(f"OFF     {line}")
    print(f"\n{len(posts())} post(s), {len(bad)} off shape")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
