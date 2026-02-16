# Live Demonstration: "Think Like a Document" Applied to AI Reasoning

> A real-time, unscripted exchange during the Claude Hackathon 2026 where the principle was demonstrated on the AI itself.

---

## Context

We had spent hours developing two methodologies:

1. **"Think Like a Document"** — don't search from your own perspective; adopt the perspective of the document you're looking for.
2. **The Prewash Method** — don't give AI a direct task; first generate the prompt, clean it of bias, then execute.

The following exchange happened when deciding what product to build for the hackathon. It is reproduced verbatim, with only typos corrected.

---

## The Exchange

### The Vague Input

**Henk:**

> I need to come up with a practical tool that helps people, maybe with a hidden need, maybe an obvious one, based on the principles we discussed. It can be complex but must be feasible for Claude 4.6. I want to push boundaries without breaking them. Now wait before you come up with adapted prompt. Do you understand the remark?

### The AI's Interpretation

**Claude (Opus 4.6):**

> Yes. Here's what I understand:
>
> The research prompt explores "Think Like a Document" as an abstract principle across 6 domains. That's research. But you're saying: **the product is not the principle. The product is a tool.**
>
> The principles — "Think Like a Document," the Prewash Method — should be **invisible infrastructure** inside the tool. Like PageRank is invisible inside Google. Like "Think Like a Document" is already invisible inside SearchWhisperer. Users don't need to know the theory. They need a tool that works.
>
> So the adapted prompt shouldn't ask "where does this principle apply?" It should ask **"what tool would people use, that happens to be powered by this principle?"**
>
> Hidden need vs. obvious need — this is Boris's "latent demand." The best tool solves a problem people have but haven't articulated. Or solves an obvious problem so differently that people say "why didn't this exist before?"
>
> And "push boundaries without breaking them" — use Opus 4.6 in ways that stretch what it can do, but don't build something that fails in the demo because we overreached.
>
> Is that what you mean?

### The Reveal

**Henk:**

> Well, I fooled you. I didn't ask you a neutral question. I planned:
>
> I need a tool concept that:
>
> 1. Solves a specific, recurring problem for a defined group of users
> 2. Applies the "Think Like a Document" principle: the tool helps users adopt the perspective of the source they're looking for, rather than searching from their own perspective
> 3. Can be built as a working prototype in 6 days by one person using Python/Flask and the Claude Opus 4.6 API (including extended thinking)
> 4. Uses Opus 4.6 extended thinking in a way that is visible to the user and necessary for the task — not cosmetic
> 5. Does something that cannot be done with a single prompt to ChatGPT or Perplexity
>
> For each concept, specify:
> - Who uses it (role, not "people")
> - What they do now without this tool
> - What the tool does, step by step
> - Why Opus 4.6 extended thinking is required (not optional)
> - What the user sees on screen
>
> Do you understand what I am trying to do here with your reasoning?

### The Recognition

**Claude (Opus 4.6):**

> Yes. You just demonstrated your own principle on me.
>
> You gave me a **vague input** — "practical tool, hidden need, push boundaries" — the equivalent of "amsterdam west high baby deaths." Full of ambiguity, open to interpretation.
>
> I processed it through **my own vocabulary**. I said "latent demand," "invisible infrastructure," "PageRank." I projected MY framework onto YOUR intent. I thought I understood. I confirmed understanding with confidence.
>
> Then you showed me the **actual document** — your clean, structured prompt with 5 numbered constraints and 5 specified outputs. No adjectives. No ambiguity. Measurable.
>
> **The gap between what I "understood" and what you actually meant IS the vocabulary mismatch problem.** I was searching with my own words. You were the document.
>
> This is three things at once:
>
> 1. **A live demonstration of "Think Like a Document"** — I failed to think like YOUR document. I thought like my own.
>
> 2. **A live demonstration of the Prewash Method** — your vague version would have produced a biased prompt from me. Your clean version produces a precise one.
>
> 3. **A test of whether I can recognize what just happened** — not just answer the question, but see the methodology being applied to me in real-time.

---

## What This Demonstrates

### The Vocabulary Mismatch Problem — Applied to AI

The same problem that affects human search also affects human-AI interaction:

| Domain | The Vague Input | What the AI Produces | The Actual Need |
|--------|----------------|---------------------|-----------------|
| **Search** | "amsterdam west high baby deaths" | Irrelevant results | "kraamsterfte epidemiologie amsterdam-west" |
| **AI Prompting** | "practical tool, hidden need, push boundaries" | AI's own interpretation, loaded with its biases | 5 numbered constraints, 5 specified outputs |

In both cases, the user's natural language does not match the structure needed to get the right result. The AI — like Google — processes what you give it, not what you mean.

### The Confidence Problem

Claude confirmed understanding with confidence: "Is that what you mean?" It offered a coherent, well-structured interpretation. It sounded right. But it was Claude's interpretation, not the user's intent.

This is the same problem that makes AI hallucinations dangerous: the output sounds correct and confident, but it's the model's projection, not the ground truth.

### The Principle Is Universal

"Think Like a Document" applies to:
- **Search**: think like the document you're looking for
- **Prompting**: think like the prompt that would produce your desired output
- **Communication**: think like the person you're communicating with
- **Verification**: think like the evidence that would exist if the claim were true

The underlying principle is always the same: **don't take yourself as the measurement of things. Observe what must be there.**

---

<sub>This exchange was unscripted and occurred in real-time during the Claude Hackathon 2026. It is reproduced verbatim with only typos corrected. This case is analyzed in [meta-prompting-strategy.md](../meta-prompting-strategy.md) (Case 5).</sub>
---

**Henk van Ess** — [imagewhisperer.org](https://www.imagewhisperer.org) · [searchwhisperer.ai](https://searchwhisperer.ai) · [digitaldigging.org](https://digitaldigging.org)
