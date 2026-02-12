# How FlipSide Showcases Opus 4.6

> Cross-reference with [Anthropic's Opus 4.6 announcement](https://www.anthropic.com/research/introducing-claude-opus-4-6) (Feb 5, 2026)

---

## 1. Adaptive Thinking — The Reasoning IS the Product

**Anthropic says:** "With adaptive thinking, Claude can decide when deeper reasoning would be helpful."

**FlipSide does:** The extended thinking stream is not hidden behind a loading spinner — it IS the interface. Users watch Opus 4.6 adopt the drafter's perspective in real time: "I am now thinking like the insurer's underwriting counsel..." The model decides how deeply to reason per clause, spending more thinking tokens on complex cross-clause interactions and less on standard boilerplate.

**Why this matters for judges:** Most hackathon projects use extended thinking as a black box. FlipSide makes it the product — the visible chain of reasoning is what makes the analysis trustworthy and educational. This is "adaptive" in the truest sense: the model calibrates its own reasoning depth to the complexity of each clause.

**Implementation:** `thinking: {type: 'adaptive'}` — no fixed budget. The model allocates its own thinking tokens. Quick scan (Haiku) handles individual clauses; Opus 4.6 deep analysis handles cross-clause reasoning that requires sustained attention across the full document.

---

## 2. Long-Context Retrieval — Finding Needles in Legal Haystacks

**Anthropic says:** "76% on MRCR v2 8-needle 1M... a qualitative shift in how much context a model can actually use while maintaining peak performance."

**FlipSide does:** Cross-clause interaction detection. Clause 2(c) excludes water damage from "gradual seepage over 14 days." Clause 2(e) defines the inspection timeline at 30 days. Neither clause is dangerous alone. Together, they deny virtually all residential water damage claims — because any damage discovered at the 30-day inspection can be retroactively classified as "gradual."

The model must hold the entire document in working memory, reason across distant clauses simultaneously, and detect compound risks that are invisible when reading linearly. This is exactly the "needle-in-a-haystack" capability that Opus 4.6 was built for — except the needles are legal traps.

**Why this matters for judges:** This isn't a demo of context length. It's a demo of context USE. The model doesn't just store 50 pages — it reasons across them to find interactions the drafter deliberately spread apart.

---

## 3. Low Over-Refusals — The Villain Voice Works

**Anthropic says:** "Opus 4.6 shows the lowest rate of over-refusals — where the model fails to answer benign queries — of any recent Claude model."

**FlipSide does:** Every red-flagged clause includes "IF THE DRAFTER COULD SPEAK AS A VILLAIN" — adversarial role-play where Opus 4.6 adopts the drafter's voice and reveals the strategic intent behind the clause. Example:

> "The math does the work. Two weeks late once and you'll never catch up — every payment feeds the fees, and the rent underneath keeps compounding. And you already waived the right to call it unreasonable."

Previous models would self-censor on this. They'd add disclaimers, soften the language, or refuse the adversarial framing entirely. Opus 4.6's low over-refusal rate means it can do the role-play that makes FlipSide's perspective flip actually work.

**Why this matters for judges:** The villain voice is not a gimmick — it's the core UX mechanism. The contrast between "what you'd think" (front of card) and "what the drafter intended" (back of card) requires the model to fully commit to the adversarial perspective. Over-refusal would destroy the product.

---

## 4. Effort Controls — User-Facing Intelligence Dial

**Anthropic says:** "Four effort levels: low, medium, high (default), max."

**FlipSide does:** The depth selector (Quick / Standard / Deep) maps directly to Opus 4.6's effort parameter. Quick analysis uses lower effort for fast results; Deep analysis uses maximum effort for thorough cross-clause reasoning. Users choose their own intelligence/speed/cost tradeoff.

**Why this matters for judges:** This is a NEW Opus 4.6 feature (not available on previous models) directly exposed in the UI. Users can see the difference: Quick mode returns in 30 seconds with individual clause assessments. Deep mode takes 90+ seconds but finds cross-clause interactions, penalty cascades, and drafter profiling that Quick mode misses.

**Implementation:** `effort` parameter in the API call, mapped to the UI depth selector.

---

## 5. Context Compaction — Follow-Up Without Limits

**Anthropic says:** "Context compaction automatically summarizes and replaces older context when the conversation approaches a configurable threshold."

**FlipSide does:** After the initial analysis, users can ask follow-up questions about the document ("What happens if I'm 3 days late on rent?"). Each follow-up sends the full document + previous analysis as context. Context compaction enables extended Q&A sessions without hitting the context window — the model summarizes prior exchanges while retaining the document and analysis.

**Why this matters for judges:** This turns a one-shot analysis tool into an interactive legal consultation. The user uploads once, then explores. Without compaction, the third or fourth follow-up question would fail. With it, the conversation can continue indefinitely.

---

## Summary: 5 Opus 4.6 Features in One Product

| # | Opus 4.6 Feature | FlipSide Implementation | Why It Matters |
|---|---|---|---|
| 1 | Adaptive thinking | Reasoning streamed as UI, model calibrates depth per clause | Thinking is the product, not overhead |
| 2 | Long-context retrieval | Cross-clause interaction detection across full documents | Finds traps deliberately spread across pages |
| 3 | Low over-refusals | Villain voice adversarial role-play without self-censoring | Enables the perspective flip that IS the product |
| 4 | Effort controls | Quick/Standard/Deep mapped to effort parameter | New 4.6 API feature directly in UI |
| 5 | Context compaction | Multi-turn follow-up Q&A about analyzed documents | Turns one-shot analysis into interactive consultation |

---

*These five capabilities are not bolted on — they are structurally necessary for FlipSide to work. Remove any one and the product degrades: without adaptive thinking, you lose the visible reasoning. Without long-context retrieval, you miss the cross-clause traps. Without low over-refusals, the villain voice dies. Without effort controls, every analysis takes 90 seconds. Without compaction, follow-up questions hit a wall.*
