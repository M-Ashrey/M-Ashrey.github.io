#!/usr/bin/env python3
"""One-off migration: push the new nav and footer shell across every page.

The site has 29 HTML files and 26 of them carried a byte-identical nav-links
list and footer-brand block. Hand-editing 26 copies of the same paragraph is
how a site ends up with three different job titles in the footer, so the
canonical blocks are read out of index.html and stamped into the rest.

Also strips the donation surfaces (Ko-fi, GitHub Sponsors) and retargets the
nav CTA at the founding-access anchor, since nothing on the site is for sale
until the payment processor question is settled.

Idempotent. Safe to re-run. Reports per-file what it changed.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NAV_OLD = """<ul class="nav-links">
    <li><a href="/kits/">Kits</a></li>
    <li><a href="/services/">Services</a></li>
    <li><a href="/ai/">AI Practice</a></li>
    <li><a href="/blog/">Blog</a></li>
  </ul>"""

NAV_NEW = """<ul class="nav-links">
    <li><a href="/services/">The Engine</a></li>
    <li><a href="/ai/">Who We Build For</a></li>
    <li><a href="/kits/">Kits</a></li>
    <li><a href="/blog/">Blog</a></li>
  </ul>"""

CTA_OLD = '<a href="/services/" class="nav-cta">Book an Audit</a>'
CTA_NEW = '<a href="/#founding" class="nav-cta">Review The Math</a>'

FOOT_OLD = """<div class="footer-brand">
      <div class="footer-wordmark">The Agent <span>Lab</span></div>
      <p class="footer-line">Automation infrastructure, designed and operated by Ashrey, Chief Architect. One operator commanding a real machine.</p>
    </div>
    <nav class="footer-nav" aria-label="Footer">
      <div class="footer-col">
        <span class="h">Products</span>
        <a href="/kits/">Kits</a>
        <a href="/kits/a09-mcp-audit/">MCP Audit Kit</a>
        <a href="/kits/a01-kindle-ebooks/">Kindle Pipeline</a>
      </div>
      <div class="footer-col">
        <span class="h">Work</span>
        <a href="/services/">Services</a>
        <a href="/ai/">AI Practice</a>
        <a href="/blog/">Blog</a>
      </div>
      <div class="footer-col">
        <span class="h">Open Source</span>
        <a href="https://github.com/M-Ashrey">GitHub</a>
        <a href="https://dev.to/m_ashrey122">dev.to</a>
        <a href="https://github.com/sponsors/M-Ashrey">Sponsor</a>
      </div>
    </nav>"""


def canonical_footer() -> str:
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<div class="footer-brand">.*?</nav>', src, re.S)
    if not m:
        sys.exit("could not read the canonical footer out of index.html")
    block = m.group(0)
    if "Co-Founder" not in block or "footer-social" not in block:
        sys.exit("index.html footer is not the migrated one; fix it first")
    return block


def main() -> int:
    foot_new = canonical_footer()
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if path.name == "index.html" and path.parent == ROOT:
            continue
        text = original = path.read_text(encoding="utf-8")
        hits = []
        if NAV_OLD in text:
            text = text.replace(NAV_OLD, NAV_NEW)
            hits.append("nav-links")
        if CTA_OLD in text:
            text = text.replace(CTA_OLD, CTA_NEW)
            hits.append("nav-cta")
        if FOOT_OLD in text:
            text = text.replace(FOOT_OLD, foot_new)
            hits.append("footer")
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append((path.relative_to(ROOT).as_posix(), hits))

    for name, hits in changed:
        print(f"  {name}: {', '.join(hits)}")
    print(f"{len(changed)} file(s) updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
