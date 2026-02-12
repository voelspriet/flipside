# Prompt: Rewrite the FlipSide Flip Card System

## Who You Are

You are a frontend specialist implementing a 3D flip card system for FlipSide, a legal document analysis tool. The backend (Anthropic Claude Opus 4.6) streams clause analysis via SSE. The frontend renders it.

## The Product

FlipSide analyzes contracts/leases. Each clause gets shown as a **physical card** that flips to reveal hidden intent:

- **FRONT**: What a normal person would think reading this clause
- **BACK**: What the drafter strategically intended

The flip IS the product. It must feel physical, satisfying, and work perfectly.

## What's Broken (and Why)

The current system has a fundamental architecture flaw:

**The render cycle (`doRenderResults()`) runs every 300ms during streaming.** Each cycle:
1. Takes `responseContent` (accumulated markdown string)
2. Runs `marked.parse()` → produces HTML
3. Sets `resultsContent.innerHTML = html` (destroys entire DOM)
4. Runs `wrapClauseSections()` (wraps h3s into clause-card divs)
5. Runs `buildFlipCards()` (converts clause-cards with reader-voice into 3D flip cards)
6. Anti-flicker cache tries to restore old cards

This means **every 300ms**: all flip cards are destroyed and rebuilt. CSS classes (`.flipped`), animation state (`.woosh-in`), height calculations, and event listeners are lost. Patches (state maps, event delegation, caching) haven't solved it because the design is wrong.

**Symptoms:**
- Card grows/shrinks repeatedly (woosh animation retriggers)
- Can't click "See the other side" (click handlers lost or card rebuilt mid-click)
- Progressive disclosure fails (all cards visible)

## The Architecture You Must Build

### Core Principle: Separate Streaming from Flip Cards

**Phase 1 — Streaming (render normally, no flip cards):**
During SSE streaming, render `responseContent` as plain styled markdown. No flip cards. No progressive disclosure. Just let the text stream in and render as normal styled clause cards (the existing `wrapClauseSections()` + `styleRiskBadges()` etc. pipeline). This works well today and doesn't need flip cards.

**Phase 2 — Transform (once, after `quick_done`):**
When `quick_done` fires, the full quick-scan response is complete. At this point, ONCE:
1. Parse the final `responseContent` string with regex to extract structured clause data
2. Build flip card DOM elements from that structured data
3. Replace `resultsContent.innerHTML` with the flip card DOM
4. Set a flag `flipCardsBuilt = true`
5. **Stop the render cycle from touching the flip card DOM**

**Phase 3 — Deep analysis streams below:**
When deep analysis text arrives (after `quick_done`), append it below the flip cards in a separate container — NOT mixed into the flip card DOM. The deep analysis content (cross-clause interactions, playbook, assessment) renders normally with the existing markdown pipeline into a separate div.

### The Guard

```javascript
function doRenderResults() {
    if (flipCardsBuilt) {
        // Only render deep analysis content into the deep-analysis container
        renderDeepAnalysisContent();
        return;
    }
    // Normal streaming render for quick scan phase...
    // (existing pipeline: marked.parse → styleRiskBadges → wrapClauseSections etc.)
}
```

This is the single most important change. Once flip cards are built, the render cycle MUST NOT destroy and rebuild them.

## Data Extraction (Phase 2)

Parse `responseContent` to extract per-clause data. The model output format for each clause is:

```
### [Title] ([Section])

> "[Quoted clause text]"

[READER]: [Naive reader's impression in second person]

[GREEN/YELLOW/RED] · Score: NN/100 · Trick: [CATEGORY]

**What the small print says:** [text]
**What you should read:** [text]
```

Note: `[READER]:` gets pre-processed to `FLIPSIDE_READER:` before markdown parsing (it collides with markdown link reference syntax). But for regex extraction from raw `responseContent`, match `[READER]:` directly.

Extract into an array of objects:
```javascript
var clauses = [
    {
        title: "Late Fee Accumulation with No Cap",
        section: "Section 1",
        quote: "If rent is not received by 11:59 PM...",
        reader: "$75 seems like a reasonable late fee...",
        risk: "red",       // "red" | "yellow" | "green"
        score: 85,
        trick: "Hidden Multiplier",
        smallPrint: "...",
        shouldRead: "..."
    },
    // ...
];
```

## Flip Card DOM Structure

Build each flip card from the extracted data — NOT from DOM manipulation of rendered markdown:

```html
<div class="flip-card" data-clause-index="0" data-risk="red">
    <div class="flip-card-inner">
        <!-- FRONT -->
        <div class="flip-card-front">
            <div class="front-content">
                <div class="clause-section-ref">Section 1</div>
                <h3 class="clause-title">Late Fee Accumulation with No Cap</h3>
                <div class="clause-quote">"If rent is not received..."</div>
                <div class="reader-voice">
                    <span class="reader-voice-label">You'd think</span>
                    <div class="reader-voice-text">"$75 seems like a reasonable late fee..."</div>
                </div>
            </div>
            <button class="flip-trigger">
                <span>See the other side</span>
                <span class="flip-trigger-arrow">&rarr;</span>
            </button>
        </div>
        <!-- BACK -->
        <div class="flip-card-back">
            <div class="back-content">
                <div class="risk-header risk-header-red">
                    <h3 class="clause-title">Late Fee Accumulation with No Cap</h3>
                    <div class="risk-badge-group">
                        <span class="risk-badge risk-badge-red">RED</span>
                        <span class="risk-score-val risk-score-red">85/100</span>
                        <span class="trick-label">Hidden Multiplier</span>
                    </div>
                </div>
                <div class="back-body">
                    <div class="drafter-voice drafter-voice-red">
                        <span class="drafter-voice-label">The drafter's thinking</span>
                        <div class="drafter-voice-text">[filled later from deep analysis, or "Deep analysis in progress..."]</div>
                    </div>
                    <div class="clause-juxtapose">
                        <div class="juxtapose-col juxtapose-says">
                            <span class="juxtapose-label">What the small print says</span>
                            [text]
                        </div>
                        <div class="juxtapose-col juxtapose-read">
                            <span class="juxtapose-label">What you should read</span>
                            [text]
                        </div>
                    </div>
                </div>
                <button class="flip-back-trigger">
                    <span class="flip-back-arrow">&larr;</span>
                    <span>Flip back</span>
                </button>
            </div>
        </div>
    </div>
</div>
```

For GREEN cards, the back body shows:
```html
<div class="green-verdict">
    <div class="green-verdict-title">No hidden intent</div>
    <div class="green-verdict-text">This clause is genuinely balanced and fair to both parties.</div>
</div>
```

## Click Handling

Use event delegation on the flip card container (NOT per-element listeners). Since the DOM is built once and never destroyed, either approach works — but delegation is cleaner:

```javascript
flipCardContainer.addEventListener('click', function(e) {
    var flipTrigger = e.target.closest('.flip-trigger');
    if (flipTrigger) {
        var card = flipTrigger.closest('.flip-card');
        card.classList.add('flipped');
        return;
    }
    var flipBack = e.target.closest('.flip-back-trigger');
    if (flipBack) {
        var card = flipBack.closest('.flip-card');
        card.classList.remove('flipped');
        return;
    }
    var nextBtn = e.target.closest('.next-clause-btn');
    if (nextBtn) {
        revealNextCard();
        return;
    }
});
```

## Progressive Disclosure

Show one card at a time. When flip cards are first built:
1. All cards get `display: none` except the first
2. First card plays woosh-in animation ONCE
3. Below visible cards: "Show next clause (N remaining)" button
4. Click reveals next card with woosh-in
5. Simple navigation: "← Previous | Clause 2 of 7 | Next →"

Implementation:
```javascript
var revealedCount = 1;

function revealNextCard() {
    revealedCount++;
    var cards = flipCardContainer.querySelectorAll('.flip-card');
    cards.forEach(function(card, i) {
        if (i < revealedCount) {
            card.style.display = '';
            if (i === revealedCount - 1) {
                card.classList.add('woosh-in');
                card.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    });
    updateProgressiveUI();
}
```

## Animation

### Card entrance (woosh-in)
```css
@keyframes cardWoosh {
    0% { transform: translateY(80px) scale(0.96); opacity: 0; filter: blur(6px); }
    55% { transform: translateY(-6px) scale(1.005); opacity: 1; filter: blur(0); }
    75% { transform: translateY(2px) scale(0.999); }
    100% { transform: translateY(0) scale(1); }
}
.flip-card.woosh-in {
    animation: cardWoosh 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
}
```

Each card plays woosh ONCE when revealed. Never again.

### 3D Flip
```css
.flip-card { perspective: 1200px; }
.flip-card-inner {
    position: relative;
    transition: transform 0.7s cubic-bezier(0.4, 0, 0.2, 1);
    transform-style: preserve-3d;
}
.flip-card.flipped .flip-card-inner { transform: rotateY(180deg); }
.flip-card-front, .flip-card-back { backface-visibility: hidden; }
.flip-card-back {
    transform: rotateY(180deg);
    position: absolute; top: 0; left: 0; width: 100%;
}
```

**Height problem**: The back may be taller/shorter than the front. When `.flipped`:
```css
.flip-card.flipped .flip-card-front {
    visibility: hidden;
    position: absolute; top: 0; left: 0; width: 100%;
}
.flip-card.flipped .flip-card-back {
    position: relative;  /* takes flow, determines height */
}
```

### Reduced motion
```css
@media (prefers-reduced-motion: reduce) {
    .flip-card-inner { transition: none; }
    .flip-card.woosh-in { animation: none; }
    .flip-card.flipped .flip-card-back { position: static; transform: none; }
    .flip-card.flipped .flip-card-front { display: none; }
}
```

## Deep Analysis Integration

When deep analysis streams `[DRAFTER]:` blocks for cross-clause interactions:
1. Parse the drafter text from the deep analysis response
2. If it references clauses that have flip cards, update the `.drafter-voice-text` content on those cards' backs
3. The cross-clause cards, playbook, and assessment render below the flip cards in a separate section

The deep analysis content goes into `<div id="deepAnalysisContent">` which sits below `<div id="flipCardContainer">`. The render cycle for deep analysis uses the normal markdown pipeline (marked.parse → style functions → wrapClauseSections).

## Design System (already defined as CSS vars)

- Font: DM Sans
- Background: var(--bg-cream) #f7f5f0
- Card: var(--bg-card) #ffffff
- Accent: var(--accent) #c44b28
- Red: var(--red) #c44b28, Yellow: var(--yellow) #b8860b, Green: var(--green) #2d8a4e
- Radius: var(--radius) 12px
- Shadows: var(--shadow-sm), var(--shadow-md), var(--shadow-lg)

All CSS for the flip card component already exists in the file (lines ~538-780). Keep it.

## File Structure

Everything is in one file: `templates/index.html` (CSS + HTML + JS inline, ~2100 lines). The Flask backend is in `app.py`. Do NOT create separate files.

## What to Change

1. **Add HTML**: A `<div id="flipCardContainer" class="hidden"></div>` inside the results area, before `resultsContent`. And a `<div id="deepAnalysisContent"></div>` after it.

2. **Add JS function `buildFlipCardsFromData(clauses)`**: Takes the extracted clause array, builds all flip card DOM elements, appends them to `flipCardContainer`, hides all except first, plays woosh-in on first.

3. **Add JS function `extractClauseData(responseContent)`**: Regex-parses the raw markdown `responseContent` string to extract the clause array. This runs on the RAW string before markdown parsing — so match `[READER]:` not `FLIPSIDE_READER:`.

4. **Modify `quick_done` handler**: Call `extractClauseData()` → `buildFlipCardsFromData()` → show `flipCardContainer` → hide `resultsContent` → set `flipCardsBuilt = true`.

5. **Modify `doRenderResults()`**: Add guard at top — if `flipCardsBuilt`, only render deep analysis content into `deepAnalysisContent`, then return.

6. **Remove**: `buildFlipCards()` function (the old DOM-manipulation approach), the flip-card-related code from the anti-flicker cache, the `flipCardData` Map, the `triggerFlips()` function if it exists.

7. **Keep**: All flip card CSS (it's correct), event delegation on click (move target from `resultsContent` to `flipCardContainer`), progressive disclosure logic.

## Verification

1. Start server, open http://127.0.0.1:5000
2. Click "try sample lease"
3. During streaming: see normal styled clause cards appearing (no flip cards yet)
4. After quick_done: cards transform into flip cards, first card wooshes in
5. Click "See the other side →" — card flips with 3D animation
6. Click "← Flip back" — card unflips
7. Click "Show next clause (3 remaining)" — next card wooshes in
8. Deep analysis streams below the flip cards
9. Flipped cards STAY flipped during deep analysis streaming
10. Animation never retriggers on already-visible cards
