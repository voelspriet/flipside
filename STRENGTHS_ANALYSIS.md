# Strengths Analysis: Henk van Ess
## Built with Opus 4.6 Hackathon - februari 2026

---

## 1. WIE IS HENK VAN ESS?

**Profiel**: Internationaal OSINT-expert, fact-checker, journalist-trainer, tool-bouwer
**Website**: digitaldigging.org (Substack)
**Bereik**: Traint journalisten wereldwijd (o.a. Walter Cronkite School, Axel Springer, UvA)
**Talen**: Nederlands, Engels, Duits - alle drie actief in zijn tools
**Publicaties**: CHI 2026 paper (SearchWhisperer), The Hallucination Files (731 juridische documenten)

---

## 2. UNIEKE DATASETS (wat niemand anders heeft)

### A. The Hallucination Files - 731 juridische documenten
**Dit is het sterkste unieke asset.**

| Kenmerk | Detail |
|---------|--------|
| Omvang | 731 PDF's + 730 geextraheerde teksten |
| Kernvinding | 551 documenten (75.5%) bevatten verzonnen AI-citaten |
| Jurisdicties | 15+ landen: VS (433), Canada (44), UK (30), Australie (26), Brazilie (12), Belgie (4), Duitsland (3), Ierland (2), Singapore, Nieuw-Zeeland, EU |
| Thema's | 18 geclassificeerde categorieen |
| Sancties | 493 documenten over disciplinaire maatregelen tegen advocaten |
| Dataformaten | cases.json (1.2 MB), hallucinations.csv (982 KB), corpus_analysis.json, jurisdiction_categories.json |
| Doorzoekbaar | 730 .txt bestanden in extracted_text/ |

**Waarom dit uniek is**: Er bestaat geen vergelijkbaar corpus ter wereld. Dit is origineel onderzoek dat Henk zelf heeft verzameld en gecategoriseerd. Geen enkele andere hackathon-deelnemer heeft toegang tot deze data.

**Top thema's uit het corpus**:
1. AI_Hallucinated_Citations: 551 docs - verzonnen rechtszaken en wetsartikelen
2. Sanctions_Discipline: 493 docs - advocaten gestraft voor AI-gebruik
3. Dismissed: 452 docs - zaken afgewezen door verzonnen citaten
4. AI_In_Legal_Practice: 439 docs - AI-gebruik in rechtbanken
5. Pro_Se_Litigant: 415 docs - zelfvertegenwoordigende partijen
6. Cryptocurrency_Blockchain: 351 docs - opkomend rechtsgebied
7. Vexatious_Frivolous: 334 docs - kwade trouw procedures

### B. 20+ jaar OSINT-methodologie
Henk's professionele werkwijze voor verificatie is gecodificeerd in zijn tools. Dit is geen theoretische kennis maar bewezen methodologie die door duizenden journalisten wordt gebruikt.

---

## 3. TECHNISCHE ASSETS (wat al gebouwd en in productie is)

### A. ImageWhisperer / DetectAI (detectai.live)
**Status**: In productie, gebruikt door journalisten, onderzoekers, en wetshandhavers

| Capability | Detail | Bewijslast |
|------------|--------|------------|
| Forensische beeldanalyse | 25+ detectiemethoden | 107K SimplifiedIntegratedDetector |
| ELA (Error Level Analysis) | Photoshop/manipulatie detectie met heatmap | ela_analyzer.py |
| GAN fingerprinting | Herkent 10+ AI-modellen (StyleGAN, DALL-E, Midjourney, Flux, Sora, etc.) | gan_fingerprint.py |
| Vanishing point analyse | Ensemble van 3 methoden, detecteert onmogelijk perspectief | 105K unified_vanishing_point.py |
| Video forensics | 7 temporele methoden, ~100% detectie op AI-video | 33K video_temporal_forensics.py |
| Gezichtsanalyse | Asymmetrie, iris, reflecties, micro-expressies, deepfake detectie | 6+ analyzers |
| Schaduwanalyse | 3 varianten incl. Farid methode | shadow_analysis*.py |
| Claim verificatie | Google CSE + TRUE/FALSE verdict met bronnen | claim_verifier.py |
| Locatie verificatie | GPS/EXIF + zonnepositie + seizoensconsistentie | location_verifier.py |
| IFCN integratie | International Fact-Checking Network | fact_check_api.py |
| Battle Mode | 25 detectiesystemen naast elkaar | battle.html |
| SSE streaming | Real-time resultaten via Server-Sent Events | Bewezen architectuur |
| Metadata analyse | EXIF, camera fingerprint, compressie-artefacten | comprehensive_metadata.py |
| Watermark detectie | SynthID, fotograaf-watermerken, AI-watermerken | watermark_detector.py |
| News verificatie | Bevestigende vs. weerleggende berichtgeving, betrouwbare bronnen | news_verification_analyzer.py |
| Rapport generatie | PDF export, screenshot, delen | api/export-pdf |

**Unieke detectietechnieken**:
- Video temporele forensics: Flicker (17x beter op AI), Optical Flow (2.7x), Edge Stability (4x), Frame Difference (3x), plus 3 kurtosis-methoden
- Vanishing point ensemble: XiaohuLu + RANSAC + heuristic, auto-selecteert snelste methode
- Rescue Scene Patterns: detecteert "crisis porn" en onrealistische reddingsscenes

### B. SearchWhisperer (searchwhisperer.ai)
**Status**: In productie, CHI 2026 paper geaccepteerd

| Capability | Detail |
|------------|--------|
| Query-analyse | Scoort zoekvragen op 4 dimensies (specificiteit, helderheid, doorzoekbaarheid, domein) |
| Google dorks | Genereert geavanceerde zoekoperatoren (filetype:, site:, intitle:, AROUND(n)) |
| Multi-LLM | Orchestreert 4 LLMs: Claude, GPT-4, Groq, Perplexity |
| Taaldetectie | Automatisch NL/EN/DE met domein-specifieke terminologie |
| "Think Like a Document" | Unieke methodologie: zoek zoals documenten schrijven, niet zoals mensen vragen |
| Library routing | Stuurt naar autoritatieve bronnen per domein |
| 4 modi | Question (analyse), Hotfix (snelle fix), Full Repair (expert), Library (bronnen) |

**Wetenschappelijke basis**: "Search Whisperer: AI-Augmented Query Reformulation for Enhanced Information Sensemaking" - CHI 2026, ACM

### C. AgentWhisperer (imagewhisperer.org/agents)
**Status**: In productie

| Capability | Detail |
|------------|--------|
| 6 agent-types | Playground, Speeltuin (NL), FreeAgent, Go, Gallery, Builder |
| UltraThink | LLM-powered temporal detection (onderscheidt tijdgevoelige vs. statische queries) |
| Multi-LLM | Claude 3.5 Sonnet, Claude 3 Opus, Gemini Pro, Perplexity |
| 50+ API routes | Complete REST API voor agent CRUD, executie, opslag |
| Prompt verfijning | 4-staps pipeline: analyse -> vragen -> verfijning -> generatie |
| Anti-hallucinatie | Perplexity-redirect voor expert/actuele queries, weigert nep-experts te genereren |
| Meertalig | EN, NL, DE interfaces en agent-templates |

### D. Prompt Bakery
**Status**: In productie

| Capability | Detail |
|------------|--------|
| 4-staps pipeline | Initial score -> AI guidance -> Refinement -> Final suggestions (0-100) |
| Prompt Autopsy | Analyseert zwaktes in prompts |
| Hall of Fame | Tracking van best-presterende prompts |
| Bestandsupload | PDF-analyse voor context-bewuste promptgeneratie |
| Meertalig | Dynamisch vertaalframework |

### E. Overige productie-tools

| Tool | Wat het doet | Uniek aspect |
|------|-------------|--------------|
| **WebWatch** | Verkiezingsmonitoring ("Defend Democracy") | Real-time monitoring platform |
| **Politiecijfers** | CBS misdaadstatistieken voor journalisten | CBS OData API, UvA data-journalistiek |
| **QGIS SQL Translator** | Nederlands naar SQL voor geografische data | Pro-versie met Leaflet kaarten + Shapefile import |
| **Reality Defender integratie** | Multimodal deepfake detectie (beeld+audio+video+tekst) | API key geconfigureerd, Flask+Node.js backends |
| **AgentOnly** | Multi-platform AI agent runner (Claude, ChatGPT, Gemini, Perplexity) | Gallery management, executie-tracking |
| **Agent Workshop** | IDE voor AI-agents bouwen en testen | Collaborative workflow builder |
| **Document Extractor** | DOCX/PDF tekst extractie | Geintegreerd in verificatie-workflow |
| **AI Intake webapp** | Enquete-tool voor trainingen | Flask + CSV, in productie op imagewhisperer.org/intake |

---

## 4. DOMEINEXPERTISE (niet-technisch)

### A. Verificatie & Fact-checking
- **20+ jaar OSINT-ervaring** - niet theoretisch maar dagelijkse praktijk
- **Traint journalisten wereldwijd**: Walter Cronkite School (VS), Axel Springer (DE), UvA (NL), en meer
- **Kent de fouten**: Weet welke verificatiefouten journalisten het vaakst maken
- **Kent de methoden**: Systematische verificatiestappen gecodificeerd in tools
- **IFCN-netwerk**: Connecties met internationale fact-checkers

### B. AI-veiligheid in journalistiek
- **Pioniersonderzoek**: 731 documenten over AI-hallucinaties in rechtbanken
- **75.5% bevinding**: Bewezen dat driekwart van AI-juridische documenten verzonnen citaten bevat
- **Disciplinaire golf**: 493 sanctiezaken gedocumenteerd
- **Internationaal**: 15+ landen, cross-jurisdictie patronen geidentificeerd

### C. Data-journalistiek
- **CBS-data expertise**: Politiecijfers tool voor UvA studenten
- **Geografische data**: QGIS SQL Translator voor ruimtelijke analyse
- **Publieke transparantie**: Tools die overheidsdata toegankelijk maken

### D. Tool-bouw voor journalisten
- **Track record**: 15+ tools gebouwd en in productie
- **Gebruikerskennis**: Weet wat journalisten nodig hebben (niet wat techneuten denken)
- **Meertalig**: Tools in NL, EN, DE
- **Productie-ervaring**: Nginx, gunicorn, systemd, Flask, FastAPI, SSE streaming

---

## 5. TECHNISCHE VAARDIGHEDEN

### Bewezen architectuurpatronen
| Patroon | Voorbeeld | Hergebruik-potentieel |
|---------|-----------|----------------------|
| SSE streaming | ImageWhisperer's `/stream-analysis` | Direct herbruikbaar voor hackathon |
| Multi-LLM orchestratie | SearchWhisperer (4 LLMs), AgentWhisperer (4 LLMs) | Bewezen fallback-strategie |
| Flask microservices | 6+ Flask apps op verschillende poorten | Snelle nieuwe app opzetten |
| PDF/DOCX extractie | Document Extractor | Juridische documenten verwerken |
| Ensemble methoden | Vanishing point (3 methoden), Video forensics (7 methoden) | Consensus-verdict systeem |
| Admin dashboards | ImageWhisperer admin, Intake admin | Herbruikbare UI-patronen |
| Feedback systemen | SQLite + admin review | Gebruikersfeedback verzamelen |
| Caching | Redis, SQLite, LRU cache, 1-uur TTL | Performance-optimalisatie |

### Tech stack mastery
- **Backend**: Python (Flask, FastAPI), Node.js (Express)
- **Frontend**: HTML/JS, React, Tailwind CSS, Three.js
- **AI APIs**: Claude (Anthropic), GPT-4 (OpenAI), Gemini (Google), Perplexity, Groq
- **Cloud**: Google Vision API, Google Maps API, Google CSE, AWS S3 (Reality Defender)
- **Infrastructure**: Nginx, Gunicorn, Systemd, SSL/HTTPS
- **Data**: SQLite, CSV, JSON, PDF parsing

---

## 6. COMPETITIEF VOORDEEL VOOR DE HACKATHON

### Wat Henk heeft dat NIEMAND anders heeft:

1. **Het 731-document corpus** - uniek ter wereld, origineel onderzoek
2. **25+ forensische detectiemethoden in productie** - niet prototype maar productie
3. **7 video forensische methoden** - state-of-the-art, geteste code
4. **CHI 2026 paper** - wetenschappelijke validatie van methodologie
5. **"Think Like a Document"** - unieke zoekmethodologie
6. **20+ jaar OSINT-ervaring** - gecodificeerd in tools
7. **Internationaal journalistennetwerk** - directe gebruikers/testers
8. **Multi-LLM orchestratie ervaring** - bewezen met 4+ providers
9. **SSE streaming architectuur** - direct herbruikbaar
10. **Meertalige tool-ervaring** - NL/EN/DE in productie

### Wat Henk NIET hoeft te bouwen (al klaar):
- PDF/DOCX extractie pipeline
- SSE streaming server
- Claim verificatie systeem
- Forensische beeld-analyse modules
- Video forensics modules
- Admin dashboard UI
- Feedback/rating systeem
- Multi-LLM fallback architectuur

### Zwaktes / Risico's:
- **Geen mobiele apps** - alle tools zijn web-based
- **Geen ML-model training** - gebruikt externe APIs (Google Vision, Sightengine, Reality Defender)
- **Solo-deelnemer** - geen team, alle werk alleen
- **6 dagen** - beperkte tijd voor ambitieuze projecten
- **Demo-video** - moet visueel aantrekkelijk zijn in 3 minuten

---

## 7. OPUS 4.6 COMPATIBILITEIT

### Waar Opus 4.6 extended thinking PERFECT past bij Henk's expertise:

| Henk's domein | Opus 4.6 capability | Match |
|---------------|---------------------|-------|
| Juridische citaat-verificatie | Multi-staps redenering, cross-referencing | PERFECT - 10+ stappen per citaat |
| Tegenstrijdig bewijs afwegen | Genuanceerde onzekerheid, niet-binair | PERFECT - precies wat OSINT vereist |
| Claim-decompositie | Complexe claims opdelen in sub-claims | STERK - systematische verificatie |
| Patroonherkenning in corpus | Grote context, honderden pagina's | STERK - corpus als expert knowledge |
| Forensische synthese | Meerdere bewijslagen combineren | STERK - beeld + tekst + context |
| Transparante redenering | Extended thinking zichtbaar maken | PERFECT - redenering IS de feature |
| Jurisdictie-specifiek | Contextbewust per rechtssysteem | GOED - maar vereist goede prompting |
| Zoekstrategie-generatie | Diepe strategische planning | STERK - SearchWhisperer + Opus 4.6 |

### Opus 4.6 voegt toe wat Henk's bestaande tools NIET kunnen:
1. **Diepe redenering over meerdere stappen** - bestaande tools zijn single-pass
2. **Transparant denkproces** - extended thinking maakt de "waarom" zichtbaar
3. **Contradictie-afweging** - kan tegenstrijdig bewijs genuanceerd wegen
4. **Gekalibreerde onzekerheid** - niet "waar/onwaar" maar een spectrum
5. **Cross-domein synthese** - combineert forensisch + semantisch + contextueel bewijs

---

## 8. SAMENVATTING: HENK'S SUPERKRACHTEN

### Top 5 onverslaanbare voordelen:

**1. DATA** - 731 juridische documenten met bewezen AI-hallucinaties. Niemand anders heeft dit. Period.

**2. PRODUCTIE-CODE** - 50.000+ regels Python in productie. Niet prototypes maar werkende tools die door echte gebruikers worden gebruikt. Direct herbruikbaar.

**3. DOMEINEXPERTISE** - 20+ jaar OSINT, fact-checking, en journalist-training. De tools zijn niet gebouwd door een techneut die dacht "dit zou cool zijn" maar door een expert die weet wat verificatie ECHT vereist.

**4. METHODOLOGIE** - "Think Like a Document" (CHI 2026), systematische verificatiestappen, 18 geclassificeerde juridische thema's. Dit is geen ad-hoc werk maar wetenschappelijk onderbouwde methodologie.

**5. INTEGRATIE-ERVARING** - Multi-LLM orchestratie, SSE streaming, ensemble methoden, Flask microservices. Henk weet hoe je complexe AI-systemen bouwt die in productie werken.

### De winnende formule:
**Unieke data + Bewezen code + Domeinexpertise + Opus 4.6 extended thinking = Onverslaanbaar**
