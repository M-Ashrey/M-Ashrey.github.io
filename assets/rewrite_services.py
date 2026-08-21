#!/usr/bin/env python3
"""Swap the services page body over to the quoting engine.

Kept as a script rather than a hand edit because the replacement spans the
whole <main> and the old body carried the Payhip checkout link, which has to
leave in the same pass. The two older service lines stay listed, since the
brief said to keep services on the page and only remove the ability to buy.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "services" / "index.html"

NEW_BODY = '''  <header class="article-head">
    <span class="eyebrow">The Engine</span>
    <h1 class="article-title">One engine. Wired to your suppliers. Loaded with your <em>numbers</em>.</h1>
    <p class="dek">This page is the price authority. Everything below is what the AI quoting engine is made of, what it costs, what you hand over, and where it stops being useful. Read that last part especially.</p>
  </header>

  <section class="section" aria-labelledby="parts-h">
    <div class="section-label">What Gets Built</div>
    <h2 class="section-title" id="parts-h">Three parts. All three have to work or the number is a guess.</h2>
    <div class="gate-grid">

      <div class="gate">
        <div class="n">01</div>
        <h4>Supplier API integration</h4>
        <p>We connect to the distributors you already buy from. Ferguson and ABC Supply are the common two, and we handle whatever else you use if it has an endpoint we can reach. Material pricing is pulled at the moment a customer asks, so a copper move does not quietly eat your margin for six weeks before anybody notices the quote sheet is stale.</p>
      </div>

      <div class="gate">
        <div class="n">02</div>
        <h4>Custom labor rate matrix</h4>
        <p>We sit down with your last bids and build the matrix out of what you actually charge. Crew size, hours by job type, access difficulty, your markup on material and your markup on labor. Your floor gets encoded as a rule, so the engine cannot produce a number you would have refused to sign.</p>
      </div>

      <div class="gate">
        <div class="n">03</div>
        <h4>Automated job intake</h4>
        <p>The form on your site asks the questions your estimator asks, in the order they ask them, and it will not submit half a job. Photos, measurements, address, access notes. By the time it lands with your team it is a priced job with a scope attached, not a name and a phone number.</p>
      </div>

    </div>
  </section>

  <section class="section" aria-labelledby="spec-h">
    <div class="section-label">The Spec</div>
    <h2 class="section-title" id="spec-h">The terms, in the order people ask about them.</h2>
    <div class="spec-row">
      <div class="spec"><span class="k">Install</span><span class="v">10,000 USD, one engine, one contractor</span></div>
      <div class="spec"><span class="k">Agency share</span><span class="v">30 percent, or 3,000 USD per install</span></div>
      <div class="spec"><span class="k">Operation</span><span class="v">Monthly, quoted per install</span></div>
      <div class="spec"><span class="k">Build time</span><span class="v">Four to six weeks from signed scope</span></div>
      <div class="spec"><span class="k">Runs on</span><span class="v">Your domain, your branding</span></div>
      <div class="spec"><span class="k">You supply</span><span class="v">Supplier account credentials and your last twenty bids</span></div>
      <div class="spec"><span class="k">We supply</span><span class="v">Integration, matrix, intake, monitoring</span></div>
      <div class="spec"><span class="k">Ownership</span><span class="v">The engine runs for you and nobody else</span></div>
    </div>
  </section>

  <section class="section" aria-labelledby="how-h">
    <div class="section-label">How The Build Runs</div>
    <h2 class="section-title" id="how-h">Four to six weeks, and you are in the room for two of them.</h2>
    <div class="step-grid">
      <div class="step">
        <div class="i">1</div>
        <h4>Rate extraction</h4>
        <p>We read your last twenty bids and pull out what you really charge, not what your website says you charge. This is the part that costs you time. Usually two sessions.</p>
      </div>
      <div class="step">
        <div class="i">2</div>
        <h4>Supplier wiring</h4>
        <p>We authenticate against your distributor accounts, map their catalogue to your job types, and handle the parts of their API that do not behave.</p>
      </div>
      <div class="step">
        <div class="i">3</div>
        <h4>Shadow run</h4>
        <p>The engine quotes live jobs alongside your estimator without publishing anything. You compare its number to yours until you stop disagreeing with it.</p>
      </div>
      <div class="step">
        <div class="i">4</div>
        <h4>Go live</h4>
        <p>Intake goes on your site. Quotes go out. Anything the engine flags as unusual routes to a human instead of guessing.</p>
      </div>
    </div>
  </section>

  <div class="limits">
    <span class="lab">Where this stops</span>
    <p><strong>If your suppliers have no usable API, we will tell you that instead of selling you a build.</strong> Some regional distributors have nothing to connect to. We can work off a rate sheet you maintain, but that is a worse product and we will price it as one.</p>
    <p><strong>Custom fabrication does not price cleanly.</strong> If most of your work is bespoke sheet metal, or structural repair with unknown conditions behind a wall, the engine will flag more jobs than it prices and you will not get your fifteen hours back.</p>
    <p><strong>The engine does not close.</strong> It puts a real number in front of a homeowner in ninety seconds instead of three days. Whether they say yes is still your job.</p>
  </div>

  <section class="section" aria-labelledby="agency-h">
    <div class="section-label">For Agencies</div>
    <div class="closing">
      <div>
        <h2 class="section-title" id="agency-h">If you already run marketing for contractors, the install is worth 3,000 USD to you.</h2>
        <p class="section-sub">White label the engine, put your name on it, place it with clients who already trust you. We handle integration and support. Thirty percent of the install and thirty percent of the monthly.</p>
      </div>
      <a class="btn-primary" href="/#partners">Review the math</a>
    </div>
  </section>

  <section class="section" aria-labelledby="also-h">
    <div class="section-label">Also From The Lab</div>
    <h2 class="section-title" id="also-h">Two older lines, still open, still priced the same.</h2>
    <p class="section-sub">These predate the engine. They are not the main business any more, but the work is real and the tooling behind it is public, so they stay listed.</p>
    <div class="spec-row">
      <div class="spec"><span class="k">MCP security audit</span><span class="v">99 USD per server, delivered in three business days</span></div>
      <div class="spec"><span class="k">Technical writing</span><span class="v">From 250 USD per article, scoped per piece</span></div>
    </div>
    <p class="fine">The audit runs on <a class="link" href="https://github.com/M-Ashrey/mcp-doctor">mcp-doctor</a>, which is open source, zero dependency and free. Read every check it makes before you pay for the layer that turns it into a report. The writing sample is the <a class="link" href="/blog/">blog</a>, published with sources cited.</p>
  </section>

  <section class="section" aria-labelledby="faq-h">
    <div class="section-label">Before You Ask</div>
    <h2 class="section-title" id="faq-h">Frequently asked</h2>
    <div class="faq">
      <details>
        <summary>Why can I not buy this on the site right now?</summary>
        <p>Our payment processor rejected the domain because we sell services rather than digital goods. We are not going to rush a fix and end up on a worse processor, so the site runs on a waitlist until that is settled properly. It has no effect on the build. Email gets you the spec, the numbers and a start date.</p>
      </details>
      <details>
        <summary>Ten thousand is a lot. What is the actual return?</summary>
        <p>Work out what you spend now. Most shops we talk to put ten to fifteen hours a week into quoting jobs that never close, and much of that is a licensed person driving. Price those hours at what you bill them and the engine pays for itself somewhere between the second and fourth month. If your numbers say otherwise, send them and we will look at them with you.</p>
      </details>
      <details>
        <summary>What if the engine quotes a job wrong?</summary>
        <p>Your margin floor is a rule inside the system, not a suggestion, so nothing goes out under it. Anything the engine is not confident about routes to a human before it reaches the customer. The shadow run exists so you find the disagreements before a homeowner does.</p>
      </details>
      <details>
        <summary>Do you need access to my accounting?</summary>
        <p>No. We need supplier account credentials so the engine can read live pricing, and enough past bids to build the rate matrix. We do not touch your books.</p>
      </details>
      <details>
        <summary>Can I see it running before I commit?</summary>
        <p>Yes. Ask for the engine walkthrough when you email. You get the real interface against a live supplier feed on a sample job, not a slide deck.</p>
      </details>
      <details>
        <summary>What if we build it and it does not work for you?</summary>
        <p>If the engine does not ship as scoped, you get your money back. That has always been the policy and it is on the <a class="link" href="/refunds/">refunds page</a>. If it ships and a number in it is flat wrong, it gets fixed.</p>
      </details>
    </div>
  </section>

  <section class="section" id="founding">
    <div class="section-label">Founding Access</div>
    <div class="closing">
      <div>
        <span class="prelaunch">Pre-launch</span>
        <h2 class="section-title">Ask for the spec. You get a document, not a sequence.</h2>
        <p class="section-sub">Contractors get the install spec and the timeline. Agencies get the partner terms and the margin sheet. Straight answer, usually the same day, and if your suppliers have nothing we can connect to we will say so in the first reply.</p>
      </div>
    </div>

    <div class="waitlist">
      <h3>Get the engine spec</h3>
      <p>One email, one document, no call required to start.</p>
      <form class="field-row" action="https://api.web3forms.com/submit" method="POST">
        <input type="hidden" name="access_key" value="26c8992d-3a5e-4c52-ad73-20f25e4dac70">
        <input type="hidden" name="subject" value="Engine spec request (services page)">
        <input type="hidden" name="from_name" value="founding access">
        <input type="checkbox" name="botcheck" class="visually-hidden">
        <label for="svc-email" class="visually-hidden">Email</label>
        <input id="svc-email" class="field-input" type="email" name="email" required placeholder="you@company.com" autocomplete="email">
        <label for="svc-role" class="visually-hidden">Who you are</label>
        <select id="svc-role" class="field-input" name="role" required>
          <option value="">Who are you?</option>
          <option value="Contractor">Contractor, I run the shop</option>
          <option value="Agency">Agency, I have contractor clients</option>
        </select>
        <button type="submit" class="btn-primary">Send me the spec</button>
      </form>
    </div>
  </section>

  <section class="section">
    <div class="section-label">Direct Line</div>
    <div class="closing">
      <div>
        <h2 class="section-title">Or just tell us the job you quote most.</h2>
        <p class="section-sub">Name the job and the suppliers you buy it from. We will tell you whether the engine can price it.</p>
      </div>
      <a class="btn-primary" href="mailto:m.ashrey122@gmail.com?subject=AI%20Quoting%20Engine">Email the lab</a>
    </div>
  </section>

'''


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    start = s.index('  <header class="article-head">')
    end = s.index("</div>\n</main>")
    out = s[:start] + NEW_BODY + s[end:]
    TARGET.write_text(out, encoding="utf-8")
    for bad in ("payhip", "Payhip", "—"):
        assert bad not in out, f"{bad} survived"
    print("services body replaced, no payhip and no em dash")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
