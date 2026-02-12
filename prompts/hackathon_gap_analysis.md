# Prompt: Hackathon Submission Gap Analysis

> Run this prompt against the FlipSide codebase to produce an actionable gap analysis before submission deadline.

---

## CONTEXT

You are auditing a hackathon project called **FlipSide** ("the dark side of small print") for the "Built with Opus 4.6: a Claude Code Hackathon" (Anthropic, February 2026). Deadline: **February 16, 3:00 PM EST**.

The project is a contract analysis tool: upload a document you didn't write → Opus 4.6 reconstructs the drafter's strategic intent → flip cards show the asymmetry between "what you'd think" and "what they intended."

## INPUTS

Read these files in order:
1. `docs/HACKATHON_BRIEF.md` — rules, schedule, submission requirements, judging criteria, prizes
2. `docs/CRITERIA_ANALYSIS.md` — strategic analysis of scoring weights
3. `HACKATHON_LOG.md` — 40+ timeline entries, 5 documented AI failures, current state table
4. `strategy.md` — 6 strategic decisions with rationale
5. `hackaton.md` — Phase 1 (50 interactive prompts, all done) + Phase 2 (50 boundary probes, status per probe)
6. `app.py` — backend (prompts, SSE streaming, parallel Haiku+Opus processing)
7. `templates/index.html` — frontend (flip cards, deep analysis, editorial design)
8. `test_ux_flow.py` — automated UX flow test
9. `README.md` — public-facing product description

## ANALYSIS STRUCTURE

For each section, output findings AND a specific action item with estimated time.

### 1. SUBMISSION REQUIREMENTS CHECKLIST

For each required deliverable, answer:
- Does it exist? (Yes/No/Partial)
- If partial: what's missing?
- Estimated time to complete
- Priority: BLOCKING (can't submit without it) / HIGH / MEDIUM / LOW

Required deliverables:
- [ ] 3-minute demo video (YouTube/Loom)
- [ ] GitHub repository (public, open source)
- [ ] Written summary (100-200 words)
- [ ] All code committed and pushed

### 2. SCORING GAP ANALYSIS

For each judging criterion, score the current project 1-10 and identify the single highest-ROI action to improve it:

| Criterion | Weight | Current Score | Evidence | Gap | Action | Time |
|-----------|--------|---------------|----------|-----|--------|------|

Criteria:
- **Demo (30%)**: "Working, impressive, holds up live, genuinely cool to watch"
- **Impact (25%)**: "Real-world potential, who benefits, how much it matters, fits problem statements"
- **Opus 4.6 Use (25%)**: "Creative use, beyond basic integration, capabilities that surprised even Anthropic"
- **Depth & Execution (20%)**: "Pushed past first idea, sound engineering, real craft not quick hack"

### 3. SPECIAL PRIZE ELIGIBILITY

For each special prize, assess:
- Current evidence strength (1-10)
- What the submission is ALREADY showing
- What one addition would strengthen the case most

Prizes:
- **Most Creative Opus 4.6 Exploration** ($5k): "The unexpected capability or use case nobody thought to try. Taught Anthropic something new."
- **The Keep Thinking Prize** ($5k): "Pushed past the obvious, iterated relentlessly, depth that turns a good hack into something genuinely surprising."

### 4. PHASE 2 BOUNDARY PROBE TRIAGE

From `hackaton.md`, all 50 Phase 2 probes (51-100) are pending. There is NOT time to do all 50.

Select the **5 probes with highest jury impact** considering:
- Which ones would be most impressive IN THE DEMO VIDEO?
- Which ones demonstrate Opus 4.6 capabilities that "surprised even Anthropic"?
- Which ones can be run in < 30 minutes each (just uploading a test document)?
- Which ones produce visual output (not just pass/fail)?

For each selected probe: what it tests, why it matters for scoring, estimated time, and what the demo would show.

### 5. DOCUMENTATION FRESHNESS

Check whether the following are up to date:
- `HACKATHON_LOG.md` — does "Current State" table match actual line counts? Are recent changes (last 24h) logged?
- `strategy.md` — does it reflect the latest architectural decisions?
- `README.md` — does it describe the product accurately?
- `hackaton.md` — are Phase 1 statuses accurate?

For each stale document: what's wrong and what to update.

### 6. RISK REGISTER

Identify the top 3 risks to a successful submission, ranked by (probability × impact):

For each risk:
- What could go wrong
- Probability (1-5)
- Impact if it happens (1-5)
- Mitigation

### 7. PRIORITY STACK

Given the deadline, produce a time-ordered action list:
1. MUST DO (submission fails without these)
2. SHOULD DO (meaningfully improves score)
3. COULD DO (nice-to-have if time remains)

For each item: action, estimated time, which criterion it improves, and expected score impact.

## OUTPUT RULES

- Be specific. "Improve the demo" is not an action. "Record a 3-minute screen recording showing: upload → first card in 5s → flip animation → villain voice → Full Verdict" is.
- Time estimates in hours, not ranges. If uncertain, estimate high.
- Score the project as a JUDGE would, not as the builder would. Judges see the demo video and repo — they don't see the effort.
- If something is genuinely strong, say so. If something is weak, say so. The builder needs accuracy, not encouragement.
- Respond in the same language as this prompt (English).
