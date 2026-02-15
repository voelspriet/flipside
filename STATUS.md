# FlipSide — Where We Stand

*24 hours before deadline. Feb 15, 2026.*

---

## Submission Deadline

**Monday, February 16, 2026, 3:00 PM EST (9:00 PM CET)**

### Required Deliverables

| Deliverable | Status | Notes |
|---|---|---|
| **Video** (most important) | NOT DONE | 3-min script exists (`DEMO_SCRIPT.md`). Judges say: "Dedicate real time to making this." |
| **GitHub repo** (open source) | PARTIAL | Code complete. Uncommitted changes in `app.py` + `index.html`. Needs commit + push. |
| **Project description** (100-200 words) | NOT DONE | Submitted alongside video. |

**The video is the most important artifact.** Direct quote from kickoff: "Judges will review your GitHub repo, project description, and *most importantly the video*."

---

## Judging Process

- **Round 1** (Tue Feb 17): Async review of all ~500 submissions → **top 6 selected**
- **Round 2** (Wed Feb 18): Live panel review by Claude Code team
- Winners present at **Claude Code's 1st Birthday Party** (Feb 21, SF)

---

## Judging Criteria

No published percentage weights. Three core dimensions:

| Dimension | What judges want | FlipSide strength |
|---|---|---|
| **Technical Innovation** | Original use of Claude's capabilities | Split-model architecture, parallel threads, streaming pipeline, 18-type trick taxonomy |
| **Implementation Quality** | Functional prototype > documentation | 13,829 lines, 14 samples, works end-to-end, ~$0.54/run |
| **Potential Impact** | Solving real problems, concrete applications | Consumer protection — 100M+ people sign documents they don't understand |

### Three Problem Tracks (pick one)

1. "Build a tool addressing currently unsolved real problems"
2. **"Break barriers by making something previously inaccessible"** ← FlipSide
3. **"Amplify human judgment through AI-augmented decision-making"** ← FlipSide

FlipSide fits tracks 2 AND 3: making legal analysis accessible to non-lawyers, amplifying judgment about what you're signing.

---

## The Judges — What They Care About

### Boris Cherny — Creator of Claude Code
- **Background**: Economics dropout, self-taught. Meta/Facebook IC8, Instagram Tokyo. Anthropic since Sept 2024.
- **Philosophy**: "Build for the model six months from now." "Look at what the model is trying to do and make that easier." 80-90% of Claude Code is written by Claude Code.
- **What impresses him**: Product overhang (surfacing existing capabilities), mission-driven work, leverage through automation, code quality regardless of who wrote it.
- **FlipSide angle**: Built entirely through Claude Code by a non-coder. The "Think Like a Document" methodology = "latent demand" — Opus already understands contract asymmetry, FlipSide surfaces it. `coding.md` documents how 4.6 built the product.

### Cat Wu — Founding PM, Claude Code
- **Background**: Index Ventures, Scale AI, Cursor (briefly), J.P. Morgan.
- **What impresses her**: Product-market fit, AI-native team structure, breakout product ideas, user research.
- **FlipSide angle**: Clear PMF (everyone signs contracts), 14 sample documents as user research proxies, editorial UX design.

### Thariq Shihipar — MTS, Anthropic
- **Background**: MIT Media Lab, YC founder (1M+ users), HubSpot acquisition. Authored "Building agents with Claude Agent SDK."
- **What impresses him**: Entrepreneurial outcomes, virality potential, agent architecture, scale.
- **FlipSide angle**: Viral potential ("flip your lease" → share-worthy). Multi-agent architecture (N parallel Haiku + Opus verdict). Real-world market.

### Lydia Hallie — MTS, Anthropic (from Bun)
- **Background**: Patterns.dev co-creator, Frontend Masters instructor, Head of DX at Bun.
- **What impresses her**: Developer experience, web performance, clean technical communication, visual educational content.
- **FlipSide angle**: DOMPurify XSS defense, CSS custom properties, editorial design system, FLIP animations, streaming SSE. Clean single-file frontend.

### Ado Kukic — Developer Relations, Anthropic
- **Background**: DevRel at Auth0, MongoDB, DigitalOcean. Created "Advent of Claude."
- **What impresses him**: Community value, educational content, practical workflows.
- **FlipSide angle**: Educational tool (teaches people to read contracts). 14 real-world samples. "Visual vocabulary" pattern for non-coders.

### Jason Bigman — Head of Community, Anthropic
- **Background**: Speaks 11+ languages. Community building since 2008.
- **What impresses him**: Community impact, accessibility, global reach.
- **FlipSide angle**: English-only analysis with original-language quotes. Works for anyone worldwide. Privacy-first (no storage). Accessibility labels.

---

## What We Built — Feature Inventory

### Core Product
- **13,829 lines of code** (3,775 backend + 10,054 frontend) in 2 files
- **83 commits** over 5 days (Feb 10-15)
- **7 major architecture pivots** (>500 lines each)
- **18 bug fix commits** with self-correction

### Architecture
- **Split-model design**: Haiku 4.5 (fast cards, ~$0.08) + Opus 4.6 (verdict, ~$0.46)
- **Parallel pipeline**: Pre-scan → N simultaneous Haiku workers → Opus verdict from t=0
- **Streaming SSE**: Real-time events from parallel threads via `queue.Queue`
- **Stream-first pipeline**: First card in ~8s (was ~25s)
- **Cost**: ~$0.54/run (3-page doc), ~$1.20 (10-page doc)

### Input Methods
- PDF upload (PyPDF2 + pdfplumber)
- DOCX upload (python-docx)
- TXT upload
- Paste text directly
- Paste URL (trafilatura extraction)
- Compare two documents
- **14 built-in sample documents** (lease, insurance, ToS, employment, loan, gym, medical, HOA, coupon, wedding, pet, sweepstakes, timeshare, hackathon waiver)

### Flip Card System (Haiku 4.5)
- **Front**: Green reassurance header, gullible reader voice, teaser
- **Back**: Risk score, trick classification (18 types), figure, example, bottom line
- **Color-coded**: Green (fair) / Yellow (notable) / Red (asymmetric)
- **Confidence badges**: HIGH/MEDIUM/LOW with reasoning
- Forced first flip — navigation hidden until user engages
- Document preview with clause markers, scrollTo sync

### Expert Verdict (Opus 4.6)
- Verdict tier (5 levels: "Sign with Confidence" → "Do Not Sign")
- What Is This, Should You Worry, The Main Thing, One Action
- Power Ratio (their rights vs. yours, counted)
- Auto-detected jurisdiction with local law flags
- Risks list + chronological checklist
- 10s auto-reveal if cards haven't arrived

### UX
- Editorial design system (cream, DM Sans, rust accent, grain overlay)
- Sticky card nav with color-coded clause pips
- Tricks detected bar (collapsible, SVG icons)
- Expert Mind loading (narrated Opus thinking → plain-language briefing)
- Fisher-Yates randomized sample tiles
- Context banner (safety framing)
- PDF download via html2pdf.js
- Mobile redesign (2D flip, bottom sheet, swipe nav)
- FLIP animations between screens

### Security & Quality
- DOMPurify on all LLM output (XSS defense)
- CDN resources with SRI integrity hashes
- Sanitized error messages (no exception leaks)
- Privacy-first: no document storage after session
- ~460 lines dead code removed
- Self-reviewed: 5 code review issues found and fixed

---

## How FlipSide Uses Opus 4.6

### Capabilities Demonstrated

| Opus 4.6 Capability | How FlipSide Uses It |
|---|---|
| **1M token context** | Holds 12,500-line codebase + conversation during development. Processes 200+ page documents. |
| **Adaptive thinking** | Verdict quality scales with document complexity (model decides budget) |
| **Long-context retrieval** (76% MRCR v2) | Connects code across 8,800 lines in two files during architecture pivots |
| **Multi-step agentic reasoning** (65.4% Terminal-Bench) | 5 concurrent threads sharing mutable state, race condition reasoning |
| **Self-correction** | 18 bug fix commits, found security issues + dead code through self-review |
| **Intent inference from imprecise input** | Non-coder gives typo-filled instructions + screenshots → correct code changes |
| **Visual vocabulary** | Screenshots → element mapping → precise CSS/DOM instructions |
| **Architecture pivots** | 7 major restructurings without breaking the system |
| **BigLaw Bench** (90.2%) | Legal document analysis — trick taxonomy, clause interaction detection |
| **Parallel tool use** | N Haiku workers + Opus verdict running simultaneously |

### Capabilities NOT Used (with rationale)

| Capability | Why Not |
|---|---|
| Agent SDK | Flask handles threading directly; SDK would add abstraction without benefit for this use case |
| Tool use (API) | Document analysis doesn't need external tool calls; all reasoning is in-context |
| Vision/image analysis | Documents are text-based; no image extraction needed |
| Claude Code hooks | Standard development workflow sufficient |
| Prompt caching | Each document is unique; cache hit rate would be ~0% |
| Extended thinking (explicit) | Using `adaptive` — model decides its own thinking budget |

---

## Competitive Position

### Strengths
1. **Unique concept**: No other tool "flips" documents to show the drafter's perspective. The metaphor is sticky and demo-able.
2. **Real impact**: Consumer protection for 100M+ people who sign without reading. Matches tracks 2 AND 3.
3. **Built by a non-coder**: The development story IS the Opus 4.6 story. `coding.md` documents this with evidence.
4. **14 relatable samples**: Everyone has signed a lease, gym contract, or ToS. Instant audience connection.
5. **The flip is the money shot**: Visceral UX moment that works on camera.
6. **Functional prototype**: Works end-to-end, handles edge cases, costs $0.54/run.
7. **Builder profile**: Henk van Ess — 20 years teaching journalists, published "Think Like a Document" methodology. Not a random developer.

### Risks
1. **Video not recorded yet**: This is the #1 submission artifact. Every minute spent on code instead of video is a mistake now.
2. **No live deployment**: Running on localhost. Judges may not run it themselves, but a deployed URL would strengthen credibility.
3. **Uncommitted changes**: Homepage redesign, expert briefing, design fixes — all uncommitted.
4. **Demo script may be outdated**: `DEMO_SCRIPT.md` references old verdict column UX. Needs review against current UI.
5. **Legal disclaimer**: FlipSide says "not legal advice" but some judges might question liability implications.

---

## Priority Stack — Final 24 Hours

### MUST DO (Submission fails without these)

| Priority | Task | Est. Time |
|---|---|---|
| **1** | **Record the video** | 2-3 hours (multiple takes) |
| **2** | **Commit + push all changes** | 10 min |
| **3** | **Write 100-200 word project description** | 15 min |
| **4** | **Update DEMO_SCRIPT.md for current UI** | 30 min |
| **5** | **Submit on platform** | 15 min |

### SHOULD DO (Strengthens submission)

| Priority | Task | Est. Time |
|---|---|---|
| **6** | Deploy to a public URL (Render/Railway/Fly.io) | 30-60 min |
| **7** | Clean up README for judges | 30 min |
| **8** | Review `coding.md` — the Opus 4.6 story is a differentiator | 15 min |

### NICE TO HAVE (Only if time allows)

| Priority | Task | Est. Time |
|---|---|---|
| **9** | Record a short "how it was built" addendum | 15 min |
| **10** | Add usage analytics (how many samples tried) | 30 min |

---

## The Winning Narrative

Based on judge profiles and judging criteria, the strongest angle is:

> **"A journalist with zero coding experience built a consumer protection tool in one weekend — entirely through conversation with Claude Opus 4.6. 13,829 lines of code. 7 architecture pivots. 83 commits. The flip card — showing you the other side of what you signed — is the UX metaphor that makes complex legal analysis feel like turning over a playing card."**

This narrative hits:
- **Boris**: "Built for the model six months from now" + "product overhang" + non-coder leverage
- **Cat**: Clear product-market fit + "aha moment" demo
- **Thariq**: Viral potential + real market + entrepreneurial scale
- **Lydia**: Clean frontend architecture + editorial design quality
- **Ado**: Educational tool + community value + developer workflow showcase
- **Jason**: Global accessibility + consumer protection impact

---

## Key Numbers for the Video/Description

| Metric | Value |
|---|---|
| Lines of code | 13,829 |
| Development time | 5 days |
| Architecture pivots | 7 |
| Commits | 83 |
| Sample documents | 14 |
| Trick types classified | 18 |
| Cost per analysis | ~$0.54 |
| Time to first card | ~8 seconds |
| Input formats | 6 (PDF, DOCX, TXT, paste, URL, compare) |
| Builder coding experience | Zero |

---

## Prizes

| Place | Prize |
|---|---|
| 1st | $50,000 API credits + SF presentation |
| 2nd | $30,000 API credits + SF presentation |
| 3rd | $10,000 API credits + SF presentation |
| Most Creative Opus 4.6 Exploration | $5,000 API credits |
| Keep Thinking Prize | $5,000 API credits |

500 participants selected from 13,000+ applications (4% acceptance rate).
Only 6 advance to live finals.

---

*The video is everything. Record it today.*
