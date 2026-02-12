# Hackathon Log Update: From Zero Code to Working Product

## Continuation of HACKATHON_LOG.md — Building Phase

> HACKATHON_LOG.md ended at Entry 17 ("FlipSide" named) with "Product code (0 lines written)." This document covers everything that happened next.

---

### Phase 3: Product Build

**Entry 18 — From Concept to Running Application**

The product went from zero lines to a working application in a single session. Architecture decisions:

- **Backend**: Flask + Anthropic SDK, SSE streaming, parallel processing
- **Frontend**: Single-page HTML with all CSS + JS inline (~3,988 lines)
- **Model**: Opus 4.6 with extended thinking (`budget_tokens` parameter)
- **Dual-pass analysis**: Quick scan (4K thinking budget, ~60s) runs in parallel with deep analysis (full budget). Both push to a shared queue. The user sees clause-by-clause results streaming in while the cross-clause analysis runs in the background.

Key prompt architecture:
- `build_quick_scan_prompt()` — analyzes each clause individually, fast
- `build_deep_analysis_prompt()` — finds cross-clause interactions, builds negotiation playbook, produces overall assessment
- `build_compare_prompt()` — document comparison mode
- `build_system_prompt()` — the core "Think Like a Document" instruction

The "Think Like a Document" principle became the system prompt: Opus adopts the perspective of the party who drafted the document and reveals what each clause strategically accomplishes for them. Two-column output: "What the small print says" (their intent) vs. "What you should read" (what it means for you).

**Result**: 982-line backend, ~3,988-line frontend. Flask app serving SSE streams. Working upload, analysis, and progressive disclosure.

---

### Phase 4: 50 Interactive Improvement Prompts (hackaton.md Phase 1)

**Entry 19 — The 50-Prompt Experiment**

Rather than building features top-down, the approach was to give Claude 4.6 exactly 50 concrete improvement prompts and execute them one by one. Each prompt was a single interactive feature. This tested:

1. How many consecutive changes the model can make without breaking previous work
2. Whether accumulated complexity causes regression
3. How the model handles conflicting requirements between prompts

**48 of 50 prompts executed successfully. 2 skipped** (scroll snap conflicted with progressive disclosure; SVG connector lines were low ROI).

Features added, by category:

| Category | Count | Examples |
|----------|-------|---------|
| UX | 14 | Progressive disclosure, skeleton loading, dark mode, font size, reading time, keyboard shortcuts |
| Navigation | 6 | Jump to worst, sidebar index, floating prev/next, minimap, active clause highlight |
| Visualization | 6 | Risk heatmap strip, risk distribution chart, trick icons, worst clause badge |
| Animation | 5 | Score counters, card drop-in, red pulse glow, assessment bar fill, fade transitions |
| Interactivity | 4 | Clause bookmarking, personal notes per clause, expandable playbook, trick tag filtering |
| Export | 4 | Print, copy all, export bookmarked, per-clause markdown |
| Filtering | 2 | Score threshold slider, hide green clauses |
| Other | 7 | Negotiation checklist, mobile swipe, session history, easter egg, etc. |

**The progressive disclosure feature** ("show one block at a time, click for next") became the default interaction model. Cards are revealed one at a time with a "Show next clause (N remaining)" button. This was a human-requested addition (Prompt 1b) that wasn't in the original 50.

---

### Phase 5: The Flicker Bug — Four Debugging Strategies

**Entry 20 — FAILURE: Surface-Level Fix**

After the 50 prompts were implemented, a UI flicker appeared. Clause cards flickered visibly during SSE streaming — buttons (MD, star, copy) in the upper right corner would flash every 300ms.

The root cause architecture: `doRenderResults()` does `resultsContent.innerHTML = html` on every SSE chunk, destroying and recreating ALL DOM nodes. This is the fundamental anti-pattern — full DOM rebuild during streaming.

First fix attempt: anti-flicker cache using `textContent.length` comparison. Failed because dynamically-added UI elements (badges "1/4 · 51s", trick icons, "Add note", star button, etc.) inflate textContent by ~40+ characters, so the threshold was always exceeded.

**Entry 21 — FAILURE: Better Heuristic, Same Result**

Second attempt: switched from text length to paragraph count (`p, blockquote, ul, ol, table`). These structural elements come from the markdown source and aren't affected by UI enrichment. Better idea — but the flicker persisted.

**Entry 22 — Root Cause Found: Title Drift**

Third attempt: the human showed a screenshot + full app state and said "write a prompt to analyse the problem and show me." This escalation forced a line-by-line code trace that found the real root cause:

`animateNewCards()` read `h3.textContent.trim()` to check if a card was new. But for cached cards, the h3 already contained badge text and trick icon text. So the title never matched `animatedCardTitles`, causing the drop-in animation, `just-arrived` glow, and `red-pulse` to re-trigger on every 300ms render cycle.

Fix: use `card.getAttribute('data-clause-title')` instead (set once before enrichment, stable).

**Entry 23 — Strategy Decision: Let 4.6 Study Via Screenshots**

This three-attempt debugging progression was documented as a strategy decision in `strategy.md`. The key insight: withholding advice from the model forces deeper analysis. Each failed fix narrows the search space. The model's debugging quality scales with how much you make it work for the answer.

> [strategy.md — Decision: Let 4.6 Study Problems Via Screenshots](strategy.md)

**Entry 24 — FAILURE: Flicker Still Not Gone**

Even after the title drift fix, the flicker persisted. The in-page MutationObserver debug panel (Ctrl+Shift+D) showed zero mutations — it was disconnecting during the render cycle, missing all mutations.

**Entry 25 — Strategy Decision: Self-Monitoring Via Playwright**

The human's instinct: "I'd rather have you watch yourself." This led to:

1. A Playwright monitoring script (`flicker_watch.py`) — launches a real browser, triggers analysis, injects MutationObserver on the first visible clause card, captures 30 seconds of mutations with periodic screenshots, dumps to JSON, analyzes patterns.

2. A systematic code exploration that cataloged every DOM mutation path in `doRenderResults()` and its 8+ downstream functions. This revealed four additional flicker sources:

   - `transition: all` on `.clause-card` — any property change triggered a 0.3s CSS transition
   - Worst badge removed from ALL cards and recreated every 300ms
   - `card.style.animation = 'none'` set on cached cards every 300ms
   - Severity summary + heatmap innerHTML rewritten with identical content every cycle

   All four fixed with targeted changes.

3. Two more issues found via screenshot analysis:
   - **Card text truncation**: anti-flicker cache compared paragraph COUNT but not text LENGTH, so text growing within existing paragraphs (common in streaming) was blocked
   - **Auto-scroll hijacking**: with progressive disclosure showing 1 card, user was always "near bottom," causing every 300ms render to scroll back to the "Show next clause" button

   Fixed with dual-fingerprint cache (count + text length) and manual scroll tracking.

> [strategy.md — Decision: Let 4.6 Watch Itself Via Playwright](strategy.md)

**Entry 26 — Bug Still Open**

After 6+ fix attempts across two strategy approaches, the flicker and skeleton line artifacts remain partially unresolved. Logged as Task #7 for continued investigation. This is itself a boundary finding: the gap between "understanding the cause from code" and "fixing the visual symptom in the browser" is wider than expected.

---

### Phase 6: Tooling and Documentation

**Entry 27 — Decision Monitor Agent**

Built `decision_monitor.py` — a Python script that reads `strategy.md`, `hackaton.md`, `HACKATHON_LOG.md`, and git history to produce a jury-readable decision timeline. Three modes:

- `python3 decision_monitor.py` — generate full text report
- `python3 decision_monitor.py --watch` — watch for file changes, auto-regenerate
- `python3 decision_monitor.py --json` — structured JSON for integration

Reports: prompt progress (48/50), strategy decisions (2), documented AI failures (2), git activity, frontend complexity (59 event listeners, 11 CSS animations, 59 JS functions, 3,988 lines).

**Entry 28 — Phase 2: 50 Boundary-Finding Prompts**

Designed 50 boundary-finding prompts (#51–#100) for Phase 2 of the hackathon exploration. These are NOT UI improvements — they probe what Opus 4.6 can and cannot do at the edges:

| Category | Count | Example boundary |
|----------|-------|-----------------|
| Reasoning Depth | 14 | Circular clause references, contradictory clauses, nested conditionals 5+ levels deep |
| Adversarial | 10 | Prompt injection in documents, misleading clause titles, hidden Unicode |
| Scale | 5 | 100-page documents, 3-sentence handshakes, context window limits |
| Meta-Cognition | 5 | "Why this score?" follow-up calls, model analyzing its own output |
| UX Edge Cases | 5 | Empty documents, all-same-score clauses, URL input |
| Multilingual | 4 | Low-resource languages, code-switching, RTL scripts |
| Performance | 3 | 10 concurrent users, context window boundary, mega-documents |
| Accessibility | 2 | Keyboard-only navigation, ARIA/screen reader support |
| Export | 2 | Shareable URL, offline self-contained HTML |

Written to `hackaton.md` as Phase 2. All pending — not yet executed.

---

## What Exists Now

| Artifact | Lines/Size | Purpose |
|----------|-----------|---------|
| `app.py` | 982 lines | Flask backend, Opus 4.6 prompts, SSE streaming, parallel processing |
| `templates/index.html` | 3,988 lines | Full frontend — CSS, HTML, JS, 48 interactive features |
| `hackaton.md` | 200 lines | 100 prompts total: 50 executed (Phase 1) + 50 pending (Phase 2) |
| `strategy.md` | 82 lines | 2 strategy decisions documented with rationale |
| `decision_monitor.py` | 225 lines | Jury-facing decision timeline generator |
| `flicker_watch.py` | 227 lines | Playwright-based DOM mutation monitor |
| `HACKATHON_LOG.md` | 160 lines | Original pre-build timeline (Phases 0–2) |
| `docs/` | 17 files | Methodology and decision documents from pre-build phase |
| This file | — | Bridge between pre-build and build phases |

## What Changed Since "Product code (0 lines written)"

- **5,197 lines of product code** written (app.py + index.html)
- **48 interactive features** implemented in one session
- **4 AI failure patterns** documented (3 pre-build + 1 during build: the flicker debugging progression)
- **2 new debugging strategies** formalized (screenshot study, Playwright self-monitoring)
- **2 new tools** built (decision monitor, flicker watcher)
- **50 boundary-finding prompts** designed for Phase 2
- **1 unresolved bug** (flicker + skeleton lines, Task #7)

---

### Phase 7: The Perspective Flip — From Decoration to Core Product

**Entry 29 — Frontend Rewrite**

The 4,018-line frontend was rewritten from scratch to ~1,810 lines — a 55% reduction. The rewrite preserved all 48 interactive features but eliminated accumulated complexity from the 50-prompt sequential build process. Key changes:
- Consolidated CSS variables and removed redundant rules
- Simplified the render pipeline
- Cleaned up state management

Backend fixes in the same session:
- `thinking.type: 'enabled'` → `'adaptive'` (Opus 4.6 deprecation)
- Removed hardcoded `budget_tokens` — model now decides thinking depth
- Added `full_text` field to SSE responses (first 5,000 chars for compare mode)

**Entry 30 — FAILURE: CSS Animation Conflict Causing "4 Clauses → 1"**

After the rewrite, integration testing showed only 1 clause card visible instead of 4. Root cause: CSS animation specificity conflict.

Cards had `opacity: 0` as base CSS + `animation: clauseDropIn 0.4s ease forwards` to animate in + `.visible` class to show. The problem: CSS animations override class-based styles during playback. When the anti-flicker cache reinserted cached cards via `replaceChild`, the animation restarted from `opacity: 0`, making all but the newest card invisible during the 300ms render cycle.

Fix: Changed base card CSS to `opacity: 1` (always visible). Created `.new-card` class that applies `opacity: 0` + animation only to genuinely new cards. Class removed via `setTimeout` after 500ms to prevent re-animation on cache reinsertion.

This is a boundary finding: CSS animations interact with JavaScript DOM manipulation in ways that are invisible in static code review. The "4 clauses → 1" symptom was misleading — all 4 cards were present in the DOM, just invisible due to the animation restart.

**Entry 31 — Concept: The Perspective Flip is the Product**

The existing "perspective flip" was a text fade between two paragraphs. The human rejected this: "nothing is actually flipping here." What the product needed was a physical card-flip animation showing two thinking processes:

- **YOU**: The naive reader's first impression. Trusting, reasonable, slightly optimistic. "This seems fair — five days is a reasonable grace period."
- **THEY**: The drafter's strategic internal monologue. As if overheard in a strategy meeting. "The 5-day grace period generates approximately $40K annual revenue across our portfolio."
- **REALITY**: Opus 4.6's analysis (the existing analysis, now positioned as the resolution between two perspectives).

The human's key insight: "I like to show how the person who came up with the clause had a very specific reason to have this clause, sometimes with an intention of making more money. So maybe we should show the thinking process of user that flips into the thinking process of the person who made the clauses."

**Method used**: Meta-prompting pattern (Entry 1, confirmed by Cat Wu at AMA). Instead of jumping to implementation, a concept assessment prompt was written first, then executed. The prompt analyzed: drafter intent taxonomy, YOU→THEY contrast architecture, three-layer information flow, visualization challenge, streaming compatibility, and what could go wrong. This was then cross-referenced against all hackathon documents and jury criteria (Demo 30%, Impact 25%, Opus 4.6 Use 25%, Depth 20%).

The assessment concluded: the flip IS the product. Not decoration on a report — the experience of seeing your naive reading physically transform into the drafter's calculated reasoning. Green clauses (safe) don't flip — their absence of flip IS the signal.

**Entry 32 — Strategy Decision: Assess Before Building**

> Documented in strategy.md as "Decision: Use Meta-Prompting to Assess Before Building"

When the human struggled to visualize the flip concept, the instinct was to build it. Instead: write a prompt to assess whether it works before coding a line. The prompt was executed, cross-referenced against 17 hackathon documents, scored against criteria and jury profiles, and validated against streaming architecture constraints. Only then was the plan updated and implementation started.

This is the meta-prompting pattern applied to product design, not just prompt engineering.

**Entry 33 — Flip Card Implementation**

Changes to backend prompts (app.py):
- `build_quick_scan_prompt()` — added `[READER]` block per clause. The reader voice is the front of the flip card: what a normal person thinks on first reading.
- `build_deep_analysis_prompt()` — added `[DRAFTER]` block per cross-clause interaction. The drafter voice is the back: the strategic thinking revealed on flip.

Changes to frontend (templates/index.html, grew from ~1,810 to ~2,060 lines):
- **CSS**: 3D flip card system — `perspective: 1200px`, `rotateY(180deg)`, `backface-visibility: hidden`, `transform-style: preserve-3d`. Front/back with position-switching on flip (front→absolute, back→relative) to handle variable card heights. `@media (prefers-reduced-motion: reduce)` fallback.
- **JS**: Four new functions — `styleReaderBlocks()` (regex parses `[READER]:` from markdown), `styleDrafterBlocks()` (same for `[DRAFTER]:`), `buildFlipCards()` (wraps clause cards in 3D flip containers), `triggerFlips()` (staggered 400ms flips, red first, yellow second, green stays face-up).
- **Streaming integration**: Quick scan → cards appear face-up showing reader's naive interpretation. Deep analysis arrives → cards flip one at a time as drafter voice is parsed. "Flipping perspective..." status message during transition.

Boundary-finding prompt #71 ("Add a drafter perspective toggle") from Phase 2 was the seed that evolved into this core product feature. Updated in hackaton.md.

**Entry 34 — Flip Cards vs. Render Cycle: Architecture Failure**

Three bugs prevented the flip cards from working in the live app:

1. **Markdown link reference collision**: `[READER]:` is valid markdown syntax (`[label]: url`). `marked.parse()` silently consumed the tokens, producing no output. No reader-voice divs → no flip cards built → everything rendered as regular clause cards. Fix: pre-process `responseContent` to replace `[READER]:` → `FLIPSIDE_READER:` before parsing.

2. **Event listeners lost on DOM rebuild**: The 300ms render cycle does `innerHTML = html` which destroys all DOM elements. Per-element `addEventListener` calls on flip buttons were lost every cycle. Fix: event delegation on the container element.

3. **Flip state destroyed every 300ms**: `buildFlipCards()` rebuilt all flip cards each cycle, resetting `.flipped` CSS class and retriggering the woosh entrance animation ("card grows and shrinks repeatedly"). Fix attempted: state preservation via Map + woosh-done tracking.

Despite all three fixes, flipping still didn't work. The fundamental problem: **you cannot build stateful interactive UI on top of a pipeline that destroys and rebuilds the entire DOM 3x/second.** Each fix addressed a symptom, but the architecture was wrong.

This is a boundary finding: the streaming render cycle (innerHTML rebuild every 300ms) is fundamentally incompatible with stateful 3D flip cards. No amount of patching (state maps, event delegation, caching) can reconcile the two. The DOM must be built once and left alone.

**Entry 35 — Strategy Decision: Meta-Prompt for Architecture Rewrite**

> Documented in strategy.md as "Decision: Write the Prompt, Not the Code"

After three sessions of incremental patching failed, the human said: "you are allowed to build a better system from the ground off. Make a prompt for a GUI specialist that does this."

Instead of attempting a fourth round of patches, a detailed rewrite prompt was written (`flip-card-rewrite-prompt.md`) that:

1. **Diagnoses the root cause**: the 300ms `doRenderResults()` cycle does `innerHTML = html`, destroying all state
2. **Specifies the new architecture**: two-phase rendering — Phase 1 streams normally (no flip cards), Phase 2 builds flip cards ONCE after `quick_done` from extracted structured data, then guards the render cycle from touching them
3. **Includes complete DOM structure, CSS, click handling, progressive disclosure, animation, and deep analysis integration**
4. **Provides a 10-step verification checklist**

This applies the meta-prompting pattern (Decision 4) to architecture: instead of coding the fix, write a prompt that makes the fix inevitable. The prompt IS the architecture document.

---

## What Exists Now

| Artifact | Lines/Size | Purpose |
|----------|-----------|---------|
| `app.py` | ~893 lines | Flask backend, Opus 4.6 prompts with [READER]/[DRAFTER], SSE streaming, parallel processing |
| `templates/index.html` | ~2,100 lines | Full frontend — CSS 3D flip cards, 48 interactive features, streaming integration |
| `flip-card-rewrite-prompt.md` | ~250 lines | Architecture rewrite prompt for flip card system |
| `hackaton.md` | 200 lines | 100 prompts total: 48 executed (Phase 1) + 50 pending (Phase 2, #71 evolved into core) |
| `strategy.md` | ~200 lines | 5 strategy decisions documented with rationale |
| `decision_monitor.py` | ~230 lines | Jury-facing decision timeline generator |
| `flicker_watch.py` | 227 lines | Playwright-based DOM mutation monitor |
| `HACKATHON_LOG.md` | 240 lines | Original pre-build timeline (Phases 0–4) |
| `docs/` | 17 files | Methodology and decision documents from pre-build phase |
| This file | — | Bridge between pre-build and build phases |

## What Changed Since "Product code (0 lines written)"

- **~2,953 lines of product code** written (app.py + index.html)
- **48 interactive features** implemented in one session
- **Frontend rewritten** from 4,018 to ~2,060 lines (49% reduction)
- **Perspective flip** added as core product feature (3D card animation)
- **6 AI failure patterns** documented (3 pre-build + 3 during build: flicker debugging, CSS animation conflict, render cycle vs. stateful UI)
- **2 debugging strategies** formalized (screenshot study, Playwright self-monitoring)
- **2 product strategies** formalized (meta-prompting for product design, meta-prompting for architecture)
- **2 tools** built (decision monitor, flicker watcher)
- **1 architecture rewrite prompt** written (flip-card-rewrite-prompt.md)
- **50 boundary-finding prompts** designed for Phase 2 (#71 evolved into core feature)

---

### Phase 8: 10 Opus 4.6 Capabilities Sprint

**Entry 36 — Opus Capabilities Audit & Implementation**

Ran a structured audit of 10 untapped Opus 4.6 capabilities. All 10 evaluated by parallel agents, ranked by (Demo Impact × Feasibility), and implemented in a single session:

1. **Vision / multimodal** — PDF pages as images to deep analysis, detects visual formatting tricks
2. **Tool use** — `assess_risk` + `flag_interaction` structured tool schemas
3. **Multi-turn follow-up** — `/ask/<doc_id>` endpoint with SSE streaming
4. **Confidence signaling** — HIGH/MEDIUM/LOW badges on flip cards with hover reasons
5. **Self-correction** — Quality Check section reviews own analysis
6. **Benchmark comparison** — Fair Standard Comparison against industry norms
7. **Visible thinking** — Collapsed reasoning panel, "Show the full report" button
8. **Methodology disclosure** — "How Opus 4.6 Analyzed This Document" section
9. **Prompt caching** — `cache_control: {type: 'ephemeral'}` on system prompts
10. **Document retention** — Documents kept for follow-up questions

**Entry 37 — Reverse Proxy Deployment Fix**

Deployed to server behind `/flipside/` prefix. All JavaScript fetch/EventSource calls used absolute paths → 404. Fixed with `BASE_URL = {{ request.script_root | tojson }}` prepended to all 5 API paths.

---

## What Exists Now

| Artifact | Lines/Size | Purpose |
|----------|-----------|---------|
| `app.py` | 1,230 lines | Flask backend, 7 prompts, vision, tool use, follow-up, caching, SSE |
| `templates/index.html` | 3,139 lines | Full frontend — flip cards, confidence, follow-up, prefix-aware |
| `prompts/` | 3 files | Opus capabilities audit, gap analysis, feasibility |
| `hackaton.md` | 200 lines | 100 prompts: 48 executed (Phase 1) + 50 pending (Phase 2) |
| `strategy.md` | ~246 lines | 7 strategy decisions documented |
| `decision_monitor.py` | ~230 lines | Jury-facing decision timeline generator |
| `HACKATHON_LOG.md` | ~300 lines | Original timeline (Phases 0–6) |
| `docs/` | 18 files | Methodology and decision documents |
| This file | — | Bridge between phases |

## What Changed Since Last Update

- **+248 lines** in `app.py` (vision, tool use, follow-up, caching, prompts)
- **+318 lines** in `templates/index.html` (confidence, follow-up, tools, prefix fix)
- **10 Opus 4.6 capabilities** implemented and visible in product
- **Deployed to server** with reverse proxy support
- **Phase 2 probes partially addressed**: #59 (follow-up), #60 (self-correction), #67 (confidence), #68 (jurisdiction via benchmark), #69 (vision/OCR)

---

### Phase 9: The Document's Perspective — UX as Argument

**Entry 38 — Reassurance Headlines: Think Like the Drafter's Marketing Team**

The flip card front showed clause titles like "SECTION 1 — RENT AND LATE FEES." Accurate but neutral. The human's insight: "make the front as POSITIVE as possible to increase the effect of the flip."

This is "Think Like a Document" applied to UX design. The drafter doesn't just write clauses — they FRAME them. A late fee clause isn't presented as a punishment mechanism; it's framed as "Flexible payment grace period." The reassurance headline on each card front is how the drafter WANTS you to feel: warm, protected, taken care of. Then the back reveals what the clause actually does.

Added `[REASSURANCE]` field to both card scan prompts. Parser extracts it. Card front shows it as large, bold, green text — the first thing the user reads. Maximum contrast when the card flips to red.

**Entry 39 — Document Preview as Navigation Map**

The sidebar showed a static document thumbnail. The human asked: "can we scroll the actual text in the left, and match the flip cards with what's happening in the text?"

Implementation: the document preview became a scrollable, interactive map. Each clause detected during streaming gets a numbered marker (colored circle: green/yellow/red) injected at its position in the document text. Click a marker → navigate to the matching card. Navigate to a card → preview auto-scrolls to show the clause in context.

**First approach failed**: sequential `innerHTML` modifications caused cascading corruption. When clause marker 1 was injected as a `<span>` tag, clause 2's search found different text because the HTML structure had changed. Each subsequent injection made it worse — clause numbers drifted, highlights overlapped, or disappeared.

**Fix**: `rebuildPreviewHighlights()` — always rebuilds from clean `escapeHtml(documentFullText)` source. Stores all clause positions in a `clauseHighlightData[]` array, finds all positions in one pass, injects all markers simultaneously. No sequential corruption because the base text is never modified.

**Why this matters for "Think Like a Document"**: The preview markers reveal the drafter's PLACEMENT STRATEGY. Clusters of red markers show where dangerous clauses are concentrated. Gaps between markers show safe zones. The spatial relationship between clauses becomes visible — you see the document the way the drafter structured it.

**Entry 40 — Reversed Text: When You Can't Think Like a Document**

A Belgian Carrefour coupon booklet produced garbled text: "teh ni neremusnoc eT" instead of "Te consumenre in het." The PDF had characters in reversed order — pdfminer extracted them faithfully wrong.

You can't "Think Like a Document" if the document is unreadable. Three approaches attempted:

1. **Hardcoded consonant heuristic** — Detected 5+ consecutive consonants. Failed: reversed Dutch still has vowels mixed in.
2. **Haiku cleanup for all text** — Called Haiku 4.5 to clean every document. Worked but added 3.5 seconds to clean text that didn't need cleaning.
3. **Hybrid gate (final)** — Fast dictionary-based detection (`_has_garbled_text()`) checks if reversed words match common words better than forward words. Only calls Haiku when garbled text is detected. 0ms for clean text, ~2s only when needed.

**Key insight**: Postel's Law for document analysis — be liberal in what you accept (garbled, reversed, OCR artifacts), strict in what you analyze (clean text only). The cleanup step is a PREREQUISITE for any analysis.

**Entry 41 — Sidebar Profile: Context Before Content**

The sidebar evolved through three iterations:

1. **2x2 metadata grid** — TYPE, DRAFTED BY, YOUR ROLE, JURISDICTION in a card with labels. Too tall, competed with document preview.
2. **Horizontal pills** — Same metadata as compact pills on one line. Better, but still stacked vertically with thumbnail below.
3. **Profile row (final)** — Small 72×96 thumbnail upper-left, pills flowing next to it. The thumbnail shows the full first page (`object-fit: contain`, no cropping) — you see what the document LOOKS like before any analysis.

This is context-as-framing. Before a single flip card appears, the user knows: what type of document this is, who drafted it, what role they play, and what the document physically looks like. The drafter's identity is visible before the drafter's strategy is revealed.

**Entry 42 — Bilingual Analysis: Two Languages, Two Perspectives**

For non-English documents, analysis was in the document's language (correct per "Think Like a Document" — analyze in the drafter's language). But English-speaking users couldn't understand the results.

Solution: bilingual cards. The primary analysis stays in the document's language. Each flip card gets collapsible English translations via `<details>` — "Show in English" reveals the small-print and should-read columns in English.

For deep analysis: the model writes a `## English Summary` section at the end. Frontend detects it and wraps it in a collapsible toggle: "Show full report in English." The summary is condensed (cross-clause interaction summaries + top concerns + key actions), not a full translation.

**Why "Think Like a Document" matters here**: The drafter wrote in their language for their jurisdiction. Analyzing in that language captures jurisdiction-specific nuances. But the USER thinks in their language. The bilingual approach serves both: drafter's language for accuracy, user's language for accessibility. Two perspectives, literally.

**Entry 43 — MCP Evaluation: What FlipSide Doesn't Need**

Evaluated whether MCPs (Model Context Protocol) would improve the product. Conclusion: no.

FlipSide's value is in the reasoning (perspective flip, cross-clause detection, villain voice), not in data fetching. MCPs add latency mid-stream and complexity for zero analytical gain. The parallel streaming pipeline already takes 30-90s — tool calls during generation would make it slower.

Where MCPs WOULD help (post-hackathon): pulling jurisdiction-specific consumer protection laws, standard contract templates for Fair Standard Comparison, or legal precedent databases. Not needed for the core product.

### Phase 10: The Reality Check Column — Making Analysis Tangible

**Entry 44 — Three-Column Layout: Spatial Information Architecture**

The flip card had everything on two sides: front (reassurance + reader voice) and back (small print + should-read + bottom line + villain voice). The user insight: "What you should read" doesn't belong on the card back — it belongs in its OWN space, because it's what the user takes away.

New layout: left sidebar (document preview), center (flip cards), right column ("Your reality check"). The insight column drops in animated when a card flips, color-coded by risk (red/yellow/green gradient + left border). Disappears when you navigate or flip back.

**Why three columns**: Each column maps to a conceptual layer:
- Left = the raw document (what the drafter published)
- Center = the drafter's intent (what the small print really says)
- Right = your reality (what this means for your wallet/rights)

**Entry 45 — "Find in Document" Bidirectional Navigation**

Cards already had preview→card navigation (click numbered markers). Added the reverse: "Find in document ↑" link on each card front. Click it → preview scrolls to the matching clause. On mobile (≤900px), also scrolls the page to show the preview.

**Entry 46 — "What Does This Mean For You": From Abstract to Concrete**

"What you should read" says the PRINCIPLE ("your debt grows faster than you can pay"). But consumers need EXAMPLES with numbers. Added `[FIGURE]` and `[EXAMPLE]` structured output to the prompt:

- `[FIGURE]`: Single worst-case stat, rendered at 1.35rem bold in risk color. Examples: "$4,100 total debt from one missed payment" / "$0 payout on a $50,000 claim" / "30 days or you lose all rights"
- `[EXAMPLE]`: 2-3 sentence scenario using the document's actual figures. Rendered smaller, muted, with dollar amounts and time periods highlighted in risk color via regex.

**Zero processing delay**: Same Haiku streaming call, ~30 extra tokens per clause. The structured format (`[FIGURE]`/`[EXAMPLE]` tags) is more reliable than parsing numbers from free text.

**Why this matters**: The figure IS the graphic. "$4,100" in 1.35rem bold red is more visually impactful than any chart. Financial literacy research shows consumers understand "$160 extra next month" far better than "8% compound rate." The insight column now escalates from abstract (should-read) to concrete (figure + example).

**Entry 47 — "Now Flip It" Call to Action**

The flip trigger was a subtle text link ("See the other side →"). Invisible to many users. Changed to a solid rust-colored pill button with white bold text: "Now flip it →". Hover lifts 1px with deeper shadow. The button IS the invitation — it must look clickable, not like a footnote.

---

## What Exists Now

| Artifact | Lines/Size | Purpose |
|----------|-----------|---------|
| `app.py` | ~1,385 lines | Flask backend, prompts with [FIGURE]/[EXAMPLE], vision, bilingual, SSE |
| `templates/index.html` | ~3,800 lines | Three-column layout, flip cards, insight column, clause markers |
| `hackaton.md` | 200 lines | 100 prompts: 48 executed (Phase 1) + 50 pending (Phase 2) |
| `strategy.md` | ~370 lines | 10 strategy decisions documented |
| `decision_monitor.py` | ~230 lines | Jury-facing decision timeline generator |
| `docs/` | 18+ files | Methodology and decision documents |
| This file | — | Bridge between phases |

## What Changed Since Last Update

- **Three-column layout**: sidebar (document) + center (flip cards) + right (insight column)
- **Insight column**: animated drop-in on flip, risk-colored, with "What you should read" + "What does this mean for you"
- **[FIGURE] + [EXAMPLE]**: structured prompt output → big headline stat + narrative with highlighted numbers
- **Number highlighting**: dollar amounts, percentages, and time periods auto-highlighted in risk color
- **"Find in document"**: bidirectional card↔preview navigation
- **"Now flip it"**: prominent rust-colored CTA button replacing subtle text link
- **Mobile responsive**: all new elements scale properly down to 380px
- **Bilingual support**: [EN-FIGURE] and [EN-EXAMPLE] for non-English documents

## What Does Not Exist Yet

- Demo video
- 100–200 word summary
- Testing with diverse document types

**Deadline: February 16, 3:00 PM EST**

---

<sub>This document bridges HACKATHON_LOG.md (pre-build) and the current state. Updated February 12, 2026.</sub>
