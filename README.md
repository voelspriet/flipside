# FlipSide

**The other side of small print.**

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
   - **Front**: What you'd think reading this ("seems fine, standard clause")
   - **Back**: What the drafter intended ("this lets us charge you for repairs we should cover")
   - Color-coded: **Green** (standard) · **Yellow** (notable) · **Red** (strategically asymmetric)

3. **Read the Full Verdict** — After browsing cards, Opus 4.6's deep analysis reveals:
   - Cross-clause interactions (risks invisible when reading clause by clause)
   - A villain voice per finding ("The math does the work — once they're two days late, the waterfall makes it impossible to get current")
   - **→ YOUR MOVE**: one concrete action per finding
   - Overall Risk Score with context-aware severity labels

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

## Why Opus 4.6 Extended Thinking

FlipSide cannot work with a lesser model. Here's why:

1. **Perspective adoption requires sustained reasoning.** Opus 4.6 must hold the entire document in context while reasoning from a different party's viewpoint for 10-15 steps per clause cluster. This is not summarization — it is adversarial role-play across a full legal document.

2. **Cross-clause interaction detection.** Insurance exclusions, penalty cascades, and indemnification asymmetries only become visible when the model reasons across multiple clauses simultaneously. Clause 2(c) and Clause 2(e) together deny water claims — neither clause does this alone.

3. **The reasoning IS the product.** The user watches the extended thinking stream in real time. The visible chain of reasoning — "I am now thinking like the insurer's underwriting counsel..." — is not a debug feature. It is the interface. It is what makes the analysis trustworthy and educational.

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
        │   HAIKU 4.5  │      │   OPUS 4.6      │
        │              │      │                 │
        │  Card scan   │      │  Deep analysis  │
        │  No thinking │      │  Ext. thinking  │
        │  8K tokens   │      │  48K+ tokens    │
        │              │      │                 │
        │  ~5s: first  │      │  ~80-100s total │
        │  flip card   │      │                 │
        └──────┬───────┘      └────────┬────────┘
               │                       │
               ▼                       ▼
        Cards stream in          Buffered until
        one at a time            user requests it
               │                       │
               ▼                       ▼
        ┌──────────────────────────────────────┐
        │           FLIP CARDS                  │
        │                                      │
        │  Front: "What you'd think"           │
        │  Back:  "What they intended"          │
        │                                      │
        │  User browses ← →                    │
        │                                      │
        │         "Full Verdict →"             │
        │               │                      │
        │               ▼                      │
        │         DEEP ANALYSIS                │
        │  Cross-clause interactions            │
        │  Villain voice per finding            │
        │  → YOUR MOVE action per section       │
        │  Who Drafted This (drafter profile)   │
        │  Overall Risk + Power Imbalance       │
        └──────────────────────────────────────┘
```

Two models run in parallel: **Haiku 4.5** scans clauses fast (first card in ~5 seconds), while **Opus 4.6** with extended thinking reasons across all clauses simultaneously to find compound risks invisible when reading clause by clause. The user browses flip cards while Opus thinks in the background.

**Tech stack:** Python/Flask, Server-Sent Events, Anthropic API (Haiku 4.5 + Opus 4.6 with extended thinking), single-file HTML/CSS/JS frontend. No external APIs beyond Anthropic. No database required.

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
- Not a chatbot (it performs one analysis per document — no conversation needed)

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
| [All docs](docs/) | 18 methodology and decision documents |

## Builder

**Henk van Ess** — International OSINT expert, journalist trainer, tool builder. Assessor for IFCN and EFCSN. Early Bellingcat contributor. 20+ years verification methodology. CHI 2026 paper on "Think Like a Document." 10,000+ newsletter subscribers from BBC, NYT, Reuters, Europol, Harvard, MIT, NATO. See [BUILDER_PROFILE.md](BUILDER_PROFILE.md).

## Hackathon

Built with Opus 4.6: a Claude Code Hackathon (February 2026)

---

<sub>FlipSide: the other side of small print. Built during the Claude Code Hackathon 2026.</sub>
