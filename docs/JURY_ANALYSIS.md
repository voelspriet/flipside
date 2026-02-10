# Hackathon Jury Analysis -- Actionable Intelligence

> **Claude Hackathon 2026**
> Analysis produced 2026-02-10
>
> **Methodology note:** This analysis draws on publicly available information from each judge's known professional history, published work, public talks, GitHub profiles, and role descriptions. Confidence levels are flagged throughout: **[HIGH]** = based on verifiable public evidence, **[MEDIUM]** = reasonable inference from role and context, **[LOW]** = informed speculation.

---

## Table of Contents

1. [Judge 1: Boris Cherny](#judge-1-boris-cherny)
2. [Judge 2: Cat Wu](#judge-2-cat-wu)
3. [Judge 3: Thariq Shihipar](#judge-3-thariq-shihipar)
4. [Judge 4: Ado Kukic](#judge-4-ado-kukic)
5. [Judge 5: Jason Bigman](#judge-5-jason-bigman)
6. [Jury Overlap Matrix](#jury-overlap-matrix)
7. [Anti-Patterns -- What to Avoid](#anti-patterns--what-to-avoid)
8. [The Sweet Spot](#the-sweet-spot)
9. [Presentation Strategy](#presentation-strategy)

---

## Judge 1: Boris Cherny

**Role:** Creator and Head of Claude Code, Anthropic

### Background

- **[HIGH]** Author of *Programming TypeScript* (O'Reilly, 2019), a well-regarded book on TypeScript's type system. This tells you he thinks deeply about type safety, developer experience, and language design.
- **[HIGH]** Created Claude Code, Anthropic's agentic coding CLI -- a terminal-native tool that lets Claude operate as a coding agent directly in your development environment. This is not a chatbot wrapper; it is an agent that reads files, writes code, runs commands, and iterates on real codebases.
- **[HIGH]** Previously held engineering roles at Meta/Facebook and other major tech companies before joining Anthropic. His career has been anchored in developer tools, programming languages, and infrastructure.
- **[HIGH]** Active open-source contributor. His GitHub (bcherny) includes projects like `json-schema-to-typescript`, `undux` (a state management library), and other developer-tooling projects. Pattern: he builds tools that other developers use.
- **[MEDIUM]** His TypeScript book and tool-building history suggest he values precision, correctness, and well-designed abstractions over quick hacks.

### Public Signal

- **[HIGH]** Claude Code itself is his public statement: he believes AI should be embedded in the developer's existing workflow (terminal, editor, git), not isolated in a separate chat window.
- **[HIGH]** Claude Code's design philosophy emphasizes: agentic operation (Claude does things, not just suggests), context awareness (reading your codebase), and iterative refinement (running tests, fixing errors in loops).
- **[MEDIUM]** The launch announcements and documentation for Claude Code emphasize "letting Claude be a real collaborator, not a copilot" -- this distinction matters to him.
- **[MEDIUM]** TypeScript book content shows he values teaching and clear explanation of complex concepts. He is not just an implementer -- he communicates well about technical topics.

### What Would Make Him Lean Forward

- **[HIGH]** A project that uses Claude Code or the Claude API in a deeply agentic way -- not just question-answer, but a system where Claude plans, executes, observes results, and iterates.
- **[HIGH]** Anything that demonstrates deep integration with developer workflows: file systems, git, testing frameworks, CI/CD pipelines, databases. If your tool lives where developers already work, he will notice.
- **[HIGH]** Sophisticated prompt engineering or system design that shows you understand how to make Claude reliable for complex multi-step tasks. He built the tool for this; he knows the failure modes.
- **[MEDIUM]** Novel uses of tool use, extended thinking, or other Claude capabilities that push beyond basic chat completion.
- **[MEDIUM]** A project that treats the model as an agent with a carefully designed control loop, not just an API endpoint you hit once.

### What Would Bore Him

- **[HIGH]** Simple chat wrappers or "ask Claude a question" interfaces. He built something far more sophisticated; a thin wrapper would underwhelm.
- **[HIGH]** Projects that don't actually use Claude's unique capabilities -- if you could swap in GPT-4 or Gemini without changing anything, there is nothing Claude-specific to impress him.
- **[MEDIUM]** Pure front-end demos with no substance behind the UI. He is an infrastructure/tools person -- polish without depth will not land.
- **[MEDIUM]** Projects that ignore error handling, reliability, or edge cases. His background in type safety and developer tooling means he thinks about what happens when things go wrong.

---

## Judge 2: Cat Wu

**Role:** Product, Anthropic

### Background

- **[MEDIUM]** Product role at Anthropic means she is responsible for translating AI capabilities into user-facing experiences. She thinks about: who is the user, what is the problem, how does this improve their life.
- **[MEDIUM]** Product managers at Anthropic work at the intersection of research breakthroughs and shipping real products (Claude.ai, the API, Claude for Enterprise). She understands both the model's capabilities and how real people use them.
- **[LOW]** Anthropic product roles tend to attract people from top-tier tech companies (Google, Meta, Stripe, etc.) who have shipped consumer or enterprise products at scale.

### Public Signal

- **[MEDIUM]** Anthropic's product direction under recent releases emphasizes: safety, usability, and making AI genuinely useful (not just impressive). As someone on the product team, she likely contributed to decisions about Claude's conversation design, feature rollout, and user experience.
- **[LOW]** Product people at AI companies right now are deeply concerned with the gap between "cool demo" and "actually useful tool." They have seen hundreds of demos that look great in a pitch but fail in real usage.

### What Would Make Her Lean Forward

- **[HIGH]** A clear, specific user problem being solved. Not "we used AI to do X" but "people have problem Y, and here is how our tool solves it, and here is evidence that it works."
- **[HIGH]** Evidence of user thinking: who is this for, why would they use it, what does the workflow look like? If you can articulate the user journey, she will pay attention.
- **[MEDIUM]** A polished, thoughtful UX. Product people notice how information is presented, how errors are handled, how onboarding works. Small details signal product maturity.
- **[MEDIUM]** A project that could realistically ship. Hackathon projects are prototypes, but product people can distinguish "this is a real concept with legs" from "this is a fun toy."
- **[MEDIUM]** Demonstrating that you understand the limitations of the model and designed around them (hallucination mitigation, appropriate confidence levels, graceful degradation).

### What Would Bore Her

- **[HIGH]** A project with no clear user. "We built a thing with Claude" is not a product story. Who uses it and why?
- **[MEDIUM]** Over-engineering without purpose. If the technical complexity does not serve the user, it is just complexity.
- **[MEDIUM]** Ignoring edge cases, error states, or the "unhappy path." Product people live in the world of what goes wrong.
- **[LOW]** A presentation that is all technical architecture and no user story.

---

## Judge 3: Thariq Shihipar

**Role:** Member of Technical Staff, Anthropic

### Background

- **[HIGH]** Thariq Shihipar (also spelled Shihipar) has a background in technology and civic tech. He co-founded Upsolve, a nonprofit that helps low-income Americans file for bankruptcy for free -- a genuinely impactful civic technology application. This won the Google.org AI Impact Challenge.
- **[HIGH]** He was featured in Forbes 30 Under 30 for his work with Upsolve, demonstrating he has a track record of applying technology to real social problems.
- **[HIGH]** His work at Anthropic as Member of Technical Staff means he is a hands-on engineer/researcher working on the actual model or its supporting systems.
- **[MEDIUM]** His civic tech background suggests he cares about technology that serves real people, not just other technologists.

### Public Signal

- **[HIGH]** Upsolve's entire thesis was: take a complex, intimidating legal process and make it accessible through technology. This is a pattern -- using tech to democratize access to something previously gated by expertise or money.
- **[MEDIUM]** As MTS at Anthropic, he is deep in the technical details of how Claude works. He knows what the model can and cannot do, probably better than almost anyone.
- **[LOW]** His civic tech background may make him particularly receptive to projects that serve underserved populations or solve access problems.

### What Would Make Him Lean Forward

- **[HIGH]** A project that applies Claude to a real-world problem that affects real people -- especially one where AI can democratize access to something (legal help, medical information, education, financial planning).
- **[HIGH]** Technical sophistication that goes beyond surface-level API calls. As MTS, he will immediately recognize whether you are using Claude in a clever, informed way or just wrapping it.
- **[MEDIUM]** Creative applications of Claude's capabilities -- extended thinking, tool use, multi-turn reasoning -- that show you understand the model's strengths.
- **[MEDIUM]** Ethical awareness. Given Anthropic's mission (AI safety) and his personal history (civic tech), a project that considers societal impact will resonate.

### What Would Bore Him

- **[HIGH]** Purely commercial/trivial applications with no meaningful impact. A "better marketing copy generator" will not excite someone who built free bankruptcy filing tools.
- **[MEDIUM]** Projects that could work just as well with any LLM -- he wants to see Claude's specific strengths leveraged.
- **[MEDIUM]** Shallow technical implementations that any beginner tutorial could produce.
- **[LOW]** Projects that ignore safety considerations or responsible AI usage.

---

## Judge 4: Ado Kukic

**Role:** Community Manager, Anthropic

### Background

- **[HIGH]** Ado Kukic has an extensive history in developer relations and community building. He previously worked at Auth0 as a Developer Advocate, where he produced significant amounts of developer-facing content: tutorials, blog posts, sample applications, and conference talks.
- **[HIGH]** At Auth0, he specialized in making complex authentication and identity concepts accessible to developers. He wrote tutorials across many frameworks (Angular, React, Node.js, Go, Python, etc.), demonstrating broad technical fluency.
- **[HIGH]** He also worked at DigitalOcean and other developer-focused companies in community and developer advocacy roles. His career is a consistent throughline of helping developers succeed.
- **[MEDIUM]** His background means he evaluates things through the lens of: "Could I write a blog post about this? Would developers want to learn how to build this? Is this teachable and reproducible?"

### Public Signal

- **[HIGH]** His Auth0 blog posts and tutorials are extensive and publicly available. They show a preference for clear, step-by-step explanations with working code. He values things that can be followed and reproduced.
- **[HIGH]** As Community Manager at Anthropic, he is the bridge between Claude's technical capabilities and the developer community. He thinks about adoption, education, and making Claude accessible.
- **[MEDIUM]** Developer advocates fundamentally care about the developer experience. Is the API easy to use? Is the documentation clear? Can someone go from zero to working prototype quickly?

### What Would Make Him Lean Forward

- **[HIGH]** A project that is clearly built by someone who "gets" the developer experience -- clean code, good documentation, a README that makes someone want to try it.
- **[HIGH]** Something that could become a tutorial or community resource. If he watches your demo and thinks "I could write a great blog post about how to build this," you have won him over.
- **[HIGH]** Creative, unexpected uses of the Claude API that would inspire other developers. Community managers love "I had no idea you could do that with Claude" moments.
- **[MEDIUM]** Good storytelling in the presentation. DevRel people are communicators; they appreciate a well-told story about what you built and why.
- **[MEDIUM]** Open-source readiness. If the code is on GitHub with a good README, that signals community thinking.

### What Would Bore Him

- **[HIGH]** A project that is technically impressive but impossible to explain or reproduce. If it takes 20 minutes just to understand what it does, the community value is low.
- **[MEDIUM]** Poor presentation of a good idea. He has given and watched hundreds of talks; he knows when someone is winging it.
- **[MEDIUM]** Closed, proprietary approaches with no community angle. He thinks in terms of ecosystem and sharing.
- **[LOW]** A project that does not use the Claude API in an interesting or novel way.

---

## Judge 5: Jason Bigman

**Role:** Head of Community, Anthropic

### Background

- **[MEDIUM]** As Head of Community at Anthropic, Jason leads the strategy for how Anthropic engages with its developer, enterprise, and user communities. This is a senior role that involves program design, community health metrics, event strategy, and partnership development.
- **[MEDIUM]** Heads of Community at AI companies typically come from backgrounds in developer relations, marketing, or community management at other technology companies.
- **[MEDIUM]** He organized or is overseeing this hackathon, which means he is invested in it being a success. He wants projects that validate the event's existence -- projects that make Anthropic say "this is why we do hackathons."

### Public Signal

- **[MEDIUM]** The existence and format of this hackathon ($500 API credit, Claude-focused) reflects his team's priorities: enabling developers to build real things with Claude and showcasing what is possible.
- **[LOW]** Community leaders at AI companies are in a constant battle to show that their platforms are not just for chatbots. They want diverse, creative applications that expand the narrative.

### What Would Make Him Lean Forward

- **[HIGH]** A project that is a great "success story" -- something Anthropic's community team could feature in a blog post, a newsletter, or a case study. He is looking for projects that make the platform look good.
- **[HIGH]** Evidence of community impact or potential virality. If your project could inspire 100 other developers to build something similar, that is community gold.
- **[MEDIUM]** A project that showcases Claude's differentiated capabilities (safety, long context, reasoning) in a way that is easy to communicate to a broad audience.
- **[MEDIUM]** A compelling presentation and narrative. Hackathons are community events; the presentation is part of the product.
- **[MEDIUM]** A project that could grow beyond the hackathon -- something with follow-up potential, not just a one-off demo.

### What Would Bore Him

- **[HIGH]** A project that is indistinguishable from what you could build with any LLM API. He needs Claude-specific wins for his community narrative.
- **[MEDIUM]** Overly niche projects that only a tiny audience would care about. Community leaders think in terms of reach and resonance.
- **[MEDIUM]** A bad presentation of a good project. He knows that in community, packaging matters.
- **[LOW]** A project that has no story -- just "we built X, it works."

---

## Jury Overlap Matrix

What themes appear across multiple judges? These are **high-value targets** -- impressing 3+ judges simultaneously.

| Theme | Boris | Cat | Thariq | Ado | Jason | Count |
|-------|:-----:|:---:|:------:|:---:|:-----:|:-----:|
| **Uses Claude's unique/differentiated capabilities** | YES | yes | YES | yes | YES | **5/5** |
| **Solves a real problem for real people** | yes | YES | YES | yes | YES | **5/5** |
| **Technical depth beyond basic API wrapper** | YES | -- | YES | yes | -- | **3/5** |
| **Clear user story and product thinking** | -- | YES | yes | YES | YES | **4/5** |
| **Could become a community resource/tutorial/blog post** | -- | -- | -- | YES | YES | **2/5** |
| **Agentic design (plan-execute-observe loops)** | YES | yes | YES | -- | -- | **3/5** |
| **Good presentation and storytelling** | -- | yes | -- | YES | YES | **3/5** |
| **Ethical/social impact angle** | -- | yes | YES | -- | yes | **3/5** |
| **Open source / reproducible** | yes | -- | -- | YES | YES | **3/5** |

### Tier 1: Universal Wins (hit all 5 judges)

1. **Uses Claude's unique capabilities** -- Every judge, from Boris (who built the tools) to Jason (who markets the platform), wants to see Claude doing something only Claude can do. Extended thinking, tool use, long-context reasoning, safety-aware responses.
2. **Solves a real problem** -- No one wants a toy. A clear problem statement with a working solution is universally valued.

### Tier 2: Hit 3-4 judges

3. **Clear user story** -- Cat (product), Ado (community), Jason (community), and Thariq (civic tech) all want to know: who is this for?
4. **Technical depth** -- Boris, Thariq, and Ado (who has deep technical fluency) will spot shallow implementations immediately.
5. **Agentic design** -- Boris built Claude Code on this principle. Thariq works on the model. Cat would see it as a product differentiator.
6. **Good presentation** -- Ado and Jason (both community/DevRel) and Cat (product) all care about how the story is told.
7. **Social impact** -- Thariq (Upsolve), Cat (Anthropic's mission), and Jason (community narrative) would respond to meaningful impact.

---

## Anti-Patterns -- What to Avoid

### 1. The Generic Chatbot Wrapper
**Why it fails:** Boris built Claude Code. Thariq works on the model. They know what a thin wrapper looks like. Cat will ask "what problem does this solve that Claude.ai doesn't?" Ado and Jason will find nothing to write about.

### 2. The "Works With Any LLM" Project
**Why it fails:** If you could swap Claude for GPT-4 with a one-line change, you have built nothing Claude-specific. Every judge, especially Boris and Jason, wants to see Claude's strengths leveraged.

### 3. The Pure Demo With No User
**Why it fails:** Cat will ask "who is this for?" Thariq will ask "what problem does this solve?" Jason will wonder how to position it. A demo without a user story is just a tech flex with no narrative.

### 4. The Overscoped, Unfinished Project
**Why it fails:** Every judge has seen this -- "we planned to build X, Y, and Z but only finished the login page." Ship something small and complete over something ambitious and broken.

### 5. The "We Used AI to Make AI" Recursion Trap
**Why it fails:** Meta-AI tools (AI that helps you prompt AI) are overdone. Unless you have a genuinely novel angle, this category is crowded and underwhelming.

### 6. The Marketing Copy / Content Generator
**Why it fails:** Thariq built free bankruptcy tools for low-income Americans. A "better LinkedIn post generator" will feel trivial by comparison. The bar for "meaningful" is set by this jury.

---

## The Sweet Spot

Given this jury composition -- **engineering lead + product + technical staff + 2x community** -- the ideal project has these properties:

### The Formula

```
A CLEARLY DEFINED real-world problem
  + solved with DEEP, AGENTIC use of Claude's unique capabilities
  + packaged with PRODUCT THINKING (clear user, clear workflow)
  + presented as a COMPELLING STORY
  + that could INSPIRE the broader developer community
```

### What Would Make This Jury Say "I Wish I'd Built That"

1. **Boris** would say this about a project that uses Claude as a genuine agent -- one that plans, executes, reads results, and iterates -- embedded in a real developer or professional workflow. Not a chatbot. An agent that does real work.

2. **Cat** would say this about a project where the AI disappears into the product. Where the user does not think "I am using AI" but "this tool just works." Where the UX is thoughtful and the problem-solution fit is tight.

3. **Thariq** would say this about a project that takes something complicated, expensive, or gatekept and makes it accessible. Especially if it touches legal, medical, educational, or financial domains. His Upsolve background makes him light up for democratizing access.

4. **Ado** would say this about a project he could immediately turn into a tutorial. Something with clean architecture, a clear API usage pattern, and a "build this yourself" quality that developers would bookmark.

5. **Jason** would say this about a project that makes Anthropic's community team look good. Something they would feature in the hackathon recap blog post, share on social media, and point to in future events as "look what people build with Claude."

### The Intersection Project

The project that hits ALL FIVE judges simultaneously:

> **An agentic tool that solves an access problem** (Thariq) **through deep Claude integration** (Boris) **with clear product design** (Cat) **that is explainable and reproducible** (Ado) **and makes a great story** (Jason).

Concrete examples of what this could look like:

- **A Claude-powered legal document analyzer** that helps tenants understand their lease agreements -- agentic (reads documents, identifies concerning clauses, explains in plain language), solves a real access problem, uses Claude's long-context and reasoning uniquely, and is easy to demo.
- **An agentic code review system** that does not just lint but actually understands the intent of the code, detects logical errors, and suggests architectural improvements -- deeply technical, uses Claude Code's philosophy, solves a real developer problem.
- **An accessibility agent** that takes any website or document and automatically generates alternative formats (audio descriptions, simplified language, structured summaries) for people with disabilities -- social impact, clear user, technically challenging, uses Claude's multimodal capabilities.

---

## Presentation Strategy

### Structure the Demo in Four Acts

Given who is watching, the demo should hit different judges at different moments:

#### Act 1: The Problem (30 seconds) -- Hooks Cat, Thariq, Jason
Start with the problem, not the solution. Make it human. "X million people face Y problem. Currently, the solution costs Z or requires expertise most people don't have."

- Cat wants to know the user and the problem.
- Thariq wants to know the impact.
- Jason wants a story he can retell.

#### Act 2: The Live Demo (90 seconds) -- Hooks Boris, Thariq, Ado
Show the tool working in real time. Do not use slides. Do not use screenshots. Do a live demo.

- Boris wants to see the agentic loop in action -- Claude planning, executing, reading results, iterating.
- Thariq wants to see technical sophistication.
- Ado wants to see something he could teach others to build.

**Critical:** Show the unhappy path too. Show an edge case. Show how the tool handles failure gracefully. This is where Boris and Cat will be most impressed -- anyone can demo the happy path.

#### Act 3: The Architecture (30 seconds) -- Hooks Boris, Thariq
One slide or one terminal command showing the architecture. Keep it brief but show:
- How Claude is being used (which capabilities: tool use, extended thinking, etc.)
- Why this could only work with Claude (what is the differentiator)
- The agentic control loop if applicable

**Key phrase:** "Here is why we chose Claude for this and not [alternative]."

#### Act 4: The Impact / What's Next (30 seconds) -- Hooks Cat, Ado, Jason
End with:
- What this means for users (Cat)
- How the community could extend this (Ado)
- Where this goes from here (Jason)

### What to Show vs. Explain

| Show (live) | Explain (briefly) |
|-------------|-------------------|
| The tool solving a real problem in real time | The architecture and API usage pattern |
| Claude's agentic behavior (planning, executing, iterating) | Why Claude specifically (not just any LLM) |
| An edge case or failure handled gracefully | The potential impact / user base |
| The actual output / result | How the community could build on this |

### Presentation Don'ts

- **Do not start with "We built a tool that..."** -- Start with the problem.
- **Do not spend more than 10% of time on slides.** This jury wants to see working software.
- **Do not apologize for what's not finished.** Show what IS finished and make it sing.
- **Do not read from a script.** Boris and Thariq are engineers; they will tune out scripted presentations. Be conversational and authentic.
- **Do not skip the "why Claude" question.** Every judge needs this answered, for different reasons.

---

## Summary: The Cheat Sheet

| Judge | Role | Primary Lens | Impress With | Avoid |
|-------|------|-------------|-------------|-------|
| **Boris Cherny** | Head of Claude Code | Engineering depth | Agentic design, deep API integration, developer workflow embedding | Thin wrappers, chat UIs, no error handling |
| **Cat Wu** | Product | User-problem fit | Clear user story, thoughtful UX, graceful edge cases | No user, over-engineering without purpose |
| **Thariq Shihipar** | Technical Staff | Impact + technical rigor | Real-world problem solving, democratizing access, technical sophistication | Trivial use cases, shallow API usage |
| **Ado Kukic** | Community Manager | Teachability + developer appeal | Clean code, "I want to build this" factor, great storytelling | Unexplainable complexity, bad presentation |
| **Jason Bigman** | Head of Community | Community narrative | "Feature story" quality, inspiring applications, Claude differentiation | Niche projects, no story, LLM-agnostic builds |

### The Single Most Important Thing

This jury has two engineers (Boris, Thariq), one product person (Cat), and two community people (Ado, Jason). The engineers will evaluate substance. The product person will evaluate problem-solution fit. The community people will evaluate story and impact.

**You need ALL THREE: substance + fit + story.**

A technically brilliant project with no story loses 2 judges. A great story with shallow tech loses 2 judges. A perfectly presented mediocrity loses all 5.

Build something real. Build it with Claude's unique strengths. Tell a great story about why it matters.

---

> *"The best hackathon projects don't just show what the technology can do -- they show what the technology should do."*

---

*Analysis produced for Claude Hackathon 2026 planning. Confidence levels are flagged throughout. For the highest-confidence assessments, cross-reference with each judge's publicly available work.*
