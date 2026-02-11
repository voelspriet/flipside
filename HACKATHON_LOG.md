# Hackathon Log: FlipSide

## Built with Opus 4.6 — Claude Code Hackathon, February 2026

> This log documents the complete decision process from hackathon kickoff to product selection. Every methodology, failure, and pivot is documented in the [docs/](https://github.com/voelspriet/flipside/tree/main/docs) folder. This file is the timeline — the docs contain the detail.

---

## The Product

**FlipSide: the other side of small print.**

Upload a document you didn't write — a contract, Terms of Service, insurance policy, loan agreement, employee handbook. Opus 4.6 adopts the perspective of the party who drafted it and reveals what each clause strategically accomplishes for them.

**Problem Statement:** Break the Barriers — take something locked behind expertise (legal document analysis) and put it in everyone's hands.

---

## Timeline

### Phase 0: Process Setup (before any product decision)

**Entry 1 — Meta-Prompting**
Instead of asking Claude to build a documentation agent, we asked it to *design the prompt for itself first*. This established the workflow for the entire hackathon: generate the prompt → review it → clean it → execute it.
→ [docs/META_PROMPTING.md](https://github.com/voelspriet/flipside/tree/main/docs/META_PROMPTING.md)

**Entry 2 — Jury Research**
Researched all 5 judges before choosing a project. Caught a critical factual error: Claude's training data incorrectly linked judge Thariq Shihipar to Upsolve (a nonprofit). Live web research proved this was wrong — Thariq is a serial entrepreneur (One More Multiverse, $17M raised). This correction changed the entire strategic direction.
→ [docs/JURY_RESEARCH_LIVE.md](https://github.com/voelspriet/flipside/tree/main/docs/JURY_RESEARCH_LIVE.md)

**Entry 3 — Omission Test**
Deliberately withheld the judging criteria to test whether Opus 4.6 would identify it as a missing variable. It did, unprompted. This validated that the model reasons about problem structure, not just surface inputs.

**Entry 4 — Criteria Analysis**
Full hackathon brief analyzed: Demo 30%, Opus 4.6 Use 25%, Impact 25%, Depth 20%. Two special prizes identified as targets: "Most Creative Opus 4.6 Exploration" and "The Keep Thinking Prize."
→ [docs/HACKATHON_BRIEF.md](https://github.com/voelspriet/flipside/tree/main/docs/HACKATHON_BRIEF.md) | [docs/CRITERIA_ANALYSIS.md](https://github.com/voelspriet/flipside/tree/main/docs/CRITERIA_ANALYSIS.md)

---

### Phase 1: Methodology Discovery

**Entry 5 — The Prewash Method**
Claude wrote a research prompt containing adjective bias ("brutally honest," "is it forced?"). The human caught it before execution. This led to documenting The Prewash Method — a two-cycle technique for cleaning AI prompts:
- Cycle 1: Remove adjective bias
- Cycle 2: Replace vague language with measurable criteria
→ [docs/PREWASH_METHOD.md](https://github.com/voelspriet/flipside/tree/main/docs/PREWASH_METHOD.md)

**Entry 6 — Live Demonstration**
The human gave Claude a deliberately vague input. Claude interpreted it confidently through its own vocabulary. The human then revealed the actual structured prompt — proving that "Think Like a Document" applies to AI reasoning itself. Documented verbatim.
→ [docs/LIVE_DEMONSTRATION.md](https://github.com/voelspriet/flipside/tree/main/docs/LIVE_DEMONSTRATION.md)

**Entry 7 — Prewash Prompt Collection**
Seven real before/after prompt examples collected as an educational resource. Shows what Cycle 1 removes and what Cycle 2 fixes in each case.
→ [docs/PREWASH_PROMPT_COLLECTION.md](https://github.com/voelspriet/flipside/tree/main/docs/PREWASH_PROMPT_COLLECTION.md)

---

### Phase 2: Product Selection (and Three AI Failures)

**Entry 8 — Initial Decision Matrix**
Four ideas evaluated against three inputs (strengths × jury × criteria). An initial winner was selected based on a proprietary dataset advantage.
→ [docs/DECISION_MATRIX.md](https://github.com/voelspriet/flipside/tree/main/docs/DECISION_MATRIX.md)

**Entry 9 — FAILURE: Anchoring Bias**
The human had flagged an existing competitor that already solved the same problem. Despite this, Claude scored the initial winner's uniqueness at 10/10 across three subsequent documents. The competitor evidence was acknowledged but never integrated into the scoring. Recommendation invalidated.
→ [docs/ANCHORING_FAILURE.md](https://github.com/voelspriet/flipside/tree/main/docs/ANCHORING_FAILURE.md)

**Entry 10 — New Concepts via "Think Like a Document"**
Five new tool concepts generated using a Prewash-compliant prompt with 5 constraints and 5 required outputs. The principle was used as a generative design constraint, not just a search technique.
→ [docs/TOOL_CONCEPTS.md](https://github.com/voelspriet/flipside/tree/main/docs/TOOL_CONCEPTS.md)

**Entry 11 — Matrix Comparison**
Earlier decision matrix retested against new concepts using identical scoring. The initial winner still led on two dimensions but no longer won on every dimension. ContractLens emerged as the strongest concept.
→ [docs/MATRIX_COMPARISON.md](https://github.com/voelspriet/flipside/tree/main/docs/MATRIX_COMPARISON.md)

**Entry 12 — Expanded Reach**
Each concept modified for broader user base. ContractLens expanded from "contracts" to "any one-sided document" (ToS, insurance, loans, HOA rules), growing from ~50M to ~250M+ potential users with zero added complexity. ContractLens ranked #1.
→ [docs/EXPANDED_REACH.md](https://github.com/voelspriet/flipside/tree/main/docs/EXPANDED_REACH.md)

**Entry 13 — Problem Deep Dive**
10 real problems identified. Three lenses applied (most users, most financial damage, least served). The Policyholder's Exclusion Maze appeared in all three lists: ~30M users/year, $10K–$50K per denied claim, zero existing tools.
→ [docs/CONTRACTLENS_PROBLEMS.md](https://github.com/voelspriet/flipside/tree/main/docs/CONTRACTLENS_PROBLEMS.md)

**Entry 14 — FAILURE: Framing Bias**
The human asked about a document comparison feature. Claude narrowed it to "compare two insurance policies" because it was anchored on ContractLens. The human's actual intent was broader: any two documents, three comparison types (contradictions, divergent conclusions, gaps). Third documented instance of AI interpreting through its most recent frame.
→ [docs/FRAMING_BIAS_FAILURE.md](https://github.com/voelspriet/flipside/tree/main/docs/FRAMING_BIAS_FAILURE.md)

**Entry 15 — Document Comparison Concept**
The broader comparison concept defined with three precise comparison types, five document pairings, and a concrete walkthrough (pharma press release vs. FDA response letter).
→ [docs/DOCUMENT_COMPARISON_CONCEPT.md](https://github.com/voelspriet/flipside/tree/main/docs/DOCUMENT_COMPARISON_CONCEPT.md)

**Entry 16 — Product Unity Analysis**
Tested whether ContractLens and document comparison could be one product. Answer: no — a single sentence cannot describe both to both audiences. Recommendation: build ContractLens only. The comparison tool's 2M users are 0.8% of ContractLens's 250M+.
→ [docs/PRODUCT_UNITY_ANALYSIS.md](https://github.com/voelspriet/flipside/tree/main/docs/PRODUCT_UNITY_ANALYSIS.md)

**Entry 17 — FlipSide**
Product named. Tagline chosen: *"FlipSide: the other side of small print."*

---

### Phase 3: Building the Product

**Entry 18 — First Working Prototype**
Flask backend + single HTML frontend. Core loop: upload document → Opus 4.6 extended thinking with SSE streaming → phased analysis output. PDF, DOCX, and paste-text extraction. Role selector (tenant, freelancer, policyholder, employee, etc.) and negotiability toggle. Sample homeowner's insurance policy embedded for instant demo.

**Entry 19 — The Meta-Prompting Framework**
System prompt redesigned to teach the model *how to think*, not just what to output. "Every clause exists for a reason — if it seems neutral, investigate what it enables." "The boring parts are the dangerous parts." This is the productized version of the two-step meta-prompting discovery from Entry 1 — the system prompt IS the pre-built reasoning framework, every document upload is the "execute" step.

**Entry 20 — Trick Taxonomy**
18 legal trick categories defined: Silent Waiver, Burden Shift, Time Trap, Escape Hatch, Moving Target, Forced Arena, Phantom Protection, Cascade Clause, Sole Discretion, Liability Cap, Reverse Shield, Auto-Lock, Content Grab, Data Drain, Penalty Disguise, Gag Clause, Scope Creep, Ghost Standard. Each clause is classified with one. This constrained vocabulary dramatically improved output consistency — the model no longer invents ad hoc categories.

**Entry 21 — "What the Small Print Says" vs. "What You Should Read"**
Replaced generic clause summaries with a forced juxtaposition: "What the small print says" (neutral restatement as a drafter would present it) vs. "What you should read" (what this actually means for you). The gap between the two IS the product's core insight. Every clause now makes the asymmetry visceral.

**Entry 22 — The Drafter's Playbook**
New analysis section: instead of just flagging individual clauses, reveal the *strategic architecture* of the entire document. "If I were the attorney who designed this, my strategic approach was: (1) Grant broad coverage upfront to suppress scrutiny... (2) Build layered exclusions that interact to deny claims..." This is the cross-clause reasoning that requires Opus 4.6's extended thinking — no other model holds the full document in context while reconstructing the drafter's strategy.

**Entry 23 — Auto-Detection**
Removed manual role selection and negotiability toggle from the required UI flow. The model now auto-detects from the document itself: who is the non-drafting party? Is this negotiable or take-it-or-leave-it? For negotiable documents: suggested revisions with Before/After quotes. For non-negotiable: "What to Watch For" with concrete scenarios.

**Entry 24 — Parallel Processing Architecture**
Single API call split into two parallel threads: a quick clause scan (fast, streams immediately) and a deep cross-clause analysis (full thinking budget, streams after quick scan completes). Uses `threading.Thread` + `queue.Queue` to interleave. The user sees clauses appearing within seconds while cross-clause reasoning runs in the background. This solved the "staring at a loading screen for 2 minutes" problem.

**Entry 25 — Depth Presets**
Three analysis modes: Quick (8K thinking budget, ~30s), Standard (16K, ~90s), Deep (32K, ~3min). Each adjusts both thinking budget and max output tokens. Deep mode enables the multi-pass cross-clause reasoning that finds the compound risks.

**Entry 26 — Document Comparison Mode**
Second major feature: upload two documents and compare them side by side. Identifies what's present in one but missing from the other, scores each area, and recommends the better deal. Originally rejected as a separate product (Entry 16), now integrated as a secondary mode within FlipSide. Same principle: think like the documents, not like the reader.

**Entry 27 — Multilingual Support**
Language rule added to all prompts: respond in the same language as the document. If the document is in Dutch, the entire analysis is in Dutch. No language selector needed — auto-detected from the document text. This opened FlipSide to non-English contracts with zero additional code.

**Entry 28 — Model ID and Thinking API Fix**
First user test revealed `claude-opus-4-6-20250219` (dated model ID) returned 404. Fixed to alias `claude-opus-4-6`. Also discovered `thinking.type: 'enabled'` is deprecated for Opus 4.6 — switched to `thinking.type: 'adaptive'`, which lets the model decide when and how deeply to think based on prompt complexity.

**Entry 29 — The Meta-Prompting Discovery (Cat Wu AMA)**
During the hackathon AMA, asked Cat Wu (Product Lead, Claude Code co-creator) about meta-prompting: why does "generate a prompt for X" then "execute it" consistently outperform directly asking "do X"? Cat confirmed the effect is real but the exact mechanism isn't fully understood. The observation: the two-step approach forces the model to separate planning from execution — it reasons about what makes a good analysis before actually analyzing. FlipSide's entire architecture is a productized version of this discovery.

---

### Phase 4: Self-Examination

**Entry 30 — FAILURE: Build Phase Documentation Gap**
We ran our own analysis prompt against this hackathon log. It found three failure modes:
1. The frontend (4,008 lines) had zero log entries — no documented examination against the project's own principles
2. Build-phase entries (18–27) document only outcomes, not iterations or failed attempts — unlike Phase 1–2, which documented failures explicitly
3. Entry 16 concluded comparison should be a separate product; Entry 26 integrated it into FlipSide without documenting what changed

This is the same pattern as the three AI failures (Entries 6, 9, 14): we applied rigorous methodology to the planning phase but not to the build phase. The Prewash Method was used on prompts but not on the UI text. "Acknowledgment is not integration" (Lesson 9) applied to us, not just the AI.

**Entry 31 — Why Comparison Mode Returned (Resolving Entry 16 → 26)**
Entry 16 rejected comparison as a separate product because: "a single sentence cannot describe both to both audiences." Entry 26 integrated it as a secondary mode. What changed: comparison was added not as a separate product but as a feature *within* FlipSide's existing interface — same upload flow, same analysis engine, same "think like the document" principle. The one-sentence test still passes: "FlipSide shows you what the other side intended when they wrote your document." Comparison is a second way to use the same perspective flip. The Entry 16 conclusion ("don't build two products") held — comparison became a feature, not a product.

**Entry 32 — Frontend Audit Against Project Principles**
Applied the Prewash Method and project principles to the frontend for the first time. Findings:
- **Prewash violation**: Tooltip text used adjectives and value judgments — "Severely one-sided," "Significantly unfair," "Standard or fair." These are the same kind of bias the Prewash Method catches in prompts. Fixed: replaced with factual, score-based descriptions.
- **Accessibility gaps**: Icon-only buttons (dark mode, font size, print, export) had no aria-labels. Form inputs (search, threshold slider) lacked proper labels. Risk indication used color alone. Fixed: added aria-labels, form labels, and text alongside color.
- **Streaming bug**: If the backend skipped the `text_start` event, results panel never appeared — user saw a blank screen. The `thinking_start` handler didn't work after the quick scan phase completed. Fixed both.
- **Marketing language in risk filter labels**: "Ok" / "Watch" / "Risk" replaced with score ranges.
The frontend was built without the same scrutiny applied to the prompts and decision process. This entry corrects that.

**Entry 33 — FAILURE: Prompting About Prompting Has the Same Bias**
Asked Claude to write a prompt analyzing our vibecoding process. The prompt contained adjective bias ("experienced practitioners," "what this builder does differently"), unverified claims ("most vibecoding starts with code in the first 5 minutes"), leading questions ("what does THIS builder treat as the product?"), and unmeasurable instructions ("analyze," "do not flatter"). The human caught it and demanded a Prewash-compliant rewrite. This is the fourth documented AI failure — and the first one caught during the self-examination phase. Same pattern: the AI uses framing language that looks neutral but carries embedded assumptions.

---

### Current State

| Artifact | Lines | Status |
|----------|-------|--------|
| `app.py` | 982 | Backend: Flask, SSE streaming, parallel processing, 4 prompt modes |
| `templates/index.html` | 4,008 | Full frontend: upload, compare, depth selector, phase indicators |
| `docs/` | 18 documents | Methodology, decisions, failures, corrections |
| `HACKATHON_LOG.md` | This file | 33 entries, complete process timeline |
| `README.md` | Product description + meta-prompting discovery |

---

## Four Documented AI Failures

Each failure was caught by the human, not by Opus 4.6. Each demonstrates a different bias pattern:

| # | Failure | Phase | Pattern | The AI did | The human did |
|---|---------|-------|---------|-----------|--------------|
| 1 | [Live Demonstration](https://github.com/voelspriet/flipside/tree/main/docs/LIVE_DEMONSTRATION.md) | Planning | Training vocabulary bias | Projected its own framework onto a vague input | Revealed the structured version |
| 2 | [Anchoring Failure](https://github.com/voelspriet/flipside/tree/main/docs/ANCHORING_FAILURE.md) | Planning | Confirmation bias across documents | Maintained a conclusion despite contradicting evidence | Scrolled back and demanded accountability |
| 3 | [Framing Bias](https://github.com/voelspriet/flipside/tree/main/docs/FRAMING_BIAS_FAILURE.md) | Planning | Recency/context anchoring | Interpreted a new concept through its most recent topic | Showed the neutral version |
| 4 | Meta-analysis prompt (Entry 33) | Self-examination | Adjective/framing bias | Wrote a prompt with "experienced," "differently," unverified claims, leading questions | Demanded Prewash-compliant rewrite |

All four are the same error at different scales: **the AI uses itself as the measurement of things, rather than observing what must be there.** This is the problem "Think Like a Document" solves.

---

## Lessons Learned

1. **Meta-prompting is worth the time.** Asking the AI to show its plan before executing adds 2 minutes and eliminates entire categories of misalignment.

2. **Process documentation can be a product.** What started as internal scaffolding became a publishable case study.

3. **Treat the jury as a design constraint.** Research evaluators the same way you research users — before you build.

4. **Always verify AI training data with live research.** The Thariq/Upsolve error would have misdirected the entire strategy.

5. **AI prompts carry invisible bias.** Every adjective is a policy decision. The Prewash Method catches them before they compound.
→ [docs/PREWASH_METHOD.md](https://github.com/voelspriet/flipside/tree/main/docs/PREWASH_METHOD.md)

6. **Removing bias is not enough — add precision.** "How well?" is unbiased but unmeasurable. "Rate 1-5" is both.

7. **AI confidence is not alignment.** "I understand" tells you nothing about whether it understood correctly.

8. **Re-examine conclusions when new evidence arrives.** The decision matrix was retested against new concepts. It held — partially.

9. **Acknowledgment is not integration.** When AI says "good point," verify that it actually changed the analysis, not just the conversation.

10. **Confirmation bias compounds across documents.** A biased conclusion in Document 1 becomes an invisible assumption in Document 3.

---

## What Exists

| Artifact | Purpose |
|----------|---------|
| `app.py` (982 lines) | Flask backend: 4 prompt modes, parallel processing, SSE streaming |
| `templates/index.html` (4,008 lines) | Full frontend: upload, compare, depth, phase indicators |
| [docs/](https://github.com/voelspriet/flipside/tree/main/docs) | 18 methodology and decision documents |
| [BUILDER_PROFILE.md](https://github.com/voelspriet/flipside/blob/main/BUILDER_PROFILE.md) | Who built this and what they bring |
| [Meta-Prompting_Explained.pdf](https://github.com/voelspriet/flipside/blob/main/Meta-Prompting_Explained.pdf) | Case study document for presentations |
| This file | 33 entries, complete process timeline |

## What Remains

- Demo video
- 100-200 word summary
- Final testing and polish

**Deadline: February 16, 3:00 PM EST**

---

<sub>Maintained during the Claude Code Hackathon 2026. Every entry links to a detailed document in the docs/ folder.</sub>
