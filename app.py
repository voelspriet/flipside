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
import time
import threading
import queue as queue_module
from io import BytesIO

from flask import Flask, request, jsonify, render_template, Response
from dotenv import load_dotenv
import anthropic

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['TEMPLATES_AUTO_RELOAD'] = True

documents = {}

MODEL = os.environ.get('FLIPSIDE_MODEL', 'claude-opus-4-6')
FAST_MODEL = os.environ.get('FLIPSIDE_FAST_MODEL', 'claude-haiku-4-5-20251001')

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

# Analysis depth presets — adaptive thinking lets the model decide budget
DEPTH_PRESETS = {
    'quick':    {'max_tokens': 16000},
    'standard': {'max_tokens': 32000},
    'deep':     {'max_tokens': 64000},
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

SAMPLE_DOCUMENT = """QUICKRENT PROPERTY MANAGEMENT
STANDARD RESIDENTIAL LEASE AGREEMENT

Unit 4B, 221 Elm Street, Portland, OR 97201

1. RENT AND LATE FEES

Monthly rent is $1,850, due on the 1st of each month. If rent is not received by 11:59 PM on the 1st, a late fee of $75 per day shall be assessed beginning on the 2nd, with no cap on accumulated late fees. Partial payments shall be applied first to any outstanding late fees, then to the oldest unpaid rent balance. Acceptance of partial payment does not waive the right to collect the full amount owed, including all accumulated late fees. Tenant waives any right to dispute the reasonableness of late fees by signing this lease.

2. MAINTENANCE AND REPAIRS

Tenant shall notify Landlord in writing of any needed repairs within 24 hours of discovery. Landlord will make repairs within a reasonable timeframe, as determined solely by Landlord. If Tenant fails to report a condition within 24 hours, Tenant assumes full financial responsibility for any resulting damage, including damage to adjacent units. Tenant may not withhold rent for any reason, including failure by Landlord to complete repairs. Tenant may not make any repairs or hire any contractor without prior written consent from Landlord.

3. ENTRY AND INSPECTION

Landlord or Landlord's agents may enter the premises for inspection, maintenance, or showing to prospective tenants or buyers upon 12 hours' notice delivered by any method, including text message, email, or note left at the door. In case of emergency, as determined by Landlord, no notice is required. Tenant agrees that determination of what constitutes an emergency rests solely with Landlord. Landlord may install and maintain smart lock systems and retains a master access code at all times.

4. TERMINATION AND SECURITY DEPOSIT

Either party may terminate with 60 days' written notice. Upon termination, Landlord shall inspect the premises and deduct from the security deposit the cost of any cleaning, repairs, or restoration needed to return the unit to its original condition, normal wear and tear excluded. Landlord reserves sole discretion to determine what constitutes normal wear and tear. Disputes regarding deductions shall be resolved by binding arbitration in Landlord's county of registration, with each party bearing its own costs. Tenant waives the right to a jury trial for any dispute arising from this lease.

By signing below, Tenant agrees to all terms and conditions of this lease.

QuickRent Property Management
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
    resp = app.make_response(render_template('index.html'))
    resp.headers['Cache-Control'] = 'no-store'
    return resp


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
            'full_text': text[:5000],
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/sample', methods=['POST'])
def sample():
    data = request.get_json(silent=True) or {}
    role = data.get('role', 'tenant')
    negotiable = data.get('negotiable', True)
    depth = data.get('depth', 'standard')

    doc_id = str(uuid.uuid4())
    documents[doc_id] = {
        'text': SAMPLE_DOCUMENT,
        'filename': 'QuickRent Lease Agreement (Sample)',
        'role': role,
        'negotiable': negotiable,
        'depth': depth,
    }

    return jsonify({
        'doc_id': doc_id,
        'filename': 'QuickRent Lease Agreement (Sample)',
        'text_length': len(SAMPLE_DOCUMENT),
        'preview': SAMPLE_DOCUMENT[:300],
        'full_text': SAMPLE_DOCUMENT[:5000],
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
    """Fast individual clause analysis with READER perspective for flip cards."""
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

> "[Quote key language from the document]"

[READER]: [1-2 sentences of what a normal, non-expert reader would think upon first reading this clause. Trusting, reasonable, slightly optimistic but not naive. This must feel authentic — something the reader would recognize as their own thought. Examples: "This seems fair — five days is a reasonable grace period." or "Standard maintenance responsibility. Makes sense that I'd report issues quickly." Write in second person.]

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
- Every clause gets: quote + [READER] perspective + risk level + score + trick + juxtaposition
- The [READER] line captures the reader's naive first impression — what they'd think before seeing the analysis
- "What you should read" reveals the reader's reality — the gap between words and what they mean
- Quote exact language from the document
- Be thorough but fast — cross-clause interactions will be analyzed separately"""


def build_card_scan_prompt():
    """Fast card scan for Haiku — SHORT flip card content, one sentence per field."""
    return """You are a contract analyst performing a fast initial scan. Analyze each clause individually, producing SHORT flip-card content. Speed matters — output each clause as soon as you analyze it.

## LANGUAGE RULE
Respond in the SAME LANGUAGE as the document. If the document is in Dutch, respond entirely in Dutch. If German, German. Match the document's language for ALL output including headers and labels.

## OUTPUT FORMAT

Output the Document Profile first, then each clause separated by --- on its own line.

## Document Profile
- **Document Type**: [type of document]
- **Drafted By**: [who drafted it]
- **Your Role**: [the non-drafting party's role]
- **Jurisdiction**: [jurisdiction if identifiable, otherwise "Not specified"]
- **Sections**: [number of major sections]

---

Then for EACH significant clause, output exactly this format:

### [Descriptive Title] ([Section Reference])

> "[Copy-paste the most revealing sentence or phrase from this clause exactly as written in the document. Do NOT paraphrase.]"

[READER]: [One sentence. What a reasonable person would think when first reading this clause. Trusting, slightly optimistic tone. Second person. Examples: "Seems fair — five days is plenty of time to pay." / "Standard maintenance rules. Of course I'd report problems quickly." / "Makes sense they'd need to enter for emergencies."]

[GREEN/YELLOW/RED] · Score: [0-100]/100 · Trick: [CATEGORY]

**Bottom line:** [One sentence visible before flipping. GREEN: confirm it's fair. YELLOW/RED: name the specific risk in plain language. Be concrete, not vague.]

**What the small print says:** [One sentence. Plain restatement of what this clause literally says. Neutral tone.]

**What you should read:** [One sentence. What this ACTUALLY means for the reader. Direct, specific. If alarming, be alarming.]

---

## RISK LEVELS
- GREEN · Score: 0-30 — Fair, balanced, no hidden intent
- YELLOW · Score: 31-65 — Imbalanced, unusual, or worth scrutiny
- RED · Score: 66-100 — Clearly favors the drafter, potential harm to reader

## TRICK CATEGORIES (pick exactly one per clause, best match):
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

## RULES
1. Output each clause immediately — do NOT wait to analyze all clauses before outputting
2. Every clause MUST end with --- on its own line
3. Every clause MUST have: quote, [READER] line, risk level with score and trick, bottom line, juxtaposition
4. Quotes must be EXACT text from the document — copy-paste, do not paraphrase
5. Keep each field to ONE sentence. Cards must be scannable, not essays
6. The [READER] voice should feel like the reader's own inner monologue — natural, not robotic
7. "What you should read" is the core insight — make it visceral
8. Do NOT include negotiation advice or action items — those come from deep analysis
9. Do NOT include cross-clause interactions — analyze each clause independently
10. The Document Profile must appear BEFORE the first clause, followed by ---"""


def build_deep_analysis_prompt():
    """Deep cross-clause analysis with DRAFTER perspective, playbook, and assessment."""
    return """You are a senior attorney who has read this entire document. Perform the DEEP analysis: cross-clause interactions, the drafter's strategic playbook, and overall risk assessment. This requires reasoning across ALL clauses simultaneously — finding what is invisible when reading clause by clause.

## LANGUAGE RULE
Respond in the SAME LANGUAGE as the document.

## OUTPUT FORMAT

## Cross-Clause Interactions

Identify clause COMBINATIONS that create compound risks invisible when reading linearly.

For each interaction:

### [Descriptive Interaction Title]

**Read separately, you'd see:** What these clauses appear to say independently. One sentence.

**Read together, you'd realize:** What they ACTUALLY do when combined — the hidden compound risk. One sentence, visceral.

**Clauses Involved**: [list specific sections]

**How They Interact**: [2-3 sentences. The mechanism — be very specific about HOW the clauses feed into each other.]

[RED/YELLOW] · Trick: [TRICK_CATEGORY]

**If the drafter could speak freely:** [2-3 sentences reconstructing what the person who designed this clause combination was likely trying to achieve. Speak as if the drafter is explaining the strategy to a colleague. Professional, strategic, calm — not villainous. Use "we" language. Example: "The 24-hour reporting requirement pairs nicely with the damage liability clause. If a tenant misses the window — and most will for minor issues — they've assumed financial responsibility. We've converted a reporting rule into a revenue mechanism."]

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

**Overall Risk Score: [0-100]/100** — How much this document can hurt you.

**Power Imbalance Index: [0-100]/100** — How little you can do about it.

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
- Every cross-clause interaction MUST include an "If the drafter could speak freely" section — the drafter's voice explaining the strategic architecture
- The drafter's voice should sound like a professional in a meeting, not a villain. Use "we" language.
- LEAD each interaction with "Read separately / Read together" — that's the hook. The drafter's voice is supporting evidence, placed AFTER.
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
            'full_text': texts[0][:5000],
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
                thinking={'type': 'adaptive'},
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
        """Two parallel API calls: Haiku card scan (fast) + Opus deep analysis."""
        q = queue_module.Queue()
        timings = {}

        def worker(label, system_prompt, max_out,
                   model=MODEL, use_thinking=True):
            stream = None
            t0 = time.time()
            try:
                create_kwargs = {
                    'model': model,
                    'max_tokens': max_out,
                    'system': system_prompt,
                    'messages': [{'role': 'user', 'content': user_msg}],
                    'stream': True,
                }
                if use_thinking:
                    create_kwargs['thinking'] = {'type': 'adaptive'}
                stream = client.messages.create(**create_kwargs)
                for event in stream:
                    q.put((label, event))
            except anthropic.APIError as e:
                q.put(('error', f'{label}: {e.message}'))
            except Exception as e:
                q.put(('error', f'{label}: {str(e)}'))
            finally:
                if stream:
                    stream.close()
                timings[label] = round(time.time() - t0, 1)
                q.put((f'{label}_done', None))

        # Haiku for fast card scan (no extended thinking)
        t_quick = threading.Thread(
            target=worker,
            args=('quick', build_card_scan_prompt(), 8000,
                  FAST_MODEL, False),
            daemon=True,
        )
        # Opus for deep cross-clause analysis (extended thinking)
        t_deep = threading.Thread(
            target=worker,
            args=('deep', build_deep_analysis_prompt(),
                  preset['max_tokens'], MODEL, True),
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
                qt = timings.get('quick', 0)
                yield sse('quick_done', json.dumps({
                    'seconds': qt, 'model': FAST_MODEL}))
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

        dt = timings.get('deep', 0)
        yield sse('done', json.dumps({
            'quick_seconds': timings.get('quick', 0),
            'deep_seconds': dt, 'model': MODEL}))

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

    port = int(os.environ.get('FLIPSIDE_PORT', 5001))
    print('\n  FlipSide — The other side of small print.')
    print(f'  Powered by Claude Opus 4.6 + Haiku 4.5 (fast cards).')
    print(f'  http://127.0.0.1:{port}\n')
    app.run(debug=True, port=port)
