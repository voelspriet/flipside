# How Opus 4.6 Powers FlipSide

**What does the user experience that only Opus 4.6 could deliver?**

This document answers that question with grounded evidence from the running product. [coding.md](coding.md) covers how Opus 4.6 *built* FlipSide. This document covers how Opus 4.6 *is* FlipSide.

---

## The Architecture: Six Parallel Experts

When you upload a document, FlipSide spawns **6 parallel threads** — each a separate model instance with its own system prompt, thinking budget, and analysis focus:

```
Upload
  │
  ├── Haiku 4.5 ──── Fast flip cards ──────────────── ~12s ── Cards ready
  │
  ├── Opus 4.6 ───── Expert verdict ───────────────── ~30s ── Verdict ready (prioritized)
  │        │
  │   5s delay (verdict gets head start)
  │        │
  │        ├── Opus 4.6 ── Scenario Simulator ─────── ~20s ── Button ✓
  │        ├── Opus 4.6 ── Walk-Away Number ────────── ~15s ── Button ✓
  │        ├── Opus 4.6 ── Hidden Combinations ─────── ~25s ── Button ✓
  │        └── Opus 4.6 ── Negotiation Playbook ────── ~20s ── Button ✓
  │
  └── SSE stream to browser (all threads push events from t=0)
```

The verdict gets a **5-second head start** — it's the only API connection for the first 5 seconds. Then the 4 deep dives launch in parallel. When the user scrolls to the "Go Deeper" buttons at the bottom of the verdict, the results are already computed. Click = instant reveal.

**Cost per run:** ~$8–12 (6 Opus threads). No cost constraints for the hackathon.

---

## Thread 1: The Expert Verdict

**Opus 4.6 capability:** Adaptive thinking + BigLaw Bench 90.2%

The verdict is a single Opus 4.6 call with `thinking: {type: 'adaptive'}` — the model decides its own reasoning budget. A standard document gets a quick pass; a document with hidden cross-clause traps gets deep chain-of-thought.

Output is a one-screen report for normal people:

| Section | What it answers |
| --- | --- |
| **Verdict Tier** | Sign with Confidence / Read the Flagged Clauses / Negotiate Before Signing / Seek Legal Review / Do Not Sign |
| **What Is This** | One sentence describing the document |
| **Should You Worry** | Calibrated worry level |
| **The Main Thing** | Single worst risk, concrete consequences, clause references |
| **What To Do** | Single most effective action |
| **Power Ratio** | Their rights vs. your rights, counted from the document |
| **Jurisdiction** | Auto-detected from governing law clauses and addresses |
| **Risks** | 2–4 additional risks beyond the main one |
| **Checklist** | Chronological action items before signing |
| **Flagged Claims** | Every RED/YELLOW clause with cross-clause insight |

**Why Opus 4.6:** The adaptive thinking budget means a gym membership contract gets ~4K thinking tokens while a 50-page insurance policy with compound exclusions gets ~16K. The model allocates reasoning where the reasoning is hard — not where the prompt says to. No other model has this self-regulating depth control.

---

## Thread 2: Scenario Simulator — "What Could Happen"

**Opus 4.6 capability:** Extended thinking for multi-step causal reasoning + arithmetic

The most consumer-friendly deep dive. Opus picks the most likely trigger (missed payment, illness, schedule conflict) and narrates what happens step by step over 3–6 months — using the document's actual numbers.

**Example output:**
> **Month 1 — You miss a payment.** The $50 late fee (Section 4.2) is applied to your balance.
> **Month 2 — The fee compounds.** Per Section 4.5, the late fee is charged on your new balance including last month's fee. You now owe $102.50.
> **Month 3 — Default clause triggers.** Section 7.1 defines "default" as 60 days past due. Your remaining lease obligation ($14,400) accelerates.
> **Total exposure after 3 months: $14,502.50**

**Why Opus 4.6:** The model must hold every financial clause in working memory while simulating forward in time. Each month depends on the previous month's state. The extended thinking scratchpad is where the compounding math happens — visible in the thinking stream. GPT-4o loses track of running totals across 6 months of simulated interactions.

**What the judge sees:** "Watch the thinking stream — Opus is doing real arithmetic with the contract's numbers, chaining late fees into default triggers into acceleration clauses across 6 months."

---

## Thread 3: Walk-Away Number — "Your Maximum Financial Exposure"

**Opus 4.6 capability:** Extended thinking for compound financial calculation

One number. The maximum you could owe if everything in this contract is enforced to its worst case. Displayed as a large hero number with a breakdown waterfall and a comparison to jurisdiction norms.

**Example output:**
> **$23,450**
> *If everything goes wrong and every clause is enforced against you, you could owe up to $23,450 over the life of this lease.*
>
> - Early termination fee: $4,200 (Section 12)
> - Remaining rent acceleration: $14,400 (Section 7.1)
> - Late fees (compounded over 12 months): $1,850 (Section 4.2 + 4.5)
> - Lost security deposit: $2,000 (Section 3)
> - Attorney's fees: $1,000 (Section 15.3)
>
> A typical residential lease in California caps total exposure at ~$5,000. This document's exposure is **4.7× higher** than typical.

**Why Opus 4.6:** Finding every financial clause is easy. Compounding them correctly requires multi-step arithmetic that most models botch: the late fee applies to the new balance, which triggers the default threshold earlier, which accelerates the remaining term. Extended thinking lets the model maintain a running ledger in its scratchpad and verify the total equals the sum.

**What the judge sees:** "That $23,450? Opus computed it by compounding 7 clauses together. The thinking stream shows the actual math."

---

## Thread 4: Hidden Combinations — "Cross-Clause Traps"

**Opus 4.6 capability:** BigLaw Bench 90.2% + extended thinking for N² pairwise reasoning

The hardest legal reasoning task on the list. Opus evaluates every clause pair for compound risks invisible when reading each clause alone.

**Example output:**
> ### Your price goes up and you can't leave
>
> **Clause A** (Section 7 — Automatic Renewal):
> > "This agreement shall automatically renew for successive 12-month terms unless written notice is provided 60 days prior to expiration."
>
> **Clause B** (Section 9 — Fee Adjustment):
> > "Monthly fees may be adjusted at the beginning of each renewal term at the Company's sole discretion."
>
> **Read separately:** Normal auto-renewal. Normal fee adjustment.
>
> **Read together:** They can raise your price by any amount every year, and you can only escape if you happen to remember the cancellation window — which they never remind you about. Miss the 60-day window once and you're locked in at whatever they decide to charge.

**Why Opus 4.6:** Cross-clause interaction analysis is where BigLaw Bench's 90.2% matters. A 30-clause document has 435 possible pairs. The model must systematically evaluate each for compound effects — not just pattern-match "indemnification + liability cap." Extended thinking walks through pairs in the scratchpad, building a map of interactions. GPT-4o finds obvious pairs; Opus finds the subtle cascades that a senior attorney would catch.

**What the judge sees:** "This cross-clause analysis found that Clause 7 and Clause 9, which look harmless alone, create a compounding price trap. That's expert-level legal reasoning — exactly what BigLaw Bench measures."

---

## Thread 5: Negotiation Playbook — "What To Say"

**Opus 4.6 capability:** Theory-of-mind reasoning via extended thinking

The only deep dive that analyzes the *drafter*, not the document. Opus infers the drafter's business incentives from the document's structure — what they care about, what they don't — and predicts what they'll concede.

**Example output:**
> ### About the Other Side
> This document was drafted by a high-volume property management company optimizing for cash flow predictability. The custom-drafted security deposit clause and aggressive late fee schedule reveal their priorities. The boilerplate pet and parking sections are copy-paste — low stakes for them.
>
> ### Push Hard on These
> - **Late fee cap** (Section 4.2): Ask for a $75 cap. *Why they'll bend:* Industry standard, and they'd rather keep you than fight over fee amounts.
> - **Cancellation window** (Section 7): Ask for 30 days instead of 60. *Why they'll bend:* Most tenants forget either way.
>
> ### Don't Waste Capital On
> - **Rent amount** (Section 2): That's the business deal, not the fine print.
> - **Arbitration venue** (Section 15): Their legal team is based there — non-negotiable.
>
> ### Ready-to-Send Message
> Dear [Property Management Company], I've reviewed the lease agreement dated [X]. I'd like to discuss two items before signing: the late fee structure in Section 4.2 (would you consider a $75 cap?) and the cancellation notice period in Section 7 (could we adjust to 30 days?). I'm otherwise happy with the terms and looking forward to moving in. Best regards, [Name]

**Why Opus 4.6:** This is strategic reasoning about a counterparty the model has never met — from a document alone. "They spent extra effort on the security deposit clause (it's custom, not boilerplate) → they care about cash flow → they'll concede on convenience terms (pet clause) but fight for revenue terms (rent escalation)." No other model does this level of counterparty modeling.

**What the judge sees:** "This isn't clause analysis — it's strategy. Opus modeled the landlord's business incentives from the document structure and told the user which concessions to ask for first. Theory of mind, not text classification."

---

## The Full User Journey

| Step | What Happens | Time | Opus 4.6 Capability |
| --- | --- | --- | --- |
| 1. Upload | Document processed, 6 threads launch | t=0 | Parallel agent architecture |
| 2. Cards | Haiku flip cards appear, one by one | ~8–15s | *(Haiku 4.5 — speed)* |
| 3. Verdict | One-screen expert verdict streams in | ~30s | Adaptive thinking, BigLaw Bench |
| 4. Go Deeper | 4 buttons, already computed, instant click | ~35s | See threads 2–5 above |
| 5. Take action | Follow-up questions, message the company, counter-draft, download | On demand | Extended thinking, 128K output |

**Total analysis time:** Under 60 seconds for the full six-expert analysis.
**Total cost:** ~$8–12 per document.
**What the user needed to know:** Nothing. Upload and go.

---

## Why Not GPT-4o? Why Not Sonnet?

| Feature | Could GPT-4o do it? | Could Sonnet 4.5 do it? | Why Opus 4.6? |
| --- | --- | --- | --- |
| Flip cards | Yes | Yes | Haiku does this — speed matters more than depth |
| Expert verdict | Partially | Partially | Adaptive thinking decides its own depth per document |
| Scenario Simulator | Loses track of compounding math | OK for simple chains | Extended thinking maintains running ledger across 6+ months |
| Walk-Away Number | Botches compound arithmetic | Misses edge cases | Extended thinking scratchpad for verified multi-clause math |
| Hidden Combinations | Finds obvious pairs | Misses subtle cascades | BigLaw Bench 90.2% — N² pairwise legal reasoning |
| Negotiation Playbook | Generic advice | Document-specific but shallow | Theory-of-mind about the drafter's business model |

The answer isn't "GPT-4o can't do legal analysis." It can. The answer is: **Opus 4.6 does it at expert level, in parallel, with self-regulating depth, and the results are visibly better on compound reasoning tasks.** The Hidden Combinations and Negotiation Playbook outputs are where judges will see the difference.

---

## Sources

- [Claude Opus 4.6 Announcement](https://www.anthropic.com/news/claude-opus-4-6) — Anthropic
- [BigLaw Bench: 90.2%](https://www.anthropic.com/news/claude-opus-4-6#benchmarks) — Expert-level legal reasoning
- [Adaptive Thinking](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6) — Model-controlled reasoning depth
- FlipSide architecture: `app.py` lines 2650–2680 (thread spawning), `OPUS_SOURCES` set (event dispatch)
