# How Opus 4.6 Built FlipSide

**0% of the code was written by a human. 14,000+ lines in 6 days, built entirely through conversation. Here's what Opus 4.6 did that no other model could.**

| Metric | Value |
| --- | --- |
| Lines written by a human | 0 |
| Total commits | 111 |
| Total insertions | 46,062 lines |
| Total deletions | 18,571 lines |
| Net codebase | 14,000+ lines (3,469 backend + 10,594 frontend) |
| Development period | 6 days (Feb 10–16, 2026) |
| Average velocity | ~5,700 lines/day |
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

**Same method, different screen — the investigation/loading state:**

| What you see | What Claude calls it |
|---|---|
| "CloudVault Terms of Service (Sample)" (title) | `#docTitleHero` / `#docTitleText` |
| White scrollable document preview | `#editorialLoading` / `.editorial-loading` |
| Document text inside preview | `#editorialLoadingText` / `.editorial-loading-text` |
| Magnifying glass scanning animation | `.investigation-loupe` (positioned by JS) |
| "... Reading the fine print" (animated dots + status) | `.editorial-loading-indicator` → `.pulsing-dots` + `#editorialLoadingStatus` |
| Rust-bordered narration ("Looking at how either side can walk away") | `#briefingSentence` / `.briefing-sentence` inside `#expertBriefing` |
| Two-track progress area | `.briefing-tracks` |
| "Clause readers" card with red dot | `.briefing-track` → `#trackReaders` (dot) + `.track-label` + `#trackReadersDetail` |
| "Expert verdict" card with red dot | `.briefing-track` → `#trackExpert` (dot) + `.track-label` + `#trackExpertDetail` |
| "2 angles considered" | `#briefingDepth` / `.briefing-depth` (computed: `tokenCount / 90`) |

The narration line is dynamic — `THINKING_TRANSLATIONS` pattern-matches Opus thinking tokens (e.g., `/terminat/i` → "Looking at how either side can walk away") and translates model reasoning into plain language in real time.

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

**What happened in FlipSide:** The entire frontend is a single 10,594-line HTML file containing CSS, HTML, and JavaScript inline. The backend is a single 3,469-line Python file containing Flask routes, 9+ prompt templates, SSE streaming, and parallel thread management. Every change requires understanding both files simultaneously.

**Grounded example:** Commit `0cc0c33` (stream-first pipeline) changed 962 lines across both files. The backend restructuring (new `_card_pipeline()`, `_run_parallel_streaming()`, streaming prescan) required matching SSE event types (`card_ready`, `cards_started`, `cards_instant`) with frontend handlers (`tryExtractNewClauses()`, `transitionToCardView()`, auto-reveal timer). A single mismatched event name or data format would silently break the pipeline. Opus 4.6 held the full 14,000+ lines in working memory and kept the cross-file contract consistent.

**Why 4.5 would struggle:** Opus 4.5 had a 200K token context window. With both files (~50K tokens) plus conversation history plus the plan, you'd routinely hit context limits during multi-file edits. Opus 4.6's 1M token window (beta) means the entire codebase fits comfortably.

---

## 3. Multi-Step Agentic Reasoning

**The benchmark:** Terminal-Bench 2.0 highest score (long-horizon agentic coding). "Plans more carefully, sustains agentic tasks for longer."

**What happened in FlipSide:** The streaming pipeline change (commits `0cc0c33` + this session) required reasoning about 5 interacting threads:

1. Upload thread → runs `_prescan_document()` with streaming Phase 1
2. N card worker threads → each generates one flip card via Haiku API
3. Pipeline forwarder thread → reads from `_card_queue`, pushes to SSE queue
4. Opus verdict thread → runs from t=0, pushes thinking/text events
5. SSE generator → yields events to the browser, handles ordering

The change involved: switching Phase 1 from a blocking API call to streaming, starting card workers during the stream as each `CLAUSE:` line arrives, forwarding individual card completions via a `Queue` bridge, removing ordered emission so the fastest card appears first, and adding a 10-second auto-reveal timer on the frontend. Each decision depended on understanding the timing relationships between all 5 threads.

**Grounded example:** The `_card_queue` design required reasoning about a race condition: the pipeline thread reads `doc['_card_total']` to know how many cards to expect, but `_card_total` is set after Phase 1 streaming finishes. If the pipeline reads it too early, it gets 0 and skips the queue. The solution: the pipeline waits for `_prescan_event` (set after Phase 1 completes and `_card_total` is stored), guaranteeing the value is correct. This kind of thread-safety reasoning across function boundaries in a 3,500-line file is where agentic planning matters.

---

## 4. Architecture Pivots Without Breaking Things

**The benchmark:** Partner reports: "thinks more deeply and more carefully revisits reasoning before settling on answers."

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

**The benchmark:** "Superior code review and debugging capabilities to identify its own mistakes."

**What happened in FlipSide:** 18 bug fix commits in the git history. Many were caught and fixed within the same session — the model identified the problem, traced it to the root cause, and fixed it without being told what was wrong.

**Grounded examples:**

- Commit `0f2f8d9` ("Harden security, fix bugs, remove ~460 lines dead code"): Opus identified that exception messages were being sent directly to the client (security risk), that PDF page image errors could misalign indices, and that ~460 lines of dead code from old architectures were still in the file. It removed the dead code, sanitized error messages, and added per-source render timers — all in one pass.

- Commit `2450d48` ("Fix 5 code review issues"): After a code review, Opus found and fixed a playbook rendering bug, keyboard event capture leaking to other components, CDN resources loaded without integrity hashes (SRI), an LLM proxy that could be exploited, and a timer memory leak. Five unrelated issues across two files, found through self-review.

- The `_precards_ev.wait(timeout=25)` bottleneck: During this session, when asked "it still takes 30 seconds before first card," Opus traced the problem through 5 thread interactions to identify the exact line causing head-of-line blocking — a `.wait()` call in a pipeline thread that was designed to be non-blocking but was actually blocking on the upload thread's batch completion.

---

## 6. Understanding Intent from Imprecise Input

**The benchmark:** GDPval-AA +144 Elo over GPT-5.2 (economically valuable knowledge work).

**What happened in FlipSide:** The user gives instructions like:

- "never show anlyze complete hre" + screenshot → Found the exact `editorialLoadingStatus` element, traced where "Analysis complete" is set (line 5457), and hid the entire indicator row
- "so why not jump out this screen the moment the first card is ready" → Understood this as an architecture question about pipeline parallelism, not a CSS question about screen transitions
- "it still takes 30 seconds before first card" → Didn't suggest superficial fixes. Traced the actual bottleneck (blocking Phase 1 → sequential Phase 2 → ordered emission) and proposed streaming Phase 1 with overlapped card generation
- "what was that program starting with a p" → Playwright

Every instruction required inferring the technical intent from non-technical language, then mapping it to the correct code location in a 14,000+-line codebase.

---

## 7. Long-Context Retrieval Across Code

**The benchmark:** MRCR v2 8-needle 1M 76% (long-context retrieval), vs Sonnet 4.5's 18.5%.

**What happened in FlipSide:** The streaming pipeline change required connecting code at line 85 (`_prescan_document` Phase 1), line 115 (`card_worker`), line 2409 (`_card_pipeline`), line 2692 (`_run_parallel_streaming`), and line 5868 (`transitionToCardView` in the frontend). These are spread across 8,800 lines of code in two files. The model had to hold all five locations in context simultaneously to ensure the Queue bridge, event types, and completion signals were consistent.

This is the code equivalent of Anthropic's needle-in-a-haystack test: finding and connecting specific code patterns separated by thousands of lines, where a mismatch at any point causes silent failure.

---

## 8. Tool Use Agent — Opus as Decision-Maker, Not Just Text Generator

**The benchmark:** BigLaw Bench 90.2% + native parallel tool use + extended thinking.

**What happened in FlipSide:** The "Ask FlipSide" follow-up feature gives Opus three tools:

| Tool | What it does |
|---|---|
| `search_document(query)` | Full-text search through the uploaded document |
| `get_clause_analysis(n)` | Retrieve FlipSide's flip card analysis for clause N |
| `get_verdict_summary()` | Retrieve the overall expert verdict |

When a user asks "What happens if I'm 3 months late on rent?", Opus doesn't receive the full document — it receives only the question. Then it reasons:

1. "Let me search for 'late payment'" → calls `search_document` → finds clauses 1 and 4
2. "Let me also check 'termination' and 'grace period'" → two more parallel searches
3. "Clause 1 looks relevant. Let me read my prior analysis." → calls `get_clause_analysis(1)`
4. "Clause 4 too." → calls `get_clause_analysis(4)`
5. Synthesizes: "$12,300 total — $6,750 in uncapped late fees on $5,550 in rent. Fees exceed the debt."

The answer includes a formatted table, cross-clause interaction analysis, and actionable negotiation advice — all derived from tool-retrieved evidence, not from the model trying to hold 40 pages in context.

**The strategic choice: tool use vs. context dump.** The old follow-up endpoint sent the entire document plus all analysis to Opus in one prompt. The new version sends just the question and lets Opus decide what to retrieve. Three advantages:

1. **Better answers**: Opus retrieves its own card analyses, which contain risk scores, trick classifications, and dollar figures it calculated during the main analysis. The follow-up answer references this structured data, not raw document text.
2. **Visible reasoning**: The user sees "Searching document for 'late payment'..." → "Reading clause analysis #1..." in real time. Transparency builds trust.
3. **Shorter context = focused output**: Instead of processing 50,000 tokens of document, Opus processes ~5,000 tokens of relevant excerpts. The answer is tighter.

**The parallel tool calls**: Opus called `search_document` three times and `get_clause_analysis` twice — all in two rounds. The Anthropic API supports parallel tool use: the model returns multiple `tool_use` blocks in one response. Opus reasons about ALL the information it needs upfront, not one query at a time. This is the same pattern as a senior attorney who, upon hearing a question, immediately thinks "I need to check the penalty clause, the termination clause, and the cure period" — not "let me check one thing, then think about what else I need."

**Why Opus 4.6:** The quality of tool use depends on three things: (1) knowing which tools to call (requires understanding the question deeply), (2) crafting good search queries (requires understanding legal concepts), and (3) synthesizing results across multiple tool returns into a coherent answer (requires extended reasoning). GPT-4o tends to over-search (calling every tool for every question) or under-search (missing relevant clauses). Opus 4.6 is calibrated — it searches strategically based on the question's legal implications.

---

## 9. On-Demand Architecture — The Product Decision That Required a System Rethink

**What happened in FlipSide:** The original architecture ran 4 parallel Opus deep dives (Scenario, Walkaway, Combinations, Playbook) automatically from t=0 alongside the verdict. Maximum parallelism. But it created UX problems: the verdict finished first, the user started reading, then deep dives completed at different times — scroll jumps, layout shifts, panels appearing while reading.

**The pivot:** Remove all 4 parallel threads. Make each deep dive on-demand — triggered by a single button click. The pipeline simplified from 6 parallel Opus threads to 1 (verdict only), with deep dives running independently via a new `/deepdive/` endpoint.

**What Opus 4.6 had to do:**
1. Remove `_launch_deep_dives()` and the threading coordination from `run_parallel()`
2. Change `OPUS_SOURCES` from `{'overall', 'scenario', 'walkaway', 'combinations', 'playbook'}` to `{'overall'}` in all 3 event loop functions
3. Add verdict text persistence (`doc['_verdict_text']`) for follow-up queries
4. Build a new self-contained SSE endpoint that runs one Opus call per click
5. Rewrite the frontend depth buttons from "wait for completion" to "click to start"
6. Add the Ask FlipSide tool-use agent as a new feature
7. Keep everything else — cards, verdict, streaming, editorial loading — working

This was a simultaneous backend simplification (remove 4 threads + event handlers) and feature addition (new endpoint + tool-use agent + frontend UI), touching both files across hundreds of lines. The model held the full 14,000+-line codebase in context while making coordinated changes to the event loop, thread management, SSE protocol, and frontend state management.

**Why this matters for 4.6:** The pivot wasn't "change a function." It was "rethink the architecture: remove parallelism, add on-demand, add tool use, keep everything else working." That requires understanding the entire system — thread timing, event loops, frontend state, SSE protocol — and making surgical changes across all of it simultaneously. This is Terminal-Bench 65.4% in action: sustained multi-step reasoning across a large codebase under changing requirements.

---

## What 4.5 Could Have Done

To be fair, Opus 4.5 could have written any individual function in FlipSide. The prompts, the card parsing regex, the CSS animations — none of these require 4.6-level reasoning.

The difference shows up in:
- **Sustained multi-file sessions** where context accumulated beyond 200K tokens
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
- FlipSide git history: 111 commits, Feb 10–16 2026
---

**Henk van Ess** — [imagewhisperer.org](https://www.imagewhisperer.org) · [searchwhisperer.ai](https://searchwhisperer.ai) · [digitaldigging.org](https://digitaldigging.org)
