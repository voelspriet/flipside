# Expanded Reach Analysis: 4 Tool Concepts Modified for Broader User Base

> Generated 2026-02-10. Each concept retains the "Think Like a Document" core mechanism (CHI 2026, Henk van Ess). The goal: expand each concept's user base by 5x or more through a single modification, then rank the modified concepts.

---

## Concept 1: SourceSight -- The Evidence Perspective Engine

### 1. Current target user and estimated user base

**Current target**: Investigative journalists, OSINT analysts, due diligence researchers, academic fact-checkers.
**Estimated user base**: ~500,000 (TOOL_CONCEPTS.md)

### 2. Modification that expands user base by 5x+

**Expand from "verify a claim" to "find the right document for any question."** Instead of requiring a falsifiable claim as input, accept any information need: "I need the building permit for Keizersgracht 220 in Amsterdam," "Where is the public filing for Tesla's 2024 lobbying expenditure," "I need the safety inspection report for my child's school." The core mechanism stays identical -- Opus 4.6 still flips perspective to reason about what the document looks like, where it lives, and what vocabulary it uses. The only change is that the input is no longer restricted to claims that need verification. It becomes a general-purpose "document finder" powered by perspective-flipping.

### 3. New target user and estimated user base

**New target**: Anyone who needs to find a specific public document -- paralegals, HR professionals, real estate agents, students writing theses, small business owners seeking permits, citizens navigating government bureaucracy.
**New estimated user base**: ~3,000,000 (paralegal and legal support staff ~1M globally, HR professionals needing regulatory documents ~500K, real estate professionals ~500K, graduate students doing literature/document research ~500K, small business owners navigating permits and filings ~500K+).

### 4. What changes in the tool

| Element | What changes |
|---------|-------------|
| **Input** | Accepts any information need (question, description of needed document), not only falsifiable claims. The input field label changes from "Enter a claim to verify" to "Describe the document you need to find." |
| **Output** | The Source Map no longer includes "absence reasoning" (what it means if the document does not exist). Instead, it includes "access pathways" -- whether the document is free, paywalled, requires FOIA/WOB request, or needs in-person retrieval. |
| **Interface** | The bottom bar feedback loop changes from "Found / Not Found / Partial" to "Found / Not Available Online / Requires Request." The re-reasoning cycle adjusts to suggest alternative access methods rather than re-evaluating claim plausibility. |
| **Removed** | Claim decomposition into sub-claims (left panel) is replaced by document-need decomposition ("You may actually need three separate documents to answer this question"). |

Everything else stays the same: the perspective flip, the Source Map, the vocabulary translation, the SSE streaming reasoning chain, the iterative refinement loop.

### 5. Feasibility impact

**No change.** The modification simplifies the prompt engineering slightly (removing absence-of-evidence reasoning, which is the hardest part of the current design) while the architecture remains identical. Flask + SSE + Opus 4.6, no new dependencies.

---

## Concept 2: GrantWhisperer -- Funding Application Source Aligner

### 1. Current target user and estimated user base

**Current target**: Grant writers at nonprofits, academic researchers applying for funding, small NGO staff.
**Estimated user base**: ~3,000,000 (TOOL_CONCEPTS.md)

### 2. Modification that expands user base by 5x+

**Expand from "grant applications" to "any application where you must match someone else's vocabulary."** Job applications, university admissions essays, vendor proposals (RFP responses), tender submissions, scholarship applications. The core mechanism is identical -- Opus 4.6 adopts the perspective of the evaluator (hiring manager, admissions officer, procurement committee) and maps the applicant's language to the evaluator's scoring vocabulary. The perspective flip ("think like the reviewer") works identically whether the document being aligned is a grant proposal or a job application.

### 3. New target user and estimated user base

**New target**: Job seekers tailoring resumes and cover letters to job descriptions, university applicants writing admissions essays, sales teams writing RFP responses, scholarship applicants, vendor proposal writers.
**New estimated user base**: ~20,000,000 (active job seekers writing tailored applications ~10M globally at any time, university applicants ~5M annually, RFP/tender respondents ~3M, scholarship applicants ~2M).

### 4. What changes in the tool

| Element | What changes |
|---------|-------------|
| **Input** | Left panel accepts any evaluative document (job posting, admissions criteria, RFP, scholarship requirements), not only grant calls. The label changes from "Paste the grant call" to "Paste the requirements you are applying to." |
| **Output** | The Funder Vocabulary Map becomes an "Evaluator Vocabulary Map." Column headers change from "Funder's language" to "Their language." Scoring section labels become generic ("Evaluation Criteria" instead of "NIH Review Sections"). |
| **Interface** | A dropdown selector is added: "What are you applying to? [Grant / Job / University / RFP / Scholarship / Other]." This selector adjusts the perspective prompt -- e.g., for jobs, "Think like the hiring manager scanning 200 applications"; for university, "Think like the admissions committee member using a scoring rubric." |
| **Removed** | Nothing removed. Grant-specific references in UI copy become generic. |

Everything else stays the same: the two-document analysis, the vocabulary bridging, the gap identification, the SSE streaming reasoning chain.

### 5. Feasibility impact

**Increases feasibility.** The modification makes the tool more generic, which simplifies prompt engineering (one flexible prompt template instead of a grant-specific one). The dropdown selector is trivial to implement. The architecture is unchanged.

---

## Concept 3: ContractLens -- The Other Side of the Agreement

### 1. Current target user and estimated user base

**Current target**: Freelancers, small business owners, tenants, independent contractors who receive contracts they did not draft.
**Estimated user base**: ~50,000,000 (TOOL_CONCEPTS.md)

### 2. Modification that expands user base by 5x+

**Expand from "contracts" to "any document written by one party that the other party must accept or negotiate."** This includes: terms of service (every app user), privacy policies (every internet user), insurance policies (every policyholder), employee handbooks (every employee), HOA rules (every homeowner in an HOA), loan agreements (every borrower). The core mechanism is identical -- Opus 4.6 adopts the perspective of the party who drafted the document and reveals what each clause strategically accomplishes for them. The perspective flip ("think like the drafter") works identically whether the document is a freelance contract or a privacy policy.

### 3. New target user and estimated user base

**New target**: Every person who accepts terms of service, signs insurance policies, reads employee handbooks, accepts loan terms, or lives under HOA rules -- effectively any literate adult who encounters one-sided documents.
**New estimated user base**: ~250,000,000+ (internet users who accept ToS without understanding them number in the billions; scoping conservatively to English/Dutch/German-speaking users who would actively use such a tool: ~250M).

### 4. What changes in the tool

| Element | What changes |
|---------|-------------|
| **Input** | The role selector expands from "I am the: Freelancer / Tenant / Contractor / Employee" to include "App User / Policyholder / Borrower / Homeowner / Other." |
| **Output** | Negotiation suggestions are replaced by "Action Options" for non-negotiable documents: "You cannot change this clause, but here is what it means for you: [specific consequence]. Alternative services without this clause: [if applicable]." For negotiable documents, negotiation suggestions remain. |
| **Interface** | A toggle is added: "Can you negotiate this document? [Yes / No]." If No, the right panel shifts from "Suggested revisions" to "What this means for you + what to watch for." |
| **Removed** | Nothing removed. The adversarial perspective analysis remains for all document types. |

Everything else stays the same: the clause-by-clause analysis, the drafter-perspective reasoning, the risk flags, the SSE streaming reasoning chain.

### 5. Feasibility impact

**No change.** The modification adds a toggle and a slightly different output template for non-negotiable documents. The core architecture, prompt structure, and reasoning mechanism are identical. Trivial UI addition.

---

## Concept 4: SourceFlipper -- The Verification Compass

### 1. Current target user and estimated user base

**Current target**: Fact-checkers, newsroom editors, content moderators, academic peer reviewers.
**Estimated user base**: ~1,000,000 (TOOL_CONCEPTS.md)

### 2. Modification that expands user base by 5x+

**Expand from "does this source support this claim" to "does this evidence support this conclusion" -- targeting students, researchers, and professionals who evaluate arguments.** The core two-phase reading mechanism is identical: Phase A reads the source on its own terms, Phase B compares the source's own message with the conclusion drawn from it. The modification opens this to: students checking whether cited papers actually support essay arguments, researchers doing literature reviews, policy analysts checking whether reports support policy recommendations, lawyers checking whether precedents actually apply, and managers evaluating whether data supports business proposals.

### 3. New target user and estimated user base

**New target**: University students checking sources in academic writing, researchers conducting literature reviews, policy analysts, business analysts evaluating reports, lawyers checking precedent applicability.
**New estimated user base**: ~8,000,000 (university students writing source-based papers ~5M active at any time, researchers doing literature reviews ~1.5M, policy and business analysts ~1M, legal professionals checking precedent applicability ~500K).

### 4. What changes in the tool

| Element | What changes |
|---------|-------------|
| **Input** | The claim field becomes "The conclusion drawn" and the source field becomes "The evidence cited." Labels change from "Enter a claim and its cited source" to "Enter a conclusion and the evidence cited to support it." |
| **Output** | The misrepresentation taxonomy expands beyond journalistic categories (cherry-picking, context removal, misquotation) to include academic and professional categories: "overcitation" (source is tangentially related but does not directly support the conclusion), "scope mismatch" (source applies to a different population, time period, or context), "strength inflation" (source says "may" but conclusion says "does"). |
| **Interface** | A context selector is added: "What is this for? [News article / Academic paper / Policy document / Business proposal / Legal brief / Other]." This adjusts the vocabulary of the output -- e.g., for academic papers, the tool uses terms like "overcitation" and "scope mismatch"; for news, it uses "context removal" and "cherry-picking." |
| **Removed** | Nothing removed. The two-phase reading architecture is unchanged. |

Everything else stays the same: the two-phase reading (source first, conclusion second), the Phase A / Phase B streaming, the verdict card, the passage extraction.

### 5. Feasibility impact

**No change.** The modification adds a context selector and expands the output taxonomy. The two-phase architecture, the SSE streaming, and the core prompt structure are unchanged. The expanded taxonomy requires slightly more prompt engineering but this is marginal.

---

## 6. Ranking: Modified Concepts by (Jury Fit x Criteria Fit x Feasibility)

### Methodology

Base scores are taken from MATRIX_COMPARISON.md. Only dimensions that the modification directly changes are adjusted. Adjustments are explained per concept.

---

### Modified SourceSight -- "Document Finder"

**What the modification changes in scoring:**

| Dimension | Base Score | Adjusted Score | Reason for Change |
|-----------|:---------:|:--------------:|-------------------|
| Jury: Cat (clear users, organic pull) | 8 | 9 | "Find any public document" is more universally graspable than "verify a claim." Broader organic pull. |
| Criteria: Impact (25%) | 8 | 9 | User base grows from ~500K to ~3M. Problem is more universally relatable. |
| Criteria: Demo (30%) | 8 | 8 | No change -- the Source Map building live is equally impressive for document-finding. |
| Feasibility | 8 | 8 | No change. |

**Adjusted totals:**

| Dimension | Score |
|-----------|:-----:|
| Jury Fit | **43/50** (was 42; Cat moves from 8 to 9) |
| Criteria Fit | **8.95** (was 8.70; Impact moves from 8 to 9: 2.40 + 2.50 + 2.25 + 1.80 = 8.95) |
| Feasibility | **8/10** (unchanged) |
| Uniqueness | **8/10** (unchanged) |
| Rule Compliance | **10/10** (unchanged) |

---

### Modified GrantWhisperer -- "Application Aligner"

**What the modification changes in scoring:**

| Dimension | Base Score | Adjusted Score | Reason for Change |
|-----------|:---------:|:--------------:|-------------------|
| Jury: Cat (clear users, organic pull) | 9 | 10 | "Align any application to any evaluator" is the most universally useful framing. Everyone applies for something. |
| Jury: Jason (story, community) | 7 | 8 | "The vocabulary gap costs millions of qualified people their jobs, funding, and admissions" is a stronger community narrative than grants alone. |
| Jury: Thariq (entrepreneur, moat) | 7 | 8 | Market grows from ~3M to ~20M. The general application-alignment category is larger than grant-writing tools alone. |
| Criteria: Impact (25%) | 8 | 9 | User base grows from ~3M to ~20M. Problem becomes near-universal. |
| Criteria: Demo (30%) | 7 | 8 | A job-application demo is more relatable to a hackathon jury than a grant-application demo. Every jury member has applied for a job. |
| Feasibility | 10 | 10 | Increases (simpler prompt engineering), but already at ceiling. |

**Adjusted totals:**

| Dimension | Score |
|-----------|:-----:|
| Jury Fit | **42/50** (was 39; Cat 9->10, Jason 7->8, Thariq 7->8) |
| Criteria Fit | **8.55** (was 7.75; Demo 7->8, Impact 8->9: 2.40 + 2.25 + 2.25 + 1.40 = 8.30. Wait -- let me recompute. Opus 4.6 Use stays 9, Depth stays 7. So: (8 x 0.30) + (9 x 0.25) + (9 x 0.25) + (7 x 0.20) = 2.40 + 2.25 + 2.25 + 1.40 = **8.30**) |
| Feasibility | **10/10** (unchanged) |
| Uniqueness | **5/10** (unchanged -- application-alignment tools exist) |
| Rule Compliance | **10/10** (unchanged) |

**Corrected Criteria Fit: 8.30**

---

### Modified ContractLens -- "One-Sided Document Analyzer"

**What the modification changes in scoring:**

| Dimension | Base Score | Adjusted Score | Reason for Change |
|-----------|:---------:|:--------------:|-------------------|
| Jury: Cat (clear users, organic pull) | 10 | 10 | Already at ceiling. The modification reinforces this. |
| Criteria: Impact (25%) | 9 | 10 | User base grows from ~50M to ~250M+. The problem becomes universal: anyone who uses the internet accepts terms of service. |
| Criteria: Demo (30%) | 9 | 10 | Demoing with a real Terms of Service (e.g., a well-known app's ToS) is the most universally relatable demo possible. Every jury member has clicked "I accept" without reading. |
| Feasibility | 10 | 10 | No change. Already at ceiling. |

**Adjusted totals:**

| Dimension | Score |
|-----------|:-----:|
| Jury Fit | **43/50** (unchanged -- no individual judge score changes) |
| Criteria Fit | **9.05** (was 8.40; Demo 9->10, Impact 9->10: (10 x 0.30) + (9 x 0.25) + (10 x 0.25) + (6 x 0.20) = 3.00 + 2.25 + 2.50 + 1.20 = **8.95**) |
| Feasibility | **10/10** (unchanged) |
| Uniqueness | **6/10** (was 5; analyzing Terms of Service and privacy policies is a less crowded AI niche than general contract review -- DoNotPay does some of this but poorly; the adversarial perspective-flip on ToS is more novel than on contracts) |
| Rule Compliance | **10/10** (unchanged) |

**Corrected Criteria Fit: 8.95**

---

### Modified SourceFlipper -- "Evidence-Conclusion Checker"

**What the modification changes in scoring:**

| Dimension | Base Score | Adjusted Score | Reason for Change |
|-----------|:---------:|:--------------:|-------------------|
| Jury: Cat (clear users, organic pull) | 7 | 8 | "Check whether your sources actually support your conclusions" is immediately graspable for anyone who has written an academic paper. Still less universal than contracts/applications. |
| Jury: Ado (teachable, tutorial) | 7 | 8 | "Build a source-conclusion checker for academic writing" is a clearer tutorial concept than the fact-checker framing. |
| Criteria: Impact (25%) | 7 | 8 | User base grows from ~1M to ~8M. |
| Criteria: Demo (30%) | 8 | 8 | No change -- the two-phase reading demo is equally compelling whether the context is journalism or academia. |
| Feasibility | 8 | 8 | No change. |

**Adjusted totals:**

| Dimension | Score |
|-----------|:-----:|
| Jury Fit | **40/50** (was 38; Cat 7->8, Ado 7->8) |
| Criteria Fit | **8.50** (was 8.25; Impact 7->8: (8 x 0.30) + (10 x 0.25) + (8 x 0.25) + (8 x 0.20) = 2.40 + 2.50 + 2.00 + 1.60 = **8.50**) |
| Feasibility | **8/10** (unchanged) |
| Uniqueness | **8/10** (unchanged) |
| Rule Compliance | **10/10** (unchanged) |

---

### Composite Ranking

To produce a single ranking, I multiply the three dimensions the user specified: Jury Fit (normalized to 0-1 by dividing by 50), Criteria Fit (normalized to 0-1 by dividing by 10), and Feasibility (normalized to 0-1 by dividing by 10).

| Rank | Concept (Modified) | Jury Fit (norm) | Criteria Fit (norm) | Feasibility (norm) | Product Score |
|:----:|---------------------|:---------------:|:-------------------:|:------------------:|:-------------:|
| **1** | **ContractLens** ("One-Sided Document Analyzer") | 0.86 | 0.895 | 1.00 | **0.770** |
| **2** | SourceSight ("Document Finder") | 0.86 | 0.895 | 0.80 | **0.616** |
| **3** | GrantWhisperer ("Application Aligner") | 0.84 | 0.830 | 1.00 | **0.697** |
| **4** | SourceFlipper ("Evidence-Conclusion Checker") | 0.80 | 0.850 | 0.80 | **0.544** |

**Sorted by product score:**

| Rank | Concept | Product Score |
|:----:|---------|:-------------:|
| 1 | ContractLens -- "One-Sided Document Analyzer" | **0.770** |
| 2 | GrantWhisperer -- "Application Aligner" | **0.697** |
| 3 | SourceSight -- "Document Finder" | **0.616** |
| 4 | SourceFlipper -- "Evidence-Conclusion Checker" | **0.544** |

---

## 7. Recommendation

### The single recommended concept is: ContractLens, modified as "One-Sided Document Analyzer"

**Reason 1:** It has the highest composite score (0.770) because it combines the strongest demo appeal (every jury member has clicked "I accept" on terms they never read) with maximum feasibility (text in, analysis out, no external APIs, buildable by 1 person in 6 days).

**Reason 2:** The modification from "contracts" to "any one-sided document" expands the user base from ~50M to ~250M+ without adding any architectural complexity -- a single toggle ("Can you negotiate this?") is the only new UI element, and the core "think like the drafter" mechanism applies identically to Terms of Service, insurance policies, and loan agreements.

**Reason 3:** It is the purest application of the builder's "Think Like a Document" principle to the largest possible audience: the adversarial perspective flip (reading a document from the other side's viewpoint) is the CHI 2026 methodology made tangible, visible, and useful to anyone who has ever signed something they did not fully understand.

---

<sub>Generated 2026-02-10. Analysis based on TOOL_CONCEPTS.md, MATRIX_COMPARISON.md, and STRENGTHS_ANALYSIS.md. Core mechanism ("Think Like a Document," CHI 2026) preserved in all modifications.</sub>
