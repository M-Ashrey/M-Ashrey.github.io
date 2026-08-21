#!/usr/bin/env python3
"""Take the checkout off the two kit pages.

Both kits shipped a Paddle v2 checkout with a live client token, a price id and
a success url pointing at /kits/thanks/. The processor rejected the domain, so
the button rendered as "Loading checkout" and then degraded to a hidden email
form that a visitor only saw if they clicked past it. That is the worst of both
states: a dead buy button in front of a working waitlist.

So the script block goes entirely, the buy slab becomes an honest pre-launch
note, and the waitlist comes out from behind hidden. The client token was public
by design, but it belongs to an account that cannot take payment on this domain,
so leaving it inlined on a live page serves nothing.

a09 also carried a price ladder that no longer exists: a 350 USD audit-plus-fixes
tier that appears on no other page, a 250 USD automation audit that the pivot
removed, and a claim that the services page is the price authority for figures
that page no longer lists. That paragraph is rewritten against the real numbers.

Idempotent: reruns find nothing to cut.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Everything from the Paddle tag to the end of the IIFE that follows it.
SCRIPT_BLOCK = re.compile(
    r'<script src="https://cdn\.paddle\.com/paddle/v2/paddle\.js"></script>\n'
    r"<script>\n.*?\n</script>\n",
    re.S,
)

BUY_ROW = re.compile(
    r'      <div class="buy-row">\n.*?\n      </div>\n'
    r'      <p class="buy-note" id="buyNote">[^<]*</p>\n',
    re.S,
)


def slab_note(price: str) -> str:
    return (
        f'      <p>Not for sale on this site yet, and the reason is boring. Our payment '
        f"processor rejected the domain because the lab sells services rather than digital "
        f"goods. We are not moving to a worse processor in a hurry over a {price} kit. "
        f"Leave an email below and the link comes to you directly, at this price.</p>\n"
        f'      <p class="buy-note">No card details here and no checkout to load. One email, '
        f"one download link, on the day it opens.</p>\n"
    )


LADDER_OLD = (
    "      <p>The kit is the cheap end on purpose. It exists to make the paid work "
    "repeatable: <strong>99 USD</strong> for a written security audit, "
    "<strong>350 USD</strong> for audit plus implementing the fixes, "
    "<strong>250 USD</strong> for an automation audit credited in full toward a build. "
    'Those are on the <a href="/services/">services page</a> and that page is the price '
    "authority.</p>"
)
LADDER_NEW = (
    "      <p>The kit is the cheap end on purpose. It exists to make the paid work "
    "repeatable, and the paid work is <strong>99 USD</strong> for a written security "
    "audit on one server. That figure lives on the "
    '<a href="/services/">engine page</a>, which is the price authority for this site. '
    "Worth saying plainly: the lab's main business is now live quoting engines for home "
    "service contractors at ten thousand an install. The audit line stays open because "
    "the work is real, not because it is where the money is.</p>"
)

TARGETS = {
    "kits/a09-mcp-audit/index.html": {
        "price": "29 dollar",
        "amt": '      <div class="amt">29 USD<span>founding price, one payment</span></div>',
        "amt_old": '      <div class="amt">29 USD<span>one payment</span></div>',
        "wl_head": "Get on the list",
        "wl_body": (
            "Leave your email and the download link arrives the day it opens, at the "
            "founding price, before it goes anywhere else."
        ),
        "subject": "Kit waitlist: MCP Reliability Audit Kit (a09, 29 USD)",
    },
    "kits/a01-kindle-ebooks/index.html": {
        "price": "69 dollar",
        "amt": '      <div class="amt">69 USD<span>founding price, one payment</span></div>',
        "amt_old": '      <div class="amt">69 USD<span>one payment</span></div>',
        "wl_head": "Get on the list",
        "wl_body": (
            "Leave your email and the download link arrives the day it opens, at the "
            "founding price, before it goes anywhere else."
        ),
        "subject": "Kit waitlist: Autonomous Kindle Publishing Pipeline (a01, 69 USD)",
    },
}


def main() -> int:
    for rel, cfg in TARGETS.items():
        path = ROOT / rel
        text = original = path.read_text(encoding="utf-8")

        text, n_script = SCRIPT_BLOCK.subn("", text)
        text, n_row = BUY_ROW.subn(slab_note(cfg["price"]), text)
        text = text.replace(cfg["amt_old"], cfg["amt"])

        # Surface the waitlist and retitle it now that it is the only path.
        text = text.replace(
            '    <div class="waitlist" id="waitlistBlock" hidden>\n'
            "      <h3>Prefer it by email?</h3>\n"
            "      <p>Leave your email and the link arrives the day it opens, at the "
            "founding price, ahead of anywhere else.</p>",
            '    <div class="waitlist">\n'
            f'      <h3>{cfg["wl_head"]}</h3>\n'
            f'      <p>{cfg["wl_body"]}</p>',
        )
        text = re.sub(
            r'(<input type="hidden" name="subject" value=")[^"]*(">)',
            rf"\1{cfg['subject']}\2",
            text,
            count=1,
        )

        if rel.endswith("a09-mcp-audit/index.html"):
            if LADDER_OLD not in text and "350 USD" in text:
                sys.exit("a09 ladder paragraph did not match")
            text = text.replace(LADDER_OLD, LADDER_NEW)

        if text == original:
            print(f"  {rel}: nothing to change")
            continue

        for bad in ("cdn.paddle.com", "buyBtn", "showWaitlist", "live_45d22d92"):
            if bad in text:
                sys.exit(f"{bad} survived in {rel}")
        path.write_text(text, encoding="utf-8")
        print(f"  {rel}: script x{n_script}, buy-row x{n_row}")

    left = sorted(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*.html")
        if "cdn.paddle.com" in p.read_text(encoding="utf-8")
    )
    print("paddle script still present in:" if left else "no paddle script anywhere")
    for name in left:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
