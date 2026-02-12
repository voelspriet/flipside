# Feasibility Prompt: Fast-Model Flip Cards + On-Demand Deep Verdict

## Context for Claude

You are helping redesign FlipSide, a contract analysis tool. The current architecture uses Claude Opus 4.6 (with extended thinking) for everything — it takes 60-120 seconds before the user sees anything useful. We want to split this into two layers:

**Layer 1 — "Card Scan" (Fast Model: Haiku 4.5 or Sonnet 4.5)**
Generates SHORT flip card content for each clause. Cards appear in 5-15 seconds.

**Layer 2 — "Deep Verdict" (Opus 4.6 with extended thinking)**
Generates full analysis. Available on demand when user clicks "Our Verdict" on any card.

## Current User Experience Problem

1. User uploads document
2. Stares at loading screen for 60-120 seconds
3. Gets a wall of detailed analysis text crammed into flip cards
4. Cards are too dense — the "other side" has paragraphs of text

## Proposed New Experience

### Flip Card — FRONT (what the reader sees first)
```
SECTION 1                              ← section-label style
Late Fee Structure                     ← title, bold
If rent is not received by 11:59 PM    ← one key sentence from clause
on the 1st, a late fee of $75/day
shall be assessed.

YOU'D THINK                            ← reader voice, italic, green-tinted
"$75 seems steep but I always pay
on time, so this won't affect me."

        See the other side →           ← flip trigger
```

### Flip Card — BACK (the drafter's side, SHORT)
```
┌─────────────────────────────────────┐
│ Late Fee Structure                  │
│ RED · 92/100 · Penalty Disguise     │ ← risk header
├─────────────────────────────────────┤
│                                     │
│ YOU'D READ                          │ ← one-sentence plain restatement
│ "$75 per day, no cap, no grace      │
│ period."                            │
│                                     │
│ YOU SHOULD KNOW                     │ ← one-sentence alarm bell
│ "Illegal under Oregon law.          │
│ A 10-day delay = $750 in fees."     │
│                                     │
│ ████████████████████░░ 92/100       │ ← score bar
│                                     │
│     [ Our Verdict → ]               │ ← links to deep Opus analysis
│                                     │
│         ← Flip back                 │
└─────────────────────────────────────┘
```

### "Our Verdict" (expands below card OR slides in as panel)
Full Opus analysis: drafter's thinking, detailed juxtaposition, legal citations, negotiation strategy. This is the current deep content — but shown on demand, not crammed into the card back.

## Design Questions to Evaluate

### 1. Model Selection for Layer 1
- **Haiku 4.5** (`claude-haiku-4-5-20251001`): ~3-8s, cheapest. Can it reliably classify risk levels (GREEN/YELLOW/RED) and assign scores? Can it identify the correct trick category from the 18-type taxonomy?
- **Sonnet 4.5** (`claude-sonnet-4-5-20250929`): ~8-20s, mid-tier. More reliable classification but slower. Worth the extra seconds?
- **Key question**: How accurate is Haiku at risk scoring vs Opus? A GREEN-flagged clause that Opus later calls RED would break trust.

### 2. Output Format for Fast Cards
The fast model needs to output structured, parseable content. Proposed format:

```
### [Title] ([Section Ref])

> "[One key sentence from the clause — the most revealing language]"

[READER]: [One sentence. What a normal person would think. Second person, trusting tone.]

[GREEN/YELLOW/RED] · Score: [0-100]/100 · Trick: [CATEGORY]

**You'd read:** [One sentence plain restatement]

**You should know:** [One sentence — the gap between words and reality. Punchy, alarming if warranted.]

---
```

This is ~6-8 lines per clause vs ~20-30 lines in the current format. The `---` separator enables incremental streaming detection (already implemented in frontend).

### 3. Opus Deep Verdict — When Does It Run?
Three options:

**A. Eager parallel (current):** Start Opus immediately alongside Haiku. Deep analysis is ready by the time user finishes flipping through cards. Cost: always runs, even if user doesn't read it.

**B. Lazy on-demand:** Only start Opus when user clicks "Our Verdict" on any card. Fastest initial load, but adds 60-120s wait when they want details. Poor UX for engaged users.

**C. Hybrid — start Opus after first Haiku card appears:** Haiku starts immediately. Once the first card is detected (proof the document parsed correctly), kick off Opus in background. By the time user reads 3-4 cards, Opus is often ready. If they click "Our Verdict" before it's ready, show "Analyzing deeper..." with thinking panel.

**Recommendation: Option C.** It balances cost, speed, and UX. The Haiku results also serve as a "document validity check" before committing to the expensive Opus call.

### 4. Risk Score Disagreement
What if Haiku says GREEN (score: 15) but Opus says RED (score: 85)?

Options:
- **Opus always wins:** Update the card header/badge when Opus result arrives. Shows the user the system is getting smarter. Risk: jarring color change.
- **Flag the upgrade:** When Opus upgrades a risk level, add a subtle "⚠ Risk upgraded after deep analysis" indicator. Builds trust.
- **Accept Haiku as final for card, Opus only in verdict:** Simpler, but could miss critical risks in the card view.

**Recommendation:** Opus overrides silently for scores. If risk LEVEL changes (e.g., GREEN→RED), add a brief animation + "Updated after deep analysis" note.

### 5. Backend Architecture

```
POST /upload → returns doc_id

GET /analyze/{doc_id} (SSE stream)
  ├─ Phase 1: Haiku card scan (fast)
  │   ├─ thinking_start → collapsed status line
  │   ├─ text events → incremental card detection via ---
  │   ├─ quick_done → all cards parsed
  │   └─ (Opus starts in background after first card)
  │
  ├─ Phase 2: Opus deep analysis (background)
  │   ├─ Streams into buffer
  │   ├─ When user clicks "Our Verdict" on card N:
  │   │   └─ Frontend requests /verdict/{doc_id}/{clause_index}
  │   │       └─ Returns buffered Opus content or streams if still running
  │   └─ deep_done → all verdicts available
  │
  └─ done
```

**Alternative (simpler):** Keep current SSE architecture but swap model for quick scan:
```python
# In run_parallel():
t_quick = Thread(target=worker, args=('quick', build_card_scan_prompt(), 8000))
# ↑ Uses Haiku with card_scan prompt
t_deep = Thread(target=worker, args=('deep', build_deep_analysis_prompt(), preset['max_tokens']))
# ↑ Uses Opus with full analysis prompt
```

This requires minimal backend changes — just a model parameter per worker thread.

### 6. Cost Analysis
Current (2x Opus): ~$0.30-0.60 per analysis
Proposed (Haiku + Opus): ~$0.01-0.03 (Haiku) + $0.15-0.30 (Opus) = ~$0.16-0.33
**~40-50% cost reduction** with better UX.

If using Option B (lazy Opus): $0.01-0.03 per analysis for users who only flip cards.

## Task

1. Evaluate the feasibility of each design decision above
2. Identify risks or failure modes I haven't considered
3. Propose improvements to the card content format
4. Write the system prompt for the fast card-scan model (Haiku or Sonnet)
5. Suggest how "Our Verdict" should be presented in the UI — inline expansion, slide-in panel, or separate view?
6. Consider: should the fast model also generate a 1-sentence "bottom line" per clause that appears BEFORE the user flips? (preview of severity without flipping)
