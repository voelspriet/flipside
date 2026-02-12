# Hackathon Log: FlipSide

## Built with Opus 4.6 — Claude Code Hackathon, February 2026

> This log documents the complete decision process from hackathon kickoff to product selection. Every methodology, failure, and pivot is documented in the [docs/](https://github.com/voelspriet/flipside/tree/main/docs) folder. This file is the timeline — the docs contain the detail.

---

## The Product

**FlipSide: the dark side of small print.**

Upload a document you didn't write — a contract, Terms of Service, insurance policy, loan agreement, employee handbook. Opus 4.6 adopts the perspective of the party who drafted it and reveals what each clause strategically accomplishes for them.

**Problem Statement:** Break the Barriers — take something locked behind expertise (legal document analysis) and put it in everyone's hands.

---

## Timeline

### Phase 0: Process Setup (before any product decision)

**Entry 1 — Meta-Prompting**
Instead of asking Claude to build a documentation agent, we asked it to *design the prompt for itself first*. This established the workflow for the entire hackathon: generate the prompt → review it → clean it → execute it.
→ [docs/META_PROMPTING.md](https://github.com/voelspriet/flipside/tree/main/docs/META_PROMPTING.md)

**Entry 2 — Jury Research**
Researched all 5 judges before choosing a project. Caught a critical factual error: Claude's training data incorrectly linked judge Thariq Shihipar to Upsolve (a nonprofit). Live web research proved this was wrong — Thariq is a serial entrepreneur (One More Multiverse, $17M raised). This correction changed the entire strategic direction.
→ [docs/JURY_RESEARCH_LIVE.md](https://github.com/voelspriet/flipside/tree/main/docs/JURY_RESEARCH_LIVE.md)

**Entry 3 — Omission Test**
Deliberately withheld the judging criteria to test whether Opus 4.6 would identify it as a missing variable. It did, unprompted. This validated that the model reasons about problem structure, not just surface inputs.

**Entry 4 — Criteria Analysis**
Full hackathon brief analyzed: Demo 30%, Opus 4.6 Use 25%, Impact 25%, Depth 20%. Two special prizes identified as targets: "Most Creative Opus 4.6 Exploration" and "The Keep Thinking Prize."
→ [docs/HACKATHON_BRIEF.md](https://github.com/voelspriet/flipside/tree/main/docs/HACKATHON_BRIEF.md) | [docs/CRITERIA_ANALYSIS.md](https://github.com/voelspriet/flipside/tree/main/docs/CRITERIA_ANALYSIS.md)

---

### Phase 1: Methodology Discovery

**Entry 5 — The Prewash Method**
Claude wrote a research prompt containing adjective bias ("brutally honest," "is it forced?"). The human caught it before execution. This led to documenting The Prewash Method — a two-cycle technique for cleaning AI prompts:
- Cycle 1: Remove adjective bias
- Cycle 2: Replace vague language with measurable criteria
→ [docs/PREWASH_METHOD.md](https://github.com/voelspriet/flipside/tree/main/docs/PREWASH_METHOD.md)

**Entry 6 — Live Demonstration**
The human gave Claude a deliberately vague input. Claude interpreted it confidently through its own vocabulary. The human then revealed the actual structured prompt — proving that "Think Like a Document" applies to AI reasoning itself. Documented verbatim.
→ [docs/LIVE_DEMONSTRATION.md](https://github.com/voelspriet/flipside/tree/main/docs/LIVE_DEMONSTRATION.md)

**Entry 7 — Prewash Prompt Collection**
Seven real before/after prompt examples collected as an educational resource. Shows what Cycle 1 removes and what Cycle 2 fixes in each case.
→ [docs/PREWASH_PROMPT_COLLECTION.md](https://github.com/voelspriet/flipside/tree/main/docs/PREWASH_PROMPT_COLLECTION.md)

---

### Phase 2: Product Selection (and Three AI Failures)

**Entry 8 — Initial Decision Matrix**
Four ideas evaluated against three inputs (strengths × jury × criteria). An initial winner was selected based on a proprietary dataset advantage.
→ [docs/DECISION_MATRIX.md](https://github.com/voelspriet/flipside/tree/main/docs/DECISION_MATRIX.md)

**Entry 9 — FAILURE: Anchoring Bias**
The human had flagged an existing competitor that already solved the same problem. Despite this, Claude scored the initial winner's uniqueness at 10/10 across three subsequent documents. The competitor evidence was acknowledged but never integrated into the scoring. Recommendation invalidated.
→ [docs/ANCHORING_FAILURE.md](https://github.com/voelspriet/flipside/tree/main/docs/ANCHORING_FAILURE.md)

**Entry 10 — New Concepts via "Think Like a Document"**
Five new tool concepts generated using a Prewash-compliant prompt with 5 constraints and 5 required outputs. The principle was used as a generative design constraint, not just a search technique.
→ [docs/TOOL_CONCEPTS.md](https://github.com/voelspriet/flipside/tree/main/docs/TOOL_CONCEPTS.md)

**Entry 11 — Matrix Comparison**
Earlier decision matrix retested against new concepts using identical scoring. The initial winner still led on two dimensions but no longer won on every dimension. ContractLens emerged as the strongest concept.
→ [docs/MATRIX_COMPARISON.md](https://github.com/voelspriet/flipside/tree/main/docs/MATRIX_COMPARISON.md)

**Entry 12 — Expanded Reach**
Each concept modified for broader user base. ContractLens expanded from "contracts" to "any one-sided document" (ToS, insurance, loans, HOA rules), growing from ~50M to ~250M+ potential users with zero added complexity. ContractLens ranked #1.
→ [docs/EXPANDED_REACH.md](https://github.com/voelspriet/flipside/tree/main/docs/EXPANDED_REACH.md)

**Entry 13 — Problem Deep Dive**
10 real problems identified. Three lenses applied (most users, most financial damage, least served). The Policyholder's Exclusion Maze appeared in all three lists: ~30M users/year, $10K–$50K per denied claim, zero existing tools.
→ [docs/CONTRACTLENS_PROBLEMS.md](https://github.com/voelspriet/flipside/tree/main/docs/CONTRACTLENS_PROBLEMS.md)

**Entry 14 — FAILURE: Framing Bias**
The human asked about a document comparison feature. Claude narrowed it to "compare two insurance policies" because it was anchored on ContractLens. The human's actual intent was broader: any two documents, three comparison types (contradictions, divergent conclusions, gaps). Third documented instance of AI interpreting through its most recent frame.
→ [docs/FRAMING_BIAS_FAILURE.md](https://github.com/voelspriet/flipside/tree/main/docs/FRAMING_BIAS_FAILURE.md)

**Entry 15 — Document Comparison Concept**
The broader comparison concept defined with three precise comparison types, five document pairings, and a concrete walkthrough (pharma press release vs. FDA response letter).
→ [docs/DOCUMENT_COMPARISON_CONCEPT.md](https://github.com/voelspriet/flipside/tree/main/docs/DOCUMENT_COMPARISON_CONCEPT.md)

**Entry 16 — Product Unity Analysis**
Tested whether ContractLens and document comparison could be one product. Answer: no — a single sentence cannot describe both to both audiences. Recommendation: build ContractLens only. The comparison tool's 2M users are 0.8% of ContractLens's 250M+.
→ [docs/PRODUCT_UNITY_ANALYSIS.md](https://github.com/voelspriet/flipside/tree/main/docs/PRODUCT_UNITY_ANALYSIS.md)

**Entry 17 — FlipSide**
Product named. Tagline chosen: *"FlipSide: the dark side of small print."*

---

### Phase 3: Building the Product

**Entry 18 — First Working Prototype**
Flask backend + single HTML frontend. Core loop: upload document → Opus 4.6 extended thinking with SSE streaming → phased analysis output. PDF, DOCX, and paste-text extraction. Role selector (tenant, freelancer, policyholder, employee, etc.) and negotiability toggle. Sample homeowner's insurance policy embedded for instant demo. Later expanded to 9 sample documents (lease, insurance, ToS, employment, loan, gym, medical, HOA, coupon) — all authored by Claude with clauses engineered to demonstrate each of the 18 trick categories. The samples are the product's demo reel: every trick type is represented across the collection.

**Entry 19 — The Meta-Prompting Framework**
System prompt redesigned to teach the model *how to think*, not just what to output. "Every clause exists for a reason — if it seems neutral, investigate what it enables." "The boring parts are the dangerous parts." This is the productized version of the two-step meta-prompting discovery from Entry 1 — the system prompt IS the pre-built reasoning framework, every document upload is the "execute" step.

**Entry 20 — Trick Taxonomy**
18 legal trick categories defined: Silent Waiver, Burden Shift, Time Trap, Escape Hatch, Moving Target, Forced Arena, Phantom Protection, Cascade Clause, Sole Discretion, Liability Cap, Reverse Shield, Auto-Lock, Content Grab, Data Drain, Penalty Disguise, Gag Clause, Scope Creep, Ghost Standard. Each clause is classified with one. This constrained vocabulary dramatically improved output consistency — the model no longer invents ad hoc categories.

**Entry 21 — "What the Small Print Says" vs. "What You Should Read"**
Replaced generic clause summaries with a forced juxtaposition: "What the small print says" (neutral restatement as a drafter would present it) vs. "What you should read" (what this actually means for you). The gap between the two IS the product's core insight. Every clause now makes the asymmetry visceral.

**Entry 22 — The Drafter's Playbook**
New analysis section: instead of just flagging individual clauses, reveal the *strategic architecture* of the entire document. "If I were the attorney who designed this, my strategic approach was: (1) Grant broad coverage upfront to suppress scrutiny... (2) Build layered exclusions that interact to deny claims..." This is the cross-clause reasoning that requires Opus 4.6's extended thinking — no other model holds the full document in context while reconstructing the drafter's strategy.

**Entry 23 — Auto-Detection**
Removed manual role selection and negotiability toggle from the required UI flow. The model now auto-detects from the document itself: who is the non-drafting party? Is this negotiable or take-it-or-leave-it? For negotiable documents: suggested revisions with Before/After quotes. For non-negotiable: "What to Watch For" with concrete scenarios.

**Entry 24 — Parallel Processing Architecture**
Single API call split into two parallel threads: a quick clause scan (fast, streams immediately) and a deep cross-clause analysis (full thinking budget, streams after quick scan completes). Uses `threading.Thread` + `queue.Queue` to interleave. The user sees clauses appearing within seconds while cross-clause reasoning runs in the background. This solved the "staring at a loading screen for 2 minutes" problem.

**Entry 25 — Depth Presets**
Three analysis modes: Quick (8K thinking budget, ~30s), Standard (16K, ~90s), Deep (32K, ~3min). Each adjusts both thinking budget and max output tokens. Deep mode enables the multi-pass cross-clause reasoning that finds the compound risks.

**Entry 26 — Document Comparison Mode**
Second major feature: upload two documents and compare them side by side. Identifies what's present in one but missing from the other, scores each area, and recommends the better deal. Originally rejected as a separate product (Entry 16), now integrated as a secondary mode within FlipSide. Same principle: think like the documents, not like the reader.

**Entry 27 — Multilingual Support**
Language rule added to all prompts: respond in the same language as the document. If the document is in Dutch, the entire analysis is in Dutch. No language selector needed — auto-detected from the document text. This opened FlipSide to non-English contracts with zero additional code.

**Entry 28 — Model ID and Thinking API Fix**
First user test revealed `claude-opus-4-6-20250219` (dated model ID) returned 404. Fixed to alias `claude-opus-4-6`. Also discovered `thinking.type: 'enabled'` is deprecated for Opus 4.6 — switched to `thinking.type: 'adaptive'`, which lets the model decide when and how deeply to think based on prompt complexity.

**Entry 29 — The Meta-Prompting Discovery (Cat Wu AMA)**
During the hackathon AMA, asked Cat Wu (Product Lead, Claude Code co-creator) about meta-prompting: why does "generate a prompt for X" then "execute it" consistently outperform directly asking "do X"? Cat confirmed the effect is real but the exact mechanism isn't fully understood. The observation: the two-step approach forces the model to separate planning from execution — it reasons about what makes a good analysis before actually analyzing. FlipSide's entire architecture is a productized version of this discovery.

---

### Phase 4: Self-Examination

**Entry 30 — FAILURE: Build Phase Documentation Gap**
We ran our own analysis prompt against this hackathon log. It found three failure modes:
1. The frontend (4,008 lines) had zero log entries — no documented examination against the project's own principles
2. Build-phase entries (18–27) document only outcomes, not iterations or failed attempts — unlike Phase 1–2, which documented failures explicitly
3. Entry 16 concluded comparison should be a separate product; Entry 26 integrated it into FlipSide without documenting what changed

This is the same pattern as the three AI failures (Entries 6, 9, 14): we applied rigorous methodology to the planning phase but not to the build phase. The Prewash Method was used on prompts but not on the UI text. "Acknowledgment is not integration" (Lesson 9) applied to us, not just the AI.

**Entry 31 — Why Comparison Mode Returned (Resolving Entry 16 → 26)**
Entry 16 rejected comparison as a separate product because: "a single sentence cannot describe both to both audiences." Entry 26 integrated it as a secondary mode. What changed: comparison was added not as a separate product but as a feature *within* FlipSide's existing interface — same upload flow, same analysis engine, same "think like the document" principle. The one-sentence test still passes: "FlipSide shows you what the other side intended when they wrote your document." Comparison is a second way to use the same perspective flip. The Entry 16 conclusion ("don't build two products") held — comparison became a feature, not a product.

**Entry 32 — Frontend Audit Against Project Principles**
Applied the Prewash Method and project principles to the frontend for the first time. Findings:
- **Prewash violation**: Tooltip text used adjectives and value judgments — "Severely one-sided," "Significantly unfair," "Standard or fair." These are the same kind of bias the Prewash Method catches in prompts. Fixed: replaced with factual, score-based descriptions.
- **Accessibility gaps**: Icon-only buttons (dark mode, font size, print, export) had no aria-labels. Form inputs (search, threshold slider) lacked proper labels. Risk indication used color alone. Fixed: added aria-labels, form labels, and text alongside color.
- **Streaming bug**: If the backend skipped the `text_start` event, results panel never appeared — user saw a blank screen. The `thinking_start` handler didn't work after the quick scan phase completed. Fixed both.
- **Marketing language in risk filter labels**: "Ok" / "Watch" / "Risk" replaced with score ranges.
The frontend was built without the same scrutiny applied to the prompts and decision process. This entry corrects that.

**Entry 33 — FAILURE: Prompting About Prompting Has the Same Bias**
Asked Claude to write a prompt analyzing our vibecoding process. The prompt contained adjective bias ("experienced practitioners," "what this builder does differently"), unverified claims ("most vibecoding starts with code in the first 5 minutes"), leading questions ("what does THIS builder treat as the product?"), and unmeasurable instructions ("analyze," "do not flatter"). The human caught it and demanded a Prewash-compliant rewrite. This is the fourth documented AI failure — and the first one caught during the self-examination phase. Same pattern: the AI uses framing language that looks neutral but carries embedded assumptions.

---

### Phase 5: The Card-First Redesign

**Entry 34 — Split-Model Architecture (Haiku + Opus)**
Rewrote the analysis pipeline to use two models in parallel: Haiku 4.5 for fast individual clause cards (no thinking, ~5s for first card) and Opus 4.6 with extended thinking for cross-clause deep analysis (~80s). Previously both phases used Opus, creating a 30-60 second wait before any content appeared. Now the user sees their first flip card in 5 seconds while Opus reasons in the background. Added `FAST_MODEL` config and modified `worker()` to conditionally include thinking parameters.

**Entry 35 — Incremental Flip Cards (Streaming Parser)**
Cards now appear one at a time during Haiku's SSE stream, not as a batch after completion. `tryExtractNewClauses()` splits `responseContent` by `---` separators during streaming, parsing each complete segment into a flip card immediately. The card viewport shows one card at a time with prev/next navigation and keyboard arrows. This replaced the old `transformToFlipCards()` batch approach.

**Entry 36 — FAILURE: LLM Output Format Mismatch**
After switching to Haiku for card scan, ALL flip cards silently failed to parse. No errors — just empty results. Root cause: Haiku outputs `Score: 88` while Opus outputs `Score: 88/100`. The `/100` suffix is model-dependent. The regex `Score:\s*(\d+)\/100` matched Opus but never Haiku. Fixed by making the suffix optional: `(\d+)(?:\/100)?`. Same principle applied to `---` separators (Haiku uses `\n\n---\n\n`, parser expected `\n---\n`; fixed with `/\n+---\n+/`) and field separators (accept `·`, `•`, `-`, `–`, `—`, `|`, `,`). **Lesson: Postel's Law for LLM parsing — be strict in what you prompt, liberal in what you parse.**

**Entry 37 — Progressive Disclosure (On-Demand Deep Analysis)**
User repeatedly reported seeing deep analysis results immediately, spoiling the card-by-card reveal. Root cause: `doRenderResults()` was called on every SSE text chunk, rendering Opus output into the DOM even though the parent container was hidden (CSS `hidden` class doesn't prevent DOM writes). Fix: `doRenderResults()` returns early when `flipCardsBuilt && !isCompareMode`. Deep analysis is buffered in `responseContent` during streaming, rendered only when user explicitly clicks "Scrutinize this even more" or "View scrutiny →". The flip card IS the product — suspense of "is there another side?" must not be spoiled.

**Entry 38 — The Verdict Button Circular Dependency**
The "Scrutinize" button on each flip card polls for deep analysis readiness by checking `deepAnalysisEl.innerHTML.trim()`. But deep analysis content is never written to `deepAnalysisEl` during streaming — it's only rendered when `revealDeepAnalysis()` is called, which IS the action the button triggers. Circular dependency: poll waits for DOM content → DOM content only appears after the action the poll is waiting to trigger. Fix: poll checks data availability (`isDoneRendering` or `responseContent.length > quickDoneContentLength + 100`) instead of DOM state.

**Entry 39 — Deep Analysis Must Add, Not Repeat**
User testing revealed the deep analysis repeated the same labels as flip cards ("What the small print says" / "What you should read"), making it feel redundant. Changed deep analysis to use distinct labels: "Read separately, you'd see" / "Read together, you'd realize" — emphasizing cross-clause interactions. Drafter voice reframed from raw `[DRAFTER]:` to "If the drafter could speak freely" with visual framing. Removed numeric scores from flip cards entirely (user: "combined risk is too complicated, people don't understand") — cards show only color badge + trick name.

**Entry 40 — Automated UX Flow Test**
Created `test_ux_flow.py` — a Python script that simulates a user session via HTTP: hits `/sample`, streams `/analyze/<id>`, and parses SSE events in real-time using the same regex logic as the frontend. Reports: time to first card, number of cards parsed, whether verdict polling would succeed, deep analysis data availability, and timing per phase. This catches LLM output format mismatches (Entry 36) server-side before they become silent frontend failures.

---

### Phase 6: 10 Opus 4.6 Capabilities Sprint

**Entry 41 — Opus Capabilities Audit**
Ran a structured audit (`prompts/opus_capabilities_audit.md`) identifying 10 Opus 4.6 capabilities FlipSide didn't use yet. Ranked by (Demo Impact × Feasibility). 10 parallel evaluation agents assessed each capability against the codebase. All 10 were implemented in a single session.

**Entry 42 — Vision / Multimodal PDF Analysis**
PDF pages are now rendered as PNG images (pdfplumber, 150 DPI, max 10 pages) and sent alongside extracted text to Opus 4.6's deep analysis. The prompt instructs Opus to detect visual formatting tricks: fine print, buried placement, table structures that obscure comparisons, visual hierarchy manipulation. Images are only sent to the Opus deep thread, not Haiku (cost optimization).

**Entry 43 — Tool Use (Structured Risk Assessment)**
Two tool schemas defined: `assess_risk` (clause-level: risk level, confidence, score, trick type, mechanism) and `flag_interaction` (cross-clause: clauses involved, interaction type, severity, explanation). Opus calls these tools during deep analysis, producing structured data alongside its prose output. Frontend handles `tool_start` and `tool_result` SSE events. This forces precision — when Opus commits to a tool call, it must provide exact values, not hedged prose.

**Entry 44 — Multi-Turn Follow-Up Questions**
New `/ask/<doc_id>` endpoint. After analysis, users see "Ask about this document" with a text input. Questions are sent as POST with SSE streaming response. Opus receives the full document text plus the question, using adaptive thinking and prompt caching. Documents are retained after analysis (changed from `pop()` to marking as analyzed). UX: immediate input clearing, "Thinking..." button state, streaming answer display.

**Entry 45 — Confidence Signaling**
Each flip card now shows a confidence badge: HIGH (green), MEDIUM (amber), LOW (red). Hover reveals the reasoning (e.g., "language is unambiguous" or "two interpretations possible"). Added to `build_card_scan_prompt()` output format and parsed via regex in `extractSingleClause()`. This increases trust — transparent uncertainty is more impressive than false confidence.

**Entry 46 — Self-Correction (Quality Check)**
Added "Quality Check" section to deep analysis prompt. Opus reviews its own analysis for: false positives (clauses flagged that are actually standard), blind spots (risks it may have missed), consistency (whether confidence levels match the evidence), and adjusted confidence. This catches the "false positive on fair documents" problem without requiring a second API call.

**Entry 47 — Benchmark Comparison (Fair Standard)**
Added "Fair Standard Comparison" section to deep analysis. Opus compares the worst clauses against what a fair, balanced version of the same document type would contain. Uses its knowledge of industry practices and legal norms. Output format: "This document says / A fair version would say / Why the gap matters."

**Entry 48 — Visible Thinking**
Changed thinking panel from hidden/collapsed to a visible status line during Opus reasoning. Shows "Opus 4.6: Deep reasoning..." with a pulsing indicator. On completion: "Opus 4.6: Reasoning complete" with "Show the full report" button that calls `revealDeepAnalysis()`. The thinking tokens contain Opus's actual reasoning — visible on demand, not forced.

**Entry 49 — Methodology Disclosure**
Added "How Opus 4.6 Analyzed This Document" section to deep analysis prompt. Opus explains which analysis techniques it used, why extended thinking was necessary for this document, and what the adaptive thinking budget was spent on. Makes the AI methodology transparent to the user.

**Entry 50 — Prompt Caching**
Both API call sites (single-stream and parallel worker) now use `cache_control: {type: 'ephemeral'}` on system prompt content blocks. FlipSide's system prompts are ~2000 tokens — caching reduces cost by ~90% on cache hits and reduces latency for repeated analyses. Invisible to users but critical for production viability.

**Entry 51 — Reverse Proxy Path Fix**
Deployed to a server behind a URL prefix (`/flipside/`). All 5 JavaScript fetch/EventSource calls used absolute paths (`/sample`, `/upload`, `/compare`, `/analyze/`, `/ask/`) causing 404s. Fixed with `BASE_URL = {{ request.script_root | tojson }}` injected by Flask's Jinja2 template engine, prepended to all API paths.

---

### Phase 7: Long Documents, Progress & Security

**Entry 52 — Full Document Text (No Truncation)**
Removed the 15,000-character truncation from all three endpoints (upload, sample, compare). The sidebar now receives the complete document text. This was the root cause of clause markers failing to appear for clauses beyond ~page 4 — the fuzzy matching was correct, but the text it searched was cut off. Modern browsers handle 200KB in a scrollable div without issue.

**Entry 53 — Dynamic Haiku Token Budget**
Haiku's hardcoded 8,000-token output limit was insufficient for long documents (50+ pages, 80+ clauses). Replaced with `max(8000, min(16000, len(text) // 5))` — short docs stay at 8K, long docs scale up to 16K. Haiku cost is negligible; the extra tokens enable ~100 cards instead of ~50.

**Entry 54 — Page Navigation Tabs (Finding-Only)**
Initial implementation showed a tab for every page (53 circles for a 53-page document — overwhelming). Redesigned: tabs start hidden and appear progressively as Haiku finds clauses on each page. A 53-page document with findings on 8 pages shows 8 tabs, not 53. Click handlers use `data-page-idx` attributes to find current DOM markers (avoiding stale closure references after `rebuildPreviewHighlights()` replaces innerHTML).

**Entry 55 — Live Clause Counter + Deep Status Indicator**
Two progress signals added: (1) "5 clauses found so far..." updates the status bar and sidebar each time a new card appears during scanning. (2) After cards complete (`quick_done`), a persistent pulsing status line shows "Opus 4.6 is building your Full Verdict..." below the card navigation. Disappears when the verdict is ready. Both give users concrete feedback instead of generic rotating messages.

**Entry 56 — Document Suitability Gate**
Added rule 13 to `build_card_scan_prompt()`: if the document has no terms/conditions/obligations (recipe, novel, academic paper), Haiku outputs `**Not Applicable**: [reason]` and skips clauses. Frontend detects this in `extractMetadata()` and shows "Not a match for FlipSide" with the explanation. Two distinct zero-card paths: unsuitable doc (wrong type) vs. clean doc (nothing concerning). Flip prompt changes to "Not everything is a contract in life."

**Entry 57 — XSS Defense with DOMPurify**
Security audit revealed that deep analysis, compare mode, and follow-up answers passed LLM output through `marked.parse()` → `innerHTML` without sanitization. A crafted document could trick the LLM into outputting malicious HTML. Added DOMPurify CDN + `safeMd2Html()` wrapper applied to all 4 `marked.parse()` call sites. Flip cards were already safe (all fields go through `escapeHtml()`).

---

### Current State

| Artifact | Lines | Status |
|----------|-------|--------|
| `app.py` | 1,815 | Backend: Flask, SSE, parallel Haiku+Opus, vision, tool use, follow-up, prompt caching, 7 prompts, dynamic token budget, suitability gate |
| `templates/index.html` | 4,469 | Card-first frontend: flip cards, confidence badges, follow-up UI, tool handlers, prefix-aware paths, page nav tabs, live counters, DOMPurify |
| `decision_monitor.py` | 352 | Hackathon strategy tracker: reads git/strategy/log files |
| `test_ux_flow.py` | 230 | Automated UX flow test: simulates user session, validates parsing |
| `maintain_docs.py` | 230 | Doc maintenance agent: detects stale info in .md files |
| `prompts/` | 3 files | Opus capabilities audit, gap analysis, feasibility study |
| `docs/` | 18 documents | Methodology, decisions, failures, corrections |
| `HACKATHON_LOG.md` | This file | 57 entries, complete process timeline |
| `README.md` | Product description + 13 Opus capabilities + meta-prompting discovery |

---

## Five Documented AI Failures

Each failure was caught by the human, not by Opus 4.6. Each demonstrates a different bias pattern:

| # | Failure | Phase | Pattern | The AI did | The human did |
|---|---------|-------|---------|-----------|--------------|
| 1 | [Live Demonstration](https://github.com/voelspriet/flipside/tree/main/docs/LIVE_DEMONSTRATION.md) | Planning | Training vocabulary bias | Projected its own framework onto a vague input | Revealed the structured version |
| 2 | [Anchoring Failure](https://github.com/voelspriet/flipside/tree/main/docs/ANCHORING_FAILURE.md) | Planning | Confirmation bias across documents | Maintained a conclusion despite contradicting evidence | Scrolled back and demanded accountability |
| 3 | [Framing Bias](https://github.com/voelspriet/flipside/tree/main/docs/FRAMING_BIAS_FAILURE.md) | Planning | Recency/context anchoring | Interpreted a new concept through its most recent topic | Showed the neutral version |
| 4 | Meta-analysis prompt (Entry 33) | Self-examination | Adjective/framing bias | Wrote a prompt with "experienced," "differently," unverified claims, leading questions | Demanded Prewash-compliant rewrite |
| 5 | LLM output format assumption (Entry 36) | Build | Format rigidity bias | Wrote a regex assuming all models produce identical output format | Debugged via console.log, found Haiku drops `/100` |

The first four are the same error at different scales: **the AI uses itself as the measurement of things, rather than observing what must be there.** The fifth is a variation: **the AI assumes consistency across models without testing.** Both solved by the same principle: observe what IS there, not what should be there.

---

## Lessons Learned

1. **Meta-prompting is worth the time.** Asking the AI to show its plan before executing adds 2 minutes and eliminates entire categories of misalignment.

2. **Process documentation can be a product.** What started as internal scaffolding became a publishable case study.

3. **Treat the jury as a design constraint.** Research evaluators the same way you research users — before you build.

4. **Always verify AI training data with live research.** The Thariq/Upsolve error would have misdirected the entire strategy.

5. **AI prompts carry invisible bias.** Every adjective is a policy decision. The Prewash Method catches them before they compound.
→ [docs/PREWASH_METHOD.md](https://github.com/voelspriet/flipside/tree/main/docs/PREWASH_METHOD.md)

6. **Removing bias is not enough — add precision.** "How well?" is unbiased but unmeasurable. "Rate 1-5" is both.

7. **AI confidence is not alignment.** "I understand" tells you nothing about whether it understood correctly.

8. **Re-examine conclusions when new evidence arrives.** The decision matrix was retested against new concepts. It held — partially.

9. **Acknowledgment is not integration.** When AI says "good point," verify that it actually changed the analysis, not just the conversation.

10. **Confirmation bias compounds across documents.** A biased conclusion in Document 1 becomes an invisible assumption in Document 3.

---

## What Exists

| Artifact | Purpose |
|----------|---------|
| `app.py` (1,815 lines) | Flask backend: 7 prompts, Haiku+Opus parallel, vision, tool use, follow-up, prompt caching, SSE streaming, suitability gate |
| `templates/index.html` (4,469 lines) | Card-first frontend: flip cards, confidence badges, follow-up UI, tool handlers, prefix-aware paths, page nav, DOMPurify |
| `decision_monitor.py` (352 lines) | Hackathon strategy tracker |
| `test_ux_flow.py` (230 lines) | Automated UX flow test |
| `maintain_docs.py` (230 lines) | Doc maintenance agent |
| `prompts/` (3 files) | Opus capabilities audit, gap analysis, feasibility study |
| [docs/](https://github.com/voelspriet/flipside/tree/main/docs) | 18 methodology and decision documents |
| [BUILDER_PROFILE.md](https://github.com/voelspriet/flipside/blob/main/BUILDER_PROFILE.md) | Who built this and what they bring |
| This file | 51 entries, complete process timeline |

## 13 Opus 4.6 Capabilities Used

| # | Capability | Visible in product |
|---|-----------|-------------------|
| 1 | Extended thinking (adaptive) | Reasoning panel, cross-clause analysis |
| 2 | Perspective adoption | Drafter's attorney voice on flip card backs |
| 3 | Vision / multimodal | PDF page images → visual formatting tricks detected |
| 4 | Tool use | `assess_risk` + `flag_interaction` structured tool calls |
| 5 | Multi-turn follow-up | "Ask about this document" after analysis |
| 6 | Confidence signaling | HIGH/MEDIUM/LOW badges on each flip card |
| 7 | Self-correction | Quality Check section reviews its own analysis |
| 8 | Benchmark comparison | Fair Standard Comparison against industry norms |
| 9 | Split-model parallel | Haiku 4.5 (fast cards) + Opus 4.6 (deep analysis) |
| 10 | Prompt caching | System prompts cached for 90% cost reduction |
| 11 | Long-context retrieval | Cross-clause interaction detection across full documents (no truncation) |
| 12 | Low over-refusals | Villain voice sustains adversarial role-play without self-censoring |
| 13 | Multilingual + bilingual | Analyzes in document's language, EN translations on cards |

## What Remains

- Demo video
- 100-200 word summary
- Testing with document types beyond leases (insurance, ToS, employment)

**Deadline: February 16, 3:00 PM EST**

---

<sub>Maintained during the Claude Code Hackathon 2026. Every entry links to a detailed document in the docs/ folder.</sub>
