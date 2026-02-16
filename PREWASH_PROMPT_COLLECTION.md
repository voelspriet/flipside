# Prewash Prompt Collection

**7 prompting patterns behind FlipSide — each maps a "Think Like a Document" principle to a concrete implementation decision.**

---

## 1. The Concept Gap in Prompts

The word "unfair" doesn't appear in unfair contracts. Just like the word "map" doesn't appear on maps.

| Concept in your head | What's literally in the document | How FlipSide prompts it |
|---|---|---|
| "Unfair clause" | Party A can terminate, Party B cannot | "Identify clauses where rights or obligations apply to only one party" |
| "Hidden fee" | "...plus applicable charges as determined from time to time" | "Find clauses where amounts are referenced but not specified" |
| "Risky contract" | Cross-references that compound penalties | "Which clauses reference other clauses, creating cascading obligations?" |
| "Fine print trick" | Definition section redefines common words | "Which definitions in Section 1 alter the plain-English meaning?" |
| "Bad for the tenant" | Landlord may enter "at reasonable times" (undefined) | "List clauses where one party has discretion that the other cannot challenge" |

Every FlipSide prompt avoids the concept word and targets the literal structure.

---

## 2. Think Like the Drafter, Then the Reader

Think Like a Document: pretend you are the writer. What would you write?

FlipSide runs this twice per clause — once as the drafter, once as the expert.

### Card front (drafter's perspective)

> "You are reading from the DRAFTER'S perspective. What would this clause look like to someone who WANTS to sign?"

| Prompt instruction | Output |
|---|---|
| "Write the reassurance headline" | "Your flexible payment timeline" |
| "Write the reader's inner monologue — gullible, never does math, FORBIDDEN from questioning fairness" | "I'd think they're just being organized about when rent is due" |
| "Write the teaser — what the fine print actually says" | "If rent is 5 days late, a $50 fee applies daily" |

### Card back (expert's perspective)

> "Now read the same clause as an expert. What is the drafter's strategic intent? What does the reader NOT see?"

| Prompt instruction | Output |
|---|---|
| "The reveal — what this clause actually does" | "This isn't a late fee. It's a daily penalty that compounds into four figures within two weeks." |
| "The figure — a specific dollar amount, derived from the example math" | "$4,100 in penalties if you're two days late on a $1,500 rent" |
| "The trick — classify from taxonomy" | "Cascade Clause: one trigger activates multiple penalties across sections" |

Same clause. Two readings. The gap between them is the product.

---

## 3. No Subjective Terms

"Important" is banned. "Interesting" is banned. Every evaluation in FlipSide is measurable.

| Subjective (forbidden) | Objective (what FlipSide uses) |
|---|---|
| "Rate how unfair this is" | "Score 0–100: How asymmetric are the rights?" |
| "Is this clause bad?" | "Count: landlord rights vs. tenant rights in this clause" |
| "What should I worry about?" | "List every clause that triggers a financial obligation" |
| "Summarize the risks" | "For each clause: What specific dollar amount is at stake?" |
| "What tricks are used?" | "Classify using this exact taxonomy: Cascade Clause, Silent Rollover, Phantom Option, ..." |

The trick taxonomy (18 constrained types) gives AI a literal vocabulary instead of letting it invent conceptual labels. Output becomes consistent and countable.

---

## 4. The Prewash — Give Me a Prompt, Then Execute

The Prewash Method: instead of telling AI what to do, ask it to write the prompt first. Then read it, fix the bias, and say "execute."

| Step | Action |
|---|---|
| 1 | *"Give me a prompt to analyze this document."* |
| 2 | Read the prompt AI wrote. Find the bias. Adapt it. |
| 3 | *"Execute."* |

FlipSide automates this as the **pre-scan**:

| Step | What happens |
|---|---|
| Pre-scan | Haiku reads the full document. Identifies which clauses deserve analysis. Outputs structured clause list. |
| Clause ID | `CLAUSE: Rent Payment — Section 4.2 — late fees and penalties` |
| Card generation | N parallel Haiku calls — one per clause — full front + back |
| Verdict | Opus reads all cards + original document — cross-validates |

The pre-scan IS the prewash. AI writes its own analysis plan before analyzing.

---

## 5. The First Answer Is Superficial

AI tests whether you'll accept the first pass. FlipSide never does.

| Level | How it pushes deeper |
|---|---|
| Cards | Full front + back with score, trick, figure, example — never a summary |
| Verdict | Opus reads all cards + document — cross-validates the parts |
| Deep dives | 4 on-demand: Scenario Simulator, Walk-Away Number, Hidden Combinations, Negotiation Playbook |
| Ask FlipSide | Tool-use agent that searches the document and does the math — doesn't answer from memory |

When you ask "What happens if I'm 3 months late on rent?", the agent doesn't guess:

| Tool call | What it does |
|---|---|
| `search_document("late payment")` | Finds the actual clause text |
| `get_clause_analysis(1)` | Retrieves the flip card for that clause |
| `get_clause_analysis(4)` | Retrieves the termination clause |
| Final answer | "$12,300. The late fees alone exceed the unpaid rent." |

Three tool calls, one answer. Verified against the source, not generated from memory.

---

## 6. Source Language

`temperature` gives 160M results. `temperatuur` gives 3.9M. Use the language that produces the best analysis.

| Principle | Implementation |
|---|---|
| Detect the source language | Auto-jurisdiction from governing law clauses and addresses |
| Analyze in the expert language | All analysis in English |
| Preserve the source | Quotes in original language with EN translations |
| Give it back | "Report in [language]" download for non-English docs |

---

## 7. The Control Trick — Verify

Verify: search for your answer alongside the subject. If 4 sources confirm, it's reliable.

FlipSide builds verification into every layer:

| Layer | Mechanism |
|---|---|
| Figure ↔ Example | Prompt rule: "FIGURE must be derivable from EXAMPLE math" — no invented numbers |
| Source links | Every card links to exact clause text — user can verify |
| Confidence scores | Each card self-reports confidence level |
| Tool-use verification | Ask FlipSide agent searches actual document — doesn't answer from memory |
| Count accuracy | Nav bar counts risks from parsed cards, not LLM-reported numbers |

---

## Prompt Function Map

| Function | Principle | What it does |
|---|---|---|
| `build_clause_id_prompt()` | The prewash | Pre-scans document, identifies clauses to analyze |
| `build_single_card_system()` | Think like drafter, then reader | Full flip card: front (reassurance) + back (reveal) |
| `build_verdict_prompt()` | Verify against source | Single Opus pass: tier, power ratio, risks, jurisdiction |
| `build_scenario_prompt()` | Ranges, not single answers | "What if 30/60/90 days late?" |
| `build_walkaway_prompt()` | Predict the answer — with math | Maximum financial exposure |
| `build_combinations_prompt()` | Think like the document | Clauses that interact with each other |
| `build_playbook_prompt()` | Don't ask, predict | The negotiation script you'd actually use |
| `build_followup_prompt()` | Search, don't guess | Agent with document search + card retrieval |

---

> "In 2009 I wrote a book to teach that the intelligence comes from you, not from the search engine. In 2026 I built FlipSide to prove the same thing about AI. The machine changed. The principle didn't."
> — Henk van Ess
---

**Henk van Ess** — [imagewhisperer.org](https://www.imagewhisperer.org) · [searchwhisperer.ai](https://searchwhisperer.ai) · [digitaldigging.org](https://digitaldigging.org)
