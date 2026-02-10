# Decision Matrix — Project Selection

> All three inputs converged: Strengths + Jury (corrected) + Criteria

---

## The Three Inputs

| Input | Key Finding |
|-------|------------|
| **Strengths** | 731-document hallucination corpus (unique worldwide), 25+ forensic methods in production, CHI 2026 paper, 20+ years OSINT, multi-LLM orchestration |
| **Jury** | 5 builders/entrepreneurs. Boris (agentic tools, latent demand), Cat (prototypes over docs), Thariq (serial entrepreneur, gaming+philosophy, NOT civic tech), Ado (teachable/tutorial-worthy), Jason (9 languages, community stories) |
| **Criteria** | Demo 30%, Opus 4.6 Use 25%, Impact 25%, Depth 20%. Special prizes: "Keep Thinking" + "Most Creative Opus 4.6 Exploration" |

---

## Four Ideas Scored Against ALL THREE Inputs

### Scoring: Jury Fit (corrected profiles)

| Judge | CiteGuard | DeepVerify | ElectionShield | SearchForTruth |
|-------|-----------|------------|----------------|----------------|
| **Boris** (agentic, latent demand, multi-instance) | 9 — Multi-step agentic reasoning loop, solves a "latent demand" problem | 8 — Orchestrates many tools, but integration complexity may show cracks | 7 — Uses existing methods, less novel agent design | 8 — Deep strategic reasoning, but less agentic |
| **Cat** (prototypes, clear users, organic pull) | 9 — Clear user (lawyers/courts), clear problem, pulls organically | 7 — Broad scope = less clear product story | 8 — Clear user (journalists/election officials) | 7 — User is "journalists" but workflow is abstract |
| **Thariq** (entrepreneur, moat, novel AI, gaming) | 9 — Unique dataset = moat, novel AI application, PubPub = info integrity | 8 — Impressive tech stack, but less unique angle | 7 — Many teams will do election/deepfake | 8 — CHI paper is strong, but less builder-exciting |
| **Ado** (teachable, tutorial-worthy, community) | 9 — "Build a legal citation checker with Opus 4.6" = great tutorial | 7 — Too complex to teach in one blog post | 8 — Deepfake detection is popular topic | 8 — Search methodology is teachable |
| **Jason** (story, community narrative, multilingual) | 10 — "731 cases of AI lying in court" = headline. Multi-jurisdiction = his multilingual lens | 8 — Good story but harder to distill | 9 — "Defend democracy" is strong narrative | 7 — Harder to make into a headline |
| **Jury Total** | **46/50** | **38/50** | **39/50** | **38/50** |

### Scoring: Criteria Fit

| Criterion (weight) | CiteGuard | DeepVerify | ElectionShield | SearchForTruth |
|--------------------|-----------|------------|----------------|----------------|
| **Demo (30%)** | 8 — Extended thinking visible, dramatic reveal of fake citations. Text-based but the reasoning IS the show | 9 — Multi-layer visuals, image + text + context | 9 — Deepfake video unmasking is spectacular | 6 — Strategy generation is intellectual, less visual |
| **Opus 4.6 Use (25%)** | 10 — Extended thinking IS the core feature. 10+ reasoning steps per citation. Cannot work with lesser model | 9 — Synthesis across layers uses extended thinking well | 7 — Opus orchestrates existing methods, less novel | 9 — Deep strategic reasoning, iterative refinement |
| **Impact (25%)** | 9 — 75.5% fabricated citations, 493 discipline cases, affects justice systems in 15+ countries | 9 — Fights disinformation across all media types | 9 — Election integrity, affects democracy | 7 — Helps journalists but narrower audience |
| **Depth (20%)** | 10 — 731 unique documents, 18 themes, CHI paper, months of research | 8 — Combines many existing methods but less original depth | 7 — Builds on existing forensic methods | 9 — CHI paper + 20yr methodology |
| **Criteria Total** | **9.1** | **8.8** | **8.2** | **7.5** |

### Scoring: Practical Factors

| Factor | CiteGuard | DeepVerify | ElectionShield | SearchForTruth |
|--------|-----------|------------|----------------|----------------|
| **Feasibility (6 days, solo)** | 9 — Focused scope, clear modules | 5 — Massive integration challenge | 6 — Many components to wire up | 8 — SearchWhisperer base exists |
| **Uniqueness (vs other teams)** | 10 — No one has the corpus | 7 — Verification tools exist | 5 — Many teams will try deepfake detection | 7 — Search tools exist |
| **New work rule compliance** | 9 — Corpus is DATA (allowed), tool is new code | 6 — Heavy reuse risk from ImageWhisperer | 6 — Heavy reuse risk from existing detectors | 8 — New tool, SearchWhisperer logic is methodology |
| **Special prize targeting** | Both — "Keep Thinking" (our process) + "Creative Opus 4.6" (extended thinking as core) | "Keep Thinking" only | "Creative Opus 4.6" possible | "Keep Thinking" natural fit |

---

## The Decision Matrix — Final Scores

| | CiteGuard | DeepVerify | ElectionShield | SearchForTruth |
|---|:---------:|:----------:|:--------------:|:--------------:|
| Jury Fit | **46** | 38 | 39 | 38 |
| Criteria Fit | **9.1** | 8.8 | 8.2 | 7.5 |
| Feasibility | **9** | 5 | 6 | 8 |
| Uniqueness | **10** | 7 | 5 | 7 |
| Rule Compliance | **9** | 6 | 6 | 8 |
| Special Prizes | **Both** | 1 | 1 | 1 |

**CiteGuard wins on every dimension.**

---

## Why CiteGuard Specifically

### The Unfair Advantages

1. **The 731-document corpus is a moat.** No other hackathon team has access to this data. It's original research, not scraped from the internet. It's been categorized into 18 themes across 15+ jurisdictions.

2. **Extended thinking IS the product.** For most hackathon projects, AI is a feature. For CiteGuard, the visible reasoning process IS the interface. This is exactly what "capabilities that surprised even us" means.

3. **The story writes itself.** "AI is fabricating legal citations. I documented 731 cases. Now I'm using the most powerful AI to catch the lies AI created." Jason Bigman (9 languages, ex-Reddit community lead) will want to share this story. Ado Kukic will want to write a tutorial. Cat Wu will see a product. Boris will see an agent. Thariq will see a novel application.

4. **Rule-safe.** The corpus is research DATA, not code. The tool itself will be built from scratch during the hackathon. No reuse risk.

5. **Scope is controllable.** Unlike DeepVerify (which needs image+text+context+search), CiteGuard has a clean scope: document in → citations extracted → each verified → report out. This is buildable in 6 days by one person.

### The Risk and Mitigation

| Risk | Mitigation |
|------|-----------|
| Text-based = less visual than image/video demos | The visible extended thinking chain IS the visual. Stream it with good typography. Add a citation heatmap on the document. |
| Legal verification is complex | Scope to pattern-matching against the corpus + web search. Don't try to build a full legal database. |
| API latency with extended thinking | Pre-process some citations for the demo. Show real-time for 2-3 citations, summarize the rest. |
| Solo developer, 6 days | Focused scope. Reuse PATTERNS (SSE streaming, Flask), not CODE. The corpus does the heavy lifting. |

---

## Recommendation

**Build CiteGuard.**

Problem Statement: **"Build a Tool That Should Exist"** (primary) + **"Break the Barriers"** (secondary — democratizing legal citation verification)

Target prizes:
- **Main prize** (1st/2nd/3rd)
- **"Most Creative Opus 4.6 Exploration"** — extended thinking as the core interface
- **"The Keep Thinking Prize"** — our documented iteration process
