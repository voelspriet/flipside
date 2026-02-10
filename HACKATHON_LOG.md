# HACKATHON_LOG.md

## Claude Hackathon 2026 -- Build Process Documentation

---

## TL;DR

**Status:** Pivoting from CiteGuard. "Think Like a Document" emerging as a universal principle for AI interaction. The Prewash Method (catching bias in AI prompts before execution) documented as a second case study. A live, unscripted demonstration proved "Think Like a Document" applies to AI reasoning itself -- Claude confidently misinterpreted a vague input, then the user revealed the clean version, proving the vocabulary mismatch problem exists in human-AI interaction.

We are participating in Claude's first hackathon ($500 API credit). Before writing a single line of product code, we invested the opening phase entirely in **methodology and process architecture**. The first significant act was a meta-prompting exercise: instead of asking Claude to build a documentation agent directly, we asked Claude to *design the prompt for itself first*, reviewed it, then executed it. This yielded a reusable case study on meta-prompting (published as both a PDF and a GitHub-ready Markdown document) and established a disciplined, observable workflow for the rest of the hackathon.

We are now running **two parallel research workstreams** to decide what to build: (1) a codebase analysis of the user's existing projects to identify strengths, and (2) jury research to understand what the panel values. The product decision will be the intersection of these two inputs. In a deliberate test of Claude 4.6's reasoning, the user withheld the official judging criteria to see if the model would identify it as a missing variable -- it did, unprompted, demonstrating "gap awareness" in incomplete decision frameworks.

**What exists so far:**
- `Meta-Prompting_Explained.pdf` -- 3-page case study document
- `docs/META_PROMPTING.md` -- GitHub-optimized version of the same
- `HACKATHON_LOG.md` -- this file (the documentation agent is now live)

**What does NOT exist yet:** A product. The tool to be built has not been decided.

---

## Timeline

### Phase 0: Meta-Strategy & Process Setup

> *"The most important prompt you write isn't the one that does the work -- it's the one that designs the one that does the work."*

#### [DECISION] Entry 0.1 -- Hackathon Acceptance & Opening Move

**When:** 2026-02-10, session start

The user was accepted into Claude's first hackathon with a $500 API credit. The very first action was **not** to brainstorm product ideas, pick a tech stack, or start coding. It was to set up observability over the entire build process.

**What was decided:** Before building anything, establish a documentation agent that would monitor and log every phase of the hackathon.

**Why this matters:** In a time-pressured hackathon, most teams jump straight into building. This team chose to invest the first minutes in infrastructure that would pay dividends later -- both as a process discipline tool and as a presentation artifact.

---

#### [BREAKTHROUGH] Entry 0.2 -- The Meta-Prompt Question

**When:** 2026-02-10, minutes into the session

Instead of saying *"Build me a documentation agent,"* the user said:

> *"Give me first a prompt for yourself that would do this."*

This single sentence shifted the interaction from **execution mode** to **design mode**. Claude produced a detailed, structured prompt specifying:
- Six documentation categories (Decision Log, Build Timeline, Technical Choices, Prompt Engineering Log, Aha Moments, Metrics)
- Output format (HACKATHON_LOG.md with TL;DR, Timeline, Decisions table, Lessons Learned, Retrospective)
- Tone guidance (dev blog post -- technical but human)
- Tagging system ([DECISION], [PIVOT], [BLOCKER], [BREAKTHROUGH], [TECHNICAL], [DESIGN])

The user could now **read, critique, and reshape** the agent's behavior before it ever ran. This is the core meta-prompting pattern.

---

#### [DECISION] Entry 0.3 -- Comparing the Two Approaches

**When:** 2026-02-10

The user asked Claude to produce a side-by-side comparison of the two options:
- **Option A (Direct Ask):** Tell Claude to monitor and document. Hope it does what you mean.
- **Option B (Meta-Prompt First):** Ask Claude to design the prompt, review it, then execute.

Claude generated a comparison table across 7 dimensions:

| Dimension | Option A: Direct Ask | Option B: Meta-Prompt |
|-----------|---------------------|----------------------|
| What you control | The output (after the fact) | The instructions (before execution) |
| Specificity | Vague, open to interpretation | Explicit categories defined |
| Structure | Claude picks a format | Format defined and approved |
| Error discovery | Late and expensive | Early and free |
| Iteration cost | High: re-explain, re-run | Low: edit the prompt, run once |
| Compounding risk | Hours of misaligned output | Alignment locked in from start |
| Analogy | "Build me a nice kitchen" | "Show me the blueprint first" |

**Alternatives considered:** Only these two. The user did not consider a hybrid approach or iterative refinement without upfront design. The binary comparison was deliberate -- it makes the case study cleaner and more teachable.

---

#### [BREAKTHROUGH] Entry 0.4 -- Recognizing the Teachable Moment

**When:** 2026-02-10

The user recognized that this meta-prompting exercise was not just process setup -- it was a **standalone case study** worth presenting to the hackathon jury. This realization turned a process decision into a deliverable.

**Why this is an aha moment:** Most hackathon teams would treat documentation setup as invisible overhead. By making the methodology itself visible and publishable, the team created value from what others would discard.

---

#### [TECHNICAL] Entry 0.5 -- PDF Generation

**When:** 2026-02-10

A professional 3-page PDF (`Meta-Prompting_Explained.pdf`) was generated covering:
1. The full story of what happened
2. The two options compared
3. A results comparison table
4. Why meta-prompting matters beyond this hackathon

**Technical approach:**
- Content authored as HTML with embedded CSS for precise formatting
- Converted to PDF using `wkhtmltopdf`
- Styling included professional typography, tables, blockquotes, and a quote callout

**Trade-off:** Using HTML+CSS for PDF generation is heavier than plain Markdown-to-PDF, but produces presentation-quality output suitable for a jury. Speed was traded for polish, which was the right call given this artifact's purpose.

---

#### [DESIGN] Entry 0.6 -- GitHub-Ready Markdown Version

**When:** 2026-02-10

A duplicate version was created at `docs/META_PROMPTING.md`, optimized for GitHub's native Markdown renderer. Placed in a `docs/` folder following standard GitHub repository conventions.

**Why both formats:**
- PDF: for presentations, email, offline sharing
- Markdown in `docs/`: for anyone browsing the GitHub repo, renders natively, no download required

---

#### [DECISION] Entry 0.7 -- "Execute the Prompt"

**When:** 2026-02-10

The user said **"Execute the prompt"** -- meaning: take the documentation agent prompt that Claude had designed earlier and activate it. This closed the meta-prompting loop:

```
Design the prompt --> Review it --> Approve it --> Execute it
```

This is the moment the documentation agent (this file) came to life.

---

#### [DECISION] Entry 0.8 -- Jury Research as a Variable

**When:** 2026-02-10

The user identified that the hackathon jury composition is a critical variable in deciding what to build. Instead of picking a project based only on personal strengths, the user chose to research the judges first and find the intersection of "what I'm good at" + "what the jury values."

The jury panel was identified from a hackathon briefing screenshot:

| # | Name | Role | Orientation |
|---|------|------|-------------|
| 1 | Boris Cherny | Creator and Head of Claude Code, Anthropic | Technical |
| 2 | Cat Wu | Product, Anthropic | Product |
| 3 | Thariq Shihpar | Member of Technical Staff, Anthropic | Technical |
| 4 | Ado Kukic | Community Manager, Anthropic | Community |
| 5 | Jason Bigman | Head of Community, Anthropic | Community |

**Key observation:** The jury is **40% technical** (Boris, Thariq) and **60% product/community** (Cat, Ado, Jason). This means the winning project needs to be technically impressive AND tell a compelling story. Pure technical depth without narrative will not win. Pure storytelling without engineering substance will not win either. The sweet spot is a project that *does something technically non-trivial* and *can be explained compellingly to a non-technical audience*.

**Meta-prompting pattern continued:** Before executing the jury research, the user again asked for the prompt first, reviewed it, then approved execution. The pattern is now established as the team's standard workflow. What started as a one-off technique in Entry 0.2 is now a repeatable process.

**Two parallel workstreams now active:**
1. **Strengths analysis** (separate Claude session on user's server) -- Analyzing the user's existing codebase to identify technical strengths, domain expertise, and reusable components
2. **Jury research** (this session) -- Researching the jury panel to understand what they value, what impresses them, and what gaps exist in current Claude Code tooling

The final project decision will be the **intersection** of these two inputs: build something at the crossroads of personal capability and jury appeal.

**Why this is strategic:** Most hackathon teams pick a project based on what excites *them*. This team is treating the jury as a design constraint -- the same way a product team treats users as a design constraint. The project must solve for the evaluator, not just the builder.

---

#### [BREAKTHROUGH] Entry 0.9 -- Testing Claude 4.6's Situational Awareness

**When:** 2026-02-10

A deliberate test was conducted. The user intentionally withheld the hackathon's official judging criteria to see whether Claude (Opus 4.6) would independently identify it as a missing variable in the decision-making process.

**Result:** Claude identified the gap unprompted. After the user explained the two-input approach (personal strengths + jury interests), Claude immediately responded by asking about the **third variable** -- the official judging criteria -- and presented a table showing all three inputs needed:

| Input | Source | Status |
|-------|--------|--------|
| Your strengths | Other Claude session on server | Done |
| Jury interests | Research agent | In progress |
| Judging criteria | ? | **Missing** |

The user acknowledged: *"On purpose, I didn't give you this. Wanted to see if 4.6 came up with it."*

**Why this matters:**
- This demonstrates Claude's ability to reason about **what it doesn't know** -- not just answering questions, but identifying which questions haven't been asked yet
- In prompt engineering terms, this is the model exhibiting "gap awareness" -- recognizing incomplete decision frameworks and flagging missing inputs
- This is especially significant in a hackathon context where a human under time pressure might rush past incomplete information. The AI caught what could have been a strategic blind spot

**For the jury:** This was a deliberate, documented test of Claude 4.6's reasoning capabilities, conducted in real-time during the hackathon build process. The user treated the AI as a collaborator whose judgment could be tested and validated.

---

#### [BREAKTHROUGH] Entry 0.10 -- The Third Variable Arrives: Full Hackathon Criteria

**When:** 2026-02-10

The user provided the complete hackathon brief, including all judging criteria, problem statements, schedule, rules, prizes, and submission requirements. This was the missing third input that Claude 4.6 had independently identified (Entry 0.9).

**Judging Criteria (the weights that matter):**

| Category | Weight | What judges are looking for |
|----------|--------|-----------------------------|
| Demo | 30% | "genuinely cool to watch" |
| Impact | 25% | "could this actually become something people use?" |
| Opus 4.6 Use | 25% | "capabilities that surprised even us" |
| Depth & Execution | 20% | "pushed past their first idea" |

**Critical insight:** Demo is the single largest scoring category at 30%. This means the project must produce visually impressive, showable output -- not just functional backend code. The 3-minute video IS the product as far as scoring goes. A project that works perfectly but demos poorly will lose to a project that demos beautifully, even if the latter is less technically deep.

**Second critical insight:** There are two special prizes ($5k each) that align perfectly with our process:
- **"Most Creative Opus 4.6 Exploration"** -- rewards finding unexpected model capabilities. Our omission test (Entry 0.9) and meta-prompting methodology are already evidence of creative exploration.
- **"The Keep Thinking Prize"** -- rewards visible iteration and depth. Our entire documented process (meta-prompting, jury research, criteria analysis, omission testing) is already evidence for this prize. This log itself is a submission artifact.

**Three problem statements identified:**
1. **Build a Tool That Should Exist** -- open-ended, build something useful
2. **Break the Barriers** -- unlock expert knowledge for everyone
3. **Amplify Human Judgment** -- make professionals more capable, human in the loop

**Strategic analysis saved to:** `docs/CRITERIA_ANALYSIS.md` and `docs/HACKATHON_BRIEF.md`

**All three decision inputs are now available:**

| Input | Source | Status |
|-------|--------|--------|
| Personal strengths | Other Claude session on server | Ready |
| Jury interests | Research agent | In progress |
| Judging criteria | Hackathon brief | **COMPLETE** |

The decision matrix can be assembled once the jury research agent finishes. The project choice will optimize for: high demo impact (30%), real-world usefulness (25%), creative Opus 4.6 usage (25%), and visible iteration depth (20%).

---

#### [BREAKTHROUGH] Entry 0.11 -- Live Jury Research Reveals Critical Correction

**When:** 2026-02-10

Live web research on all 5 judges produced a **major correction** and several enhancements to the jury analysis.

**CRITICAL CORRECTION -- Thariq Shihipar:**
The initial analysis (from training data) incorrectly linked Thariq to Upsolve, a nonprofit providing free bankruptcy filing. Live research confirmed Upsolve was founded by Rohan Pavluri, Jonathan Petts, and Mark Hansen -- Thariq has NO connection to it.

Thariq's actual background: serial entrepreneur who founded One More Multiverse (YC gaming company, $17M raised, 1M+ users), co-founded Chime (acquired by HubSpot), built Edgeout.gg (sold to Blitz.gg), co-founded PubPub (academic publishing), and attended MIT Media Lab. He blogs about AI interpretability AND spirituality/philosophy.

**Impact of correction:** The entire "social impact / civic tech" strategic angle was based on the wrong person. This removes social justice framing as a primary jury strategy. The jury is actually a panel of builders and entrepreneurs, not activists.

**Key enhancements from live research:**

| Judge | Key findings from live research |
|-------|--------------------------------|
| Boris Cherny | Self-taught, IC8 Principal at Meta, 100% of his code written by Claude, values "latent demand" and generalist engineers, envisions orchestrating multiple Claude instances |
| Cat Wu | Product Lead specifically for Claude Code, briefly left for Cursor then returned in 2 weeks, values prototypes over docs, "source of truth is the codebase" |
| Thariq Shihipar | Serial entrepreneur, gaming background (One More Multiverse, $17M raised), MIT Media Lab, builds AI agents, writes about philosophy -- NOT connected to Upsolve |
| Ado Kukic | Confirmed Auth0/MongoDB/DO/Sourcegraph background, recently excited about new Claude API features |
| Jason Bigman | Speaks 9 languages, lived in 10+ countries, previously at Reddit/Facebook/Coinbase/Coursera, connected to Gray Area art/tech nonprofit |

**Updated sweet spot:** The jury is primarily **builders** (Boris, Cat, Thariq) and **community amplifiers** (Ado, Jason). The winning project needs to be an agentic tool that works as a prototype, solves a real problem, shows craft, is teachable, and uses Opus 4.6 creatively.

**Saved to:** `docs/JURY_RESEARCH_LIVE.md`

---

#### [DECISION] Entry 0.12 -- Decision Matrix Assembled: All Three Inputs Converged

**When:** 2026-02-10

All three decision inputs are now complete and have been cross-referenced:

1. **Strengths analysis** (from separate Claude session on server): Identified 731-document hallucination corpus as the #1 unique asset, plus 25+ forensic methods in production, CHI 2026 paper, 20+ years OSINT expertise, multi-LLM orchestration experience.

2. **Ideas generated** (from separate session): Four candidates:

| Candidate | Description |
|-----------|-------------|
| CiteGuard | Legal citation hallucination verifier |
| DeepVerify | Full-spectrum verification tool |
| ElectionShield | Election deepfake detector |
| SearchForTruth | Research journalism accelerator |

3. **Jury + Criteria** (this session): Live-verified jury profiles, corrected Thariq analysis, weighted scoring criteria (Demo 30%, Opus 4.6 25%, Impact 25%, Depth 20%).

**The decision matrix was built crossing all three inputs.** CiteGuard scored highest on EVERY dimension:

| Dimension | CiteGuard Score | Next Best |
|-----------|----------------|-----------|
| Jury fit | 46/50 (highest) | -- |
| Criteria fit | 9.1/10 (highest) | -- |
| Feasibility | 9/10 (highest) | -- |
| Uniqueness | 10/10 (highest -- nobody else has the corpus) | -- |
| Rule compliance | 9/10 (corpus is data, not code) | -- |
| Special prize targeting | Both prizes (only candidate targeting both) | -- |

**Key insight from the corrected jury analysis:** The Thariq correction (NOT connected to Upsolve) actually STRENGTHENED CiteGuard's position. The original analysis suggested social impact would resonate with Thariq. The corrected analysis shows he is a serial entrepreneur who values unique datasets as competitive moats and novel AI applications -- which maps even better to CiteGuard's 731-document corpus advantage.

**Why CiteGuard wins the matrix:**
- **Demo (30%):** Paste a legal brief, watch citations turn red/green in real-time -- visually compelling, instantly understandable
- **Impact (25%):** Lawyers already have this problem; hallucinated citations cause real sanctions and malpractice risk
- **Opus 4.6 Use (25%):** Multi-step reasoning across legal databases, corpus matching, confidence scoring -- genuine agentic workflow
- **Depth & Execution (20%):** The 731-document corpus is a unique asset no other hackathon team can replicate
- **Special prizes:** Targets both "Most Creative Opus 4.6 Exploration" and "The Keep Thinking Prize"

**Decision matrix saved to:** `docs/DECISION_MATRIX.md`

---

#### [BREAKTHROUGH] Entry 0.13 -- The Prewash Method: Catching Bias in AI Prompts

**When:** 2026-02-10

A critical moment. The user asked Claude to write a research prompt for exploring the "Think Like a Document" principle across multiple domains. Claude produced the prompt -- following the established meta-prompting pattern. But before approving execution, the user identified BIAS embedded in Claude's prompt.

**Examples of bias caught:**

| Biased phrase | Problem |
|---------------|---------|
| "Be brutally honest" | Primes for negative evaluation |
| "Is it forced?" | Plants the negative option in the question |
| "Stress test, not a cheerleader" | Frames the entire task as skeptical |
| "Compelling" | Injects aesthetic judgment |

The user explained this as **The Prewash Method** -- a technique they developed from their OSINT practice:

```
1. Don't say "summarize this document"     (lets loose an uncontrolled algorithm)
2. Say "give me a prompt for summarizing"   (makes the instructions visible)
3. Clean the bias from the prompt           (the prewash step)
4. Then execute the cleaned prompt          (controlled execution)
```

**The deeper insight:** The Prewash Method IS "Think Like a Document" applied to prompts. Just as you should not search using your own vocabulary (search using the document's vocabulary), you should not prompt using your own biases (prompt using neutral, clean instructions). Both are about flipping perspective away from yourself.

**This is the user's core methodology manifesting:** The same principle -- "don't take yourself as the measurement of things, but observe what must be there" -- applies to search, to prompting, and potentially to the hackathon product itself.

**Impact on the project:** This confirms that "Think Like a Document" is NOT just a search technique. It is a universal principle for human-AI interaction. This strengthens the case for building a product that applies it across multiple domains.

**Documented for GitHub at:** `docs/PREWASH_METHOD.md`

---

#### [BREAKTHROUGH] Entry 0.14 -- Prewash Method Has Two Cycles

**When:** 2026-02-10

The user reviewed Claude's "cleaned" research prompt and found it still contained vague, unmeasurable language. Removing adjective bias (Cycle 1) was not enough -- vague terms needed to be replaced with measurable criteria (Cycle 2).

**The user's specific corrections:**

| Claude's "clean" version | User's fix | What changed |
|--------------------------|-----------|--------------|
| "How well?" | "Rate applicability 1-5 and explain why" | Vague to measurable scale |
| "add the most value" | "produces the longest non-trivial reasoning chain" | Subjective to observable metric |
| "better" | "more feasible to build in 6 days" | Open comparison to concrete constraint |

**The insight:** The Prewash Method has two cycles:

```
Cycle 1: Remove adjective bias       (strip emotional loading)
Cycle 2: Replace vague with measurable (turn subjective into quantifiable)
```

Both cycles are necessary. Cycle 1 alone still leaves the AI free to interpret vague instructions however it wants. A prompt that is unbiased but vague will produce inconsistent results across runs -- the model fills in the vagueness with its own interpretation each time.

**Updated:** `docs/PREWASH_METHOD.md` now documents both cycles.

---

#### [BREAKTHROUGH] Entry 0.15 -- Live Demonstration: The Principle Applied to the AI Itself

**When:** 2026-02-10

The most significant moment of the hackathon process so far. The user deliberately gave Claude a vague, adjective-laden input ("I need a practical tool that helps people, maybe with a hidden need, maybe an obvious one, push boundaries without breaking them") and asked "Do you understand?"

Claude confidently confirmed understanding, interpreting the input through its own vocabulary -- referencing "latent demand," "invisible infrastructure," "PageRank." Claude projected its own framework onto the user's intent.

The user then revealed the ACTUAL prompt they had prepared -- a clean, structured specification with 5 numbered constraints and 5 specified outputs. No adjectives. No ambiguity.

**The gap between Claude's confident interpretation and the user's actual intent IS the vocabulary mismatch problem** -- the same problem "Think Like a Document" was designed to solve. Claude was "searching with its own words" instead of "thinking like the document."

This demonstrated three things simultaneously:
1. **"Think Like a Document" applies to AI interaction, not just search** -- the vocabulary mismatch problem is universal
2. **The Prewash Method catches exactly this kind of drift** -- if the user had accepted Claude's confident interpretation, the project would have drifted off course
3. **The AI's confident "I understand" can mask fundamental misalignment** -- confidence and alignment are independent variables

**The exchange was documented verbatim at:** `docs/LIVE_DEMONSTRATION.md`

**Why this is the most important entry so far:** This is not just process documentation. This is a live, unscripted, reproducible demonstration of the core principle that the hackathon product is built on. It proves the principle works by showing what happens when it is NOT applied (Claude's biased interpretation) vs. when it IS (the clean structured prompt). The before/after comparison is the strongest possible evidence.

---

#### [DECISION] Entry 0.16 -- Retesting Earlier Conclusions Against New Evidence

**When:** 2026-02-10

A comparison analysis was launched between two documents produced at different stages of the decision process:

1. **DECISION_MATRIX.md** (earlier) — evaluated 4 original ideas. CiteGuard scored highest on every dimension.
2. **TOOL_CONCEPTS.md** (later) — generated 5 new concepts using the "Think Like a Document" principle as the organizing constraint.

**Why this matters:** When new evidence arrives, you don't evaluate it in isolation — you go back to earlier conclusions and test whether they still hold. The DECISION_MATRIX was built before the "Think Like a Document" constraint reshaped the concept space. If CiteGuard still wins under the same scoring method, the earlier analysis was robust. If a new concept wins, the earlier analysis was limited by the assumptions it started with. Either outcome is documented.

**Methodology:** The comparison uses the exact same scoring dimensions as the original matrix (jury fit, criteria fit, feasibility, uniqueness, rule compliance) applied to the new concepts. No new dimensions were introduced — this isolates whether the CONCEPTS changed the outcome, not the SCORING.

**This is an investigative practice applied to the decision process itself:** re-examine conclusions when new information arrives. The Prewash Method was applied to the comparison prompt (no adjectives, measurable scales, no leading questions).

**Saved to:** `docs/MATRIX_COMPARISON.md` (in progress)


#### [CRITICAL ERROR] Entry 0.17 -- The Anchoring Failure: AI Recommends a Product That Already Exists
**Time**: 2026-02-10
**Type**: CRITICAL ERROR / METHODOLOGY VALIDATION

The human caught a compounding confirmation bias across three analysis documents. Despite the human flagging Damien Charlotin's hallucination database (907 cases + PelAIkan verification tool) as a direct competitor to CiteGuard, Opus 4.6 continued recommending CiteGuard across DECISION_MATRIX.md, TOOL_CONCEPTS.md, and MATRIX_COMPARISON.md — scoring its uniqueness at 10/10 each time. The competitor evidence was acknowledged in conversation but never propagated into the scoring. This validates the Prewash Method's warning: "Long-running agent: Dangerous — misalignment compounds over hours." Documented in docs/ANCHORING_FAILURE.md.

**Decision**: CiteGuard recommendation is invalidated. Product decision reopened.

---

## Decisions

| # | Decision | Rationale | Alternatives Rejected | Category |
|---|----------|-----------|----------------------|----------|
| 1 | Set up documentation before building anything | Process discipline pays dividends in a time-pressured environment; documentation becomes a presentation artifact | Jump straight into coding | [DECISION] |
| 2 | Use meta-prompting (design the prompt before executing) | Aligns agent behavior upfront; avoids compounding misalignment; lower iteration cost | Direct ask (let Claude interpret freely) | [DECISION] |
| 3 | Create the meta-prompting comparison as a formal case study | Turns process overhead into a deliverable; demonstrates engineering thinking to jury | Keep it as internal notes only | [BREAKTHROUGH] |
| 4 | Generate PDF via HTML+CSS+wkhtmltopdf | Presentation-quality output for jury; professional formatting | Plain Markdown-to-PDF (faster but less polished) | [TECHNICAL] |
| 5 | Maintain both PDF and Markdown versions | PDF for presentations; Markdown for GitHub browsing | Single format only | [DESIGN] |
| 6 | Place Markdown docs in `docs/` folder | GitHub convention; clean repo structure | Root directory (cluttered) | [DESIGN] |
| 7 | **Tool/product: NOT YET DECIDED** | Still in pre-build phase | N/A | -- |
| 8 | Research the jury before choosing a project | Jury composition (40% technical, 60% product/community) is a critical design constraint; the winning project must satisfy both audiences | Pick a project based on personal interest alone; pick based on technical impressiveness alone | [DECISION] |
| 9 | Analyzed judging criteria before choosing a project | Demo (30%) is the largest factor -- project must be visually impressive and produce showable output | Building something technically cool but hard to demo | [DECISION] |
| 10 | Ran live web research to verify jury analysis from training data | Caught a critical factual error (wrong person linked to Upsolve) that would have misguided strategy | Trusting unverified training data | [BREAKTHROUGH] |
| 11 | Built a formal decision matrix crossing strengths x jury x criteria | Systematic approach eliminates subjective bias; CiteGuard won every dimension | Going with gut feeling or picking the most technically ambitious option | [DECISION] |
| 12 | Identified and documented bias in Claude's research prompt before execution | The Prewash Method: making invisible AI instructions visible to catch bias | Running biased prompts without review | [BREAKTHROUGH] |
| 13 | Refined the Prewash Method to include two cycles (remove bias + replace vague with measurable) | Vague-but-unbiased prompts still produce inconsistent results | Stopping after removing adjectives only | [BREAKTHROUGH] |
| 14 | Documented the live demonstration verbatim for GitHub | This exchange is the strongest evidence that the principle works -- showing failure (vague input to biased interpretation) and success (clean input to precise output) side by side | Paraphrasing or summarizing the exchange (would lose the impact) | [BREAKTHROUGH] |
| 15 | Retested earlier CiteGuard decision against 5 new concepts using identical scoring | New evidence requires re-examination of prior conclusions; same scoring method isolates the variable | Assuming earlier conclusion still holds without retesting | [DECISION] |

---

## Prompt Engineering Log

### Prompt 1: The Meta-Prompt Request

**What was said:**
> "Give me first a prompt for yourself that would do this."

**Result:** Claude produced a comprehensive, structured documentation agent prompt with six tracking categories, output format specification, tone guidance, and a tagging system.

**What made it effective:** The request was precise about the *type* of output (a prompt, not an execution) and the *target* (yourself). This framing forced Claude into design mode rather than execution mode.

**Learning:** Asking an LLM to produce instructions for itself is a powerful alignment technique. It makes the model's interpretation of your request *visible and editable* before any work begins.

### Prompt 2: The Comparison Table Request

**What was said:** (paraphrased) "Compare Option A vs Option B and put it in a table."

**Result:** A structured 7-dimension comparison that became the backbone of the published case study.

**What made it effective:** Requesting a specific format (table) and specific structure (two named options) gave Claude clear constraints, which produced a focused output.

### Prompt 3: The Deliberate Omission Test

**What was done:** The user intentionally withheld the judging criteria while discussing the decision matrix for choosing a project.

**What happened:** Claude independently identified "judging criteria" as a missing third variable and asked for it, presenting a table that clearly showed the gap.

**What this demonstrates:** You don't always test an AI by what you ask -- sometimes you test it by what you *don't* say. Omission testing reveals whether the model is reasoning about the problem holistically or just responding to surface-level inputs. In this case, Claude wasn't just answering the question in front of it; it was reasoning about the *structure* of the decision and noticed a load-bearing input was absent.

**Learning:** Deliberate omission is a powerful prompt engineering technique for calibrating trust in an AI collaborator. If the model catches the gap, you know it is reasoning about the problem space, not just pattern-matching on your words. If it misses the gap, you know to provide more explicit structure.

### Prompt 4: The Biased Research Prompt

**What was done:** The user asked Claude to write a research prompt for exploring "Think Like a Document" across multiple domains, following the meta-prompting pattern.

**What happened:** Claude produced a prompt containing adjectives ("brutally honest"), leading questions ("is it forced?"), and tone bias ("stress test, not a cheerleader"). The user caught these before execution and identified them as bias that would skew results toward negative evaluation.

**What this demonstrates:** Even meta-prompted instructions carry the prompt-writer's bias. The meta-prompting pattern (Entry 0.2) makes the instructions *visible*, but visibility alone is not enough -- you also need a **cleaning step** to remove embedded assumptions, leading language, and aesthetic judgments. This is the Prewash Method: generate, review, clean, execute.

**Learning:** Every adjective in a prompt is a policy decision. "Be thorough" and "be concise" produce fundamentally different outputs from the same model. "Be brutally honest" and "be balanced" produce fundamentally different evaluations of the same subject. The Prewash Method adds a bias-cleaning step between prompt generation and execution, preventing these invisible policy decisions from compounding through agent systems.

### Prompt 5: The Two-Cycle Prewash

**What was done:** After Cycle 1 cleaned adjective bias from the research prompt (Entry 0.13 / Prompt 4), the user reviewed the "cleaned" version and found it still contained vague, unmeasurable language.

**What happened:** Three specific corrections transformed the prompt from clean-but-vague to clean-and-precise: "How well?" became "Rate applicability 1-5 and explain why"; "add the most value" became "produces the longest non-trivial reasoning chain"; "better" became "more feasible to build in 6 days."

**What this demonstrates:** Unbiased and precise are two different qualities. A prompt can pass Cycle 1 (no adjective bias) and still fail Cycle 2 (vague terms that the model interprets differently each run). Both cycles are required for reliable, reproducible AI output.

**Learning:** After removing bias, replace every vague term with a measurable criterion. If you cannot measure it, the AI cannot consistently produce it. The question "How well does X apply?" has infinite valid answers. The question "Rate applicability 1-5 with justification" has a bounded, comparable output. This is the difference between a prompt that works once and a prompt that works every time.

### Prompt 6: The Deliberate Vague Input

**What was done:** The user gave Claude a vague, adjective-laden description on purpose: "I need a practical tool that helps people, maybe with a hidden need, maybe an obvious one, push boundaries without breaking them." Then asked: "Do you understand?"

**What happened:** Claude processed it through its own framework and confirmed understanding confidently, mapping the vague input to concepts like "latent demand," "invisible infrastructure," and "PageRank." The user then revealed a structured 5-constraint, 5-output prompt that bore little resemblance to Claude's interpretation.

**What this demonstrates:** The vocabulary mismatch problem exists in AI prompting, not just in search. When given vague input, the AI does not ask for clarification -- it fills the gaps with its own vocabulary and frameworks, then presents the result with full confidence. The user's actual intent was invisible to Claude because it was expressed in language the model could freely reinterpret.

**Learning:** Never accept "I understand" from an AI at face value. The model's confidence tells you nothing about alignment. The only way to verify alignment is to compare the model's interpretation against your actual structured intent. This is why the Prewash Method requires showing the clean version: it makes misalignment visible before it compounds.

---

## Metrics

| Metric | Value |
|--------|-------|
| Time in Phase 0 (process setup) | ~30-45 minutes (estimated) |
| Documents created | 10 (PDF, 8 markdown docs, this log) |
| Lines of documentation written | ~200+ across all files |
| Lines of product code written | 0 |
| Product decisions made | 0 |
| Process/methodology decisions made | 15 |
| Meta-prompts used | 1 (the foundational one) |
| Pivots so far | 0 |
| Blockers so far | 0 |
| AI reasoning tests conducted | 2 (1 passed -- gap detection; 1 caught -- prompt bias) |

---

## Lessons Learned

*(Updated as the hackathon progresses)*

### Lesson 1: Meta-Prompting Is Worth the Time Investment
Asking Claude to show its plan before executing adds maybe 2 minutes of overhead but eliminates entire categories of misalignment. In a hackathon setting where every minute matters, this feels counterintuitive -- but the math works out. One aligned execution beats three misaligned attempts.

### Lesson 2: Process Documentation Can Be a Product
What started as internal scaffolding (a documentation agent) became a publishable case study. When working under time pressure, look for artifacts that serve double duty.

### Lesson 3: The First Decision Sets the Tone
Choosing to start with methodology rather than code established a disciplined, deliberate pace. This is a bet that compounds -- if the rest of the hackathon benefits from this rigor, the early investment pays for itself many times over.

### Lesson 4: Format Matters for Different Audiences
The same content was published in two formats (PDF and Markdown) because the audiences differ. Jury members may want a polished PDF. GitHub browsers want native Markdown. Thinking about distribution early prevents rework later.

### Lesson 5: Treat the Jury as a Design Constraint
Researching judges before choosing a project is a strategic advantage. Knowing that this jury is 40% technical and 60% product/community changes what "winning" looks like -- it is not enough to build something technically deep if you cannot tell its story, and it is not enough to tell a great story if there is no engineering substance behind it. Treat the evaluator the same way a product team treats users: understand them first, then build for them.

### Lesson 6: Test Your AI Collaborator's Judgment
The user deliberately withheld information to validate whether Claude would identify a gap in the decision framework. It did. This kind of calibration -- testing whether the model catches what you expect it to catch -- builds justified trust. You should not blindly trust OR blindly distrust your AI tools. Test them, document the results, and calibrate accordingly. In this case, the omission test confirmed that Claude 4.6 reasons about problem structure, not just surface-level inputs -- which means it can be trusted with more autonomous decision-making later in the hackathon.

### Lesson 7: Read the Scoring Rubric Before You Build
Demo is 30% -- almost a third of the total score. This single data point eliminates entire categories of projects (invisible backend tools, CLI-only utilities, anything that is hard to show in a 3-minute video). The scoring weights are not just evaluation criteria; they are design constraints. Let the weights guide what you build, not just what you *can* build. A project optimized for the rubric will outperform a technically superior project that ignores it.

### Lesson 8: Always Verify AI Training Data with Live Research
The initial jury analysis confidently linked Thariq to Upsolve -- it was completely wrong. Without live verification, our entire strategy would have targeted "social impact" based on a factual error. Confidence flags ([HIGH], [MEDIUM], [LOW]) help, but live research is the only real verification. This is especially dangerous when the AI presents incorrect information with high confidence: there is no syntactic difference between a correct fact and a hallucinated one. The fix is simple -- always ground-truth claims about real people and organizations with live web searches before building strategy on top of them.

### Lesson 9: Cross-Reference All Inputs Before Deciding
Had we picked an idea based on strengths alone, we might have chosen DeepVerify (most technically ambitious). Had we picked based on criteria alone, we might have chosen ElectionShield (most visual demo). Only by crossing ALL THREE inputs (strengths + jury + criteria) did CiteGuard emerge as the clear winner on every dimension. The decision matrix is not overhead -- it is the mechanism that prevents you from optimizing for one variable while ignoring the others. In a hackathon where the scoring rubric has four weighted categories and five judges with different backgrounds, single-variable optimization is a trap.

### Lesson 10: AI Prompts Carry Invisible Bias
Every adjective is a policy decision. "Be thorough" and "be concise" produce fundamentally different outputs from the same model. "Be brutally honest" and "be balanced" produce fundamentally different evaluations of the same subject. The Prewash Method -- generating the prompt, reviewing it for bias, cleaning it, then executing -- prevents compounding bias in agent systems. This is especially critical in multi-step agentic workflows where one biased prompt feeds into the next: the bias does not stay flat, it amplifies. Catching it at generation time is orders of magnitude cheaper than correcting it after it has propagated through an entire chain of reasoning.

### Lesson 11: Removing Bias Is Not Enough -- You Must Also Add Precision
"How well does this apply?" is unbiased but unmeasurable. "Rate applicability 1-5" is both unbiased AND measurable. Cycle 1 (remove adjectives) + Cycle 2 (add metrics) together produce clean, precise instructions. Without Cycle 2, you get a prompt that does not steer the model toward negativity or positivity, but still lets it wander freely within an unbounded answer space. Precision constrains the output to a comparable, reproducible format. This is the difference between asking a question and designing an instrument.

### Lesson 12: AI Confidence Is Not Alignment
Claude said "Is that what you mean?" with full confidence, after producing an interpretation that missed the user's actual intent. The lesson: never accept "I understand" from an AI at face value. Show it the clean version and compare. Confidence is a property of the model's output fluency, not a measure of how well it has captured your intent. A model can be maximally confident and maximally misaligned at the same time. The only reliable test is to present the structured version and observe the delta between what the AI assumed and what you actually meant.

### Lesson 13: Re-Examine Conclusions When New Information Arrives
The DECISION_MATRIX concluded CiteGuard wins. Then 5 new concepts appeared. Testing the old conclusion against new options using the same scoring method is how you distinguish robust conclusions from premature ones. If CiteGuard still wins after being compared against concepts designed around a new organizing principle ("Think Like a Document"), the original analysis was genuinely robust. If a new concept wins, the original analysis was limited by the assumptions it started with. Either way, the re-examination produces a stronger, more defensible decision than simply assuming the earlier conclusion still holds.


### Lesson 14: Acknowledgment ≠ Integration
When AI acknowledges contradicting evidence ("good point," "noted"), this does NOT mean it has integrated that evidence into its analysis. The AI will move forward to new tasks while carrying the old, now-contradicted conclusions. The human must explicitly demand rescoring. Passive acknowledgment is not active correction.

### Lesson 15: Confirmation Bias Compounds Across Documents
A biased conclusion in Document 1 becomes an invisible assumption in Document 2 and a foundational premise in Document 3. Each document inherits the framing of the previous one. No document goes back to check whether the foundational claims still hold. This is the Prewash problem applied to multi-step reasoning chains.

---

## Final Retrospective

*(To be filled at the end of the hackathon)*

- **What we built:** TBD
- **What worked:** TBD
- **What we would do differently:** TBD
- **Biggest surprise:** TBD
- **If we had one more hour:** TBD

---

## Open Questions

1. **What tool are we building?** -- The product has not been decided yet. Two parallel research workstreams are converging on this answer: (a) a codebase/strengths analysis running on the user's server, and (b) jury research in this session. The decision will be the intersection of personal strengths and jury appeal.
2. **What's the tech stack?** -- Depends on the product decision.
3. **How will we use the $500 API credit?** -- TBD based on what we build.

---

<sub>This log is maintained by a documentation agent designed via meta-prompting during the Claude Hackathon 2026. It is a living document updated throughout the build process.</sub>
