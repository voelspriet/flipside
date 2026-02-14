# 5 New Ideas: Making Opus 4.6 Shine in FlipSide

Based on capabilities from the [Opus 4.6 announcement](https://www.anthropic.com/news/claude-opus-4-6) that FlipSide doesn't yet exploit.

---

## 1. Agent Teams — Threads That Talk to Each Other

**The capability:** Opus 4.6 introduces "agent teams" — multiple agents that work in parallel and coordinate autonomously, each owning its piece of the task and communicating with the others.

**What FlipSide does now:** 4 Opus threads run independently. The interactions thread doesn't know what the archaeology thread found. The asymmetry thread can't tell the overall thread "this document is unusually one-sided — flag it harder."

**The idea:** Make the 4 verdict threads into an agent team. After each thread finishes its first pass, it publishes key findings to a shared brief. Then each thread gets a second, short pass where it can incorporate the others' discoveries:

- **Interactions** finds Clause 12 + Clause 47 create a compound trap → shares this with **Asymmetry**, which checks whether the power ratio is even worse when those clauses combine
- **Archaeology** identifies that Section 8 is heavily customized → shares this with **Interactions**, which prioritizes cross-references involving Section 8
- **Overall** receives all three threads' summaries and writes a synthesis that references their specific findings instead of working from scratch

**Why it matters:** Currently each thread works in isolation. Agent teams would produce a verdict that reads like four experts who actually talked to each other — not four separate reports stapled together. The verdict column becomes a conversation between specialists, not parallel monologues.

**What the user sees:** A verdict where the Overall Assessment says "The archaeology team flagged Section 8 as heavily customized — and the interactions team found that's exactly where the compound traps are concentrated. This is not a coincidence." Cross-references between sections. A coordinated rather than redundant analysis.

---

## 2. 128K Output Tokens — The Exhaustive Deep Dive

**The capability:** Opus 4.6 supports **128K output tokens** — enabling "larger-output tasks without breaking them into multiple requests."

**What FlipSide does now:** Each Opus thread is capped at 16K–64K tokens depending on depth preset. Long documents get compressed analysis. The counter-draft rewrites clauses one at a time.

**The idea:** A new "Forensic Mode" that produces a book-length analysis of a single document. Instead of a verdict summary, the user gets:

- **Complete clause-by-clause walkthrough** — every clause analyzed, not just the flagged ones. Green clauses get a sentence explaining why they're fair. Yellow/Red clauses get the full treatment.
- **Cross-reference matrix** — every pair of clauses that interact, including benign interactions ("Clause 3 defines a term used correctly in Clause 17")
- **Full counter-draft** — the entire document rewritten with fair alternatives, not just the flagged clauses. Produced in a single pass so Opus can maintain consistency across the full rewrite.
- **Negotiation playbook** — for each unfair clause: what to ask for, what the drafter will likely counter with, and what your walk-away point should be

**Why it matters:** Current token limits force the analysis to be selective — only flagging the worst clauses. With 128K output, Opus can be exhaustive. Some users (buying a house, signing an employment contract) want to understand *everything*, not just the traps.

**What the user sees:** A "Forensic Mode" toggle that warns "This will take 2–3 minutes and produce a 30+ page analysis" — then delivers a document that could replace a $500/hour attorney review.

---

## 3. BigLaw Bench Legal Reasoning — Jurisdiction-Aware Analysis

**The capability:** Opus 4.6 scores **90.2% on BigLaw Bench** with 40% perfect scores — demonstrating expert-level legal reasoning across practice areas.

**What FlipSide does now:** Analysis is jurisdiction-agnostic. A California lease and a Texas lease get the same treatment. The counter-draft suggests fair alternatives without knowing which are legally required in the user's jurisdiction.

**The idea:** Add a jurisdiction selector (US state, EU country, or "I don't know"). Then leverage Opus's legal reasoning to:

- **Flag clauses that violate local law** — "This late fee exceeds the 5% statutory maximum in California (Civil Code §1671)" or "This non-compete is unenforceable in the Netherlands under Dutch labor law"
- **Distinguish unenforceable from merely unfair** — some clauses are bad but legal; others are actually void. The user should know the difference.
- **Generate jurisdiction-specific counter-drafts** — rewrite clauses to match what local law actually requires, citing specific statutes
- **Warn about missing required clauses** — "California leases must include [X] disclosure. This lease doesn't."

**Why it matters:** The difference between "this clause is unfair" and "this clause is illegal in your jurisdiction" is the difference between "maybe I should negotiate" and "I have legal standing." Opus 4.6's BigLaw Bench performance suggests it can make this distinction reliably.

**What the user sees:** A jurisdiction badge next to each flagged clause: "Unfair" (yellow), "Potentially Unenforceable" (orange), or "Violates [Statute]" (red with citation). The counter-draft cites actual law.

---

## 4. BrowseComp — Real-World Cross-Referencing

**The capability:** Opus 4.6 leads all frontier models on **BrowseComp**, an evaluation of the ability to locate hard-to-find information — suggesting strong retrieval and synthesis across diverse sources.

**The idea:** After FlipSide analyzes a document, offer a "Real-World Check" that uses Opus to generate targeted research queries, then cross-references findings:

- **Enforcement history** — "Companies using this exact arbitration clause structure have faced [N] consumer complaints with the CFPB"
- **Industry comparison** — "This gym's cancellation clause is more restrictive than 3 of 4 major chains' published policies"
- **Regulatory context** — "The FTC issued guidance in 2025 specifically targeting the 'negative option' renewal pattern used in Clause 7"
- **Court precedent signals** — "Clauses with this structure have been challenged in [State] courts — [outcome]"

**Why it matters:** FlipSide currently analyzes documents in isolation. But the user's real question is often: "Is this normal? Has anyone fought this? What happened?" BrowseComp performance suggests Opus can connect document clauses to real-world outcomes — turning analysis into actionable intelligence.

**What the user sees:** A "Check the record" button on each red-flagged clause. Opus returns 2–3 real-world data points with sources. The user goes from "this clause seems unfair" to "this clause has been struck down in court" or "the FTC says this is deceptive."

---

## 5. Life Sciences Expertise — Medical Document Deep Analysis

**The capability:** Opus 4.6 is **almost 2× better than Opus 4.5 on computational biology, structural biology, organic chemistry, and phylogenetics** — a dramatic improvement in scientific reasoning.

**What FlipSide does now:** Medical consent forms are one of the 14 sample documents. But the analysis treats them like any other contract — focusing on legal tricks (liability waivers, arbitration clauses) without understanding the medical content.

**The idea:** When FlipSide detects a medical document (consent form, clinical trial agreement, insurance coverage details), activate a specialized medical analysis layer:

- **Informed consent audit** — Does the document actually explain the risks in terms a patient can understand? Are known complications listed? Are alternatives mentioned? Compare against published informed consent standards.
- **Coverage gap analysis** — For insurance policies covering medical procedures: cross-reference the exclusions against common complications of the covered procedures. "This policy covers knee replacement surgery but excludes 'post-surgical infection treatment beyond 30 days' — yet 12% of knee replacements develop infections requiring longer treatment."
- **Clinical trial red flags** — For research consent forms: check whether compensation for adverse events is adequate, whether the withdrawal clause is truly voluntary, whether data usage extends beyond the stated purpose.
- **Drug interaction with contract terms** — "This anesthesia consent form asks you to confirm you've fasted for 8 hours, but the pre-op instructions sent separately say 6 hours. Which applies?"

**Why it matters:** Medical documents are where the stakes are highest and the power asymmetry is greatest. A patient signing a surgical consent form at 6 AM on the morning of surgery is not reading carefully. Opus 4.6's scientific expertise means FlipSide can catch not just legal tricks but *medical* gaps — risks the document should disclose but doesn't, coverage that sounds comprehensive but has scientifically predictable holes.

**What the user sees:** Medical documents get an additional "Clinical Review" section in the verdict with a stethoscope icon. Findings like: "This consent form lists 4 risks for this procedure. Published literature identifies 7 significant risks. Missing: [list]. Ask your surgeon about these before signing."

---

## Implementation Priority

| Idea | Effort | Impact | Dependencies |
| --- | --- | --- | --- |
| 1. Agent Teams | High — requires inter-thread messaging | High — verdict quality step-change | Agent teams API access |
| 2. 128K Output | Low — raise token caps, add mode toggle | Medium — niche but high-value users | None (API supports it now) |
| 3. Jurisdiction-Aware | Medium — add selector, update prompts | Very High — transforms actionability | BigLaw Bench-level reliability |
| 4. Real-World Check | Medium — needs web search integration | Very High — connects analysis to reality | Web search API or tool use |
| 5. Medical Deep Analysis | Medium — add document type detection, specialized prompts | High — highest-stakes documents | Life sciences reasoning reliability |

**Recommended order:** 3 → 2 → 5 → 1 → 4. Jurisdiction awareness has the highest impact-to-effort ratio and requires no new API capabilities. 128K output is a quick win. Medical analysis leverages an existing sample document. Agent teams and real-world checking need new infrastructure.
