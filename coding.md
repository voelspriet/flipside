# How Opus 4.6 Built FlipSide

**0% of the code was written by a human. 14,000+ lines in 6 days, built entirely through conversation. Here's how Opus 4.6 made it possible.**

| Metric | Value |
| --- | --- |
| Lines written by a human | 0 |
| Total commits | 134 |
| Total insertions | 46,622 lines |
| Total deletions | 19,369 lines |
| Net codebase | 14,000+ lines (3,514 backend + 10,708 frontend) |
| Development period | 6 days (Feb 10–16, 2026) |
| Average velocity | ~7,700 insertions/day |
| Architecture pivots | 7 major restructurings (>500 lines changed) |
| Bug fixes | 18 commits |
| Files | 2 main files (app.py + index.html) |

Every claim below is grounded in the git history, benchmarks, and the actual development process. FlipSide was built entirely through conversation with Claude Code (powered by Opus 4.6). Not a single line was typed by a human.

---

## 1. Visual Vocabulary — Directing Code Changes Through Conversation

**The problem:** You can SEE the element you want to change, but you don't know what it's called in code. You can't say "move the `#dropZone`" if you've never opened the HTML.

**The method:** Screenshot → Element Map → Precise Instructions.

**Step 1: Show, don't describe.** Take a screenshot and ask Claude Code "how do you call each element?" Claude maps every visible element to its CSS class or ID:

| What you see | What Claude calls it |
|---|---|
| "FlipSide" (big title) | `.brand h1` |
| *"The dark side of small print."* | `.tagline` |
| *"Upload any contract..."* | `.brand-explain` |
| White card containing the upload area | `.upload-container` |
| Dashed box with "Drop a document here" | `#dropZone` / `.drop-zone` |
| "Drop a document here" | `.dz-title` |
| "or click to browse" | `.hint` |
| "PDF · DOCX · TXT" | `.filetypes` |
| Link row (Paste text / URL / Compare / FAQ) | `.upload-links` |
| Green-bordered disclaimer at bottom | `.disclaimer` |

**Step 2: Use the names.** Now you can give precise instructions:
- "Move the `.disclaimer` above the `.upload-container`"
- "Show a preview image inside the `.drop-zone`"
- "Hide the `.tagline` on mobile"
- "Change the `.brand-explain` text"

**Why it works:** The screenshot IS the specification. No ambiguity about which element you mean. No "the thing at the bottom" or "that grey box." Claude reads the screenshot, maps the visual layout to the DOM, and from that point forward you share a vocabulary.

**More sophisticated uses in this project:**
- "Show the image in the grey box" → Claude knows `.upload-container` has the white/cream card styling
- "Show image in `.drop-zone`" → targeting a specific nested element by name learned from a previous screenshot round
- Screenshot + "why is there a gap between these two?" → Claude measures the CSS margins/padding on the exact elements visible
- Screenshot + "this takes too long" → Claude traces the visual state to the code that controls when it transitions (not a CSS question — an architecture question)

**The progression:** The project started with imprecise instructions ("never show anlyze complete hre" + screenshot) and evolved into a systematic workflow: screenshot first, get the vocabulary, then direct changes precisely. The screenshot replaced the IDE — instead of right-clicking "Inspect Element," you just show Claude what you see.

**Cross-screen animation — swooshing elements between two screenshots:**

The most sophisticated use of visual vocabulary is directing animations *between* screens. The user showed two screenshots and said "keep the briefing info, swoosh it into the card nav":

| Image 12 (briefing/loading state) | Image 13 (card view) | Animation |
|---|---|---|
| `.briefing-track` "Clause readers" | `#cardNavPips` (clause pip dots) | Track ghost flies to pips area, scales down, fades |
| `.briefing-track` "Expert verdict" | `#verdictProgressStrip` (verdict building bar) | Track ghost flies to verdict strip, scales down, fades |
| `.briefing-sentence` (narration) | *(no target — decorative)* | Floats up 40px, elegant fade out |
| `#briefingDepth` ("N angles considered") | *(no target — decorative)* | Shrinks to 70%, fades out |

This produced `swooshBriefingToCardNav()` — a FLIP animation that captures source rects from Image 12's DOM, creates fixed-position ghost clones, switches to Image 13's DOM, measures target rects, then animates ghosts from source → target using the Web Animations API. The instruction pattern: "keep [Image A element], swoosh it into [Image B element]" → map elements across screenshots → FLIP animation between the two states.

---

## 2. Large Codebase Navigation

**The benchmark:** Terminal-Bench 2.0 65.4% (agentic coding), up from 59.8% for Opus 4.5.

**What happened in FlipSide:** The entire frontend is a single 10,708-line HTML file containing CSS, HTML, and JavaScript inline. The backend is a single 3,514-line Python file containing Flask routes, 9+ prompt templates, SSE streaming, and parallel thread management. Every change requires understanding both files simultaneously.

**Grounded example:** Commit `0cc0c33` (stream-first pipeline) changed 962 lines across both files. The backend restructuring (new `_card_pipeline()`, `_run_parallel_streaming()`, streaming prescan) required matching SSE event types with frontend handlers. A single mismatched event name would silently break the pipeline. The change required connecting `_prescan_document()`, `card_worker()`, `_card_pipeline()`, `_run_parallel_streaming()` in the backend and `transitionToCardView()` in the frontend — spread across thousands of lines, where a mismatch at any point causes silent failure.

---

## 3. Multi-Step Agentic Reasoning

**The benchmark:** Terminal-Bench 2.0 highest score (long-horizon agentic coding). "Plans more carefully, sustains agentic tasks for longer."

**What happened in FlipSide:** The streaming pipeline change (commit `0cc0c33`) required reasoning about 5 interacting threads:

1. Upload thread → runs `_prescan_document()` with streaming Phase 1
2. N card worker threads → each generates one flip card via Haiku API
3. Pipeline forwarder thread → reads from `_card_queue`, pushes to SSE queue
4. Opus verdict thread → runs from t=0, pushes thinking/text events
5. SSE generator → yields events to the browser, handles ordering

The change involved: switching Phase 1 from a blocking API call to streaming, starting card workers during the stream as each `CLAUSE:` line arrives, forwarding individual card completions via a `Queue` bridge, removing ordered emission so the fastest card appears first, and adding a 10-second auto-reveal timer on the frontend. Each decision depended on understanding the timing relationships between all 5 threads.

**Grounded example:** The `_card_queue` design required reasoning about a race condition: the pipeline thread reads `doc['_card_total']` to know how many cards to expect, but `_card_total` is set after Phase 1 streaming finishes. If the pipeline reads it too early, it gets 0 and skips the queue. The solution: the pipeline waits for `_prescan_event` (set after Phase 1 completes and `_card_total` is stored), guaranteeing the value is correct. This kind of thread-safety reasoning across function boundaries in a 3,500-line file is where agentic planning matters.

---

## 4. Architecture Pivots Without Breaking Things

**The benchmark:** Anthropic's Opus 4.6 announcement: "thinks more deeply and more carefully revisits reasoning before settling on answers."

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

## 5. Self-Correction During Development

**The benchmark:** Anthropic's Opus 4.6 announcement: "superior code review and debugging capabilities to identify its own mistakes."

**What happened in FlipSide:** 18 bug fix commits in the git history. Many were caught and fixed within the same session — the model identified the problem, traced it to the root cause, and fixed it without being told what was wrong.

**Grounded examples:**

- Commit `0f2f8d9` ("Harden security, fix bugs, remove ~460 lines dead code"): Opus identified that exception messages were being sent directly to the client (security risk), that PDF page image errors could misalign indices, and that ~460 lines of dead code from old architectures were still in the file. It removed the dead code, sanitized error messages, and added per-source render timers — all in one pass.

- Commit `2450d48` ("Fix 5 code review issues"): After a code review, Opus found and fixed a playbook rendering bug, keyboard event capture leaking to other components, CDN resources loaded without integrity hashes (SRI), an LLM proxy that could be exploited, and a timer memory leak. Five unrelated issues across two files, found through self-review.

- The `_precards_ev.wait(timeout=25)` bottleneck: During this session, when asked "it still takes 30 seconds before first card," Opus traced the problem through 5 thread interactions to identify the exact line causing head-of-line blocking — a `.wait()` call in a pipeline thread that was designed to be non-blocking but was actually blocking on the upload thread's batch completion.

---

## 6. Understanding Intent from Imprecise Input

**The benchmark:** GDPval-AA top score (economically valuable knowledge work — finance, legal, and other domains).

**What happened in FlipSide:** The user gives instructions like:

- "never show anlyze complete hre" + screenshot → Found the exact `editorialLoadingStatus` element, traced where "Analysis complete" is set (line 5457), and hid the entire indicator row
- "so why not jump out this screen the moment the first card is ready" → Understood this as an architecture question about pipeline parallelism, not a CSS question about screen transitions
- "it still takes 30 seconds before first card" → Didn't suggest superficial fixes. Traced the actual bottleneck (blocking Phase 1 → sequential Phase 2 → ordered emission) and proposed streaming Phase 1 with overlapped card generation
- "what was that program starting with a p" → Playwright

Every instruction required inferring the technical intent from non-technical language, then mapping it to the correct code location in a 14,000+-line codebase.

---

## 7. Tool Use Agent — Opus as Decision-Maker, Not Just Text Generator

**The benchmark:** BigLaw Bench 90.2% + native parallel tool use + extended thinking.

**What happened in FlipSide:** The "Ask FlipSide" follow-up feature gives Opus three tools:

| Tool | What it does |
|---|---|
| `search_document(query)` | Full-text search through the uploaded document |
| `get_clause_analysis(n)` | Retrieve FlipSide's flip card analysis for clause N |
| `get_verdict_summary()` | Retrieve the overall expert verdict |

When a user asks "What happens if I'm 3 months late on rent?", Opus receives only the question — not the full document. It autonomously searches for "late payment," "termination," and "grace period" (parallel tool calls), retrieves the relevant clause analyses, then synthesizes: "$12,300 total — $6,750 in uncapped late fees on $5,550 in rent." The user sees each tool call live — transparency builds trust.

The strategic choice: the old endpoint sent the entire document to Opus. The new version lets Opus decide what to retrieve. Shorter context, better answers, visible reasoning.

---

## 8. Architecture Rethinks — The Product Decision That Required a System Rethink

**What happened in FlipSide:** The architecture went through three phases: (1) 4 parallel Opus deep dives from t=0, (2) simplified to 1 verdict + on-demand deep dives via `/deepdive/` endpoint, (3) expanded back to 6 parallel threads (verdict + 5 deep dives) when we realized the wall-clock cost of parallel is zero and the UX gain is enormous — everything arrives together.

Each pivot required a full system rethink across both files:

**Phase 1 → 2 (simplify):** Remove `_launch_deep_dives()`, change `OPUS_SOURCES` in 3 event loop functions, add verdict persistence, build a new SSE endpoint for on-demand calls, rewrite frontend buttons from "wait" to "click to start," add the Ask FlipSide tool-use agent.

**Phase 2 → 3 (expand):** Restore parallel threading with 6 Opus calls from t=0, add progress tracking ("3 of 5 reports ready"), coordinate deep dive completion with frontend collapsible panels, keep on-demand `/deepdive/` as fallback.

**Why this matters for 4.6:** Each pivot wasn't "change a function." It was "rethink the architecture while keeping everything else working." Thread timing, event loops, frontend state, SSE protocol — surgical changes across all of it simultaneously, across 14,000+ lines.

---

## What 4.5 Could Have Done

To be fair, Opus 4.5 could have written any individual function in FlipSide. The prompts, the card parsing regex, the CSS animations — none of these require 4.6-level reasoning.

The difference shows up in:
- **Sustained multi-file sessions** where both files (~50K tokens) plus conversation history plus the plan had to be held simultaneously
- **Architecture pivots** that required rethinking the system, not just editing it
- **Thread safety reasoning** across 5 concurrent threads sharing mutable state
- **Self-correction** that caught security issues, dead code, and race conditions
- **Intent inference** from non-technical, typo-filled instructions
- **Visual vocabulary** — reading screenshots and establishing shared element names through conversation

Opus 4.6 didn't write better functions. It built a better system — and rebuilt it 7 times as the design evolved — while maintaining consistency across 14,000+ lines and understanding imprecise intent from three misspelled words and a screenshot.

---

## Sources

- [Claude Opus 4.6 Announcement](https://www.anthropic.com/news/claude-opus-4-6) — Anthropic
- [What's New in Claude 4.6](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6) — Claude API Docs
- [Opus 4.6 vs 4.5 Benchmarks](https://ssntpl.com/blog-claude-opus-4-6-vs-4-5-benchmarks-testing/) — Real-world testing results
- [Opus 4.6: A Step Change for the Enterprise](https://thenewstack.io/anthropics-opus-4-6-is-a-step-change-for-the-enterprise/) — The New Stack
- FlipSide git history: 134 commits, Feb 10–16 2026
---

**Henk van Ess** — [imagewhisperer.org](https://www.imagewhisperer.org) · [searchwhisperer.ai](https://searchwhisperer.ai) · [digitaldigging.org](https://digitaldigging.org)
