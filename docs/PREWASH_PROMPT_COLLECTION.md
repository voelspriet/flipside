# The Prewash Prompt Collection: Real Before & After Examples

### How removing adjectives and replacing vague language with measurable criteria changes AI output -- documented during the Claude Hackathon 2026

---

## Prompt 1: The Documentation Agent

**What the user needed:** A separate AI agent to monitor and document the entire hackathon build process in detail.

**The vague version:**

> "Monitor my process and document everything in detail as a separate agent."

**The cleaned version:**

> "Give me first a prompt for yourself that would do this."

Then, after seeing Claude's generated blueprint, the user reviewed and approved explicit categories: decisions, pivots, blockers, breakthroughs, metrics, timeline, TL;DR, decision table, retrospective -- before execution.

**Cycle 1 fixes -- adjectives removed:**
- "detail" (undefined scope -- whose definition of detail?)
- "everything" (loads the task toward completeness rather than relevance)

**Cycle 2 fixes -- vague replaced with measurable:**

| Before | After |
|--------|-------|
| "Document everything" | Explicit category list: decisions, pivots, blockers, breakthroughs, metrics, timeline |
| "In detail" | Defined format: TL;DR + timeline + decision table + retrospective |
| "Monitor my process" | Specified tracking dimensions: what was decided, what changed, what blocked progress |

**What the prompt produced:** A structured documentation agent blueprint that the user could review, edit, and approve before it ran -- preventing hours of misaligned output.

---

## Prompt 2: The Research Exploration Prompt

**What the user needed:** A research prompt exploring whether the "Think Like a Document" principle could extend beyond search into other domains.

**The vague version (what Claude generated):**

> A prompt containing: "Be brutally honest," "Is it forced?", "Stress test, not a cheerleader," find what is "compelling," check if the principle "genuinely applies."

**The cleaned version:**

The user caught the biases before execution and would have replaced them with neutral instructions: "Analyze" instead of "be brutally honest," "How does it apply?" instead of "Is it forced?", "Effective" instead of "compelling," "Apply" instead of "genuinely apply," and removed "stress test, not a cheerleader" entirely.

**Cycle 1 fixes -- adjectives and biased words removed:**
- "brutally honest" (primes for negative evaluation)
- "forced" (plants the negative option)
- "compelling" (injects aesthetic judgment)
- "genuinely" (implies the answer might be no)
- "stress test, not a cheerleader" (frames the entire task as skeptical)

**Cycle 2 fixes -- vague replaced with measurable:**

| Before | After |
|--------|-------|
| "Be brutally honest" | "Analyze" |
| "Is it forced?" | "How does it apply?" |
| "Does this genuinely apply?" | "Rate applicability 1-5 and explain why" |
| "Where does it add the most value?" | "Which produces the longest non-trivial reasoning chain?" |
| "Is it better as X or Y?" | "Which is more feasible to build in 6 days?" |

**What the prompt produced:** The Prewash Method itself -- this was the incident that revealed the pattern of adjective bias in AI-generated prompts and led to documenting the method.

---

## Prompt 3: The Tool Concept Generation Prompt

**What the user needed:** Concrete tool concepts that apply "Think Like a Document" using Opus 4.6, buildable in 6 days by one person.

**The vague version:**

> "I need to come up with a practical tool that helps people, maybe with a hidden need, maybe an obvious one, based on the principles we discussed. It can be complex but must be feasible for Claude 4.6. I want to push boundaries without breaking them."

**The cleaned version:**

> I need a tool concept that:
>
> 1. Solves a specific, recurring problem for a defined group of users
> 2. Applies the "Think Like a Document" principle: the tool helps users adopt the perspective of the source they're looking for, rather than searching from their own perspective
> 3. Can be built as a working prototype in 6 days by one person using Python/Flask and the Claude Opus 4.6 API (including extended thinking)
> 4. Uses Opus 4.6 extended thinking in a way that is visible to the user and necessary for the task -- not cosmetic
> 5. Does something that cannot be done with a single prompt to ChatGPT or Perplexity
>
> For each concept, specify:
> - Who uses it (role, not "people")
> - What they do now without this tool
> - What the tool does, step by step
> - Why Opus 4.6 extended thinking is required (not optional)
> - What the user sees on screen

**Cycle 1 fixes -- adjectives and vague words removed:**
- "practical" (every tool should be practical -- adds nothing)
- "helps people" (undefined beneficiary -- replaced with "defined group of users")
- "hidden need" / "obvious one" (speculative framing removed)
- "complex" (undefined -- replaced with specific tech stack constraint)
- "push boundaries without breaking them" (metaphor, not a specification)

**Cycle 2 fixes -- vague replaced with measurable:**

| Before | After |
|--------|-------|
| "Helps people" | "Solves a specific, recurring problem for a defined group of users" |
| "Based on the principles we discussed" | "Applies the 'Think Like a Document' principle: the tool helps users adopt the perspective of the source" |
| "Feasible for Claude 4.6" | "Can be built as a working prototype in 6 days by one person using Python/Flask and the Claude Opus 4.6 API" |
| "Push boundaries" | "Uses Opus 4.6 extended thinking in a way that is visible to the user and necessary for the task -- not cosmetic" |
| (no output spec) | 5 specified output fields per concept: who, current workflow, steps, why Opus 4.6, screen layout |

**What the prompt produced:** TOOL_CONCEPTS.md -- five detailed tool concepts (SourceSight, CiteGuard, GrantWhisperer, ContractLens, SourceFlipper), each with feasibility ratings, reasoning chain lengths, user base estimates, and full screen layout descriptions.

---

## Prompt 4: The User Base Expansion Prompt

**What the user needed:** Modified versions of the tool concepts that expand the user base by 5x or more through a single change per concept.

**The vague version (reconstructed):**

> "How can we make these tools reach more people? Which one would be best for the broadest audience?"

**The cleaned version (reconstructed from EXPANDED_REACH.md structure):**

> For each of the 4 tool concepts (SourceSight, GrantWhisperer, ContractLens, SourceFlipper), provide:
>
> 1. Current target user and estimated user base (from TOOL_CONCEPTS.md)
> 2. One modification that expands the user base by 5x or more
> 3. New target user and estimated user base
> 4. What changes in the tool (table: element, what changes)
> 5. Feasibility impact
>
> Then rank the modified concepts by (Jury Fit x Criteria Fit x Feasibility) as a composite product score. End with a single recommendation and three reasons.

**Cycle 1 fixes -- adjectives removed:**
- "best" (subjective -- replaced with composite score)
- "broadest" (undefined -- replaced with "5x or more" as a measurable threshold)

**Cycle 2 fixes -- vague replaced with measurable:**

| Before | After |
|--------|-------|
| "Reach more people" | "Expands user base by 5x or more" |
| "Which is best?" | "Rank by (Jury Fit x Criteria Fit x Feasibility) as a composite product score" |
| "Broader audience" | "New target user and estimated user base" (with numbers) |
| (open-ended format) | 5 numbered fields per concept + ranking table + single recommendation with 3 reasons |

**What the prompt produced:** EXPANDED_REACH.md -- four modified concepts with quantified user base growth (SourceSight 500K to 3M, GrantWhisperer 3M to 20M, ContractLens 50M to 250M+, SourceFlipper 1M to 8M), composite ranking, and the recommendation of ContractLens as "One-Sided Document Analyzer."

---

## Prompt 5: The Document Comparison Concept Prompt

**What the user needed:** A concept definition for a tool that compares two documents using Opus 4.6 extended thinking.

**The vague version:**

> "We should introduce an option to compare different documents using 4.6 strengths and pushing boundaries -- only applicable for people comparing stuff. Write a prompt for that."

**The cleaned version:**

> Concept: a tool where users upload 2 or more documents and Opus 4.6 identifies contradictions, overlaps, and gaps between them using extended thinking.
>
> Write a prompt that defines:
> - What document types this works for (legal filings, news articles, research papers, corporate reports -- pick one or specify all)
> - What "comparison" means here: factual contradictions? different conclusions from same data? missing information in one that exists in another?
> - What Opus 4.6 extended thinking does that a simple diff tool cannot
> - What the user sees as output
> - A concrete example with two real document types

**Cycle 1 fixes -- adjectives and vague words removed:**
- "different" (all documents being compared are different -- adds nothing)
- "strengths" (undefined -- replaced with specific capability: "identifies contradictions, overlaps, and gaps")
- "pushing boundaries" (metaphor, not specification -- removed)
- "people comparing stuff" (undefined user and task -- replaced with specific document types and comparison types)

**Cycle 2 fixes -- vague replaced with measurable:**

| Before | After |
|--------|-------|
| "Compare different documents" | "Identifies contradictions, overlaps, and gaps between them" (three defined comparison types) |
| "Using 4.6 strengths" | "What Opus 4.6 extended thinking does that a simple diff tool cannot" |
| "People comparing stuff" | "Legal filings, news articles, research papers, corporate reports" |
| "Pushing boundaries" | "A concrete example with two real document types" |
| (no output spec) | "What the user sees as output" |

**What the prompt produced:** DOCUMENT_COMPARISON_CONCEPT.md -- a complete concept definition with exactly 3 comparison types (factual contradictions, divergent conclusions, information gaps), 5 document pairings, a full screen layout, and a detailed walkthrough using a pharmaceutical press release vs. an FDA Complete Response Letter.

---

## Prompt 6: The ContractLens Problems Prompt

**What the user needed:** Specific, concrete problems that ContractLens would solve for real users, to validate the tool concept.

**The vague version (reconstructed):**

> "What are the biggest problems people face with contracts? Give me good examples of why ContractLens would be useful."

**The cleaned version (reconstructed from CONTRACTLENS_PROBLEMS.md structure):**

> List 10 specific problems with one-sided documents that ContractLens solves. For each problem, specify:
> - User (specific role, not "people")
> - What happens now without the tool
> - What ContractLens shows them (using the drafter-perspective mechanism from TOOL_CONCEPTS.md and EXPANDED_REACH.md)
> - Estimated annual users
>
> Then organize into categories. Then produce three lists:
> - 3a: Most users affected annually (top 3)
> - 3b: Most financial damage per incident (top 3, with dollar amounts)
> - 3c: Least served by existing tools (top 3, with rationale)
>
> Identify the single problem that appears in 2+ lists. Deep-dive that problem: describe the user's current 5-step workflow, where ContractLens intervenes, and what the user sees on screen at each step.

**Cycle 1 fixes -- adjectives removed:**
- "biggest" (subjective ranking -- replaced with three defined ranking criteria)
- "good" (aesthetic judgment -- removed)
- "useful" (vague benefit -- replaced with specific mechanism: "what ContractLens shows them")

**Cycle 2 fixes -- vague replaced with measurable:**

| Before | After |
|--------|-------|
| "Biggest problems" | Three ranked lists with defined criteria: user count, financial damage (dollar amounts), existing tool coverage |
| "People face" | "User (specific role)" -- each problem specifies: freelance developer, apartment tenant, consumer, homeowner, employee, borrower, etc. |
| "Good examples" | "10 specific problems" with 4 required fields each |
| "Why it would be useful" | "What ContractLens shows them (using the drafter-perspective mechanism)" |
| (open-ended) | "Identify the single problem that appears in 2+ lists" and "deep-dive with 5-step workflow" |

**What the prompt produced:** CONTRACTLENS_PROBLEMS.md -- 10 specific problems (from freelancer non-competes to patient consent form waivers), organized into 4 categories, with three ranked lists identifying "The Policyholder's Exclusion Maze" as the problem appearing in all three lists (~30M users, highest per-incident damage at $10K-$50K+, and least served by existing tools), plus a detailed deep-dive with step-by-step screen mockup.

---

## Prompt 7: The Matrix Comparison Prompt

**What the user needed:** A comparison of two analysis documents (an earlier decision matrix with 4 ideas vs. a later ideation with 5 concepts) to check whether the original recommendation still held.

**The vague version (reconstructed):**

> "Compare these two documents. Does CiteGuard still win? Is it still the best option?"

**The cleaned version (reconstructed from MATRIX_COMPARISON.md structure):**

> Compare DECISION_MATRIX.md (4 ideas, CiteGuard selected) against TOOL_CONCEPTS.md (5 concepts via "Think Like a Document"). Provide:
>
> 1. What changed: list assumptions from DECISION_MATRIX.md that TOOL_CONCEPTS.md challenges or invalidates, list assumptions that held up, and list new information not available when DECISION_MATRIX.md was written
> 2. Score each TOOL_CONCEPTS.md concept using the same Decision Matrix dimensions (Jury Fit per judge with rationale, Criteria Fit weighted by Demo 30% / Opus 4.6 Use 25% / Impact 25% / Depth 20%, Feasibility 1-10, Uniqueness 1-10, Rule Compliance 1-10)
> 3. Answer: does CiteGuard still score highest? Show a composite comparison table with all numbers
> 4. What does the comparison reveal about the decision process? Where did earlier assumptions narrow the option space?

**Cycle 1 fixes -- adjectives removed:**
- "best" (subjective -- replaced with specific scoring dimensions)
- "still win" (frames as competition -- replaced with "still score highest" on defined dimensions)

**Cycle 2 fixes -- vague replaced with measurable:**

| Before | After |
|--------|-------|
| "Compare these two documents" | "List assumptions that are challenged, that held up, and new information" (three specific categories) |
| "Does CiteGuard still win?" | "Does CiteGuard still score highest?" with a composite comparison table showing all numbers |
| "Is it still the best?" | Score every concept using identical dimensions: Jury Fit (5 judges x 1-10), Criteria Fit (4 weighted criteria), Feasibility, Uniqueness, Rule Compliance |
| (no process reflection) | "Where did earlier assumptions narrow the option space?" |

**What the prompt produced:** MATRIX_COMPARISON.md -- a 320-line analysis showing CiteGuard still scored highest on Jury Fit (46/50) and Criteria Fit (9.15), but no longer won on every dimension (GrantWhisperer and ContractLens scored 10 on feasibility vs. CiteGuard's 8), with a detailed breakdown of where earlier assumptions had narrowed the option space and how the "Think Like a Document" constraint opened new possibilities.

---

## The Pattern

### The 5 most common adjectives that appeared in vague versions

1. **"best"** -- appeared in prompts 4, 7, and implicitly in most vague versions
2. **"practical"** -- appeared in prompt 3's vague version
3. **"good"** -- appeared in prompt 6's vague version
4. **"biggest"** -- appeared in prompt 6's vague version
5. **"comprehensive" / "detailed"** -- appeared in prompts 1 and 2 (Claude's generated instructions)

### The 5 most common vague-to-measurable replacements

1. **"people" --> specific role** (e.g., "people comparing stuff" became "fact-checkers, newsroom editors, litigation attorneys")
2. **"best" / "biggest" --> ranked by defined criteria** (e.g., "best option" became "highest composite score on Jury Fit x Criteria Fit x Feasibility")
3. **"in detail" / "comprehensive" --> enumerated category list** (e.g., "document in detail" became "decisions, pivots, blockers, breakthroughs, metrics, timeline")
4. **"helps" / "useful" --> specifies mechanism** (e.g., "useful tool" became "identifies contradictions, overlaps, and gaps using extended thinking")
5. **"push boundaries" / "feasible" --> specific constraints** (e.g., "push boundaries" became "built in 6 days by one person using Python/Flask and the Claude Opus 4.6 API")

### What all cleaned prompts have in common

Every cleaned prompt eliminates adjectives, specifies who the user is by role, defines what the output must contain by listing numbered fields or categories, replaces subjective quality words with measurable criteria or numeric scales, and tells the AI what format to produce -- so the AI executes a specification instead of interpreting a wish.

---

<sub>Compiled from the Claude Hackathon 2026 session. All prompts are real or faithfully reconstructed from the documents that produced them. The Prewash Method was developed by Henk van Ess.</sub>

<sub>Full analysis with the self-reflection hypothesis and 30 agent-tested comparisons: [meta-prompting-strategy.md](../meta-prompting-strategy.md)</sub>
