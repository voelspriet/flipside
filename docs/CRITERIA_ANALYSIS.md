# Judging Criteria — Strategic Analysis

> What the scoring weights actually tell us about what to build.

---

## The Weights, Decoded

```
Demo .............. 30%  ← THE BIGGEST SINGLE FACTOR
Impact ............ 25%
Opus 4.6 Use ...... 25%
Depth & Execution . 20%
```

### What This Means

**Demo is king (30%).** Almost a third of the score is "Is this genuinely cool to watch?" This is NOT "does the code work." It's "does the DEMO impress." Implications:
- Visual output > invisible backend magic
- A polished 3-minute video matters more than elegant architecture
- The tool should produce something **showable** — not just functional
- Live-feeling, real-time interactions score higher than batch processing

**Opus 4.6 Use (25%) — They want to be surprised.** The exact wording: *"Did they surface capabilities that surprised even us?"* This means:
- Don't just use Claude as a chatbot
- Don't just use it for summarization or Q&A
- Find something Opus 4.6 can do that's unexpected or at the edge of its capabilities
- Multi-modal, agentic, tool-use, extended thinking — go deep on what makes 4.6 special

**Impact (25%) — Real-world, not theoretical.** They ask: *"Could this actually become something people use?"* This means:
- Pick a real problem with real users
- Show who benefits and why it matters
- Must fit one of the 3 problem statements
- "Cool tech demo" alone won't score here — needs a clear use case

**Depth & Execution (20%) — Show the craft.** Key phrase: *"Did the team push past their first idea?"* This means:
- Iterate visibly — the "Keep Thinking" special prize reinforces this
- Don't ship the first thing that works
- Sound engineering matters but polish matters more than perfection
- Show evidence of wrestling with the problem

---

## Strategic Implications

### What to Optimize For (in priority order)

1. **A demo that makes people say "wow" (30%)**
   - Visual, interactive, real-time
   - Clear narrative arc in the 3-minute video
   - Show, don't tell

2. **Creative Opus 4.6 usage that surprises Anthropic (25%)**
   - Use agentic capabilities, tool use, extended thinking
   - Chain multiple Claude capabilities together
   - Find an edge case or novel application

3. **A problem real people actually have (25%)**
   - Fits one of the 3 problem statements
   - Has clear beneficiaries
   - Could plausibly become a real product

4. **Evidence of iteration and craft (20%)**
   - Our documentation process already demonstrates this
   - Show architectural decisions, not just final output
   - The HACKATHON_LOG.md itself is evidence of depth

### The Special Prizes Are Bonus Targets

| Prize | How to Target It |
|-------|-----------------|
| **Most Creative Opus 4.6 Exploration** ($5k) | Find an unexpected capability — something 4.6 can do that nobody thought to try |
| **The "Keep Thinking" Prize** ($5k) | Our documented iteration process is ALREADY evidence for this prize |

### Problem Statement Fit

Given the scoring, **Problem Statement 2 ("Break the Barriers")** or **Problem Statement 3 ("Amplify Human Judgment")** likely score highest because:
- They naturally produce visual, demo-able output
- They have clear real-world beneficiaries (Impact score)
- They invite creative AI use beyond simple chat (Opus 4.6 Use score)

Problem Statement 1 ("Build a Tool That Should Exist") is riskier because utility tools are harder to make visually impressive in a 3-minute demo.

---

## The Winning Formula

```
Winning Project =
    Visually impressive demo (30%)
  + Surprising use of Opus 4.6 (25%)
  + Real problem, real users (25%)
  + Visible iteration & craft (20%)
```

**The meta-insight:** Our entire documentation process (meta-prompting, jury research, criteria analysis, deliberate testing of Claude 4.6) already covers 20% of the score (Depth & Execution) before we write a single line of product code. We're not just building a tool — we're building a STORY of building a tool.
