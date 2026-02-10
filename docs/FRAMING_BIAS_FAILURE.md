# Framing Bias Failure: How Recent Context Narrows AI Interpretation

> A third documented case of AI bias during the Claude Hackathon 2026. The AI interpreted a broad concept through the lens of its most recent conversation topic, producing a narrower answer than the user intended.

---

## What Happened

The user said:

> "We should introduce an option to compare different documents using 4.6 strengths and pushing boundaries — only applicable for people comparing stuff. Write a prompt for that."

The AI (Claude Opus 4.6) responded by interpreting this as a **feature of ContractLens** — the tool concept that had been discussed for the previous hour. The AI framed "compare documents" as comparing two insurance policies or two leases from the drafter's adversarial perspective.

The user then revealed their actual intent — a neutral, structured prompt:

> **Concept: a tool where users upload 2 or more documents and Opus 4.6 identifies contradictions, overlaps, and gaps between them using extended thinking.**
>
> Write a prompt that defines:
> - What document types this works for (legal filings, news articles, research papers, corporate reports — pick one or specify all)
> - What "comparison" means here: factual contradictions? different conclusions from same data? missing information in one that exists in another?
> - What Opus 4.6 extended thinking does that a simple diff tool cannot
> - What the user sees as output
> - A concrete example with two real document types

---

## The Gap Between AI's Interpretation and User's Intent

| Dimension | What the AI produced | What the user meant |
|-----------|---------------------|-------------------|
| **Scope** | A feature of ContractLens | A potentially standalone tool concept |
| **Document types** | Insurance policies, leases, contracts | Legal filings, news articles, research papers, corporate reports — any document |
| **What "comparison" means** | Strategic intent differences (one type) | Factual contradictions, divergent conclusions, information gaps (three types) |
| **Framework** | Adversarial/drafter perspective | Neutral — no predetermined framing |
| **Output** | Which contract is worse for you | Contradictions, overlaps, gaps between any two documents |

The AI produced a subset of what the user intended. The answer was not wrong — comparing insurance policies from the drafter's perspective is one valid application. But it was **one application out of many**, presented as if it were the whole concept.

---

## Why This Happened

### Recency Bias / Context Anchoring

The AI had spent the previous hour discussing ContractLens. When the user said "compare documents," the AI's most activated context was:
- ContractLens
- One-sided documents
- Adversarial perspective
- Insurance policies, leases, contracts

The AI interpreted the new input through this frame rather than treating it as a fresh concept. It heard "compare documents" and filled in "...like the ones we've been discussing" rather than asking "compare what kind of documents?"

### The Narrowing Pattern

This is the third documented instance of the same pattern during this hackathon:

| Instance | What the AI did | What it should have done |
|----------|----------------|------------------------|
| **[Live Demonstration](LIVE_DEMONSTRATION.md)** | Interpreted a vague input through its own vocabulary ("latent demand," "PageRank," "invisible infrastructure") | Asked what the user's structured requirements were |
| **[Anchoring Failure](ANCHORING_FAILURE.md)** | Maintained CiteGuard as the recommendation despite evidence of an existing competitor | Re-scored CiteGuard's uniqueness after the competitor was flagged |
| **Framing Bias (this document)** | Interpreted "compare documents" as "compare contracts from drafter's perspective" | Recognized that "compare documents" is underspecified and asked what types, what comparison means, and what output looks like |

The common thread: **the AI fills ambiguity with its own most recent or most confident frame, rather than recognizing the ambiguity and resolving it.**

---

## The User's Key Insight

> "The main fix: 'compare documents' can mean 50 things. The neutral version forces you to define what kind of comparison, for whom, and what the output looks like."

This is the Prewash Method applied to concept generation. The vague version ("compare documents") lets the AI project its own frame. The neutral version forces specificity before execution — eliminating the space where bias operates.

---

## Connection to Methodology

| Principle | How It Applies Here |
|-----------|-------------------|
| **Think Like a Document** | The AI thought like its own recent context, not like the user's intent. |
| **The Prewash Method** | The user's neutral rewrite strips the ambiguity that allowed the AI to project. "Compare documents" becomes three defined comparison types + specified document types + required output format. |
| **Anchoring Failure** | Same mechanism — a prior conclusion (ContractLens) became the invisible frame for a new question. |

### The Three Failures as a Progression

1. **Live Demonstration**: AI projects its *training vocabulary* onto user intent
2. **Anchoring Failure**: AI projects its *prior conclusion* onto new evidence
3. **Framing Bias**: AI projects its *recent conversation context* onto a new concept

All three are the same error at different scales: **the AI uses itself as the measurement of things, rather than observing what must be there.**

This is, ironically, the exact problem that "Think Like a Document" solves.

---

<sub>Documented during the Claude Hackathon 2026. Third instance in a series of three bias failures, all caught by the human.</sub>
