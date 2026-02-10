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
Four ideas evaluated against three inputs (strengths × jury × criteria). CiteGuard (legal citation hallucination detector) won on every dimension.
→ [docs/DECISION_MATRIX.md](https://github.com/voelspriet/flipside/tree/main/docs/DECISION_MATRIX.md)

**Entry 9 — FAILURE: Anchoring Bias**
The human had flagged an existing competitor (Damien Charlotin's 907-case database + PelAIkan tool). Despite this, Claude scored CiteGuard's uniqueness at 10/10 across three subsequent documents. The competitor evidence was acknowledged but never integrated into the scoring. CiteGuard recommendation invalidated.
→ [docs/ANCHORING_FAILURE.md](https://github.com/voelspriet/flipside/tree/main/docs/ANCHORING_FAILURE.md)

**Entry 10 — New Concepts via "Think Like a Document"**
Five new tool concepts generated using a Prewash-compliant prompt with 5 constraints and 5 required outputs. The principle was used as a generative design constraint, not just a search technique.
→ [docs/TOOL_CONCEPTS.md](https://github.com/voelspriet/flipside/tree/main/docs/TOOL_CONCEPTS.md)

**Entry 11 — Matrix Comparison**
Earlier decision matrix retested against new concepts using identical scoring. CiteGuard still led on jury fit (46/50) and criteria fit (9.15) but no longer won on every dimension. ContractLens emerged as the closest challenger.
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

## Three Documented AI Failures

Each failure was caught by the human, not by Opus 4.6. Each demonstrates a different bias pattern:

| # | Failure | Pattern | The AI did | The human did |
|---|---------|---------|-----------|--------------|
| 1 | [Live Demonstration](https://github.com/voelspriet/flipside/tree/main/docs/LIVE_DEMONSTRATION.md) | Training vocabulary bias | Projected its own framework onto a vague input | Revealed the structured version |
| 2 | [Anchoring Failure](https://github.com/voelspriet/flipside/tree/main/docs/ANCHORING_FAILURE.md) | Confirmation bias across documents | Maintained a conclusion despite contradicting evidence | Scrolled back and demanded accountability |
| 3 | [Framing Bias](https://github.com/voelspriet/flipside/tree/main/docs/FRAMING_BIAS_FAILURE.md) | Recency/context anchoring | Interpreted a new concept through its most recent topic | Showed the neutral version |

All three are the same error at different scales: **the AI uses itself as the measurement of things, rather than observing what must be there.** This is the problem "Think Like a Document" solves.

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
| [docs/](https://github.com/voelspriet/flipside/tree/main/docs) | 17 methodology and decision documents |
| [BUILDER_PROFILE.md](https://github.com/voelspriet/flipside/blob/main/BUILDER_PROFILE.md) | Who built this and what they bring |
| [Meta-Prompting_Explained.pdf](https://github.com/voelspriet/flipside/blob/main/Meta-Prompting_Explained.pdf) | Case study document for presentations |
| This file | The timeline connecting everything |

## What Does Not Exist Yet

- Product code (0 lines written)
- Demo video
- 100-200 word summary

**Deadline: February 16, 3:00 PM EST**

---

<sub>Maintained during the Claude Code Hackathon 2026. Every entry links to a detailed document in the docs/ folder.</sub>
