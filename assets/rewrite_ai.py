#!/usr/bin/env python3
"""Point /ai/ at the trades instead of at generic SMB automation.

This page was the old "AI automation practice" pitch: lead response agents,
front desks, support bots, priced $250 to $3,000. None of that survives the
pivot, and worse, its prices contradicted the ones on /services/ and on the
landing page. So the whole <main> body goes.

What stays is the cited data and the open-source proof list. The speed to lead
research is not about quoting, it is about lead response, and the page now says
so out loud rather than letting the reader assume the numbers are about quote
turnaround. A quote is a lead response, which is the argument, but the citation
has to stay honest about what it measured.

Head metadata and the Service JSON-LD are rewritten in the same pass, and the
free scorecard link is dropped from the hero. It was a generic AI readiness
scan, which is a different business than a quoting engine, and "score your site
free" is not the posture this site takes any more.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "ai" / "index.html"

TITLE = "Who We Build For | AI Quoting Engines For Trades | The Agent Lab"
DESC = (
    "We build live AI quoting engines for plumbers, HVAC, roofing, electrical "
    "and remodelling contractors. Wired to your suppliers, loaded with your "
    "labor rates, quoting in ninety seconds instead of three days."
)
OG_DESC = (
    "Live AI quoting engines for plumbers, HVAC, roofers and electricians. "
    "Wired to your suppliers, loaded with your rates, quoting in ninety seconds."
)
LD_DESC = (
    "Live AI quoting engines for home service contractors. Supplier API "
    "integration, a labor rate matrix built from your own bids, and automated "
    "job intake, so a customer gets a real priced quote in ninety seconds "
    "instead of waiting three days for a manual estimate."
)
SAME_AS = (
    '["https://www.linkedin.com/in/mohamed-ashrey/", '
    '"https://github.com/M-Ashrey", "https://dev.to/m_ashrey122", '
    '"https://www.youtube.com/@TheAgentLab"]'
)

NEW_BODY = '''  <header class="article-head">
    <span class="eyebrow">Who We Build For</span>
    <h1 class="article-title">Trades that price work <em>on site</em>, by hand, for free.</h1>
    <p class="dek">Plumbing, HVAC, roofing, electrical and remodelling. If a licensed person is driving to a house to produce a number that a customer might not even read, that is the work we automate. <strong>Ninety seconds instead of three days</strong>, on your rates, from your suppliers.</p>
    <div class="article-actions">
      <a class="btn-primary" href="/services/">See the spec</a>
      <a class="btn-secondary" href="/#partners">Agency partners</a>
      <a class="btn-ghost" href="#proof">See the code</a>
    </div>
    <p class="fine">Every figure on this page is published industry data with a citation, or software you can open and read right now. No borrowed logos and no revenue promises.</p>
  </header>

  <section class="section">
    <div class="section-label">The Bottleneck</div>
    <h2 class="section-title">The job is usually lost before anyone quotes it.</h2>
    <div class="metric-grid">
      <div class="metric">
        <div class="n">21x</div>
        <div class="d">More likely to convert when a lead is contacted within 5 minutes rather than 30.</div>
        <div class="c">National Association of Realtors, 2025</div>
      </div>
      <div class="metric">
        <div class="decay">
          <div class="decay-row"><span class="k">1 min</span><span class="track"><i style="width:100%"></i></span><span class="v">+391%</span></div>
          <div class="decay-row"><span class="k">5 min</span><span class="track"><i style="width:74%"></i></span><span class="v">21x odds</span></div>
          <div class="decay-row"><span class="k">30 min</span><span class="track"><i style="width:20%"></i></span><span class="v">baseline</span></div>
          <div class="decay-row"><span class="k">15+ hrs</span><span class="track"><i style="width:6%"></i></span><span class="v">avg agent</span></div>
        </div>
        <div class="c">Contact rate and conversion: MIT and Dr James Oldroyd. Average response: Inman, 2025. 78% of buyers purchase from whoever responds first.</div>
      </div>
    </div>
    <p class="fine">To be exact about it, this research measures lead response, not quote turnaround. We are treating a priced quote as the response, because for a contractor that is what the customer is actually waiting for. A callback with no number in it does not stop them phoning the next three shops.</p>
  </section>

  <section class="section">
    <div class="section-label">The Other Half</div>
    <h2 class="section-title">Then there are the hours you already paid for.</h2>
    <p class="section-sub">Most shops we talk to put ten to fifteen hours a week into pricing jobs. A large share of that is a licensed estimator in a truck, on the road, producing a document for free. Some of those become work. Many of them were price shopping from the first phone call, and you found that out after the site visit.</p>
    <div class="spec-row">
      <div class="spec"><span class="k">What it costs now</span><span class="v">Drive time, estimator hours, three day turnaround</span></div>
      <div class="spec"><span class="k">What the customer gets</span><span class="v">Nothing, until somebody finds a free evening</span></div>
      <div class="spec"><span class="k">What the engine changes</span><span class="v">A real number, priced on your rates, in ninety seconds</span></div>
      <div class="spec"><span class="k">Who still drives out</span><span class="v">The jobs that priced high enough to be worth the trip</span></div>
    </div>
    <p class="fine">The engine does not remove the site visit from complicated work. It removes the site visit from work that was never going to close.</p>
  </section>

  <section class="section">
    <div class="section-label">By Trade</div>
    <h2 class="section-title">Where an engine prices cleanly, and what actually changes.</h2>
    <div class="data-table-container">
      <div class="data-table-header">
        <span class="data-table-title">Trade map</span>
        <span class="data-table-badge">Scoped per shop, not guaranteed</span>
      </div>
      <table>
        <thead>
          <tr>
            <th scope="col">Trade</th>
            <th scope="col">Where the hours go</th>
            <th scope="col">What the engine prices</th>
            <th scope="col">What changes</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Plumbing</td>
            <td>Repipes, water heaters and drain work all get quoted on site, one house at a time.</td>
            <td><strong>Material from your distributor, labor from your matrix.</strong> Copper, PEX and fixtures priced live off Ferguson or whoever you buy from, hours set by job type and access.</td>
            <td>Homeowner gets a number the same hour they ask. Your estimator only drives out when the job is worth it.</td>
          </tr>
          <tr>
            <td>HVAC</td>
            <td>Replacement quotes wait on equipment pricing that moves and on load sizing.</td>
            <td><strong>Equipment and install by tonnage and configuration.</strong> Unit cost pulled live, install hours from your own bids, your markup enforced as a rule.</td>
            <td>Replacement quotes go out during the call instead of after the weekend, with your margin already in them.</td>
          </tr>
          <tr>
            <td>Roofing</td>
            <td>Square footage, tear off layers and material choice, worked out by hand per roof.</td>
            <td><strong>Squares, layers, pitch and material.</strong> Shingle and underlayment pricing from ABC Supply or your supplier, labor scaled by pitch and access difficulty.</td>
            <td>Intake collects what your estimator asks for, so the quote is priced before anybody climbs a ladder.</td>
          </tr>
          <tr>
            <td>Electrical</td>
            <td>Panel upgrades and rewires priced off a walkthrough that has to be scheduled.</td>
            <td><strong>Panels, runs and fixture counts.</strong> Material live from your distributor, labor by circuit count and building age band.</td>
            <td>Standard upgrades price themselves. Anything behind a wall gets flagged for a human instead of guessed at.</td>
          </tr>
          <tr>
            <td>Remodelling and GC</td>
            <td>Multi-trade scopes assembled in a spreadsheet, every single time.</td>
            <td><strong>The repeatable line items.</strong> Known assemblies price automatically, unknowns are flagged. This one is a partial fit and we will say so before we quote you.</td>
            <td>The estimator starts from a priced draft instead of a blank sheet, and only argues with the unusual parts.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="fine">Outcomes are stated as what the engine does, measured against your current turnaround, never as a revenue promise. Whether it fits your specific mix gets settled before anything is built.</p>
  </section>

  <div class="limits">
    <span class="lab">Where we are not a fit</span>
    <p><strong>If your suppliers have no usable API, we will tell you.</strong> Some regional distributors have nothing to connect to. We can run off a rate sheet you maintain by hand, but that is a worse product and we price it as one.</p>
    <p><strong>If most of your work is bespoke, this is not for you.</strong> Custom fabrication and structural repair with unknown conditions behind a wall do not price from a form. The engine will flag more jobs than it prices and you will not get your hours back.</p>
    <p><strong>If you are not the one who sets pricing, we cannot build it.</strong> The matrix comes out of your real bids and your real margin floor. Somebody with authority over those numbers has to sit in two sessions with us.</p>
  </div>

  <section class="section">
    <div class="section-label">One Price</div>
    <h2 class="section-title">There is one product and one number.</h2>
    <p class="section-sub">This is not a menu. Every contractor gets the same engine, wired to their own suppliers and loaded with their own rates. The full spec, the build timeline and the terms live on the engine page, which is the price authority for this site.</p>
    <div class="spec-row">
      <div class="spec"><span class="k">Direct install</span><span class="v">10,000 USD, one engine, one contractor</span></div>
      <div class="spec"><span class="k">Agency share</span><span class="v">30 percent, or 3,000 USD per install</span></div>
      <div class="spec"><span class="k">Operation</span><span class="v">Monthly, quoted per install</span></div>
      <div class="spec"><span class="k">Build time</span><span class="v">Four to six weeks from signed scope</span></div>
    </div>
    <div class="hero-actions">
      <a class="btn-primary" href="/services/">Read the full spec</a>
      <a class="btn-secondary" href="#founding">Founding access</a>
    </div>
  </section>

  <section class="section">
    <div class="section-label">How You Find Out</div>
    <h2 class="section-title">Four steps, and two of them are free.</h2>
    <div class="step-grid">
      <div class="step"><div class="i">01</div><h4>Name the job</h4><p>Tell us the job you quote most and who you buy the material from. One email. No call and no discovery sequence.</p></div>
      <div class="step"><div class="i">02</div><h4>We check the suppliers</h4><p>We look at whether your distributors expose pricing we can reach. If they do not, that is the end of it and we say so.</p></div>
      <div class="step"><div class="i">03</div><h4>Spec and number</h4><p>You get the build scope, the timeline and the price in writing before anything is committed.</p></div>
      <div class="step"><div class="i">04</div><h4>Build and shadow run</h4><p>Four to six weeks. The engine quotes live jobs beside your estimator until you stop disagreeing with it, then intake goes on your site.</p></div>
    </div>
    <div class="callout">
      <span class="lab">The guarantee</span>
      <p>Your margin floor is enforced inside the engine, not suggested to it, and anything it is unsure about routes to <strong>a human before it reaches the customer</strong>. We guarantee the deliverable and the timeline. We do not guarantee a revenue number, because we do not control whether your customers say yes.</p>
    </div>
  </section>

  <section class="section" id="proof">
    <div class="section-label">Proof Of Work</div>
    <h2 class="section-title">Do not take the claim. Open the code.</h2>
    <p class="section-sub">The engine itself runs for the contractor who paid for it, so it is not public. The infrastructure work behind it is, and it has been for a while.</p>
    <ul class="proof-list">
      <li><a href="https://github.com/M-Ashrey/mcp-doctor" target="_blank" rel="noopener"><span class="nm">mcp-doctor</span><span class="ds">CLI health check and security audit for MCP servers, MIT</span></a></li>
      <li><a href="https://github.com/M-Ashrey/memory-mcp" target="_blank" rel="noopener"><span class="nm">memory-mcp</span><span class="ds">Persistent memory MCP server, listed on Glama</span></a></li>
      <li><a href="https://github.com/M-Ashrey/promptlint" target="_blank" rel="noopener"><span class="nm">promptlint</span><span class="ds">Linter for prompts and agent files, CI and tests</span></a></li>
      <li><a href="https://github.com/M-Ashrey/claude-mcp-starter-kit" target="_blank" rel="noopener"><span class="nm">claude-mcp-starter-kit</span><span class="ds">Turn Claude into an autonomous operator</span></a></li>
      <li><a href="/blog/"><span class="nm">the blog</span><span class="ds">Cited technical analysis, published continuously</span></a></li>
    </ul>
    <p class="fine">Integrating against a distributor API that was designed for a purchasing department, not a quoting engine, is the actual job. This is the kind of work it looks like.</p>
  </section>

  <section class="section">
    <div class="section-label">For Agencies</div>
    <div class="closing">
      <div>
        <h2 class="section-title">You already run marketing for these shops. The install is worth 3,000 USD to you.</h2>
        <p class="section-sub">You know their real problem is not traffic. You have watched good leads sit in an inbox for three days. White label the engine, put your name on it, place it with clients who already trust you. Thirty percent of the install and thirty percent of the monthly, with no developer on your payroll.</p>
      </div>
      <a class="btn-primary" href="/#partners">Review The Math</a>
    </div>
  </section>

  <section class="section" id="founding">
    <div class="section-label">Founding Access</div>
    <div class="closing">
      <div>
        <span class="prelaunch">Pre-launch</span>
        <h2 class="section-title">Nothing here is for sale on the site yet, and that is deliberate.</h2>
        <p class="section-sub">Our payment processor rejected the domain because we sell services rather than digital goods. We are not rushing to a worse processor over it. The founding group is small, the terms are better, and the first builds happen with us in the room.</p>
      </div>
    </div>

    <div class="waitlist">
      <h3>Get founding access</h3>
      <p>Contractors get the install spec and the timeline. Agencies get the partner terms and the margin sheet. One document, no sequence of nine emails.</p>
      <form class="field-row" action="https://api.web3forms.com/submit" method="POST">
        <input type="hidden" name="access_key" value="26c8992d-3a5e-4c52-ad73-20f25e4dac70">
        <input type="hidden" name="subject" value="Founding access (who we build for page)">
        <input type="hidden" name="from_name" value="founding access">
        <input type="checkbox" name="botcheck" class="visually-hidden">
        <label for="ai-email" class="visually-hidden">Email</label>
        <input id="ai-email" class="field-input" type="email" name="email" required placeholder="you@company.com" autocomplete="email">
        <label for="ai-role" class="visually-hidden">Who you are</label>
        <select id="ai-role" class="field-input" name="role" required>
          <option value="">Who are you?</option>
          <option value="Contractor">Contractor, I run the shop</option>
          <option value="Agency">Agency, I have contractor clients</option>
        </select>
        <button type="submit" class="btn-primary">Send me the numbers</button>
      </form>
    </div>
  </section>

  <section class="section" id="book">
    <div class="section-label">Direct Line</div>
    <div class="closing">
      <div>
        <h2 class="section-title">Tell us the job you quote most.</h2>
        <p class="section-sub">Name the job and the suppliers you buy it from. We will tell you whether the engine can price it, usually the same day, and we will tell you when it cannot.</p>
      </div>
      <a class="btn-primary" href="mailto:m.ashrey122@gmail.com?subject=AI%20Quoting%20Engine">Email the lab</a>
    </div>
    <p class="fine"><strong>Sources.</strong> Speed to lead: National Association of Realtors (2025), MIT and Dr James Oldroyd, Inman (2025). These figures measure inbound lead response, which we treat here as a proxy for quote turnaround. Quoting hours are what contractors have told us directly, not a published study. Figures are directional industry benchmarks from published reports, not audited data and not results claimed by this lab.</p>
  </section>

'''


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")

    start = s.index('  <header class="article-head">')
    end = s.index("</div>\n</main>")
    out = s[:start] + NEW_BODY + s[end:]

    subs = [
        (r"<title>.*?</title>", f"<title>{TITLE}</title>"),
        (r'(<meta name="description" content=")[^"]*(")', rf"\1{DESC}\2"),
        (r'(<meta property="og:title" content=")[^"]*(")', rf"\1{TITLE}\2"),
        (r'(<meta property="og:description" content=")[^"]*(")', rf"\1{OG_DESC}\2"),
        (r'(<meta name="twitter:title" content=")[^"]*(")', rf"\1{TITLE}\2"),
        (r'(<meta name="twitter:description" content=")[^"]*(")', rf"\1{OG_DESC}\2"),
        (
            r'(<meta property="og:image:alt" content=")[^"]*(")',
            r"\1The Agent Lab, AI quoting engines for home service contractors\2",
        ),
        (
            r'("name": "The Agent Lab - AI Automation")',
            '"name": "AI Quoting Engine"',
        ),
        (r'("description": ")[^"]*(")', rf"\1{LD_DESC}\2"),
        (r'("sameAs": )\[[^\]]*\]', rf"\1{SAME_AS}"),
    ]
    for pat, rep in subs:
        out, n = re.subn(pat, rep, out, count=1, flags=re.S)
        if not n:
            sys.exit(f"no match for {pat}")

    for bad in ("—", "ai-readiness-scorecard", "Book a 15 min", "$250", "$1,500"):
        if bad in out:
            sys.exit(f"{bad} survived the rewrite")

    TARGET.write_text(out, encoding="utf-8")
    print(f"wrote {TARGET.relative_to(ROOT).as_posix()} ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
