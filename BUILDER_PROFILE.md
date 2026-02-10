# Builder Profile: Henk van Ess

## Built with Opus 4.6 Hackathon — February 2026

---

## Who

Henk van Ess is an internationally recognized expert in online research methods, leveraging the web and AI to uncover information effectively. His expertise is sought after by Pulitzer winners, NGOs, research firms, and law enforcement.

A pioneer in AI-powered digital research and open-source intelligence (OSINT), Henk's methods for discovering and verifying online information have earned him international recognition. Through hands-on workshops and training sessions worldwide, he empowers professionals with practical digital investigation skills.

**Assessor** for Poynter's International Fact-Checking Network (IFCN) and the European Fact-Checking Standards Network (EFCSN). Early contributor to **Bellingcat**, the renowned collective specializing in open-source investigations. Author of multiple books on internet research and data analysis.

**Newsletter**: 10,000+ subscribers from BBC, Google, Microsoft, The New York Times, The Washington Post, Reuters, Amnesty International, Europol, The United Nations, Harvard, Oxford, Stanford, MIT, NATO, and Interpol.

**Website**: [digitaldigging.org](https://digitaldigging.org)

---

## Why FlipSide Comes From This Builder

FlipSide applies a methodology Henk has been developing for 20+ years: **don't take yourself as the measurement of things — observe what must be there.**

In search, this became "Think Like a Document" — a peer-reviewed methodology (CHI 2026, ACM) that teaches users to search from the document's perspective, not their own. In FlipSide, the same principle is applied to contracts: read from the drafter's perspective, not yours.

This is not an abstract idea. It comes from decades of training journalists to find documents they couldn't find, verify claims they couldn't verify, and see what was hidden in plain sight. FlipSide applies the same thinking to legal documents.

---

## Published Work

### "Think Like a Document" — CHI 2026

**Paper**: "Search Whisperer: AI-Augmented Query Reformulation for Enhanced Information Sensemaking" — CHI 2026, ACM

The methodology behind SearchWhisperer and FlipSide: don't search or read using your own vocabulary and perspective. Adopt the perspective of the source. Published and peer-reviewed at the world's largest HCI conference.

### GIJN Guide: Detecting AI-Generated Content

Author of the [Reporter's Guide to Detecting AI-Generated Content](https://gijn.org/resource/guide-detecting-ai-generated-content/) for the Global Investigative Journalism Network. Covers seven detection techniques for identifying machine-made content, including mathematical signatures, physics failures, and noise pattern analysis.

---

## Production Tools

### ImageWhisperer / DetectAI (detectai.live)

Born from the GIJN guide. Runs parallel LLM analysis alongside forensic image processing.

- 25+ forensic image detection methods
- 7 video temporal forensic methods (~100% detection on AI-generated video)
- GAN fingerprinting for 10+ AI models (StyleGAN, DALL-E, Midjourney, Flux, Sora)
- Claim verification with source attribution
- SSE streaming architecture for real-time results

### SearchWhisperer (searchwhisperer.ai)

The "Think Like a Document" methodology as a tool. CHI 2026 paper.

- Scores search queries on 4 dimensions (specificity, clarity, searchability, domain)
- Orchestrates 4 LLMs: Claude, GPT-4, Groq, Perplexity
- Generates advanced Google operators
- Multilingual: NL/EN/DE with domain-specific terminology

### AI Whisperer ([github.com/voelspriet/aiwhisperer](https://github.com/voelspriet/aiwhisperer))

Open-source tool for preparing documents for AI analysis. Shrinks massive PDFs to fit AI upload limits. Sanitizes documents before uploading to reduce risk of exposing sensitive data. Used in investigative workflows.

---

## What Professionals Say

> *"Henk van Ess is the best in the game at explaining OSINT tips and tricks and how AI is affecting the world of OSINT."* — Explainabl

> *"As Fact-Checkers and Researchers, we learn tremendously from your insights."* — Dr. Stefan Hertrampf

> *"I have attended your seminars at NBC News and am in awe of your investigative abilities."* — Polly DeFrank

> *"When I teach OSINT I refer my delegates to your work and that of Bellingcat."* — Ray Massie

> *"I am a senior analyst... I think you share information that is essential for us to continue to do our work well as researchers/analysts."* — Paolo

---

## Technical Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python (Flask, FastAPI), Node.js (Express) |
| **Frontend** | HTML/JS, React, Tailwind CSS |
| **AI APIs** | Claude (Anthropic), GPT-4 (OpenAI), Gemini (Google), Perplexity, Groq |
| **Infrastructure** | Nginx, Gunicorn, Systemd, SSL/HTTPS |
| **Data** | SQLite, CSV, JSON, PDF parsing |

### Proven Architecture Patterns

| Pattern | Where It's Proven |
|---------|------------------|
| SSE streaming | ImageWhisperer real-time analysis |
| Multi-LLM orchestration | SearchWhisperer (4 LLMs), AgentWhisperer (4 LLMs) |
| Flask microservices | 6+ production apps |
| PDF/DOCX extraction | AI Whisperer, Document Extractor |
| Ensemble methods | Vanishing point (3 methods), Video forensics (7 methods) |

---

<sub>Profile compiled for the Claude Hackathon 2026. All tools listed are in production.</sub>
