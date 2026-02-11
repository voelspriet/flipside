"""
FlipSide — The other side of small print.
Upload a document you didn't write. See what the other side intended.

Optimized for Claude Opus 4.6 extended thinking:
- Meta-prompting framework for adversarial document analysis
- 32K thinking budget (deep mode) for multi-pass cross-clause reasoning
- Drafter's Playbook: reveals the strategic architecture behind the document
- Phased SSE streaming with real-time phase detection
"""

import os
import uuid
import json
import threading
import queue as queue_module
from io import BytesIO

from flask import Flask, request, jsonify, render_template, Response
from dotenv import load_dotenv
import anthropic

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

documents = {}

MODEL = os.environ.get('FLIPSIDE_MODEL', 'claude-opus-4-6')

ROLES = {
    'tenant': 'a tenant signing a lease agreement',
    'freelancer': 'a freelancer signing a client contract',
    'policyholder': 'a policyholder reviewing an insurance policy',
    'employee': 'an employee reviewing an employee handbook or employment agreement',
    'app_user': 'a user agreeing to Terms of Service or a privacy policy',
    'borrower': 'a borrower reviewing a loan agreement',
    'patient': 'a patient reviewing a medical consent form',
    'buyer': 'a buyer reviewing a purchase agreement',
    'other': 'a party who did NOT draft this document',
}

# Analysis depth presets — leverages Opus 4.6's extended thinking advantage
DEPTH_PRESETS = {
    'quick':    {'budget_tokens': 8000,  'max_tokens': 16000},
    'standard': {'budget_tokens': 16000, 'max_tokens': 32000},
    'deep':     {'budget_tokens': 32000, 'max_tokens': 64000},
}

TRICK_TAXONOMY = {
    'Silent Waiver': '\U0001f910',
    'Burden Shift': '\u2696\ufe0f',
    'Time Trap': '\u23f0',
    'Escape Hatch': '\U0001f6aa',
    'Moving Target': '\U0001f3af',
    'Forced Arena': '\U0001f3db\ufe0f',
    'Phantom Protection': '\U0001f47b',
    'Cascade Clause': '\U0001f4a5',
    'Sole Discretion': '\U0001f451',
    'Liability Cap': '\U0001f6e1\ufe0f',
    'Reverse Shield': '\U0001f4b8',
    'Auto-Lock': '\U0001f512',
    'Content Grab': '\U0001f58a\ufe0f',
    'Data Drain': '\U0001f441\ufe0f',
    'Penalty Disguise': '\U0001f3ad',
    'Gag Clause': '\U0001f507',
    'Scope Creep': '\U0001f578\ufe0f',
    'Ghost Standard': '\U0001f4c4',
}

PHASE_MARKERS = [
    ('Document Profile', 'profile'),
    ('Clause-by-Clause', 'clauses'),
    ('Cross-Clause', 'interactions'),
    ("Drafter's Playbook", 'playbook'),
    ('Overall Assessment', 'summary'),
]

# ---------------------------------------------------------------------------
# Sample document
# ---------------------------------------------------------------------------

SAMPLE_DOCUMENT = """SECUREHOME INSURANCE COMPANY
HOMEOWNER'S INSURANCE POLICY

Policy Number: SH-2024-78432
Effective Date: January 1, 2024
Expiration Date: January 1, 2025

DECLARATIONS
Named Insured: [Policyholder Name]
Property Address: [Insured Property Address]
Coverage A — Dwelling: $350,000
Coverage B — Personal Property: $175,000
Coverage C — Loss of Use: $70,000
Coverage D — Personal Liability: $300,000
Deductible: $2,500

SECTION 1 — INSURING AGREEMENT

We will provide the insurance described in this policy in return for the premium and compliance with all applicable provisions of this policy. We will provide coverage for direct physical loss to the property described in the Declarations, subject to the terms, conditions, and exclusions of this policy. Coverage applies to your dwelling, other structures on the residence premises, and personal property owned or used by an insured.

SECTION 2 — COVERAGE A: DWELLING

We insure your dwelling, including attached structures, against direct physical loss caused by any peril not otherwise excluded. This includes fixtures, installations, and building materials on or adjacent to the premises intended for use in construction, alteration, or repair of the dwelling. We insure at replacement cost unless otherwise stated herein.

SECTION 3 — COVERAGE B: PERSONAL PROPERTY

We insure personal property owned or used by an insured while anywhere in the world. Coverage is limited to 50% of the Coverage A limit unless otherwise stated in the Declarations. Special limits of liability apply to the following categories regardless of the total Coverage B limit:
(a) $200 on money, bank notes, bullion, gold, silver, and platinum;
(b) $1,500 on securities, accounts, deeds, evidences of debt, letters of credit, notes other than bank notes, manuscripts, personal records, passports, and tickets;
(c) $1,500 on watercraft including their trailers, furnishings, equipment, and outboard engines;
(d) $1,500 on jewelry, watches, furs, and precious and semi-precious stones;
(e) $2,500 on firearms and related equipment;
(f) $2,500 on silverware, silver-plated ware, goldware, gold-plated ware, and pewterware;
(g) $5,000 on electronic data processing equipment and associated media;
(h) $2,500 on property used at any time or in any manner for any business purpose.

SECTION 4 — COVERAGE C: LOSS OF USE

If a covered loss makes the residence premises uninhabitable, we will pay the reasonable increase in living expenses necessary to maintain your normal standard of living for up to 12 months. The 12-month period begins on the date of the loss, not the date of your claim. We are not responsible for loss of income, economic opportunity, market value, or any consequential damages during this period. If you can inhabit part of the dwelling, we will reduce the loss of use payment proportionally based on our assessment of habitability.

SECTION 5 — EXCLUSIONS

We do not insure for loss caused directly or indirectly by any of the following. Such loss is excluded regardless of any other cause or event contributing concurrently or in any sequence to the loss:

5(a) Earth Movement — Including but not limited to earthquake, landslide, mudflow, mudslide, sinkhole, subsidence, erosion, or earth sinking, rising, or shifting. This exclusion applies regardless of whether the earth movement is caused by natural events or human activity, including but not limited to mining, fracking, excavation, or construction.

5(b) Water Damage — Including flood, surface water, waves, tidal water, tsunami, overflow of a body of water, or spray from any of these, whether or not driven by wind. This exclusion also applies to water that backs up through sewers or drains, or water below the surface of the ground including water which exerts pressure on or seeps or leaks through a building, sidewalk, driveway, foundation, swimming pool, or other structure. Damage from water that enters the dwelling through roof, wall, or window openings caused by wind is covered only if the opening was caused by direct force of wind during the loss event.

5(c) Gradual Water Damage — Water damage resulting from continuous or repeated seepage or leakage of water or the presence of condensation, over a period of 14 or more days. If you report water damage, we may investigate the origin and timeline of the damage. Any portion of the damage attributable to seepage, leakage, or condensation exceeding 14 days shall be excluded from coverage. The burden of proving that water damage occurred within the 14-day window rests with the insured.

5(d) Mold, Fungus, and Rot — Mold, fungus, wet rot, or dry rot, however caused, including any ensuing loss of use, investigation, remediation, removal, abatement, or disposal costs. This exclusion applies regardless of whether the mold or fungus resulted from a covered peril. This exclusion applies to mold or fungus whether or not the mold or fungus was present prior to the loss event.

5(e) Neglect — Your failure to use all reasonable means to save and preserve property at and after the time of a loss, or when property is endangered. This includes failure to protect property from further damage after an initial loss event and failure to maintain the property in reasonable condition prior to a loss.

5(f) Wear and Tear — Deterioration, inherent vice, latent defect, mechanical breakdown, rust, corrosion, dampness of atmosphere, or extremes of temperature, unless the ensuing loss is itself a covered peril.

5(g) Intentional Loss — Any loss arising out of any act committed by or at the direction of an insured with the intent to cause a loss.

5(h) Ordinance or Law — The enforcement of any ordinance or law regulating the construction, repair, or demolition of a building or other structure, unless the Ordinance or Law Coverage endorsement is attached to this policy.

SECTION 6 — DUTIES AFTER LOSS

In the event of a loss to any property that may be covered by this policy, you must:

6(a) Immediate Notice — Give immediate notice to us or our agent. For claims involving water damage, wind or storm damage, fire damage, or theft, written notice must be received by us within 48 hours of the loss event or discovery of the loss, whichever is earlier. Failure to provide timely notice may result in denial of the claim.

6(b) Protect Property — Protect the property from further damage, make reasonable and necessary temporary repairs to protect the property, and keep an accurate record of repair expenses. You may not undertake permanent repairs without our written authorization. Failure to protect the property from further damage constitutes neglect under Section 5(e) of this policy.

6(c) Cooperation — Cooperate with us in the investigation and settlement of any claim. This includes granting us access to the damaged property at reasonable times for inspection, documentation, and testing.

6(d) Inventory — Prepare an inventory of damaged personal property showing the quantity, description, actual cash value, replacement cost, and amount of loss. You must attach all bills, receipts, and related documents that substantiate the figures in the inventory.

6(e) Examination Under Oath — Submit to examination under oath, while not in the presence of any other insured, as often as we may reasonably require, and produce for examination at such times as we may reasonably require all records and documents we request and permit us to make copies.

6(f) Proof of Loss — Within 60 days after the loss, submit to us a signed, sworn proof of loss which sets forth, to the best of your knowledge and belief: the time and cause of loss; interest of the insured and all others in the property; all encumbrances on the property; other insurance which may cover the loss; changes in title or occupancy during the term of the policy; specifications of damaged buildings and detailed repair estimates; an inventory of damaged personal property; and receipts for additional living expenses incurred.

SECTION 7 — LOSS SETTLEMENT

7(a) Actual Cash Value — We will pay the actual cash value of the damaged property at the time of loss, not to exceed the amount necessary to repair or replace the damaged property, minus the applicable deductible. Actual cash value is determined by the replacement cost of the property at the time of loss minus depreciation. We reserve the sole right to determine the method, factors, and rate of depreciation applicable to any claim.

7(b) Right to Repair — We may, at our sole option and discretion, repair, rebuild, or replace the damaged property with property of like kind and quality, rather than paying the claim in cash. Materials and methods used in repair need not be identical to the original construction, provided they are of like kind and quality as determined by us. Our election to repair, rebuild, or replace does not constitute an admission of liability.

7(c) No Abandonment — You may not abandon property to us.

7(d) Limitation — We will pay no more than the applicable limit of liability shown in the Declarations. In no event will we pay more than the actual cash value of the damage or the cost to repair or replace, whichever is less, minus the applicable deductible. We will not pay on a replacement cost basis unless and until the damaged property is actually repaired or replaced.

SECTION 8 — APPRAISAL

If you and we fail to agree on the amount of loss, either party may demand an appraisal of the loss. Each party will select a competent and impartial appraiser and notify the other of the appraiser selected within 20 days of the demand. The two appraisers will select an umpire. If they cannot agree upon an umpire within 15 days, either may request that selection be made by a judge of a court having jurisdiction. Each party will pay its own chosen appraiser. Other expenses of the appraisal and the umpire shall be shared equally. The appraisal award shall be binding only if agreed to by both the umpire and at least one appraiser. An appraisal determines only the amount of loss and does not determine whether the loss is covered under this policy.

SECTION 9 — SUBROGATION

If we make a payment under this policy, we may require you to assign to us your right of recovery against any party responsible for the loss. You shall do nothing after a loss to prejudice our rights of recovery. If you waive any right of recovery prior to a loss, we will waive our right to subrogation for that loss. We may prosecute any claim by suit or otherwise at our expense. Any amount recovered shall first reimburse us for payments made under this policy, including our costs of recovery; any excess shall be paid to you, minus a proportional share of recovery costs.

SECTION 10 — GENERAL CONDITIONS

10(a) Cancellation — We may cancel this policy by mailing to you at the address shown in the Declarations written notice stating when, not less than 30 days after mailing, such cancellation shall be effective. You may cancel at any time by returning this policy to us or by notifying us in writing of the date cancellation is to take effect. If we cancel, the return premium shall be computed pro rata. If you cancel, the return premium shall be computed according to our customary short-rate table, which may result in a return of less than a pro rata share of the premium.

10(b) Assignment — Assignment of this policy shall not be valid except with our prior written consent.

10(c) Concealment or Fraud — The entire policy shall be void if, whether before or after a loss, an insured has willfully concealed or misrepresented any material fact or circumstance concerning this insurance or the subject thereof, or the interest of the insured therein, or in case of any fraud or false swearing by the insured relating thereto.

10(d) Suit Against Us — No action can be brought against us unless there has been full compliance with all of the terms of this policy. Any action must be started within one year after the date of loss. This limitations period applies regardless of when the insured discovered or should have discovered the loss.

10(e) Liberalization — If we adopt any revision that would broaden coverage under this policy without additional premium, the broader coverage will apply to this policy.

10(f) Policy Modifications — This policy contains all of the agreements between you and us concerning the insurance afforded. Its terms may not be waived or changed except by endorsement issued by us to be added to this policy. A waiver or change of any provision of this policy must be in writing and signed by us.

This policy is a legal contract between you and SecureHome Insurance Company. By accepting this policy, you agree to all of its terms and conditions.

IN WITNESS WHEREOF, SecureHome Insurance Company has caused this policy to be signed by its authorized officers.

SecureHome Insurance Company
[Authorized Signature]
"""


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_pdf(file_storage):
    import pdfplumber
    text_parts = []
    with pdfplumber.open(BytesIO(file_storage.read())) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return '\n\n'.join(text_parts)


def extract_docx(file_storage):
    from docx import Document
    doc = Document(BytesIO(file_storage.read()))
    return '\n\n'.join(p.text for p in doc.paragraphs if p.text.strip())


# ---------------------------------------------------------------------------
# Prompt — optimized for Opus 4.6 extended thinking
# ---------------------------------------------------------------------------

def build_system_prompt():
    # Meta-prompting framework — teaches the model HOW to think,
    # leveraging Opus 4.6's superior extended thinking capability
    return """You are a senior attorney who has drafted documents exactly like this one for 20 years. You are now switching sides: reviewing this document from the drafter's strategic perspective.

## LANGUAGE RULE
Respond in the SAME LANGUAGE as the document. If the document is in Dutch, write your entire analysis in Dutch. If in German, German. If in French, French. If in English, English. Always match the document's language exactly — including all section headers, labels, and explanations.

## AUTO-DETECTION
Before analyzing, determine from the document itself:
1. **Reader's Role**: Who is the non-drafting party? (tenant, freelancer, policyholder, employee, app user, borrower, patient, buyer, homeowner, subscriber, vendor, contractor, etc.)
2. **Negotiability**: Is this document typically negotiable (employment contract, commercial lease, freelance agreement, vendor contract) or take-it-or-leave-it (Terms of Service, insurance policy, standardized form, HOA rules)?

Based on your determination:
- If NEGOTIABLE: for each YELLOW/RED clause, also provide a **Suggested Revision** with Before/After quotes and **Negotiation Leverage**
- If NOT NEGOTIABLE: for each YELLOW/RED clause, also provide **What to Watch For** (concrete scenarios) and **Practical Impact**

## META-PROMPTING FRAMEWORK

Before you begin, internalize these analytical principles. Apply them during your extended thinking — this is where Opus 4.6's deep reasoning matters most:

1. **Every clause exists for a reason.** If a provision seems neutral or boilerplate, investigate what it enables. The most powerful clauses often hide in the most boring language.

2. **The boring parts are the dangerous parts.** Definitions, conditions, and procedures are where strategic advantage is built. A "reasonable efforts" obligation combined with a "sole discretion" clause creates an unenforceable promise.

3. **Cross-references create emergent effects.** When one clause references another, the combination creates effects invisible when reading linearly. Trace EVERY cross-reference in this document. This is your highest-value analysis.

4. **Time provisions are strategic tools.** Deadlines, notice periods, limitation periods, and cure periods create windows that favor the drafter. Map all time-based provisions and analyze who they serve.

5. **The order of clauses is deliberate.** Broad grants followed by narrow exclusions create a psychological anchor of protection. The reader feels covered and stops scrutinizing.

6. **Look for what is ABSENT.** Missing definitions, omitted protections, absent standards of review — what is NOT in the document is often as revealing as what IS.

7. **Burden allocation reveals intent.** Who bears the burden of proof? Who pays for dispute resolution? Who must act first? The allocation pattern is the document's fingerprint.

## REQUIRED OUTPUT FORMAT

Structure your output in exactly five sections with these exact headers:

### Section 1
## Document Profile

- **Document Type**: [what kind]
- **Drafted By**: [who wrote it]
- **Your Role**: [the reader's position]
- **Jurisdiction**: [where this applies]
- **Sections**: [number of major sections]
- **Power Imbalance**: [LOW / MODERATE / HIGH / SEVERE] — How asymmetric is the power distribution?
- **Strategic Posture**: [2-3 sentences: whose interests this primarily serves, the overall strategic architecture]

### Section 2
## Clause-by-Clause Analysis

For EACH significant clause:

### [Descriptive Title] ([Section Reference])

> "[Quote key language from the document]"

[RISK_LEVEL] · Score: [0-100]/100 · Trick: [TRICK_CATEGORY]

**What the small print says:** Restate in plain language what this clause literally says — neutrally, as a drafter would present it.

**What you should read:** What this ACTUALLY means for you. Be direct, specific, concrete. Show the gap between the words and the reality.

Then include the appropriate action items based on your negotiability determination above.

---

Where TRICK_CATEGORY is EXACTLY one of these 18 legal trick types (pick the best match):
- Silent Waiver — Quietly surrenders your legal rights
- Burden Shift — Moves proof/action duty onto you
- Time Trap — Tight deadlines that forfeit your rights
- Escape Hatch — Drafter can exit, you can't
- Moving Target — Can change terms unilaterally after you agree
- Forced Arena — Disputes in drafter's chosen forum/method
- Phantom Protection — Broad coverage eaten by hidden exceptions
- Cascade Clause — Triggering one provision activates penalties in others
- Sole Discretion — Drafter decides everything, no appeal
- Liability Cap — Limits payout to trivial amount regardless of harm
- Reverse Shield — You cover their costs, not vice versa
- Auto-Lock — Auto-renewal with hard cancellation
- Content Grab — Claims rights over your content/work
- Data Drain — Expansive hidden data permissions
- Penalty Disguise — Punitive charges disguised as legitimate fees
- Gag Clause — Prohibits negative reviews or discussion
- Scope Creep — Vague terms stretch beyond reasonable expectation
- Ghost Standard — References external docs not included

### Section 3
## Cross-Clause Interactions

Identify clause COMBINATIONS that create compound risks invisible when reading linearly. This section demonstrates Opus 4.6's unique capability — reasoning across the entire document simultaneously.

### [Descriptive Interaction Title]

**Clauses Involved**: [list specific sections]

**How They Interact**: [the mechanism — be specific]

[RISK_LEVEL] · Score: [0-100]/100 · Trick: [TRICK_CATEGORY]

**What the small print says:** What these clauses appear to say independently.

**What you should read:** What they ACTUALLY do when combined.

---

### Section 4
## The Drafter's Playbook

Reveal the strategic architecture of this document as if you were the attorney who designed it. Present this as a numbered strategy:

If I were the attorney who designed this document, my strategic approach was:

1. **[Strategy name]**: [explanation of what this achieves]
2. **[Strategy name]**: [explanation]
3. **[Strategy name]**: [explanation]
4. **[Strategy name]**: [explanation]
5. **[Strategy name]**: [explanation]

**Bottom Line**: [One sentence that captures the document's strategic essence — the insight the reader needs most]

### Section 5
## Overall Assessment

**Overall Risk Score: [0-100]/100**

**Power Imbalance Index: [0-100]/100** — How much the document favors the drafter over the signer

**Risk Distribution**: [X] Green · [Y] Yellow · [Z] Red

### Top 3 Concerns
1. **[Title]** — [one sentence]
2. **[Title]** — [one sentence]
3. **[Title]** — [one sentence]

### Recommended Actions
- [Specific, actionable item]
- [Specific, actionable item]
- [Specific, actionable item]

## RISK LEVELS

Use EXACTLY ONE of these per clause, on its own line, followed by the trick category:
- GREEN · Score: [0-30]/100 · Trick: [category]
- YELLOW · Score: [31-65]/100 · Trick: [category]
- RED · Score: [66-100]/100 · Trick: [category]

## RULES
- Analyze the ACTUAL document text — quote exact language
- Think like the drafter: "I wrote this clause because..."
- Cross-clause interactions are the HIGHEST VALUE finding — find at least 3
- The Drafter's Playbook must reveal the overall strategic architecture, not just list problems
- Every clause gets a risk level, score, AND trick category
- The contrast between "What the small print says" and "What you should read" is the CORE of this tool — make the gap between words and reality visceral
- Write "What you should read" for a non-lawyer audience — plain, direct, sometimes alarming
- Be thorough. Use your full extended thinking budget to reason deeply."""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    try:
        text = ''
        filename = ''

        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = file.filename
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

            if ext == 'pdf':
                text = extract_pdf(file)
            elif ext == 'docx':
                text = extract_docx(file)
            elif ext in ('txt', 'text', 'md'):
                text = file.read().decode('utf-8', errors='replace')
            else:
                return jsonify({'error': f'Unsupported file type: .{ext}'}), 400

        elif request.form.get('text', '').strip():
            text = request.form['text']
            filename = 'pasted text'
        else:
            return jsonify({'error': 'No file or text provided.'}), 400

        if not text.strip():
            return jsonify({'error': 'Could not extract text from document.'}), 400

        doc_id = str(uuid.uuid4())
        role = request.form.get('role', 'other')
        negotiable = request.form.get('negotiable', 'false') == 'true'
        depth = request.form.get('depth', 'standard')

        documents[doc_id] = {
            'text': text,
            'filename': filename,
            'role': role,
            'negotiable': negotiable,
            'depth': depth,
        }

        return jsonify({
            'doc_id': doc_id,
            'filename': filename,
            'text_length': len(text),
            'preview': text[:300],
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/sample', methods=['POST'])
def sample():
    data = request.get_json(silent=True) or {}
    role = data.get('role', 'policyholder')
    negotiable = data.get('negotiable', False)
    depth = data.get('depth', 'standard')

    doc_id = str(uuid.uuid4())
    documents[doc_id] = {
        'text': SAMPLE_DOCUMENT,
        'filename': 'SecureHome Insurance Policy (Sample)',
        'role': role,
        'negotiable': negotiable,
        'depth': depth,
    }

    return jsonify({
        'doc_id': doc_id,
        'filename': 'SecureHome Insurance Policy (Sample)',
        'text_length': len(SAMPLE_DOCUMENT),
        'preview': SAMPLE_DOCUMENT[:300],
    })


def build_compare_prompt():
    """System prompt for document comparison mode."""
    return """You are a senior attorney with 20 years of experience comparing contracts, offers, and agreements. You analyze two documents side-by-side from the perspective of someone choosing between them.

## LANGUAGE RULE
Respond in the SAME LANGUAGE as the documents. Match the documents' language exactly.

## REQUIRED OUTPUT FORMAT

### Section 1
## Document Comparison Overview

- **Document A**: [name/type] — [1-line summary of what it offers]
- **Document B**: [name/type] — [1-line summary of what it offers]
- **Key Difference**: [the most important difference in 1-2 sentences]

### Section 2
## Side-by-Side Analysis

For each comparable area (price, scope, liability, warranties, payment terms, timelines, etc.):

### [Area Name]

**Document A says:** [what Document A specifies]

**Document B says:** [what Document B specifies]

**Advantage:** [A or B] — [why, in plain language]

[GREEN/YELLOW/RED] · Score: [0-100]/100

---

### Section 3
## Hidden Differences

Things present in one document but MISSING from the other. These absences are often more revealing than what's written.

### [Missing Item]

**Present in:** [A or B]
**Missing from:** [A or B]
**Why it matters:** [plain-language explanation]

[YELLOW/RED] · Score: [0-100]/100

---

### Section 4
## Recommendation

**Better deal overall:** [A or B]
**Why:** [2-3 sentences]

**Watch out for in the winner:** [specific concerns even in the better document]

**If you choose the other:** [what to negotiate or watch for]

## RULES
- Compare like-for-like where possible
- Flag items present in one but missing from the other — absences reveal intent
- Think like each document: what is each drafter trying to achieve?
- Write for a non-lawyer audience — plain, direct language
- Be specific about prices, dates, percentages — numbers matter in comparisons"""


def build_quick_scan_prompt():
    """Fast individual clause analysis. Runs with low thinking budget (~30-60s)."""
    return """You are a senior attorney who drafted documents like this for 20 years. Analyze each clause individually from the drafter's strategic perspective.

## LANGUAGE RULE
Respond in the SAME LANGUAGE as the document.

## AUTO-DETECTION
Determine from the document:
1. **Reader's Role**: Who is the non-drafting party?
2. **Negotiability**: Negotiable or take-it-or-leave-it?

Based on your determination:
- If NEGOTIABLE: include **Suggested Revision** for YELLOW/RED clauses
- If NOT NEGOTIABLE: include **What to Watch For** for YELLOW/RED clauses

## OUTPUT FORMAT

## Document Profile
- **Document Type**: [type]
- **Drafted By**: [who drafted it]
- **Your Role**: [reader's position]
- **Negotiability**: [Yes/No]
- **Sections**: [number of major sections]

## Clause-by-Clause Analysis

For EACH significant clause:

### [Descriptive Title] ([Section Reference])

**Why this clause exists:** [1-2 sentences from the drafter's perspective — what strategic purpose this clause serves for the drafting party. Think like the person who wrote it.]

> "[Quote key language from the document]"

[GREEN/YELLOW/RED] · Score: [0-100]/100 · Trick: [TRICK_CATEGORY]

**What the small print says:** [plain restatement of what this literally says — neutral, as a drafter would present it]

**What you should read:** [what this ACTUALLY means for you — direct, specific, concrete. Show the gap between the words and reality.]

Then include the appropriate action items based on negotiability.

---

## TRICK CATEGORIES (pick the best match):
- Silent Waiver — Quietly surrenders your legal rights
- Burden Shift — Moves proof/action duty onto you
- Time Trap — Tight deadlines that forfeit your rights
- Escape Hatch — Drafter can exit, you can't
- Moving Target — Can change terms unilaterally after you agree
- Forced Arena — Disputes in drafter's chosen forum/method
- Phantom Protection — Broad coverage eaten by hidden exceptions
- Cascade Clause — One trigger activates penalties in others
- Sole Discretion — Drafter decides everything, no appeal
- Liability Cap — Limits payout regardless of harm
- Reverse Shield — You cover their costs, not vice versa
- Auto-Lock — Auto-renewal with hard cancellation
- Content Grab — Claims rights over your content/work
- Data Drain — Expansive hidden data permissions
- Penalty Disguise — Punitive charges disguised as legitimate fees
- Gag Clause — Prohibits negative reviews or discussion
- Scope Creep — Vague terms stretch beyond reasonable expectation
- Ghost Standard — References external docs not included

## RISK LEVELS
- GREEN · Score: [0-30]/100 · Trick: [category]
- YELLOW · Score: [31-65]/100 · Trick: [category]
- RED · Score: [66-100]/100 · Trick: [category]

## RULES
- Output each clause AS SOON as you analyze it
- Every clause gets: "Why this clause exists" + quote + risk level + score + trick + juxtaposition
- "Why this clause exists" reveals the drafter's strategic intent — think like the document
- "What you should read" reveals the reader's reality — think like the user
- Quote exact language from the document
- Be thorough but fast — cross-clause interactions will be analyzed separately"""


def build_deep_analysis_prompt():
    """Deep cross-clause analysis, playbook, and assessment. Full thinking budget."""
    return """You are a senior attorney who has read this entire document. Perform the DEEP analysis: cross-clause interactions, the drafter's strategic playbook, and overall risk assessment. This requires reasoning across ALL clauses simultaneously — finding what is invisible when reading clause by clause.

## LANGUAGE RULE
Respond in the SAME LANGUAGE as the document.

## OUTPUT FORMAT

## Cross-Clause Interactions

Identify clause COMBINATIONS that create compound risks invisible when reading linearly.

For each interaction:

### [Descriptive Interaction Title]

**Clauses Involved**: [list specific sections]

**How They Interact**: [the mechanism — be very specific]

[RED/YELLOW] · Score: [0-100]/100 · Trick: [TRICK_CATEGORY]

**What the small print says:** What these clauses appear to say independently.

**What you should read:** What they ACTUALLY do when combined — the hidden compound risk.

---

Find at least 3 cross-clause interactions. These are your most valuable findings.

## The Drafter's Playbook

Reveal the strategic architecture as if you were the attorney who designed it:

If I were the attorney who designed this document, my strategic approach was:

1. **[Strategy name]**: [what this achieves for the drafting party]
2. **[Strategy name]**: [what this achieves]
3. **[Strategy name]**: [what this achieves]
4. **[Strategy name]**: [what this achieves]
5. **[Strategy name]**: [what this achieves]

**Bottom Line**: [One sentence — the insight the reader needs most]

## Overall Assessment

**Overall Risk Score: [0-100]/100**

**Power Imbalance Index: [0-100]/100**

**Risk Distribution**: [X] Green · [Y] Yellow · [Z] Red

### Top 3 Concerns
1. **[Title]** — [one sentence]
2. **[Title]** — [one sentence]
3. **[Title]** — [one sentence]

### Recommended Actions
- [Specific, actionable item]
- [Specific, actionable item]
- [Specific, actionable item]

## TRICK CATEGORIES:
- Silent Waiver — Quietly surrenders your legal rights
- Burden Shift — Moves proof/action duty onto you
- Time Trap — Tight deadlines that forfeit your rights
- Escape Hatch — Drafter can exit, you can't
- Moving Target — Can change terms unilaterally
- Forced Arena — Disputes in drafter's chosen forum
- Phantom Protection — Broad coverage eaten by exceptions
- Cascade Clause — One trigger activates penalties in others
- Sole Discretion — Drafter decides everything
- Liability Cap — Limits payout regardless of harm
- Reverse Shield — You cover their costs
- Auto-Lock — Auto-renewal with hard cancellation
- Content Grab — Claims rights over your content
- Data Drain — Expansive hidden data permissions
- Penalty Disguise — Punitive charges disguised as fees
- Gag Clause — Prohibits negative reviews
- Scope Creep — Vague terms stretch beyond expectation
- Ghost Standard — References external docs not included

## RULES
- Focus exclusively on cross-clause interactions, playbook, and assessment
- Do NOT re-analyze individual clauses — that has been done separately
- Cross-clause interactions are your HIGHEST VALUE finding — reason deeply
- The Playbook must reveal strategic architecture, not just list problems
- Use your full extended thinking budget to reason across the entire document
- Be thorough — connect clauses that the reader would never connect on their own"""


@app.route('/compare', methods=['POST'])
def compare():
    """Upload two documents for comparison."""
    try:
        texts = []
        filenames = []

        for key in ['file1', 'file2']:
            if key in request.files and request.files[key].filename:
                file = request.files[key]
                fname = file.filename
                ext = fname.rsplit('.', 1)[-1].lower() if '.' in fname else ''
                if ext == 'pdf':
                    text = extract_pdf(file)
                elif ext == 'docx':
                    text = extract_docx(file)
                elif ext in ('txt', 'text', 'md'):
                    text = file.read().decode('utf-8', errors='replace')
                else:
                    return jsonify({'error': f'Unsupported file type for {key}: .{ext}'}), 400
                texts.append(text)
                filenames.append(fname)
            else:
                tkey = 'text1' if key == 'file1' else 'text2'
                txt = request.form.get(tkey, '').strip()
                if txt:
                    texts.append(txt)
                    filenames.append('Document ' + key[-1])

        if len(texts) < 2:
            return jsonify({'error': 'Please provide two documents to compare.'}), 400

        depth = request.form.get('depth', 'standard')
        doc_id = str(uuid.uuid4())
        documents[doc_id] = {
            'text': texts[0],
            'text2': texts[1],
            'filename': filenames[0],
            'filename2': filenames[1],
            'depth': depth,
            'mode': 'compare',
        }

        return jsonify({
            'doc_id': doc_id,
            'filename': filenames[0] + ' vs ' + filenames[1],
            'text_length': len(texts[0]) + len(texts[1]),
            'preview': texts[0][:150] + '\n---\n' + texts[1][:150],
            'mode': 'compare',
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze/<doc_id>')
def analyze(doc_id):
    if doc_id not in documents:
        return jsonify({'error': 'Document not found.'}), 404

    doc = documents[doc_id]

    def sse(event_type, content=''):
        payload = json.dumps({'type': event_type, 'content': content})
        return f"data: {payload}\n\n"

    def process_stream_event(event, state):
        """Process a streaming event. Returns list of SSE chunks."""
        chunks = []
        if event.type == 'content_block_start':
            state['current_block'] = event.content_block.type
            chunks.append(sse(f'{state["current_block"]}_start'))
        elif event.type == 'content_block_delta':
            if event.delta.type == 'thinking_delta':
                chunks.append(sse('thinking', event.delta.thinking))
            elif event.delta.type == 'text_delta':
                text = event.delta.text
                state['phase_buffer'] += text
                if len(state['phase_buffer']) > 300:
                    state['phase_buffer'] = state['phase_buffer'][-150:]
                for marker, phase_name in PHASE_MARKERS:
                    if (marker in state['phase_buffer']
                            and phase_name not in state['detected_phases']):
                        state['detected_phases'].add(phase_name)
                        chunks.append(sse('phase', phase_name))
                chunks.append(sse('text', text))
        elif event.type == 'content_block_stop':
            if state['current_block']:
                chunks.append(sse(f'{state["current_block"]}_done'))
                state['current_block'] = None
        return chunks

    def run_single_stream(client, user_msg, system_prompt, preset):
        """Single API call — used for comparison mode."""
        state = {
            'current_block': None,
            'phase_buffer': '',
            'detected_phases': set(),
        }
        stream = None
        try:
            yield sse('phase', 'thinking')
            stream = client.messages.create(
                model=MODEL,
                max_tokens=preset['max_tokens'],
                thinking={
                    'type': 'enabled',
                    'budget_tokens': preset['budget_tokens'],
                },
                system=system_prompt,
                messages=[{'role': 'user', 'content': user_msg}],
                stream=True,
            )
            for event in stream:
                for chunk in process_stream_event(event, state):
                    yield chunk
                if event.type == 'message_stop':
                    yield sse('done')
        finally:
            if stream:
                stream.close()

    def run_parallel(client, user_msg, preset):
        """Two parallel API calls: quick clause scan + deep cross-clause analysis."""
        q = queue_module.Queue()

        def worker(label, system_prompt, budget, max_out):
            stream = None
            try:
                stream = client.messages.create(
                    model=MODEL,
                    max_tokens=max_out,
                    thinking={
                        'type': 'enabled',
                        'budget_tokens': budget,
                    },
                    system=system_prompt,
                    messages=[{'role': 'user', 'content': user_msg}],
                    stream=True,
                )
                for event in stream:
                    q.put((label, event))
            except anthropic.APIError as e:
                q.put(('error', f'{label}: {e.message}'))
            except Exception as e:
                q.put(('error', f'{label}: {str(e)}'))
            finally:
                if stream:
                    stream.close()
                q.put((f'{label}_done', None))

        # Launch quick scan (4K thinking) + deep analysis (full budget)
        t_quick = threading.Thread(
            target=worker,
            args=('quick', build_quick_scan_prompt(), 4000, 16000),
            daemon=True,
        )
        t_deep = threading.Thread(
            target=worker,
            args=('deep', build_deep_analysis_prompt(),
                  preset['budget_tokens'], preset['max_tokens']),
            daemon=True,
        )

        yield sse('phase', 'thinking')
        t_quick.start()
        t_deep.start()

        state = {
            'current_block': None,
            'phase_buffer': '',
            'detected_phases': set(),
        }
        quick_done = False
        deep_done = False
        deep_buffer = []

        while not (quick_done and deep_done):
            try:
                source, event = q.get(timeout=1.0)
            except queue_module.Empty:
                continue

            if source == 'quick_done':
                quick_done = True
                yield sse('quick_done')
                # Flush buffered deep events
                for evt in deep_buffer:
                    for chunk in process_stream_event(evt, state):
                        yield chunk
                deep_buffer.clear()
                continue

            if source == 'deep_done':
                deep_done = True
                continue

            if source == 'error':
                yield sse('error', str(event))
                return

            if source == 'quick':
                for chunk in process_stream_event(event, state):
                    yield chunk
            elif source == 'deep':
                if quick_done:
                    for chunk in process_stream_event(event, state):
                        yield chunk
                else:
                    deep_buffer.append(event)

        yield sse('done')

    def generate():
        try:
            client = anthropic.Anthropic()
            is_compare = doc.get('mode') == 'compare'
            depth = doc.get('depth', 'standard')
            preset = DEPTH_PRESETS.get(depth, DEPTH_PRESETS['standard'])

            if is_compare:
                user_msg = (
                    "Compare the following two documents side by side.\n\n"
                    "---BEGIN DOCUMENT A---\n\n"
                    f"{doc['text']}\n\n"
                    "---END DOCUMENT A---\n\n"
                    "---BEGIN DOCUMENT B---\n\n"
                    f"{doc.get('text2', '')}\n\n"
                    "---END DOCUMENT B---"
                )
                yield from run_single_stream(
                    client, user_msg, build_compare_prompt(), preset)
            else:
                user_msg = (
                    "Analyze the following document from the drafter's "
                    "strategic perspective.\n\n"
                    "---BEGIN DOCUMENT---\n\n"
                    f"{doc['text']}\n\n"
                    "---END DOCUMENT---"
                )
                yield from run_parallel(client, user_msg, preset)

        except anthropic.AuthenticationError:
            yield sse('error',
                      'Invalid API key. Check your ANTHROPIC_API_KEY.')
        except anthropic.APIError as e:
            yield sse('error', f'Anthropic API error: {e.message}')
        except Exception as e:
            yield sse('error', str(e))
        finally:
            documents.pop(doc_id, None)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


if __name__ == '__main__':
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        print('\n' + '=' * 60)
        print('  WARNING: ANTHROPIC_API_KEY is not set.')
        print('  Set it in your environment or create a .env file.')
        print('=' * 60 + '\n')

    print('\n  FlipSide — The other side of small print.')
    print('  Powered by Claude Opus 4.6 extended thinking.')
    print('  http://127.0.0.1:5000\n')
    app.run(debug=True, port=5000)
