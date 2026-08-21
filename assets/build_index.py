#!/usr/bin/env python3
"""Rebuild the blog archive list and sitemap.xml from what is actually on disk.

The site had drifted into two separate problems that share one cause: nothing
generated either list, so both were maintained by hand and both fell behind.

  - /blog/ linked 4 of the 8 posts under blog/<slug>/ and 8 of the 11 under
    blog/posts/. Seven published posts were reachable only by guessing the URL.
  - sitemap.xml listed 11 legacy blog/posts/*.html files, zero of the newer
    blog/<slug>/ directories, and no /kits/ index at all. It also listed
    /kits/thanks/, which is noindex.

So both are generated from one walk of the tree now. Titles come from each
page's own <h1 class="article-title">, deks from its meta description, dates
from the filename prefix. Run this after adding a post.

Two pages are deliberately excluded:

  - blog/2026-08-08-claude-code-cross-session-messaging/ is the same story as
    blog/2026-08-08-claude-code-sessions-talk/, published two minutes apart and
    self-canonical. Two URLs competing for one query is worse than one. The
    orphan gets a canonical pointing at the linked twin and stays out of both
    lists.
  - anything carrying <meta name="robots" content="noindex">.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://theagentlab.site"
TODAY = "2026-08-21"

DUPLICATE = "blog/2026-08-08-claude-code-cross-session-messaging/index.html"
CANONICAL_TWIN = f"{BASE}/blog/2026-08-08-claude-code-sessions-talk/"

MONTHS = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December",
}

# Most posts carry the brand shell and its .article-title heading. Two of the
# August posts were hand authored with a bare <h1> and no brand CSS at all, and
# a generator that walks the tree should read what is there rather than insist
# on a class. Falls back to the first <h1> of any kind.
H1 = re.compile(r'<h1 class="article-title">(.*?)</h1>', re.S)
H1_ANY = re.compile(r"<h1(?:\s[^>]*)?>(.*?)</h1>", re.S)
DESC = re.compile(r'<meta name="description" content="([^"]*)"')
TAGS = re.compile(r"<[^>]+>")

# Static pages, in the order they should appear, with their sitemap weights.
STATIC = [
    ("/", "monthly", "1.0"),
    ("/services/", "monthly", "0.9"),
    ("/ai/", "monthly", "0.9"),
    ("/kits/", "monthly", "0.7"),
    ("/kits/a09-mcp-audit/", "monthly", "0.7"),
    ("/kits/a01-kindle-ebooks/", "monthly", "0.7"),
    ("/blog/", "daily", "0.8"),
    ("/terms/", "yearly", "0.3"),
    ("/refunds/", "yearly", "0.4"),
    ("/privacy/", "yearly", "0.3"),
]


def text_of(fragment: str) -> str:
    return html.unescape(TAGS.sub("", fragment)).strip()


def collect() -> list[dict]:
    posts = []
    paths = sorted(ROOT.glob("blog/*/index.html")) + sorted(ROOT.glob("blog/posts/*.html"))
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        if rel == DUPLICATE:
            continue
        body = path.read_text(encoding="utf-8")
        if 'name="robots" content="noindex"' in body:
            continue

        stem = path.parent.name if path.name == "index.html" else path.stem
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})-", stem)
        if not m:
            sys.exit(f"no date prefix on {rel}")
        y, mo, d = m.groups()

        h1 = H1.search(body) or H1_ANY.search(body)
        desc = DESC.search(body)
        if not h1 or not desc:
            sys.exit(f"missing h1 or description in {rel}")

        url = (
            f"/blog/{path.parent.name}/"
            if path.name == "index.html"
            else f"/blog/posts/{path.name}"
        )
        posts.append(
            {
                "iso": f"{y}-{mo}-{d}",
                "pretty": f"{MONTHS[mo]} {int(d)}, {y}",
                "url": url,
                "title": text_of(h1.group(1)),
                "dek": html.unescape(desc.group(1)),
            }
        )
    posts.sort(key=lambda p: (p["iso"], p["url"]), reverse=True)
    return posts


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_index(posts: list[dict]) -> None:
    path = ROOT / "blog" / "index.html"
    body = path.read_text(encoding="utf-8")
    items = "\n".join(
        f'<li class="post"><a href="{p["url"]}">'
        f'<span class="post-date">{p["pretty"]}</span>'
        f'<span class="post-title">{esc(p["title"])}</span>'
        f'<span class="post-dek">{esc(p["dek"])}</span></a></li>'
        for p in posts
    )
    block = f"<!-- POSTS:START -->\n{items}\n<!-- POSTS:END -->"
    new = re.sub(
        r"<!-- POSTS:START -->.*?<!-- POSTS:END -->", lambda _: block, body, flags=re.S
    )
    if new == body:
        print("  blog/index.html: unchanged")
    else:
        path.write_text(new, encoding="utf-8")
        print(f"  blog/index.html: {len(posts)} post(s) listed")


def write_sitemap(posts: list[dict]) -> None:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, freq, pri in STATIC:
        lines.append(
            f"  <url><loc>{BASE}{loc}</loc><lastmod>{TODAY}</lastmod>"
            f"<changefreq>{freq}</changefreq><priority>{pri}</priority></url>"
        )
    for p in posts:
        lines.append(
            f'  <url><loc>{BASE}{p["url"]}</loc><lastmod>{p["iso"]}</lastmod>'
            f"<changefreq>monthly</changefreq><priority>0.7</priority></url>"
        )
    lines.append("</urlset>")
    out = "\n".join(lines) + "\n"
    (ROOT / "sitemap.xml").write_text(out, encoding="utf-8")
    print(f"  sitemap.xml: {len(STATIC)} page(s) + {len(posts)} post(s)")


def fix_duplicate() -> None:
    path = ROOT / DUPLICATE
    body = path.read_text(encoding="utf-8")
    new = re.sub(
        r'(<link rel="canonical" href=")[^"]*(")',
        rf"\1{CANONICAL_TWIN}\2",
        body,
        count=1,
    )
    if new == body:
        print("  duplicate: canonical already pointed at the twin")
        return
    path.write_text(new, encoding="utf-8")
    print(f"  {DUPLICATE}: canonical repointed at the linked twin")


def main() -> int:
    posts = collect()
    write_index(posts)
    write_sitemap(posts)
    fix_duplicate()
    if (ROOT / "kits" / "thanks" / "index.html").exists():
        sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        assert "/kits/thanks/" not in sm, "noindex page leaked into the sitemap"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
