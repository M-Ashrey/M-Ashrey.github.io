#!/usr/bin/env python3
"""Rehome the posts whose private stylesheet was labelled `brand-core`.

Five posts arrived from the remote carrying a <style id="brand-core"> block that
was not brand.css. It was page specific CSS wearing the canonical id, between
8.6 and 12.9 KB of it, and on some pages it defined the only rules their chrome
had: .nav-inner, .nav-brand, .article-header, .footer-grid on one, .bar, .mark,
.artHead, .byline on another, .site-footer and .social-links on a third.

assets/brand_inline.py could not tell that apart from a stale stamp. It found
the id, replaced the contents with current brand.css, and every rule those pages
depended on went with it. --check then passed, because the block really was byte
identical to brand.css by that point. Two of the five rendered as unstyled
documents on a dark background. The other three kept their chrome, because their
nav and footer already used system names, and lost their article body instead.

brand_inline.py now refuses to overwrite a block that does not look like an
older brand.css, so the same mistake cannot repeat. This script cleans up after
the one time it did.

Reverting is not an option. These pages carry the rewritten CTA, the removed
Ko-fi ask and the new footer copy, and those are the point of the pivot. So the
markup moves onto the shell instead, which is where the other 31 pages already
are. After this the private vocabulary is gone and the stamp is honest.

What changes, and why that particular direction:

  .article-body, .article-content -> .prose
      Duplicates. .prose is the same component with 39 rules behind it and 28
      pages already using it. The paragraphs are all direct children, so the
      `.prose > p` child selector reaches every one of them.

  .article-meta
      Kept, and promoted into brand.css instead. It is not a duplicate of
      .updated: that is a revision stamp above the title, this is a bordered
      byline under the dek. Five pages use it and it now has one definition.

  bespoke heads and footers -> the canonical shell
      Lifted out of index.html so there stays one copy of the truth.

Two off palette inline styles go at the same time, a #222 rule and #888 body
text, which are the last hardcoded colours outside the token set. So does the
old footer tagline on the OJCP post, which still described the site as notes on
Claude and MCP.

Idempotent. Reruns find nothing to do. Run assets/brand_inline.py afterwards.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

BENCH = ROOT / "blog/2026-08-20-opus-5-benchmark-trap/index.html"
FAKEGIT = ROOT / "blog/2026-08-19-ai-agents-supply-chain-phishing-fakegit/index.html"
OJCP = ROOT / "blog/2026-08-12-ojcp-open-job-context-protocol/index.html"
FILESYS = ROOT / "blog/2026-08-16-ai-coding-filesystem-problem/index.html"
IPO = ROOT / "blog/2026-08-21-anthropic-ipo-agent-ecosystem/index.html"

TOUCHED = (BENCH, FAKEGIT, OJCP, FILESYS, IPO)

# Names that only ever existed in those private stylesheets. If one survives the
# rewrite, some markup is still pointing at CSS that is gone. Written as full
# attribute fragments where a bare name would collide with a real system class:
# `nav-link` is a substring of the canonical `nav-links`, and `wordmark` is a
# substring of both `nav-wordmark` and `footer-wordmark`.
ORPHANS = (
    'class="nav"', 'class="nav-inner"', 'class="nav-brand"', 'class="nav-link"',
    'class="article-header"', 'class="article-dek"', 'class="article-cta"',
    'class="article-body"', 'class="article-content"',
    'class="site-footer"', 'class="footer-grid"', 'class="footer-links"',
    'class="footer-bottom"', 'class="social-links"', 'class="wordmark"',
    'class="footer-logo"', 'class="footer-tagline"', 'class="footer-link"',
    'class="footer-nav-title"', 'class="footer-meta"',
    'class="artHead', 'class="byline"', 'class="dot"',
    'class="bar"', 'class="mark"', 'class="wrap"', 'footer class="site',
    "reveal",
)


def canonical(pattern: str, label: str) -> str:
    """Lift a shell block out of index.html so there is one copy of the truth."""
    src = INDEX.read_text(encoding="utf-8")
    m = re.search(pattern, src, re.S)
    if not m:
        sys.exit(f"could not read the canonical {label} out of index.html")
    return m.group(0)


def swap(text: str, old: str, new: str, path: Path, label: str) -> str:
    if old not in text:
        sys.exit(f"{path.parent.name}: could not find the {label} block to replace")
    if text.count(old) != 1:
        sys.exit(f"{path.parent.name}: {label} appears {text.count(old)} times")
    return text.replace(old, new)


def cut(text: str, pattern: str, new: str, path: Path, label: str) -> str:
    m = re.search(pattern, text, re.S)
    if not m:
        sys.exit(f"{path.parent.name}: no {label} found")
    return text.replace(m.group(0), new)


# --------------------------------------------------------------------------
# Per page chrome surgery. Each guards on the shape it is about to create.
# --------------------------------------------------------------------------

def do_bench(nav: str, footer: str) -> bool:
    text = original = BENCH.read_text(encoding="utf-8")
    if 'class="nav-bar"' in text:
        return False

    text = swap(
        text,
        '<a href="#main" class="skip-link">Skip to main content</a>',
        '<a class="skip-link" href="#main">Skip to content</a>',
        BENCH,
        "skip link",
    )
    text = cut(text, r'<nav class="nav" role="navigation".*?</nav>', nav, BENCH, "bespoke nav")

    # The head listed the date above the title and used its own dek class. The
    # system puts the title first and the meta line under the dek.
    text = swap(
        text,
        """<main id="main" class="page-narrow">
  <article>
    <header class="article-header">
      <div class="article-meta">
        <time datetime="2026-08-20">August 20, 2026</time>
        <span>By Ashrey</span>
      </div>
      <h1 class="article-title">Opus 5's Benchmark Trap: Why the "Best" Model Feels Worse to Use</h1>
      <p class="article-dek">Opus 5 scores higher on benchmarks but feels worse for daily coding. The reason: benchmarks reward bold assumptions; real engineering punishes them.</p>
    </header>

    <div class="article-body">""",
        """<main id="main">
<div class="page-narrow">

  <header class="article-head">
    <span class="eyebrow">Claude &middot; Opus 5 &middot; Coding agents</span>
    <h1 class="article-title">Opus 5's Benchmark Trap: Why the "Best" Model Feels Worse to Use</h1>
    <p class="dek">Opus 5 scores higher on benchmarks but feels worse for daily coding. The reason: benchmarks reward bold assumptions; real engineering punishes them.</p>
    <div class="article-meta">
      <time datetime="2026-08-20">August 20, 2026</time>
      <span>By Ashrey</span>
    </div>
  </header>

  <article class="prose">""",
        BENCH,
        "article head",
    )

    # The hr and the grey paragraph were both hardcoded hex. The system already
    # has a quiet closing note, and the outbound link to the site root becomes
    # the internal route it was standing in for.
    text = swap(
        text,
        """    </div>

    <div class="article-cta">
      <hr style="margin:2.5rem 0 1.5rem;border:none;border-top:1px solid #222">
      <p style="font-size:0.95rem;color:#888">Everything the lab builds in public stays in public. The source is on <a href="https://github.com/M-Ashrey">GitHub</a>, and the current build is a <a href="https://theagentlab.site/">live AI quoting engine</a> for home service contractors.</p>
    </div>
  </article>
</main>""",
        """  </article>

  <p class="fine endnote">Everything the lab builds in public stays in public. The source is on <a href="https://github.com/M-Ashrey">GitHub</a>, and the current build is a <a href="/services/">live AI quoting engine</a> for home service contractors.</p>

  <div class="backBottom">
    <a href="/blog/">Back to all posts</a>
  </div>

</div>
</main>""",
        BENCH,
        "article tail",
    )
    text = cut(
        text, r'<footer class="footer page-container">.*?</footer>', footer, BENCH, "bespoke footer"
    )

    BENCH.write_text(text, encoding="utf-8")
    return text != original


def do_fakegit(nav: str, footer: str) -> bool:
    text = original = FAKEGIT.read_text(encoding="utf-8")
    if 'class="nav-bar"' in text:
        return False

    text = cut(
        text,
        r'  <div class="bar">.*?\n  </div>\n',
        '\n<a class="skip-link" href="#main">Skip to content</a>\n\n' + nav + "\n",
        FAKEGIT,
        "bespoke bar",
    )
    text = swap(text, '<body>\n<div class="wrap">\n', "<body>\n", FAKEGIT, "wrapper open")
    text = swap(
        text,
        """  <main>
  <header class="artHead reveal">""",
        """<main id="main">
<div class="page-narrow">

  <header class="article-head">""",
        FAKEGIT,
        "main open",
    )
    text = swap(
        text,
        "    <h1>AI Agents Have a Supply-Chain Phishing Problem</h1>",
        '    <h1 class="article-title">AI Agents Have a Supply-Chain Phishing Problem</h1>',
        FAKEGIT,
        "h1",
    )
    text = swap(
        text,
        """    <div class="byline">
      <span>2026-08-19</span>
      <span class="dot"></span>
      <span>Ashrey</span>
    </div>""",
        """    <div class="article-meta">
      <time datetime="2026-08-19">August 19, 2026</time>
      <span>By Ashrey</span>
    </div>""",
        FAKEGIT,
        "byline",
    )
    text = swap(text, '<article class="prose reveal">', '<article class="prose">', FAKEGIT, "prose")
    text = swap(
        text, '<div class="backBottom reveal">', '<div class="backBottom">', FAKEGIT, "back link"
    )
    text = swap(text, "  </main>\n", "</div>\n</main>\n", FAKEGIT, "main close")
    text = cut(
        text,
        r'  <footer class="site reveal">.*?</footer>\n\n</div>\n',
        "\n" + footer + "\n",
        FAKEGIT,
        "bespoke footer",
    )

    # Nothing carries .reveal any more, so the observer that reveals it is dead
    # weight that would keep the class alive for the next person reading this.
    text = cut(
        text,
        r"<script>\ndocument\.documentElement\.classList\.add\('js'\);.*?</script>\n",
        "",
        FAKEGIT,
        "reveal observer",
    )

    FAKEGIT.write_text(text, encoding="utf-8")
    return text != original


def do_ojcp(footer: str) -> bool:
    """Nav is already canonical here. The head, the tail and the footer are not.

    The nav keeps its own markup rather than taking the lifted copy: it uses a
    div of anchors where index.html uses a list, `.nav-links` is a flex box with
    list-style none either way, and the div version carries an aria-current the
    canonical one does not.
    """
    text = original = OJCP.read_text(encoding="utf-8")
    if 'class="article-head"' in text:
        return False

    text = swap(
        text,
        """<main id="main">
<article>
  <header class="article-header">
    <div class="article-meta">
      <time datetime="2026-08-12">2026-08-12</time>
      <span aria-hidden="true">·</span>
      <span>By Ashrey</span>
    </div>
    <h1 class="article-title">OJCP — The Open Standard for Agent-Consumable Job Feeds</h1>""",
        """<main id="main">
<div class="page-narrow">

  <header class="article-head">
    <span class="eyebrow">MCP &middot; Open standards &middot; Agent infrastructure</span>
    <h1 class="article-title">OJCP — The Open Standard for Agent-Consumable Job Feeds</h1>""",
        OJCP,
        "article head open",
    )
    text = swap(
        text,
        '    <p class="article-dek">OJCP defines how',
        '    <p class="dek">OJCP defines how',
        OJCP,
        "dek",
    )
    text = swap(
        text,
        """  </header>

  <div class="article-body">""",
        """    <div class="article-meta">
      <time datetime="2026-08-12">August 12, 2026</time>
      <span>By Ashrey</span>
    </div>
  </header>

  <article class="prose">""",
        OJCP,
        "article body open",
    )
    text = swap(
        text,
        """  </div>

  <div class="article-cta">
    <p class="fine endnote">Everything the lab builds in public stays in public. The source is on <a href="https://github.com/M-Ashrey">GitHub</a>, and the current build is a <a href="/">live AI quoting engine</a> for home service contractors.</p>
  </div>
</article>
</main>""",
        """  </article>

  <p class="fine endnote">Everything the lab builds in public stays in public. The source is on <a href="https://github.com/M-Ashrey">GitHub</a>, and the current build is a <a href="/services/">live AI quoting engine</a> for home service contractors.</p>

  <div class="backBottom">
    <a href="/blog/">Back to all posts</a>
  </div>

</div>
</main>""",
        OJCP,
        "article tail",
    )
    text = cut(
        text,
        r'<footer class="site-footer" role="contentinfo">.*?</footer>',
        footer,
        OJCP,
        "bespoke footer",
    )

    OJCP.write_text(text, encoding="utf-8")
    return text != original


# --------------------------------------------------------------------------
# Shared cleanup. Runs over every touched page, including the ones whose chrome
# was already canonical and only lost their body container.
# --------------------------------------------------------------------------

RENAMES = (
    ('class="article-body"', 'class="prose"'),
    ('class="article-content"', 'class="prose"'),
    # The nav is lifted verbatim out of index.html, where the founding anchor is
    # on the page itself. Anywhere else it has to be an absolute route.
    ('<a href="#founding" class="nav-cta">', '<a href="/#founding" class="nav-cta">'),
)

# Three of the five spelled the byline as bare spans around a literal middot.
# `.article-meta` is a flex row with a 24px gap, so the separator was doing work
# the layout already does, and a plain span throws away a machine readable date.
# One shape for all five: a <time> element and the author.
BYLINES = {
    "2026-08-19": ("August 19, 2026", "Ashrey"),
    "2026-08-20": ("August 20, 2026", "By Ashrey"),
    "2026-08-21": ("August 21, 2026", "By Ashrey"),
}

# Same byline, three spellings of the author across the five pages. Professional
# casing, one form.
AUTHORS = ("<span>by Ashrey</span>", "<span>Ashrey</span>")
AUTHOR = "<span>By Ashrey</span>"


def one_byline(body: str, path: Path) -> str:
    for iso, (pretty, author) in BYLINES.items():
        if not path.parent.name.startswith(iso):
            continue
        body = body.replace(
            f"""<div class="article-meta">
      <span>{pretty}</span>
      <span>&middot;</span>
      <span>{author}</span>
    </div>""",
            f"""<div class="article-meta">
      <time datetime="{iso}">{pretty}</time>
      <span>{author}</span>
    </div>""",
        )
        break
    head, _, rest = body.partition('<article class="prose">')
    for wrong in AUTHORS:
        head = head.replace(wrong, AUTHOR)
    return head + _ + rest


TAIL_OPEN = "  </article>\n\n"
MAIN_CLOSE = "\n</div>\n</main>"


def close_article(body: str) -> str:
    """Move whatever follows the prose inside the article, where the CSS is.

    The rehomes above closed </article> early, which reads naturally but puts
    everything after it out of reach. brand.css scopes the whole tail to the
    article: `.prose .backBottom`, `.prose .ctaBlock`, `.prose .ctaRow`,
    `.prose .ctaItem`. Outside it the back link lost its top rule, its 48px
    margin and its 14px secondary link colour and rendered as a bare sentence,
    and on the fakegit post the entire CTA card lost its panel, its border and
    its two column row. The seven posts under blog/posts/ close the article
    after the tail. Now these do too.

    Anchoring on </article> rather than on the endnote is deliberate. A first
    version keyed off `<p class="fine endnote">` and so skipped fakegit, which
    has no endnote and goes straight from the prose to the CTA.
    """
    if TAIL_OPEN not in body:
        return body
    before, _, rest = body.partition(TAIL_OPEN)
    tail, sep, after = rest.partition(MAIN_CLOSE)
    if not sep:
        return body
    lines = tail.rstrip("\n").split("\n")
    indented = "\n".join(("  " + ln if ln.strip() else ln) for ln in lines)
    return before + indented + "\n  </article>" + sep + after


def normalize(path: Path) -> bool:
    text = original = path.read_text(encoding="utf-8")
    head, body = text.split("</head>", 1)
    for old, new in RENAMES:
        body = body.replace(old, new)
    body = one_byline(body, path)
    body = close_article(body)
    # One .reveal outlived its stylesheet on the CTA wrapper, which is generated
    # by assets/rewrite_cta.py and so sits outside the blocks rehomed above.
    body = body.replace('<div class="ctaBlock reveal">', '<div class="ctaBlock">')
    text = head + "</head>" + body
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    nav = canonical(r'<nav class="nav-bar">.*?</nav>', "nav").replace(
        '<a href="#founding" class="nav-cta">', '<a href="/#founding" class="nav-cta">'
    )
    footer = canonical(r'<footer class="footer">.*?\n</footer>', "footer")
    if "footer-social" not in footer or "Co-Founder" not in footer:
        sys.exit("index.html footer is not the migrated one; fix it first")

    rehomed = {
        BENCH: do_bench(nav, footer),
        FAKEGIT: do_fakegit(nav, footer),
        OJCP: do_ojcp(footer),
    }
    for path in TOUCHED:
        changed = normalize(path) or rehomed.get(path, False)
        print(f"  {path.parent.name}: {'rewritten' if changed else 'already rehomed'}")

    bad = []
    for path in TOUCHED:
        body = path.read_text(encoding="utf-8").split("</head>", 1)[1]
        for orphan in ORPHANS:
            if orphan in body:
                bad.append(f"{path.parent.name}: {orphan}")
    if bad:
        print("\nmarkup still points at deleted CSS:")
        for b in bad:
            print(f"  {b}")
        return 1

    print(f"\n{sum(1 for p in TOUCHED)} page(s) checked, no orphaned class names left")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
