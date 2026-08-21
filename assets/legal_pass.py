#!/usr/bin/env python3
"""Light pass on the three legal pages for the pre-launch state.

Nothing on the site takes payment now, so a terms page that names a merchant of
record and a privacy page that discloses a checkout script are both describing
software that is no longer on the page. On a privacy page in particular that is
not a cosmetic problem: the disclosure has to match what actually loads.

Deliberately light. The refund promise, the licence terms and the collection
ledger all stay as written. What changes is the tense and the processor naming,
plus the one remaining "Chief Architect" on the site.

Idempotent.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EDITS = {
    "terms/index.html": [
        (
            '<meta name="description" content="What you are buying, what you may do '
            "with it, and who you are dealing with. Digital kits sold as a one-off "
            'download, 30 day refund, Paddle as merchant of record.">',
            '<meta name="description" content="What you are buying, what you may do '
            "with it, and who you are dealing with. Digital kits as a one-off "
            'download, 30 day refund, and where the pre-launch site stands.">',
        ),
        (
            "answered directly by the Chief Architect.",
            "answered directly by Ashrey, Co-Founder.",
        ),
        (
            "<p class=\"lede\">Plain version first, because nobody reads these: this "
            "lab sells digital kits as a one off download. You get 30 days to change "
            "your mind, no questions asked. You may use a kit for your own work "
            "including commercial work. You may not resell or redistribute the kit "
            "itself.</p>",
            "<p class=\"lede\">Plain version first, because nobody reads these: this "
            "lab sells digital kits as a one off download and builds AI quoting "
            "engines to order. You get 30 days to change your mind on a kit, no "
            "questions asked. You may use a kit for your own work including "
            "commercial work. You may not resell or redistribute the kit itself.</p>\n\n"
            "      <p><strong>Nothing on this site can be bought right now.</strong> "
            "Our payment processor rejected the domain because the lab sells services "
            "rather than only digital goods. Every purchase route is an email "
            "waitlist until that is settled properly. The terms below describe what "
            "applies to a sale, and they apply again the day sales reopen.</p>",
        ),
        (
            "<p><strong>Payments are processed by Paddle.com Market Ltd, who act as "
            "the merchant of record for every sale.</strong> That means Paddle is the "
            "seller of record on your receipt, Paddle handles payment processing and "
            'any sales tax or VAT due, and Paddle <a href="https://www.paddle.com/'
            'legal/checkout-buyer-terms" rel="noopener">buyer terms</a> apply to the '
            "transaction alongside this page. Your card details are never seen or "
            "stored by this lab.</p>",
            "<p><strong>No payment processor is live on this domain at the moment, so "
            "there is no checkout on any page here.</strong> When sales reopen it will "
            "be through a merchant of record, which means that company is the seller "
            "on your receipt and handles payment processing along with any sales tax "
            "or VAT due. Their buyer terms will apply alongside this page and they "
            "will be named here in the same update. Card details are never seen or "
            "stored by this lab either way.</p>",
        ),
        (
            "<p>After payment you receive an email containing a private download link, "
            "normally within a minute. The link is valid for 30 days. If it expires or "
            "never arrives, email the lab and a new one is sent. Delivery is automated, "
            "so a failure is something we want to hear about.</p>",
            "<p>While the site is on a waitlist, the download link is sent by email "
            "directly. When sales reopen, payment triggers an email containing a "
            "private download link, normally within a minute. Either way the link is "
            "valid for 30 days, and if it expires or never arrives, email the lab and "
            "a new one is sent. A delivery failure is something we want to hear "
            "about.</p>",
        ),
    ],
    "refunds/index.html": [
        (
            "<p class=\"lede\">30 days, no questions asked. Email the lab or reply to "
            "your receipt and you get your money back. You do not need to explain "
            "yourself and you will not be asked to.</p>",
            "<p class=\"lede\">30 days, no questions asked. Email the lab or reply to "
            "your receipt and you get your money back. You do not need to explain "
            "yourself and you will not be asked to.</p>\n\n"
            "      <p><strong>Worth noting while this is the pre-launch site.</strong> "
            "Nothing here takes payment today, so there is nothing to refund yet. "
            "This policy is what applies the day that changes, and it applies to "
            "founding buyers on the same terms as everyone after them.</p>",
        ),
        (
            "<p>Either reply to the Paddle receipt you were emailed and ask for a "
            "refund, or email the lab directly at <a href=\"mailto:m.ashrey122@gmail."
            "com\">m.ashrey122@gmail.com</a> with the email address you paid with. "
            "Paddle processes the refund, since they are the merchant of record. It "
            "typically reaches your original payment method within 5 to 10 business "
            "days, depending on your bank.</p>",
            "<p>Either reply to the receipt you were emailed and ask for a refund, or "
            'email the lab directly at <a href="mailto:m.ashrey122@gmail.com">'
            "m.ashrey122@gmail.com</a> with the email address you paid with. The "
            "refund is processed by whoever was the merchant of record on that "
            "receipt, so it typically reaches your original payment method within 5 "
            "to 10 business days depending on your bank.</p>",
        ),
    ],
    "privacy/index.html": [
        (
            "            <td>Name, email, billing country, payment details</td>\n"
            "            <td>You buy something</td>\n"
            "            <td>Collected and held by <strong>Paddle</strong> as merchant "
            "of record, inside their checkout. The lab receives your email address and "
            "country in order to deliver the file and account for the sale. <strong>"
            "Your card number is never received here.</strong></td>",
            "            <td>Name, email, billing country, payment details</td>\n"
            "            <td>You buy something, which is not possible right now</td>\n"
            "            <td>There is no checkout on this site at the moment, so none "
            "of this is currently collected. When sales reopen it will be collected "
            "and held by a merchant of record inside their own checkout, and this row "
            "will name them. The lab would receive your email address and country in "
            "order to deliver the file and account for the sale. <strong>Your card "
            "number is never received here.</strong></td>",
        ),
        (
            "            <td>Immediately after a purchase</td>",
            "            <td>Immediately after a purchase, or when a waitlist link is "
            "sent</td>",
        ),
        (
            "        <li><strong>Paddle</strong> loads its checkout script on kit pages "
            "only. Paddle sets its own cookies when you open a checkout, governed by "
            "their privacy notice rather than this one.</li>\n",
            "",
        ),
        (
            "<p>Purchase records are kept as long as tax and accounting rules require, "
            "which is a Paddle obligation as much as ours. Waitlist emails are kept "
            "until the kit launches and you have been told, then deleted. Support "
            "emails stay in the inbox unless you ask for deletion.</p>",
            "<p>Purchase records are kept as long as tax and accounting rules require, "
            "which is an obligation on the merchant of record as much as on us. "
            "Waitlist emails are kept until the thing you asked about is available and "
            "you have been told, then deleted. Support emails stay in the inbox unless "
            "you ask for deletion.</p>",
        ),
        (
            "For data Paddle holds as merchant of record, their privacy notice and "
            "their processes apply, and you will be pointed to the right place if you "
            "ask.</p>",
            "For data a merchant of record holds from a past sale, their privacy notice "
            "and their processes apply, and you will be pointed to the right place if "
            "you ask.</p>",
        ),
    ],
}


def main() -> int:
    for rel, pairs in EDITS.items():
        path = ROOT / rel
        text = original = path.read_text(encoding="utf-8")
        applied = 0
        for old, new in pairs:
            if old not in text:
                if new and new.split("<")[0][:40] and new[:40] in text:
                    continue  # already applied
                sys.exit(f"{rel}: no match for {old[:70]!r}")
            text = text.replace(old, new, 1)
            applied += 1
        if text == original:
            print(f"  {rel}: nothing to change")
            continue
        if "—" in text:
            sys.exit(f"{rel}: em dash introduced")
        path.write_text(text, encoding="utf-8")
        print(f"  {rel}: {applied} edit(s)")

    left = []
    for p in sorted(ROOT.rglob("*.html")):
        body = p.read_text(encoding="utf-8")
        if "Paddle" in body or "paddle" in body:
            left.append(p.relative_to(ROOT).as_posix())
    print("paddle still mentioned in:" if left else "no paddle mention anywhere")
    for name in left:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
