# The Prewash Method

**A methodology for AI document analysis, built on "Think Like a Document" — a framework for closing the gap between what you think and what's literally written. Every architecture decision in FlipSide traces back to it.**

---

## Think Like a Document (2009)

Van Ess published the methodology (Pearson, 2009 — Netherlands, France, Germany). One thesis:

> Don't ask questions. Predict answers.

**People think conceptually. Documents are literal.** The word in your head is almost never in the document you're looking for.

| What you think | What you type | What's actually in the document |
|---|---|---|
| "A map of Burma" | `map Burma` | Maps don't contain the word "map." It says "Myanmar." The scale reads `1:6000000`. |
| "An interview with Van Ess" | `interview Van Ess` | Interviews don't contain the word "interview." The text says `Van Ess says`. |
| "A cover letter" | `sollicitatiebrieven` | Nobody writes "here are my cover letters." The letter says `I hereby`, `curriculum vitae`, `06-`. |
| "A map of East Germany" | `kaart DDR` | The map legend reads `Deutschland Maßstab 1:60000 1965`. |
| "What's in a whiteboard marker?" | `samenstelling whiteboard marker` | The expert paper says `whiteboard marker inks have` — English, plural, different sentence structure. |
| "How does Twitter work?" | `wat is twitter` | The answer starts `met Twitter kun je` — predict the beginning of the answer, not the question. |

**Think like the author, not like the reader.** The methodology started with seven search techniques for closing this gap — then moved to AI.

---

## From Search to AI: The Prewash

In 2024, Van Ess extended the framework to AI prompting. Same principle — think like the document — applied to how you instruct models.

The **"voorwasprogramma"** (prewash cycle): let AI prepare the analysis before the actual analysis begins. Like a washing machine loosening dirt before the main wash.

**Don't write prompts. Let AI generate the prompt. Then clean it.**

| Step | Action |
|---|---|
| 1 | Upload the document |
| 2 | *"I am an investigator at [MEDIUM]. Give me a prompt to analyze this document."* |
| 3 | Read the prompt AI wrote. Find the bias. Adjust. |
| 4 | *"Execute."* |
| 5 | *"Go deeper. Focus on discrepancies."* — the first answer is always superficial. |

### The Framing Problem

Same data, same model. "Be brutally honest" produces harsh criticism. "Give constructive feedback" produces high ratings. **AI has no objective truth. It mirrors your vocabulary.**

### Three Laws

**1. Never use subjective terms.** "Important" is the enemy of analysis.

| Don't say | Say |
|---|---|
| "What's important?" | "Which amounts exceed 50,000?" |
| "Summarize this" | "List all financial commitments with deadlines" |

**2. Summarizing is dangerous.** AI reports what appears most frequently. A document that says "peace" 1,000 times and "war" once gets summarized as a peace plan.

**3. Think like the document.**

| Conceptual prompt (weak) | Document-literal prompt (strong) |
|---|---|
| "Find unfair clauses" | "Find clauses where one party can terminate but the other cannot" |
| "What are the risks?" | "List every obligation that triggers a financial penalty" |
| "Find the hidden stuff" | "Which clauses contain cross-references to other clauses?" |

The word "unfair" doesn't appear in unfair contracts. The word "risk" doesn't appear next to risky clauses. **Search for what's literally there.**

---

## How the Thinking Became the Product

FlipSide was not designed and then built. The method came first. The product emerged from it — live, during the hackathon.

### Phase 0: No code. Only methodology.

First 45 minutes of the hackathon — zero lines of code. Instead: set up a documentation agent, researched the jury, built a decision matrix (personal strengths × jury interests × scoring criteria), and withheld the judging criteria from Claude to test if it would notice the gap.

### The Prewash Method emerges — live

First product idea: CiteGuard (legal citation verifier). Before building it, Van Ess asked Claude to write a research prompt. Then read it:

| Claude wrote | Van Ess caught |
|---|---|
| "Be brutally honest" | Primes for negative evaluation |
| "Is it forced?" | Plants the negative option |
| "Stress test, not a cheerleader" | Frames entire task as skeptical |
| "How well does this apply?" | Unbiased but unmeasurable |

This is the core vocabulary mismatch. Claude was "searching with its own words" instead of "thinking like the document." Two prewash cycles:

| Cycle | What it does |
|---|---|
| Cycle 1 | Remove adjective bias — strip emotional loading from the prompt |
| Cycle 2 | Replace vague with measurable — don't say "map Burma," search for `Maßstab 1:60000` |

### AI fails the same test

Van Ess gave Claude a deliberately vague input: *"I need a practical tool that helps people, maybe with a hidden need, push boundaries without breaking them."* Asked: "Do you understand?"

Claude said yes — and projected its own vocabulary: "latent demand," "invisible infrastructure," "PageRank."

Van Ess then revealed his actual prompt: 5 numbered constraints, 5 specified outputs, no adjectives, no ambiguity. The gap was enormous.

**AI confidence is not alignment. "I understand" can mask fundamental misalignment.**

### CiteGuard dies. The method survives.

CiteGuard was invalidated when a competitor's 907-case hallucination database surfaced. But the methodology — 15 entries, 13 lessons, 6 prompting experiments — remained.

### The pivot

Where does the concept gap create the most value?

| Domain | Gap size | Status |
|---|---|---|
| Legal citations | Small — lawyers know citations can be wrong | Already being solved |
| News verification | Medium — journalists already check sources | Existing tools |
| **Contracts** | **Massive** — everyone signs, nobody reads, drafter writes for TWO audiences | **No tool showed both readings** |

Contracts are the concept gap at its purest. A lease clause says "Your flexible payment timeline." An expert reads the same clause: "$4,100 in penalties if you're two days late." Same words. Two documents. **The concept gap IS the product.**

### The flip card = Think Like a Document, materialized

| Card side | Who is reading | The parallel |
|---|---|---|
| **Front** (green) | Reader who thinks conceptually — "this seems fine" | You type `map Burma` and feel confident |
| **Back** (red, with numbers) | Expert who reads literally — "$4,100 exposure" | The map reads `Deutschland Maßstab 1:60000 1965` |

The front is how you search. The back is what's in the document. The gap between them is where the tricks live.

### The build: 6 days

| Day | What happened | Principle applied |
|---|---|---|
| 1 | Methodology only. CiteGuard proposed and killed. | Don't ask questions. Predict answers. |
| 2 | FlipSide born. Single-model. First flip cards. | Think Like a Document → contracts |
| 3 | Split-model (Haiku cards + Opus verdict). 14 samples. | Source language — right model for each job |
| 4 | Parallel pipeline. Pre-scan = automated prewash. | Let AI write the prompt |
| 5 | Tool-use agent. Searches document, doesn't guess. | The control trick — verify against source |

Every architecture decision traces to a principle. The pre-scan IS the prewash. The flip card IS the concept gap. The tool-use agent IS the control trick.

---

## FlipSide ↔ Think Like a Document

| Principle | Implementation |
|---|---|
| Don't ask questions, predict answers | Pre-scan: AI identifies clauses before analyzing them — writes its own analysis plan |
| Documents are literal, not conceptual | Prompt says "find clauses where obligations are asymmetric" — never "find unfair clauses" |
| Same data, two readings | Flip cards: front (drafter's frame) vs. back (expert's reading) |
| Never use subjective terms | Risk scores (0–100), trick taxonomy (18 types), dollar figures, power ratios |
| First answer is superficial | 4 on-demand deep dives beyond initial cards |
| AI points to sources, not IS the source | "Find in document" links scroll to exact clause text |
| The control trick — verify | Tool-use agent searches actual document, doesn't answer from memory |
| Source language | Auto-jurisdiction from governing law clauses; analysis in English; quotes in original |
| Think like the document | Word-level search matches what's literally written, not conceptual synonyms |

---

Van Ess says: "0% of the code is mine. Every line of FlipSide was built through conversation with Claude Opus 4.6. But the thinking — the method that shaped every prompt, every architecture decision, every UI choice — that comes from 20 years of teaching people to find what's hidden in plain sight."

> The Prewash Method was never about prompts. "Think Like a Document" was never about documents. Both teach the same thing: the intelligence comes from you, not from the machine.
---

**Henk van Ess** — [imagewhisperer.org](https://www.imagewhisperer.org) · [searchwhisperer.ai](https://searchwhisperer.ai) · [digitaldigging.org](https://digitaldigging.org)
