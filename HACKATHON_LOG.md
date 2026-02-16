# Hackathon Log: FlipSide

## Built with Opus 4.6 — Claude Code Hackathon, February 2026

> 78 entries in 5 days. 5 documented AI failures -- all caught by the human. 7 architecture pivots. 222 pages stress-tested with 36/36 planted traps caught. This is the full build story. Key methodologies and failures link to detailed documents in the [docs/](https://github.com/voelspriet/flipside/tree/main/docs) folder.

---

## The Product

**FlipSide: the dark side of small print.**

Upload a document you didn't write — a contract, Terms of Service, insurance policy, loan agreement, employee handbook. Opus 4.6 adopts the perspective of the party who drafted it and reveals what each clause strategically accomplishes for them.

**Problem Statement:** Break the Barriers — take something locked behind expertise (legal document analysis) and put it in everyone's hands.

---

**Highlights for judges:**
- **#9** Anchoring bias failure -- AI scored uniqueness 10/10 across three documents despite known competitor. Human caught it.
- **#36** Postel's Law for LLMs -- Haiku silently broke every parser. The fix: be strict in what you prompt, liberal in what you parse.
- **#58** Opus card backs never rendered -- 3 hours lost to DOM mutation inside GPU-cached 3D transforms. Kill your darlings moment.
- **#74** Frisian language test -- 500K-speaker language, zero degradation, correct Dutch jurisdiction law cited.
- **#76** 222-page cross-clause test -- 36/36 planted traps caught, including interaction between clause 3 and clause 297.
- **#77** Playwright QC pipeline -- 48 findings in 3 rounds of dual-expert review. LLM compliance plateau documented at ~80-90%.

**Five AI failures, one thesis:** Training vocabulary bias (#6), anchoring/confirmation bias (#9), framing/recency bias (#14), adjective bias in meta-analysis (#33), format rigidity across models (#36). The first four are the same error at different scales: the AI uses itself as the measurement of things, rather than observing what must be there. All five caught by the human.

---

## Timeline

### Phase 0: Process Setup (before any product decision)

**Entry 1 — Meta-Prompting**
Instead of asking Claude to build a documentation agent, we asked it to *design the prompt for itself first*. This established the workflow for the entire hackathon: generate the prompt → review it → clean it → execute it.
→ See [meta-prompting-strategy.md](meta-prompting-strategy.md)

**Entry 2 — Jury Research**
Researched all 5 judges before choosing a project. Caught a critical factual error: Claude's training data incorrectly linked judge Thariq Shihipar to Upsolve (a nonprofit). Live web research proved this was wrong — Thariq is a serial entrepreneur (One More Multiverse, $17M raised). This correction changed the entire strategic direction.
→ Jury research conducted via live web search

**Entry 3 — Omission Test: Testing Opus 4.6's Gap Awareness**
A deliberate test. The human explained the two-input decision approach (personal strengths + jury interests) but intentionally withheld the hackathon's official judging criteria. Opus 4.6 independently identified it as a missing variable and presented this table:

| Input | Source | Status |
|-------|--------|--------|
| Your strengths | Other Claude session | Done |
| Jury interests | Research agent | In progress |
| Judging criteria | ? | **Missing** |

The human acknowledged: *"On purpose, I didn't give you this. Wanted to see if 4.6 came up with it."*

This demonstrates that the model reasons about **what it doesn't know** — not just answering questions, but identifying which questions haven't been asked. You don't always test an AI by what you ask — sometimes you test it by what you *don't* say.

**Entry 4 — Criteria Analysis**
Full hackathon brief analyzed: Demo 30%, Opus 4.6 Use 25%, Impact 25%, Depth 20%. Two special prizes identified as targets: "Most Creative Opus 4.6 Exploration" and "The Keep Thinking Prize."
→ Criteria: Demo 30%, Impact 25%, Opus 4.6 Use 25%, Depth 20%

---

### Phase 1: Methodology Discovery

**Entry 5 — The Prewash Method**
Claude wrote a research prompt containing adjective bias ("brutally honest," "is it forced?"). The human caught it before execution. This led to documenting The Prewash Method — a two-cycle technique for cleaning AI prompts:
- Cycle 1: Remove adjective bias
- Cycle 2: Replace vague language with measurable criteria
→ [PREWASH_METHOD.md](PREWASH_METHOD.md)

**Entry 6 — Live Demonstration**
The human gave Claude a deliberately vague input. Claude interpreted it confidently through its own vocabulary. The human then revealed the actual structured prompt — proving that "Think Like a Document" applies to AI reasoning itself. Documented verbatim.
→ [docs/LIVE_DEMONSTRATION.md](https://github.com/voelspriet/flipside/tree/main/docs/LIVE_DEMONSTRATION.md)

**Entry 7 — Prewash Prompt Collection**
Seven real before/after prompt examples collected as an educational resource. Shows what Cycle 1 removes and what Cycle 2 fixes in each case.
→ [PREWASH_PROMPT_COLLECTION.md](PREWASH_PROMPT_COLLECTION.md)

---

### Phase 2: Product Selection (and Three AI Failures)

**Entry 8 — Initial Decision Matrix**
Four ideas evaluated against three inputs (strengths × jury × criteria). **CiteGuard** — a legal citation hallucination verifier — scored highest on every dimension: 46/50 jury fit, 9.1/10 criteria fit, 10/10 uniqueness. The team's 731-document hallucination corpus was the competitive moat.
→ CiteGuard scored 46/50 jury fit, 9.1/10 criteria fit, 10/10 uniqueness

**Entry 9 — FAILURE: Anchoring Bias**
The human had flagged Damien Charlotin's hallucination database (907 cases + PelAIkan verification tool) as a direct competitor to CiteGuard. Despite this, Claude scored CiteGuard's uniqueness at 10/10 across three subsequent documents. The competitor evidence was acknowledged in conversation but never propagated into the scoring. CiteGuard recommendation invalidated. Product decision reopened.
→ [docs/ANCHORING_FAILURE.md](https://github.com/voelspriet/flipside/tree/main/docs/ANCHORING_FAILURE.md)

**Entry 10 — New Concepts via "Think Like a Document"**
Five new tool concepts generated using a Prewash-compliant prompt with 5 constraints and 5 required outputs. The principle was used as a generative design constraint, not just a search technique.
→ Five concepts: SourceSight (source credibility), CiteGuard (citation verification), GrantWhisperer (grant optimization), ContractLens (one-sided document analysis → later became FlipSide), SourceFlipper (perspective-based comparison)

**Entry 11 — Matrix Comparison**
Earlier decision matrix retested against new concepts using identical scoring. The initial winner still led on two dimensions but no longer won on every dimension. ContractLens — a tool to analyze one-sided contracts from the drafter's perspective — emerged as the strongest concept.

**Entry 12 — Expanded Reach**
Each concept modified for broader user base. ContractLens expanded from "contracts" to "any one-sided document" (ToS, insurance, loans, HOA rules), growing from ~50M to ~250M+ potential users with zero added complexity. ContractLens ranked #1.
→ ContractLens expanded from ~50M to ~250M+ potential users

**Entry 13 — Problem Deep Dive**
10 real problems identified. Three lenses applied (most users, most financial damage, least served). The Policyholder's Exclusion Maze — the labyrinth of interacting exclusion clauses insurers use to deny legitimate claims — appeared in all three lists: ~30M users/year, $10K–$50K per denied claim, zero existing tools.
→ Policyholder's Exclusion Maze: ~30M users/year, $10K–$50K per denied claim

**Entry 14 — FAILURE: Framing Bias**
The human asked about a document comparison feature. Claude narrowed it to "compare two insurance policies" because it was anchored on ContractLens. The human's actual intent was broader: any two documents, three comparison types (contradictions, divergent conclusions, gaps). Third documented instance of AI interpreting through its most recent frame.
→ Third documented instance of AI interpreting through its most recent frame

**Entry 15 — Document Comparison Concept**
The broader comparison concept defined with three precise comparison types, five document pairings, and a concrete walkthrough (pharma press release vs. FDA response letter).
→ Three comparison types defined: contradictions, divergent conclusions, gaps

**Entry 16 — Product Unity Analysis**
Tested whether ContractLens and document comparison could be one product. Answer: no — a single sentence cannot describe both to both audiences. Recommendation: build ContractLens only. The comparison tool's 2M users are 0.8% of ContractLens's 250M+.
→ Recommendation: build ContractLens only. Comparison tool's 2M users = 0.8% of ContractLens's 250M+

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
During the hackathon AMA, asked Cat Wu (Product Lead, Claude Code co-creator) two questions about meta-prompting.

**Question 1**: "What's the Claude Code team's approach to meta-prompting?"

**Question 2 (follow-up)**: "Give me a prompt to analyze [topic]" and then "execute prompt" works way better than "analyze this topic" — why is that?

**Cat Wu's answer** (34:12–35:41 in AMA recording):

> "I'm not totally sure why it is, but we have noticed this as well, which is why we've shipped things like prompt improver. I wish I had a great answer for you on this.
>
> My best guess is that it's changing the model from doing fast thinking to slow thinking. Like if you ask a coworker, 'Hey, can you take a quick look at X?' — they might just do an 80% pass and give it back to you. Whereas if you meet with that coworker live for 30 minutes and you say, 'Hey, we really need to do this, this is why it's important,' then they might go back, do a bit more thorough work given that they understand how important it is.
>
> I don't think this is a fully satisfying explanation because it's not an exact parallel, but I'll just echo that. We definitely see this as well. We're not totally sure why it happens. I think it's possible that you asking the model to elaborate actually causes the — like you asking the model to improve the prompt causes the model to believe that this is a more important thing to do, that it should be more comprehensive in."

Our hypothesis: the two-step approach forces the model to reflect on *the task itself* (what makes a good analysis, what biases to avoid) rather than just reflecting on *what the user wants* (which is what plan mode does). We validated this with 30 agent-tested comparisons and 7 documented before/after cases — see [meta-prompting-strategy.md](meta-prompting-strategy.md). FlipSide's entire architecture is a productized version of this discovery.

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
Ran a structured audit identifying 10 Opus 4.6 capabilities FlipSide didn't use yet. Ranked by (Demo Impact × Feasibility). 10 parallel evaluation agents assessed each capability against the codebase. All 10 were implemented in a single session.

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

### Phase 8: The Model Placement Pivot

**Entry 58 — FAILURE: Opus Card Backs Never Rendered**
We spent 3+ hours trying to get Opus 4.6 onto the back of flip cards. The idea was compelling: Haiku generates the naive front (fast, gullible), Opus generates the expert back (deep, precise). The "flip IS the model transition" — literally switching from a small model to a large one mid-animation. Three separate approaches to inject Opus-generated HTML into the card back DOM all failed: `replaceWith`, `innerHTML`, and `cloneNode`. The HTML was correct. The matching worked. But injecting new content into a `preserve-3d` CSS container 60-70 seconds after initial render consistently produced invisible or corrupt results. Root cause: DOM mutation inside a 3D-transformed element that has already been painted, transformed, and cached by the browser's compositor is unreliable. The back content arrived too late into a container that the GPU had already baked.

**Entry 59 — Haiku Was Already Great at Cards**
When the DOM rendering bug forced us to let Haiku produce both card sides, we discovered something we hadn't tested: Haiku 4.5 was already doing a great job on card backs. With the constrained output format (tagged fields, 18-category trick taxonomy, score range 0-100), Haiku correctly identifies risk patterns, classifies tricks, writes punchy bottom lines, and produces concrete figures using the document's actual numbers. The structured prompt format guides Haiku to consistent, high-quality results. We had assumed the card back — the big reveal — needed Opus 4.6's extended thinking to be convincing. It didn't. When you give a fast model a clear format and a focused task, it performs. Cards now render with both sides from Haiku in ~12 seconds. No skeleton loading. No waiting for Opus. Instant flip from the moment the card appears.

**Entry 60 — 5-Thread Architecture: Where Opus 4.6 Actually Shines**
With Haiku owning the cards, Opus 4.6 was redirected to four focused expert threads — each targeting a capability that Haiku genuinely cannot deliver:

1. **Cross-clause compound risks** (`interactions` thread) — Opus holds multiple clauses in working memory simultaneously and reasons about their interaction. "Section 3's liability cap interacts with Section 7's indemnification to create unlimited personal exposure." Haiku analyzes clauses one at a time; Opus connects them. This requires the kind of multi-step reasoning that extended thinking enables.

2. **Power asymmetry analysis + fair standard** (`asymmetry` thread) — Opus quantifies how many obligations fall on each party, computes a power ratio ("You have 23 obligations. They have 4. Ratio: 5.75:1"), and constructs a counterfactual: what would a balanced version of this clause look like? This requires legal reasoning and counterfactual generation — capabilities that emerge with extended thinking but not with pattern matching.

3. **Document archaeology + drafter profiling** (`archaeology` thread) — Opus distinguishes boilerplate (template language, generic) from custom-drafted clauses (specific to this deal, recently modified). It reasons about writing style, specificity, and internal consistency to build a drafter profile: "Drafted by a large property management company using a template last updated circa 2019, with custom additions to Sections 4 and 11." This is deductive reasoning from stylistic evidence — Haiku would guess, Opus deduces.

4. **Overall assessment with self-correction** (`overall` thread) — The meta-analysis: overall risk score with reasoning, methodology disclosure ("How Opus 4.6 Analyzed This"), and a quality check where Opus reviews its own analysis for false positives and blind spots. Self-correction — the model critiquing its own output — is a capability that requires the depth of extended thinking. Haiku doesn't second-guess itself.

All 4 Opus threads plus Haiku start at t=0. No dependencies. No buffers. No gating. Each thread's output streams independently into a collapsible verdict column. The event loop dropped from ~200 lines of buffer-stitching logic to ~30 lines of independent dispatch.

**Entry 61 — Seven Opus 4.6 Capabilities, Each in Its Own Place**
The 5-thread architecture isn't just a performance optimization — it's a capability showcase. Each Opus feature now has a dedicated stage where it's the star:

| Capability | Where it lives | Why only Opus can do it |
|-----------|---------------|----------------------|
| Extended thinking (compound reasoning) | Interactions thread | Multi-clause working memory + step-by-step logical chains |
| Counterfactual generation | Asymmetry thread | "What would a fair version say?" requires legal reasoning |
| Stylistic deduction | Archaeology thread | Distinguishing template from custom by writing patterns |
| Self-correction | Overall thread | Reviewing own analysis for false positives requires metacognition |
| Vision / multimodal | Deep analysis (PDF images) | Detecting 6pt fine print, buried placement, visual hierarchy tricks |
| Multi-turn follow-up | `/ask/<doc_id>` endpoint | Holding full document + prior analysis in context for conversational Q&A |
| Confidence calibration | All Opus threads | Explicit reasoning chains backing HIGH/MEDIUM/LOW judgments |

The lesson: the most creative use of a frontier model isn't putting it everywhere — it's identifying the specific capabilities that only it can deliver and building features around those capabilities. Haiku gets the cards. Opus gets the expert verdict. Each model gets a stage that showcases what it does best.

**Entry 62 — English-Only Output with Original-Language Quotes**
Reversed the bilingual approach. All prompts now output in English regardless of document language. Quotes from non-English documents are kept in the original language with English translations in parentheses. Removed ~125 lines of bilingual code: EN-READER/EN-FIGURE/EN-EXAMPLE fields, reader-voice-en rendering, en-report-summary collapsible wrapper. Added `**Language**` field to Document Profile metadata. New "Report in [language]" header button uses the `/ask` endpoint to translate the full analysis into the document's language for download. English is the universal analysis language; the original language is preserved only where it matters — in the actual document quotes.

**Entry 63 — "Message the Company" Feature**
After the deep analysis summary, a button appears: "Draft a message to [Company Name]" (drafter name from metadata). Opus 4.6 generates a professional, firm-but-polite complaint letter citing the specific high-risk clauses found. Uses the existing `/ask` endpoint — zero new backend code. Streams the response live, then offers "Copy to clipboard" and "Open in email" action buttons. This is the follow-through feature: analysis → understanding → action.

**Entry 64 — Midpoint Self-Evaluation**
Halftime assessment against judging criteria. Scores: Demo 7/10, Opus 4.6 Use 8/10, Impact 8/10, Depth & Execution 9/10 (composite 7.9/10). Biggest strength: the flip card as product metaphor + 14 visible Opus capabilities + documentation depth. Biggest gap: no demo video (30% of score), outdated README, and Opus wait time in live demo. Priority for second half: 60% presentation (video, README, summary) and 40% product polish. Full evaluation with prompt and answer in `strategy.md`.

**Entry 65 — Verdict Column: Focused Reading Mode**
Replaced the old toggle-collapse behavior with a proper UX flow. Pulsing (gold) sections are now visually locked (dimmed, not clickable) — users can't trigger GUI glitches by clicking half-rendered content. When a section turns green (done), clicking it opens a focused reading panel with ←→ navigation between completed sections only. The "Read full verdict" button shows "N of 4 ready" as a progress counter and only becomes active when all 4 Opus threads complete. If the user is reading a single section when the last thread finishes, the nav counter updates to "Full report ready →" with an inline link. The invitation text ("look over the expert's shoulder") fills the wait time before the first section completes.

**Entry 66 — README Overhaul + Submission Summary**
README fully rewritten: 5-thread architecture diagram (was 3-thread), 14 capabilities (was 13), English-only output (was bilingual), message-the-company + counter-draft added, seven-stage pipeline table, third-party license attribution. 173-word submission summary added as the first paragraph after the tagline. HACKATHON_LOG inconsistencies fixed: line counts, capability #14, entry counts.

**Entry 67 — Live "Tricks Detected" Panel in Verdict Column**
While users wait for the Opus expert report, the verdict column now shows a live "Tricks detected" panel that populates incrementally as Haiku finds each clause. Trick categories (from the 18-type taxonomy) appear as hoverable pills sorted by frequency (top 10), with SVG line icons matching the demo tile stroke style and tooltip descriptions on hover. The pill shows a ×N count when a trick appears more than once. Replaced emoji `TRICK_MAP` with `TRICK_ICONS` containing 18 SVG line icons — used consistently across verdict pills, card back footnotes, badge labels, filter chips, and the Drafter's Playbook visualization. Accumulator resets on each new analysis.

**Entry 68 — Verdict Panel Readability Pass**
Reviewed all verdict column elements for readability in the ~300px sidebar. Fixes: trick name font 0.65→0.76rem, count font 0.55→0.65rem with bold weight, icons 14→16px in verdict pills (12px in compact contexts like chips/footnotes, 14px in playbook), tooltip positioning changed from center-aligned (clipped at edges) to left-aligned with arrow at 1rem. "Expert report complete" status text now hides when done (redundant with "Your verdict is ready" header). Context-aware icon sizing via CSS cascade.

**Entry 69 — Clean Export + Not-Applicable Gating**
Save Report rewritten: builds clean HTML from card `data-*` attributes and DOM queries instead of dumping raw `innerHTML` (which included broken SVG score rings and 3D flip transforms). Loading time estimates added ("about a minute" / "about 30 seconds"). Verdict column now hides for non-applicable documents. Spinning ⟳ flip icon on all cards.

**Entry 70 — Hackathon Event Waiver as 14th Sample**
Added the real "Built with Opus 4.6" hackathon event waiver as a sample document. Claude sparkle icon tile. Meta-recursive: FlipSide analyzes the document that governs its own creation. Generated thumbnails. Demo script created (3-minute 7-scene narrative).

**Entry 71 — Verdict Summary + Home Button + Layout Fixes**
Persistent verdict summary appears when all 4 Opus sections complete: risk score + first sentence from overall assessment. Stays visible as user navigates cards. Home button replaces "Back" text with house icon. "Paste text" / "Compare" links moved under drop zone. Score label moved below ring (was clipped inside SVG). "Read full verdict" button flips on Y-axis when ready. Card flip ⟳ stops spinning after flip.

**Entry 72 — Header Layout + Privacy + Bug Fixes**
Header rearranged: action buttons (Copy, Email, Export, Dark mode, Home) moved left next to brand, status pill + model badge moved right. Rich verdict summary: scores + Power Imbalance Index + rights/obligations counts + power ratio extracted from Opus threads. Privacy notice added to upload screen ("analyzed by Claude and never stored"). Fixed: duplicate Drafter's Playbook on re-render, verdict summary PII duplicate line, all three columns aligned to same top position. Data persistence audit confirmed: no disk writes, no database, no temp files — documents exist only in memory during session.

**Entry 73 — FAQ + The FlipSide Fair Clause**
Left sidebar navigation added to upload screen with 8-section FAQ: What is FlipSide, How it works (5-thread architecture), Your data & privacy (nothing stored), What Claude keeps (Anthropic API policy — not used for training, 30-day safety retention, no sharing), Why is it free (MIT, hackathon origin, $300/hr attorney access), Is this legal advice (no), Who built this (Henk van Ess — 0% human code). The centerpiece: The FlipSide Fair Clause — a 7-provision model service agreement written by Opus 4.6 with extended thinking. Each section shows the reasoning and names the trick it avoids (Content Grab, Forced Arena, Cascade Clause, asymmetric exit). Score 0/100, power ratio 1:1, no tricks detected. The clause teaches users the trick vocabulary before they upload, making flip card reveals more meaningful.

**Entry 74 — Phase 2 Probe #51: Low-Resource Language Test (Frisian)**
Boundary test: uploaded a 6-clause residential lease written entirely in West Frisian (Frysk, ~500,000 speakers) — one of the lowest-resource European languages. The contract was deliberately loaded with every trick from the 18-type taxonomy: uncapped daily late fees, tenant bears all structural repairs, asymmetric termination (14 days vs 6 months), Moving Target rent changes with 7-day notice, forced arbitration in landlord's jurisdiction, and class action waiver.

**Result: No degradation. No hallucination. Analysis quality indistinguishable from English documents.**

All 5 threads completed successfully (5,073 SSE events). Detailed findings:

*Language handling:*
- Both Haiku and all 4 Opus threads correctly identified the language as "Frisian (West Frisian)" / "Frysk"
- Every Frisian quote accurately translated inline: "sûnder maksimum" → "without maximum", "it dak" → "the roof", "De Eigener hat gjin ferplichting" → "The Owner has no obligation"
- Zero language confusion or misidentification across 16,294 chars of Haiku output and 21,952 chars of Opus output

*Trick detection — all 6 caught:*
| Clause | Trick | Score |
|--------|-------|-------|
| Uncapped late fees (§1) | Penalty Disguise | 92/100 |
| Tenant bears all repairs (§2) | Reverse Shield | 88/100 |
| Asymmetric termination (§3) | Escape Hatch | 86/100 |
| Rent changes, 7-day notice (§5) | Moving Target | detected in interactions |
| Landlord-chosen arbitration (§6) | Forced Arena | detected in clauses |
| Continued use = acceptance (§5) | Cascade Clause | detected in interactions |

*Cross-clause compound analysis:*
- "The Infinite Debt Spiral": rent increase + uncapped penalties + payment waterfall = mathematically inescapable debt vortex. Opus traced the exact mechanism: landlord raises rent on Monday → tenant's old payment is now "partial" → partial payments go to penalties first → rent balance stays unpaid → generates fresh penalties daily at €65/day → no mathematical ceiling
- "The Maintenance Hostage Lock": can't leave for 6 months + must pay for structural repairs + no rent offset → locked into paying for landlord's property improvements

*Jurisdiction-aware legal context:*
- Opus correctly identified Dutch law as the governing framework for a Frisian-language document
- Cited specific Burgerlijk Wetboek articles: Art. 7:206 BW (landlord maintenance duty), Art. 7:271–274 BW (exhaustive termination grounds requiring court order)
- Identified the Huurcommissie (rent commission) framework for regulated rent increases
- Called multiple clauses "almost certainly void under mandatory Dutch law"
- Fair Standard Comparison cited real Dutch legal standards for each provision

*Document archaeology:*
- Correctly classified the preamble as boilerplate ("skeleton designed to be unsigned or signed under pressure")
- Identified §1 (rent) and §2 (maintenance) as custom-drafted with specific explanations: the payment waterfall was "an engineered compounding mechanism" and the maintenance clause was "deliberately stripped of any qualification"

*Power asymmetry:*
- Your rights: 2 · Their rights: 11 · Your obligations: 12 · Their obligations: 2
- Power Ratio: 11:2 — "The Owner holds virtually unchecked unilateral control"
- Sole discretion (them): 4×

*Overall assessment:*
- Risk Score: 88/100 — "Serious risk — seek professional legal review"
- Power Imbalance Index: 95/100
- Opus thinking log shows it translated and analyzed each clause methodically, identified Dutch BW as the applicable legal framework, and noted that several clauses would be void as a matter of mandatory tenant-protection law

**Why this matters:** Frisian is a genuine low-resource language — not just "non-English" but rare enough that training data is sparse. The test proves that Opus 4.6 can (1) correctly identify obscure languages, (2) translate accurately inline, (3) apply the correct legal jurisdiction based on language context, and (4) detect all trick types with the same precision as English documents. This is capability #12 (long-context retrieval) and #2 (perspective adoption) working on genuinely novel input.

**Entry 75 — Phase 2 Probe: Compare Mode Precision Test (Near-Identical Documents)**
Boundary test: uploaded two nearly identical 6-clause service agreements where only Clause 4 (Liability) was changed. Document A: "$500 cap + client waives all consequential damages." Document B: "liability capped at total fees paid" (no waiver). All other clauses word-for-word identical. The question: does compare mode detect ONLY the real difference, or does it hallucinate phantom findings?

**Result: The real difference was detected with surgical precision. Minor noise in "Hidden Differences" section — but by design, not by error.**

Compare mode uses a single Opus 4.6 stream (no Haiku, no parallel threads) with the full `build_compare_prompt()` — a structured 4-section report format (Overview, Side-by-Side Analysis, Hidden Differences, Recommendation). This is purely LLM-based semantic comparison — no `difflib`, no text diff, no character-level matching anywhere in the codebase.

*What Opus found correctly:*
- **Section 1 (Overview):** Immediately identified "these two documents are identical in every respect except for the liability clause (Section 4)" as the single most important difference
- **Section 2 (Side-by-Side):** Rated 5 of 7 comparable areas as 🟢 GREEN (neutral — identical language). The liability cap and consequential damages waiver both received 🔴 RED ratings with correct quantitative analysis: "$500 vs $60,000 = 120× difference in protection"
- **Section 4 (Recommendation):** Correctly declared Document B as the better deal, with specific negotiation advice for both scenarios

*What Opus added beyond the diff:*
- **Section 3 (Hidden Differences):** Flagged three YELLOW items missing from BOTH documents — dispute resolution, indemnification, and insurance requirements. These aren't false positives — they're genuine gaps that a senior attorney would note. The prompt instructs "absences reveal intent," so flagging shared omissions is by design.
- **Consequential damages waiver** treated as a separate finding from the liability cap, even though both are in the same clause. This is correct — they're two independent legal mechanisms (cap on direct damages vs. waiver of indirect damages).

*Architectural observation:*
Compare mode follows a fundamentally different rendering path from normal analysis. No sidebar (document preview hidden), no flip cards (incremental clause extraction bypassed), no verdict column (4 Opus sections suppressed), no follow-up questions. The response streams as markdown and renders directly via `safeMd2Html()` with the same risk badge styling (`styleRiskBadges()`) used elsewhere. This is `run_single_stream()` — one API call, not `run_parallel()`.

**The trade-off is deliberate:** A text diff would mechanically guarantee "only the changed words" but would miss semantic implications. The LLM comparison trades mechanical precision for legal understanding — it can explain WHY the change matters ("120× less protection"), not just WHAT changed. For a product about revealing hidden risks, semantic comparison is the right architecture. The cost: the model will always try to fill all 4 report sections, which means shared gaps get flagged even when the user only asked about differences.

**Entry 76 — Phase 2 Probe #53: Context Window Boundary Test (100+ Page Documents)**
Systematic test of Opus 4.6 cross-clause reasoning quality at increasing document scale. Generated synthetic contracts with 4 deliberately planted cross-clause traps (innocent "A" clause near the start + dangerous "B" clause near the end). Each trap tests a different exploit pattern:
- Trap 1: Service credits look fair (§A) → sole remedy waiver guts them (§B)
- Trap 2: CPI adjustment + payment waterfall (§A) → uncapped $75/day late fees + acceleration (§B)
- Trap 3: Narrow IP license (§A) → perpetual derivative works grab (§B)
- Trap 4: Data export right (§A) → 7-year retention + ML training exclusion (§B)

**Two test rounds** — short clauses (testing clause count), then verbose clauses (testing token count):

*Round 1: Short clauses (distance test)*
| Clauses | Chars | Tokens | Max distance | Traps caught |
|---------|-------|--------|-------------|-------------|
| 25 | 8,475 | ~2K | 19 | **4/4** |
| 50 | 13,890 | ~3K | 40 | **4/4** |
| 100 | 25,240 | ~6K | 90 | **4/4** |
| 150 | 36,161 | ~9K | 140 | **4/4** |
| 200 | 47,007 | ~12K | 194 | **4/4** |

*Round 2: Verbose clauses (context window test)*
| Clauses | Chars | Est. tokens | Pages | Max distance | Traps caught | Time |
|---------|-------|------------|-------|-------------|-------------|------|
| 50 | 104K | ~26K | 34 | 44 | **4/4** | 135s |
| 100 | 217K | ~54K | 72 | 94 | **4/4** | 156s |
| 200 | 442K | ~110K | 147 | 194 | **4/4** | 171s |
| 300 | 667K | ~167K | 222 | 294 | **4/4** | 94s |

**Result: 36 out of 36 traps caught across 9 documents. Zero misses.**

At 222 pages (~167K tokens), Opus 4.6 caught a cross-clause interaction between §3 and §297 — separated by 294 clauses and ~660K characters of filler. It referenced both section numbers by name and explained the compound risk mechanism.

**The Haiku bottleneck:** Haiku card scan found only 10-14 clauses per document regardless of size (output token ceiling at ~32K tokens). On a 222-page document, Haiku analyzed ~5% of clauses. This is an engineering constraint (output token budget), not a model quality limitation — Haiku correctly READ the full document but ran out of space to write cards for all clauses.

**Conclusion:** We could not find the failure point for Opus 4.6 cross-clause reasoning within the 200K context window. At ~167K tokens (the largest document that fits with system prompt), reasoning quality was indistinguishable from a 25-clause document. The practical bottleneck for long documents is not Opus's reasoning but Haiku's output token budget — addressable by increasing `quick_max` or implementing chunked card generation.

**Entry 77 — Expert Scrutiny via Playwright: QC the LLM Output Quality**
Used Playwright to capture FlipSide's full LLM output (all 13 flip cards + verdict) from a real analysis run, then fed the complete capture to two parallel Opus 4.6 expert agents — a GUI/UX expert and a narrative/prompt expert — who independently reviewed the output for quality issues.

**48 combined findings** across severity levels. Two were false positives (wrong Playwright DOM selector: `.back-bottom-line` vs `.back-bottom-line-lead`; textContent concatenation artifact for "The lure" label). The remaining 46 real findings triggered three rounds of prompt iteration:

| Round | Changes | Issues remaining |
|-------|---------|-----------------|
| 1 | Expanded forbidden words, added Rules 17-20, verdict calibration tiers, green card regex fix | 8 |
| 2 | "ABSOLUTELY FORBIDDEN" emphasis, replacement vocabulary, INTERLEAVE rule | 7 |
| 3 | Planning step in Rule 1 (list sections before outputting), explicit replacements, gullible voice template | 6 (3 mild) |

**Key prompt additions:**
- Rule 1 → mandatory planning step: list clause sections, merge overlaps, interleave severity, THEN output cards
- Rule 17: Merge overlapping clauses (same right/risk = one card)
- Rule 18: Teaser variety (different rhetorical angles, no keyword repetition)
- Rule 19: Example variety ("no recourse" max once across all cards)
- Rule 20: Clause ordering (interleave RED/YELLOW, max 3 consecutive REDs)
- Verdict `[SHOULD_YOU_WORRY]` calibration tiers based on red-flag count
- Reader voice forbidden words expanded to ~30 terms with explicit replacement vocabulary

**LLM compliance plateau:** Reader voice forbidden-word compliance improved from pervasive violations to ~80-90% across 3 rounds — diminishing returns on prompt engineering. Documented as Decision 26 in strategy.md.

**Entry 78 — Live Thinking Narration + Card Nav Cleanup**
Replaced canned capability ticker messages ("PERSPECTIVE SHIFT", "LONG-CONTEXT RETRIEVAL") with live sentences extracted from the Opus thinking stream. `narrateFromThinking(chunk)` accumulates text, splits on sentence boundaries, strips bullet points/markdown/LLM prefixes, deduplicates, and pushes to the header capability ticker via `showCapTickerNarration()` with a "THINKING" label. Rate-limited to 3.5s between updates. Zero extra API calls — the thinking stream is free narration material.

Simultaneously cleaned up the card nav area — removed three elements that now live exclusively inside the verdict card:
- **Risk summary strip** (`#riskSummaryStrip`): concern/watch/fair counts with colored dots — now rendered at very top of `renderOneScreenVerdict()` by counting `data-risk-level` attributes from flip card DOM
- **Tricks detected bar** (`#tricksDetectedBar` + `#tricksDetectedPills`): removed from DOM entirely — trick pills with SVG icons rendered inside verdict below risk summary
- **Thinking viewer + toggle** (`#thinkingViewer`, `#thinkingToggle`): removed from DOM — narration only in header ticker

Also locked "Go Deeper" buttons (`.locked` class: 45% opacity, `cursor: not-allowed`) until `deepTextComplete` — prevents users from starting Opus deep dives before the verdict is ready. Auto-unlock on `overall_done`.

---

### Current State

| Artifact | Lines | Status |
|----------|-------|--------|
| `app.py` | 3,861 | Backend: Flask, SSE, parallel processing, vision, tool use, follow-up, prompt caching, dynamic token budget, suitability gate, 14 sample docs |
| `templates/index.html` | 10,748 | Card-first frontend: instant flip cards, live thinking narration, one-screen verdict with risk summary + tricks + 4 Go Deeper buttons, clean export, confidence badges, follow-up UI, DOMPurify |
| `docs/` | 2 files | LIVE_DEMONSTRATION.md, ANCHORING_FAILURE.md |
| `HACKATHON_LOG.md` | This file | 78 entries, complete process timeline |
| `README.md` | Product description + 14 Opus capabilities + meta-prompting discovery |

---

## Five Documented AI Failures

Each failure was caught by the human, not by Opus 4.6. Each demonstrates a different bias pattern:

| # | Failure | Phase | Pattern | The AI did | The human did |
|---|---------|-------|---------|-----------|--------------|
| 1 | [Live Demonstration](https://github.com/voelspriet/flipside/tree/main/docs/LIVE_DEMONSTRATION.md) | Planning | Training vocabulary bias | Projected its own framework onto a vague input | Revealed the structured version |
| 2 | [Anchoring Failure](https://github.com/voelspriet/flipside/tree/main/docs/ANCHORING_FAILURE.md) | Planning | Confirmation bias across documents | Maintained a conclusion despite contradicting evidence | Scrolled back and demanded accountability |
| 3 | Framing Bias | Planning | Recency/context anchoring | Interpreted a new concept through its most recent topic | Showed the neutral version |
| 4 | Meta-analysis prompt (Entry 33) | Self-examination | Adjective/framing bias | Wrote a prompt with "experienced," "differently," unverified claims, leading questions | Demanded Prewash-compliant rewrite |
| 5 | LLM output format assumption (Entry 36) | Build | Format rigidity bias | Wrote a regex assuming all models produce identical output format | Debugged via console.log, found Haiku drops `/100` |

The first four are the same error at different scales: **the AI uses itself as the measurement of things, rather than observing what must be there.** The fifth is a variation: **the AI assumes consistency across models without testing.** Both solved by the same principle: observe what IS there, not what should be there.

---

## Lessons Learned

1. **Meta-prompting is worth the time.** Asking the AI to show its plan before executing adds 2 minutes and eliminates entire categories of misalignment.

2. **Process documentation can be a product.** What started as internal scaffolding became a publishable case study.

3. **Treat the jury as a design constraint.** Research evaluators the same way you research users — before you build.

4. **Always verify AI training data with live research.** The Thariq/Upsolve error would have misdirected the entire strategy.

5. **AI prompts carry invisible bias.** Every adjective is a policy decision. The [Prewash Method](PREWASH_METHOD.md) catches them before they compound.

6. **Removing bias is not enough — add precision.** "How well?" is unbiased but unmeasurable. "Rate 1-5" is both.

7. **AI confidence is not alignment.** "I understand" tells you nothing about whether it understood correctly.

8. **Re-examine conclusions when new evidence arrives.** The decision matrix was retested against new concepts. It held — partially.

9. **Acknowledgment is not integration.** When AI says "good point," verify that it actually changed the analysis, not just the conversation.

10. **Confirmation bias compounds across documents.** A biased conclusion in Document 1 becomes an invisible assumption in Document 3.

11. **The first decision sets the tone.** We chose methodology over code for the first 45 minutes. Zero lines of product code, 15 process decisions. That discipline compounded through the rest of the build.

12. **Test your AI collaborator's judgment.** The omission test (Entry 3) built justified trust — not blind trust. If the model catches what you expect, you can hand it more autonomy later.

13. **Read the scoring rubric before you build.** Demo is 30% of the score. That single number eliminates entire categories of projects — CLI tools, invisible backends, anything hard to show in 3 minutes.

14. **Cross-reference all inputs before deciding.** Strengths alone → DeepVerify. Criteria alone → ElectionShield. Only by crossing all three inputs did CiteGuard emerge — and then fail on a fourth input the AI ignored.

15. **Format matters for different audiences.** The same content was published as PDF (for presentations) and Markdown (for GitHub). Thinking about distribution early prevents rework later.

---

## What Exists

| Artifact | Purpose |
|----------|---------|
| `app.py` (3,861 lines) | Flask backend: prompts, parallel processing, vision, tool use, follow-up, prompt caching, SSE streaming, suitability gate, 14 sample docs |
| `templates/index.html` (10,748 lines) | Card-first frontend: instant flip cards, one-screen verdict, 4 Go Deeper buttons, live thinking narration, clean export, confidence badges, follow-up UI with tool calls, DOMPurify |
| [docs/](https://github.com/voelspriet/flipside/tree/main/docs) | Methodology documents (LIVE_DEMONSTRATION, ANCHORING_FAILURE) |
| [BUILDER_PROFILE.md](https://github.com/voelspriet/flipside/blob/main/BUILDER_PROFILE.md) | Who built this and what they bring |
| This file | 78 entries, complete process timeline |

## What Remains

- ~~Demo video (3 minutes, scripted narrative)~~ Done
- ~~100-200 word summary~~ Done (173 words)
- ~~Update README.md to match current state~~ Done
- ~~Reduce perceived Opus wait time~~ Addressed: verdict progress strip, live thinking narration (Expert Mind), 10s auto-reveal, one-screen verdict
- ~~Save Report broken (SVG dump)~~ Fixed: clean HTML export from structured data
- ~~Non-applicable docs show verdict~~ Fixed: verdict column hides

**Deadline: February 16, 3:00 PM EST**

## 14 Opus 4.6 Capabilities Used

| # | Capability | Visible in product |
|---|-----------|-------------------|
| 1 | Extended thinking (adaptive) | Single Opus verdict thread with adaptive thinking — model decides reasoning depth per document |
| 2 | Perspective adoption | Gullible reader voice on card fronts, drafter's perspective on card backs + villain voice in deep dives |
| 3 | Vision / multimodal | PDF page images → visual formatting tricks detected (font size, buried placement) |
| 4 | Tool use | Follow-up Q&A: `search_document`, `get_clause_analysis`, `get_verdict_summary` tools |
| 5 | Multi-turn follow-up | "Ask about this document" — Opus traces answers through all relevant clauses |
| 6 | Confidence calibration | HIGH/MEDIUM/LOW badges with explicit reasoning chains |
| 7 | Self-correction | Quality Check in verdict colophon — reviews own analysis for false positives and blind spots |
| 8 | Counterfactual generation | Power ratio + on-demand counter-draft rewrites unfair clauses |
| 9 | Stylistic deduction | Drafter profile in verdict + on-demand "Hidden Combinations" deep dive |
| 10 | Split-model parallel | Haiku 4.5 (instant full cards) + 1 Opus 4.6 (one-screen verdict) + 4 on-demand Opus deep dives |
| 11 | Prompt caching | System prompts cached for 90% cost reduction |
| 12 | Long-context retrieval | Cross-clause interaction detection across full documents (no truncation) |
| 13 | Low over-refusals | Gullible reader, villain voice, drafter perspective — all sustained without self-censoring |
| 14 | English-only + download in language | All output in English (universal access); download full report translated to document's original language |

---

<sub>Maintained during the Claude Code Hackathon 2026. Every entry links to a detailed document in the docs/ folder.</sub>
---

**Henk van Ess** — [imagewhisperer.org](https://www.imagewhisperer.org) · [searchwhisperer.ai](https://searchwhisperer.ai) · [digitaldigging.org](https://digitaldigging.org)
