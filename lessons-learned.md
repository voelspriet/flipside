# Lessons Learned: Building with Opus 4.6

> This document provides the **builder's perspective** — process decisions, quality control methods, and development insights that shaped the product. For the coding-side story, see [coding.md](coding.md).

---

## Lesson 1: Three Expert Agents as Decision-Makers

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

## Lesson 2: Playwright QC — The Model Reviews Its Own Output

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

## Lesson 3: Live Thinking Narration — Free Intelligence

**What happened:** The loading screen originally showed generic rotating messages like "Building a mental model of the entire agreement" on a 4-second timer. Meanwhile, Opus was generating document-specific reasoning in its thinking stream — but that stream was hidden.

We replaced the generic messages with live narration extracted from the thinking stream. The system filters for document-specific sentences (those mentioning dollar amounts, party names, or legal concepts) and suppresses model self-talk. Updates appear every 3.5 seconds.

**What the user sees:** Instead of "Building a mental model of the entire agreement," the loading screen now shows real-time insights like "Non-compete restricts working anywhere in North America for 24 months" or "Late fees compound monthly on the outstanding balance." The narration is specific to THEIR document, not a generic placeholder — and it costs zero additional API calls.

**The lesson:** The thinking stream is free narration material. Opus already generates document-specific reasoning as part of its analysis. Surfacing it as the loading experience turns dead wait time into an engagement hook. Users arrive at the analysis already primed with context about their document.

**Why Opus 4.6:** This is only possible because Opus 4.6's extended thinking produces coherent, document-specific sentences. With lesser models' thinking, you'd get fragments and reasoning artifacts that aren't presentable. The adaptive thinking budget means the narration quality scales with document complexity — a simple contract produces brief, factual narration; a complex one produces detailed, clause-specific reasoning.

---

## Lesson 4: 0% Human Code — 14,600 Lines via Conversation

> For the full development story with grounded examples from the git history, see [coding.md](coding.md).

**What happened:** Every line of FlipSide was written by Claude Code — 0% by a human. 89 commits over 5 days. 7 major architecture pivots where the entire system was restructured.

The development method that made this possible: screenshot the current state, ask Claude to label every visible element with its name, then use those names to direct changes. For bugs: show the screenshot, say "it flickers," give NO hypothesis — let the model trace from evidence.

**What the user sees:** A polished product that went through 7 complete rethinks — from single-model to split-model, from sequential to parallel, from blocking to streaming — each time getting faster and more useful. The final product feels like it was built by a team, not iterated by one person and one model.

**The lesson:** Opus 4.6 doesn't just write code — it translates between visual thinking and technical implementation. The screenshot-to-vocabulary workflow replaced the IDE entirely. And with a 1M token context window, the entire codebase fits in working memory during every edit.

**Why Opus 4.6:** Any model can write a function. But rethinking a system 7 times — while maintaining consistency across 14,600 lines, understanding imprecise intent from three misspelled words and a screenshot — requires the combination of Terminal-Bench 65.4% (agentic coding), MRCR 76% (long-context retrieval across code), and GDPval-AA +144 Elo (understanding intent from imprecise input).

---

## The Meta-Lesson

Every lesson above shares a common thread: **Opus 4.6 is reliable enough to be trusted with judgment calls, not just execution.**

- Expert agents: the model evaluates ideas through consistent expert personas
- Playwright QC: the model reviews its own output through expert lenses
- Live narration: the model's internal reasoning is presentable to users
- Architecture pivots: the model rethinks the system, not just edits it

For the coding-side capabilities — large codebase navigation, agentic reasoning, self-correction, and intent inference — see [coding.md](coding.md).

The shift from 4.5 to 4.6 isn't "better code generation." It's the difference between a model you supervise and a model you collaborate with.

---

## Sources

- [Claude Opus 4.6 Announcement](https://www.anthropic.com/news/claude-opus-4-6) — Anthropic
- [BigLaw Bench: 90.2%](https://www.anthropic.com/news/claude-opus-4-6#benchmarks) — Expert-level legal reasoning
- [Terminal-Bench 2.0: 65.4%](https://www.anthropic.com/news/claude-opus-4-6#benchmarks) — Agentic coding
- [Adaptive Thinking](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6) — Model-controlled reasoning depth
- FlipSide git history: 89 commits, Feb 10–15, 2026
- FlipSide architecture: `app.py` (3,861 lines), `templates/index.html` (10,748 lines)
---

**Henk van Ess** — [imagewhisperer.org](https://www.imagewhisperer.org) · [searchwhisperer.ai](https://searchwhisperer.ai) · [digitaldigging.org](https://digitaldigging.org)
