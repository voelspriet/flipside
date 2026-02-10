# FlipSide

**The other side of small print.**

Upload a document you didn't write — a contract, Terms of Service, insurance policy, loan agreement, employee handbook. FlipSide uses Claude Opus 4.6 extended thinking to adopt the perspective of the party who drafted it and reveals what each clause strategically accomplishes for them.

---

## How It Works

1. **Upload** a document (PDF, DOCX, or paste text)
2. **Watch** Opus 4.6 reason from the drafter's perspective in real time
3. **Read** clause-by-clause findings: what's standard, what's notable, what's asymmetric

## Why This Exists

250 million+ people regularly accept documents written by someone else's legal team. These documents are designed to protect the drafter — not the person signing. No tool existed to show you the other side's strategy. FlipSide does.

## The Principle

FlipSide applies **"Think Like a Document"** (CHI 2026, Henk van Ess) to one-sided documents:

> Don't read from your own perspective. Read from the perspective of the party who drafted it.

This is the same principle used in search ("don't search using your words — search using the document's words"), now applied to contract analysis.

## Built With

- Python / Flask
- Claude Opus 4.6 API with extended thinking
- Server-Sent Events (SSE) for real-time streaming
- No external APIs beyond Anthropic

## The Process

This project documents not just the product, but the entire decision-making process — including three documented AI failures and two new methodologies for working with AI:

| Document | What It Covers |
|----------|---------------|
| [Hackathon Log](HACKATHON_LOG.md) | Timeline from kickoff to product selection |
| [Product Concept](docs/FLIPSIDE_PRODUCT.md) | What FlipSide does and why |
| [The Prewash Method](docs/PREWASH_METHOD.md) | How to clean bias from AI prompts before execution |
| [Live Demonstration](docs/LIVE_DEMONSTRATION.md) | "Think Like a Document" demonstrated on the AI itself |
| [Prewash Prompt Collection](docs/PREWASH_PROMPT_COLLECTION.md) | 7 real before/after prompt examples |
| [Three AI Failures](docs/ANCHORING_FAILURE.md) | Confirmation bias, framing bias, vocabulary bias — all caught by the human |
| [All docs](docs/) | 18 methodology and decision documents |

## Builder

**Henk van Ess** — International OSINT expert, journalist trainer, tool builder. 20+ years verification methodology. CHI 2026 paper on "Think Like a Document." See [BUILDER_PROFILE.md](BUILDER_PROFILE.md).

## Hackathon

Built with Opus 4.6: a Claude Code Hackathon (February 2026)

**Problem Statement:** Break the Barriers — take something locked behind expertise and put it in everyone's hands.

---

<sub>FlipSide: the other side of small print. Built during the Claude Code Hackathon 2026.</sub>
