# FlipSide

**The dark side of small print.**

> Upload a document you didn't write. See what the other side intended.

---

## The Problem

Every day, 250 million+ people accept documents they did not draft and do not fully understand: contracts, Terms of Service, insurance policies, loan agreements, employee handbooks, HOA rules, medical consent forms.

These documents are written by one party's legal team to protect that party's interests. The person signing sees the words. They do not see the strategy behind the words.

There is no tool that shows you what a document looks like from the other side — from the perspective of the party who drafted it.

---

## What FlipSide Does

You upload a document. FlipSide reads it as if it were the drafter's attorney — the person who wrote it and knows exactly why every clause is there. Then it tells you what it found.

**One input. One perspective flip. One output.**

### The Three Steps

1. **Upload** — Drag in a PDF, DOCX, or paste text.

2. **Browse flip cards** — Cards appear one at a time within seconds. Each card is a clause:
   - **Front**: A calm green header bar with a reassurance headline ("Your flexible payment timeline ✓") followed by the reader's naive impression in first person. This is how the drafter WANTS you to feel. The green framing lulls you.
   - **Back**: What the drafter intended — a red/yellow risk header with villain voice, the key figure in large bold type ("$4,100 in penalties"), a concrete example scenario, and bottom-line action. The sidebar dims to 35% opacity to spotlight the reveal; the green front fades out during the 3D flip.
   - **Confidence badge**: HIGH / MEDIUM / LOW — how certain Opus is about each finding
   - Color-coded: **Green** (standard) · **Yellow** (notable) · **Red** (strategically asymmetric)
   - **Bilingual**: Non-English documents include collapsible English translations per card
   - **Document preview**: Sidebar shows the full document text with page dividers and numbered clause markers (①②③) that highlight when you navigate cards. Fuzzy matching ensures markers appear even when PDF text extraction differs from model quotes.

3. **Read the Full Verdict** — After browsing cards, Opus 4.6's deep analysis reveals:
   - Cross-clause interactions (risks invisible when reading clause by clause)
   - A villain voice per finding ("The math does the work — once they're two days late, the waterfall makes it impossible to get current")
   - **→ YOUR MOVE**: one concrete action per finding
   - **Fair Standard Comparison**: how the worst clauses compare to industry norms
   - **Who Drafted This**: a profile of the drafter and what it signals
   - **Quality Check**: Opus reviews its own analysis for false positives and blind spots
   - **How Opus 4.6 Analyzed This**: methodology disclosure — what techniques were used

4. **Ask follow-up questions** — After the verdict, ask anything about the document:
   - "What happens if I'm 3 months late on rent?"
   - "Which clauses can I actually negotiate?"
   - "Explain clause 4 like I'm 16"
   - Opus 4.6 traces the answer through all relevant clauses with extended thinking

---

## Who Uses It

| User | Document | What they learn |
|------|----------|----------------|
| **Freelancer** | Client contract | A non-compete clause covers their entire skill set for 18 months worldwide |
| **Tenant** | Lease agreement | "Repairs not covered by building insurance" means they pay for plumbing, electrical, and HVAC |
| **Homeowner** | Insurance policy | Two exclusion clauses interact to deny most real-world water damage claims |
| **Employee** | Employee handbook | An at-will clause renders every other promise (discipline process, severance) unenforceable |
| **App user** | Terms of Service | "We may share with partners" means unrestricted sale to data brokers |
| **Borrower** | Loan agreement | A single late payment triggers a cascade of penalties designed to stack |
| **Patient** | Medical consent form | A liability waiver is placed after medical disclosures to benefit from the assumption that everything on the form is standard |

---

## 13 Opus 4.6 Capabilities in One Product

FlipSide uses more Opus 4.6 capabilities than any single feature would require — including five that Anthropic [specifically highlights in the Opus 4.6 announcement](https://www.anthropic.com/research/introducing-claude-opus-4-6): adaptive thinking, long-context retrieval, low over-refusals, effort controls, and context compaction. Each capability is **visible in the product** — not a behind-the-scenes optimization.

| # | Opus 4.6 Feature | What the user sees |
|---|-----------|-------------------|
| 1 | **Adaptive thinking** | Opus decides its own reasoning depth per clause — spending more on complex cross-clause interactions, less on boilerplate. The reasoning stream IS the interface, not overhead |
| 2 | **Long-context retrieval** | Cross-clause interaction detection across the full document. Clause 2(c) and Clause 2(e) together deny water claims — neither clause is dangerous alone. This is Opus 4.6's "76% on MRCR v2 8-needle" capability applied to legal traps deliberately spread across pages |
| 3 | **Low over-refusals** | Every red-flagged clause includes a villain voice — adversarial role-play where Opus adopts the drafter's perspective. Previous models would self-censor on this. Opus 4.6's low over-refusal rate means it can fully commit to the adversarial framing |
| 4 | **Effort controls** | The depth selector (Quick/Standard/Deep) maps to Opus 4.6's `effort` parameter (medium/high/max). Architecture ready; awaiting Python SDK support (v0.46.0 doesn't expose it yet). Currently using `max_tokens` as depth knob |
| 5 | **Context compaction** | After analysis, users ask follow-up questions. Each follow-up sends the full document + analysis as context. Compaction enables extended Q&A without hitting the context window |
| 6 | **Vision / multimodal** | PDF pages sent as images — Opus detects fine print, buried placement, visual hierarchy tricks invisible to text extraction |
| 7 | **Tool use** | `assess_risk` and `flag_interaction` tools structure findings with risk level, confidence %, trick type during deep analysis |
| 8 | **Confidence signaling** | Each flip card shows HIGH/MEDIUM/LOW confidence with hover-reveal reasoning |
| 9 | **Self-correction** | Quality Check — Opus reviews its own analysis for false positives and blind spots before presenting results |
| 10 | **Split-model parallel** | Haiku 4.5 for fast cards, Opus 4.6 for deep analysis, both running simultaneously |
| 11 | **Prompt caching** | System prompts cached server-side for 90% cost reduction on repeated analyses |
| 12 | **Benchmark comparison** | Fair Standard Comparison — worst clauses measured against industry norms |
| 13 | **Multilingual + bilingual** | Analyzes in the document's language (drafter's perspective), offers EN translations on each flip card and deep analysis summary. Two languages = two perspectives |

### Why Opus 4.6 Specifically

Five capabilities from [Anthropic's Opus 4.6 announcement](https://www.anthropic.com/research/introducing-claude-opus-4-6) are **structurally necessary** for FlipSide to work. Remove any one and the product degrades:

1. **Adaptive thinking — the reasoning IS the product.** The extended thinking stream is not hidden behind a loading spinner — it IS the interface. Users watch Opus adopt the drafter's perspective in real time. The model decides how deeply to reason per clause, spending more thinking tokens on complex cross-clause interactions and less on standard boilerplate. Most projects use extended thinking as a black box. FlipSide makes it visible.

2. **Long-context retrieval — finding legal traps spread across pages.** Anthropic reports "76% on MRCR v2 8-needle 1M — a qualitative shift in how much context a model can actually use." FlipSide applies this to cross-clause interaction detection: Clause 2(c) excludes water damage from "gradual seepage over 14 days." Clause 2(e) defines the inspection timeline at 30 days. Neither clause is dangerous alone. Together, they deny virtually all residential water damage claims. The model holds the entire document in working memory and reasons across distant clauses simultaneously.

3. **Low over-refusals — the villain voice works.** Every red-flagged clause includes adversarial role-play where Opus adopts the drafter's voice: *"The math does the work. Two weeks late once and you'll never catch up."* Previous models would self-censor, add disclaimers, or refuse the adversarial framing entirely. Opus 4.6's low over-refusal rate means the perspective flip — the core product mechanic — actually works.

4. **Effort controls — user-facing intelligence dial.** The depth selector (Quick/Standard/Deep) is designed to map directly to Opus 4.6's new `effort` parameter (Quick→medium, Standard→high, Deep→max). The UI and backend architecture are ready — currently using `max_tokens` as the depth knob because the `effort` parameter is not yet available in the Python SDK (v0.46.0). When the SDK adds support, it's a one-line change per preset. This is a NEW 4.6 API feature that FlipSide is built to expose directly in the UI.

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
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
        ┌──────────────┐      ┌─────────────────┐
        │   HAIKU 4.5  │      │   OPUS 4.6               │
        │              │      │                          │
        │  Card scan   │      │  Deep analysis           │
        │  No thinking │      │  Ext. thinking           │
        │  8K tokens   │      │  48K+ tokens             │
        │  Confidence  │      │  + Vision (PDF images)   │
        │  badges      │      │  + Tool use (assess_risk,│
        │              │      │    flag_interaction)      │
        │  ~5s: first  │      │  ~40-100s total          │
        │  flip card   │      │                          │
        └──────┬───────┘      └────────┬─────────────────┘
               │                       │
               ▼                       ▼
        Cards stream in          Buffered until
        one at a time            user requests it
               │                       │
               ▼                       ▼
        ┌──────────────────────────────────────┐
        │           FLIP CARDS                  │
        │  Front: Green ✓ "Everything's fine"  │
        │  Back:  Red ✗ "What they intended"   │
        │  Sidebar dims → card spotlighted     │
        │  Confidence: HIGH/MEDIUM/LOW          │
        │  User browses ← →                    │
        │                                      │
        │         "Full Verdict →"             │
        │               │                      │
        │               ▼                      │
        │         DEEP ANALYSIS                │
        │  Cross-clause interactions            │
        │  Villain voice per finding            │
        │  → YOUR MOVE action per section       │
        │  Fair Standard Comparison             │
        │  Who Drafted This (drafter profile)   │
        │  Quality Check (self-correction)      │
        │  How Opus 4.6 Analyzed This           │
        │  Overall Risk + Power Imbalance       │
        │               │                      │
        │               ▼                      │
        │         FOLLOW-UP                    │
        │  "What happens if I'm late?"         │
        │  Opus traces through all clauses     │
        └──────────────────────────────────────┘
```

Two models run in parallel: **Haiku 4.5** scans clauses fast (first card in ~5 seconds), while **Opus 4.6** with extended thinking reasons across all clauses simultaneously to find compound risks invisible when reading clause by clause. The user browses flip cards while Opus thinks in the background.

**Tech stack:** Python/Flask (1,387 lines), Server-Sent Events, Anthropic API (Haiku 4.5 + Opus 4.6 with extended thinking, vision, tool use, prompt caching), single-file HTML/CSS/JS frontend (4,207 lines). No external APIs beyond Anthropic. No database required. Bilingual analysis for non-English documents. Deployable behind a reverse proxy with URL prefix.

---

## The Demo Moment

The user uploads a real homeowner's insurance policy. Opus 4.6 begins reasoning as the insurer's underwriting counsel:

> *"Section 1 grants broad coverage for 'direct physical loss.' From the insurer's perspective, the strategic value of this broad grant is that it creates a feeling of total protection that makes the policyholder less likely to scrutinize the exclusions."*

> *"Exclusion 2(c) excludes water damage from 'gradual seepage over 14 days.' The insurer knows that most residential water damage IS gradual. The 14-day threshold means almost any water claim can be reclassified as 'gradual' after the fact."*

Clauses turn red as risks are identified. The audience — every one of whom has signed something they didn't fully understand — watches the other side's strategy become visible in real time.

---

## What This Is Not

- Not a legal advice tool (it analyzes documents, it does not give legal recommendations)
- Not a contract generator (it reads existing documents, it does not create new ones)
- Not a diff tool (it reveals strategic intent, not textual differences)
- Not a chatbot (it performs one analysis per document — though you can ask follow-up questions after)

---

## FlipSide vs. Anthropic's Legal Plugin

On February 2, 2026, Anthropic launched a [legal plugin for Claude Cowork](https://legaltechnology.com/2026/02/03/anthropic-unveils-claude-legal-plugin-and-causes-market-meltdown/) — enterprise contract review that crashed legal tech stocks by $50B+. FlipSide, built during this hackathon, approaches the same domain from the opposite direction. The plugin reviews contracts FOR legal teams. FlipSide reveals what the drafting team intended — for the 250M+ people who sign documents without a legal team. Same model. Different side of the table.

| | Anthropic Legal Plugin | FlipSide |
|---|---|---|
| **User** | In-house corporate counsel | Consumer who received a document they didn't write |
| **Perspective** | Reviews FROM your configured playbook | Flips TO the drafter's perspective — no playbook needed |
| **Opus 4.6 use** | Standard clause flagging | 13 capabilities: adaptive thinking, long-context retrieval, low over-refusals, effort controls, context compaction, vision, tool use, confidence signaling, self-correction, prompt caching, split-model parallel, benchmark comparison |
| **Input** | Contracts your legal team handles | Any document: leases, insurance, ToS, loans, employment, medical consent |
| **Output** | Redline suggestions, NDA triage | Flip cards ("What you'd think" → "What they intended"), villain voice, YOUR MOVE actions |
| **Requires** | Cowork enterprise license, MCP integrations, configured playbook | Nothing — upload and go |
| **Approach** | Automates what a lawyer already does | Reveals what the lawyer on the other side was thinking |

### How FlipSide pushes Opus 4.6 further

The legal plugin uses Opus for clause flagging and redline suggestions — standard contract review. FlipSide pushes Opus 4.6 into capabilities the plugin does not use:

- **Low over-refusals → villain voice** — Opus role-plays as the drafter's attorney, sustaining a hostile viewpoint across the entire document. Previous models would self-censor or add disclaimers. Opus 4.6's low over-refusal rate means it fully commits to the adversarial perspective that IS the product.
- **Long-context retrieval → cross-clause detection** — The model holds the full document in working memory and reasons across distant clauses simultaneously to find compound risks (penalty cascades, exclusion interactions) invisible when reading clause by clause. This is the "qualitative shift in how much context a model can actually use" that Anthropic describes.
- **Effort controls → user-facing intelligence dial** — Quick/Standard/Deep maps to the new `effort` API parameter (medium/high/max). Users choose their own speed/depth tradeoff.
- **Context compaction → follow-up without limits** — After analysis, users ask questions ("What happens if I'm 3 months late?") and Opus traces the answer through all clauses. Compaction enables extended Q&A sessions without hitting the context window.
- **Vision / multimodal** — PDF pages sent as images to detect visual formatting tricks (fine print, buried placement, table manipulation) that text extraction misses entirely.
- **Tool use during analysis** — `assess_risk` and `flag_interaction` tools force structured data (risk level, confidence %, trick type) alongside prose.

The plugin is a **workflow tool** for professionals. FlipSide is a **thinking tool** for everyone else — and it uses more Opus 4.6 capabilities to get there.

---

## Problem Statement Fit

**Primary: Break the Barriers**
Legal document analysis is locked behind expertise ($300-500/hour attorneys) and cost. FlipSide puts it in everyone's hands.

**Secondary: Amplify Human Judgment**
FlipSide doesn't replace the user's decision to sign or not sign. It makes them dramatically more informed — human in the loop, but now with the other side's perspective visible.

---

## The Process

This project documents not just the product, but the entire decision-making process — including three documented AI failures and two new methodologies for working with AI:

| Document | What It Covers |
|----------|---------------|
| [Hackathon Log](HACKATHON_LOG.md) | Timeline from kickoff to product selection |
| [The Prewash Method](docs/PREWASH_METHOD.md) | How to clean bias from AI prompts before execution |
| [Live Demonstration](docs/LIVE_DEMONSTRATION.md) | "Think Like a Document" demonstrated on the AI itself |
| [Prewash Prompt Collection](docs/PREWASH_PROMPT_COLLECTION.md) | 7 real before/after prompt examples |
| [Three AI Failures](docs/ANCHORING_FAILURE.md) | Confirmation bias, framing bias, vocabulary bias — all caught by the human |
| [Strategy Decisions](strategy.md) | 14 strategy decisions with rationale (debugging, meta-prompting, architecture, contrast pivot, fuzzy matching, "Think Like a Document" UX) |
| [All docs](docs/) | 18+ methodology and decision documents |

## Builder

**Henk van Ess** — International OSINT expert, journalist trainer, tool builder. Assessor for IFCN and EFCSN. Early Bellingcat contributor. 20+ years verification methodology. CHI 2026 paper on "Think Like a Document." 10,000+ newsletter subscribers from BBC, NYT, Reuters, Europol, Harvard, MIT, NATO. See [BUILDER_PROFILE.md](BUILDER_PROFILE.md).

## Hackathon

Built with Opus 4.6: a Claude Code Hackathon (February 2026)

---

<sub>FlipSide: the dark side of small print. Built during the Claude Code Hackathon 2026.</sub>
