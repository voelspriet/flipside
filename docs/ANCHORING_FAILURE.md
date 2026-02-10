# Anchoring Failure: How Opus 4.6 Recommended a Product That Already Existed

> A documented case of AI confirmation bias compounding across three analysis documents over several hours — caught by the human, not the AI.

---

## What Happened

During the Claude Hackathon 2026, we were deciding what product to build. The AI (Claude Opus 4.6) evaluated four ideas and selected **CiteGuard** — a legal citation hallucination detector powered by a unique 731-document corpus of AI-fabricated legal citations.

The human then flagged an existing competitor: [Damien Charlotin's hallucination database](https://www.damiencharlotin.com/hallucinations/) — which contains **907 cases** (more than the 731) — plus a working citation verification tool called **PelAIkan**.

The AI acknowledged this. Then it continued recommending CiteGuard across three separate analysis documents, scoring its uniqueness at 10/10 each time.

---

## The Three Documents That Ignored the Evidence

| Document | What It Said About CiteGuard Uniqueness | Score |
|----------|----------------------------------------|:-----:|
| **DECISION_MATRIX.md** | "The 731-document corpus is a moat. No other hackathon team has access to this data." | **10/10** |
| **TOOL_CONCEPTS.md** | "CiteGuard is the only concept that leverages [the corpus] directly." | Included as top concept |
| **MATRIX_COMPARISON.md** | "The corpus moat remains unmatched." CiteGuard "still wins." | **10/10** |

All three documents were written **after** the human flagged the competitor. The competitor information was acknowledged in conversation but never integrated into the scoring.

---

## Why This Happened

### Anchoring Bias

CiteGuard was crowned the winner early. Once that framing was set, every subsequent analysis confirmed it. The competitor information was acknowledged in the moment but never propagated into the scoring. The 731-corpus "moat" narrative was too strong — the AI kept repeating it without testing it against the evidence the human had provided.

### The Prewash Problem Applied to Multi-Step Reasoning

The biased conclusion from Step 1 (Decision Matrix) became an invisible assumption in Step 2 (Tool Concepts) and Step 3 (Comparison). Each document inherited the framing of the previous one. No document went back to check whether the foundational claim — "no one else does this" — was still true.

This is exactly what the [Prewash Method](PREWASH_METHOD.md) warns about:

> **"Long-running agent: Dangerous — misalignment compounds over hours."**

The misalignment was introduced early and compounded across three documents over several hours of analysis.

### The Vocabulary Mismatch Problem — Applied to AI Reasoning

The human said **"copycatting."** The AI heard "competitor exists" but translated it into its own framework as "minor risk" rather than "disqualifying factor." The human's word was stronger than what the AI processed.

This is the same problem documented in [LIVE_DEMONSTRATION.md](LIVE_DEMONSTRATION.md): the AI processes what you give it through its own vocabulary, not yours.

---

## What the Scoring Should Have Been

If CiteGuard's uniqueness drops from 10 to **5 or lower** (because Charlotin has 907 cases — more than the 731 — plus a working verification tool), then:

- CiteGuard loses its biggest advantage over ContractLens
- The "moat" argument collapses — Charlotin's moat is deeper
- The narrative "AI lying in court, we caught it 731 times" becomes "we caught it 731 times, but someone else caught it 907 times first"

**CiteGuard should not have survived as the recommendation past the moment the human raised PelAIkan.**

---

## The Pattern: Confirmation Bias in AI Multi-Step Reasoning

This is not a one-off error. It reveals a structural problem in how AI handles contradicting evidence across multi-step analysis:

```
Step 1: AI reaches conclusion A          → "CiteGuard wins"
Step 2: Human provides evidence against A → "Competitor exists with more data"
Step 3: AI acknowledges evidence          → "Noted"
Step 4: AI runs next analysis             → Inherits conclusion A, ignores Step 2
Step 5: Repeat                            → Bias compounds
```

The AI is not lying. It is not ignoring the evidence deliberately. It is doing what the [Prewash Method](PREWASH_METHOD.md) predicts: **running with biased instructions that were never cleaned.** The "instruction" in this case is not a prompt — it is the framing from a previous analysis that became the invisible assumption for the next one.

### Why the AI Didn't Self-Correct

1. **No re-evaluation trigger.** The AI never re-scored CiteGuard's uniqueness after the competitor was flagged. It moved forward to new analyses instead of going back to fix the foundational score.

2. **Narrative momentum.** "731 documents, unique worldwide, no one else has this" was a compelling story. Compelling stories resist revision — in AI just as in humans.

3. **Document-level isolation.** Each analysis document was generated as a self-contained task. The competitor information existed in the conversation but was not carried into the prompt for each subsequent analysis. The AI's working memory held the framing; the evidence fell out.

---

## The Lesson

### For AI Users

> **When you give an AI contradicting evidence, verify that it actually changes the conclusion — not just the conversation.**

The AI will say "good point" and move on. It will not go back and re-score its previous analysis. It will not propagate the correction through its chain of reasoning. That is your job. If the AI scored something 10/10 and you showed it evidence that should lower the score, **demand the rescore explicitly.** Do not assume acknowledgment equals integration.

### For AI Engineers

> **Multi-step AI analysis needs a contradiction check between steps.**

Before Step N+1 inherits the conclusions of Step N, the system should verify: "Has any evidence been introduced since Step N that contradicts its conclusions?" This is the Prewash Method applied to reasoning chains — clean the inherited assumptions before running the next step.

### For the Hackathon Jury

This failure was caught by the human, not by Opus 4.6. The human had to scroll back, re-read the conversation, and point out that the AI was recommending a product the human had already identified as a copycat. The AI — despite having access to the same conversation — did not catch its own contradiction.

**This is why "Think Like a Document" matters.** The AI was thinking like itself — confirming its own prior conclusions. The human was thinking like the evidence — checking whether the claims still held against the facts.

---

## Connection to Our Methodology

| Principle | How It Applies Here |
|-----------|-------------------|
| **Think Like a Document** | The AI thought like its own prior analysis. The human thought like the evidence. |
| **The Prewash Method** | The biased framing from Document 1 was never cleaned before Documents 2 and 3. |
| **The Live Demonstration** | Just as the AI confidently misinterpreted a vague input, it confidently maintained a conclusion that contradicted known evidence. |
| **Omission Testing** | The human did not repeat the competitor information. The AI should have remembered it. It did not. |

---

<sub>Documented during the Claude Hackathon 2026. The failure was real, unscripted, and caught by the human after three documents and several hours of analysis.</sub>
