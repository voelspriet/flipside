# FlipSide Hackathon — Strategy Decisions

## Decision: Let 4.6 Study Problems Via Screenshots

**Date**: 2025-02-11
**Context**: During the hackathon, a UI flicker bug appeared in the clause card buttons (MD, star, copy). Rather than describing the problem or suggesting a cause, the approach was to show Claude 4.6 the screenshot and ask it to analyze.

**The strategy**: Present the visual evidence. Don't coach. Don't offer hypotheses. Let the model study the problem independently and trace the root cause.

**What happened**:

1. First attempt — showed screenshot, said "it flickers". Claude identified the DOM rebuild as the cause but implemented a text-length comparison that didn't work (threshold too small because dynamically-added UI elements inflate `textContent`).

2. Second attempt — showed the same screenshot again, said "still flickering, upper right corner". Claude switched to paragraph-count comparison. Better idea, but still didn't fix the flicker.

3. Third attempt — showed screenshot + full app state, said "hovering over first block still makes right corner flicker. write a prompt to analyse the problem and show me." This time Claude traced the actual execution path line by line and found the real root cause: `animateNewCards()` was reading `h3.textContent.trim()` which included dynamically-added badge and icon text, causing the title to never match `animatedCardTitles`, which re-triggered the drop-in animation on every 300ms render cycle.

**Why this works**:

- Forcing the model to diagnose from evidence (not hints) produces deeper analysis
- Each failed fix narrows the search space — the model eliminates hypotheses
- The screenshot provides ground truth the model can't hallucinate about
- Withholding advice prevents anchoring bias — the model explores freely
- Progressively increasing pressure ("write a prompt to analyse the problem") escalates the model's analytical depth

**When to use this pattern**:

- Visual bugs where the cause isn't obvious from code alone
- Performance/timing issues that manifest visually
- Any bug where you suspect the model's first instinct will be a surface-level fix
- When you want the model to build a mental model of the system, not just patch symptoms

**When NOT to use this pattern**:

- When you already know the cause and just want it fixed fast
- For logic bugs with no visual component
- When the model needs domain context it can't infer from screenshots

**Key insight**: The model's debugging quality scales with how much you make it work for the answer. Giving it the answer short-circuits the deep tracing that produces robust fixes.

---

## Decision: Let 4.6 Watch Itself Via Playwright

**Date**: 2025-02-11
**Context**: After three code-level fix attempts, the flicker persisted. The in-page debug monitor (MutationObserver injected into the app) showed zero mutations — it was disconnecting during the render cycle, missing all mutations. The user's instinct: "I'd rather have you watch yourself."

**The strategy**: Instead of describing what might be wrong or asking the model to guess from code, give it automated tooling to observe its own output in a real browser. Let the model write a Playwright script, run it against the live app, capture every DOM mutation programmatically, and then analyze the data.

**What happened**:

1. The in-page MutationObserver debug panel was empty because it stopped/restarted around each `doRenderResults()` call — disconnecting during the exact window when all mutations occurred.

2. A Playwright monitoring script (`flicker_watch.py`) was created to launch a real browser, trigger a sample analysis, inject a MutationObserver on the first visible clause card, and capture 30 seconds of mutations with periodic screenshots.

3. Before running Playwright, a systematic code exploration was performed — tracing every function called from `doRenderResults()` and cataloging every DOM mutation path. This revealed four remaining flicker sources that the screenshot-based approach had missed:
   - **`transition: all`** on `.clause-card` — any CSS property change triggered a 0.3s transition, amplifying micro-mutations into visible flicker
   - **Worst badge remove/re-add cycle** — every 300ms, the "Highest risk" badge was removed from all cards and recreated on the worst card
   - **`card.style.animation = 'none'`** — set on every cached card every 300ms, interacting with `transition: all`
   - **Severity summary + heatmap innerHTML rewrites** — unchanged content was being written to DOM every render cycle

4. All four sources were fixed with targeted changes: specific CSS transitions, stable badge logic, no-op mutation elimination, and innerHTML comparison guards.

**Why self-monitoring works**:

- The model can observe its own output objectively, without the anchoring bias of reading its own code
- Automated tooling captures mutations at timescales humans can't perceive (sub-millisecond)
- The Playwright approach separates "what is happening in the DOM" from "what should be happening" — evidence vs. intent
- Systematic code tracing (cataloging all mutation paths) is more thorough than screenshot-based debugging because it finds dormant bugs, not just visible ones
- When the model writes its own diagnostic tools, it understands the data format and can interpret results without translation

**When to use this pattern**:

- When visual bugs persist after multiple fix attempts
- When in-page debugging tools fail (scoping, timing, observer paradox)
- When the model needs to observe temporal patterns (mutation frequency, animation timing)
- When you want the model to build a complete mutation map of a system, not just chase symptoms

**Relationship to screenshot approach**: This is an escalation. Start with screenshots (cheap, fast, forces deep thinking). If three attempts fail, escalate to automated self-monitoring (thorough, systematic, finds all sources). The two approaches are complementary.

**Key insight**: Making the model both the author and the observer of diagnostic tooling creates a closed feedback loop. The model knows what to look for because it wrote the system, and it knows what the data means because it wrote the monitor.

---

## Prompt: Parallel Tasks & Speed Improvements Probe

**Date**: 2026-02-11
**Context**: FlipSide's analysis pipeline runs quick scan + deep analysis in parallel, but the frontend render cycle (300ms) does heavy synchronous work. This prompt forces a full-path audit from upload to rendered card.

**The prompt**:

> Identify every opportunity to reduce wall-clock time in FlipSide's analysis pipeline. Trace the full path from file upload to final rendered card — backend (app.py) and frontend (templates/index.html). For each stage, answer:
>
> 1. What runs sequentially today that could run in parallel?
> 2. What work is repeated that could be cached or memoized?
> 3. What blocks the UI that could be deferred or streamed earlier?
>
> Specific areas to probe:
>
> BACKEND
> - The quick scan and deep analysis already run as parallel threads. Can the quick scan itself be split — e.g., send each clause to a separate Opus call and merge results? What are the API rate limits and latency tradeoffs?
> - Document parsing (text extraction, chunking) — does it block before any API call starts? Can we stream the first chunk to Opus while still parsing the rest?
> - Are there synchronous operations in the SSE generator that could be async (e.g., queue polling, markdown assembly)?
>
> FRONTEND
> - doRenderResults() runs every 300ms: innerHTML rebuild → wrapClauseSections → animateNewCards → applyProgressiveDisclosure → highlightTerms → updateSidebarData → renderMinimap. Which of these are independent and could run outside the render cycle or be skipped when nothing changed?
> - marked.parse() is called on the FULL responseContent every 300ms. Can we do incremental markdown parsing (only parse the new delta)?
> - The anti-flicker cache saves/restores cards. Could we skip the innerHTML rebuild entirely for stable sections and only parse+render the new tail of the markdown?
> - wrapClauseSections() walks ALL h3 elements every cycle. Can it track which ones are already wrapped and only process new ones?
> - CSS: are there layout thrashing patterns (reading offsetHeight then writing style) that force synchronous reflows?
>
> NETWORK
> - SSE sends one event per text chunk. Could we batch multiple chunks per event to reduce HTTP overhead?
> - Are there redundant data fields being sent that the frontend doesn't use?
>
> For each finding, state: what it is, how much time it wastes (estimate), how hard it is to fix (1-3), and the specific code location (file:line).

**Why this prompt works**:

- Forces the model to trace the FULL path (upload → parse → API → SSE → render → DOM), not just optimize one layer
- Asks three distinct questions per stage (parallel, cache, defer) which prevents the model from fixating on one optimization type
- Names specific functions and line numbers to anchor the analysis in real code, not hypotheticals
- Requires difficulty estimates (1-3) which forces the model to weigh implementation cost against benefit
- Separates backend, frontend, and network — each has different optimization strategies

**When to use this pattern**: After the product works but before polish. Speed improvements have the highest ROI when the feature set is stable.

---

## Decision: Use Meta-Prompting to Assess Before Building

**Date**: 2026-02-11
**Context**: The human had a concept for a 3D card-flip animation showing two thinking processes (reader's naive impression → drafter's strategic intent). The concept was clear emotionally ("I physically want to see something flip") but unclear technically — the visualization, streaming integration, and prompt architecture were tangled together. The instinct was to start coding.

**The strategy**: Instead of building the flip card directly, write a concept assessment prompt first. Execute the prompt. Cross-reference the output against all 17 hackathon documents. Score against jury criteria. Only then update the plan and build.

**What happened**:

1. The human described the concept: "show the thinking process of user that flips into the thinking process of the person who made the clauses." Gave a concrete example: YOU (seems fair) → THEY (we want extra money, this clause should help).

2. Instead of jumping to CSS/JS, a structured assessment prompt was written with 8 analysis sections: drafter intent taxonomy, YOU→THEY contrast architecture, three-layer information flow, visualization challenge, streaming compatibility, risks, core tension, and implications.

3. The prompt was executed. It produced: 9 intent categories (Revenue Engineering, Liability Shifting, etc.), a three-phase streaming architecture (cards appear → cards flip → analysis resolves), key constraint (the flip must be literal — 3D CSS transform, not a text fade), and three risk factors (drafter voice becoming cartoonish, green clause handling, streaming timing).

4. The output was cross-referenced against all hackathon documents: DECISION_MATRIX.md, CRITERIA_ANALYSIS.md, JURY_ANALYSIS.md, LIVE_DEMONSTRATION.md, FLIPSIDE_PRODUCT.md, TOOL_CONCEPTS.md, PRODUCT_UNITY_ANALYSIS.md, strategy.md, and hackathon_log_update.md. Scored against criteria weights (Demo 30%, Impact 25%, Opus 4.6 Use 25%, Depth 20%).

5. Assessment conclusion: the flip IS the product — it scores highest on Demo (physical animation is memorable), Opus 4.6 Use (requires extended thinking to generate drafter voice), and Impact (makes the asymmetry visceral, not just reported). Only then was the plan updated and implementation started.

**Why this works**:

- Separates "is this the right thing to build?" from "how do I build it?" — the assessment answers the first question without commitment
- Cross-referencing against hackathon documents catches alignment gaps before code is written (e.g., does this help with the "Keep Thinking Prize"? Yes — the drafter voice requires deep cross-clause reasoning)
- The structured prompt format (8 sections with specific questions) prevents the model from giving a vague "this sounds great" endorsement
- Scoring against criteria weights makes the decision auditable — the jury can see why this feature was prioritized

**When to use this pattern**:

- When a concept is clear emotionally but unclear technically
- When the builder struggles to visualize the implementation
- When the feature could be the core product differentiator (high-stakes decision)
- When multiple architectural approaches exist (3D flip vs. slide vs. fade vs. morph)

**When NOT to use this pattern**:

- For incremental improvements where the approach is obvious
- For bug fixes with clear symptoms
- When time pressure requires building to learn (prototype → assess → iterate is faster than assess → build)

**Relationship to other strategies**: This is the meta-prompting pattern (Entry 1, confirmed by Cat Wu) applied to product design. The screenshot strategy (Decision 1) and Playwright strategy (Decision 2) are for debugging. This strategy is for deciding what to build.

**Key insight**: The builder's instinct when they can't visualize something is to start coding. The better instinct is to write a prompt that forces the visualization to become explicit — then execute it, cross-reference it, and only build what survives scrutiny.

---

## Decision: Write the Prompt, Not the Code

**Date**: 2026-02-11
**Context**: The 3D flip card feature had been through three debugging sessions. Each session found and fixed real bugs (markdown token collision, event listener loss, state destruction), but the flip still didn't work — the card grew and shrank repeatedly, clicks didn't register, and progressive disclosure failed. The human recognized the pattern: incremental patching of a broken architecture.

**The strategy**: Instead of a fourth round of patches, write a detailed architecture rewrite prompt that a specialist (human or AI) could execute from scratch. The prompt documents: what's broken, why it's broken, the correct architecture, exact DOM structure, CSS, JS, data flow, and verification steps.

**What happened**:

1. Three sessions of incremental fixes addressed symptoms: `[READER]:` being eaten by markdown parser (pre-processing fix), event listeners lost on DOM rebuild (delegation fix), flip state reset every 300ms (state map fix). Each fix was correct in isolation. None solved the problem.

2. Root cause identified: `doRenderResults()` runs every 300ms and does `innerHTML = html` — a total DOM wipe. You cannot build stateful interactive UI (flip cards that remember whether they're flipped) on top of a pipeline that destroys and rebuilds the DOM 3x/second.

3. Instead of coding a fourth fix, the human said: "you are allowed to build a better system from the ground off. Make a prompt for a GUI specialist."

4. A 250-line architecture prompt was written (`flip-card-rewrite-prompt.md`) specifying a two-phase approach: Phase 1 = stream normally (no flip cards), Phase 2 = after `quick_done`, extract structured data from response, build flip cards ONCE, guard the render cycle from ever touching them again.

**Why this works**:

- The prompt forces the architecture to be explicit before any code is written — unlike the three previous sessions where architecture was implicit and wrong
- A complete rewrite prompt is a better artifact than patched code: it can be executed by any agent, reviewed by the human, and modified before implementation
- The prompt captures not just WHAT to build but WHY the old approach failed — preventing the next implementer from making the same mistake
- Writing the prompt revealed the real design: two separate DOM trees (flip cards + deep analysis), not one DOM tree trying to serve both streaming and interactivity

**When to use this pattern**:

- When three or more fix attempts haven't solved the problem
- When each fix is correct but the system still doesn't work (architecture problem, not bug)
- When the human says "build it from scratch" — that's the signal
- When you need to hand off to a different session or agent

**Relationship to other strategies**: This is Decision 4 (meta-prompting to assess before building) applied to architecture recovery. Decision 4 prevents building the wrong thing. This decision prevents debugging the wrong architecture. The progression: assess concept → build → debug → realize architecture is wrong → write prompt for correct architecture → execute.

**Key insight**: When incremental patches keep failing, the problem isn't the patches — it's the architecture. Writing a prompt instead of more code forces you to design the architecture explicitly. The prompt becomes both the specification and the documentation.

---

## Decision: Split-Model Architecture (Haiku for Speed, Opus for Depth)

**Date**: 2026-02-11
**Context**: The single-Opus pipeline made users stare at a thinking panel for 30-60 seconds before seeing any content. The flip card IS the product — every second without a visible card is a second of doubt. But Opus's extended thinking is what makes the deep analysis valuable.

**The strategy**: Use Haiku 4.5 (fast, no thinking) for individual clause card scans, and Opus 4.6 (extended thinking) for cross-clause deep analysis. Run both in parallel threads.

**What happened**:

1. First card appears in ~5 seconds instead of ~40 seconds
2. Cards stream incrementally during Haiku's response — user sees them one at a time
3. Opus reasoning runs in the background while user browses cards
4. Deep analysis available on demand after Opus completes (~80-100s total)

**The bug this revealed**: Haiku and Opus produce subtly different output for the same prompt instructions. Haiku writes `Score: 88`, Opus writes `Score: 88/100`. The frontend regex assumed the Opus format, so ALL Haiku cards silently failed to parse. No errors thrown — just empty results. Fix: make format suffixes optional in all regexes.

**Key insight**: When using multiple models, your parser must be tested against EACH model's actual output. "Be strict in what you prompt, liberal in what you parse" (Postel's Law for LLMs). Different models in the same family are NOT format-identical.

---

## Decision: On-Demand Deep Analysis (Don't Spoil the Flip)

**Date**: 2026-02-12
**Context**: User testing revealed that deep analysis results appeared immediately alongside flip cards, spoiling the progressive discovery. The whole point of the flip card is suspense — "is there another side?" Showing the full verdict while the user browses Card 1 of 8 kills that.

**The strategy**: Buffer deep analysis data during streaming, render only when the user explicitly requests it via "Scrutinize this even more" button or "View scrutiny →" navigation.

**What happened**:

1. First attempt: wrapped deep analysis in a CSS `hidden` div. Failed — `doRenderResults()` still wrote to the DOM on every SSE chunk, and browser paint cycles could flash content.
2. Second attempt: added `Cache-Control: no-store` and `TEMPLATES_AUTO_RELOAD`. Fixed template caching but not the rendering.
3. Third attempt (root cause fix): `doRenderResults()` returns early when `flipCardsBuilt && !isCompareMode`. Deep analysis content stays in `responseContent` string, never touches the DOM until `revealDeepAnalysis()` is explicitly called.

**Key insight**: CSS visibility is a presentation concern, not a data concern. To truly hide content during streaming, prevent the render function from writing to the DOM at all — not just from showing it.
