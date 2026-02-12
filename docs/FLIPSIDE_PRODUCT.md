# FlipSide: the dark side of small print

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

1. **Upload** — Drag in a PDF, DOCX, or paste text. Select your role (tenant, freelancer, policyholder, employee, app user, borrower, patient). Toggle: "Can you negotiate this document?" (Yes/No).

2. **Watch the reasoning** — Opus 4.6 extended thinking streams in real time. You see the AI adopt the drafter's perspective clause by clause. The reasoning is visible — not hidden behind a loading spinner.

3. **Read the findings** — Each clause is flagged:
   - **Green**: Standard boilerplate, no strategic concern
   - **Yellow**: Notable — creates expectations or shifts default assumptions
   - **Red**: Significantly asymmetric — strategically favors the drafter at your expense

   For negotiable documents: suggested revisions.
   For non-negotiable documents (ToS, insurance): "What this means for you" + "What to watch for."

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

Estimated user base: **~250 million+** (English/Dutch/German-speaking users who encounter one-sided documents).

---

## Why Opus 4.6 Extended Thinking

FlipSide cannot work with a lesser model. Here's why:

1. **Perspective adoption requires sustained reasoning.** Opus 4.6 must hold the entire document in context while reasoning from a different party's viewpoint for 10-15 steps per clause cluster. This is not summarization — it is adversarial role-play across a full legal document.

2. **Cross-clause interaction detection.** Insurance exclusions, penalty cascades, and indemnification asymmetries only become visible when the model reasons across multiple clauses simultaneously. Clause 2(c) and Clause 2(e) together deny water claims — neither clause does this alone.

3. **The reasoning IS the product.** The user watches the extended thinking stream in real time. The visible chain of reasoning — "I am now thinking like the insurer's underwriting counsel..." — is not a debug feature. It is the interface. It is what makes the analysis trustworthy and educational.

---

## The "Think Like a Document" Principle

FlipSide applies a published methodology (CHI 2026, Henk van Ess) to a new domain:

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
  Flask backend extracts text (PDF/DOCX/paste)
        │
        ▼
  Opus 4.6 API call with extended thinking
  System prompt: "You are the attorney who drafted this document.
  Analyze each clause from the drafter's strategic perspective.
  Explain what each clause accomplishes for the drafting party."
        │
        ▼
  SSE streaming → real-time reasoning displayed to user
        │
        ▼
  Structured output: clause-by-clause analysis
  with risk flags (green/yellow/red)
  and action options (revise or understand)
```

**Tech stack:** Python/Flask, Server-Sent Events, Anthropic API (Opus 4.6 with extended thinking), HTML/CSS frontend. No external APIs beyond Anthropic. No database required.

**Feasibility:** 5/5 — text in, analysis out. Proven SSE streaming pattern. The entire value is in prompt engineering and UI design.

---

## The Demo Moment

In the 3-minute demo video, the user uploads a real homeowner's insurance policy. Opus 4.6 begins reasoning as the insurer's underwriting counsel:

> *"Section 1 grants broad coverage for 'direct physical loss.' From the insurer's perspective, the strategic value of this broad grant is that it creates a feeling of total protection that makes the policyholder less likely to scrutinize the exclusions."*

> *"Exclusion 2(c) excludes water damage from 'gradual seepage over 14 days.' The insurer knows that most residential water damage IS gradual. The 14-day threshold means almost any water claim can be reclassified as 'gradual' after the fact."*

Clauses turn red as risks are identified. The audience — every one of whom has signed something they didn't fully understand — watches the other side's strategy become visible in real time.

---

## Problem Statement Fit

**Primary: Break the Barriers**
Legal document analysis is locked behind expertise ($300-500/hour attorneys) and cost. FlipSide puts it in everyone's hands.

**Secondary: Amplify Human Judgment**
FlipSide doesn't replace the user's decision to sign or not sign. It makes them dramatically more informed — human in the loop, but now with the other side's perspective visible.

---

## What This Is Not

- Not a legal advice tool (it analyzes documents, it does not give legal recommendations)
- Not a contract generator (it reads existing documents, it does not create new ones)
- Not a diff tool (it reveals strategic intent, not textual differences)
- Not a chatbot (it performs one analysis per document — no conversation needed)

---

<sub>Product concept for the Claude Hackathon 2026. Applies the "Think Like a Document" principle (CHI 2026, Henk van Ess) to one-sided documents using Opus 4.6 extended thinking.</sub>
