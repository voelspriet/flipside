# Builder Profile: Henk van Ess

## Built with Opus 4.6 Hackathon — February 2026

---

## Who

International OSINT expert, fact-checker, and journalist trainer. Builds verification tools used by newsrooms, researchers, and law enforcement worldwide. Trains journalists at Walter Cronkite School (US), Axel Springer (DE), and University of Amsterdam (NL).

**Publications**: CHI 2026 paper (SearchWhisperer)
**Languages**: Dutch, English, German — all three active in production tools
**Website**: digitaldigging.org

---

## Core Methodology

### 20+ Years of OSINT Methodology

Professional verification methods codified into tools. Not theoretical knowledge — proven methodology used by thousands of journalists.

### "Think Like a Document" (CHI 2026)

Don't search using your own words — search using the document's words. Don't read from your own perspective — read from the drafter's perspective. This principle, published at CHI 2026, is the foundation of FlipSide.

---

## Production Tools

### ImageWhisperer / DetectAI (detectai.live)

In production. Used by journalists, researchers, and law enforcement.

- 25+ forensic image detection methods
- 7 video temporal forensic methods (~100% detection on AI-generated video)
- GAN fingerprinting for 10+ AI models (StyleGAN, DALL-E, Midjourney, Flux, Sora)
- Vanishing point analysis (ensemble of 3 methods)
- Claim verification with source attribution
- Location verification (GPS/EXIF + sun position + season consistency)
- SSE streaming architecture for real-time results
- Battle Mode: 25 detection systems side by side

### SearchWhisperer (searchwhisperer.ai)

In production. CHI 2026 paper accepted at ACM.

- Scores search queries on 4 dimensions (specificity, clarity, searchability, domain)
- Generates advanced Google operators (filetype:, site:, intitle:, AROUND(n))
- Orchestrates 4 LLMs: Claude, GPT-4, Groq, Perplexity
- "Think Like a Document" methodology: search the way documents are written, not the way people ask

**Paper**: "Search Whisperer: AI-Augmented Query Reformulation for Enhanced Information Sensemaking" — CHI 2026, ACM

---

## Domain Expertise

### Verification & Fact-Checking
- 20+ years of daily OSINT practice
- Trains journalists worldwide
- Connected to the International Fact-Checking Network (IFCN)

### Data Journalism
- Crime statistics tools for University of Amsterdam students
- QGIS SQL Translator for geographic data analysis
- Tools that make government data accessible to journalists

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
| PDF/DOCX extraction | Document Extractor pipeline |
| Ensemble methods | Vanishing point (3 methods), Video forensics (7 methods) |

---

<sub>Profile compiled for the Claude Hackathon 2026. All tools listed are in production.</sub>
