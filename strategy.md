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
