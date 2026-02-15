# How Opus 4.6 Built FlipSide

**What did Claude Opus 4.6 do as the developer that Opus 4.5 couldn't?**

This document answers that question with grounded evidence from the git history, benchmarks, and the actual development process. FlipSide was built entirely through conversation with Claude Code (powered by Opus 4.6) by a journalist with zero programming experience.

---

## The Numbers

| Metric | Value |
| --- | --- |
| Total commits | 82 |
| Total insertions | 28,550 lines |
| Total deletions | 8,357 lines |
| Net codebase | 12,500+ lines (3,535 backend + 8,994 frontend) |
| Development period | 5 days (Feb 10–15, 2026) |
| Average velocity | ~5,700 lines/day |
| Architecture pivots | 7 major restructurings (>500 lines changed) |
| Bug fixes | 18 commits |
| Files | 2 main files (app.py + index.html) |

---

## 1. Large Codebase Navigation

**The benchmark:** Opus 4.6 scores **65.4%** on Terminal-Bench 2.0 (agentic coding), up from 59.8% for Opus 4.5. Anthropic specifically notes it can "operate more reliably in larger codebases" and is "better at navigating large codebases and determining appropriate modifications."

**What happened in FlipSide:** The entire frontend is a single 8,994-line HTML file containing CSS, HTML, and JavaScript inline. The backend is a single 3,535-line Python file containing Flask routes, 9+ prompt templates, SSE streaming, and parallel thread management. Every change requires understanding both files simultaneously.

**Grounded example:** Commit `0cc0c33` (stream-first pipeline) changed 962 lines across both files. The backend restructuring (new `_card_pipeline()`, `_run_parallel_streaming()`, streaming prescan) required matching SSE event types (`card_ready`, `cards_started`, `cards_instant`) with frontend handlers (`tryExtractNewClauses()`, `transitionToCardView()`, auto-reveal timer). A single mismatched event name or data format would silently break the pipeline. Opus 4.6 held the full 12,500 lines in working memory and kept the cross-file contract consistent.

**Why 4.5 would struggle:** Opus 4.5 had a 200K token context window. With both files (~50K tokens) plus conversation history plus the plan, you'd routinely hit context limits during multi-file edits. Opus 4.6's 1M token window (beta) means the entire codebase fits comfortably.

---

## 2. Multi-Step Agentic Reasoning

**The benchmark:** Terminal-Bench 2.0 tests "long-horizon agentic coding tasks" — multi-step plans executed across files. Opus 4.6 achieves the industry's highest score. Anthropic says it "plans more carefully, sustains agentic tasks for longer."

**What happened in FlipSide:** The streaming pipeline change (commits `0cc0c33` + this session) required reasoning about 5 interacting threads:

1. Upload thread → runs `_prescan_document()` with streaming Phase 1
2. N card worker threads → each generates one flip card via Haiku API
3. Pipeline forwarder thread → reads from `_card_queue`, pushes to SSE queue
4. Opus verdict thread → runs from t=0, pushes thinking/text events
5. SSE generator → yields events to the browser, handles ordering

The change involved: switching Phase 1 from a blocking API call to streaming, starting card workers during the stream as each `CLAUSE:` line arrives, forwarding individual card completions via a `Queue` bridge, removing ordered emission so the fastest card appears first, and adding a 10-second auto-reveal timer on the frontend. Each decision depended on understanding the timing relationships between all 5 threads.

**Grounded example:** The `_card_queue` design required reasoning about a race condition: the pipeline thread reads `doc['_card_total']` to know how many cards to expect, but `_card_total` is set after Phase 1 streaming finishes. If the pipeline reads it too early, it gets 0 and skips the queue. The solution: the pipeline waits for `_prescan_event` (set after Phase 1 completes and `_card_total` is stored), guaranteeing the value is correct. This kind of thread-safety reasoning across function boundaries in a 3,500-line file is where agentic planning matters.

---

## 3. Architecture Pivots Without Breaking Things

**The benchmark:** Anthropic's partners report Opus 4.6 handles "complex, multi-step coding work" more effectively. It "thinks more deeply and more carefully revisits reasoning before settling on answers."

**What happened in FlipSide:** The git history shows 7 major architecture pivots — not incremental changes, but fundamental restructurings of how the system works:

| Commit | What Changed | Lines |
| --- | --- | --- |
| `bdfeb31` | Split-model architecture: Haiku cards + Opus verdict | 4,157 ins / 3,234 del |
| `f27409c` | Verdict progress strip, investigation phases | 1,404 ins / 238 del |
| `b9ab146` | Restructure verdict from 4 threads to single report | 859 ins / 130 del |
| `4dab518` | Expert panel synthesis, parallel card architecture | 1,628 ins / 930 del |
| `99ec343` | UX overhaul: skeleton, columns, card nav | 788 ins / 266 del |
| `f92994b` | Mobile redesign: 2D flip, bottom sheet, swipe | 522 ins / 3 del |
| `0cc0c33` | Stream-first pipeline: overlapped Phase 1+2 | 962 ins / 380 del |

Each pivot required understanding the entire existing system, identifying what could be kept vs. what had to change, and making cross-file modifications that maintained consistency. Commit `bdfeb31` rewrote 3,234 lines (over half the codebase at the time) while keeping the SSE streaming protocol, prompt structure, and card parsing intact.

**Why this matters for 4.6 vs 4.5:** A pivot like `bdfeb31` (split-model architecture) isn't a diff — it's a rethink. The model had to: (1) understand the existing single-model architecture, (2) design a two-model system where Haiku does cards and Opus does verdict, (3) implement it across backend (new thread management, new event types) and frontend (new card rendering, new verdict column), (4) handle the LLM output format differences between Haiku and Opus (Score format, separators). That's planning, not just coding.

---

## 4. Self-Correction During Development

**The benchmark:** Anthropic specifically highlights Opus 4.6's "superior code review and debugging capabilities to identify its own mistakes." The model can "detect and correct its own mistakes during code review."

**What happened in FlipSide:** 18 bug fix commits in the git history. Many were caught and fixed within the same session — the model identified the problem, traced it to the root cause, and fixed it without being told what was wrong.

**Grounded examples:**

- Commit `0f2f8d9` ("Harden security, fix bugs, remove ~460 lines dead code"): Opus identified that exception messages were being sent directly to the client (security risk), that PDF page image errors could misalign indices, and that ~460 lines of dead code from old architectures were still in the file. It removed the dead code, sanitized error messages, and added per-source render timers — all in one pass.

- Commit `2450d48` ("Fix 5 code review issues"): After a code review, Opus found and fixed a playbook rendering bug, keyboard event capture leaking to other components, CDN resources loaded without integrity hashes (SRI), an LLM proxy that could be exploited, and a timer memory leak. Five unrelated issues across two files, found through self-review.

- The `_precards_ev.wait(timeout=25)` bottleneck: During this session, when asked "it still takes 30 seconds before first card," Opus traced the problem through 5 thread interactions to identify the exact line causing head-of-line blocking — a `.wait()` call in a pipeline thread that was designed to be non-blocking but was actually blocking on the upload thread's batch completion.

---

## 5. Understanding Intent from Imprecise Input

**The benchmark:** Opus 4.6 outperforms GPT-5.2 by 144 Elo points on GDPval-AA (economically valuable knowledge work). This measures the gap between "understands what you typed" and "understands what you meant."

**What happened in FlipSide:** The user is a non-coder who gives instructions like:

- "never show anlyze complete hre" + screenshot → Found the exact `editorialLoadingStatus` element, traced where "Analysis complete" is set (line 5457), and hid the entire indicator row
- "so why not jump out this screen the moment the first card is ready" → Understood this as an architecture question about pipeline parallelism, not a CSS question about screen transitions
- "it still takes 30 seconds before first card" → Didn't suggest superficial fixes. Traced the actual bottleneck (blocking Phase 1 → sequential Phase 2 → ordered emission) and proposed streaming Phase 1 with overlapped card generation
- "what was that program starting with a p" → Playwright

Every instruction required inferring the technical intent from non-technical language, then mapping it to the correct code location in a 12,500-line codebase.

---

## 6. Long-Context Retrieval Across Code

**The benchmark:** Opus 4.6 scores **76%** on MRCR v2 8-needle 1M (long-context retrieval), vs Sonnet 4.5's **18.5%**. Anthropic calls this "a qualitative shift in how much context a model can actually use."

**What happened in FlipSide:** The streaming pipeline change required connecting code at line 85 (`_prescan_document` Phase 1), line 115 (`card_worker`), line 2409 (`_card_pipeline`), line 2692 (`_run_parallel_streaming`), and line 5868 (`transitionToCardView` in the frontend). These are spread across 8,800 lines of code in two files. The model had to hold all five locations in context simultaneously to ensure the Queue bridge, event types, and completion signals were consistent.

This is the code equivalent of Anthropic's needle-in-a-haystack test: finding and connecting specific code patterns separated by thousands of lines, where a mismatch at any point causes silent failure.

---

## What 4.5 Could Have Done

To be fair, Opus 4.5 could have written any individual function in FlipSide. The prompts, the card parsing regex, the CSS animations — none of these require 4.6-level reasoning.

The difference shows up in:
- **Sustained multi-file sessions** where context accumulated beyond 200K tokens
- **Architecture pivots** that required rethinking the system, not just editing it
- **Thread safety reasoning** across 5 concurrent threads sharing mutable state
- **Self-correction** that caught security issues, dead code, and race conditions
- **Intent inference** from non-technical, typo-filled instructions

Opus 4.6 didn't write better functions. It built a better system — and rebuilt it 7 times as the design evolved — while maintaining consistency across 12,500 lines and understanding a non-coder's intent from three misspelled words and a screenshot.

---

## Sources

- [Claude Opus 4.6 Announcement](https://www.anthropic.com/news/claude-opus-4-6) — Anthropic
- [What's New in Claude 4.6](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6) — Claude API Docs
- [Opus 4.6 vs 4.5 Benchmarks](https://ssntpl.com/blog-claude-opus-4-6-vs-4-5-benchmarks-testing/) — Real-world testing results
- [Opus 4.6: A Step Change for the Enterprise](https://thenewstack.io/anthropics-opus-4-6-is-a-step-change-for-the-enterprise/) — The New Stack
- FlipSide git history: 82 commits, Feb 10–15 2026
