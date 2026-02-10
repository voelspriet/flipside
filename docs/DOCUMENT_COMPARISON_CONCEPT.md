# Document Comparison Tool: Concept Definition

> Generated 2026-02-10. Applies the "Think Like a Document" principle (CHI 2026, Henk van Ess) to multi-document comparison using Opus 4.6 extended thinking.

---

## 1. Document Types and Pairings

The tool accepts text-extractable documents: PDF, DOCX, TXT, and pasted text. It works for any pairing where two or more documents address the same subject but originate from different authors, institutions, or time periods. The tool does not process images, audio, or video.

### 5 Specific Pairings

| # | Pairing | User Role | Estimated User Base |
|---|---------|-----------|---------------------|
| 1 | **Two competing news articles about the same event** (e.g., Reuters vs. TASS reporting on the same military incident) | Fact-checker, newsroom editor | ~100,000 |
| 2 | **A company's ESG report and an NGO's assessment of the same company** (e.g., Shell's sustainability report vs. a Climate Action Tracker evaluation) | Due diligence analyst, ESG researcher | ~200,000 |
| 3 | **Two versions of the same contract or policy** (e.g., a lease agreement before and after negotiation, or two drafts of an employee handbook) | Paralegal, contract manager, tenant advocate | ~1,000,000 |
| 4 | **A scientific paper and the press release describing it** (e.g., a Nature study on vaccine efficacy and the university press release summarizing it) | Science journalist, academic peer reviewer | ~500,000 |
| 5 | **Two expert witness reports filed in the same legal case** (e.g., plaintiff's economist vs. defendant's economist on damages calculation) | Litigation attorney, judge, law clerk | ~300,000 |

---

## 2. What "Comparison" Means: Exactly 3 Types

### Type A: Factual Contradictions

**Definition**: Document A states X. Document B states not-X. Both cannot be true simultaneously.

**Example**: Two news articles about a factory explosion. Article A (local newspaper) states "the explosion occurred at 3:15 PM and injured 12 workers." Article B (wire service) states "the explosion occurred at 2:40 PM and injured 7 workers." The time and casualty count are mutually exclusive claims. The tool identifies the specific data points that conflict, quotes the exact passages, and flags them.

### Type B: Divergent Conclusions

**Definition**: Both documents reference the same underlying data, evidence, or events but reach different conclusions from them.

**Example**: Two expert witness reports in a patent infringement case. Both cite the same 14 prior art references. Expert A concludes "the patent claims are obvious in light of the prior art." Expert B concludes "the patent claims are non-obvious because no single prior art reference teaches the combination." The underlying data is identical; the interpretive frameworks diverge. The tool identifies the shared data, maps each expert's reasoning path, and pinpoints where the reasoning diverges.

### Type C: Information Gaps

**Definition**: Information present in Document A that is absent from Document B, or information present in Document B that is absent from Document A.

**Example**: A company's annual report and the same company's SEC 10-K filing. The annual report discusses a new product launch in three paragraphs. The 10-K filing does not mention the product at all. Conversely, the 10-K discloses a pending lawsuit in the risk factors section that does not appear anywhere in the annual report. The tool identifies what each document covers that the other omits, organized by topic.

---

## 3. What Opus 4.6 Extended Thinking Does That Other Tools Cannot

Three capabilities, each in one sentence:

1. **Sustained cross-document reasoning**: Opus 4.6 extended thinking holds the full content of both documents in working memory simultaneously and reasons across them for 10-20 steps, whereas a diff tool operates on string-level matching without semantic understanding and a summary tool processes each document independently.

2. **Perspective sequencing**: Opus 4.6 reads Document A on its own terms first, then reads Document B on its own terms second, then compares them -- a three-phase process that prevents the framing of one document from biasing the reading of the other, which a single ChatGPT prompt cannot enforce because both documents are visible simultaneously from the start.

3. **Absence detection**: Opus 4.6 reasons about what SHOULD be present but is not -- identifying that Document B fails to mention a topic that Document A covers -- which requires the model to construct a mental inventory of Document A's topics and check each against Document B, a task that no diff tool or summary tool performs because they operate only on what IS present, not what is missing.

---

## 4. What the User Sees as Output

The interface is a single page with four sections, rendered in HTML/CSS served by Flask. All Opus 4.6 output streams via Server-Sent Events (SSE) so the user sees reasoning appear in real time.

### Screen Layout

```
+---------------------------------------------------------------+
|  HEADER BAR                                                   |
|  Upload area: two file slots (drag-and-drop or paste)         |
|  [Document A: _______ ]  [Document B: _______ ]  [Compare]   |
+---------------------------------------------------------------+
|                    |                                           |
|  LEFT PANEL        |  CENTER PANEL                            |
|  (30% width)       |  (70% width)                             |
|                    |                                           |
|  Document          |  EXTENDED THINKING STREAM                |
|  summaries:        |                                           |
|                    |  Phase 1: "Reading Document A on its      |
|  Doc A:            |  own terms..."                            |
|  - Title/source    |  [streaming text from Opus 4.6]          |
|  - Key claims      |                                           |
|  - Topics covered  |  Phase 2: "Reading Document B on its      |
|                    |  own terms..."                            |
|  Doc B:            |  [streaming text from Opus 4.6]          |
|  - Title/source    |                                           |
|  - Key claims      |  Phase 3: "Comparing..."                 |
|  - Topics covered  |  [streaming text from Opus 4.6]          |
|                    |                                           |
+--------------------+------------------------------------------+
|                                                               |
|  BOTTOM PANEL: COMPARISON RESULTS                             |
|                                                               |
|  Three tabs:                                                  |
|  [Factual Contradictions] [Divergent Conclusions] [Gaps]      |
|                                                               |
|  Each tab contains cards. Each card shows:                    |
|  - The topic or claim in dispute                              |
|  - The exact quote from Document A                            |
|  - The exact quote from Document B (or "Not addressed")       |
|  - The Opus 4.6 reasoning that identified this finding        |
|                                                               |
+---------------------------------------------------------------+
```

### Panel Details

**Header bar**: Two upload slots accepting PDF, DOCX, or pasted text. A single "Compare" button triggers the analysis. No settings, no dropdowns, no configuration.

**Left panel**: After upload, displays a structured summary of each document generated during Phases 1 and 2. Lists the document's key factual claims, the topics it covers, and its stated conclusions. This panel populates as the extended thinking streams in the center panel.

**Center panel**: The extended thinking stream. Displays three labeled phases:
- Phase 1 header: "Reading Document A on its own terms..." followed by streaming reasoning text.
- Phase 2 header: "Reading Document B on its own terms..." followed by streaming reasoning text.
- Phase 3 header: "Comparing across documents..." followed by streaming reasoning text that identifies contradictions, divergent conclusions, and gaps.

Each phase is visually separated. The streaming text uses a monospace font on a light background to distinguish it from the structured output panels.

**Bottom panel**: Three tabs, one per comparison type. Each tab contains result cards that appear as Phase 3 completes. Cards are color-coded: red border for factual contradictions, amber border for divergent conclusions, blue border for information gaps. Each card contains the topic, exact quoted passages from both documents, and the reasoning Opus 4.6 used to identify the finding.

---

## 5. Concrete Walkthrough

### Documents

- **Document A**: A pharmaceutical company's Phase III clinical trial press release for a new diabetes drug, published on the company's investor relations page.
- **Document B**: The FDA's Complete Response Letter (CRL) for the same drug, obtained via FOIA.

### User Role

Biotech equity analyst at an investment firm, evaluating whether to maintain a "buy" rating on the company's stock after the FDA response.

### Phase 1: Reading Document A (Company Press Release)

The extended thinking stream displays:

```
Reading Document A on its own terms...

This is a press release from [Company] dated [date] announcing Phase III
results for drug candidate [name].

Key factual claims in this document:
- The trial enrolled 3,200 patients across 140 sites in 12 countries.
- The primary endpoint (HbA1c reduction) was met with statistical
  significance (p < 0.001).
- The drug showed "a favorable safety profile consistent with earlier
  trials."
- Adverse events occurred in 18% of the treatment group vs. 12% in the
  placebo group.
- The company states it "expects FDA approval in Q3 2026."

Topics this document covers: efficacy data, safety summary, enrollment
numbers, regulatory timeline, CEO quote on commercial potential.

Topics this document does NOT address (notable by absence for a Phase III
press release): specific adverse event types, dropout rates, subgroup
analysis results, manufacturing readiness, post-marketing commitments.
```

### Phase 2: Reading Document B (FDA Complete Response Letter)

The extended thinking stream displays:

```
Reading Document B on its own terms...

This is an FDA Complete Response Letter (CRL) for [drug name], NDA
[number], dated [date]. A CRL means the FDA has DECLINED to approve the
drug in its current form.

Key factual claims in this document:
- The FDA identifies "a statistically significant increase in
  cardiovascular events" in the treatment group: 4.2% vs. 1.1% in
  placebo.
- The FDA states the adverse event rate was 23% in the treatment group,
  not 18%.
- The FDA requires an additional cardiovascular outcomes trial (CVOT)
  before resubmission.
- The FDA notes that 14% of trial participants dropped out of the
  treatment arm vs. 6% in placebo, "suggesting tolerability concerns."
- The CRL references a pre-specified subgroup analysis showing the drug
  was ineffective in patients over age 65.

Topics this document covers: cardiovascular safety signal, corrected
adverse event rates, dropout rates, subgroup analysis, required
additional studies, manufacturing deficiencies at one production site.
```

### Phase 3: Comparison

The extended thinking stream displays each finding as it is identified. Below is what appears for each comparison type.

#### Factual Contradictions (red cards)

```
FACTUAL CONTRADICTION IDENTIFIED

Topic: Adverse event rate in treatment group

Document A (press release): "Adverse events occurred in 18% of the
treatment group."
Document B (FDA CRL): "The adverse event rate was 23% in the treatment
group."

These are mutually exclusive figures for the same measurement in the
same trial. The FDA letter references the full clinical study report
(CSR), which is the primary data source. The press release does not
cite a data source for its 18% figure. The 5 percentage point
discrepancy is not attributable to rounding or different measurement
windows -- the FDA letter specifically states this figure applies to
the full study period.
```

#### Divergent Conclusions (amber cards)

```
DIVERGENT CONCLUSION IDENTIFIED

Topic: Safety profile characterization

Shared data: Both documents reference the same Phase III trial, the
same patient population, and the same study period.

Document A concludes: "The drug showed a favorable safety profile
consistent with earlier trials."

Document B concludes: The drug has "a statistically significant
increase in cardiovascular events" requiring an additional
cardiovascular outcomes trial before the drug can be reconsidered
for approval.

Both documents draw from the same trial data. Document A
characterizes the safety profile as "favorable." Document B
identifies a specific cardiovascular safety signal serious enough
to require an entirely new trial. The underlying data is the same;
the characterization is opposite.
```

#### Information Gaps (blue cards)

```
INFORMATION GAP IDENTIFIED

Topic: Dropout rates

Document A: Does not mention dropout rates at any point.
Document B: States 14% dropout in treatment arm vs. 6% in placebo,
calling this evidence of "tolerability concerns."

A 14% vs. 6% differential dropout rate is material information for
evaluating a clinical trial. Its absence from the press release is
a gap.

---

INFORMATION GAP IDENTIFIED

Topic: Subgroup analysis (patients over age 65)

Document A: Does not mention any subgroup analysis.
Document B: States the drug was ineffective in patients over age 65
based on a pre-specified subgroup analysis.

Inefficacy in a major demographic subgroup is material information.
Its absence from the press release is a gap.

---

INFORMATION GAP IDENTIFIED

Topic: Manufacturing deficiencies

Document A: Does not mention manufacturing.
Document B: Identifies manufacturing deficiencies at one production
site as an additional issue requiring resolution.

This is present only in Document B.
```

---

## 6. Standalone Tool or ContractLens Mode?

**(c) A mode that could work in both.**

The comparison mechanism (upload two documents, apply three comparison types, stream extended thinking) is architecturally identical whether the documents are contracts, news articles, or scientific papers -- but when both documents are contracts, the ContractLens "think like the drafter" perspective adds value that a generic comparison tool does not provide, making it worth integrating as a ContractLens mode while also functioning independently for non-contract document pairs.

---

## 7. Feasibility Rating

**4 out of 5.**

The architecture is Flask + SSE streaming (proven in ImageWhisperer) + PDF/DOCX text extraction (existing code) + three sequential Opus 4.6 API calls (Phase 1, Phase 2, Phase 3), with the only engineering challenge being prompt design that enforces the three-phase reading sequence and produces structured output parseable into the three comparison-type tabs -- achievable by one person in 6 days but not trivially so because the Phase 3 prompt must reliably distinguish between the three comparison types without conflating them.

---

<sub>Generated for Claude Hackathon 2026. Applies the "Think Like a Document" principle (CHI 2026, Henk van Ess). Comparison types limited to the 3 defined above. No external APIs beyond Anthropic.</sub>
