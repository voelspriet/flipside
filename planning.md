# How FlipSide Was Born

The first thing I told Claude wasn't "build me an app." It was: here's how I think. That conversation took over 8 hours before a single line of code was written.

---

## The Starting Point: Two Ideas and a Model

I came to the hackathon with two things I'd spent years developing:

**"Think Like a Document"** — a methodology for AI-augmented query reformulation and enhanced information sensemaking.

**Meta-prompting** — a technique I'd discovered for getting better results from AI. Instead of telling Claude to do something, I said: *"Give me first a prompt for yourself that would do this."* ([verbatim transcript](docs/META_PROMPTING.md)) Then I read what it wrote, found the bias, cleaned it, and said "execute." The AI designs its own instructions — but I review them before they run. We later validated this across [30 agents and 8 real cases](meta-prompting-strategy.md).

I wanted to see what happens when you merge these two ideas with Opus 4.6.

---

## The Conversation

I explained both concepts to Claude. Not as a product brief — as a way of thinking. I described how "Think Like a Document" works in search, how the [Prewash Method](docs/PREWASH_METHOD.md) catches bias in prompts, and asked: what could we build that puts these principles inside a product?

Claude's first instinct was **CiteGuard** — a legal citation hallucination verifier. We built a [decision matrix](docs/DECISION_MATRIX.md) crossing three inputs: builder strengths, [jury interests](docs/JURY_RESEARCH_LIVE.md), and [judging criteria](docs/CRITERIA_ANALYSIS.md). CiteGuard scored highest on every dimension: 46/50 jury fit, 9.1/10 criteria fit, 10/10 uniqueness.

I deliberately withheld the judging criteria to test whether Opus 4.6 would identify it as a missing variable. It did, unprompted — presenting a table showing the gap before I revealed the data. ([HACKATHON_LOG](HACKATHON_LOG.md), Entry 3.)

Then I found Damien Charlotin's 907-case hallucination database and PelAIkan verification tool — a direct competitor. I told Claude. Claude said "good point" — and kept scoring CiteGuard's uniqueness at 10/10 across [three subsequent documents](docs/ANCHORING_FAILURE.md).

Saying "you're wrong" didn't work. The AI heard "copycatting" and translated it into its own framework as "minor risk" rather than "disqualifying factor." So I used the same technique that started this project — the meta-prompt:

> *"Write me a prompt that would evaluate whether CiteGuard's uniqueness claim still holds, given that a competitor already has 907 cases and a working verification tool."*

That changed everything. Instead of defending its conclusion, Claude had to design the criteria for testing it. The prompt it wrote included: *"Does the competitor's dataset overlap with ours? Is the overlap >50%? Does the competitor's tool already serve the same users?"* — questions it had never asked while it was busy confirming its own analysis.

When Claude executed its own evaluation prompt, CiteGuard's uniqueness dropped from 10/10 to 5/10. The entire recommendation collapsed.

That was the first real lesson: **acknowledgment is not integration.** Telling an AI "you're wrong" triggers acknowledgment. Asking it to *design the test for its own claim* triggers actual re-evaluation. The Prewash Method isn't just for cleaning prompts — it's for breaking through confirmation bias. The AI won't question itself, but it will write the prompt that questions itself.

This is also the core of "Think Like a Document": the AI was reading from its own perspective (confirming its prior conclusion). The meta-prompt forced it to read from the evidence's perspective (testing the claim against the competitor data).

---

## The Iteration

What followed was not a straight line. It was a conversation — sometimes an argument — between a human who knows how hidden information works and a model that knows how to write code.

Five new concepts were generated using a [Prewash-compliant prompt](docs/TOOL_CONCEPTS.md) with "Think Like a Document" as the organizing constraint. **ContractLens** emerged as the strongest ([Entry 11](HACKATHON_LOG.md)), was [expanded](docs/EXPANDED_REACH.md) from "contracts" to "any one-sided document," and eventually became [FlipSide](HACKATHON_LOG.md) (Entry 17).

The idea that survived: what if "Think Like a Document" applies to contracts? Every contract has a drafter. The drafter wrote it for a reason. If you could read from the drafter's perspective instead of your own, you'd see things you'd never notice as a reader.

That's when the flip card was born ([Decision 5](strategy.md)). Here's what one looks like — a real gym membership:

**Card front:**
> *"Your flexible cancellation options"*
>
> I'd think: OK, I can cancel anytime with 30 days' notice. That's pretty standard. And there's no cancellation fee listed in the summary. Seems fair for $29/month.

**Flip it →**

**Card back:**
> **BUT IN REALITY** — They keep charging while you wait.
>
> **$133 to leave a $29/month gym.** "30 business days" is 6 weeks. Two more payments of $29 plus a $75 "processing fee" buried in Section 8.2. The "no cancellation fee" on the front refers to the membership fee only — the processing fee is classified as an "administrative charge."

The front shows what the drafter wants you to feel. The back shows what they actually intended. The gap between the two is the product. The card front was refined into what we called "Reassurance as Weapon" ([Decision 10](strategy.md)) — the green header that lulls the reader. The design principle — "the comparison lives in memory, not on screen" ([Decision 16](strategy.md)) — meant no split-screen juxtaposition. You remember the front. You flip. The reveal hits harder because you trusted the front.

The perspective flip only works if both sides are convincing. Opus 4.6 was the first model that fully committed to the naive voice without self-censoring — Anthropic reports it has the [lowest rate of over-refusals among all recent Claude models](https://www.anthropic.com/news/claude-opus-4-6).

---

## The Architecture That Emerged

Through 7 major restructurings (each >500 lines changed — [coding.md](coding.md)), the architecture evolved:

1. **Single Opus pass** — too slow, 60+ seconds
2. **Haiku cards + Opus backs** — fast fronts, but Opus backs blocked the stream
3. **All Opus, 4 parallel threads** — interactions, asymmetry, archaeology, overall ([Decision 21](strategy.md))
4. **Haiku does full cards (front + back)** — the breakthrough. We'd assumed the flip needed Opus. [It didn't](strategy.md) (Decision 22: "Haiku Was Already Great at Cards")
5. **Parallel Haiku workers** — N cards simultaneously. First card at ~8s
6. **Single Opus verdict** — consolidated 4 threads into one pass, offered deep dives on demand
7. **6 parallel Opus threads** — verdict + 5 specialist reports, all from t=0. Wall-clock cost of 6 is the same as 1

Each pivot came from the same pattern: I'd look at the product and say "this doesn't feel right." Claude would diagnose why and propose a fix. Sometimes the fix was wrong and we'd try again. Sometimes I was wrong and Claude would explain why.

The meta-prompting technique was baked into every step. I never told Claude "write a prompt for analyzing contracts." I said "write me a prompt that would make you think like the drafter of this contract." The system prompt IS a meta-prompt — it teaches the model a way of thinking before any document arrives. The user never sees this. They just see better results.

---

## Five Failures, One Thesis

Along the way, Claude failed five times. I caught all five. Each is documented with the original evidence.

| # | Failure | Entry | Evidence |
|---|---------|-------|----------|
| 1 | Training vocabulary bias | [Entry 6](HACKATHON_LOG.md) | [docs/LIVE_DEMONSTRATION.md](docs/LIVE_DEMONSTRATION.md) — verbatim transcript |
| 2 | Anchoring bias | [Entry 9](HACKATHON_LOG.md) | [docs/ANCHORING_FAILURE.md](docs/ANCHORING_FAILURE.md) — 10/10 across 3 documents |
| 3 | Framing bias | [Entry 14](HACKATHON_LOG.md) | [docs/FRAMING_BIAS_FAILURE.md](docs/FRAMING_BIAS_FAILURE.md) — narrowed to insurance |
| 4 | Adjective bias | [Entry 33](HACKATHON_LOG.md) | Prompt contained "brutally honest" — priming for negative evaluation |
| 5 | Format rigidity | [Entry 36](HACKATHON_LOG.md) | Haiku silently broke every parser by drifting from the specified output format |

The first four are the same error at different scales: the AI uses itself as the measurement of things, rather than observing what must be there.

That sentence is also the core of "Think Like a Document." The methodology I taught the machine is the same methodology I used to catch its mistakes. Man and machine, using the same principle, correcting each other.

---

## What This Produced

8+ hours of planning. 89 commits. 7 architecture pivots. 14,600+ lines of code (3,861 backend + 10,748 frontend — [coding.md](coding.md)). [30 strategic decisions](strategy.md). 5 documented AI failures. Zero lines written by a human.

Not because the human didn't contribute — because the human's contribution was the thinking, not the typing.

---

*[30 decisions with rationale](strategy.md) · [78-entry build timeline](HACKATHON_LOG.md) · [meta-prompting: 30 agents, 8 cases](meta-prompting-strategy.md) · [5 AI failures documented](docs/ANCHORING_FAILURE.md) · [the Prewash Method](docs/PREWASH_METHOD.md) · [builder profile](BUILDER_PROFILE.md)*
