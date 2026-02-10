# Tool Concepts: "Think Like a Document" Applied via Opus 4.6

> Generated 2026-02-10. Each concept applies the core principle from the CHI 2026 SearchWhisperer paper: instead of approaching information from your own perspective, adopt the perspective of the document that contains the answer.

---

## Evaluation Key

- **Feasibility**: 1 (impossible solo in 6 days) to 5 (comfortably buildable)
- **Reasoning chain length**: Number of visible extended thinking steps Opus 4.6 performs per user interaction
- **User base**: Order-of-magnitude estimate of people who have this problem regularly

---

## Concept 1: SourceSight -- The Evidence Perspective Engine

### Who uses it

Investigative journalists, OSINT analysts, due diligence researchers, and academic fact-checkers -- anyone who needs to verify a claim by finding its original source.

### What they do now without this tool

They receive a claim ("Company X dumped waste in river Y in 2024") and manually try search queries from their own vocabulary. They guess which databases, which government agencies, which file types might hold the evidence. They cycle through failed searches, gradually learning the right terminology. A senior OSINT professional does this intuitively in 20 minutes. A junior analyst struggles for hours or gives up. Neither can articulate the reasoning steps they followed.

### What the tool does, step by step

1. **User enters a claim to verify.** Example: "The mayor of Rotterdam approved a 12 million euro contract with his brother-in-law's company in 2023."
2. **Opus 4.6 extended thinking activates (visible to user).** The model reasons through the claim from the perspective of the EVIDENCE, not the searcher:
   - "If this claim is true, what documents MUST exist?"
   - "A municipal contract of 12M EUR in the Netherlands would appear in TenderNed (the Dutch procurement portal) as a published award notice."
   - "The document would be in Dutch. It would use terms like 'gunningsbeslissing' (award decision), not 'contract approval.'"
   - "It would be a PDF, likely with a reference number format like 'TN-2023-XXXXX.'"
   - "A conflict of interest would appear in 'integriteitsmelding' (integrity report) filed with the gemeenteraad (city council), not in the procurement system itself."
   - "The brother-in-law's company would appear in the KvK (Chamber of Commerce) register. The family relationship would NOT appear in any public procurement document -- it would need to be established separately via KvK records or BRP (municipal registry)."
   - "So this claim requires THREE different document types from THREE different systems: TenderNed, KvK, and municipal council records."
3. **The tool generates a Source Map**: a structured diagram showing each document type needed, where it lives, what language and vocabulary it uses, what format it is in, and what search operators would find it.
4. **For each source, the tool generates ready-to-use search queries** using the document's own vocabulary -- not the user's natural language. These include Google dorks (site:, filetype:, intitle:), direct database URLs, and API endpoints where applicable.
5. **The user selects which leads to pursue.** The tool does NOT search for them -- the human decides what to investigate and in what order. This is "Amplify Human Judgment," not "Replace Human Judgment."
6. **After the user reports what they found (or did not find), Opus 4.6 re-reasons**: adjusts the Source Map, suggests alternative document types, identifies what the absence of expected documents might mean ("If no TenderNed record exists for a 12M contract, either the claim is false, or the contract was split into smaller amounts below the publication threshold -- which itself would be a finding").

### Why Opus 4.6 extended thinking is required (not optional)

The core value of this tool IS the reasoning chain. Each claim requires 8-15 steps of multi-domain reasoning:

- Decomposing the claim into independently verifiable sub-claims
- Identifying the jurisdiction and its specific document ecosystem
- Translating from the user's vocabulary to each document's vocabulary (which differs per source type and per country)
- Reasoning about what ABSENCE of evidence means (not just presence)
- Adjusting the strategy based on what the user found in previous steps

This cannot be done in a single prompt to ChatGPT or Perplexity because: (a) it requires iterative, stateful reasoning across multiple verification attempts, (b) the perspective-flipping from "what do I want to know" to "what would the evidence look like" requires sustained multi-step reasoning that must remain coherent across the entire chain, and (c) the reasoning itself -- visible and auditable -- IS the product. A one-shot answer would hide the methodology the user needs to learn.

Extended thinking is not decoration here. The user watches the reasoning unfold and learns the methodology. The thinking chain teaches them to "Think Like a Document" for future investigations where they will not have the tool.

### What the user sees on screen

- **Left panel**: The claim they entered, decomposed into numbered sub-claims.
- **Center panel**: A live-streaming reasoning chain from Opus 4.6, showing the perspective flip happening in real time. Each step is labeled: "Identifying jurisdiction..." "Mapping document ecosystem..." "Translating to source vocabulary..." "Generating search strategy..."
- **Right panel**: The Source Map -- a structured view showing each document type, its location, vocabulary, format, and ready-to-use search queries. Updates as the reasoning progresses.
- **Bottom bar**: After the user investigates, they mark each lead as "Found," "Not Found," or "Partial." This triggers a re-reasoning cycle.

### Ratings

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Feasibility (1 person, 6 days) | **4** | Flask backend + SSE streaming (proven pattern from ImageWhisperer) + clean frontend. No external APIs beyond Claude. The complexity is in the prompt engineering, not the infrastructure. |
| Opus 4.6 reasoning chain length | **8-15 steps** per claim | Decompose claim (2-3 steps) + identify jurisdiction and document ecosystem (2-3 steps) + vocabulary translation per source (2-3 steps) + search strategy generation (2-3 steps) + absence reasoning (1-2 steps) |
| Number of users with this problem | **~500,000** | Investigative journalists (~100K globally), OSINT analysts (~50K), due diligence professionals (~200K), academic researchers doing source verification (~150K+) |

---

## Concept 2: CiteGuard -- Legal Citation Hallucination Detector

### Who uses it

Lawyers, judges, law clerks, legal aid attorneys, and pro se litigants who receive AI-generated legal documents and need to know which citations are real and which are fabricated.

### What they do now without this tool

They manually look up every citation in legal databases (Westlaw, LexisNexis, CanLII, BAILII). This costs $200-500/hour in attorney time. Pro se litigants -- people representing themselves, often in desperate situations -- cannot do this at all. The result: fabricated citations enter court records, judges cite non-existent cases, and people lose real cases based on imaginary law. The builder's corpus documents 731 such cases across 15+ jurisdictions.

### What the tool does, step by step

1. **User uploads a legal document** (PDF or DOCX) or pastes text containing legal citations.
2. **Opus 4.6 extracts all citations** -- case names, statute numbers, regulation references, journal citations -- using jurisdiction-aware pattern recognition.
3. **For each citation, Opus 4.6 extended thinking activates (visible).** The model reasons FROM THE PERSPECTIVE OF THE CITATION:
   - "If this citation is real, what would it look like in the official database?"
   - "R. v. Anderson [2023] SCC 14 -- this claims to be a Supreme Court of Canada decision. SCC decisions in 2023 are numbered sequentially. SCC 14 would be the 14th decision of 2023. I can check: does the case name, number, and year form a plausible combination?"
   - "The citation format matches the SCC naming convention. But: the case name 'Anderson' combined with the subject matter described in this brief (employment law) does not match any known SCC 2023 employment case."
   - "PATTERN MATCH: This matches hallucination pattern #3 from the corpus -- correct format, plausible-sounding name, non-existent case. This pattern appears in 47% of the fabricated citations in Canadian jurisdiction documents."
4. **Each citation receives a verdict**: Verified, Likely Fabricated, Suspicious, or Unverifiable -- with the full reasoning chain visible.
5. **A Citation Health Report is generated**: summary statistics, confidence per citation, patterns detected, and cross-references to known hallucination patterns from the 731-document corpus.

### Why Opus 4.6 extended thinking is required (not optional)

Legal citation verification is inherently a multi-step reasoning task:

- Parsing the citation format to identify jurisdiction, court level, and time period (2-3 steps)
- Reasoning about whether the citation components are internally consistent (2-3 steps)
- Cross-referencing against known hallucination patterns from the corpus (2-3 steps)
- Weighing probability: a citation can have the right format but wrong content, or vice versa (2-3 steps)
- Synthesizing across all citations in the document: if 3 out of 7 are fabricated, what does that tell us about the remaining 4? (1-2 steps)

This requires sustained reasoning that must hold 15+ jurisdictions' citation formats in context simultaneously. A single prompt to ChatGPT would hallucinate its own verification -- it cannot reliably distinguish its own fabrications from real citations. The corpus of 731 documented cases provides the ground truth that makes this verification possible rather than circular.

### What the user sees on screen

- **Top**: Document upload area. Drag-and-drop or paste.
- **Center**: Each extracted citation displayed as a card. As Opus 4.6 reasons about each one, the thinking streams in real-time beneath the citation. The card border changes color: green (verified), red (fabricated), yellow (suspicious), gray (unverifiable).
- **Right sidebar**: Running statistics -- "4 of 7 citations analyzed. 2 verified. 1 fabricated. 1 suspicious."
- **Bottom**: Citation Health Report with corpus statistics: "This document matches hallucination patterns seen in 551 of 731 documented cases across 15 jurisdictions."

### Ratings

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Feasibility (1 person, 6 days) | **4** | PDF extraction (existing pipeline), Flask+SSE (proven), Opus 4.6 API. The 731-document corpus is DATA input, not code. Main work: prompt engineering for multi-jurisdiction citation parsing + frontend. |
| Opus 4.6 reasoning chain length | **10-15 steps** per citation | Format parsing (2-3) + internal consistency check (2-3) + corpus pattern matching (2-3) + probability weighing (2-3) + document-level synthesis (2-3) |
| Number of users with this problem | **~2,000,000** | 1.3M active attorneys in the US alone, plus judges, clerks, legal aid organizations, and pro se litigants. The problem scales with AI adoption in legal practice. |

---

## Concept 3: GrantWhisperer -- Funding Application Source Aligner

### Who uses it

Grant writers at nonprofits, academic researchers applying for funding, and small NGO staff who write 5-20 grant applications per year.

### What they do now without this tool

They read a grant call (RFP/RFA) and write their application from THEIR perspective -- describing their project, their qualifications, their budget. The result: 85% of grant applications are rejected, often not because the project is bad but because the application does not speak the funder's language. The applicant writes "we will help underserved communities" when the funder's scoring rubric rewards "measurable reduction in health disparities among populations identified in HHS Priority Area 3." The vocabulary mismatch between applicant and funder is the same problem as the vocabulary mismatch between searcher and document.

### What the tool does, step by step

1. **User uploads or pastes the grant call / RFP.** The tool also accepts a URL to the funding opportunity page.
2. **Opus 4.6 extended thinking activates.** The model "thinks like the grant reviewer" -- adopting the perspective of the person who will score the application:
   - "This is an NIH R01 application. The reviewer will score on Significance, Investigators, Innovation, Approach, and Environment -- in that order."
   - "The call mentions 'health equity' 7 times, 'social determinants' 4 times, and 'community-engaged research' 3 times. These are scoring keywords."
   - "The review criteria say 'demonstrate feasibility through preliminary data.' This means Section C must contain pilot study results, not just a literature review."
   - "The funder is NIH NIMHD. Their strategic plan (2021-2025) prioritizes 'structural racism as a determinant of health.' An application that uses this exact framing will score higher than one that says 'racial disparities in healthcare.'"
3. **The tool generates a Funder Vocabulary Map**: the exact terms, phrases, and framing the grant call uses -- organized by scoring section.
4. **User enters their project description** in their own words.
5. **Opus 4.6 re-reasons**, now bridging the gap: "Your description says 'we help poor neighborhoods.' The funder's vocabulary for this concept is 'addressing health disparities in under-resourced communities as defined by Area Deprivation Index scores.' Here is how to rewrite Section 2.1 using the funder's language while preserving your meaning."
6. **The output is a section-by-section alignment guide** -- not a written application (the human writes that) but a translation map between the applicant's language and the funder's language.

### Why Opus 4.6 extended thinking is required (not optional)

Grant alignment requires reasoning across two complete documents (the call and the application) while maintaining the perspective of a third entity (the reviewer):

- Parsing the grant call's scoring rubric to identify weighted criteria (2-3 steps)
- Extracting the funder's specific vocabulary and mapping it to scoring sections (3-4 steps)
- Analyzing the user's project description to identify where their language diverges from the funder's (2-3 steps)
- Generating vocabulary bridges that preserve the applicant's meaning while adopting the funder's terms (3-4 steps)
- Identifying gaps: sections the funder requires that the applicant has not addressed at all (2-3 steps)

This is a genuine perspective-adoption task: the model must simultaneously hold the applicant's intent, the funder's vocabulary, and the reviewer's scoring logic. A single ChatGPT prompt might suggest "use funder keywords" generically, but cannot perform the deep structural alignment between two specific documents while reasoning from the reviewer's perspective. The extended thinking chain makes the alignment logic visible so the applicant understands WHY specific language changes matter.

### What the user sees on screen

- **Left panel**: The grant call, with key terms highlighted and annotated ("This term appears in the scoring rubric with weight: HIGH").
- **Center panel**: The streaming reasoning chain -- Opus 4.6 thinking like the reviewer, visible in real time.
- **Right panel**: The Alignment Guide -- a two-column view: "Your language" on the left, "Funder's language" on the right, with explanations of why the funder's version scores higher.
- **Bottom**: Gap analysis -- "The call requires a Data Management Plan (Section 4.3). Your description does not address this. Here is what reviewers expect in this section."

### Ratings

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Feasibility (1 person, 6 days) | **5** | Simplest architecture of all concepts. Text in, reasoning out. No file parsing beyond basic PDF/text. No external APIs. Flask + SSE + Opus 4.6. Frontend is two text areas + streaming output. |
| Opus 4.6 reasoning chain length | **12-18 steps** | Rubric parsing (2-3) + vocabulary extraction (3-4) + user text analysis (2-3) + vocabulary bridging (3-4) + gap identification (2-3) |
| Number of users with this problem | **~3,000,000** | ~500K nonprofit organizations in the US alone file grant applications. Add academic researchers (~1.5M globally who apply for grants), NGOs, and small businesses applying for government contracts. |

---

## Concept 4: ContractLens -- The Other Side of the Agreement

### Who uses it

Freelancers, small business owners, tenants, and independent contractors who receive contracts they did not draft and must decide whether to sign.

### What they do now without this tool

They read the contract from their own perspective ("Does this look fair to me?") and miss clauses written to benefit the other party. They cannot afford a lawyer ($300-500/hour). They sign contracts with non-compete clauses they did not understand, liability waivers that expose them to unlimited risk, or automatic renewal terms that lock them in for years. Or they ask ChatGPT "is this contract fair?" and receive a generic summary that misses the specific traps.

### What the tool does, step by step

1. **User uploads a contract** (PDF, DOCX, or pasted text) and specifies their role ("I am the freelancer / tenant / contractor").
2. **Opus 4.6 extended thinking activates.** The model adopts the perspective of THE PARTY WHO DRAFTED THE CONTRACT -- the other side:
   - "I am now thinking like the landlord's attorney who wrote this lease."
   - "Clause 7.3 says 'Tenant shall be responsible for all repairs not covered by building insurance.' From the landlord's perspective, this shifts ALL maintenance costs to the tenant. The phrase 'not covered by building insurance' sounds like a reasonable exception, but building insurance typically covers only structural damage and natural disasters -- meaning the tenant pays for plumbing, electrical, appliances, and all routine maintenance."
   - "Clause 12.1 says 'This agreement automatically renews for successive 12-month periods unless terminated by written notice 90 days prior to expiration.' From the landlord's perspective, 90 days is designed to be easy to miss. Most tenants remember 30 days before, not 90."
   - "Clause 15.2 says 'Any disputes shall be resolved by binding arbitration in [City].' From the landlord's perspective, this removes the tenant's right to sue in court and requires travel to a specific city for arbitration -- which may not be where the tenant lives."
3. **Each clause is annotated** with two perspectives: what it appears to say (surface reading) and what it means from the drafter's strategic perspective.
4. **Risk flags are generated**: clauses ranked by asymmetry (how much they favor the other party).
5. **Negotiation suggestions**: for each flagged clause, the tool suggests specific language changes that would make the clause more balanced, phrased in standard legal terminology the other party's lawyer would accept.

### Why Opus 4.6 extended thinking is required (not optional)

Contract analysis from the drafter's perspective requires adversarial reasoning -- the model must simultaneously understand what a clause says, what it strategically accomplishes for the drafter, and what risk it creates for the user:

- Identifying the drafter's likely intent behind specific word choices (2-3 steps per clause)
- Recognizing standard "trap" patterns (automatic renewal, binding arbitration, broad indemnification) and explaining them in plain language (2-3 steps)
- Reasoning about interactions between clauses -- how Clause 7 and Clause 12 together create a worse outcome than either alone (3-4 steps)
- Generating balanced alternative language that a drafter's attorney would plausibly accept (2-3 steps)
- Calibrating severity: distinguishing between standard boilerplate (low risk) and genuinely asymmetric terms (high risk) (2-3 steps)

A single ChatGPT prompt produces a flat summary. This tool produces adversarial perspective-taking -- "here is why the other side wrote it this way" -- which requires sustained reasoning across the full document. The extended thinking chain is visible because the user needs to UNDERSTAND the reasoning, not just receive a verdict.

### What the user sees on screen

- **Left panel**: The contract text, with clauses color-coded by risk level (green = standard, yellow = notable, red = significantly asymmetric).
- **Center panel**: Streaming reasoning from Opus 4.6. For each flagged clause, the user sees: "Thinking like the drafter..." followed by the strategic analysis.
- **Right panel**: Risk Summary -- a ranked list of the most asymmetric clauses with plain-language explanations and suggested revisions.
- **Top bar**: User's role selector ("I am the: Freelancer / Tenant / Contractor / Employee") -- this changes the perspective analysis.

### Ratings

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Feasibility (1 person, 6 days) | **5** | Text in, analysis out. No external APIs. Flask + SSE + Opus 4.6. PDF parsing is trivial. The entire value is in prompt engineering and UI design. |
| Opus 4.6 reasoning chain length | **10-15 steps** per clause cluster | Clause identification (2-3) + drafter intent analysis (2-3) + cross-clause interaction (3-4) + alternative language generation (2-3) + severity calibration (2-3) |
| Number of users with this problem | **~50,000,000** | 59M freelancers in the US alone. Add tenants signing leases (~44M renter households), small business owners signing vendor contracts, employees signing employment agreements. The problem is near-universal for anyone who signs a contract they did not write. |

---

## Concept 5: SourceFlipper -- The Verification Compass

### Who uses it

Fact-checkers, newsroom editors, content moderators, and academic peer reviewers -- anyone who receives a claim with a cited source and needs to determine whether the source actually supports the claim.

### What they do now without this tool

They read the claim, read the cited source, and use their own judgment to determine if the source supports the claim. This fails in three ways: (1) the source is in a language they do not read, (2) the source is a 200-page report and they check only the section the claimant referenced, missing contradictory information elsewhere, or (3) the source technically contains the cited words but in a different context than the claim implies. These are all perspective failures -- the fact-checker is reading the source through the lens of the claim, instead of reading the source on its own terms.

### What the tool does, step by step

1. **User enters a claim and its cited source** (URL, uploaded PDF, or pasted text). Example: Claim: "WHO says masks are ineffective against COVID." Source: [WHO guidance document URL].
2. **Opus 4.6 extended thinking activates -- in two phases.**

   **Phase A: Read the source on its own terms** (before looking at the claim):
   - "I am reading this WHO document as if I have never seen the claim."
   - "This document is 47 pages. Its main conclusions are: (1) masks are recommended in healthcare settings, (2) community masking is recommended when transmission is high, (3) cloth masks provide limited filtration but reduce source transmission."
   - "The document contains the sentence: 'The use of a mask alone is insufficient to provide an adequate level of protection.' This is the likely source of the claim."
   - "However, the full paragraph says: 'The use of a mask alone is insufficient... and other measures such as hand hygiene, physical distancing, and respiratory etiquette should also be adopted.' This is a recommendation for COMBINED measures, not a statement that masks are ineffective."

   **Phase B: Compare the source's own message with the claim**:
   - "The claim says 'masks are ineffective.' The source says 'masks alone are insufficient and should be combined with other measures.' These are fundamentally different statements."
   - "The claim performs a CONTEXT REMOVAL: it takes a sentence about combined measures and presents it as a standalone verdict on masks."
   - "Verdict: The source does NOT support the claim as stated. The source recommends masks as part of a multi-layered strategy. The claim misrepresents this as masks being ineffective."

3. **The tool outputs**: (a) what the source actually says (in its own terms), (b) what the claim says the source says, (c) the specific misrepresentation technique used (context removal, cherry-picking, misquotation, outdated version, etc.), and (d) the exact passages that prove the gap.

### Why Opus 4.6 extended thinking is required (not optional)

The two-phase reading process is the core innovation and requires extended thinking:

- Phase A (source-first reading) requires the model to summarize a potentially long document WITHOUT being biased by the claim. This is a deliberate perspective constraint -- the model must suppress the claim's framing while reading. (4-6 steps)
- Phase B (comparison) requires holding two representations simultaneously: the source's own message and the claim's characterization of it. (3-5 steps)
- Identifying the specific misrepresentation technique requires reasoning about HOW the gap was created, not just THAT it exists. (2-3 steps)
- Multi-language support: if the source is in Dutch and the claim is in English, the model must reason in both languages without introducing translation artifacts. (1-2 additional steps)

This cannot be done with a single prompt because the two-phase structure is essential. If you give ChatGPT both the claim and the source simultaneously, it reads the source through the lens of the claim -- which is exactly the bias this tool is designed to prevent. The deliberate sequencing (source first, then claim) requires architectural separation that a single prompt cannot provide.

### What the user sees on screen

- **Top left**: The claim as entered.
- **Top right**: The source document (scrollable, with key passages highlighted as the reasoning identifies them).
- **Center**: Two-phase reasoning stream. Phase A is labeled "Reading the source on its own terms..." Phase B is labeled "Comparing with the claim..."
- **Bottom**: The verdict card showing: Source's actual message, Claim's characterization, Misrepresentation type, Key passages (linked to the document view above).

### Ratings

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Feasibility (1 person, 6 days) | **4** | Core is two sequential Opus 4.6 calls with SSE streaming. URL fetching adds minor complexity. PDF parsing is existing code. Main challenge: prompt engineering for the two-phase reading without leakage between phases. |
| Opus 4.6 reasoning chain length | **10-16 steps** | Phase A source reading (4-6) + Phase B comparison (3-5) + misrepresentation technique identification (2-3) + passage extraction (1-2) |
| Number of users with this problem | **~1,000,000** | Professional fact-checkers (~10K), newsroom editors (~50K), content moderators at platforms (~100K), academic peer reviewers (~500K+), plus librarians, teachers, and policy analysts who verify sourced claims. |

---

## Comparative Summary

| Concept | Feasibility | Reasoning Steps | User Base | "Think Like a Document" Application | Best Problem Statement Fit |
|---------|:-----------:|:---------------:|:---------:|-----------------------------------|-----------------------------|
| **1. SourceSight** | 4 | 8-15 | ~500K | Think like the evidence that would exist if the claim were true | Amplify Human Judgment |
| **2. CiteGuard** | 4 | 10-15 | ~2M | Think like the legal database entry that should contain this citation | Build a Tool That Should Exist |
| **3. GrantWhisperer** | 5 | 12-18 | ~3M | Think like the grant reviewer who will score this application | Break the Barriers |
| **4. ContractLens** | 5 | 10-15 | ~50M | Think like the attorney who drafted this contract against you | Break the Barriers |
| **5. SourceFlipper** | 4 | 10-16 | ~1M | Think like the source document before you know the claim | Amplify Human Judgment |

---

## Strategic Notes

### Which concepts produce the most visible extended thinking?

All five concepts require Opus 4.6 extended thinking as the core mechanism, not as decoration. However, they differ in how visually dramatic the reasoning is:

- **ContractLens** and **CiteGuard** produce the most immediately understandable reasoning -- anyone who has signed a contract or read a legal document can follow along.
- **SourceSight** produces the most intellectually impressive reasoning -- watching the model map an entire document ecosystem is a "wow" moment for the jury.
- **GrantWhisperer** produces the longest reasoning chains (12-18 steps) and the most practically useful output.
- **SourceFlipper** produces the most methodologically novel reasoning -- the two-phase reading is a technique no existing tool implements.

### Which concepts best showcase "Think Like a Document"?

The principle is most visible and most necessary in **SourceSight** (the entire tool IS the perspective flip) and **SourceFlipper** (the two-phase reading is a pure application of the principle). In **ContractLens** and **GrantWhisperer**, the principle is applied to a specific domain (contracts, grants) where the perspective flip is intuitive and immediately useful. In **CiteGuard**, the principle is applied to verification (think like the database that should contain this citation).

### Which concepts cannot be replicated by a single prompt to ChatGPT?

All five are designed to require multi-step, stateful reasoning. But the strongest cases are:

- **SourceFlipper**: The two-phase reading (source first, claim second) is architecturally impossible in a single prompt where both are visible simultaneously.
- **SourceSight**: The iterative feedback loop (user reports findings, model re-reasons) is inherently multi-turn and stateful.
- **CiteGuard**: The corpus of 731 documented hallucination patterns provides ground truth that no general-purpose LLM has access to.

### Jury Fit (based on corrected jury profiles)

| Judge | Best Concept | Why |
|-------|-------------|-----|
| **Boris** (agentic, latent demand, multi-instance) | SourceSight or CiteGuard | Multi-step agentic reasoning loop with iterative refinement. Both show Claude doing real work, not just answering questions. |
| **Cat** (prototypes, clear users, organic pull) | ContractLens or GrantWhisperer | Clearest user story, clearest "I would use this" reaction. ContractLens has the largest user base by an order of magnitude. |
| **Thariq** (entrepreneur, moat, novel AI, gaming) | CiteGuard or SourceFlipper | CiteGuard has an unbeatable data moat (the corpus). SourceFlipper has the most novel AI architecture (two-phase adversarial reading). |
| **Ado** (teachable, tutorial-worthy, community) | ContractLens or GrantWhisperer | Both are immediately explainable: "Upload your contract, see what the other side intended." Tutorial-ready. |
| **Jason** (story, community narrative, multilingual) | CiteGuard or SourceSight | CiteGuard: "AI is lying in court, and we caught it 731 times." SourceSight: "Think like the evidence, not the investigator." Both are headline-ready stories. |

---

## Decision Factors Beyond This Document

The final choice should weigh:

1. **Which concept lets you show the principle most clearly in 3 minutes?** The demo is 30% of the score. The principle must be visible, not just described.
2. **Which concept uses your unique assets?** The 731-document corpus is an asset no other team has. CiteGuard is the only concept that leverages it directly. SourceSight leverages 20+ years of OSINT methodology. The others leverage the principle itself but not the specific data.
3. **Which concept produces the longest, most impressive visible reasoning chain?** GrantWhisperer (12-18 steps) and SourceFlipper (10-16 steps with the novel two-phase structure) lead here.
4. **Which concept has the "this should exist" reaction?** ContractLens (~50M potential users) and CiteGuard (legally urgent, 493 documented discipline cases) are the strongest on this dimension.

---

<sub>Generated for Claude Hackathon 2026. Each concept applies the "Think Like a Document" principle from the CHI 2026 SearchWhisperer paper to a different domain, using Opus 4.6 extended thinking as the core mechanism.</sub>
