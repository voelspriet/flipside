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

## What Does Not Exist Yet

- Phase 2 boundary prompt execution (50 prompts pending)
- Flicker/skeleton line fix (Task #7)
- Demo video
- 100–200 word summary

**Deadline: February 16, 3:00 PM EST**

---

<sub>This document bridges HACKATHON_LOG.md (pre-build) and the current state. Updated February 11, 2026.</sub>
