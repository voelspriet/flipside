# Product Unity Analysis: ContractLens vs. Document Comparison

> Generated 2026-02-10. Based on CONTRACTLENS_PROBLEMS.md, EXPANDED_REACH.md, DOCUMENT_COMPARISON_CONCEPT.md, and TOOL_CONCEPTS.md. No features beyond those documents are proposed. No concepts renamed. No user groups added.

---

## 1. What the Two Concepts Share (Identical Elements Only)

Only elements that are mechanically identical in both concepts are listed. Similarities, analogies, and "spirit of" overlaps are excluded.

| Element | How It Is Identical |
|---------|---------------------|
| **Core principle** | Both apply "Think Like a Document" (CHI 2026, Henk van Ess). Both require Opus 4.6 to adopt a perspective that is not the user's own before analyzing. |
| **Model** | Both use Claude Opus 4.6 extended thinking as the sole AI component. No other model is used in either concept. |
| **Extended thinking visibility** | Both stream the Opus 4.6 reasoning chain to the user in real time via SSE. The thinking is the product in both cases, not a hidden intermediate step. |
| **Backend architecture** | Both use Flask + Server-Sent Events (SSE) for streaming. No other backend framework is specified in either concept. |
| **Input format** | Both accept PDF, DOCX, and pasted text. Neither processes images, audio, or video. |
| **Text extraction** | Both require PDF/DOCX text extraction as a preprocessing step before sending content to Opus 4.6. |
| **Output delivery** | Both render structured HTML/CSS output served by Flask. Both populate output panels progressively as the extended thinking stream completes. |
| **No external APIs** | Neither concept calls any API beyond the Anthropic API. No search APIs, no legal databases, no third-party services. |
| **Single-page application** | Both are described as single-page interfaces with panels (left, center, right/bottom). |
| **Builder** | Both originate from the same person (Henk van Ess) and the same CHI 2026 methodology. |

**Total identical elements: 10.**

---

## 2. What Differs (Elements Where One Does Something the Other Does Not)

Only elements where one concept performs a function the other lacks entirely. Shared elements that differ in degree are excluded.

### ContractLens does; Document Comparison does not:

| Element | What ContractLens Does |
|---------|----------------------|
| **Single-document input** | Accepts exactly 1 document. There is no second document. |
| **Drafter-perspective adoption** | Opus 4.6 adopts the perspective of the party who wrote the document (landlord's attorney, insurer's underwriter, company's legal team). The comparison tool adopts no adversarial authorial perspective. |
| **Role selector** | User declares their role ("I am the: Freelancer / Tenant / Policyholder / ..."). This selector shapes the entire analysis. The comparison tool has no role selector. |
| **Negotiation toggle** | User declares whether the document is negotiable (Yes/No). This toggle switches the output between "Suggested revisions" and "Action Options." The comparison tool has no negotiation toggle. |
| **Clause-by-clause analysis** | Each clause is individually analyzed for strategic intent and risk. The comparison tool does not analyze individual clauses within a document. |
| **Risk flags with severity ranking** | Clauses are ranked by asymmetry (how much they favor the drafter over the user). The comparison tool does not rank findings by severity. |
| **Color-coded source text** | The uploaded document is color-coded in the left panel (green/yellow/red by risk level). The comparison tool does not color-code source documents by risk. |
| **Negotiation suggestions / Action Options** | For negotiable documents: specific alternative language. For non-negotiable documents: practical consequences and what to watch for. The comparison tool generates neither. |
| **Adversarial reasoning** | The model reasons against the user's interest by design (thinking like the opposing party). The comparison tool reasons neutrally across both documents. |

### Document Comparison does; ContractLens does not:

| Element | What Document Comparison Does |
|---------|-------------------------------|
| **Multi-document input** | Accepts 2+ documents. ContractLens accepts exactly 1. |
| **Three-phase reading sequence** | Phase 1: Read Document A on its own terms. Phase 2: Read Document B on its own terms. Phase 3: Compare. ContractLens has no phased reading sequence; it reads one document once from the drafter's perspective. |
| **Perspective sequencing to prevent framing bias** | Document A is read before Document B is considered, so A's framing does not bias the reading of B (and vice versa). ContractLens does not need this because there is only one document. |
| **Factual contradiction detection** | Identifies mutually exclusive claims across documents (Document A says X, Document B says not-X). ContractLens analyzes one document and has no cross-document contradiction function. |
| **Divergent conclusion detection** | Identifies cases where both documents share the same underlying data but reach opposite conclusions. ContractLens does not compare conclusions across documents. |
| **Information gap detection** | Identifies topics present in one document but absent from the other. ContractLens does not perform absence detection across documents. |
| **Three-tab output structure** | Results are organized into three tabs: Factual Contradictions, Divergent Conclusions, Gaps. ContractLens has no tabbed output structure. |
| **Color-coded result cards** | Red border (contradictions), amber border (divergent conclusions), blue border (gaps). ContractLens color-codes the source document, not the output cards. |
| **No user role input** | The tool does not ask the user who they are. It treats both documents neutrally. ContractLens requires the user to declare a role. |
| **Document-neutral analysis** | Works identically regardless of document type (news articles, scientific papers, expert reports, contracts). ContractLens is specialized for one-sided documents drafted by an opposing party. |

---

## 3. Can a Single Product Name, Landing Page, and Sentence Describe Both?

### Attempt

**Product name**: DocLens

**Single sentence**: "Upload a document you did not write, or two documents that disagree, and see what you are missing."

### Test

**Does a tenant uploading a lease understand the product from that sentence?**

No. The sentence does not communicate that the tool will reveal the landlord's strategic intent. "See what you are missing" could mean a grammar check, a summary, or a risk score. The tenant's core need -- understanding why the other side wrote it this way -- is absent from the sentence. The tenant would not know this tool analyzes the lease from the landlord's perspective.

**Does a fact-checker uploading two news articles understand the product from that sentence?**

No. The sentence does not communicate that the tool reads each document on its own terms before comparing, or that it identifies factual contradictions, divergent conclusions, and information gaps as distinct categories. "See what you are missing" is vague enough to describe any diff tool or summary tool. The fact-checker would not know this tool performs three-phase perspective-sequenced comparison.

**Conclusion**: A single sentence cannot describe both products without becoming so vague that neither target user recognizes their specific problem in it.

---

## 4. Three Options: Build Specifications

### Option A: One product, one interface, mode selector

The user lands on one page and selects a mode: "Analyze one document" (ContractLens) or "Compare two documents" (Document Comparison). Similar to how ContractLens already has a role selector.

| Dimension | Count |
|-----------|:-----:|
| Pages to build | **1** (single page with conditional UI: mode selector toggles between single-upload + role selector + negotiation toggle and dual-upload + compare button) |
| Opus 4.6 prompt templates | **3** (1 for ContractLens negotiable documents, 1 for ContractLens non-negotiable documents, 1 for Document Comparison with its three-phase sequence) |
| 3-minute demo can show | **Both modes**, but superficially. ~90 seconds per mode. Neither mode gets the full walkthrough needed to show Opus 4.6 extended thinking completing its full reasoning chain. A ContractLens demo needs ~2 minutes to show the drafter-perspective reasoning unfolding clause by clause. A comparison demo needs ~2 minutes to show all three phases streaming. At 90 seconds each, the jury sees the beginning of both but the completion of neither. |

### Option B: One product, two separate interfaces sharing a backend

Two URLs (or two pages) under the same product name. Shared Flask backend, shared Opus 4.6 API calls, shared text extraction pipeline. Each interface is purpose-built for its use case.

| Dimension | Count |
|-----------|:-----:|
| Pages to build | **2** (one page for ContractLens with role selector, negotiation toggle, clause-by-clause output; one page for Document Comparison with dual upload, three-phase stream, three-tab output) |
| Opus 4.6 prompt templates | **3** (same as Option A: 1 ContractLens negotiable, 1 ContractLens non-negotiable, 1 Document Comparison three-phase) |
| 3-minute demo can show | **Only one mode** in depth. The demo must choose which interface to show. Switching between two pages mid-demo costs 15-20 seconds in navigation and context-setting, and splits the jury's attention. The presenter could mention the second mode exists but cannot demonstrate it meaningfully. |

### Option C: Two separate products

Two independent products. Separate names, separate landing pages, separate repositories. No shared backend, no shared branding.

| Dimension | Count |
|-----------|:-----:|
| Pages to build | **2** (identical to Option B in build effort, but without shared backend code) |
| Opus 4.6 prompt templates | **3** (identical to Options A and B; the prompts are the same regardless of packaging) |
| 3-minute demo can show | **Only one product**. The hackathon submission is one product. Submitting two products means two separate entries, each judged independently, each getting its own 3-minute demo. This doubles the preparation effort without improving either demo. |

---

## 5. Scoring Each Option Against Hackathon Weights

Weights: Demo 30%, Opus 4.6 Use 25%, Impact 25%, Depth 20%.

### Option A: One product, one interface, mode selector

| Dimension | Weight | Score (1-10) | Rationale | Weighted |
|-----------|:------:|:------------:|-----------|:--------:|
| Demo | 30% | **6** | Both modes shown but neither completes. The jury sees two half-demos. The extended thinking stream -- which IS the product -- gets cut off mid-reasoning in both modes. The demo feels rushed and unfocused. | 1.80 |
| Opus 4.6 Use | 25% | **8** | Three prompt templates, each showcasing a different Opus 4.6 capability (adversarial reasoning, perspective sequencing, absence detection). The breadth is impressive. But the jury only sees each capability start, not finish. | 2.00 |
| Impact | 25% | **9** | Combined addressable user base: ~252M (250M ContractLens + 2M Comparison). The broadest impact claim of any option. | 2.25 |
| Depth | 20% | **4** | Neither mode gets deep treatment. The mode selector adds UI complexity without adding analytical depth. The jury cannot evaluate whether either mode works well because neither is shown completely. A tool that does two things shallowly scores lower on depth than a tool that does one thing thoroughly. | 0.80 |
| **Total** | | | | **6.85** |

### Option B: One product, two separate interfaces sharing a backend

| Dimension | Weight | Score (1-10) | Rationale | Weighted |
|-----------|:------:|:------------:|-----------|:--------:|
| Demo | 30% | **8** | One mode shown in full depth. The presenter demonstrates ContractLens (the stronger demo, per EXPANDED_REACH.md scoring) with a real document, and the extended thinking streams to completion. The second interface is mentioned ("and here is the comparison mode") with a 10-second screen flash but not demoed. The jury sees one complete, compelling demo. | 2.40 |
| Opus 4.6 Use | 25% | **8** | Same three prompt templates as Option A. The demoed mode shows Opus 4.6 extended thinking in full. The second mode's Opus 4.6 use is described, not shown. Judges who explore after the demo can see both. | 2.00 |
| Impact | 25% | **9** | Same combined user base as Option A (~252M). The product page can claim both user groups. | 2.25 |
| Depth | 20% | **7** | The demoed mode gets full depth treatment. The second mode exists and works but is not deeply evaluated by the jury during the demo. Depth score is limited by the fact that only one mode is shown thoroughly. | 1.40 |
| **Total** | | | | **8.05** |

### Option C: Two separate products

| Dimension | Weight | Score (1-10) | Rationale | Weighted |
|-----------|:------:|:------------:|-----------|:--------:|
| Demo | 30% | **9** | If only one product is submitted: that product gets the full 3 minutes. ContractLens, demoed with a real insurance policy or lease, is the strongest single demo (per EXPANDED_REACH.md: score 10 on demo). But only one product is submitted, so the comparison tool is not entered at all. | 2.70 |
| Opus 4.6 Use | 25% | **7** | Only 2 prompt templates in the submitted product (ContractLens negotiable + non-negotiable). The three-phase comparison prompt is not part of the submission. Less Opus 4.6 breadth than Options A or B. | 1.75 |
| Impact | 25% | **8** | Only ContractLens's ~250M user base. The ~2M comparison users are not part of the submission. Still the largest single-concept user base, but the impact claim is narrower than Options A or B. | 2.00 |
| Depth | 20% | **9** | One product, fully built, fully demoed, fully deep. Every second of the demo and every line of code serves one coherent purpose. The jury evaluates one thing done excellently. | 1.80 |
| **Total** | | | | **8.25** |

### Summary Table

| Option | Demo (30%) | Opus 4.6 Use (25%) | Impact (25%) | Depth (20%) | **Weighted Total** |
|--------|:----------:|:-------------------:|:------------:|:-----------:|:------------------:|
| A: One interface, mode selector | 1.80 | 2.00 | 2.25 | 0.80 | **6.85** |
| B: Two interfaces, shared backend | 2.40 | 2.00 | 2.25 | 1.40 | **8.05** |
| C: Two separate products | 2.70 | 1.75 | 2.00 | 1.80 | **8.25** |

---

## 6. Recommendation

**Option C: Two separate products. Build and submit ContractLens only. Build Document Comparison separately if time permits, but do not combine them.**

One sentence why: ContractLens alone scores highest because a 3-minute demo that shows one tool analyzing a real document from the drafter's perspective -- with the extended thinking streaming to completion -- is more compelling to every judge than a split demo that shows two tools superficially, and the depth penalty for splitting attention (Option A: 4/10, Option B: 7/10) outweighs the marginal impact gain from claiming a second user group that is 0.8% the size of the first.

---

<sub>Generated 2026-02-10. Based on CONTRACTLENS_PROBLEMS.md, EXPANDED_REACH.md, DOCUMENT_COMPARISON_CONCEPT.md, and TOOL_CONCEPTS.md. No features proposed beyond those documents. No concepts renamed. No user groups added.</sub>
