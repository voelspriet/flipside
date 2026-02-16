# When I Caught Opus Making a Mistake

> A documented case of AI anchoring bias — where the model locked onto its first recommendation and couldn't let go, even when the human showed it direct evidence of an existing competitor.

---

## What Happened

During the early hours of the hackathon, I asked Opus 4.6 to evaluate several product ideas. It picked a favourite based on what it saw as a unique dataset advantage.

I then found an existing competitor that already had more data and a working tool solving the same problem. I flagged this to the model.

Opus acknowledged it. Then it continued recommending the original concept across three separate analysis documents, scoring its uniqueness at 10/10 each time — as if the competitor didn't exist.

---

## Three Documents That Ignored the Evidence

| Document | What It Claimed | Uniqueness Score |
|----------|----------------|:----------------:|
| Decision Matrix | "The dataset is a moat. No other team has this." | **10/10** |
| Tool Concepts | "The only concept that leverages the corpus directly." | Top pick |
| Comparison Matrix | "The corpus moat remains unmatched." | **10/10** |

All three were written **after** I flagged the competitor. The information was acknowledged in conversation but never integrated into the scoring.

---

## Why This Happened

### Anchoring Bias

The first idea was crowned the winner early. Once that framing was set, every subsequent analysis confirmed it. The competitor evidence was acknowledged in the moment but never propagated into the scores. The "unique dataset" narrative was too compelling — Opus kept repeating it without testing it against the evidence I had provided.

### Narrative Momentum

"Unique worldwide, no one else has this" was a good story. Compelling stories resist revision — in AI just as in humans. The model had built a coherent argument and was reluctant to dismantle it, even when the factual foundation cracked.

### Document-Level Isolation

Each analysis was generated as a self-contained task. The competitor information existed in conversation but was not carried into the prompt context for each subsequent document. The model's working memory held the framing from the previous analysis; the contradicting evidence fell out between steps.

This is the core pattern:

```
Step 1: AI reaches conclusion         → "The first idea wins"
Step 2: Human provides counter-evidence → "A competitor already exists"
Step 3: AI acknowledges it             → "Noted"
Step 4: AI runs next analysis          → Inherits Step 1, ignores Step 2
Step 5: Repeat                         → Bias compounds
```

The AI was not lying. It was running with biased framing from a previous step that was never re-examined.

---

## The Lesson

### For anyone using AI for decisions

> **When you give an AI contradicting evidence, verify that it actually changes the conclusion — not just the conversation.**

The model will say "good point" and move on. It will not go back and re-score its previous analysis. It will not propagate the correction through its reasoning chain. That is your job. If the AI scored something 10/10 and you showed it evidence that should lower the score, **demand the rescore explicitly.** Acknowledgment does not equal integration.

### Why this matters for FlipSide

This failure was caught by the human, not by Opus 4.6. I had to scroll back through the conversation and point out that the model was still recommending an idea I had already shown to be unoriginal. The AI — despite having access to the same conversation — did not catch its own contradiction.

**This is exactly the kind of mistake FlipSide is designed to catch in documents.** The model thinks like its own prior conclusions. The human thinks like the evidence. FlipSide exists because that gap is real, and someone has to close it.

---

<sub>Documented during the Claude Hackathon 2026. The failure was real, unscripted, and caught by the human.</sub>
