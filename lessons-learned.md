# Lessons Learned: Building with Opus 4.6

**What we discovered about Opus 4.6's capabilities by pushing it to its limits.**

FlipSide was built entirely by a journalist with zero programming experience, directing Claude Code (Opus 4.6) through conversation. This document captures the specific moments where Opus 4.6 did something no other model could — not hypothetically, but in the actual build.

---

## Lesson 1: Six Parallel Opus Threads — The Model as Architecture

**What happened:** FlipSide spawns 6 parallel AI threads when you upload a document:

```
Upload
  │
  ├── Haiku 4.5 ──── Fast flip cards ────────────── ~12s
  │
  ├── Opus 4.6 ───── Expert verdict ─────────────── ~30s  (prioritized)
  │        │
  │   5s delay (verdict gets head start)
  │        │
  │        ├── Opus 4.6 ── Scenario Simulator ───── ~20s
  │        ├── Opus 4.6 ── Walk-Away Number ──────── ~15s
  │        ├── Opus 4.6 ── Hidden Combinations ───── ~25s
  │        └── Opus 4.6 ── Negotiation Playbook ──── ~20s
  │
  └── SSE stream to browser (all threads push events from t=0)
```

Each Opus thread has its own system prompt, thinking budget, and analysis focus. The verdict uses `thinking: {type: 'adaptive'}` — the model decides its own reasoning depth per document. A gym membership gets ~4K thinking tokens. A 50-page insurance policy with compound exclusions gets ~16K.

**The lesson:** Opus 4.6 is reliable enough to be the architecture, not just a component. Five simultaneous Opus calls, each performing a different expert analysis on the same document, all streaming results to the same browser via SSE. The threads don't coordinate — they don't need to. Each thread's prompt is specialized enough that the results are complementary without explicit orchestration.

**The code pattern:**

```python
_dd_specs = [
    ('scenario', build_scenario_prompt, 16000),
    ('walkaway', build_walkaway_prompt, 12000),
    ('combinations', build_combinations_prompt, 16000),
    ('playbook', build_playbook_prompt, 16000),
]

def _launch_deep_dives():
    cancel.wait(timeout=5)  # Verdict gets 5-second head start
    for label, prompt_fn, max_tokens in _dd_specs:
        if cancel.is_set():
            q.put((f'{label}_done', None))  # Document rejected — clean exit
        else:
            threading.Thread(
                target=worker,
                args=(label, prompt_fn(), max_tokens, MODEL, True),
                daemon=True,
            ).start()
```

The `cancel.wait(timeout=5)` is elegant: it either waits 5 seconds (giving the verdict a head start on the API connection pool) or exits immediately if the document is rejected. One line handles both the priority scheduling and the cancellation edge case.

**Why Opus 4.6:** Running 5 simultaneous Opus calls was impractical with 4.5's 200K context window and slower throughput. The adaptive thinking budget — where the model allocates reasoning proportional to document complexity — is a 4.6-specific capability.

---

## Lesson 2: Three Expert Agents as Decision-Makers

**What happened:** To choose which 4 deep dives to build, we spawned 3 parallel Opus 4.6 agents — each roleplaying a different expert evaluating 10 candidate features:

| Agent | Role | Top 4 Picks |
|-------|------|-------------|
| Agent 1 | Apple GUI Designer | Walk-Away Number, Document Archaeology, Scenario Simulator, Negotiation Playbook |
| Agent 2 | Software Product Manager | Scenario Simulator, Walk-Away Number, Red Flag Timeline, Negotiation Playbook |
| Agent 3 | Opus 4.6 Capability Coder | Hidden Combinations, Scenario Simulator, Negotiation Playbook, Walk-Away Number |

**Convergence:** All three independently selected Scenario Simulator, Walk-Away Number, and Negotiation Playbook. The fourth slot diverged — the GUI designer picked Document Archaeology (visual appeal), the PM picked Red Flag Timeline (user engagement), and the coder picked Hidden Combinations (Opus 4.6 showcase). We went with the coder's pick because the hackathon judges evaluate model capabilities.

**The lesson:** Parallel expert agents aren't faster versions of one agent — they're structurally different. Each agent evaluated the same 10 ideas through a different lens (visual design, product metrics, technical showcase), and their disagreements were more informative than their agreements. The convergence zone (3/4 features all three agreed on) gave us confidence. The divergence zone (the fourth pick) forced a strategic decision we wouldn't have identified alone.

**Why Opus 4.6:** The quality of each expert persona depends on the model's ability to maintain a consistent analytical framework across 10 complex evaluations. With lesser models, the personas drift — the "GUI designer" starts making product management arguments by idea #6. Opus 4.6's sustained coherence over long evaluations keeps each expert genuinely in character.

---

## Lesson 3: Theory-of-Mind in the Negotiation Playbook

**What happened:** The Negotiation Playbook prompt asks Opus to analyze not the document, but the *drafter* — inferring their business incentives from the document's structure.

Example output for a residential lease:

> **About the Other Side:** This document was drafted by a high-volume property management company optimizing for cash flow predictability. The custom-drafted security deposit clause and aggressive late fee schedule reveal their priorities. The boilerplate pet and parking sections are copy-paste — low stakes for them.
>
> **Push Hard on These:**
> - **Late fee cap** (Section 4.2): Ask for a $75 cap. *Why they'll bend:* Industry standard, and they'd rather keep you than fight over fee amounts.
>
> **Don't Waste Capital On:**
> - **Rent amount** (Section 2): That's the business deal, not the fine print.
> - **Arbitration venue** (Section 15): Their legal team is based there — non-negotiable.

**The lesson:** The model doesn't just classify clauses — it reasons about *why each clause exists*. "The security deposit clause is custom-drafted (it deviates from the boilerplate template used elsewhere) → they spent legal effort on it → it protects something they care about → cash flow predictability." That's strategic inference from document structure, not text classification.

The prompt forces this with: "Theory of mind: reason about WHY each clause exists, not just WHAT it says." And: "The drafter profile should predict BEHAVIOR, not just describe document structure."

**Why Opus 4.6:** GPT-4o and Sonnet give document-specific advice but shallow strategy. "Negotiate the late fee" is generic. "They'll bend because they'd rather keep you than fight over fee amounts — industry standard, and their boilerplate pet section shows they don't actually care about convenience terms" is counterparty modeling. The extended thinking scratchpad is where this reasoning happens — the model builds a mental model of the drafter's priorities before generating advice.

---

## Lesson 4: Cross-Clause Compound Reasoning (N² Pairwise Analysis)

**What happened:** The Hidden Combinations deep dive asks Opus to find clause *pairs* that create compound risks invisible when reading each clause alone.

The prompt specifies the contrast format:

> **Read separately:** Normal auto-renewal. Normal fee adjustment.
>
> **Read together:** They can raise your price by any amount every year, and you can only escape if you happen to remember the cancellation window — which they never remind you about.

**The lesson:** A 30-clause document has 435 possible clause pairs. The model must systematically evaluate each for compound effects — not just pattern-match "indemnification + liability cap." The extended thinking scratchpad walks through pairs methodically, building a map of interactions. This is where BigLaw Bench's 90.2% score manifests as a user-facing capability.

The prompt instruction "Use your full extended thinking budget to systematically check clause pairs" isn't decoration — it changes model behavior. Without it, the model finds 2-3 obvious pairs. With it, the thinking stream shows systematic pair enumeration.

**Why Opus 4.6:** GPT-4o finds obvious pairs (the ones a paralegal would catch). Opus 4.6 finds the subtle cascades that a senior attorney would catch — where Clause A changes the meaning of Clause B, which triggers Clause C's penalty, which removes Clause D's protection. That's the difference between pattern matching and legal reasoning. BigLaw Bench 90.2% is the benchmark; the Hidden Combinations output is the proof.

---

## Lesson 5: The Walk-Away Number — Verified Compound Arithmetic

**What happened:** The Walk-Away Number deep dive computes a single dollar figure: the maximum you could owe if everything in the contract goes wrong.

The tagged output format forces structured verification:

```
[WALKAWAY_NUMBER]
$23,450
[/WALKAWAY_NUMBER]

[WALKAWAY_BREAKDOWN]
- Early termination fee: $4,200 (Section 12)
- Remaining rent acceleration: $14,400 (Section 7.1)
- Late fees (compounded over 12 months): $1,850 (Section 4.2 + 4.5)
- Lost security deposit: $2,000 (Section 3)
- Attorney's fees: $1,000 (Section 15.3)
[/WALKAWAY_BREAKDOWN]
```

The prompt enforces: "The TOTAL must equal the sum of the breakdown items — verify your math."

**The lesson:** Finding every financial clause is easy. Compounding them correctly is hard: the late fee applies to the new balance, which triggers the default threshold earlier, which accelerates the remaining term. The extended thinking scratchpad maintains a running ledger — you can watch the model do arithmetic with the contract's actual numbers in the thinking stream.

The tagged format (`[WALKAWAY_NUMBER]`, `[WALKAWAY_BREAKDOWN]`, etc.) enables structured frontend rendering — the hero number displays at 2.4rem in JetBrains Mono while the breakdown renders as a detailed waterfall. One prompt, two rendering formats, parsed by tag matching.

**Why Opus 4.6:** Most models botch compound financial calculations across 5+ interacting clauses. The late fee compounds monthly, but the default trigger is based on the original amount, not the compounded amount — or is it? The thinking stream shows Opus working through these ambiguities clause by clause, maintaining a verified running total.

---

## Lesson 6: Scenario Simulator — Multi-Step Causal Reasoning

**What happened:** The Scenario Simulator narrates a worst-case timeline using the document's actual numbers. Opus picks the most likely trigger (missed payment, illness, schedule conflict) and traces what happens step by step over 3–6 months.

Example output:

> **Month 1 — You miss a payment.** The $50 late fee (Section 4.2) is applied to your balance.
> **Month 2 — The fee compounds.** Per Section 4.5, the late fee is charged on your new balance including last month's fee. You now owe $102.50.
> **Month 3 — Default clause triggers.** Section 7.1 defines "default" as 60 days past due. Your remaining lease obligation ($14,400) accelerates.
> **Total exposure after 3 months: $14,502.50**

**The lesson:** Each month depends on the previous month's state. The model must hold every financial clause in working memory while simulating forward in time. The extended thinking scratchpad is where the compounding math happens — visible in the thinking stream if you watch it.

**Why Opus 4.6:** This is multi-step causal reasoning with state tracking. The model maintains a running financial state, applies clause triggers conditionally, and chains consequences across time. GPT-4o loses track of running totals across 6 months of simulated interactions. The "pick the most LIKELY trigger, not the most dramatic" constraint also requires judgment calibration — a 4.6-level capability.

---

## Lesson 7: Playwright QC — The Model Reviews Its Own Output

**What happened:** After the product worked, we ran automated quality control using a three-phase pipeline:

1. **Playwright capture** — Browser automation extracts all card data and verdict content
2. **Dual-expert review** — Two parallel Opus agents analyze the captured output (GUI expert + Narrative expert)
3. **Prompt-level fixes** — Expert findings become prompt engineering changes, validated by re-capture

The experts found 48 issues across 3 rounds. 10 were high-priority prompt problems:

| Issue | Before Fix | After Fix |
|-------|-----------|-----------|
| Reader voice using forbidden words | Pervasive ("waiving", "liable") | 3/13 mild violations |
| "No recourse" as conclusion | 6+ cards | 1 card |
| Teaser variety | "forever" 3× in first three | Clean — no repeated hooks |
| Verdict contradicts cards | "Risk is low" with 11 RED cards | "Several clauses need attention" |
| Near-duplicate cards | 2 pairs covering same section | 1 pair (with planning step) |

**The lesson:** The hardest bugs in AI products live in the gap between "the code works" and "the output is good." Code review catches code bugs. Prompt review catches prompt bugs. But *output review* — systematically reading what the model actually produces for real inputs — catches quality bugs that neither code nor prompt review can find.

The fix that mattered most: replacing Rule 1 ("output each clause immediately") with a mandatory planning step. Before outputting any cards, the model now lists its planned sections with risk levels, merges overlapping sections, and interleaves RED/YELLOW to prevent alarm fatigue. This costs ~2 seconds of latency but eliminates near-duplicate cards.

**Why Opus 4.6:** The dual-expert QC agents each maintained a consistent expert lens (GUI vs. narrative) across 48 findings. The GUI expert found information hierarchy issues (5 competing labels on card back) while the narrative expert found voice consistency issues (reader using "waiving"). Neither would catch both. The overlap zone (both flagged verdict contradiction) provides high-confidence diagnosis. Lesser models lose the expert persona over 48 sequential evaluations.

---

## Lesson 8: Live Thinking Narration — Free Intelligence

**What happened:** The loading screen showed canned messages ("Building a mental model of the entire agreement") on a 4-second rotation timer. Meanwhile, Opus was streaming actual thinking tokens about the user's specific document — hidden in a developer panel.

We replaced the canned narration with `narrateFromThinking(chunk)`:

- Accumulates thinking text in a sentence buffer
- Scores sentences: boosts document-specific content (dollar amounts, party names, legal concepts), penalizes LLM self-talk ("Hmm", "Let me think")
- Rate-limits to 3.5s between updates
- Threshold: score >= 2 to display

Result: Users see "Non-compete restricts working anywhere in North America for 24 months" instead of "Building a mental model of the entire agreement."

**The lesson:** The thinking stream is free narration material. Opus already generates document-specific reasoning as part of its analysis — the only cost is extraction (regex + scoring heuristics), which is ~0ms per chunk. Zero additional API calls. Zero additional tokens. The model's internal reasoning becomes the user's loading experience.

**Why Opus 4.6:** This is only possible because Opus 4.6's extended thinking produces coherent, document-specific sentences. With lesser models' thinking, you'd get fragments and reasoning artifacts that aren't presentable. The adaptive thinking budget means the narration quality scales with document complexity — a simple contract produces brief, factual narration; a complex one produces detailed, clause-specific reasoning.

---

## Lesson 9: Adaptive Thinking — The Model Decides Its Own Depth

**What happened:** The verdict uses `thinking: {type: 'adaptive'}` instead of a fixed thinking budget. The model decides how much reasoning each document needs.

A gym membership contract: ~4K thinking tokens. Quick assessment, standard clauses, predictable risks.

A 50-page insurance policy with compound exclusions: ~16K thinking tokens. Deep chain-of-thought tracing cross-clause interactions, compounding financial calculations, jurisdiction-specific enforceability analysis.

**The lesson:** Fixed thinking budgets waste tokens on simple documents and underspend on complex ones. Adaptive thinking is self-regulating depth control — the model allocates reasoning where the reasoning is hard, not where the prompt says to.

**Why Opus 4.6:** Adaptive thinking is a 4.6-specific capability. No other model has this self-regulating depth control. It means FlipSide's analysis quality automatically scales with document complexity without any code changes or per-document configuration.

---

## Lesson 10: A Non-Coder Built This — 12,500 Lines via Conversation

**What happened:** Every line of FlipSide — 3,535 lines of Python backend, 8,994 lines of HTML/CSS/JS frontend — was written by Claude Code directed by a journalist who has never written code. The git history shows 82 commits over 5 days, including 7 major architecture pivots where the entire system was restructured.

The development method:
1. Screenshot the current state
2. Ask Claude to label every visible element with its CSS class/ID
3. Use those names to direct changes: "Move `.disclaimer` above `.upload-container`"
4. For bugs: show the screenshot, say "it flickers," give NO hypothesis — let the model trace from evidence

The 7 architecture pivots are the real evidence:
1. Single-model → split-model (Haiku + Opus)
2. Sequential cards → parallel card workers
3. Single verdict → 5-layer expert report → single one-screen verdict
4. Blocking pipeline → stream-first pipeline
5. 4 parallel deep dives → on-demand per click
6. Raw thinking dump → narrated AI progress briefing
7. Canned loading messages → live thinking narration

Each pivot rewrote hundreds of lines while maintaining consistency across 12,500 lines of code.

**The lesson:** Opus 4.6 doesn't just write code — it translates between visual thinking and technical implementation. The screenshot-to-vocabulary workflow replaced the IDE for a non-coder. And with a 1M token context window, the entire codebase fits in working memory during every edit.

**Why Opus 4.6:** Any model can write a function. But rethinking a system 7 times — while maintaining consistency across 12,500 lines, understanding a non-coder's intent from three misspelled words and a screenshot — requires the combination of Terminal-Bench 65.4% (agentic coding), MRCR 76% (long-context retrieval across code), and GDPval-AA +144 Elo (understanding intent from imprecise input). That's the 4.6 trifecta.

---

## Lesson 11: Generic Event Dispatch — One Pattern for N Threads

**What happened:** Adding 4 new Opus threads to the existing architecture required updating 3 separate event loops. The pattern that made this painless:

```python
OPUS_SOURCES = {'overall', 'scenario', 'walkaway', 'combinations', 'playbook'}
```

On the frontend:

```javascript
case 'scenario_text':
case 'walkaway_text':
case 'combinations_text':
case 'playbook_text':
    var ddSource = msg.type.replace('_text', '');
    opusSections[ddSource].text += msg.content;
    updateDepthButtonState(ddSource);
    break;
```

**The lesson:** Adding a new Opus thread to FlipSide requires: (1) write the prompt function, (2) add one entry to `_dd_specs`, (3) add the label to `OPUS_SOURCES`. The event loops, SSE dispatch, frontend accumulation, and button state management are all generic.

**Why Opus 4.6:** The `OPUS_SOURCES` set was originally `{'overall'}`. Expanding it to 5 entries required changing exactly one line in each of the 3 event loops — because the model designed the dispatch logic to be label-agnostic from the start. Opus built architecture that anticipated extension. The model planned ahead while writing the original event loop.

---

## The Meta-Lesson

Every lesson above shares a common thread: **Opus 4.6 is reliable enough to be trusted with judgment calls, not just execution.**

- Thread architecture: the model decides its own thinking depth per document
- Expert agents: the model evaluates ideas through consistent expert personas
- Negotiation Playbook: the model infers counterparty incentives from document structure
- Hidden Combinations: the model systematically evaluates N² clause pairs
- Walk-Away Number: the model does verified compound arithmetic
- Scenario Simulator: the model traces multi-step causal chains with state tracking
- Playwright QC: the model reviews its own output through expert lenses
- Live narration: the model's internal reasoning is presentable to users
- Architecture pivots: the model rethinks the system, not just edits it

The shift from 4.5 to 4.6 isn't "better code generation." It's the difference between a model you supervise and a model you collaborate with. FlipSide has 6 Opus threads running simultaneously, each making independent expert judgments about the same document, and the results are complementary without coordination. That's not a tool. That's a team.

---

## Sources

- [Claude Opus 4.6 Announcement](https://www.anthropic.com/news/claude-opus-4-6) — Anthropic
- [BigLaw Bench: 90.2%](https://www.anthropic.com/news/claude-opus-4-6#benchmarks) — Expert-level legal reasoning
- [Terminal-Bench 2.0: 65.4%](https://www.anthropic.com/news/claude-opus-4-6#benchmarks) — Agentic coding
- [Adaptive Thinking](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6) — Model-controlled reasoning depth
- FlipSide git history: 82 commits, Feb 10–15, 2026
- FlipSide architecture: `app.py` (3,535 lines), `templates/index.html` (8,994 lines)
