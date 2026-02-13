# FlipSide

**The dark side of small print.**

**What did you agree to?** We show you what a trusting reader sees — then flip the card to reveal what an expert catches.

**FlipSide** analyzes documents you didn't write — leases, insurance policies, Terms of Service — and shows you what the other side intended. Upload a document. Flip cards appear within seconds: the front shows how the drafter *wants* you to feel ("Your flexible payment timeline"). Flip the card — the back reveals what the drafter intended ("$4,100 in penalties if you're two days late"). The naive reading and the expert analysis are two sides of the same card. Behind the flip: 5 parallel threads. Haiku 4.5 generates instant cards (both sides, ~12 seconds). Four Opus 4.6 threads build the expert verdict simultaneously — cross-clause compound risks, power asymmetry analysis, document archaeology, and an overall assessment where Opus reviews its own work for blind spots. After the verdict: message the company with a professional letter citing specific clauses, or generate a counter-draft with fair alternatives. 14 Opus 4.6 capabilities in one product. Each visible in the interface, each doing work a smaller model cannot. One input. One perspective flip. The dark side of small print.

---

## The Problem

Every day, millions of people accept documents they did not draft and do not fully understand: leases, insurance policies, Terms of Service, employment contracts, loan agreements, gym memberships, medical consent forms, HOA bylaws, coupon reward programs, wedding venue contracts, pet adoption agreements, timeshare packages, sweepstakes rules.

These documents are written by one party's legal team to protect that party's interests. The person signing sees the words. They do not see the strategy behind the words.

There is no tool that shows you what a document looks like from the other side — from the perspective of the party who drafted it.

---

## What FlipSide Does

You upload a document. FlipSide reads it as if it were the drafter's attorney — the person who wrote it and knows exactly why every clause is there. Then it tells you what it found.

**One input. One perspective flip. One output.**

### The Four Steps

1. **Upload** — Drag in a PDF, DOCX, or paste text. Or pick from 13 built-in sample documents (lease, insurance, ToS, employment, loan, gym membership, medical consent, HOA rules, coupon booklet, wedding venue, pet adoption, timeshare vacation package, and a real Coca-Cola sweepstakes) — sample contracts authored by Claude with clauses engineered to demonstrate each of the 18 trick categories, plus one real-world document.

2. **Browse flip cards** — Cards appear one at a time within seconds. Each card is a clause with two sides:
   - **Front**: A calm green header bar with a reassurance headline ("Your flexible payment timeline") followed by the reader's gullible first-person impression. This is how the drafter WANTS you to feel. Navigation is hidden until the user flips their first card — forcing the core mechanic.
   - **Back**: What the drafter intended — a red/yellow/green risk header with risk score, trick classification, the key figure in large bold type ("$4,100 in penalties"), a concrete example scenario, and bottom-line action. The sidebar dims to 35% opacity to spotlight the reveal.
   - **Confidence badge**: HIGH / MEDIUM / LOW with reasoned explanation
   - Color-coded: **Green** (standard) · **Yellow** (notable) · **Red** (strategically asymmetric)
   - **Document preview**: Sidebar shows the full document text with page dividers and numbered clause markers (①②③) that highlight when you navigate cards. Page navigation tabs appear progressively — only for pages that contain findings. Fuzzy matching ensures markers appear even when PDF text extraction differs from model quotes.
   - **Live progress**: During scanning, a clause counter updates in real-time ("5 clauses found so far...").
   - **Document suitability**: If a document has no terms to analyze (recipe, novel, personal letter), the model detects this immediately and shows a clear explanation instead of empty results.
   - **All output in English** — regardless of the document's language. Original-language terms are quoted directly. A download button generates the full report translated into the document's language.

3. **Read the Expert Verdict** — While you browse cards, 4 parallel Opus 4.6 threads build the expert verdict in the right column, each section appearing as it completes:
   - **Cross-clause interactions** — compound risks invisible when reading clause by clause, with villain voice and **YOUR MOVE** actions
   - **Power Asymmetry & Fair Standard** — obligation count per party, power ratio, and how the worst clauses compare to industry norms
   - **Document Archaeology & Drafter Profile** — boilerplate vs. custom clauses, who drafted this and what it signals
   - **Overall Assessment** — overall risk score, methodology disclosure, and quality check where Opus reviews its own analysis for false positives and blind spots

4. **Take action** — After the verdict:
   - **Ask follow-up questions** — "What happens if I'm 3 months late on rent?" / "Which clauses can I actually negotiate?" — Opus traces the answer through all relevant clauses with extended thinking
   - **Message the company** — One-click draft of a professional complaint letter citing the specific high-risk clauses found, with copy-to-clipboard and open-in-email
   - **Counter-draft** — Opus rewrites unfair clauses with negotiable alternatives you can propose
   - **Download report** — Export the full analysis, optionally translated to the document's original language

---

## Who Uses It

| User | Document | What they learn |
|------|----------|----------------|
| **Tenant** | Lease agreement | "Repairs not covered by building insurance" means they pay for plumbing, electrical, and HVAC |
| **Homeowner** | Insurance policy | Two exclusion clauses interact to deny most real-world water damage claims |
| **Employee** | Employment contract | An at-will clause renders every other promise (discipline process, severance) unenforceable |
| **App user** | Terms of Service | "We may share with partners" means unrestricted sale to data brokers |
| **Borrower** | Loan agreement | A single late payment triggers a cascade of penalties designed to stack |
| **Gym member** | Fitness membership | Auto-renewal kicks in silently, and the cancellation window is 30 days before a date they never told you |
| **Patient** | Medical consent form | A liability waiver is placed after medical disclosures to benefit from the assumption that everything on the form is standard |
| **Homeowner** | HOA bylaws | The board can levy special assessments with no cap and fine you daily for violations defined at their sole discretion |
| **Shopper** | Coupon reward program | "Savings" require minimum spend thresholds that make every "deal" cost more than buying at full price |
| **Couple** | Wedding venue contract | A force majeure clause protects the venue but not you — if they cancel, you get a credit; if you cancel, you lose everything |
| **Pet owner** | Adoption contract | A return clause lets the shelter reclaim the animal at any time if they judge your care "inadequate" — no appeal process |
| **Vacationer** | Timeshare package | A "cooling off" period is shorter than the payment processing time, making the exit window structurally impossible to use |
| **Winner** | Sweepstakes rules | Accepting the prize grants perpetual, worldwide rights to your name, likeness, and story for marketing — with no compensation |

---

## 14 Opus 4.6 Capabilities in One Product

FlipSide uses more Opus 4.6 capabilities than any single feature would require — including five that Anthropic [specifically highlights in the Opus 4.6 announcement](https://www.anthropic.com/research/introducing-claude-opus-4-6): adaptive thinking, long-context retrieval, low over-refusals, effort controls, and context compaction. Each capability is **visible in the product** — not a behind-the-scenes optimization.

| # | Opus 4.6 Feature | What the user sees |
|---|-----------|-------------------|
| 1 | **Adaptive thinking** | 4 parallel Opus threads each decide their own reasoning depth — spending more on complex cross-clause interactions, less on boilerplate |
| 2 | **Long-context retrieval** | Cross-clause interaction detection across the full document. Clause 2(c) and Clause 2(e) together deny water claims — neither clause is dangerous alone |
| 3 | **Low over-refusals** | Villain voice — adversarial role-play where Opus adopts the drafter's perspective. Previous models would self-censor. Opus 4.6 fully commits to the adversarial framing |
| 4 | **Effort controls** | Architecture maps depth selector to Opus 4.6's `effort` parameter (medium/high/max). Currently using `max_tokens` as depth knob pending SDK support |
| 5 | **Context compaction** | Follow-up questions send full document + analysis as context. Compaction enables extended Q&A without hitting the context window |
| 6 | **Vision / multimodal** | PDF pages sent as images — Opus detects fine print, buried placement, visual hierarchy tricks invisible to text extraction |
| 7 | **Tool use** | `assess_risk` and `flag_interaction` tools structure findings with risk level, confidence %, trick type |
| 8 | **Confidence calibration** | HIGH/MEDIUM/LOW badges with explicit reasoning chains — not pattern-matched, but thought through |
| 9 | **Self-correction** | Quality Check — Opus reviews its own analysis for false positives and blind spots before presenting results |
| 10 | **Split-model parallel** | Haiku 4.5 (instant full cards) + 4× Opus 4.6 (expert verdict threads) — 5 threads at t=0 |
| 11 | **Prompt caching** | System prompts cached server-side for 90% cost reduction on repeated analyses |
| 12 | **Counterfactual generation** | Fair Standard Comparison — worst clauses measured against industry norms. Counter-draft rewrites unfair clauses |
| 13 | **Stylistic deduction** | Document Archaeology — boilerplate vs. custom clauses, drafter profile from writing patterns |
| 14 | **English-only + download in language** | All output in English for universal access. Download full report translated to the document's original language via Opus |

### Why Opus 4.6 Specifically

Five capabilities from [Anthropic's Opus 4.6 announcement](https://www.anthropic.com/research/introducing-claude-opus-4-6) are **structurally necessary** for FlipSide to work. Remove any one and the product degrades:

1. **Adaptive thinking — the reasoning IS the product.** The extended thinking stream is not hidden behind a loading spinner — it IS the interface. Each of 4 parallel Opus threads decides its own reasoning depth: spending more thinking tokens on complex interactions and less on standard boilerplate. Most projects use extended thinking as a black box. FlipSide makes it visible in the expert verdict.

2. **Long-context retrieval — finding legal traps spread across pages.** Anthropic reports "76% on MRCR v2 8-needle 1M — a qualitative shift in how much context a model can actually use." FlipSide applies this to cross-clause interaction detection: Clause 2(c) excludes water damage from "gradual seepage over 14 days." Clause 2(e) defines the inspection timeline at 30 days. Neither clause is dangerous alone. Together, they deny virtually all residential water damage claims. The model holds the entire document in working memory and reasons across distant clauses simultaneously.

3. **Low over-refusals — the villain voice works.** Every red-flagged interaction includes adversarial role-play where Opus adopts the drafter's voice: *"The math does the work. Two weeks late once and you'll never catch up."* Previous models would self-censor, add disclaimers, or refuse the adversarial framing entirely. Opus 4.6's low over-refusal rate means the perspective flip — the core product mechanic — actually works.

4. **Effort controls — user-facing intelligence dial.** The depth selector (Quick/Standard/Deep) is designed to map directly to Opus 4.6's new `effort` parameter (Quick→medium, Standard→high, Deep→max). The UI and backend architecture are ready — currently using `max_tokens` as the depth knob because the `effort` parameter is not yet available in the Python SDK (v0.46.0). When the SDK adds support, it's a one-line change per preset.

5. **Context compaction — follow-up without limits.** After analysis, users ask questions ("What happens if I'm 3 months late?"). Each follow-up sends the full document + previous analysis as context. Compaction summarizes prior exchanges while retaining the document — turning a one-shot analysis into an interactive consultation.

Plus: **vision** catches formatting tricks text extraction misses, **tool use** structures the reasoning into assessable data, and **self-correction** reviews the analysis for false positives before the user sees it.

---

## The Meta-Prompting Discovery

During the hackathon, we stumbled on something that even the Claude Code team couldn't fully explain.

When you ask Claude to **"analyze this contract"**, you get a decent analysis. But when you ask Claude to **"write a prompt for analyzing this contract"** and then say **"now execute that prompt"** — the results are dramatically better.

Why? The two-step approach forces the model to separate *planning* from *execution*. In the first step, it reasons about what makes a good analysis — what to look for, what perspectives to take, how to structure findings. In the second step, it follows its own expert framework. It's chain-of-thought at the meta level.

**Cat Wu** (Product Lead and co-creator of Claude Code) confirmed this pattern during the hackathon AMA — the effect is real, though the exact mechanism isn't fully understood.

FlipSide's entire architecture is a **productized version of this discovery**. The system prompt doesn't just say "analyze this document." It teaches Claude *how to think about documents*: adopt the drafter's perspective, apply a taxonomy of 18 legal trick types (Silent Waiver, Time Trap, Cascade Clause...), contrast "what the small print says" against "what you should read." The prompt is a pre-built reasoning framework that every uploaded document then executes against.

The user never sees this meta-prompt. They just see better results.

---

## The Principle

FlipSide applies **"Think Like a Document"** (CHI 2026, Henk van Ess) to a new domain:

| In search | In FlipSide |
|-----------|-------------|
| Don't search using YOUR words | Don't read using YOUR perspective |
| Think like the document you're looking for | Think like the party who drafted the document |
| The document doesn't know your vocabulary | The contract doesn't serve your interests |
| Match the document's language to find it | Adopt the drafter's perspective to understand it |

The underlying principle is the same: **don't take yourself as the measurement of things. Observe what must be there.**

---

## Architecture

```
                    User uploads document
                            │
                            ▼
                Flask extracts text (PDF/DOCX/paste)
                            │
     ┌──────────────────────┼──────────────────────┐
     │                      │                       │
     ▼                      ▼                       ▼
┌──────────┐  ┌─────────────────────────┐  ┌─────────────────────┐
│ HAIKU 4.5│  │     OPUS 4.6 × 4       │  │   OPUS 4.6 × 4      │
│          │  │                         │  │   (continued)        │
│ Full     │  │  Thread 1: Interactions │  │  Thread 3: Archaeol. │
│ flip     │  │  Cross-clause compound  │  │  Boilerplate vs      │
│ cards    │  │  risks, villain voice,  │  │  custom, drafter     │
│ (both    │  │  YOUR MOVE actions      │  │  profile              │
│ sides)   │  │                         │  │                       │
│          │  │  Thread 2: Asymmetry    │  │  Thread 4: Overall   │
│ ~12s:    │  │  Power ratio, fair      │  │  Assessment, quality │
│ first    │  │  standard comparison    │  │  check, methodology  │
│ card     │  │                         │  │                       │
└────┬─────┘  └────────────┬────────────┘  └──────────┬──────────┘
     │                     │                           │
     │              All 5 threads start at t=0         │
     │                     │                           │
     ▼                     ▼                           ▼
 Cards stream      Verdict column fills         Overall waits for
 in (~12s)         section by section           parts 1-3 before
                   (~15-60s)                    auto-expanding
     │                     │                           │
     ▼                     ▼                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLIP CARDS + EXPERT VERDICT               │
│                                                             │
│  ┌─────────────────────┐   ┌──────────────────────────┐    │
│  │ Card column (Haiku) │   │ Verdict column (Opus)    │    │
│  │                     │   │                          │    │
│  │ Front: Green bar,   │   │ Cross-Clause Interact.   │    │
│  │ reassurance, naive  │   │ Power Asymmetry          │    │
│  │ reader voice        │   │ Document Archaeology     │    │
│  │                     │   │ Overall Assessment       │    │
│  │ — flip card —       │   │                          │    │
│  │                     │   │ Each section streams in  │    │
│  │ Back: Risk header,  │   │ independently, pulsing   │    │
│  │ score, trick, figure│   │ dot → solid when done    │    │
│  │ example, bottom line│   │                          │    │
│  └─────────────────────┘   └──────────────────────────┘    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ACTION BAR                                           │   │
│  │ Message the Company · Counter-Draft · Follow-up Q&A  │   │
│  │ Download Report (EN or document language)             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Seven-Stage Pipeline

FlipSide is a seven-stage pipeline with 5 threads running at t=0 and 2 on-demand actions:

| Stage | Agent | What It Does | What the User Sees |
|---|---|---|---|
| 1. **Instant Cards** | Haiku 4.5 | Full flip cards — both sides. Front: reassurance + gullible reader. Back: risk score, trick, figure, example, bottom line. | Cards fly in within ~12s. Flip any card instantly. |
| 2. **Cross-Clause** | Opus 4.6 Thread 1 | Compound risks across clauses, villain voice, YOUR MOVE actions | Verdict column section 1 streams in |
| 3. **Asymmetry** | Opus 4.6 Thread 2 | Power ratio, obligation count per party, fair standard comparison | Verdict column section 2 streams in |
| 4. **Archaeology** | Opus 4.6 Thread 3 | Boilerplate vs. custom, drafter profile from writing patterns | Verdict column section 3 streams in |
| 5. **Overall** | Opus 4.6 Thread 4 | Overall assessment, methodology, quality check (self-correction) | Auto-expands after sections 1-3 complete |
| 6. **Counter-Draft** | Opus 4.6 (on demand) | Rewrites unfair clauses with negotiable alternatives | Fair-language replacements per flagged clause |
| 7. **Follow-up** | Opus 4.6 (interactive) | User asks questions → Opus traces answers through all clauses | Open-ended consultation + message-the-company |

**5 threads at t=0**: Haiku generates full cards (~12s for first card), while 4 Opus threads build the expert verdict in parallel. The user browses and flips cards while the verdict column fills in section by section. No waiting, no dependencies between card browsing and expert analysis.

**Key architectural insight**: We originally put Opus 4.6 on the card backs — assuming the flip needed the most powerful model. After 3 hours of DOM rendering failures, we discovered Haiku was already doing a great job on cards. Opus's real value is in the work Haiku *can't* do: cross-clause reasoning, power analysis, archaeological deduction, and self-correction. Each model now has a stage that showcases what it does best. See [strategy.md](strategy.md) for the full decision story.

**Tech stack:** Python/Flask, Server-Sent Events, Anthropic API (Haiku 4.5 + Opus 4.6 with extended thinking, vision, tool use, prompt caching), single-file HTML/CSS/JS frontend, DOMPurify for XSS protection on LLM output. 12 built-in sample documents with generated thumbnails (including a real Coca-Cola sweepstakes). No external APIs beyond Anthropic. No database required. All output in English; download reports in the document's original language. Deployable behind a reverse proxy with URL prefix.

---

## The Demo Moment

The user uploads a real homeowner's insurance policy. Cards appear within seconds.

**Card front (the naive reader):**
> *"Comprehensive coverage for your peace of mind"*
>
> I'D THINK: OK, so my house is covered for "direct physical loss" — that sounds like everything. Water damage, fire, theft. Good. That's exactly what I'm paying for.

The audience nods. That IS what they'd think.

**User flips the card.**

**Card back (the expert analysis):**
> RED · Score: 82/100 · Trick: Phantom Protection
>
> **$0 payout on a $50,000 water damage claim.** Exclusion 2(c) excludes "gradual seepage over 14 days." Clause 2(e) sets the inspection window at 30 days. Together: virtually all residential water damage can be reclassified as "gradual" after the fact. The broad coverage on the front is a psychological anchor — it makes you stop reading before you reach the exclusions that take it away.

Meanwhile, the verdict column is filling in: the cross-clause interaction thread has already detected that Clauses 2(c) and 2(e) create a compound trap. The user sees the card-level analysis AND the document-level synthesis simultaneously.

**Then the user clicks "Message the Company"** — and Opus drafts a professional letter citing the specific clauses, ready to copy or email.

---

## What This Is Not

- Not a legal advice tool (it analyzes documents, it does not give legal recommendations)
- Not a contract generator (it reads existing documents, it does not create new ones)
- Not a diff tool (it reveals strategic intent, not textual differences)
- Not a chatbot (it performs one analysis per document — though you can ask follow-up questions after)

---

## FlipSide vs. Anthropic's Legal Plugin

On February 2, 2026, Anthropic launched a [legal plugin for Claude Cowork](https://legaltechnology.com/2026/02/03/anthropic-unveils-claude-legal-plugin-and-causes-market-meltdown/) — enterprise contract review that crashed legal tech stocks by $50B+. FlipSide, built during this hackathon, approaches the same domain from the opposite direction. The plugin reviews contracts FOR legal teams. FlipSide reveals what the drafting team intended — for the millions of people who sign documents without a legal team. Same model. Different side of the table.

| | Anthropic Legal Plugin | FlipSide |
|---|---|---|
| **User** | In-house corporate counsel | Consumer who received a document they didn't write |
| **Perspective** | Reviews FROM your configured playbook | Flips TO the drafter's perspective — no playbook needed |
| **Opus 4.6 use** | Standard clause flagging | 14 capabilities: adaptive thinking, long-context retrieval, low over-refusals, effort controls, context compaction, vision, tool use, confidence calibration, self-correction, split-model parallel, prompt caching, counterfactual generation, stylistic deduction, English+download |
| **Input** | Contracts your legal team handles | Any document: leases, insurance, ToS, loans, employment, medical consent |
| **Output** | Redline suggestions, NDA triage | Flip cards, villain voice, YOUR MOVE actions, message-the-company, counter-draft |
| **Requires** | Cowork enterprise license, MCP integrations, configured playbook | Nothing — upload and go |
| **Approach** | Automates what a lawyer already does | Reveals what the lawyer on the other side was thinking |

### How FlipSide pushes Opus 4.6 further

The legal plugin uses Opus for clause flagging and redline suggestions — standard contract review. FlipSide pushes Opus 4.6 into capabilities the plugin does not use:

- **5-thread parallel architecture** — 1 Haiku + 4 Opus threads at t=0. Cards ready in ~12s while 4 expert analysis streams fill the verdict column. No sequential bottlenecks.
- **Low over-refusals → villain voice** — Opus role-plays as the drafter's attorney, sustaining a hostile viewpoint across the entire document. Previous models would self-censor. Opus 4.6 fully commits.
- **Long-context retrieval → cross-clause detection** — The model holds the full document in working memory and reasons across distant clauses simultaneously to find compound risks invisible when reading clause by clause.
- **Adaptive thinking → per-thread depth** — Each Opus thread decides its own reasoning depth. A simple power ratio gets light analysis. A cascading penalty interaction gets deep reasoning.
- **Self-correction → quality check** — The overall thread reviews the analysis from all other threads for false positives and blind spots before presenting results.
- **Stylistic deduction → document archaeology** — Opus distinguishes boilerplate from custom-drafted clauses and builds a drafter profile from writing patterns.
- **Vision / multimodal** — PDF pages sent as images to detect visual formatting tricks (fine print, buried placement) that text extraction misses.
- **Analysis → action** — "Message the Company" generates a professional complaint letter citing specific clauses. Counter-draft rewrites unfair clauses.

The plugin is a **workflow tool** for professionals. FlipSide is a **thinking tool** for everyone else — and it uses more Opus 4.6 capabilities to get there.

---

## Problem Statement Fit

**Primary: Break the Barriers**
Legal document analysis is locked behind expertise ($300-500/hour attorneys) and cost. FlipSide puts it in everyone's hands.

**Secondary: Amplify Human Judgment**
FlipSide doesn't replace the user's decision to sign or not sign. It makes them dramatically more informed — human in the loop, but now with the other side's perspective visible.

---

## The Process

This project documents not just the product, but the entire decision-making process — including five documented AI failures and two new methodologies for working with AI:

| Document | What It Covers |
|----------|---------------|
| [Hackathon Log](HACKATHON_LOG.md) | 68 entries, complete process timeline |
| [Strategy Decisions](strategy.md) | 22 strategy decisions with rationale — including a midpoint self-evaluation |
| [The Prewash Method](docs/PREWASH_METHOD.md) | How to clean bias from AI prompts before execution |
| [Live Demonstration](docs/LIVE_DEMONSTRATION.md) | "Think Like a Document" demonstrated on the AI itself |
| [Prewash Prompt Collection](docs/PREWASH_PROMPT_COLLECTION.md) | 7 real before/after prompt examples |
| [Five AI Failures](docs/ANCHORING_FAILURE.md) | Confirmation bias, framing bias, vocabulary bias, adjective bias, format rigidity — all caught by the human |
| [All docs](docs/) | 18+ methodology and decision documents |

## What's Next

- **Browser extension** — Flag Terms of Service on any website before you click "I Agree." The same pipeline, triggered by a single button on any page with legal text.
- **Collaborative review** — Share your analysis with a lawyer or community group via link.
- **Benchmarking** — Compare your lease or insurance policy against anonymized analyses of similar documents. "Your landlord's late fee clause is harsher than 82% of leases we've seen."

## Builder

**Henk van Ess** — International OSINT expert, journalist trainer, tool builder. Assessor for IFCN and EFCSN. Early Bellingcat contributor. 20+ years verification methodology. CHI 2026 paper on "Think Like a Document." 10,000+ newsletter subscribers from BBC, NYT, Reuters, Europol, Harvard, MIT, NATO. See [BUILDER_PROFILE.md](BUILDER_PROFILE.md).

## Hackathon

Built with Opus 4.6: a Claude Code Hackathon (February 2026)

---

## Third-Party Licenses

FlipSide is [MIT licensed](LICENSE). It uses the following open-source libraries:

| Library | License | Use |
|---------|---------|-----|
| [Flask](https://flask.palletsprojects.com/) | BSD-3-Clause | Web framework |
| [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) | MIT | Claude API client |
| [python-docx](https://python-docx.readthedocs.io/) | MIT | DOCX text extraction |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | MIT | PDF text extraction |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | BSD-3-Clause | Environment variables |
| [marked.js](https://marked.js.org/) | MIT | Markdown rendering |
| [DOMPurify](https://github.com/cure53/DOMPurify) | Apache-2.0 / MPL-2.0 | XSS sanitization |
| [DM Sans](https://fonts.google.com/specimen/DM+Sans) | Open Font License | Body typography |
| [JetBrains Mono](https://www.jetbrains.com/lp/mono/) | Open Font License | Monospace labels |

---

## Why This Is Open Source

FlipSide is released under the [MIT License](LICENSE) — free for anyone to use, modify, and distribute.

This project was built entirely with Claude Code by someone who does not write code. Every line — the Flask backend, the SSE streaming architecture, the 5-thread parallel pipeline, the flip card frontend — was written through conversation with Claude Opus 4.6.

That changes who gets to build software. If a journalist with zero programming experience can ship a 5,918-line frontend and a 2,514-line backend in a weekend, then the barrier to building tools is gone. The only barrier left is having something worth building.

This is in the public domain of ideas because the tools that made it possible should produce things that are accessible to everyone. The people who need FlipSide most — tenants, patients, borrowers, app users — are the same people who could never afford to hire a developer to build it. Now they don't have to.

---

<sub>FlipSide: the dark side of small print. Built during the Claude Code Hackathon 2026.</sub>
