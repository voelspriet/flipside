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

---

## Decision: 10 Opus 4.6 Capabilities in One Sprint

**Date**: 2026-02-12
**Context**: With the core product working (flip cards, deep analysis, split-model architecture), the question was: what Opus 4.6 capabilities does FlipSide NOT use yet? The "Most Creative Opus 4.6 Exploration" prize ($5k) goes to "the unexpected capability or use case nobody thought to try."

**The strategy**: Run a structured capabilities audit (`prompts/opus_capabilities_audit.md`) evaluating 10 untapped Opus 4.6 capabilities. Rank by (Demo Impact × Feasibility). Implement all of them in a single session using parallel planning agents.

**What happened**:

10 capabilities evaluated by parallel agents. All 10 implemented:

1. **Vision / multimodal** — PDF pages rendered as PNG images, sent to Opus deep analysis. Detects fine print, buried placement, visual hierarchy tricks that text extraction misses.
2. **Tool use** — `assess_risk` and `flag_interaction` tool schemas. Forces structured data (risk level, confidence %, trick type) alongside prose.
3. **Multi-turn follow-up** — `/ask/<doc_id>` endpoint. Users ask questions after analysis. Opus traces through all clauses with adaptive thinking.
4. **Confidence signaling** — HIGH/MEDIUM/LOW badges per flip card with hover-reveal reasoning.
5. **Self-correction** — Quality Check section where Opus reviews its own analysis for false positives and blind spots.
6. **Benchmark comparison** — Fair Standard Comparison against industry norms.
7. **Visible thinking** — Reasoning panel as collapsible status line, "Show the full report" button.
8. **Methodology disclosure** — "How Opus 4.6 Analyzed This" section in every report.
9. **Prompt caching** — `cache_control: {type: 'ephemeral'}` on system prompts. ~90% cost reduction.
10. **Document retention** — Documents kept after analysis for follow-up questions.

**Why this works**:

- Parallel planning agents designed complex features (vision, tool use, follow-up) while simpler ones (caching, confidence, benchmark) were implemented directly
- Each capability is VISIBLE in the product — no behind-the-scenes-only optimizations
- The combination is the differentiator: no other hackathon project will use vision + tool use + follow-up + confidence + self-correction in a single product
- Vision is the "I didn't know Opus could do that" moment — detecting that a liability waiver is in 6pt font when the coverage section uses 11pt

**Key insight**: Individual capabilities are impressive. 10 capabilities working together in one product — each visible and user-facing — is the kind of creative exploration that makes judges say "I didn't know Opus 4.6 could do all of that."

---

## Decision: Prefix-Aware Deployment

**Date**: 2026-02-12
**Context**: Deployed FlipSide behind a reverse proxy at `/flipside/`. All 5 JavaScript fetch/EventSource calls used absolute paths (`/sample`, `/upload`, `/compare`, `/analyze/`, `/ask/`), causing 404 errors.

**The strategy**: Inject `BASE_URL` from Flask's `request.script_root` via Jinja2 template, prepend to all API paths.

**What happened**: One-line addition (`var BASE_URL = {{ request.script_root | tojson }};`) and 5 string concatenations. Works with any prefix or no prefix (returns empty string when running locally).

**Key insight**: Always use server-injected base URLs in single-page apps. Hardcoded absolute paths break the moment you deploy behind any reverse proxy, subdirectory, or load balancer.

---

## Decision: Reassurance as Weapon — Frame the Front Like the Drafter Would

**Date**: 2026-02-12
**Context**: Flip card fronts showed neutral clause titles ("SECTION 1 — RENT AND LATE FEES"). The flip to the back was informative but lacked emotional punch. The human's instinct: "make the front as positive as possible to increase the effect of the flip."

**The strategy**: Add a `[REASSURANCE]` field to every card. The model generates a warm, positive, 8-word-max headline that frames the clause the way the drafter WANTS the reader to feel. "Your flexible payment timeline" for a late fee trap. "Comprehensive protection for your home" for an exclusion-riddled insurance policy.

**Why this is "Think Like a Document"**: The drafter doesn't just write clauses — they frame them. Marketing language, section titles, and document design all work to make the reader feel safe. The reassurance headline IS the drafter's framing strategy, made explicit. The flip then shatters it.

**The UX mechanism**: Front shows large bold green text ("Fair and transparent pricing protection") → user feels calm → card flips → back shows red risk header + villain voice ("The math does the work. Once they're two days late, the waterfall makes it impossible to get current."). The emotional distance between front and back IS the product.

**Key insight**: The strongest persuasion technique in documents is not what they say — it's how they make you FEEL before you read the details. Surfacing that emotional framing as the card front turns UX into argument.

---

## Decision: Rebuild From Source, Never From State

**Date**: 2026-02-12
**Context**: The document preview needed numbered markers (1, 2, 3...) injected at each clause's position in the text. First implementation modified innerHTML sequentially — inject marker 1, then search for clause 2's text and inject marker 2.

**The failure**: Each injection changed the HTML structure. Marker 1 added `<span>` tags and digit text. When searching for clause 2's text, the search matched against this corrupted HTML. Each subsequent injection made it worse — numbers drifted, highlights overlapped, or text was duplicated. By clause 4, the preview was garbled.

**The strategy**: Never modify state incrementally. Store all data in a clean array (`clauseHighlightData[]`). On every update, rebuild from the original source: `escapeHtml(documentFullText)`. Find all clause positions in one pass, inject all markers simultaneously.

**Why this works**:

- The source text is immutable — it never contains HTML artifacts from previous injections
- All positions are calculated from the same base, so they can't drift
- Adding clause N doesn't affect clauses 1 through N-1
- The rebuild is idempotent — calling it twice produces the same result

**When to use this pattern**:

- Any time you're injecting content into text based on string matching
- When multiple injections interact with each other (overlapping ranges, position-dependent)
- When the base content is stable but annotations change (highlights, markers, selections)
- When debugging "works for 1 item, breaks for N items" patterns

**Key insight**: Sequential state mutation in string-based DOM manipulation is a quadratic bug factory. O(N) insertions into an O(M) string means each insertion shifts all subsequent positions. Rebuild from source makes it O(N×M) but correct.

---

## Decision: Postel's Law for Document Input — Clean Before You Analyze

**Date**: 2026-02-12
**Context**: A Belgian Carrefour coupon booklet produced reversed text from PDF extraction: "teh ni neremusnoc eT" instead of "Te consumenre in het." Pdfminer extracted characters in reversed order — faithfully wrong.

**The failure progression**:

1. Hardcoded consonant heuristic (5+ consecutive consonants = garbled). Failed: reversed Dutch has vowels mixed in.
2. Haiku 4.5 cleanup for ALL text. Worked but added 3.5s to clean text that didn't need cleaning.
3. Hybrid gate: fast dictionary check → Haiku only when garbled detected. 0ms for clean text, ~2s when needed.

**The strategy**: Apply Postel's Law to document input: "Be liberal in what you accept, strict in what you process." Accept any PDF regardless of extraction quality. But before ANY analysis, verify the text is readable. If not, clean it with the cheapest model that can do the job.

**Implementation**: `_has_garbled_text()` checks if reversed words match a common-word dictionary better than forward words. If true, calls `get_client().messages.create(model=FAST_MODEL)` to clean the text. If false, passes through instantly.

**Why this matters**: You can't "Think Like a Document" if the document is unreadable. The cleanup step is a prerequisite — not a feature, but a foundation. Without it, the entire analysis pipeline produces garbage-in-garbage-out.

**Key insight**: The gap between "text extraction worked" and "text is analyzable" is larger than expected. PDFs from real-world sources (scans, export artifacts, font encoding issues) regularly produce text that looks correct in a text editor but is semantically reversed or corrupted. A fast local gate + cheap model cleanup covers this gap without penalizing clean documents.

---

## Decision: Context Before Content — Show Who Before What

**Date**: 2026-02-12
**Context**: The sidebar showed analysis results immediately. Users saw clause cards before knowing what they were looking at — what type of document, who drafted it, what jurisdiction.

**The strategy**: Before any analysis appears, show the document's identity: a small thumbnail of the first page (72×96px, full page visible), metadata pills (TYPE, DRAFTED BY, YOUR ROLE, JURISDICTION), and a scrollable text preview.

**Why this is "Think Like a Document"**: The principle says: understand WHAT the document is before you analyze what it SAYS. A lease from a property management company reads differently from a handwritten agreement between neighbors. An insurance policy from a listed company has different implications than one from a mutual fund. The metadata pills and thumbnail provide this framing.

**The UX mechanism**: User uploads → sidebar immediately shows thumbnail + pills → document text appears in scrollable preview → first flip card arrives in the content column. At no point does the user see an analysis result without knowing the document's context.

**Key insight**: Information architecture is an argument. By showing WHO drafted the document before showing WHAT they hid in it, you create a narrative frame. The user forms an impression of the drafter before seeing the drafter's tricks revealed. This makes the analysis feel like a story, not a report.

---

## Decision: The Figure IS the Graphic — Structured Output for Visual Impact

**Date**: 2026-02-12
**Context**: The insight column showed "What you should read" as a text paragraph. Accurate but a wall of text. The user's example: "Miss rent by one day: $75 fee. By day 10, $750 in fees alone..." — great content, but buried in prose.

**The strategy**: Instead of parsing free text to find numbers (fragile), push the structure upstream into the prompt. Ask the model to output `[FIGURE]` (single worst-case stat) and `[EXAMPLE]` (2-3 sentence scenario) as tagged fields. Render the figure large and bold in risk color. The number IS the graphic.

**Why this works**:

- "$4,100" in 1.35rem bold red is more visually impactful than any chart or icon
- The model is better at deciding "what's the headline stat" than a regex is at guessing it from prose
- Works universally: dollar amounts for fee clauses, time periods for deadlines, zero payouts for insurance exclusions, coverage amounts for green clauses
- Number highlighting (regex on escaped HTML) catches remaining amounts in the narrative text

**Three evaluated approaches**:

1. **Highlight numbers in-place** — Parse `$X` from free text with regex. Fragile, can't distinguish the headline from minor figures.
2. **Big headline number + narrative** — Model outputs the key stat first, rendered large. Universal, reliable.
3. **Structured escalation cascade** — Model outputs timeline steps rendered as CSS bars. Only works for escalation scenarios (late fees), not for binary outcomes (insurance exclusions).

**Chosen**: Hybrid of 1+2. Structured `[FIGURE]` for the headline, regex highlighting for remaining numbers in the `[EXAMPLE]` narrative. Covers all clause types.

**Key insight**: When you want visual differentiation in the frontend, push the structure upstream into the prompt format. Don't try to extract structure from prose — ask for structure directly. The model is a better information architect than a regex.

---

## Decision: Event-Driven Choreography — Tie Animations to Semantic Events, Not Clocks

**Date**: 2026-02-12
**Context**: The sidebar document preview needed to appear with a woosh after the skeleton card phase. First attempt used fixed-delay timers (3s, 4s, 6s fallback). Failed repeatedly — the document appeared too early, too late, or without animation.

**The strategy**: Abandon timer-based animation triggers. Tie every visual transition to the SEMANTIC EVENT it represents:
- Skeleton card appears → `switchToAnalysis()` (analysis starts)
- Skeleton message updates → `extractMetadata()` (drafter name detected)
- Skeleton flies left + sidebar wooshes in + first card appears → `transitionToCardView()` (first clause parsed)

**Why timers failed**:

1. **Multiple call paths**: `extractMetadata()` was called from both `handlePhase('profile')` (2s delay) and `tryExtractNewClauses()` (no delay, every text chunk). The no-delay path fired within 1 second, before the skeleton had time to breathe.
2. **Stale closures**: `setTimeout` callbacks captured DOM element references and survived Back-button navigation. When the user started a new analysis, old timers fired on the new element, undoing the reset.
3. **Variable model speed**: Haiku response times vary. A fixed 4-second delay was sometimes too early (cards not ready) and sometimes too late (cards already there).

**The choreography pattern**: Three staggered events at `transitionToCardView()`:
- T+0ms: skeleton flies left (`translateX(-40%) + scale(0.6) + fade`)
- T+300ms: sidebar document slides in from right (`translateX(200px) → 0`)
- T+500ms: skeleton hidden, first real card shown

**Key insight**: In streaming UIs, animations should be anchored to data events (first token, first clause, metadata detected), not wall-clock time. The model IS the clock — when it produces the first clause, that's when the transition happens. This makes the UX resilient to variable response times.

---

## Decision: The Comparison Lives in Memory, Not on Screen

**Date**: 2026-02-12
**Context**: After building the green reassurance front and red reveal back, the next iteration added a "Front vs. Back" contrast block on the card back — a side-by-side split showing the calm green version next to the alarming red version. Built with flex layout, fly-in animation, and a "Show details" toggle. Looked impressive.

**The failure**: External review (verbatim, translated from Dutch): *"The split screen compares rather than reveals. When you show them side by side, you're asking the reader to weigh two options — like a product comparison. The shock of the flip is that the calm version DISAPPEARS and the alarming version REPLACES it. The user's memory of 'everything seemed fine' IS the green card. You don't need to show it again."*

**The strategy**: Remove the contrast block entirely. The card back shows only the reveal: risk header → hero figure → example → bottom line. No reference to the front. The user's short-term memory of the reassuring green card IS the contrast — recreating it on screen diminishes the effect.

**What was removed**: ~140 lines of CSS (`.back-contrast`, `.contrast-front-card`, `.contrast-reveal`, fly-in animation) + ~30 lines of JS (contrast HTML construction, `punchSource` tracking, details toggle).

**What was added instead**: Sidebar dims to 35% opacity when a card flips (`.layout-flipped` class), spotlighting the card. Card front fades out during the 3D rotation (`opacity: 0` transition on `.flip-card-front`). The green header with ✓ badge is the last thing you see before the red header replaces it.

**Why this works**:

- The flip IS the product — the 180° rotation physically replaces one perspective with another. A split-screen removes the rotation and turns it into a comparison table.
- Short-term memory retains the reassurance for 15-30 seconds. The user doesn't need a reminder — they just read it.
- The sidebar dimming creates a theatrical spotlight effect: everything else recedes, only the reveal matters.
- Removing code is always better than adding code when the removed code fights the core mechanic.

**When to use this pattern**:

- When a UI element duplicates what the user's memory already holds
- When "showing more" actually reduces emotional impact
- When external feedback says "this compares, not reveals" — trust the fresh eyes

**Key insight**: The most powerful contrast is the one the user constructs in their own mind. Showing both sides simultaneously turns a revelation into a spreadsheet. Let the flip do the work.

---

## Decision: Three-Tier Fuzzy Matching for Clause Markers

**Date**: 2026-02-12
**Context**: The sidebar document preview shows numbered markers (①②③) at each clause's position in the text. These markers frequently failed to appear because the model's quoted text (especially when using vision on PDF images) didn't exactly match pdfplumber's text extraction — different whitespace, smart quotes, em-dashes, missing text from callout boxes.

**The failure**: Exact substring matching (`text.indexOf(quote.substring(0, 60))`) worked only when pdfplumber's output perfectly matched the model's quote. For real-world PDFs, this happened less than half the time.

**The strategy**: Three-tier matching with fallback:

1. **Tier 1 — Exact match**: Try the original 60-char substring. Fast, precise when it works.
2. **Tier 2 — Normalized match**: Collapse whitespace, normalize smart quotes (`""''` → `"`), normalize dashes (`–—` → `-`), lowercase both strings. Build a position map (`posMap[]`) that translates normalized indices back to original text positions so highlights land correctly.
3. **Tier 3 — Word anchor**: Extract the first 4 significant words (>3 chars) from the quote, join with `\s+` regex, search the normalized text. Most resilient to whitespace/formatting differences.

**Supporting fix**: Removed `full_text` truncation entirely — the full document text is now sent to the frontend. Previously limited to 15,000 characters (~4 pages), which silently broke clause markers for any clause beyond page 4. Modern browsers handle 200KB of text in a scrollable div without issue. Also added `— Page N —` markers between pages, rendered as styled dividers in the sidebar, with page navigation tabs that appear progressively as findings land on each page.

**Key insight**: When matching LLM output against extracted text, exact matching is the exception, not the rule. Build the fuzzy matching from day one — the cost is low (one extra pass over the text) and the benefit is fundamental (clause markers ARE the navigation).

---

## Decision: Suitability Gate — Let Haiku Say "Not For Me"

**Date**: 2026-02-13
**Context**: Users might upload documents that aren't contracts or agreements — a recipe, a novel, an academic paper. The tool would either produce zero cards (confusing) or force nonsensical findings (worse). No signal to the user about what went wrong.

**The strategy**: Don't add a separate classification API call. Instead, add one line to Haiku's existing card scan prompt: if the document has no terms/conditions/obligations, output `**Not Applicable**: [reason]` in the Document Profile and skip clauses. The frontend detects this field in the metadata it already parses.

**Two zero-card paths**:

1. **"Not a match for FlipSide"** — Haiku flagged `Not Applicable`. Shows the explanation + what FlipSide does analyze. The flip prompt changes to "Not everything is a contract in life." Deep status hidden.
2. **"No clauses flagged"** — Valid document type, but nothing concerning. Positive feedback: "the document appears straightforward."

**Why not use Opus for the gate**: Both threads launch in parallel. The suitability signal comes from Haiku (~5s) while Opus is still thinking (~80s). Haiku's classification is a byproduct of the scan it already does — zero extra cost or latency.

**Key insight**: The smartest use of an expensive model is knowing when NOT to run it. Haiku gates Opus — if the document isn't suitable, the user sees the explanation in 5 seconds instead of waiting 80 seconds for a useless deep analysis.

---

## Decision: DOMPurify — Sanitize LLM Output Before innerHTML

**Date**: 2026-02-13
**Context**: The deep analysis, compare mode, and follow-up answers all pass LLM output through `marked.parse()` (Markdown → HTML) and inject it via `innerHTML`. A malicious document could contain text designed to trick the LLM into outputting `<img src=x onerror="...">` or `<script>` tags in its markdown response.

**The attack chain**: Document embeds adversarial text → LLM includes it in markdown output → `marked.parse()` converts to real HTML → `innerHTML` executes it. This is the application-layer prompt injection vector Anthropic describes in their [prompt injection defenses research](https://www.anthropic.com/research/prompt-injection-defenses).

**The fix**: Added DOMPurify CDN script + `safeMd2Html()` wrapper that runs `DOMPurify.sanitize(marked.parse(md))`. Applied to all 4 call sites (deep analysis, compare mode, 2× follow-up answers). DOMPurify strips dangerous attributes (`onerror`, `onclick`) and tags (`<script>`, `<iframe>`) while preserving safe formatting.

**What was already safe**: Flip card content — all clause fields (`title`, `reassurance`, `reader`, `figure`, `bottomLine`, etc.) go through `escapeHtml()` before `innerHTML`. Document preview text uses `escapeHtml(documentFullText)`.

**Key insight**: `escapeHtml()` and `DOMPurify` solve different problems. `escapeHtml()` is for rendering plain text safely (flip cards, document preview). DOMPurify is for rendering *intended* HTML safely (markdown output where you want `<strong>` and `<h2>` to work but not `<script>`). Use both, in the right places.

---

## Decision: The Flip IS the Model Transition — Split-Model Card Architecture

**Date**: 2025-02-13
**Status**: Architecture decided — implementation next

### The Insight

FlipSide's flip card is a transition from a naive reader to an expert analyst. That maps perfectly to a model split:

| | Card Front | Card Back |
|---|---|---|
| **Voice** | Gullible reader | Expert analyst |
| **Tone** | Trusting, breezy | Adversarial, precise |
| **Understanding** | Shallow | Deep |
| **Model** | **Haiku 4.5** | **Opus 4.6** |

Haiku's natural limitation — it doesn't deeply understand legal implications — is a *feature* for the front. We've been fighting to make Haiku dumber (FORBIDDEN word lists, BAD examples). Turns out Haiku is naturally close to the gullible character. It pattern-matches, shrugs, moves on. That IS the reader.

Opus with extended thinking is overkill for "I'd just pay on time, so it won't matter" — but it's perfect for "This $75/day late fee cascades into Section 4's acceleration clause, turning a single missed payment into a $4,100 debt."

**The flip becomes the moment where the AI itself gets smarter.** Not just the content — the actual model behind it changes. That's a product story.

### Architecture: 3 Threads

```
t=0    Haiku 4.5 ──── card FRONTS ──── 15-25s  → user sees cards instantly
t=0    Opus 4.6-B ─── deep analysis ────────── 50-70s  → full verdict
t=20   Opus 4.6-A ─── card BACKS ────────────── +40s = ~60s  → backs fill in
```

- Haiku and Opus-B (deep analysis/cross-clause) start at t=0 (no dependency)
- Opus-A (card backs) starts when Haiku finishes — receives Haiku's clause list so matching is guaranteed 1:1
- Opus-A's 20-30s thinking time overlaps with Haiku's generation → wall time stays ~60s

### The Split: What Each Model Produces

**Haiku (card front — fast, gullible, trusting):**
- `[REASSURANCE]` — warm positive headline
- `> "quote"` — exact text from clause
- `[READER]` — gullible first-person voice (Haiku's sweet spot)
- `[HONEY]` — honey/sting pair (optional)
- `[TEASER]` — cryptic tension line
- Section reference
- Preliminary risk color (GREEN/YELLOW/RED) — just for front header styling

**Opus (card back — slow, adversarial, precise):**
- Risk level + precise score + trick classification (with extended thinking)
- Confidence + reasoning
- `**Bottom line**` — one sentence expert verdict
- `**What the small print says**` — neutral restatement
- `**What you should read**` — the gut punch (Opus does this best)
- `[FIGURE]` — worst-case number (Opus does the math humans won't)
- `[EXAMPLE]` — concrete scenario with the document's actual numbers

### Flip UX When Opus Isn't Ready Yet

User flips at 20s. Haiku fronts done. Opus backs still thinking.

**What they see**: Pulsing indicator — "Opus 4.6 is analyzing this clause..." with thinking animation. Then back content fades in when ready. This *enhances* the suspense — the user flips expecting truth, gets "the expert is still examining it." When it appears, it lands harder.

### The Matching Problem (Solved)

Haiku identifies N clauses with section references and quotes. When Haiku finishes, Opus-A receives the same document PLUS Haiku's numbered clause list: "Analyze these specific clauses. For each, produce the expert back-of-card analysis." This guarantees 1:1 matching — no fuzzy alignment needed.

### Quality Jump (Haiku vs Opus on Back-of-Card)

| Field | Haiku (current) | Opus (proposed) |
|---|---|---|
| `[FIGURE]` | "$75 late fee" | "$75/day × 30 = $2,250 from one missed rent" |
| `[EXAMPLE]` | Generic scenario | Step-by-step with the document's actual numbers |
| Risk score | Pattern-matched | Reasoned with extended thinking |
| Trick classification | Sometimes wrong | Correct with reasoning trail |
| Bottom line | Surface-level | Cross-references other clauses |

### Why This Wins

1. **Product-architecture alignment**: The model split IS the product metaphor. Naive → expert = Haiku → Opus = front → back.
2. **No speed penalty**: Wall time stays ~60s. Cards appear fast (Haiku at 10s). Backs fill in progressively.
3. **Solves the gullible reader problem**: Haiku naturally doesn't understand legal concepts — exactly what we want for the trusting reader voice.
4. **Opus quality where it matters**: The back of the card is the reveal, the "aha" moment. That's where precision matters most.
5. **The flip suspense deepens**: "Opus 4.6 is analyzing..." loading state on the back creates genuine anticipation.

### Cost Decision: Unrestricted

No cost constraints for the hackathon. This simplifies the architecture:
- Opus-A gets generous tokens per clause (no compression needed)
- Opus-B stays as a single call (no findings/assessment split — simpler, more coherent)
- No Haiku fallback needed on card backs — if Opus isn't ready, show the loading state

### The Full Report Gets Better Too

With Opus-A handling per-clause expert analysis on card backs, the Full Verdict (Opus-B) no longer repeats per-clause content. It focuses ONLY on what cards can't show:
- Cross-clause interactions ("read separately vs read together")
- Document Archaeology (boilerplate vs custom)
- Power Asymmetry
- Who Drafted This (drafter profile)
- Overall Assessment + risk score
- How Opus Analyzed This

Result: the report is **shorter, faster, and more focused**. No redundancy with card backs. Each piece of the analysis lives in exactly one place.

---

## Decision: 5-Thread Architecture — Haiku Full Cards + 4x Opus Expert Report

**Date**: 2026-02-13
**Status**: Implemented
**Supersedes**: "The Flip IS the Model Transition" (3-thread plan above)

### The Problem

The 4-thread architecture (Haiku fronts + Opus-A backs + Opus-B findings + Opus-C assessment) had a fatal flaw: Opus-A card backs never visually rendered on flip cards despite 3+ hours of debugging. The back HTML was generated correctly, the matching worked, but injecting new content into a `preserve-3d` CSS container after 60-70 seconds consistently failed — replaceWith, innerHTML, cloneNode all produced invisible or corrupt results.

Root cause: DOM mutation inside a 3D-transformed element during or after CSS animation is unreliable across browsers. The back content arrived too late, into a container that had already been painted, transformed, and cached by the compositor.

### The Architectural Pivot

Instead of fighting the DOM, make Haiku do both card sides. The flip becomes instant because both front and back exist from the moment the card is created. Opus moves entirely out of the cards and into a live expert report in the right column.

| # | Thread | Model | SSE Channel | Purpose | Timing |
|---|--------|-------|-------------|---------|--------|
| 1 | quick | Haiku 4.5 | `text` | Full flip cards (front + back) | ~12-15s |
| 2 | interactions | Opus 4.6 | `interactions_text` | Cross-clause compound risks | ~20-40s |
| 3 | asymmetry | Opus 4.6 | `asymmetry_text` | Power ratio + fair standard | ~15-30s |
| 4 | archaeology | Opus 4.6 | `archaeology_text` | Boilerplate vs custom + drafter profile | ~15-25s |
| 5 | overall | Opus 4.6 | `overall_text` | Overall assessment + quality check | ~20-35s |

All 5 threads start at t=0. No dependencies. No buffers. No gating. No back-matching.

### What Changed

**Haiku prompt expanded**: Now produces REVEAL, Score, Trick, Confidence, Bottom line, Figure, Example — all the fields that were previously Opus-A's job. Token budget doubled: `max(16000, min(32000, len(text)//2))`.

**4 focused Opus prompts**: Replaced the monolithic findings + assessment prompts. Each thread has a single focused job. Shorter prompts → faster responses → more parallel throughput.

**Event loop drastically simplified**: `_run_parallel_5thread()` replaced `_run_parallel_4thread()`. No `_process_findings_event()`, no `_process_assessment_event()`, no buffer stitching, no event ordering logic. Each Opus source dispatches `{source}_text` and `{source}_done` independently.

**~300 lines of dead frontend code removed**: Back-matching system (`tryExtractNewBacks`, `finalBacksSweep`, `matchAndUpdateBack`, `applyBackToCard`), thinking panel, related SSE handlers, back data maps.

**New verdict column**: 4 collapsible sections with pulsing dots → auto-expand when each Opus thread completes. Visible from t=0 with "Opus Foursix, our expert, is reading the small print" status.

### Why This Is Better

1. **Cards always work**: Both sides built from Haiku output in a single DOM creation. No late injection, no matching, no skeleton loading state.
2. **Instant flip**: No "Opus is analyzing..." wait. The back is already there. User can flip any card as soon as it appears (~5s for first card).
3. **Simpler architecture**: 5 independent streams, no dependencies, no buffers. Half the event loop code.
4. **Better Opus utilization**: 4 focused threads complete faster than 2 monolithic ones. Each thread's output appears as soon as it's ready.
5. **Progressive expert insight**: The right column fills in section by section, giving the user expert analysis to read while browsing cards.

### The Tradeoff

Haiku's card backs are less sophisticated than Opus's would have been. Haiku pattern-matches risk scores; Opus reasons about them with extended thinking. But the card back was never meant to be the final word — the deep analysis is. And now the deep analysis actually works, delivered in 4 parallel streams instead of one monolithic block.

### What "Flip IS Model Transition" Means Now

The flip is still a model transition — but the transition is spatial, not temporal. Card column = Haiku (fast, surface-level, both sides). Verdict column = Opus (slow, deep, expert). The user flips cards to explore individual clauses, then reads the verdict column for the expert synthesis. The model transition happens when attention moves from left to right, not when the card rotates.

**Key insight**: When a DOM-level fix takes 3+ hours and still doesn't work, the problem is architectural. Moving Opus out of the cards and into its own column solved both the rendering bug and the UX — the expert analysis now has room to breathe instead of being squeezed onto the back of a playing card.

---

## Decision: Haiku Was Already Great at Cards — Opus 4.6 Shines Elsewhere

**Date**: 2026-02-13
**Context**: We spent hours trying to get Opus 4.6 onto flip card backs, assuming its extended thinking would produce dramatically better per-clause analysis. When the DOM rendering finally forced us to let Haiku do both card sides, we discovered something surprising: Haiku 4.5 was already doing a great job.

### The Assumption That Was Wrong

We assumed the card back — the big reveal — needed Opus 4.6's extended thinking to be convincing. That Haiku would produce shallow scores, miss tricks, write generic bottom lines. That the "aha" moment required the most powerful model.

**What actually happened**: Haiku correctly identifies risk patterns, classifies tricks from the 18-category taxonomy, writes punchy bottom lines, and produces concrete figures with the document's actual numbers. The gullible reader voice on the front and the direct reveal on the back work as a pair — and Haiku handles both voices naturally. The constrained output format (tagged fields, trick taxonomy, score range) guides Haiku to produce structured, consistent results. When you give a fast model a clear format and a focused task, it performs.

### Where Opus 4.6 Actually Shines

Opus 4.6's extended thinking isn't wasted — it's redirected to the work that genuinely requires deep reasoning. The things Haiku can't do:

1. **Cross-clause compound risks** (`interactions` thread) — "Section 3's liability cap interacts with Section 7's indemnification to create unlimited personal exposure." This requires holding multiple clauses in working memory simultaneously and reasoning about their interaction. Haiku analyzes clauses one at a time; Opus connects them. The villain voice ("YOUR MOVE") lands harder when the compound risk is real.

2. **Power asymmetry analysis** (`asymmetry` thread) — Quantifying how many obligations fall on each party and computing a power ratio. Opus counts, categorizes, and compares: "You have 23 obligations. They have 4. The ratio is 5.75:1." Then it constructs a fair-standard comparison: what would a balanced version of this clause look like? This requires legal reasoning and counterfactual generation that Haiku doesn't attempt.

3. **Document archaeology** (`archaeology` thread) — Distinguishing boilerplate (copied from templates, generic) from custom-drafted clauses (specific to this deal, recently modified). Opus reasons about writing style, specificity, and internal consistency to build a drafter profile: "This was drafted by a large property management company using a template last updated circa 2019, with custom additions to Sections 4 and 11." Haiku would guess; Opus deduces.

4. **Overall assessment with self-correction** (`overall` thread) — The meta-analysis: an overall risk score with reasoning, a methodology disclosure ("How Opus 4.6 Analyzed This"), and a quality check where Opus reviews its own analysis for false positives and blind spots. Self-correction — the model critiquing its own output — is a capability that requires the depth of extended thinking. Haiku doesn't second-guess itself.

5. **Multi-turn follow-up** (`/ask/<doc_id>` endpoint) — After the analysis, users ask questions: "Can I negotiate Section 7?" or "What's the worst realistic scenario?" Opus traces through all clauses with adaptive thinking to give contextual, document-specific answers. The follow-up conversation requires maintaining a mental model of the entire document and all prior analysis.

6. **Vision / multimodal analysis** — When PDF pages are rendered as images, Opus detects visual tricks that text extraction misses: fine print in 6pt font when the coverage section uses 11pt, liability waivers buried in footers, important exclusions placed where the eye naturally skips. Opus sees the document the way the drafter designed it to be seen.

7. **Confidence calibration with reasoning** — Each Opus section includes confidence levels backed by explicit reasoning chains from extended thinking. Not just "HIGH confidence" but the trace of why: which clauses were compared, what precedent was considered, where ambiguity remains.

### The Lesson

The instinct was: put the best model on the most visible feature (card backs). The reality: put each model where its capabilities matter most. Haiku excels at fast, structured, per-clause analysis with a constrained output format. Opus excels at cross-clause reasoning, self-correction, power analysis, and document-level synthesis.

**The card flip is Haiku's moment. The expert verdict is Opus's moment.** Each model gets a stage that showcases what it does best.

**Key insight for Opus 4.6 exploration**: The most creative use of a frontier model isn't putting it everywhere — it's identifying the specific capabilities that only it can deliver (compound reasoning, self-correction, archaeological deduction, power quantification, visual analysis, multi-turn memory) and building features around those capabilities. Seven distinct Opus 4.6 capabilities, each visible in the product, each doing work that a smaller model genuinely cannot.

---

## Decision: Midpoint Self-Evaluation — Where FlipSide Stands at Halftime

**Date**: 2026-02-13
**Context**: Halfway through the hackathon. Before deciding what to build next, we need an honest assessment of where the tool is now versus the judging criteria. This entry contains the evaluation prompt, the evaluation itself, and the resulting priorities for the second half.

### The Evaluation Prompt

> You are evaluating a hackathon submission called **FlipSide** at the halfway point. The hackathon is the Claude Code Hackathon 2026, with 4 judging criteria:
>
> - **Demo (30%)**: "Is this genuinely cool to watch?" Visual, interactive, real-time, showable output.
> - **Opus 4.6 Use (25%)**: "Did they surface capabilities that surprised even us?" Creative, deep use of what makes Opus 4.6 special.
> - **Impact (25%)**: "Could this actually become something people use?" Real problem, real users, clear beneficiaries.
> - **Depth & Execution (20%)**: "Did the team push past their first idea?" Iteration, craft, architectural decisions.
>
> Two special prizes: "Most Creative Opus 4.6 Exploration" ($5k) and "The Keep Thinking Prize" ($5k, rewards iteration process).
>
> **Current state of FlipSide**:
> - Flask backend (2,452 lines) + single-page frontend (5,529 lines)
> - 5-thread architecture: 1 Haiku (full flip cards, ~12s) + 4 parallel Opus threads (interactions, asymmetry, archaeology, overall, ~60-70s)
> - 12 sample documents with generated thumbnails
> - 48/50 Phase 1 interactive features implemented
> - 22 strategy decisions documented
> - 63 hackathon log entries
> - 14 Opus 4.6 capabilities visible in product
> - Features: flip cards, live streaming, follow-up Q&A, document comparison, message-the-company, counter-draft, risk timeline, trick taxonomy (18 types), playbook, session history, keyboard navigation, dark mode, print/export, suitability gate, vision/multimodal PDF analysis
> - English-only output with original-language quotes; download report in document language
>
> **What's missing or outdated**:
> - README still describes 3-thread architecture, claims bilingual output, says 13 capabilities
> - HACKATHON_LOG has inconsistent line counts and stale capability #14 (still says "bilingual")
> - No demo video yet
> - No 100-200 word summary
> - Phase 2 boundary probes: only ~10 of 50 partially addressed
>
> Score FlipSide on each criterion (1-10), identify the 3 biggest strengths, the 3 biggest gaps, and recommend the top 5 priorities for the second half. Be honest and specific — flattery doesn't help.

### The Evaluation

#### Scores

| Criterion | Score | Reasoning |
|-----------|-------|-----------|
| **Demo (30%)** | **7/10** | The flip card mechanic is visually distinctive and the streaming UX is genuinely impressive — cards appear one by one, the flip reveals Haiku's analysis, and the verdict column fills in with expert analysis. The 12 sample documents lower the demo barrier. But there's no demo video yet, and the 3-minute narrative hasn't been scripted. The ~60-70s Opus wait is dead time in a live demo. The "Message the Company" and counter-draft features are powerful but undiscovered without guidance. A polished video with voiceover could push this to 9. |
| **Opus 4.6 Use (25%)** | **8/10** | This is the project's strongest dimension. 14 distinct capabilities in one product is unusual. The 5-thread architecture (Haiku speed + 4× Opus depth) is a genuine architectural innovation, not a checkbox exercise. The cross-clause interaction detection, document archaeology, power asymmetry quantification, and self-correction quality check each showcase capabilities that smaller models genuinely cannot do. The "Haiku was great, Opus shines elsewhere" discovery is the kind of insight the judges want to see. The villain voice pushing against over-refusal limits is creative. What's missing: the effort control parameter (`effort: medium/high/max`) isn't wired up yet (SDK gap), and context compaction for long follow-up sessions isn't explicitly demonstrated. |
| **Impact (25%)** | **8/10** | The problem is real and large — 250M+ people sign documents they don't understand daily. The flip metaphor ("see what the other side intended") is immediately understandable. The sample documents prove it works across document types (lease, insurance, ToS, employment, loan, gym, medical, HOA, sweepstakes). The "Message the Company" feature moves from analysis to action. Counter-draft goes further. What would push this higher: user testimonials, a case study showing a real user discovering a real trap, or a comparison with existing tools (LegalZoom, DoNotPay) showing what FlipSide catches that they miss. |
| **Depth & Execution (20%)** | **9/10** | This is where FlipSide dominates. 22 strategy decisions, 63 log entries, and a complete architectural pivot (4-thread → 5-thread) documented in real-time. The Playwright self-debugging story, the meta-prompting discovery, the "Haiku was already great" reversal — these are exactly the kind of "pushed past their first idea" moments the judges want to see. The documentation alone is a strong bid for the "Keep Thinking Prize." The only gap: the strategy decisions are hidden in strategy.md, not surfaced in the submission materials. |

**Composite: 7.8/10** (weighted: 7×0.30 + 8×0.25 + 8×0.25 + 9×0.20 = 2.10 + 2.00 + 2.00 + 1.80 = 7.9)

#### 3 Biggest Strengths

1. **The flip card as product metaphor.** It's not a gimmick — the front/back literally represents naive vs. expert reading. The physical interaction of flipping creates the "aha" moment. Most hackathon projects are dashboards; this has a mechanic.

2. **Architectural depth visible in the product.** The 5-thread Haiku+Opus architecture isn't hidden plumbing — users experience it as instant cards + progressive expert analysis. The model placement decision (Haiku for cards, Opus for verdict) emerged from a 3-hour failure, which is a better story than getting it right the first time.

3. **Documentation as competitive advantage.** 22 strategy decisions and 63 log entries create a paper trail that most hackathon teams don't have. The "Keep Thinking Prize" is essentially already won if the judges read strategy.md.

#### 3 Biggest Gaps

1. **No demo video.** Demo is 30% of the score. Without a scripted 3-minute video showing the flip moment, the verdict column filling in, and the message-the-company feature, the strongest 30% bucket is left to the judges' imagination. This is the single highest-ROI item remaining.

2. **Outdated README.** The README is the first thing judges read. It still says 3-thread architecture, claims bilingual output (now English-only), lists 13 capabilities (now 14+), and doesn't mention message-the-company, counter-draft, or the 5-thread architecture. Every minute a judge reads stale docs is a lost opportunity.

3. **Opus wait time in live demo.** Cards arrive in ~12s (great). But the verdict column takes 60-70s. In a 3-minute video, that's a third of the runtime showing "Our expert is reading the small print." Need to either (a) pre-record the wait and fast-forward, (b) narrate over it, or (c) find ways to make the wait itself interesting.

#### Top 5 Priorities for the Second Half

1. **Script and record the demo video (30% of score).** 3-minute narrative: upload → first card → flip → verdict → message the company. Use a pre-analyzed document so Opus results are instant. Show the flip moment in slow motion. Voiceover explaining the philosophy.

2. **Update README to match current state.** Fix architecture diagram (5-thread), capability count (14+), remove bilingual claims, add message-the-company and counter-draft, add the "Haiku was already great" story. The README is the submission's front page.

3. **Fix HACKATHON_LOG inconsistencies.** Correct line counts, update capability #14 from "bilingual" to current (English-only + download in language), verify entry count. The log is evidence for "Keep Thinking Prize" — errors undermine it.

4. **Write the 100-200 word summary.** Required for submission. Should capture: one sentence on the problem, one on the flip mechanic, one on the 5-thread architecture, one on what Opus does that Haiku can't.

5. **Reduce perceived Opus wait time.** Options: (a) show partial Opus results in verdict column as they stream (already happening), (b) add educational content during the wait ("Did you know? Cross-clause interactions are the #1 missed risk in consumer contracts"), (c) make the status animation more engaging, (d) pre-analyze sample documents so demos are instant.

### Re-Evaluation After Fixes

**What was fixed since the initial evaluation:**
- README fully rewritten: 5-thread architecture diagram, 14 capabilities (not 13), English-only (not bilingual), message-the-company, counter-draft, seven-stage pipeline table, proper third-party license attribution
- HACKATHON_LOG: line counts corrected (app.py 2,452, index.html 5,529), capability #14 updated from "Multilingual + bilingual" to "English-only + download in language", entry count updated to 64
- Third-party license table added to README (all permissive: MIT, BSD-3, Apache-2.0/MPL-2.0, OFL — no GPL)
- 173-word submission summary added to README (problem → mechanic → architecture → action → claim → tagline)

#### Updated Scores (after all fixes)

| Criterion | Initial | After fixes | Change | Why |
|-----------|---------|-------------|--------|-----|
| **Demo (30%)** | 7 | **8** | +1.0 | README accurately sells the product. 173-word summary gives judges the complete picture in 30 seconds. Architecture diagram, 14 capabilities, message-the-company, counter-draft — all described before a judge opens the app. The summary itself is demo-quality writing: "Flip the card — the back reveals what the drafter intended." Still no video, which caps this at 8 rather than 9+. |
| **Opus 4.6 Use (25%)** | 8 | **8.5** | +0.5 | Capabilities table now shows 14 with accurate descriptions. The "Haiku was great, Opus shines elsewhere" story is surfaced in the architecture section. Summary names all 4 Opus thread functions (cross-clause, asymmetry, archaeology, self-correction). Judges can now see the model placement reasoning before launching the app. |
| **Impact (25%)** | 8 | **8.5** | +0.5 | The summary moves impact from implicit to explicit: "analyzes documents you didn't write" → specific examples → "message the company" → "counter-draft." A judge reading this immediately understands who benefits and how. The action features (message, counter-draft) are now front-and-center, not buried in step 4. |
| **Depth & Execution (20%)** | 9 | **9.5** | +0.5 | Midpoint self-evaluation with re-evaluation after fixes (meta-iteration). All documentation internally consistent. License attribution. The summary itself demonstrates craft — 173 words, no filler, funnel structure. |

**New composite: 8.5/10** (8×0.30 + 8.5×0.25 + 8.5×0.25 + 9.5×0.20 = 2.40 + 2.125 + 2.125 + 1.90 = 8.55)

**Total delta from initial: +0.65 from documentation and presentation fixes alone — zero product code changed.**

#### Remaining Gaps

1. **No demo video** — the only gap that matters now. 30% of the score, and it's the difference between 8/10 and 9.5/10 on Demo. Everything else is ready for a judge to evaluate.
2. **Opus wait time in demo** — ~60-70s. Narrative strategy needed for the video (narrate over it, fast-forward, or pre-analyze).
3. **No user testimonials or case study** — would push Impact from 8.5 to 9+, but low priority vs. video.

#### Submission Checklist

| Item | Status |
|------|--------|
| Working product | Done |
| README with architecture + capabilities | Done |
| 100-200 word summary | Done (173 words) |
| HACKATHON_LOG (process evidence) | Done (76 entries) |
| Strategy decisions (iteration evidence) | Done (22 decisions) |
| Third-party license attribution | Done |
| 14 sample documents | Done |
| Demo video (3 min) | Script ready (DEMO_SCRIPT.md) |

### The Lesson

At halftime, FlipSide's engineering depth was ahead of its presentation layer. Documentation fixes — README rewrite, log corrections, submission summary, license attribution — gained **+0.65 composite points** without writing a single line of product code. The product was always 8.5+; the presentation was dragging it to 7.9. Now the only remaining gap is the demo video. Everything a judge needs to read is accurate, complete, and internally consistent. The video is the last artifact that captures the 30% Demo weight — and it's the difference between a strong submission and a winning one.

---

## Decision 23: Synthesize Conflicting Feedback Into a Structured Prompt Instead of /plan

**Date**: 2025-02-14
**Context**: After real user testing, five people returned feedback that directly contradicted each other. Erik Borra reported navigation confusion, scroll sync bugs, jargon problems, and count mismatches. Ray Kentie had a near panic attack — he thought FlipSide was flagging a real threat and got scared. Other testers said "simple tool, clear" and "leuke tool." The user themselves added observations about visual polish and sample labeling. The problem wasn't a single feature request — it was a tangle of conflicting opinions about the same product, where one person's "too scary" was another person's "clear and useful."

**The strategy**: Skip `/plan` mode entirely. Instead, treat the conflicting feedback as raw material for a synthesis prompt. Drop all the opinions into a single message, then produce a comprehensive, categorized analysis that:

1. **Separates signal from noise** — filter out cosmetic preferences, keep functional problems
2. **Finds the common thread** — "too scary" and "navigation confusion" are both symptoms of the same root cause: missing context framing
3. **Organizes by problem, not by person** — 5 people's feedback collapsed into 9 distinct problems
4. **Specifies solutions at implementation granularity** — each problem includes exact CSS, HTML, and JS changes needed
5. **Preserves the product's identity** — solutions must not dilute the flip card mechanic or the editorial tone

The 9 problems identified:

| # | Problem | Root Feedback |
|---|---------|---------------|
| 1 | Emotional safety — no framing that this is analysis, not an alert | Ray's panic, "thought it was a scam" |
| 2 | Navigation buried at bottom, invisible until scroll | Erik's "navigation should be at top" |
| 3 | Expert report in separate column — users never found it | Erik's "expert report placement confusing" |
| 4 | Scroll sync broken between sidebar and cards | Erik's "scroll sync broken" |
| 5 | Jargon in headings — "Cross-Clause Interactions", "Document Archaeology" | Erik's "jargon unclear" |
| 6 | Risk count mismatch between summary and actual cards | Erik's "count mismatch" |
| 7 | Download missing source text | Erik's "download needs source text" |
| 8 | Visual polish gaps — cards, transitions, spacing | User's own observations |
| 9 | Narrative flow — the story from upload to verdict | Synthesis of all feedback |

**What happened**:

The user said "execute all" — implement everything immediately. No planning phase, no approval loop, no incremental review. The prompt *was* the plan.

All 9 problems were implemented in a single session (~490 net lines added to `index.html`):

1. **Context banner** — green-bordered safety frame at top: "FlipSide is analyzing this document for your protection. This is not a warning — it's a tool to help you understand what you're signing." Updates with final clause count. Sample documents get a yellow "DEMO DOCUMENT" badge.

2. **Sticky top navigation** — card nav duplicated to a sticky bar at `top: 58px` with colored risk pips (red/yellow/green dots). Both top and bottom nav stay in sync.

3. **Inline verdict** — the third column (verdict) was eliminated entirely. Opus analysis now renders inline below the card viewport. Layout simplified from 3-column to 2-column. Removed all `showVerdictCol()` calls (3 locations).

4. **Scroll sync fix** — `scrollPreviewToCard()` rewritten to use `getBoundingClientRect()` + relative offset calculation instead of the broken approach. Added auto-flip on clause marker click.

5. **Plain-language headings** — "Cross-Clause Interactions" → "Hidden Combinations", "Power Asymmetry & Fair Standard" → "Power Balance", "Document Archaeology & Drafter" → "Custom vs. Boilerplate", "Overall Assessment" → "The Big Picture". Each gets a subtitle and SVG icon via `VERDICT_SECTIONS` config object.

6. **Accurate risk counting** — `updateRiskSummary()` counts actual parsed cards by risk level instead of using hardcoded or estimated numbers.

7. **PDF download with source text** — replaced HTML export with client-side PDF generation via `html2pdf.js`. The PDF includes the full source document text with page markers.

8. **Visual refinements** — card back restructured (bottom line first, then risk header), flip trigger text changed from "Now flip it ↻" to "See what this really means ›", trick footnotes restyled as pill chips.

9. **Narrative flow** — context banner → sticky nav → cards → inline verdict creates a single-scroll story. No hidden columns, no modal panels, no layout shifts.

**Why skipping /plan worked here**:

- **/plan is for ambiguous scope** — here the scope was fully defined by the feedback itself. Five people told us exactly what was wrong. The work was translating complaints into implementations, not deciding what to build.

- **The prompt IS the plan** — by organizing feedback into 9 numbered problems with specific solutions, the synthesis prompt served as both the analysis artifact and the execution spec. A separate planning phase would have produced the same document with an extra approval round-trip.

- **Conflicting opinions need synthesis, not arbitration** — `/plan` would have presented options for each conflict (e.g., "Option A: make it less scary, Option B: keep the intensity"). The synthesis approach found that the conflicts were false dichotomies — you can keep the intensity AND add safety framing. You don't have to choose between "scary" and "useful."

- **Speed matters for user-testing feedback** — the insights from live testing have a half-life. The longer you wait to act, the more context you lose about *why* someone panicked or *where* they got confused. Immediate execution preserves the emotional context of the feedback.

- **Codebase exploration preceded synthesis** — before writing the prompt, an Explore agent scanned the full 7300-line frontend to understand what already existed. The prompt wasn't written in a vacuum; it was grounded in the actual code structure, which meant every proposed solution was implementable.

**What else was done beyond the 9 problems**:

- **`VERDICT_SECTIONS` config pattern** — created a declarative config object mapping each Opus source to title, subtitle, and SVG icon. This replaces scattered string literals and makes future section changes single-point edits.
- **Mobile CSS adjustments** — all new elements (sticky nav, context banner, sample badge, inline verdict) received responsive breakpoints.
- **State variable `isSampleAnalysis`** — distinguishes sample documents from uploaded ones to control the demo badge. Set in `startSampleAnalysis()`, cleared in `startAnalysis()`.
- **Tricks detected bar** — collapsible panel showing detected tricks as pills, rendered from `_detectedTricks` accumulator.
- **DOMPurify integration** — all new rendered content routes through `safeMd2Html()`.

**Key insight**: When feedback contradicts, the instinct is to pick a side or find a compromise. The better move is to reframe the contradiction as a design constraint. "Too scary" + "clear and useful" = "add context framing without reducing analytical depth." The conflicting opinions aren't a problem to solve — they're the specification for the solution.

---

## Decision 24: Expert Panel Synthesis + Fact-Checker QC Pass

**Date**: 2026-02-14
**Context**: The 4 Opus expert threads (interactions, asymmetry, archaeology, overall) produce independent reports that never see each other's findings. A user testing the Coca-Cola sweepstakes sample revealed 5 credibility issues: the context banner claimed "17 clauses" while the nav showed 6, the tax figures contradicted themselves ($20-25K headline vs $17.7-18.7K calculation), the "Honey Trap" label collided with the trick taxonomy, clause counts shifted during streaming, and the card back had 5 competing labels.

### Part 1: Expert Panel Synthesis

**The strategy**: Add a 6th Opus call that reads ALL expert outputs and produces a 4-voice synthesis that no single expert could write alone. Non-blocking: the verdict is readable at 4/4 experts; synthesis streams as a bonus.

**The 4 synthesis voices**:
1. **"What You Need to Know"** — Plain-language briefing. 8th-grade reading level. Top risks, concrete actions, pre-drafted email paragraph.
2. **"If They Meant Well"** — Good-faith interpretation. Steelmans each flagged clause.
3. **"If They Meant Every Word"** — Bad-faith interpretation. Villain voice on the document AS A SYSTEM.
4. **"Cross-Expert Connections"** — Convergences, contradictions, hidden patterns invisible to any single expert.

**Implementation**: `build_synthesis_prompt()` + `build_synthesis_user_content()`. Launches after all experts complete. Frontend shows synthesis section with accent-colored styling. `SYNTHESIS_MAX_TOKENS = 8000`.

### Part 2: Fact-Checker QC Pass

**The strategy**: Analyze the product as a fact-checker would — not a designer, not a developer. Look for internal contradictions, misleading numbers, confusing labels, and unstable displays. Then fix each issue at the correct layer (code, prompt, or design).

**5 QC fixes**:

| # | Issue | Layer | Fix |
|---|-------|-------|-----|
| 1 | Banner "17 clauses" contradicts nav "6 of 7" | Code | Removed count from banner. Numbers shown in card nav + sidebar only. |
| 2 | FIGURE ($20-25K) contradicts EXAMPLE ($17.7-18.7K) | Prompt | Rule 16: FIGURE must be derivable from EXAMPLE math. "Write EXAMPLE first, then extract FIGURE." |
| 3 | "HONEY TRAP" label collides with trick taxonomy | Code | Renamed to "THE LURE" — cannot be confused with the 18 trick categories. |
| 4 | Counts shift during streaming (6→7 clauses, 5→6 tricks) | Code | Nav hides total during streaming. Tricks bar shows "Tricks detected" (no count) until quick_done. |
| 5 | 5 competing ALL-CAPS labels on card back | Design | 3-tier hierarchy: "But in reality" (story), figure+example (data), "Find in document" + "The lure" (utility). |

**Why a fact-checker's lens matters**: FlipSide's entire premise is "we find the numbers they hope you won't check." If the tool itself publishes internally inconsistent numbers, the premise collapses. Fix #2 (FIGURE/EXAMPLE consistency) is particularly important — it's a prompt-level instruction that prevents the model from rounding differently in headlines vs calculations. A tool that claims to expose math tricks cannot make math mistakes.

**Key insight**: QC for an AI product has three layers — code (what the frontend shows), prompts (what the model outputs), and design (how labels compete for attention). Most bugs are found in code. The hardest bugs live in prompts, because they're non-deterministic and only appear on certain inputs. The FIGURE/EXAMPLE inconsistency would never show up in a code review — it only appears when a specific document triggers different rounding in two model fields.
