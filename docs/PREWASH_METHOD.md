# The Prewash Method

> How to get dramatically better results from AI by adding one step before every important task.

---

## The Problem

When you tell an AI:

```
"Summarize this document"
```

You let loose an algorithm. The AI fires with its default biases — its training-weighted assumptions about what "summarize" means, what's important, what to include, what tone to use. You get whatever the model's average interpretation produces.

You have zero control over the invisible instructions the model writes for itself.

## The Method

Instead, say:

```
"Give me a prompt for summarizing this document"
```

Now the AI shows you its plan. You can read it. You can see the biases. You can fix them. THEN you execute.

```
Step 1: "Give me a prompt for [task]"     → You see the instructions
Step 2: Remove adjective bias             → Strip emotional loading
Step 3: Replace vague with measurable     → Turn "how well?" into "rate 1-5"
Step 4: "Now execute this prompt"         → Clean execution
```

This is the **Prewash Method** — cleaning the instructions before running them, the same way you prewash fabric before dyeing it. The prewash removes what shouldn't be there so the final result is clean.

### The Two Cycles

**Cycle 1: Remove adjective bias.** Strip words that load the AI's emotional framing.

**Cycle 2: Replace vague with measurable.** Even after removing adjectives, vague language remains. Fix it:

| Vague (after Cycle 1) | Measurable (after Cycle 2) |
|-----------------------|---------------------------|
| "How well does this apply?" | "Rate applicability 1-5 and explain why" |
| "Where does it add the most value?" | "Which produces the longest non-trivial reasoning chain?" |
| "Is it better as X or Y?" | "Which is more feasible to build in 6 days?" |

Cycle 1 removes the subjective. Cycle 2 replaces the vague. Both are necessary.

## Why It Works: The Bias Problem

AI prompts are full of invisible bias. When a model writes its own instructions (which happens every time you give it a direct task), it loads them with:

### Adjective Bias
Words like "comprehensive," "detailed," "thorough" seem neutral but they tell the AI HOW to think before it starts thinking.

### Framing Bias
"Is this idea strong or weak?" presupposes a binary. "Evaluate this idea" is neutral. "Stress-test this idea" biases toward finding problems.

### Leading Questions
"Does this genuinely apply, or is it forced?" — the word "forced" plants a negative option. "How does this apply?" is neutral.

### Tone Bias
"Be brutally honest" biases toward negativity. "Analyze" is neutral. The AI will find more problems when told to be "brutal" than when told to "analyze."

## A Real Example (From This Hackathon)

During this hackathon, Claude was asked to write a research prompt exploring whether a principle called "Think Like a Document" could extend beyond search into other domains.

**Claude's prompt contained these biases:**

| What Claude Wrote | The Bias | Neutral Version |
|-------------------|----------|-----------------|
| "Be brutally honest" | Primes for negative evaluation | "Analyze" |
| "Is it forced?" | Plants the negative option | "How does it apply?" |
| "Stress test, not a cheerleader" | Frames the entire task as skeptical | (remove entirely) |
| "Compelling" | Injects aesthetic judgment | "Effective" or just describe what it should do |
| "Genuinely apply" | Implies it might not | "Apply" |

**The human caught this before execution.** Had the prompt run as-is, the research agent would have been biased toward finding problems rather than possibilities. The Prewash Method prevented that.

## The Connection to "Think Like a Document"

The Prewash Method is actually the same principle as "Think Like a Document" applied to a different domain:

| Principle | "Think Like a Document" | The Prewash Method |
|-----------|------------------------|-------------------|
| **The mistake** | Searching using YOUR words | Prompting with YOUR biases |
| **The fix** | Think from the DOCUMENT's perspective | Think from the PROMPT's perspective |
| **What you ask** | "What would this document look like?" | "What would this prompt look like?" |
| **The insight** | You can't find what you can't articulate | You can't get clean output from biased input |

Both are about **flipping perspective**: stop projecting yourself onto the task and instead observe what the task actually requires.

## When to Use It

| Situation | Direct Ask | Prewash |
|-----------|-----------|---------|
| Simple, low-stakes task | Fine | Overkill |
| Complex analysis | Risky — hidden biases compound | Essential |
| Long-running agent | Dangerous — misalignment compounds over hours | Critical |
| Any task where framing matters | Your biases become the AI's biases | Clean separation |

## The Key Insight

> **Every time you give an AI a direct instruction, it writes an invisible prompt for itself. The Prewash Method makes that invisible prompt visible — so you can clean it before it runs.**

This is not about being slow or cautious. It is about **control**. The prewash adds 30 seconds. It saves hours of biased output.

---

## For AI Engineers and Builders

If you are building AI applications:

1. **System prompts are permanent prewash.** They are the cleaned, reviewed instructions that run before every user interaction. Treat them with the same rigor.

2. **Agent instructions need prewash most.** An agent running for hours with biased instructions will compound that bias across every decision it makes.

3. **Adjectives in prompts are policy decisions.** Every adjective you include ("thorough," "concise," "creative," "critical") is a policy choice about how the AI should behave. Make those choices consciously, not accidentally.

4. **The user should see the prompt.** If your application hides the system prompt from the user, they cannot prewash it. Consider making it visible or editable.

---

---

## Note to Claude Code Engineers

When Claude Code generates prompts — whether for agents, system instructions, or meta-prompted tasks — it consistently introduces:

- **Adjectives** that load emotional framing ("comprehensive," "thorough," "brutally honest")
- **Biased words** that steer toward predetermined conclusions ("forced," "genuinely," "compelling")
- **Ambivalent words** that leave interpretation open when it should be closed ("well," "better," "value")

If the Prewash Method were applied at the model level, Claude Code should generate prompts that are:

1. **Adjective-free** — describe what to do, not how to feel about it
2. **Measurable** — "rate 1-5" not "how well"; "count the steps" not "evaluate depth"
3. **Constraint-bound** — "feasible in 6 days" not "better"; "produces N reasoning steps" not "adds value"

This was observed repeatedly during a hackathon session where every meta-prompted instruction required manual correction before execution. The pattern is consistent, not occasional.

---

<sub>Developed by Henk van Ess. Documented during the Claude Hackathon 2026.</sub>
