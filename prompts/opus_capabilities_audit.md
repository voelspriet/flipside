# Prompt: Untapped Opus 4.6 Capabilities for FlipSide

> Goal: find capabilities of Claude Opus 4.6 that FlipSide doesn't use yet — not as behind-the-scenes tests, but as features that would be VISIBLE in a 3-minute demo.

---

## WHAT FLIPSIDE CURRENTLY USES

1. **Extended thinking (adaptive)** — Opus reasons across all clauses to find cross-clause compound risks
2. **Perspective adoption** — System prompt instructs Opus to think as the drafter's attorney
3. **SSE streaming** — Thinking and text tokens stream to the frontend in real-time
4. **Split-model parallel processing** — Haiku 4.5 for fast card scan, Opus 4.6 for deep analysis, both running simultaneously
5. **Structured output via prompting** — Markdown with `---` separators, parsed by regex
6. **Multilingual detection** — Opus responds in the document's language automatically
7. **Constrained vocabulary** — 18-category trick taxonomy forces consistent classification

That's it. Everything else Opus 4.6 can do is untouched.

## WHAT FLIPSIDE DOES NOT USE

For each capability below, answer three questions:

**A.** What would this look like as a user-facing feature in FlipSide? (Not a test. A feature the user sees and interacts with.)

**B.** Would this be impressive in a 3-minute demo? (The demo is 30% of the jury score. If it's invisible, it's worthless for scoring.)

**C.** How hard is it to add? (Hours, not days. The deadline is Monday.)

### Capabilities to evaluate:

**1. Tool use / function calling**
Opus can call tools during its reasoning. FlipSide gives it raw text and gets text back. No tools.
- Could Opus look up jurisdiction-specific laws during analysis? ("This non-compete violates California Business & Professions Code §16600")
- Could it query a legal database, a definitions API, or even a currency converter for penalty calculations?
- Could it call a "confidence checker" tool that forces it to rate its own certainty per finding?

**2. Vision / multimodal input**
Opus 4.6 can read images natively. FlipSide extracts text from PDFs using Python libraries (pdfplumber/PyPDF2) and sends plain text to the API.
- Could Opus read the PDF pages as images instead? This would catch: formatting signals (fine print literally in smaller font), signature placement, checkbox layouts, table structures that convey meaning beyond text.
- Could it analyze document LAYOUT as a persuasion tactic? ("The liability waiver is placed on page 7 of 8, after all medical disclosures, to benefit from signing fatigue.")
- What would this look like in the flip card? ("VISUAL TRICK: This clause is set in 6pt font while the coverage section uses 11pt")

**3. Multi-turn follow-up**
FlipSide is single-shot: upload → analysis → done. The user cannot ask follow-up questions.
- "What happens if I'm 3 days late on rent?" → Opus traces the cascade through all relevant clauses
- "Which clauses can I actually negotiate?" → Opus re-analyzes with negotiation strategy
- "Explain clause 4 like I'm 16" → Opus simplifies one specific finding
- Would a "Ask about this clause" button on each flip card be demo-worthy?

**4. Structured JSON output**
FlipSide parses markdown with regex (Postel's Law). Opus can output structured JSON directly.
- Would switching to JSON output eliminate the parsing fragility that caused the Haiku/Opus format mismatch (Entry 36)?
- Or does markdown streaming + incremental parsing give a better UX (cards appearing mid-stream)?
- Is there a hybrid: JSON for the structured fields (score, level, trick) + markdown for the prose (reader voice, drafter voice)?

**5. Self-assessment / confidence signaling**
Opus can reason about its own uncertainty. FlipSide doesn't ask it to.
- Could each flip card show a confidence indicator? ("I'm 90% sure this is a Time Trap" vs. "This might be a Scope Creep — the language is ambiguous")
- Would this INCREASE trust (transparent about uncertainty) or DECREASE trust (user sees the AI doubting itself)?
- Demo angle: show a clause where Opus says "I'm uncertain — the language supports two interpretations" → that's more impressive than false confidence

**6. Extended thinking as visible product**
FlipSide currently HIDES Opus thinking during the deep analysis phase. The thinking panel is collapsed/hidden.
- The thinking tokens contain Opus's actual reasoning: "Let me consider how §3 and §7 interact... if the tenant is late by even one day, §3 triggers... and §7 means they've already waived..."
- This IS the "Keep Thinking" prize material. Is there a way to make the thinking VISIBLE and VALUABLE without the dark panel that users hated?
- Could the thinking be post-processed into a "reasoning trail" that shows HOW Opus connected clauses? A visual graph? An animated sequence?

**7. Comparative multi-document reasoning**
FlipSide has a compare mode (two documents). But it's basic — same prompt, two inputs.
- Could Opus compare a document against a STANDARD? ("Here's your lease. Here's what a fair lease looks like in your jurisdiction.")
- Could it compare against its own knowledge? ("This penalty clause is 3x the industry standard for residential leases.")
- Could it compare versions? ("Your landlord sent you a 'revised' lease. Here's what actually changed and why.")

**8. Agentic loop / self-correction**
Opus can be called multiple times in sequence where each call builds on the previous.
- First pass: quick analysis. Second pass: Opus reviews its OWN output and flags where it was too harsh or too lenient.
- Could this catch the "false positive on fair documents" problem? (Opus finds phantom risks in a balanced mutual NDA.)
- Demo angle: "FlipSide checks its own work" — visible self-correction is impressive and builds trust.

**9. Batch / parallel clause analysis**
FlipSide sends the ENTIRE document to one Haiku call. Could each clause be sent as a SEPARATE parallel API call?
- 10 clauses × 10 parallel Haiku calls = all cards in ~2 seconds instead of ~15 seconds
- Trade-off: loses context between clauses (can't say "this clause is worse because of clause 3")
- Is the speed gain worth the context loss?

**10. System prompt caching**
Anthropic supports prompt caching — the system prompt is stored server-side and reused across calls.
- FlipSide's system prompt is large (~2000 tokens with trick taxonomy). Could caching reduce latency and cost?
- Is this invisible to the user (yes) and therefore irrelevant for demo scoring (yes)?
- Still worth doing for production cost optimization?

## OUTPUT FORMAT

Rank all 10 capabilities by: **(Demo Impact × Feasibility)**

For the top 3, write a concrete feature spec:
- What the user sees
- What the demo shows (in 20 seconds — it needs to fit in the 3-minute video)
- What changes in the code (which file, which function)
- Estimated implementation time

For the bottom 7, write one sentence explaining why they rank lower.

## THE REAL QUESTION

Which of these capabilities, if added, would make a jury member say: "I didn't know Opus 4.6 could do that"?

That's the only question that matters for the "Most Creative Opus 4.6 Exploration" prize. Everything else is engineering polish.
