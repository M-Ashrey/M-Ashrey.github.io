#!/usr/bin/env python3
"""Rewrite the legacy CTA block at the foot of the older posts.

Those blocks were written when the lab sold generic agent automation in the
first person, and they are the last place on the site that still says so. Each
one carries three problems:

  - "I build AI-agent automations and MCP integrations for a living" is the old
    freelancer positioning, singular and consultative. The lab builds quoting
    engines now and speaks as a company.
  - A free AI readiness scorecard on a Vercel subdomain. It resolves, but no
    first-party page links it any more and "score your site free" is not the
    posture this site takes. It goes.
  - Em dashes and literal arrow glyphs in link text. The arrows were never CSS,
    they were typed into the anchor.

The August posts add a fourth: a "Book an audit" link selling an MCP security
audit, which is a service line the pivot retired.

The hosted scanner at mcp-doctor-cloud.onrender.com is a separate call. DNS
resolves to a live Render origin, but it could not be reached from here, and a
link on eight indexed pages should not depend on a free tier instance that
sleeps. Both scanner links now point at the GitHub repos, which is what the
/ai/ proof list already does. The repo is the durable artifact.

The per-post lead in for the first item is kept, because it is the only part of
these blocks that was ever specific to the post it sits under. The two items
after it are canonical across every post.

The blocks are not indented alike. The July posts nest the row two levels
deeper than the August one, so the indentation is read off the opening tag and
the replacement is built to match rather than assumed.

Idempotent: reruns find nothing to replace.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MCP_DOCTOR = "https://github.com/M-Ashrey/mcp-doctor"
STARTER_KIT = "https://github.com/M-Ashrey/claude-mcp-starter-kit"

# Anything in this list means a page still carries pre-pivot CTA copy.
STALE = (
    "ai-readiness-scorecard",
    "onrender.com",
    "I build AI-agent",
    "Book an audit",
    "MCP Security Audit",
)

# Keyed on the path relative to the repo root. The first item keeps its own
# heading and its own reason for existing on that particular post. Everything
# after it is the same everywhere.
LEAD = {
    "blog/posts/2026-07-24-claude-opus-5-what-matters-for-agent-builders.html": (
        "Audit your MCP servers before you trust them with a more capable model",
        "Run the open source CLI against your own servers before you hand a "
        "smarter model a wider tool surface. MIT licensed, runs locally, runs "
        "in CI.",
    ),
    "blog/posts/2026-07-25-mcp-goes-stateless-july-28.html": (
        "Audit your MCP servers before the spec lands",
        "Catch the compliance problems while you still have time to fix them "
        "quietly. The CLI runs against a local server or in your own pipeline.",
    ),
    "blog/posts/2026-07-25-sharedroot-claude-cowork-sandbox-escape.html": (
        "Audit your MCP servers and agent toolchain",
        "SharedRoot is a sandbox story. Your MCP servers are a separate "
        "surface with its own failure modes. The CLI checks spec compliance "
        "and configuration before either one becomes an incident.",
    ),
    "blog/posts/2026-07-26-context-engineering-claude-5-unhobbling.html": (
        "Audit your MCP server configurations",
        "While you are trimming the system prompt, it is worth reading what "
        "your MCP servers are actually advertising into it. The CLI reports the "
        "tool surface and the config problems.",
    ),
    "blog/posts/2026-07-27-claude-code-pretooluse-hooks-enforcement.html": (
        "Audit your MCP server configurations",
        "Hooks stop the call. The CLI tells you what was reachable in the "
        "first place. Worth running once while you have the config open.",
    ),
    "blog/posts/2026-07-28-robots-txt-vs-noindex-claude-chats.html": (
        "Audit your MCP server configurations",
        "Before you ship anything that mints public URLs, check what your MCP "
        "servers expose. The CLI runs locally and nothing leaves your machine.",
    ),
    "blog/posts/2026-07-29-ai-coding-agents-silo-teams.html": (
        "Check your MCP server security",
        "Before you run agent workflows at team scale, make sure your servers "
        "are spec compliant and not handing out more than the job needs.",
    ),
    "blog/2026-08-19-ai-agents-supply-chain-phishing-fakegit/index.html": (
        "Audit the MCP servers you did not write",
        "Eight hundred fake servers is a supply chain problem, and the only "
        "defence is reading what a server actually does before you trust it. "
        "The open source CLI checks spec compliance and the tool surface a "
        "server advertises. Runs locally, runs in CI.",
    ),
}

OPEN = re.compile(r'^([ \t]*)<div class="ctaRow">$', re.M)


def block_pattern(indent: str) -> re.Pattern:
    """The row runs to its own closing tag, then the ctaBlock's, one level out."""
    outer = indent[:-2] if len(indent) >= 2 else ""
    return re.compile(
        r'(' + re.escape(indent) + r'<div class="ctaRow">\n)'
        r'.*?'
        r'(\n' + re.escape(indent) + r'</div>\n' + re.escape(outer) + r'</div>)',
        re.S,
    )


def row(heading: str, lead: str, indent: str) -> str:
    item = indent + "  "
    inner = indent + "    "
    parts = [
        (heading, lead, None),
        (
            "What the lab builds now",
            "The Agent Lab builds live AI quoting engines for home service "
            "contractors. Supplier APIs, a labor rate matrix built from the "
            "shop's own bids, automated job intake. The same infrastructure "
            "work, pointed at an industry that still prices jobs by hand.",
            ("/services/", "Read the engine spec"),
        ),
        (
            "If you sell to contractors already",
            "Agencies and dev shops white label the engine and put their own "
            "name on it. Installs start from 8,000 USD and the partner keeps 30 "
            "percent of the install and 30 percent of the monthly. No developer "
            "on the payroll.",
            ("/#partners", "Review the math"),
        ),
    ]
    out = []
    for head, body, link in parts:
        out.append(f'{item}<div class="ctaItem">')
        out.append(f'{inner}<div class="k">{head}</div>')
        out.append(f"{inner}<p>{body}</p>")
        if link is None:
            out.append(
                f'{inner}<a class="go" href="{MCP_DOCTOR}" target="_blank"'
                ' rel="noopener">mcp-doctor on GitHub, MIT</a><br>'
            )
            out.append(
                f'{inner}<a class="go" href="{STARTER_KIT}" target="_blank"'
                ' rel="noopener">claude-mcp-starter-kit, free</a>'
            )
        else:
            href, label = link
            out.append(f'{inner}<a class="go" href="{href}">{label}</a>')
        out.append(f"{item}</div>")
    return "\n".join(out)


def main() -> int:
    touched = 0
    for name, (heading, lead) in LEAD.items():
        path = ROOT / name
        if not path.exists():
            sys.exit(f"missing {name}")
        text = original = path.read_text(encoding="utf-8")

        if not any(bad in text for bad in STALE):
            print(f"  {name}: already rewritten")
            continue

        opens = OPEN.findall(text)
        if len(opens) != 1:
            sys.exit(f"{name}: found {len(opens)} ctaRow opening tag(s)")
        indent = opens[0]

        text, n = block_pattern(indent).subn(
            lambda m: m.group(1) + row(heading, lead, indent) + m.group(2), text
        )
        if n != 1:
            sys.exit(f"{name}: matched the cta row {n} time(s)")

        for bad in STALE:
            if bad in text:
                sys.exit(f"{name}: {bad} survived")
        if text == original:
            print(f"  {name}: nothing changed")
            continue
        path.write_text(text, encoding="utf-8")
        touched += 1
        print(f"  {name}: cta rewritten")

    left = sorted(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*.html")
        if not p.relative_to(ROOT).as_posix().startswith((".cejel/", ".playwright-mcp/"))
        and any(bad in p.read_text(encoding="utf-8", errors="replace") for bad in STALE)
    )
    print(f"{touched} file(s) rewritten")
    print("old positioning still present in:" if left else "no stale CTA copy anywhere")
    for name in left:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
