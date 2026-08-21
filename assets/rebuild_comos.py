#!/usr/bin/env python3
"""Rebuild the one blog post that never made it into the brand system.

blog/2026-08-10-comos-federation/ was published with its own hand-rolled
stylesheet: teal links, a 760px measure, no nav, no footer, no canonical and
no favicon. It is also the only page on the site with no <style id="brand-core">
block, which means the brand checker has nothing to check. It links to
https://theagentlab.site/mcp-doctor/, which does not exist in this repo and
returns a 404.

Rather than hand-copy 1800 lines of inlined CSS, the head is lifted from a
post that is already correct and the metadata swapped. Run brand_inline.py
afterwards like any other page.

Content is preserved. Em dashes are replaced with ordinary punctuation and the
dead internal link is repointed at the public repo.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "blog" / "2026-08-08-claude-code-sessions-talk" / "index.html"
TARGET = ROOT / "blog" / "2026-08-10-comos-federation" / "index.html"

SLUG = "2026-08-10-comos-federation"
URL = f"https://theagentlab.site/blog/{SLUG}/"
TITLE = "ComOS Federation: One MCP Gateway for Every AI Commerce Store"
DESC = (
    "ComOS Federation is a multi-tenant MCP gateway that replaces per-platform "
    "commerce integrations with a single connection. What it does, how the "
    "virtual context routing works, and what it costs you to adopt."
)

BODY = """<body>

<a class="skip-link" href="#main">Skip to content</a>

<nav class="nav-bar">
  <a class="nav-wordmark" href="/">The Agent <span>Lab</span></a>
  <ul class="nav-links">
    <li><a href="/services/">The Engine</a></li>
    <li><a href="/ai/">Who We Build For</a></li>
    <li><a href="/kits/">Kits</a></li>
    <li><a href="/blog/">Blog</a></li>
  </ul>
  <a href="/#founding" class="nav-cta">Review The Math</a>
</nav>

<main id="main">
<div class="page-container">

  <header class="article-head">
    <span class="eyebrow">The Agent Lab</span>
    <h1 class="article-title">ComOS Federation: One MCP Gateway for Every AI Commerce Store</h1>
    <p class="dek">Every store, marketplace and platform ships its own API with its own quirks. ComOS Federation puts one MCP gateway in front of all of them, so you write a single integration instead of one per backend.</p>
    <p class="updated">Ashrey &middot; August 10, 2026</p>
  </header>

  <article class="prose">
<p class="lede">AI commerce is fragmented. Every store, marketplace and platform has its own API, its own quirks and its own way of doing things. For anyone building AI powered commerce tools, that means a tangle of integrations, each one a custom project and each one a maintenance cost that never goes away.</p>

<p><a href="https://glama.ai/mcp/connectors/io.github.ronrey/federation">ComOS Federation</a> is an attempt to end that. It is a multi-tenant MCP gateway that lets you connect to every store through a single integration. One connection, every store.</p>

<h2>What it does</h2>

<p>ComOS Federation is an MCP connector that acts as a translator for commerce APIs. It sits between your application and the stores you want to reach, standardising every interaction through the <a href="https://modelcontextprotocol.io">Model Context Protocol</a>. What you get:</p>

<ul>
<li><strong>Unified API.</strong> One interface for every store, whatever the backend is.</li>
<li><strong>MCP native.</strong> Built on the same protocol that Claude, Cursor and most agent tooling already speak.</li>
<li><strong>Multi-tenant.</strong> Multiple stores under a single gateway instance.</li>
<li><strong>Agent first.</strong> Designed for programmatic callers rather than a human clicking through a dashboard.</li>
</ul>

<h2>Why it matters if you build this stuff</h2>

<p>The real cost in commerce tooling is integration sprawl. Instead of writing custom code for Shopify, WooCommerce, BigCommerce and everything else, you write one integration against the gateway and it handles translation into each native API.</p>

<ul>
<li><strong>Faster to ship.</strong> Build once, point it at more stores. No platform specific branch per backend.</li>
<li><strong>Lower maintenance.</strong> When a store changes its API, the translation layer absorbs it and your code does not move.</li>
<li><strong>Wider reach.</strong> Long tail platforms become viable because the marginal cost of adding one is close to zero.</li>
<li><strong>Built for agents.</strong> MCP was designed for programmatic callers, and this brings that model to commerce.</li>
</ul>

<h2>How it works</h2>

<p>ComOS Federation is an MCP server that exposes a virtual context for each store you connect. When your agent talks to a store it is really talking to a virtual MCP context the gateway provisions and manages.</p>

<p>The flow, simplified:</p>

<ol>
<li>Your agent sends an MCP request to the gateway, for example "list products in store A".</li>
<li>The gateway routes it to that store's virtual context.</li>
<li>The virtual context translates the MCP request into the store's native API call.</li>
<li>The response comes back translated into MCP.</li>
</ol>

<p>Your agent only ever sees MCP. The store only ever sees its own API. Translation happens in the middle.</p>

<h2>Getting started</h2>

<p>ComOS Federation ships as a <a href="https://glama.ai/mcp/connectors/io.github.ronrey/federation">Glama.ai MCP connector</a>. To wire it in:</p>

<ol>
<li><strong>Install the connector</strong> on your Glama.ai MCP server.</li>
<li><strong>Configure your stores</strong> in the ComOS Federation dashboard.</li>
<li><strong>Point your agent</strong> at the gateway and start sending requests.</li>
</ol>

<p>The <a href="https://glama.ai/mcp/connectors/io.github.ronrey/federation">connector documentation</a> covers setup step by step. If you are new to MCP and want to check your own server before you add another moving part, <a href="https://github.com/M-Ashrey/mcp-doctor">mcp-doctor</a> is open source, zero dependency and audits spec compliance for you.</p>

<h2>The honest caveat</h2>

<p>A gateway in the middle is a gateway you now depend on. Everything you gain in integration cost you pay back in a single point of failure and in latency on every call. That trade is usually worth it when you are talking to five platforms and clearly not worth it when you are talking to one. Count your backends before you adopt it.</p>

<div class="backBottom"><a href="/blog/">Back to the blog</a></div>
  </article>

</div>
</main>
"""


def main() -> int:
    if not TEMPLATE.exists():
        sys.exit(f"template missing: {TEMPLATE}")
    src = TEMPLATE.read_text(encoding="utf-8")

    head = src[: src.index("</head>") + len("</head>")]
    tail = src[src.index("<footer class=\"footer\">") :]

    # Swap the template's own metadata out for this post's.
    head = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", head, flags=re.S)
    head = re.sub(
        r'(<meta name="description" content=")[^"]*(")', rf"\1{DESC}\2", head
    )
    head = re.sub(
        r'(<meta property="og:title" content=")[^"]*(")', rf"\1{TITLE}\2", head
    )
    head = re.sub(
        r'(<meta property="og:description" content=")[^"]*(")', rf"\1{DESC}\2", head
    )
    head = re.sub(
        r'(<meta name="twitter:title" content=")[^"]*(")', rf"\1{TITLE}\2", head
    )
    head = re.sub(
        r'(<meta name="twitter:description" content=")[^"]*(")', rf"\1{DESC}\2", head
    )
    head = re.sub(
        r'(<meta property="og:image:alt" content=")[^"]*(")',
        r"\1ComOS Federation, one MCP gateway in front of every commerce backend\2",
        head,
    )
    head = re.sub(
        r'(<meta property="og:site_name" content=")[^"]*(")',
        r"\1The Agent Lab\2",
        head,
    )
    head = head.replace("2026-08-08-claude-code-sessions-talk", SLUG)
    head = head.replace("2026-08-08T12:40:00+02:00", "2026-08-10T00:00:00+02:00")
    head = head.replace('"datePublished": "2026-08-08"', '"datePublished": "2026-08-10"')
    head = head.replace('"dateModified": "2026-08-08"', '"dateModified": "2026-08-10"')
    head = re.sub(
        r'("headline": ")[^"]*(")', rf"\1{TITLE}\2", head
    )
    head = re.sub(
        r'("description": ")[^"]*(")', rf"\1{DESC}\2", head
    )

    # The template post has an og.png; this one does not, so drop the image
    # claims rather than point a social card at a 404.
    head = re.sub(r'<meta property="og:image[^>]*>\n?', "", head)
    head = re.sub(r'<meta name="twitter:image"[^>]*>\n?', "", head)
    head = re.sub(r'\s*"image": "[^"]*",\n', "\n", head)
    head = head.replace(
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:card" content="summary">',
    )

    out = f"{head}\n{BODY}\n{tail}"
    if "—" in out:
        sys.exit("em dash survived the rebuild")
    TARGET.write_text(out, encoding="utf-8")
    print(f"wrote {TARGET.relative_to(ROOT).as_posix()} ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
