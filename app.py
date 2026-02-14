"""
FlipSide — The dark side of small print.
Upload a document you didn't write. See what the other side intended.

Optimized for Claude Opus 4.6 extended thinking:
- Meta-prompting framework for adversarial document analysis
- 32K thinking budget (deep mode) for multi-pass cross-clause reasoning
- Drafter's Playbook: reveals the strategic architecture behind the document
- Phased SSE streaming with real-time phase detection
"""

import os
import re
import uuid
import json
import time
import threading
import queue as queue_module
import base64
from io import BytesIO

from flask import Flask, request, jsonify, render_template, Response
from dotenv import load_dotenv
import httpx
import anthropic

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['TEMPLATES_AUTO_RELOAD'] = True

documents = {}
_documents_lock = threading.Lock()
DOCUMENT_TTL = 30 * 60  # 30 minutes

def _evict_stale_documents():
    """Remove documents older than DOCUMENT_TTL."""
    now = time.time()
    with _documents_lock:
        stale = [k for k, v in documents.items() if now - v.get('_ts', 0) > DOCUMENT_TTL]
        for k in stale:
            del documents[k]

def store_document(doc_id, doc):
    """Store a document with a timestamp, evicting stale entries first."""
    _evict_stale_documents()
    doc['_ts'] = time.time()
    with _documents_lock:
        documents[doc_id] = doc
    # Pre-scan + pre-generate cards during upload (skip compare mode)
    if doc.get('mode') != 'compare':
        doc['_prescan_event'] = threading.Event()
        doc['_precards_event'] = threading.Event()
        threading.Thread(
            target=_prescan_document, args=(doc_id,), daemon=True
        ).start()


def _prescan_document(doc_id):
    """Background: identify clauses AND pre-generate cards during upload.
    Phase 1 (~7s): clause identification → sets _prescan_event
    Phase 2 (~8s): parallel card generation → sets _precards_event
    By the time user clicks Analyze, cards are already done."""
    doc = documents.get(doc_id)
    if not doc or not doc.get('text'):
        if doc:
            doc['_prescan'] = None
            doc.get('_prescan_event', threading.Event()).set()
            doc.get('_precards_event', threading.Event()).set()
        return
    try:
        import anthropic as _anthropic
        client = _anthropic.Anthropic()
        fast_model = os.environ.get('FLIPSIDE_FAST_MODEL', 'claude-haiku-4-5-20251001')
        user_msg = (
            "Analyze the following document from the drafter's "
            "strategic perspective.\n\n"
            "---BEGIN DOCUMENT---\n\n"
            f"{doc['text']}\n\n"
            "---END DOCUMENT---"
        )

        # ── Phase 1: Identification scan ──
        t0 = time.time()
        response = client.messages.create(
            model=fast_model,
            max_tokens=4000,
            system=[{
                'type': 'text',
                'text': build_clause_id_prompt(),
                'cache_control': {'type': 'ephemeral'},
            }],
            messages=[{'role': 'user', 'content': user_msg}],
        )
        scan_text = response.content[0].text
        profile_text, clauses, green_text = parse_identification_output(scan_text)
        scan_seconds = round(time.time() - t0, 1)
        doc['_prescan'] = {
            'scan_text': scan_text,
            'profile_text': profile_text,
            'clauses': clauses,
            'green_text': green_text,
            'seconds': scan_seconds,
        }
        print(f'[prescan] {doc_id[:8]}: {len(clauses)} clauses in {scan_seconds}s')
        doc.get('_prescan_event', threading.Event()).set()

        # ── Phase 2: Pre-generate cards in parallel ──
        if clauses and '**Not Applicable**' not in scan_text:
            card_system = build_single_card_system(doc['text'])
            total_cards = len(clauses) + (1 if green_text else 0)
            card_results = {}
            card_events = {}

            def card_worker(idx, user_content):
                try:
                    resp = client.messages.create(
                        model=fast_model,
                        max_tokens=4000,
                        system=[{
                            'type': 'text',
                            'text': card_system,
                            'cache_control': {'type': 'ephemeral'},
                        }],
                        messages=[{'role': 'user', 'content': user_content}],
                    )
                    card_results[idx] = resp.content[0].text
                except Exception as e:
                    print(f'[precard] {doc_id[:8]} card {idx}: Error: {e}')
                    card_results[idx] = ''
                finally:
                    card_events[idx].set()

            for i, clause_info in enumerate(clauses):
                card_events[i] = threading.Event()
                card_user_msg = (
                    f"Generate a complete flip card for this specific clause:\n\n"
                    f"Title: {clause_info['title']}\n"
                    f"Section Reference: {clause_info.get('section', 'Not specified')}\n"
                    f"Risk Level: {clause_info['risk']}\n"
                    f"Score: {clause_info['score']}/100\n"
                    f"Trick Category: {clause_info['trick']}\n"
                    f"Key Quote: \"{clause_info['quote']}\"\n\n"
                    f"Analyze the clause in the document and output the COMPLETE flip card."
                )
                threading.Thread(
                    target=card_worker, args=(i, card_user_msg), daemon=True
                ).start()

            if green_text:
                green_idx = len(clauses)
                card_events[green_idx] = threading.Event()
                threading.Thread(
                    target=card_worker,
                    args=(green_idx, build_green_summary_user(green_text)),
                    daemon=True,
                ).start()

            # Wait for all cards
            for idx in range(total_cards):
                card_events[idx].wait(timeout=30)

            cards_seconds = round(time.time() - t0 - scan_seconds, 1)
            doc['_precards'] = {
                'cards': [card_results.get(i, '') for i in range(total_cards)],
                'seconds': cards_seconds,
            }
            print(f'[precard] {doc_id[:8]}: {total_cards} cards in {cards_seconds}s '
                  f'(total {round(scan_seconds + cards_seconds, 1)}s)')
        else:
            doc['_precards'] = None

    except Exception as e:
        print(f'[prescan] {doc_id[:8]}: Error: {e}')
        doc['_prescan'] = doc.get('_prescan')  # Keep Phase 1 if it succeeded
        if not doc.get('_prescan'):
            doc['_prescan'] = None
    finally:
        doc.get('_prescan_event', threading.Event()).set()
        doc.get('_precards_event', threading.Event()).set()


def _build_claims_summary(prescan, precards):
    """Build a concise summary of all flagged claims for the Opus verdict prompt.
    Parses pre-generated card texts to extract key findings per clause."""
    if not prescan or not precards:
        return ''
    clauses = prescan.get('clauses', [])
    cards = precards.get('cards', [])
    if not clauses or not cards:
        return ''

    lines = [
        '## PRE-ANALYZED FLAGGED CLAIMS',
        'The card scan identified these flagged clauses. Reference them in your verdict — '
        'ensure [FLAGGED_CLAIMS] covers ALL of them with consumer impact.\n',
    ]
    for i, card_text in enumerate(cards):
        if not card_text or 'Fair Clauses Summary' in card_text:
            continue
        # Extract title from ### heading
        title_match = re.search(r'^###\s+(.+)', card_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f'Clause {i + 1}'
        # Extract risk/score/trick from [RED] · Score: 85/100 · Trick: ...
        risk_match = re.search(
            r'\[(RED|YELLOW|GREEN)\]\s*[·•]\s*Score:\s*(\d+)/100\s*[·•]\s*Trick:\s*(.+)',
            card_text)
        if risk_match:
            risk, score, trick = risk_match.group(1), risk_match.group(2), risk_match.group(3).strip()
        elif i < len(clauses):
            risk, score, trick = clauses[i]['risk'], clauses[i]['score'], clauses[i]['trick']
        else:
            risk, score, trick = '?', '?', 'Unknown'
        # Extract REVEAL, bottom line, FIGURE
        reveal_m = re.search(r'\[REVEAL\]:\s*(.+)', card_text)
        bl_m = re.search(r'\*\*Bottom line:\*\*\s*(.+)', card_text)
        fig_m = re.search(r'\[FIGURE\]:\s*(.+)', card_text)
        reveal = reveal_m.group(1).strip() if reveal_m else ''
        bottom_line = bl_m.group(1).strip() if bl_m else ''
        figure = fig_m.group(1).strip() if fig_m else ''

        lines.append(f'Claim {i + 1}: {title}')
        lines.append(f'  Risk: {risk} | Score: {score}/100 | Trick: {trick}')
        if reveal:
            lines.append(f'  Finding: {reveal}')
        if figure:
            lines.append(f'  Impact: {figure}')
        if bottom_line:
            lines.append(f'  Bottom line: {bottom_line}')
        lines.append('')

    return '\n'.join(lines)


MODEL = os.environ.get('FLIPSIDE_MODEL', 'claude-opus-4-6')
FAST_MODEL = os.environ.get('FLIPSIDE_FAST_MODEL', 'claude-haiku-4-5-20251001')
SYNTHESIS_MAX_TOKENS = 8000  # ~1500 words + thinking for expert panel synthesis

# Module-level client for utility functions (text cleaning etc.)
_client = None
def get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client

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

# Analysis depth presets — token budget per depth level
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

SAMPLE_DOCUMENTS = {

'lease': {
    'filename': 'QuickRent Lease Agreement (Sample)',
    'text': """QUICKRENT PROPERTY MANAGEMENT
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
},

'insurance': {
    'filename': 'SafeGuard Home Insurance Policy (Sample)',
    'text': """SAFEGUARD MUTUAL INSURANCE COMPANY
HOMEOWNER'S INSURANCE POLICY — STANDARD COVERAGE

Policy No. HO-2026-4481927
Effective: January 1, 2026 – December 31, 2026
Named Insured: [Policyholder]
Covered Property: 847 Maple Drive, Austin, TX 78703

SECTION 1 — DWELLING COVERAGE

Your dwelling is covered for direct physical loss up to $425,000, including attached structures, built-in appliances, and permanent fixtures. This broad coverage protects your home from fire, lightning, windstorm, hail, explosion, riot, aircraft, vehicles, smoke, vandalism, theft, falling objects, weight of ice and snow, and sudden accidental discharge of water or steam.

SECTION 2 — PERSONAL PROPERTY

Personal belongings are covered up to 70% of dwelling coverage ($297,500) at actual cash value. Replacement cost coverage is available for an additional premium. Items stored off-premises are covered up to 10% of personal property coverage. Special limits apply: $200 for cash and securities; $1,500 for jewelry, watches, and furs (aggregate); $2,500 for firearms; $1,000 for watercraft.

SECTION 3 — LIABILITY PROTECTION

Personal liability coverage of $100,000 per occurrence for bodily injury or property damage claims. Medical payments coverage of $1,000 per person for injuries on your property regardless of fault.

SECTION 4 — EXCLUSIONS

4(a) Earth Movement. Loss caused by earthquake, landslide, mudflow, sinkhole, subsidence, or any earth movement, whether natural or man-made, is excluded. This exclusion applies even if fire, explosion, or flooding follows the earth movement.

4(b) Water Damage. Loss caused by flood, surface water, waves, tidal water, overflow of a body of water, or spray from any of these, whether or not driven by wind, is excluded. Loss caused by water that backs up through sewers or drains, or water below the surface of the ground that seeps through foundations, walls, or floors is excluded.

4(c) Gradual Damage. Loss resulting from wear and tear, deterioration, rust, corrosion, mold, wet or dry rot, contamination, smog, settling, cracking, shrinkage, bulging, or expansion is excluded. Loss caused by insects, rodents, or vermin is excluded. Loss caused by gradual seepage or leakage of water or steam over a period of more than 14 days is excluded.

4(d) Maintenance Failures. Loss resulting from faulty, inadequate, or defective planning, design, workmanship, materials, or maintenance is excluded. If a covered peril ensues, we cover the ensuing loss, but not the cost of correcting the original defect.

4(e) Vacancy. If the dwelling has been vacant for more than 60 consecutive days, coverage for vandalism, glass breakage, water damage, and theft is suspended. All other covered losses are subject to a 25% reduction in payment.

4(f) Timing of Claims. All claims must be filed within 90 days of the date of loss. Failure to file within this period constitutes a waiver of the claim. Proof of loss must include dated photographs, original receipts, and a sworn statement. The insurer reserves the right to inspect the premises and examine the insured under oath before paying any claim.

SECTION 5 — DEDUCTIBLES AND PAYMENT

Standard deductible: $2,500 per occurrence. Wind/hail deductible: 2% of dwelling coverage ($8,500). The insurer shall pay covered losses within 60 days of proof of loss, or within such longer period as may be reasonably necessary to complete investigation. Payment shall be made at actual cash value until repairs are completed, at which point the difference to replacement cost will be paid upon submission of receipts. If the cost of repairs exceeds 50% of the dwelling's replacement value, the insurer may elect to pay the actual cash value of the dwelling and cancel the policy.

SECTION 6 — POLICY CONDITIONS

This policy may be cancelled by the insurer with 30 days' written notice for any reason during the first 60 days. After 60 days, the insurer may cancel for non-payment of premium (10 days' notice) or material misrepresentation. The insured may cancel at any time; refunds are calculated on a short-rate basis (not pro rata). In the event of a loss, the insured's duties include protecting the property from further damage, cooperating fully with the insurer's investigation, and submitting to examination under oath. Any disagreement about the value of a claim shall be resolved by appraisal, with each party selecting an appraiser at its own expense.

SafeGuard Mutual Insurance Company
[Authorized Representative]
"""
},

'tos': {
    'filename': 'CloudVault Terms of Service (Sample)',
    'text': """CLOUDVAULT INC.
TERMS OF SERVICE
Last updated: January 15, 2026

By creating an account or using any CloudVault service, you agree to these Terms of Service ("Terms"). If you do not agree, do not use our services.

1. YOUR ACCOUNT

You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You must be at least 16 years old to create an account. You agree to provide accurate, current, and complete information. CloudVault reserves the right to suspend or terminate accounts that contain inaccurate information or that have been inactive for more than 12 months. Upon termination of an inactive account, all stored data will be permanently deleted without notice.

2. YOUR CONTENT

You retain ownership of content you upload to CloudVault ("Your Content"). By uploading Your Content, you grant CloudVault a worldwide, royalty-free, sublicensable, transferable license to use, reproduce, modify, distribute, display, and create derivative works from Your Content for the purposes of operating, promoting, and improving our services. This license survives termination of your account. You represent that you have all rights necessary to grant this license.

3. DATA COLLECTION AND USE

CloudVault collects: (a) information you provide (name, email, payment info); (b) content you upload or create; (c) usage data including access times, pages viewed, files accessed, search queries, and features used; (d) device information including IP address, browser type, operating system, device identifiers, and location data; (e) information from third-party services you connect. We may share aggregated or de-identified data with third parties for any purpose, including advertising, analytics, and research. We may share personal data with service providers, business partners, and affiliates. In the event of a merger, acquisition, or sale of assets, your data may be transferred to the acquiring entity.

4. PRIVACY AND SECURITY

CloudVault employs industry-standard security measures to protect your data. However, no method of electronic storage is 100% secure. CloudVault does not guarantee absolute security and shall not be liable for any unauthorized access to your data. You acknowledge that you upload content at your own risk. CloudVault may access your content to enforce these Terms, comply with legal requirements, or respond to claims that content violates third-party rights. CloudVault may also access, analyze, and scan your content using automated systems for the purposes of service improvement, feature development, and training of machine learning models.

5. SERVICE AVAILABILITY

CloudVault aims to provide 99.9% uptime but does not guarantee uninterrupted service. We may modify, suspend, or discontinue any feature or service at any time without notice. Free-tier accounts may experience reduced performance, limited storage, or feature restrictions at CloudVault's discretion. We are not liable for any loss of data, lost profits, or business interruption resulting from service unavailability, regardless of the cause.

6. PAYMENT AND SUBSCRIPTION

Paid subscriptions automatically renew at the end of each billing period at the then-current rate. Price increases take effect at the next renewal date. You must cancel at least 7 days before the renewal date to avoid being charged. Refunds are not provided for partial billing periods or unused time. If payment fails, CloudVault will attempt to charge the payment method on file for 14 days. After 14 days of failed payment, your account will be downgraded to free tier and data exceeding the free storage limit will be scheduled for deletion after 30 days.

7. LIMITATION OF LIABILITY

TO THE MAXIMUM EXTENT PERMITTED BY LAW, CLOUDVAULT'S TOTAL LIABILITY FOR ANY CLAIMS ARISING FROM THESE TERMS OR YOUR USE OF THE SERVICES SHALL NOT EXCEED THE AMOUNT YOU PAID TO CLOUDVAULT IN THE TWELVE (12) MONTHS PRIOR TO THE CLAIM. CLOUDVAULT SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING LOSS OF DATA, LOSS OF PROFITS, OR BUSINESS INTERRUPTION, REGARDLESS OF THE THEORY OF LIABILITY.

8. DISPUTE RESOLUTION

Any dispute arising from these Terms shall be resolved by binding arbitration administered by the American Arbitration Association in San Francisco, California. You agree to waive your right to participate in a class action lawsuit or class-wide arbitration. The arbitrator's decision is final and binding. You agree that any dispute must be brought within one (1) year after the cause of action arises, or be permanently barred.

9. CHANGES TO TERMS

CloudVault may modify these Terms at any time. Continued use of the service after modifications constitutes acceptance of the updated Terms. If you do not agree with the changes, your sole remedy is to delete your account.

CloudVault Inc.
San Francisco, CA
"""
},

'employment': {
    'filename': 'TechForward Employment Agreement (Sample)',
    'text': """TECHFORWARD SOLUTIONS LLC
EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into between TechForward Solutions LLC ("Company") and the undersigned employee ("Employee"), effective upon the Employee's start date.

1. POSITION AND DUTIES

Employee is hired as Senior Software Engineer, reporting to the VP of Engineering. Employee agrees to devote full professional time and effort to the Company. Employee shall not engage in any outside employment, consulting, or business activity without prior written approval from the Company, whether or not such activity competes with the Company.

2. COMPENSATION

Base salary: $145,000 per year, paid bi-weekly. Salary reviews occur annually at the Company's discretion; the Company is under no obligation to increase compensation. Bonus: Employee may be eligible for an annual performance bonus of up to 15% of base salary, at the sole discretion of management. Bonus criteria and targets may change at any time. No bonus is earned or payable if Employee is not actively employed on the bonus payment date.

3. AT-WILL EMPLOYMENT

Employment is at-will. Either party may terminate the employment relationship at any time, for any reason or no reason, with or without cause or notice. No provision of this Agreement, any Company policy, handbook, or statement by any Company representative shall be construed to alter the at-will nature of employment. The at-will nature of employment cannot be modified except by a written agreement signed by the CEO.

4. INTELLECTUAL PROPERTY ASSIGNMENT

Employee assigns to the Company all rights, title, and interest in any invention, discovery, design, code, algorithm, process, technique, improvement, or work of authorship ("Work Product") conceived, developed, or reduced to practice during employment, whether or not during working hours, whether or not using Company resources, and whether or not related to the Company's current or anticipated business. Employee agrees to execute any documents necessary to perfect the Company's ownership. This assignment includes all patents, copyrights, trade secrets, and other intellectual property rights worldwide. Employee waives all moral rights in the Work Product.

5. NON-COMPETE AND NON-SOLICITATION

For a period of 18 months following termination of employment for any reason, Employee shall not: (a) engage in, be employed by, consult for, or have any ownership interest in any business that competes with the Company's products or services, anywhere in North America; (b) solicit, recruit, or hire any employee, contractor, or consultant of the Company; (c) solicit or service any customer or prospective customer with whom Employee had contact during the last 24 months of employment. The Company may extend the non-compete period by an additional 12 months by providing written notice before the original period expires.

6. CONFIDENTIALITY

Employee shall not, during or after employment, disclose any Confidential Information. "Confidential Information" includes all non-public information about the Company's business, including but not limited to: code, algorithms, data, product plans, financial information, customer lists, pricing, marketing strategies, personnel information, vendor relationships, and any information designated as confidential. This obligation survives termination of employment indefinitely. Employee shall not retain copies of any Confidential Information upon termination.

7. MANDATORY ARBITRATION

Any dispute arising from this Agreement or the employment relationship shall be resolved by final and binding arbitration in accordance with the rules of JAMS, in the Company's principal office location. Employee waives the right to a jury trial and to participate in any class or collective action. The arbitrator may not award punitive or exemplary damages. Each party bears its own attorney's fees and costs. This arbitration clause survives termination of employment.

8. SEVERANCE

If the Company terminates Employee's employment without Cause, Employee will receive 2 weeks of base salary as severance, contingent upon execution of a full release of all claims against the Company. "Cause" includes: unsatisfactory performance as determined by the Company, violation of any Company policy, any conduct the Company deems detrimental to its interests, or any other reason the Company considers sufficient.

TechForward Solutions LLC
[Authorized Representative]

Employee Signature: _______________
Date: _______________
"""
},

'loan': {
    'filename': 'QuickCash Personal Loan Agreement (Sample)',
    'text': """QUICKCASH FINANCIAL SERVICES
PERSONAL LOAN AGREEMENT

Loan No. QC-2026-08834
Borrower: [Borrower Name]
Date: February 1, 2026

1. LOAN TERMS

Principal Amount: $15,000. Annual Percentage Rate (APR): 24.99% fixed. Term: 48 months. Monthly Payment: $494.17, due on the 15th of each month. Total amount payable over the life of the loan: $23,720.16 (principal + $8,720.16 in interest).

2. LATE PAYMENT

If any payment is not received within 5 days of the due date, a late fee of $39 or 5% of the payment amount (whichever is greater) shall be assessed. If payment is more than 30 days late, the interest rate on the remaining balance shall increase to 29.99% APR for the remainder of the loan term. This rate increase is permanent and cannot be reversed by bringing the account current. A second late payment within any 12-month period triggers an additional rate increase to 34.99% APR.

3. PREPAYMENT

Borrower may prepay the loan in full or in part at any time. However, if prepayment occurs within the first 24 months, a prepayment penalty of 3% of the remaining principal balance shall apply. Partial prepayments are applied first to accrued interest and fees, then to principal. Partial prepayment does not reduce the monthly payment amount; it reduces the number of remaining payments.

4. DEFAULT AND ACCELERATION

The loan is in default if: (a) any payment is more than 60 days past due; (b) Borrower files for bankruptcy; (c) Borrower provides false information on the application; (d) Borrower's credit score drops below 580 at any point during the loan term; (e) Borrower's employment status changes and Borrower fails to notify QuickCash within 15 days. Upon default, the entire remaining principal balance, plus all accrued interest and fees, becomes immediately due and payable. QuickCash may report the default to all credit bureaus and may assign the debt to a collection agency, with collection costs added to the balance owed.

5. SECURITY INTEREST

As security for this loan, Borrower grants QuickCash a security interest in all personal property currently owned or hereafter acquired by Borrower, including but not limited to: bank accounts, investment accounts, vehicles, electronics, furniture, and other tangible personal property. Upon default, QuickCash may take possession of secured property without prior notice and sell it to satisfy the outstanding balance.

6. MANDATORY ARBITRATION AND DISPUTE RESOLUTION

Any dispute arising from this Agreement shall be resolved through binding arbitration administered by the National Arbitration Forum in QuickCash's home jurisdiction (Wilmington, Delaware). Borrower waives the right to a jury trial and waives the right to participate in any class action. The arbitrator's fees shall be borne by the losing party. Borrower agrees that QuickCash may pursue collection through any court of competent jurisdiction notwithstanding this arbitration clause.

7. COMMUNICATIONS CONSENT

Borrower consents to receiving communications from QuickCash and its agents by any means, including telephone calls, text messages, and emails, at any number or address provided, including auto-dialed or pre-recorded calls. This consent applies to any phone number associated with Borrower's account, including numbers added in the future. Borrower may not revoke this consent while any balance remains outstanding.

8. GOVERNING LAW AND AMENDMENTS

This Agreement is governed by the laws of Delaware. QuickCash may amend the terms of this Agreement, including interest rates and fees, with 15 days' written notice. Continued acceptance of the loan after notice constitutes agreement to the amended terms. If any provision is found unenforceable, all remaining provisions remain in full effect.

QuickCash Financial Services
Wilmington, DE
[Authorized Signature]
"""
},

'gym': {
    'filename': 'IronClad Fitness Membership Agreement (Sample)',
    'text': """IRONCLAD FITNESS CENTERS
MEMBERSHIP AGREEMENT

Member: [Member Name]
Location: IronClad Fitness — Downtown, 500 Main Street
Membership Type: Premium All-Access
Start Date: February 1, 2026

1. MEMBERSHIP TERM AND RENEWAL

Initial term: 12 months. Monthly dues: $79.99, plus an annual enhancement fee of $49.99 charged each January. Membership automatically renews for successive 12-month terms unless cancelled. To cancel, Member must provide written notice by certified mail, received at IronClad's corporate office at least 45 days before the end of the current term. Cancellation requests submitted by email, phone, or in-person are not valid. Early termination fee: remaining months' dues multiplied by 75%, due immediately upon early cancellation.

2. SERVICES AND FACILITY ACCESS

Member has access to all IronClad locations during staffed hours. IronClad reserves the right to modify hours, close locations, discontinue equipment, programs, or amenities at any time without notice and without reduction in dues. Certain classes, training programs, and amenities (sauna, pool, recovery rooms) may require additional fees. IronClad may designate any program or amenity as "premium" at any time.

3. HEALTH AND SAFETY

Member represents that they are physically fit and have no medical condition that would prevent safe exercise. Member assumes all risk of injury, illness, or death arising from use of IronClad's facilities, equipment, classes, or programs, including risks arising from the negligence of IronClad, its employees, or other members. Member agrees to consult a physician before beginning any exercise program but acknowledges that IronClad has no duty to verify Member's fitness or medical status.

4. WAIVER OF LIABILITY AND INDEMNIFICATION

Member waives all claims against IronClad, its owners, officers, employees, agents, and contractors for any injury, loss, damage, or death, including claims arising from IronClad's negligence, defective equipment, inadequate supervision, or failure to maintain safe conditions. Member agrees to indemnify and hold harmless IronClad from any claims by Member or Member's family, heirs, or estate. This waiver extends to injuries caused by other members or third parties on IronClad premises.

5. PERSONAL TRAINING AND ADDITIONAL SERVICES

Personal training packages are non-refundable. Unused sessions expire 90 days after purchase. Sessions must be cancelled at least 24 hours in advance; late cancellations are charged as completed sessions. Personal training rates may increase with 30 days' notice. IronClad reserves the right to assign any available trainer; Member may not select or refuse a specific trainer.

6. BILLING AND COLLECTIONS

Dues are charged to the payment method on file on the 1st of each month. If payment fails, IronClad will attempt to charge the payment method for 30 days. After 30 days of failed payment, the full remaining balance for the membership term becomes immediately due. Accounts more than 60 days past due may be referred to a collection agency. Member agrees to pay all collection costs, including agency fees up to 35% of the balance and reasonable attorney's fees.

7. GUEST AND FAMILY POLICY

Members may bring guests for a $20 per-visit fee. Guests must sign a liability waiver. Member is responsible for their guest's conduct and any damage caused by their guest. Family add-on memberships are available but are subject to separate terms and may not be cancelled independently of the primary membership.

8. PHOTO AND MEDIA RELEASE

By entering any IronClad facility, Member consents to being photographed, filmed, or recorded. IronClad may use Member's image, likeness, and voice in marketing, advertising, social media, and promotional materials without compensation, attribution, or prior notice. This consent is irrevocable and survives termination of membership.

9. DISPUTE RESOLUTION

Any dispute arising from this Agreement or membership shall be resolved by binding arbitration in the county of IronClad's corporate headquarters. Member waives the right to a jury trial and class action participation. The prevailing party is entitled to reasonable attorney's fees. Claims must be brought within 6 months of the event giving rise to the dispute.

IronClad Fitness Centers
[General Manager Signature]
"""
},

'medical': {
    'filename': 'Lakewood Medical Center Consent Form (Sample)',
    'text': """LAKEWOOD MEDICAL CENTER
PATIENT CONSENT AND AGREEMENT FORM

Patient: [Patient Name]
Date of Service: _______________
Provider: Lakewood Medical Center and affiliated practitioners

1. CONSENT TO TREATMENT

I consent to examinations, diagnostic procedures, treatments, and medical care by the physicians, nurses, and staff at Lakewood Medical Center and any affiliated or consulting practitioners, including telemedicine providers. I understand that medicine is not an exact science and that no guarantees have been made regarding the outcome of any treatment or procedure. I authorize my care team to perform such procedures as are necessary or advisable in their professional judgment, including procedures not specifically described to me in advance.

2. ACKNOWLEDGMENT OF RISKS

I acknowledge that all medical treatment carries inherent risks, including but not limited to: adverse reactions to medications, infection, bleeding, nerve damage, organ damage, disability, disfigurement, and death. I acknowledge that I have been given the opportunity to ask questions about proposed treatments and their alternatives. By signing this form, I confirm that my questions have been answered to my satisfaction, whether or not I actually asked any questions.

3. FINANCIAL RESPONSIBILITY

I agree to be personally responsible for all charges not covered by insurance. I understand that Lakewood Medical Center's providers may or may not participate in my insurance network, and that services rendered by out-of-network providers, including anesthesiologists, radiologists, pathologists, and consulting specialists, will be billed separately at the provider's standard rates. I agree to pay any balance remaining after insurance, including co-pays, deductibles, and denied claims, within 30 days of billing. Accounts not paid within 60 days are subject to a 1.5% monthly finance charge and may be referred to collections.

4. AUTHORIZATION FOR RELEASE OF INFORMATION

I authorize Lakewood Medical Center to release my medical records and health information to: my insurance company, any referring physician, any physician or facility involved in my care, government agencies as required by law, and any other party as Lakewood deems necessary for treatment, payment, or healthcare operations. I understand that once information is disclosed, it may no longer be protected by federal privacy regulations.

5. ADVANCE DIRECTIVE AND REPRESENTATIVE

If I become unable to make medical decisions, I authorize Lakewood Medical Center to make treatment decisions consistent with accepted medical practice until my designated healthcare representative is contacted. If no representative is designated or reachable, Lakewood's medical team will make decisions in their professional judgment.

6. PHOTOGRAPHY AND RECORDING

I consent to photography, video, or audio recording before, during, and after procedures for medical records, education, research, or quality improvement purposes. I understand these records may be used in medical publications or presentations with reasonable efforts to de-identify my information, but that complete de-identification cannot be guaranteed.

7. WAIVER OF LIABILITY

I release Lakewood Medical Center, its physicians, nurses, staff, and affiliates from any and all liability for outcomes resulting from treatment provided in good faith, including outcomes resulting from provider error, equipment malfunction, or miscommunication between providers. I understand that this waiver does not apply to claims of gross negligence or willful misconduct, but that the determination of what constitutes "gross negligence" versus "ordinary negligence" shall be made through binding arbitration rather than a jury trial.

8. DISPUTE RESOLUTION

Any dispute, claim, or controversy arising from treatment at Lakewood Medical Center, including claims of medical malpractice, shall first be submitted to a mandatory mediation process. If mediation fails, disputes shall be resolved by binding arbitration conducted by a panel selected by the American Health Lawyers Association. I waive the right to a jury trial. Any claim must be filed within one (1) year of the date of treatment, regardless of when the injury was discovered. I agree that any arbitration award shall not exceed the cost of the medical services provided.

9. RESEARCH AND DATA USE

I consent to the use of my de-identified health data, biological specimens, and treatment outcomes for medical research, quality improvement, and data analytics purposes. Data may be shared with research partners, pharmaceutical companies, and technology companies developing health-related products. I understand I will not receive compensation for any commercial applications derived from my data.

Lakewood Medical Center
[Witness Signature]

Patient Signature: _______________
Date: _______________
"""
},

'hoa': {
    'filename': 'Crestview HOA Rules & Covenants (Sample)',
    'text': """CRESTVIEW ESTATES HOMEOWNERS ASSOCIATION
DECLARATION OF COVENANTS, CONDITIONS, AND RESTRICTIONS

Recorded: Crestview Estates, 1200 Summit Drive
Effective for all property owners within Crestview Estates subdivision

1. ASSESSMENT AND DUES

Monthly HOA assessment: $385 per lot. The Board of Directors may increase assessments by up to 10% annually without homeowner approval. Special assessments for capital improvements, repairs, or legal expenses may be levied at any time by majority Board vote. Assessments are due on the 1st of each month. A late fee of $50 applies after the 10th, plus 1.5% monthly interest on the outstanding balance. Assessments unpaid for 90 days constitute a lien on the property, and the Association may initiate foreclosure proceedings to collect, with all legal fees added to the homeowner's balance.

2. ARCHITECTURAL CONTROL

No exterior modification, including paint color, landscaping, fencing, signage, satellite dishes, solar panels, decorations, or structural changes, may be made without prior written approval from the Architectural Review Committee ("ARC"). Applications must be submitted at least 60 days before the planned modification. The ARC has sole discretion to approve, deny, or impose conditions on any application. If the ARC does not respond within 60 days, the application is deemed denied. Approved modifications must be completed within 90 days or the approval expires. Unauthorized modifications must be removed at the homeowner's expense within 14 days of written notice, or the Association may remove them and charge the cost to the homeowner.

3. MAINTENANCE AND APPEARANCE

Homeowners must maintain their property in a condition consistent with community standards as determined by the Board. Lawns must be mowed to a maximum height of 4 inches. Dead plants must be replaced within 14 days. Vehicles must be parked in garages or driveways; street parking is prohibited between 10 PM and 6 AM. No commercial vehicles, boats, RVs, trailers, or inoperable vehicles may be visible from any street or neighboring property. Trash containers must be stored out of sight except on collection day. Holiday decorations may be displayed no earlier than 30 days before and must be removed within 14 days after the holiday.

4. FINES AND ENFORCEMENT

Violations of any covenant, rule, or standard shall be subject to fines of $100 for the first offense, $250 for the second offense within 12 months, and $500 per day for each subsequent day the violation continues. The Board may impose fines without a hearing if the violation is observable from common areas or public spaces. Homeowners may request a hearing before the Board within 10 days of receiving a fine notice; failure to request a hearing constitutes acceptance of the fine. The Board serves as both the prosecuting and adjudicating body for violation hearings.

5. COMMON AREAS AND AMENITIES

The Association maintains common areas including the pool, clubhouse, playground, and walking trails. The Board may restrict access to amenities for homeowners with outstanding assessments or fines. The Association is not liable for injuries occurring in common areas, including injuries resulting from inadequate maintenance, defective equipment, or lack of supervision. Use of the pool is at the homeowner's own risk. Guest access requires registration; homeowners are responsible for guests' conduct and any damage caused.

6. LEASING AND RENTAL RESTRICTIONS

Homeowners may lease their property with Board approval. Minimum lease term: 12 months. The Board may deny lease approval if the homeowner has any outstanding assessments, fines, or violations, or for any other reason at the Board's sole discretion. No more than 15% of units in the community may be leased at any time; applications beyond this cap are waitlisted. Tenants must agree to abide by all Association rules, and homeowners are responsible for tenant violations and associated fines.

7. GOVERNANCE AND AMENDMENTS

The Board of Directors consists of 5 members elected by homeowners. The Board may adopt, amend, or repeal rules and regulations without homeowner vote. Amendments to these Covenants require approval by 75% of all lot owners (not just those present at a meeting). The Board may engage legal counsel and charge all legal fees to the Association. The Board and its members shall not be personally liable for actions taken in good faith.

8. DISPUTE RESOLUTION

Any dispute between a homeowner and the Association shall first be submitted to the Association's internal grievance process. If unresolved, disputes shall be settled by binding arbitration in the county where the property is located. The prevailing party shall be entitled to recover attorney's fees and costs. Homeowners waive the right to a jury trial. No homeowner may withhold assessments as a means of protesting any action by the Board.

Crestview Estates Homeowners Association
Board of Directors
[President Signature]
"""
},

'coupon': {
    'filename': 'MegaMart Rewards Coupon Book (Sample)',
    'text': """MEGAMART REWARDS
EXCLUSIVE MEMBER COUPON BOOK — SPRING 2026

Congratulations! As a valued MegaMart Rewards member, you've received this exclusive coupon book with over $500 in savings!

COUPON 1 — FRESH PRODUCE
Save 30% on all organic produce! Stock up on fresh fruits and vegetables for the whole family.
Valid: Feb 1–28, 2026. Minimum purchase: $40 in organic produce in a single transaction. Discount applies to regular-priced items only. Cannot be combined with weekly specials, manager's markdowns, or other coupons. Excludes pre-packaged salads, cut fruit, and items from the prepared foods section. Limit one coupon per household per visit. If total organic produce in transaction is below $40 after removing excluded items, coupon is void.

COUPON 2 — HOUSEHOLD ESSENTIALS
Buy 2, Get 1 Free on all cleaning products! Spring cleaning has never been so affordable.
Valid: Feb 1–28, 2026. Free item must be of equal or lesser value to the lowest-priced purchased item. Applies to cleaning products in aisle 7 only. Does not include floor care machines, refill cartridges, cleaning tools, or items over $15. Cannot be combined with manufacturer coupons on the same items. MegaMart reserves the right to limit quantities to 3 per household. Coupon must be presented before checkout is completed; retroactive application is not available.

COUPON 3 — PREMIUM MEAT & SEAFOOD
$10 Off any purchase of $50 or more from our butcher counter! Premium cuts at everyday prices.
Valid: Feb 1–14, 2026 only. Applies to butcher-counter items only; does not include pre-packaged meats, frozen seafood, deli meats, or rotisserie items. $50 minimum is calculated before tax and after all other discounts. If a manufacturer coupon is applied to any item in the qualifying purchase, the total is recalculated and may fall below the $50 threshold. MegaMart Rewards points are not earned on the discounted amount.

COUPON 4 — BABY & FAMILY CARE
20% Off all diapers and baby formula! Because every family deserves savings.
Valid: Feb 1–28, 2026. Maximum discount: $15. Applies to in-stock items only. If the item is out of stock, rain checks are not issued for coupon promotions. Excludes specialty and hypoallergenic formulas. Limit 2 items per category per transaction. Discount is calculated per item, not per transaction; if purchasing items below $5, per-item discount may be less than expected. Cannot be combined with WIC benefits.

COUPON 5 — ELECTRONICS
Free Bluetooth Speaker (value $29.99) with any electronics purchase of $100 or more!
Valid: Feb 1–28, 2026. While supplies last; no rain checks. Free speaker model is MegaMart house brand (MM-BT100) only. Electronics purchase must be in a single transaction and excludes gift cards, phone cards, gaming currency, and accessories under $20. If the qualifying purchase is returned, the retail value of the speaker ($29.99) will be deducted from the refund. If the speaker has been opened, it cannot be returned. MegaMart Rewards members only; membership must be active at time of purchase and redemption.

COUPON 6 — PHARMACY
Save $25 on any new or transferred prescription! Your health matters to us.
Valid: Feb 1–28, 2026. New customers only. Applies to prescriptions transferred from non-MegaMart pharmacies. Does not apply to controlled substances (Schedules II-V), prescriptions covered by government insurance programs (Medicare, Medicaid, TRICARE), or prescriptions where a third-party payer covers more than 80% of the cost. By transferring your prescription, you authorize MegaMart Pharmacy to access your prescription history and share it with MegaMart's health and wellness marketing program. Savings applied as MegaMart store credit, not cash.

COUPON 7 — WINE & SPIRITS
15% Off any 6 bottles of wine! Perfect for entertaining this spring.
Valid: Feb 1–28, 2026. Must purchase exactly 6 or more bottles in a single transaction. Bottles must be 750ml or larger. Excludes wines already on sale, clearance items, and bottles under $8. Discount applied to the 6 lowest-priced qualifying bottles. Cannot be combined with case discounts. Valid only at locations with a liquor license. ID required; MegaMart reserves the right to refuse sale.

GENERAL TERMS AND CONDITIONS

All coupons are issued to the named MegaMart Rewards member and are non-transferable. MegaMart reserves the right to modify, suspend, or cancel any coupon promotion at any time without notice. Coupons have no cash value and may not be exchanged for cash, gift cards, or store credit. MegaMart reserves the right to void any transaction where coupon fraud is suspected, as determined in MegaMart's sole discretion. By using these coupons, you consent to MegaMart collecting and analyzing your purchase history for targeted marketing purposes. All coupons are single-use unless otherwise stated. Photocopies, digital screenshots, and damaged coupons are not accepted. MegaMart's decision on all coupon-related matters is final.

MegaMart Rewards Program
[Marketing Director]
"""
},

'wedding': {
    'filename': 'Evergreen Estate Venue Contract (Sample)',
    'text': """EVERGREEN ESTATE EVENT VENUE
WEDDING & RECEPTION RENTAL AGREEMENT

Event Date: Saturday, September 13, 2026
Client: [Bride/Groom Names]
Venue: Evergreen Estate, 44 Orchard Lane, Napa Valley, CA 94558

1. RENTAL FEE AND DEPOSIT

Total venue rental fee is $18,500 for use of the Main Hall, Garden Terrace, and Bridal Suite from 10:00 AM to 11:00 PM. A non-refundable deposit of $7,400 (40%) is due upon signing. The remaining balance is due 90 days before the event date. If the remaining balance is not received by the due date, Evergreen Estate reserves the right to cancel the reservation and retain the deposit. All payments are by certified check or wire transfer only; credit card payments incur a 4.5% processing surcharge.

2. OVERTIME AND EXTENDED USE

The venue must be vacated by 11:00 PM. Any use beyond 11:00 PM will be billed at $1,200 per 30-minute increment, or any portion thereof, with a minimum charge of one increment. Overtime charges include mandatory additional staffing fees of $350 per half hour. If the event has not concluded by 11:30 PM, Evergreen Estate may, at its sole discretion, direct the DJ or band to stop playing, turn on house lights, and begin breakdown. Client is responsible for ensuring all guests vacate the premises. Any guest remaining on the property after midnight will result in a $500 trespassing remediation fee.

3. VENDOR RESTRICTIONS

All catering must be provided by one of Evergreen Estate's three Preferred Caterers. Outside catering is not permitted under any circumstances, including for dietary, cultural, or religious requirements. Client may submit a written request for an exception no later than 120 days before the event; approval is at Evergreen Estate's sole discretion and subject to an outside caterer surcharge of $3,500. Photography and videography vendors must carry $2,000,000 in liability insurance naming Evergreen Estate as additional insured. Drone photography is prohibited. All vendor vehicles must be removed from the property by 5:00 PM on the event day.

4. CANCELLATION AND FORCE MAJEURE

Cancellation more than 180 days before the event: deposit forfeited. Cancellation 90–180 days: 75% of total fee is due. Cancellation less than 90 days: 100% of total fee is due. In the event of force majeure (defined exclusively as government-mandated closure of the specific venue property), Evergreen Estate will offer a replacement date within 18 months, subject to availability, with no refund option. Weather, illness, travel disruption, vendor cancellation, family emergency, or change of personal plans do not constitute force majeure. Evergreen Estate strongly recommends purchasing wedding insurance, though no specific policy is endorsed.

5. DAMAGE, CLEANUP, AND INDEMNIFICATION

Client is responsible for all damage to the venue, grounds, furnishings, and landscaping caused by Client, guests, or vendors. A refundable damage deposit of $3,000 is required 30 days before the event. Evergreen Estate will assess damages within 14 business days following the event and deduct costs from the deposit. If damages exceed the deposit, Client is liable for the balance. Assessment of damage is at Evergreen Estate's sole discretion. Client agrees to indemnify and hold harmless Evergreen Estate against any claims arising from the event, including but not limited to guest injuries, alcohol-related incidents, and vendor disputes.

By signing below, Client acknowledges reading all terms and agrees to the conditions of this contract.

Evergreen Estate Event Venue
[Venue Director]
"""
},

'sweepstakes': {
    'filename': 'Coca-Cola Around the World Sweepstakes Part 2 — Official Rules (Sample)',
    'text': """COCA-COLA\u00ae AROUND THE WORLD SWEEPSTAKES PART 2
OFFICIAL RULES
NO PURCHASE OR PAYMENT OF ANY KIND IS NECESSARY TO ENTER OR WIN. A PURCHASE OR PAYMENT WILL NOT INCREASE YOUR CHANCES OF WINNING.

1. Eligibility: The Coca\u2011Cola Around the World Sweepstakes Part 2 (the "Sweepstakes") is open only to legal residents of the 50 U.S./D.C. ("Eligibility Area"), who are 18 years of age or older as of the date of entry ("Entrant"). Void outside the Eligibility Area and where prohibited by law. Employees of The Coca\u2011Cola Company (the "Sponsor"), WPP plc, Coca\u2011Cola bottlers, Don Jagoda Associates, Inc. ("Administrator"), and their respective subsidiaries, parents, divisions, franchisees, promotional partners, agencies, affiliates, advertising and promotion agencies (collectively, the "Released Sweepstakes Parties") as well as the immediate family (spouse, parents, siblings and children) and household members of each such employee, are not eligible to participate. This Sweepstakes is subject to all applicable federal, state, and local laws and regulations. Participation constitutes Entrant's full and unconditional agreement to these Official Rules.

2. Sweepstakes Period: The Sweepstakes begins at 9:00 am Eastern Time ("ET") on November 10, 2025 and ends at 11:59 pm ET on December 31, 2025 ("Sweepstakes Period").

3. How to Enter: There are three (3) ways to enter during the Sweepstakes Period:
Via Instagram: The Sponsor will post an Instagram ad/post (an "Instagram Post") in relation to the Sweepstakes. Click on the Instagram Post and complete the registration form on screen in its entirety in order to receive one (1) entry into the random drawing, subject to the limit below ("Instagram Entry"). If you do not have an Instagram account, you can create one for free.
Via Facebook: The Sponsor will post a Facebook ad/post (a "Facebook Post") in relation to the Sweepstakes. Click on the Facebook Post and complete the registration form on screen in its entirety in order to receive one (1) entry into the random drawing, subject to the limit below ("Facebook Entry"). If you do not have a Facebook account, you can create one for free.

Any attempt by any Entrant to obtain more than the stated number of Facebook or Instagram Entries by using multiple/different social media accounts, email addresses, identities, registrations or logins, or any other methods will void that Entrant's Facebook or Instagram Entries and that Entrant may be disqualified from the Sweepstakes. In the event of a dispute as to any Facebook or Instagram Entry, the authorized account holder of the email address associated with their Facebook or Instagram account will be deemed to be the Entrant. The "authorized account holder" is the natural person assigned an email address by an Internet access provider, online service provider or other organization responsible for assigning email addresses for the domain associated with the submitted address. The Potential winner may be required to show proof of being the authorized account holder.
Mail-in Alternate Method of Entry ("AMOE"): To enter without completing an Instagram Entry or a Facebook Entry, you may enter by hand-printing your complete name, street address (no P.O. Boxes), city, state, ZIP code, telephone numbers (including area code), date of birth (mm/dd/yyyy) and a valid email address on a plain 3"x5" index card, and mail it in an envelope with sufficient postage affixed, to: The Coca\u2011Cola Around the World Sweepstakes Part 2, P.O. Box 7656, Melville, NY 11775-7656 to receive one (1) entry into the Sweepstakes ("AMOE Entry"). AMOE Entries must be postmarked by December 31, 2025 and received by January 8, 2026. AMOE Entries that are mechanically reproduced, copied, illegible, incomplete, postage-due or inaccurate and AMOE Entries submitted by any means which subvert the AMOE Entry process are void. AMOE Entries become the property of the Sponsor and will not be acknowledged or returned.

Instagram Entry, Facebook Entry, and AMOE Entry will be collectively referred to as "Entry" or "Entries". There is a limit of one (1) Entry per Entrant, regardless of the method of Entry.

4. Random Drawing and Odds of Winning: One (1) Grand Prize winner will be selected in a random drawing on or about January 9, 2026 from among all eligible Entries received. Drawing will be conducted by the Administrator, an independent judging organization whose decisions are final and binding on all matters related to the drawing. The odds of winning will depend on the total number of eligible Entries received.

5. Prize/Approximate Retail Value ("ARV"):
Grand Prize (1): The Grand Prize consists of the following trips (each a "Trip"):
A 3-day, 2-night Trip for two (2) to Atlanta, Georgia. This portion of the Grand Prize includes round-trip economy air transportation for the winner and one (1) travel companion from major airport nearest winner's home to Atlanta, Georgia, hotel accommodations for two (2) nights for the winner and travel companion [based on one (1) room, double occupancy], a Sponsor-specified World of Coca\u2011Cola tour, and a private tour of Atlanta, GA, (each an "Atlanta Tour"), and a $750 check for winner that can be used towards spending money.
A 5-day, 4-night Trip for two (2) to Mexico City, Mexico. This portion of the Grand Prize includes round-trip economy air transportation for the winner and one (1) travel companion from major airport nearest winner's home to Mexico City, Mexico, hotel accommodations for four (4) nights for the winner and travel companion [based on one (1) room, double occupancy], two (2) tickets for a personalized and private Mexico City taco tour, a Mexico City highlights tour and hidden gems tour (each a "Mexico City Tour") and a $750 check that can be used towards spending money for the Grand Prize winner.
A 7-day, 6-night Trip for two (2) to Rio De Janeiro, Brazil. This portion of the Grand Prize includes round-trip economy air transportation for the Grand Prize winner and travel companion from major airport nearest winner's home to Rio De Janeiro, Brazil, hotel accommodations for six (6) nights for the winner and travel companion [based on one (1) room, double occupancy], the Grand Prize winner and travel companion will also receive, a Rio Carnival experience with tour guide, a Christ Redeemer entrance pass, and a Sugarloaf cable car entrance pass (each a "Rio De Janeiro Tour"). The Grand Prize winner will also receive a $750 check that can be used towards spending money.
A 7-day, 6-night Trip for two (2) to Tokyo, Japan. This portion of the Grand Prize includes round-trip economy air transportation for the Grand Prize winner and travel companion from major airport nearest winner's home to Tokyo, Japan, hotel accommodations for six (6) nights for the winner and travel companion [based on one (1) room, double occupancy], the winner and travel companion will also receive, a Coca\u2011Cola Japan bottlers factory tour, a Private half-day tour, and Mt. Fuji full-day tour (each a "Tokyo Tour"). The winner will also receive a $750 check that can be used towards spending money.
A 6-day, 5-night Trip for two (2) to London, England. This portion of the Grand Prize includes round-trip economy air transportation for the Grand Prize winner and travel companion from major airport nearest winner's home to London, England, hotel accommodations for five (5) nights for the winner and travel companion [based on one (1) room, double occupancy], the winner and travel companion will also receive London-in-a-Day walking tour, and two (2) tickets to London Eye fast track (each a "London Tour"). The winner will receive a $750 check that can be used towards spending money.

The Grand Prize winner will also receive a check in the amount of $15,000 that can be used to help defray the tax liability associated with the complete Grand Prize.

ARV of the complete Grand Prize: $57,312.
Each Atlanta Tour, Mexico City Tour, Rio De Janeiro Tour, Tokyo Tour, and London Tour will collectively be referred to as "Tour" or "Tours". The Grand Prize will be referred to as "Prize".

Trips do not need to be taken consecutively. Airline tickets are for travel from major airport in the United States nearest winner's home to each destination city. Airline carrier's regulations and conditions apply. Prize may not be combined with any other offer and travel may not qualify for frequent flyer miles. The Prize winner may select a different travel companion for each Trip or may have the same travel companion for all Trips. The Prize winner and travel companion for the applicable Trip must travel together on the same itinerary. Each travel companion (or winner on behalf of travel companion who is a minor and their child/charge) of the winner, will be required to execute a Release of Liability prior to departure. All travelers must have applicable valid travel documents prior to departure [i.e., REAL ID-compliant driver's license or REAL ID-compliant non-driver identification, passport (or passport card), VISA, etc.]. Passports must valid for at least six (6) months after travel is completed for international travel. All Trips must be completed within two (2) years of winner verification (or any Trips not taken will be forfeited); dates of departure and return for each Trip are subject to change. The Atlanta, Georgia Trip must be booked no less than 30 days prior to departure. The Mexico City, Mexico Trip and London, England Trip must be booked no less than 60 days prior to departure. The Rio De Janeiro Trip must be booked no less than 6 months prior to departure. Tokyo, Japan Trip must be booked no less than 90 days prior to departure. Certain restrictions and blackout dates may apply for each Trip. Seat selection and timing of Trips are subject to availability and confirmation of reservations. In the event the winner lives within a 150-mile radius of Atlanta, GA, round-trip ground transportation will be provided in lieu of air transportation and no additional compensation will be provided for the air transportation portion of that Trip. If the Prize winner elects to travel or participate in any Trip with no travel companion, no additional compensation will be awarded for the travel companion portion of that Trip. No refunds or credit for changes are allowed. All other expenses and costs, not expressly listed above, including, but not limited to, airline baggage fees, taxes, tips, entertainment, transfers, and transportation to airports to and from winner's home residence are the winner's sole responsibility. Prize winner will be required to provide a valid major credit card or some other acceptable form of payment, as determined in the hotel's sole discretion upon hotel check-in and all in-room charges, telephone calls, meals, beverages, hotel upgrades, amenities, personal incidentals and any other expenses charged to the winner's hotel room will be charged to that major valid credit card. In the event that the winner or their travel companion for any Trip engage in behavior that (as determined by Sponsor in Sponsor's sole discretion) is inappropriate or threatening, illegal or that is intended to annoy, abuse, threaten or harass any other person, Sponsor reserves the right to terminate any Trip early and/or eject them from any portion of a Trip or the applicable Tour, in whole or in part, and send the winner and their travel companion home with no further compensation to the Prize winner.

Lost, mutilated, or stolen Tour tickets will not be replaced. By accepting the Prize, Prize winner agrees to abide by any terms, conditions and restrictions provided by the applicable Tour and the Tour venue. Sponsor is not responsible if winner does not use Tour tickets on day of a scheduled Tour. Sponsor is not responsible if the Tour is delayed, postponed or cancelled for any reason and the winner will not be reimbursed. Released Sweepstakes Parties will not be responsible for Acts of God, acts of terrorism, civil disturbances, work stoppage or any other natural disaster outside of Released Sweepstakes Parties' control that may cause the cancellation or postponement of any Tour. Tour tickets are subject to issuer's standard terms and conditions, including but not limited to rain-check policies and procedures. Restrictions, conditions and limitations may apply. Winner and their travel companion(s) must follow any applicable COVID or other protocols in place at time of travel and each Tour. All Prize details are in Sponsor's sole discretion. Tours may need to be taken during certain times of the year or season and certain Tours may not be available at time of Trip or some Tours may be cancelled or discontinued. In case of any Tour cancellation, that portion of the Trip will go unawarded and no additional compensation will be provided.

If the Prize (or portion of the Prize) becomes unavailable, Sponsor will substitute the Prize or portion of equal or greater retail value (except as stated specifically above). No transfer, cash or other substitution of the Prize is permitted except Sponsor may substitute Prize in whole or in part for one of comparable or greater retail value for any reason. Resale of the complete Prize or any Trip is prohibited.

6. Winner Notification: The potential Prize winner will be contacted via email and will be required to sign and return a Declaration of Eligibility and Liability Release and except where prohibited, publicity release ("Declaration") within three (3) days of notification in order to be confirmed as the winner. If the potential winner fails to return the completed Declaration within three (3) days, Declaration is returned as undeliverable, Entrant shall be deemed to be ineligible, the Prize will be forfeited and an alternate potential winner will be selected for the Prize. Upon Prize forfeiture, no compensation will be given. Administrator will contact the winner within 3-4 weeks after verification to begin travel arrangements. Return of the Prize or notification as undeliverable will result in disqualification and Prize will be forfeited and an alternate will be selected. If an Entrant is disqualified for one of the reasons mentioned above and an alternate is selected, the alternate must complete and return the required documents in the timeframe specified. Up to three (3) alternates may be selected, time permitting. The Prize winner is solely responsible for all taxes in connection with the Prize, including without limitation federal, state and local taxes, and the reporting consequences thereof. The Prize winner will be issued a 1099 tax form for the actual value of the Prize the year the Prize (or portion of the Prize) is awarded.

7. Publicity: Except where prohibited, participation in the Sweepstakes constitutes winner's consent to Sponsor and its agents' use of winner's name, likeness, photograph, voice, opinions and/or hometown and state for promotion, advertising, marketing, and promotional purposes in any media, worldwide, without further notice, payment or consideration.

8. General Rules: By participating in the Sweepstakes, Entrant fully and unconditionally agrees to and accepts these Official Rules and the decisions of the Sponsor and Administrator, whose decisions are final and binding in all matters related to the Sweepstakes. Any normal Internet/phone access and data/usage charges imposed by Entrants' online/cellular service will apply and are Entrants' sole responsibility. Sponsor is not responsible for any compatibility issues with Entrant's device/browser used for Entry. Entries become the property of Sponsor upon receipt and will not be acknowledged or returned. Entries specifying an invalid, non-working, or inactive email address may be disqualified. No information regarding Entries, other than as otherwise set forth in these Official Rules, will be disclosed. Sponsor is not responsible for lost, interrupted or unavailable network server or other connection; miscommunications; failed phone or computer or telephone transmissions; technical failure; jumbled, scrambled or misdirected transmissions; late, lost, incomplete, delayed, or misdirected Entries; or other errors of any kind whether human, mechanical, or electronic. In the event the Sweepstakes is compromised or impaired in any way for any reason, including but not limited to, fraud, virus, bug, unauthorized human intervention, outbreak of widespread illness, pandemic, civil unrest or any other problem or other causes beyond the control of Sponsor that corrupts or impairs the administration, security, fairness, or proper conduct of the Sweepstakes, Sponsor reserves the right in its sole discretion to suspend or terminate the Sweepstakes and select the winner from among all eligible Entries received prior to cancellation. Sponsor is not responsible for lost, late, misdirected, corrupted, or incomplete Entries. Proof of submission is not proof of receipt by Sponsor. By participation in the Sweepstakes, Entrants, winner, and winner's travel companion(s) release and hold harmless the Released Sweepstakes Parties, Facebook, and Instagram from and against any and all liability, claims, or actions of any kind whatsoever for injuries, damages, or losses to persons or property which may be sustained in connection with submitting an Entry or otherwise participating in any aspect of the Sweepstakes, the receipt, ownership or use of the Prize or any Trip awarded, or while preparing for, participating in any Prize-related activity or any typographical or other errors in these Official Rules or the announcement or offering of the Prize.

9. Fraudulent/Disruptive Activities: Any attempt to tamper with, interfere with, or manipulate the Entry process, the operation of the Sweepstakes or the Prize determination, including, but not limited to, the use of AI, bots, automated systems, or fraudulent identities, is strictly prohibited. Entries generated by AI, script, macro, or other automated means, or by any means that subvert the entry process, will be disqualified and may result in the Entrant being disqualified and banned from future promotions conducted by Sponsor and its affiliates. The Sponsor reserves the right to disqualify any individual suspected of engaging in this prohibited conduct, including but not limited to, creating multiple social media accounts, submitting false information, or engaging in any activity that violates these Official Rules. Any such actions may be a violation of criminal and civil law, and, should such an attempt be made, Sponsor reserves the right to not only disqualify such individual but seek damages from such individual to the fullest extent permitted by law. Furthermore, any Entrant that acts in an unsportsmanlike or disruptive manner, or with intent to annoy, abuse, threaten or harass any other person will be disqualified. Sponsor's failure to enforce any term of these Official Rules shall not constitute a waiver of this provision.

10. Disputes: Entrant agrees that: (a) they release and will defend, indemnify and hold harmless the Released Sweepstakes Parties from and all any and all Claims ("Claims"); (b) Claims arising out of or connected with this Sweepstakes, or the Prize awarded shall be resolved individually, without resort to any form of class action, and solely and exclusively in a federal or state court located in Atlanta, GA; (c) Entrant submits to sole and exclusive personal jurisdiction to said courts in the State of Georgia for any such dispute and irrevocably waives any and all rights to object to such jurisdiction; (d) any and all Claims, judgments, and awards shall be limited to actual damages of no more than $100, including costs associated with entering this Sweepstakes, but in no event attorneys' fees; and (e) under no circumstances will Entrant be permitted to obtain awards for and Entrant hereby waives all rights to claim punitive, incidental and consequential damages and any other damages, other than for actual out-of-pocket expenses, and any and all rights to have damages multiplied or otherwise increased. SOME JURISDICTIONS DO NOT ALLOW THE LIMITATION OR EXCLUSION OF LIABILITY FOR INCIDENTAL OR CONSEQUENTIAL DAMAGES, SO THE ABOVE MAY NOT APPLY TO YOU. All issues and questions concerning the construction, validity, interpretation and enforceability of these Official Rules, or the rights and obligations of Entrants or the Released Sweepstakes Parties in connection with this Sweepstakes shall be governed by, and construed in accordance with, the laws of the State of Georgia, without giving effect to any choice of law or conflict of law rules of provisions (whether of the State of Georgia or any other jurisdiction), which would cause the application of the laws of any jurisdiction other than the State of Georgia.

11. Privacy Policy: Information collected by Sponsor in connection with this Sweepstakes may be used by Sponsor and shared with third parties involved in administration of the Sweepstakes in accordance with the Sponsor's online Privacy Policy. The Entrant agrees to the collection, processing and storage of their personal data by Sponsor for the purposes of the Sweepstakes.

12. Winner List: For the name of the winner, available after February 9, 2026, send an email with COKE AROUND THE WORLD SWEEPSTAKES PART 2 WINNERS & 01-2991-62 as the subject line.

13. Sponsor/Administrator: Sponsor of the Sweepstakes is The Coca\u2011Cola Company, One Coca\u2011Cola Plaza, Atlanta, GA 30313. Administrator of the Sweepstakes is Don Jagoda Associates, Inc., 100 Marcus Drive, Melville, NY 11747.

The Sweepstakes is in no way sponsored, endorsed or administered by, or associated with Facebook or Instagram. You understand that you are providing your information to The Coca\u2011Cola Company and not to Facebook or Instagram. The information you provide will only be used in connection with this Sweepstakes or in connection with promotional or other activities of The Coca\u2011Cola Company.
"""
},

'pet': {
    'filename': 'Forever Friends Animal Shelter Adoption Contract (Sample)',
    'text': """FOREVER FRIENDS ANIMAL SHELTER
ADOPTION CONTRACT AND AGREEMENT

Shelter Location: 1220 County Road 9, Shelter Building C, Minneapolis, MN 55412
Animal ID: FF-2026-03892
Animal Name: [Pet Name] — [Breed/Description], approx. [Age]

This contract is legally binding. Please read all terms before signing.

1. ADOPTION FEE AND INCLUDED SERVICES

Adoption fee of $350 includes initial veterinary exam, age-appropriate vaccinations, spay/neuter surgery (or spay/neuter deposit if underage), microchip with registration, and a 14-day health guarantee covering pre-existing conditions documented at adoption. The health guarantee covers veterinary costs up to the adoption fee amount only and requires Adopter to use a Forever Friends-approved veterinarian for the initial visit. Use of a non-approved veterinarian within the first 30 days voids the health guarantee.

2. HOME ENVIRONMENT REQUIREMENTS

Adopter certifies that all members of the household have been informed of and consent to the adoption. If Adopter rents, Adopter must provide written landlord approval before the animal may be released. Adopter agrees to keep the animal indoors (cats) or in a securely fenced yard (dogs) at all times. Dogs may not be tethered outdoors as a primary containment method. Adopter agrees to provide adequate food, water, shelter, veterinary care, and socialization appropriate to the species. Failure to meet these requirements constitutes a breach of contract and grounds for animal recovery.

3. HOME VISITS AND INSPECTIONS

Adopter grants Forever Friends the right to conduct a pre-adoption home inspection and follow-up post-adoption home visits at 2 weeks, 3 months, and 12 months. Additional visits may be conducted at any time if Forever Friends receives a concern about the animal's welfare, from any source. Inspections will be scheduled with at least 24 hours' notice when possible, but Forever Friends reserves the right to conduct unannounced welfare checks if it has reasonable cause for concern, as determined solely by Forever Friends. Refusal to allow a home visit is grounds for animal recovery.

4. TRANSFER, REHOMING, AND RETURN POLICY

Adopter may NOT sell, give away, or transfer the animal to any third party under any circumstances. If Adopter can no longer care for the animal at any point during the animal's lifetime, Adopter MUST return the animal to Forever Friends. No refund of adoption fees will be issued upon return. If the animal is found in the possession of anyone other than the Adopter without prior written approval, Forever Friends may recover the animal immediately and pursue legal action for breach of contract. Adopter is responsible for all costs associated with recovery, including attorney fees.

5. BREEDING PROHIBITION AND MEDICAL DECISIONS

The adopted animal may not be bred under any circumstances. If the animal has not been spayed/neutered at the time of adoption, Adopter agrees to complete the surgery within 30 days or by 6 months of age, whichever comes later, using a Forever Friends-approved veterinarian. Failure to provide proof of spay/neuter by the deadline results in forfeiture of the $150 spay/neuter deposit and is grounds for animal recovery. Adopter may not have the animal declawed, devocalized, or subjected to any cosmetic surgical procedure. Euthanasia decisions require prior consultation with Forever Friends unless a licensed veterinarian certifies the animal is in acute, untreatable suffering.

6. MICROCHIP AND LIFETIME TRACKING

The microchip registered to the adopted animal shall remain registered to Forever Friends as the secondary contact in perpetuity. Adopter agrees to keep registration information current, including address and phone number, and to notify Forever Friends within 7 days of any change of address. Failure to maintain current registration is a breach of this contract. Forever Friends retains the right to contact the Adopter at any time to inquire about the animal's welfare. This obligation survives for the lifetime of the animal.

By signing below, Adopter acknowledges reading all terms and agrees to the conditions of this contract.

Forever Friends Animal Shelter
[Adoption Coordinator]
"""
},

'timeshare': {
    'filename': 'Hilton Grand Vacations — Details of Participation (Real)',
    'text': """HILTON GRAND VACATIONS
DETAILS OF PARTICIPATION

ELIGIBILITY

No one is excluded from visiting our properties or purchasing a timeshare. Although anyone can visit our properties or purchase our timeshare products, our special preview vacation packages are only available to persons who meet certain requirements for combined gross annual income, underwriting and credit worthiness, reside in a state where our projects are registered for sale and agree to attend a timeshare sales presentation. Offer valid one per household only.

You are not eligible to participate in this promotion if you:

have an open, incomplete vacation package with Hilton Grand Vacations or one of its affiliates ("HGV") requiring attendance at a sales presentation,
have attended an HGV sales presentation within the last year,
are an employee of HGV, Hilton Worldwide or their affiliated companies, or their immediate family members,
have a credit score as established by the developer or if FICO information is not readily available, otherwise meet the seller's financial risk underwriting requirements (If married or cohabitating, at least one must meet the credit requirements),
have filed for bankruptcy within the past 7 years, or
are a group, consisting of more than one household traveling together.

SALES PRESENTATION EXPECTATIONS

This special promotion requires attendance at an approximately two-hour timeshare sales presentation (one-hour sales presentation for current HGV owners) on the benefits of vacation ownership. To participate in this promotion you must present a current government-issued personal identification, such as a driver's license or passport and have a personal major credit card at the time of sales presentation. If married or living together, both parties must attend the sales presentation together.

If eligibility criteria are not met or the sales presentation is not completed, the credit card used to purchase the vacation package will be charged the full retail value of this promotional offer and you will not be eligible to receive any gifts or discounts in connection with this offer. If you do not meet the criteria, but you have received gifts, you will be charged the verifiable retail value for such gifts, plus all applicable taxes, and less any payments by you.

ACCOMMODATION DETAILS

Accommodations as specified in the vacation package offer may include a standard double hotel room at a Hilton portfolio hotel or a studio or suite at a Hilton Grand Vacations resort (valued at $175-$900/night) except in locations where accommodations at another brand hotel or resort may be offered. Certain restrictions may apply, accommodation upgrades, and stays over weekends, during high season and holidays are limited and may include additional fees. Savings and available accommodations may vary. We can accommodate up to four (4) people with your vacation package, with the exception of Las Vegas and New York, which accommodate up to two (2) people.

Vacation package includes accommodations and named presentation incentive rewards or gifts only. Transportation, parking fees, personal expenses, and taxes and other fees are the sole responsibility of the purchaser. Pets are not permitted. Parking and access for recreational vehicles may be restricted. Accommodations are subject to availability.

RESERVATION CHANGE AND CANCELLATION POLICY

Vacation packages are non-refundable and non-transferable. Vacation package expires 12 months from date of purchase unless otherwise stated in the offer received.

A $19.95 charge applies to each reservation change made 7 days or more prior to arrival. Should plans change within 7 days of scheduled arrival, requiring a reservation cancellation, change, or no-show, the equivalent of one (1) night at the currently published retail price ($175-$900) for the applicable resort or hotel at that time will be charged to the credit card used to purchase the vacation package.

PURPOSE OF PROMOTION

THIS MATERIAL IS FOR THE PURPOSE OF SOLICITING TIMESHARE OWNERSHIP INTERESTS. THE COMPLETE OFFERING TERMS ARE IN AN OFFERING PLAN AVAILABLE FROM THE DEVELOPER. Prices range from $9,900 to $853,990 USD, subject to availability. Pricing is dependent on product purchased, without promotions and discounts and subject to change. Eligibility and financing requirements apply. Additional restrictions may apply.

This is neither an offer or solicitation to sell to residents in jurisdictions in which registration requirements have not been fulfilled, and your eligibility and the timeshare plan available for purchase will depend upon the state of the purchaser.

The Developer reserves the right to change this offer prior to purchase without notice. Offer not valid with any other promotional offer. Information gathered through this promotion will be used to solicit timeshare sales.

SALES AND DEVELOPER INFORMATION

Hilton Resorts Corporation is the sales and marketing agent (dba Hilton Grand Vacations) located at 6355 Metrowest Blvd. Orlando, FL 32835.

Hilton Resorts Corporation and its affiliates, subsidiaries, parent and its parent's affiliates and subsidiaries and partners are also the developer/seller of timeshare interests in the US and internationally. Hilton Grand Vacations Club LLC, HVC International Club Inc. and Extraordinary Escapes Corporation are the exchange agents.

Certain travel services are provided by Great Vacation Destinations Inc., a Florida corporation located at 5323 Millenia Lakes Blvd, Suite 400 Orlando, Florida ("GVD"). Florida Seller of Travel Ref. No. ST37755; Washington GVD SOT ID # 602283711 and HRC SOT ID # 602154160; California GVD CST# 2068362-50 and HRC CST#2114968-50. Registration as a seller of travel does not constitute approval by the State of California.

DISPUTE RESOLUTION AND LIABILITY

Any claims arising from this offer shall be limited to the amount paid for the vacation package. Any disputes must be resolved individually and any right to a class action and/or a jury trial is waived.

Hilton Grand Vacations is a registered trademark of Hilton Worldwide Holdings Inc. or its subsidiaries and licensed to Hilton Grand Vacations Inc.

Updated 9/26/25
"""
},

'hackathon': {
    'filename': 'Built with Opus 4.6: Claude Code Hackathon — Event Waiver (Real)',
    'text': """BUILT WITH OPUS 4.6: A CLAUDE CODE HACKATHON
EVENT WAIVER AND LIABILITY RELEASE

Event Overview

All individuals interested in attending the Built with Opus 4.6: a Claude Code Hackathon (the "Event") must complete and submit an application through the official application process. Applications must be submitted by Sunday, February 8th at 8 p.m. (PST) to be considered for attendance. All fields in the application form must be completed accurately and truthfully. Incomplete or false information may result in automatic rejection. Submission of an application does not guarantee attendance at the Event. The Organizers reserve the right to change or cancel the Event at any time.

The Event is limited to 500 individuals. Participants will be provided $500 in API credits for development over a seven (7) day period. Participants will submit their project to Cerebral Valley's portal.

Finalists will be chosen by a panel of judges. The judges' selections are final and binding.

Five (5) finalists may receive prizes which may include:
1st Prize: $50,000 in API credits
2nd Prize: $30,000 in API credits
3rd Prize: $10,000 in API credits
Special Prizes:
"Most Creative Opus 4.6 Exploration": $5,000 in API credits
"The 'Keep Thinking' Prize": $5,000 in API credits

Age Restrictions and Eligibility Requirements

Participants must be at least 18 years old to join the Event. The Organizers reserve the right to rescind an invitation or decline registration to the Event for any reason; the Organizers' decision regarding attendance of the Event is final.

Participants must also not be residents of Italy, Quebec, Crimea, Cuba, Iran, Syria, North Korea, Sudan, Belarus, Russia, or any other country restricted under applicable U.S. or international law, must not be subject to U.S. export controls or sanctions, and must have access to the internet as of December 17, 2025. Employees, contractors, interns, government-affiliated individuals, or other parties whose participation would create a real or apparent conflict of interest are not eligible.

Acknowledgment of Risk

The Participant understands and acknowledges that participation in a virtual event involves inherent risks, including but not limited to: interruptions or failures of internet connectivity, hardware, or software; security, privacy, or data breaches related to third-party platforms; loss of data, code, submissions, or work product; exposure to offensive, inappropriate, or unlawful conduct or content from other participants. The Participant voluntarily assumes all risks associated with participation in the Event.

Release of Liability

To the fullest extent permitted by law, the Participant, on behalf of themselves and their heirs, executors, families, estates, trustees, administrators, personal representatives, successors, and assigns, hereby releases, waives, and discharges the Organizers, their affiliates, and their respective officers, directors, employees, volunteers, contractors, sponsors, partners, agents, representatives, licensees, successors, and assigns (collectively, the "Released Parties") for and from, and against any and all present and future claims, liabilities, damages, losses, demands, actions, or causes of action arising out of or related to (a) the Participant's participation in the Event, including but not limited to the use of online platforms, communications, Submissions, or interactions with other participants; or (b) the use of video, audio, or screenshots taken during the Event (including your likeness incorporated therein), including claims of defamation, invasion of privacy, or rights of publicity or copyright infringement. This waiver and release does not extend to claims for gross negligence, willful misconduct, or any other liabilities that California law does not permit to be released by agreement.

Participant acknowledges and agrees that they have read and understood Section 1542 of the California Civil Code or any equivalent law of any other jurisdiction, which says, in substance: "A GENERAL RELEASE DOES NOT EXTEND TO CLAIMS THAT THE CREDITOR OR RELEASING PARTY DOES NOT KNOW OR SUSPECT TO EXIST IN HIS OR HER FAVOR AT THE TIME OF EXECUTING THE RELEASE AND THAT, IF KNOWN BY HIM OR HER, WOULD HAVE MATERIALLY AFFECTED HIS OR HER SETTLEMENT WITH THE DEBTOR OR RELEASE PARTY." Participant hereby expressly waives and relinquishes all rights and benefits under such section and any law of any jurisdiction of similar effect with respect to your release of any claims hereunder you may have against the Organizers.

To the maximum extent permitted by law, Participant hereby covenants not to sue the Released Parties for any claims hereunder.

Indemnification

The Participant agrees to indemnify, defend, and hold harmless the Released Parties from and against any and all losses, liabilities, damages, costs, and expenses (including reasonable attorney's fees) resulting from any claim, action, or proceeding brought by any third party based on or arising out of the Participant's actions, conduct, participation, or other behavior of participants, in the Event.

Governing Law and Venue

These terms shall be governed by and construed in accordance with the laws of the state of California, without regard to its conflict of law provisions. Any action or proceeding arising out of or related to this Agreement shall be brought exclusively in the state or federal courts located in San Francisco, California.

Release of Information

The Participant agrees to allow personal information submitted to this event (including but not limited to name, email address), with event sponsors or other parties for marketing purposes related to products and services that may be of interest to the Participant. The Participant understands that they may receive communications from event sponsors and affiliates after the Event has concluded. Due to the nature of the Event, none of the Organizers can agree to obligations of confidentiality, non-use or non-disclosure with regard to any of your content or any other ideas, information, feedback, pitches, developments or materials that you may provide, share, or use during or in connection with the Event (your "Materials"). You agree that by providing, sharing, or using your Materials in connection with the Event, you agree that your Materials will not be considered confidential or proprietary, and you grant the Organizers a royalty free, transferable, sub-licensable, worldwide and perpetual and irrevocable license to access, use, host, cache, store, reproduce, transmit, display, publish, distribute, and modify your Materials.

Image, Video and Audio Recording Consent

The Participant acknowledges that the Event may be recorded, livestreamed, or otherwise captured via video, audio, screenshots, or other digital means. By participating, the Participant consents to and gives the Organizers the right to store, reproduce, create derivative works of, publicly display, publicly perform, distribute, record and otherwise use their name, likeness, voice, image, chat messages, screen shares, and submissions in any media, worldwide, in perpetuity, for promotional, marketing, educational, archival, or any other lawful business purposes without compensation. All recordings shall be the sole property of the Organizers. The Participant waives any right to inspect or approve of the use of such video, audio, or screenshots in accordance with these terms and represent and warrant that they are authorized to grant the foregoing rights.

Hackathon Submission

As between the Hackathon Organizer and the entrant, the entrant retains ownership of all intellectual and industrial property rights (including moral rights) in and to the Submission. As a condition of submission, Entrant grants the Organizers, their subsidiaries, agents and partner companies, a perpetual, irrevocable, worldwide, royalty-free, and non-exclusive license to use, reproduce, adapt, modify, publish, distribute, publicly perform, create a derivative work from, publicly display, and otherwise exploit the Submission for any purpose without restriction, including, without limitation, for use in marketing materials (e.g., newsletters, social media, websites, and demonstration at live events).

By submitting a project to the Event (a "Submission"), the Participant represents, warrants, and agrees that their Submission: (a) is their (or their Team's or Organization's) original work product; (b) is solely owned by the Participant, their Team, or Organization, with no other person or entity having any right or interest in it; and (c) does not violate the intellectual property or other rights (including copyright, trademark, patent, contract, or privacy rights) of any other person or entity. Participants may contract with a third party for technical assistance, provided the Submission components remain the Participant's own work and the Participant owns all rights to them. Participants may also include open source software or hardware, provided applicable open source licenses are followed and the Submission enhances or builds upon the underlying open source product.

Fees and Taxes

Winners, and all participating team or organization members, are responsible for any fees associated with receiving or using a Prize, including wiring, currency exchange, and applicable taxes. Winners may need to provide tax forms (e.g., W-9 for U.S. residents, W-8BEN for non-U.S. residents) or other documentation to comply with applicable withholding and reporting requirements. Winners are responsible for foreign exchange and banking compliance in their jurisdiction and for reporting the receipt of any Prize to relevant authorities.

Code of Conduct and Right to Refuse Participation

Participants agree to conduct themselves in a professional, respectful, considerate, mindful, and inclusive manner in all virtual spaces associated with the Event, including chat platforms, video calls, forums, and shared repositories.

The Organizers reserve the right, in their sole discretion, to suspend, remove, or disqualify any participant whose behavior is disruptive, abusive, discriminatory, demeaning, or otherwise inconsistent with the spirit of the Event, without liability, including, without limitation, participants whose actions are meant to intimidate or engage in harassment.

Privacy Policy

Personal information collected during the application process. By submitting an application, participants consent to the collection, processing, and sharing of their personal information, including by and to Anthropic in accordance with its Privacy Policy, for purposes related to the Event.

Modifications

The Organizers reserve the right to modify these terms at any time. Significant changes will be communicated to approved participants. By submitting an application and registration to attend the Event, you acknowledge that you have read, understood, and agree to these terms.

Third-Party Platforms and Services

The Participant acknowledges that the Event may rely on third-party platforms and services. The Organizers are not responsible for the availability, security, functionality, or policies of such platforms and disclaim all liability arising from the Participant's use of them.

Participant Acknowledgment of Third-Party Conduct

The Participant understands that the Organizers are not responsible for the actions, comments, or conduct of other participants, judges, sponsors, or volunteers, and waive any claim arising from interactions with such parties during the Event.

Waiver; Severability

Any failure to enforce any provision of these terms will not constitute a waiver of that provision or of any other provision. If any provision of these terms are held to be invalid, illegal, or unenforceable, the validity, legality, and enforceability of the remaining provisions shall not be affected or impaired in any way.

Binding Effect

These terms shall be binding upon the Participant, and their respective heirs, executors, administrators, and assigns.

IN WITNESS WHEREOF, the Participant has executed this Liability & Information Release and Waiver Agreement as of the date set forth below.

Date: February 6th, 2026
"""
},

}

# Load sample thumbnails from static directory
SAMPLE_THUMBNAILS = {}
_thumb_dir = os.path.join(os.path.dirname(__file__), 'static')
for _key in SAMPLE_DOCUMENTS:
    _path = os.path.join(_thumb_dir, f'thumb_{_key}.jpg')
    if os.path.exists(_path):
        with open(_path, 'rb') as _f:
            SAMPLE_THUMBNAILS[_key] = base64.b64encode(_f.read()).decode()


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

MAX_VISION_PAGES = 10
VISION_DPI = 150
MAX_IMAGE_DIMENSION = 4000   # px – well under Anthropic's 8000px hard limit
MAX_IMAGE_BYTES = 4 * 1024 * 1024  # 4 MB – under the 5 MB API limit


def _has_garbled_text(text):
    """Fast local check: does this text likely contain reversed segments?

    Counts common function words in original vs reversed version of each line.
    If any line scores better reversed, the text needs cleaning.
    """
    import re
    COMMON = {
        'de', 'het', 'van', 'en', 'een', 'voor', 'in', 'te', 'op', 'aan',
        'met', 'bij', 'uit', 'naar', 'dat', 'die', 'niet', 'ook', 'maar',
        'per', 'door', 'tot', 'je', 'zijn', 'kan', 'was',
        'the', 'and', 'for', 'of', 'to', 'is', 'with', 'on', 'at', 'by',
        'not', 'but', 'or', 'this', 'that', 'you', 'your', 'all', 'can',
        'le', 'la', 'les', 'des', 'du', 'un', 'une', 'et', 'est', 'dans',
        'pour', 'par', 'sur', 'avec', 'que', 'qui', 'ce',
        'der', 'die', 'das', 'und', 'ist', 'ein', 'von', 'auf', 'mit',
    }
    def hits(words):
        return sum(1 for w in words
                   if re.sub(r'[^a-zA-Z]', '', w).lower() in COMMON)

    for line in text.split('\n'):
        words = line.split()
        if len(words) < 4:
            continue
        rev_words = line[::-1].split()
        if hits(rev_words) > hits(words) + 1:
            return True
    return False


def clean_extracted_text(text):
    """Use Haiku 4.5 to fix garbled/reversed text from PDF extraction.

    Only calls Haiku when the fast local check detects garbled segments.
    Clean text passes through with zero delay.
    """
    if not text or len(text) < 50:
        return text

    if not _has_garbled_text(text):
        return text  # Clean text — no API call needed

    try:
        result = get_client().messages.create(
            model=FAST_MODEL,
            max_tokens=min(len(text) // 3 + 500, 8192),
            messages=[{'role': 'user', 'content': text}],
            system=(
                'You are a text cleaning tool. The input is extracted from a PDF and may contain '
                'garbled, reversed, or duplicated text segments from complex layouts. '
                'Fix any reversed text (characters in wrong order), remove obvious duplicates, '
                'and clean up extraction artifacts. '
                'Return ONLY the cleaned text — no commentary, no explanations. '
                'If the text looks fine, return it unchanged.'
            ),
        )
        cleaned = result.content[0].text.strip()
        # Sanity check: cleaned text shouldn't be drastically different in length
        if cleaned and 0.3 < len(cleaned) / len(text) < 2.0:
            return cleaned
    except Exception as e:
        print(f'[clean_extracted_text] Haiku cleanup failed, using raw text: {e}')
    return text


def extract_pdf(file_storage):
    import pdfplumber
    from PIL import Image
    pdf_bytes = file_storage.read()
    text_parts = []
    page_images = []
    ocr_used = False
    use_ocr_for_all = None  # None = undecided, True/False after first page test

    def text_quality(t):
        """Score text: fraction of tokens that look like real words."""
        words = t.split()
        if not words:
            return 0
        good = sum(1 for w in words if 2 <= len(w) <= 20 and sum(c.isalpha() for c in w) / max(len(w), 1) > 0.7)
        return good / len(words)

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            pil_img = None
            if i < MAX_VISION_PAGES:
                try:
                    img = page.to_image(resolution=VISION_DPI)
                    pil_img = img.original
                    # Constrain dimensions to stay under API limit
                    if max(pil_img.size) > MAX_IMAGE_DIMENSION:
                        pil_img.thumbnail(
                            (MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION),
                            Image.LANCZOS,
                        )
                    # Encode as JPEG to keep file size bounded
                    buf = BytesIO()
                    pil_img.convert('RGB').save(buf, format='JPEG', quality=80)
                    # If still too large, reduce quality
                    if buf.tell() > MAX_IMAGE_BYTES:
                        buf = BytesIO()
                        pil_img.convert('RGB').save(buf, format='JPEG', quality=50)
                    page_images.append(base64.b64encode(buf.getvalue()).decode())
                except Exception as e:
                    print(f'[extract_pdf] Page image rendering failed: {e}')
                    page_images.append(None)  # Placeholder to keep indices aligned
            # OCR: test on first page, then apply decision to all pages
            if use_ocr_for_all is None and pil_img:
                # First page with an image — test OCR vs embedded text
                try:
                    import pytesseract
                    ocr_text = pytesseract.image_to_string(pil_img)
                    ocr_score = text_quality(ocr_text) if ocr_text else 0
                    orig_score = text_quality(page_text) if page_text else 0
                    use_ocr_for_all = ocr_score > orig_score + 0.05
                    print(f'[extract_pdf] Page 1 quality test: embedded={orig_score:.2f}, OCR={ocr_score:.2f} → {"OCR" if use_ocr_for_all else "embedded"} for all pages')
                    if use_ocr_for_all:
                        page_text = ocr_text
                        ocr_used = True
                except Exception as e:
                    print(f'[extract_pdf] OCR test failed: {e}')
                    use_ocr_for_all = False
            elif use_ocr_for_all:
                # OCR won on first page — OCR this page too
                try:
                    import pytesseract
                    ocr_img = pil_img or page.to_image(resolution=VISION_DPI).original
                    ocr_text = pytesseract.image_to_string(ocr_img)
                    if ocr_text and len(ocr_text.strip()) > len((page_text or '').strip()):
                        page_text = ocr_text
                except Exception as e:
                    print(f'[extract_pdf] OCR failed for page {i+1}: {e}')
            if page_text:
                text_parts.append(page_text)
    if ocr_used:
        print('[extract_pdf] OCR was used for scanned pages')
    # Tag each page so the sidebar can render page dividers
    # and later clauses from page 3+ are matchable
    tagged = []
    for i, part in enumerate(text_parts):
        tagged.append(f'\n\n— Page {i + 1} —\n\n{part}')
    raw_text = ''.join(tagged).strip()
    return clean_extracted_text(raw_text), page_images, ocr_used


def extract_docx(file_storage):
    from docx import Document
    doc = Document(BytesIO(file_storage.read()))
    return '\n\n'.join(p.text for p in doc.paragraphs if p.text.strip())


# ---------------------------------------------------------------------------
# Prompt — optimized for Opus 4.6 extended thinking
# ---------------------------------------------------------------------------

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
        page_images = []

        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = file.filename
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

            ocr_used = False
            if ext == 'pdf':
                text, page_images, ocr_used = extract_pdf(file)
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

        store_document(doc_id, {
            'text': text,
            'filename': filename,
            'role': role,
            'negotiable': negotiable,
            'depth': depth,
            'page_images': page_images,
        })

        # Generate a small thumbnail from the first page image
        thumbnail = None
        if page_images:
            try:
                from PIL import Image
                img_bytes = base64.b64decode(page_images[0])
                img = Image.open(BytesIO(img_bytes))
                img.thumbnail((200, 280))
                buf = BytesIO()
                img.save(buf, format='JPEG', quality=50)
                thumbnail = base64.b64encode(buf.getvalue()).decode()
            except Exception:
                pass

        resp = {
            'doc_id': doc_id,
            'filename': filename,
            'text_length': len(text),
            'preview': text[:300],
            'full_text': text,
            'thumbnail': thumbnail,
        }
        if ocr_used:
            resp['ocr_used'] = True
        return jsonify(resp)

    except Exception as e:
        print(f'[upload/compare] Error: {e}')
        return jsonify({'error': 'An internal error occurred. Please try again.'}), 500


@app.route('/sample', methods=['POST'])
def sample():
    data = request.get_json(silent=True) or {}
    role = data.get('role', 'tenant')
    negotiable = data.get('negotiable', True)
    depth = data.get('depth', 'standard')
    sample_type = data.get('type', 'lease')

    doc = SAMPLE_DOCUMENTS.get(sample_type, SAMPLE_DOCUMENTS['lease'])
    text = doc['text']
    filename = doc['filename']

    doc_id = str(uuid.uuid4())
    store_document(doc_id, {
        'text': text,
        'filename': filename,
        'role': role,
        'negotiable': negotiable,
        'depth': depth,
    })

    return jsonify({
        'doc_id': doc_id,
        'filename': filename,
        'text_length': len(text),
        'preview': text[:300],
        'full_text': text,
        'thumbnail': SAMPLE_THUMBNAILS.get(sample_type),
    })


def build_compare_prompt():
    """System prompt for document comparison mode."""
    return """You are a senior attorney with 20 years of experience comparing contracts, offers, and agreements. You analyze two documents side-by-side from the perspective of someone choosing between them.

## LANGUAGE RULE
ALWAYS respond in ENGLISH regardless of the documents' language. Keep quotes from the documents in their original language with English translations in parentheses.

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


def build_card_scan_prompt():
    """Haiku fast scan — FULL flip cards (front + back). Complete card data in one pass."""
    return """You are a contract analyst. Identify the MOST SIGNIFICANT clauses and produce COMPLETE flip cards — the reassuring front AND the expert back that reveals the truth. Speed matters — output each clause as soon as you identify it.

## CLAUSE LIMIT
Output a MAXIMUM of 12 individual RED/YELLOW cards. Pick the 10-12 clauses with the highest impact on the reader. Combine ALL remaining fair/benign clauses into a single GREEN summary card. Total output: 10-12 cards + 1 green summary = 11-13 cards maximum. If you find more than 12 concerning clauses, pick the worst 12 and note any omitted ones in the green summary.

## LANGUAGE RULE
ALWAYS respond in ENGLISH regardless of the document's language. When quoting text from the document, keep quotes in the original language and add an English translation in parentheses if the quote is not in English. All analysis, card fields, headers, labels, REASSURANCE, READER, TEASER, REVEAL, bottom line, small print, should read, FIGURE, EXAMPLE must be in English.

## OUTPUT FORMAT

Output the Document Profile first, then each clause separated by --- on its own line.

## Document Profile
- **Document Type**: [type of document]
- **Drafted By**: [who drafted it]
- **Your Role**: [the non-drafting party's role]
- **Jurisdiction**: [jurisdiction if identifiable, otherwise "Not specified"]
- **Language**: [language of the document, e.g. "English", "Dutch", "German", "French"]
- **Sections**: [number of major sections]

---

Then for EACH significant clause, output exactly this format:

### [Descriptive Title] ([Context — Section/Product/Coverage])

The section reference MUST anchor the clause to the document structure so the reader knows WHERE they are. Examples:
- Insurance policy: "Travel Cancellation Coverage, Article 4.2" not just "Article 4.2"
- Coupon booklet: "Danone Alpro coupon — Carrefour hypermarkt only" not just "Page 3"
- Lease: "Maintenance & Repairs, §2(b)" not just "§2(b)"
For multi-product documents (coupon books, product bundles): specify WHICH product or offer.

[REASSURANCE]: [One short, warm, positive headline (max 8 words) that frames this clause as beneficial, protective, or fair — how the drafter WANTS you to feel. Must sound genuinely reassuring, not sarcastic. Examples: "Your home is fully protected" / "Clear and simple payment terms" / "Comprehensive coverage for your peace of mind".]

> "[Copy-paste the most revealing sentence or phrase from this clause exactly as written in the document. Do NOT paraphrase.]"

[READER]: [2-4 sentences. You ARE a trusting person who just skims and signs. Think out loud in FIRST PERSON ("I") and SHRUG EVERYTHING OFF. You see basic facts but they don't worry you at all. You NEVER do math, NEVER calculate totals, NEVER question fairness, NEVER express doubt, NEVER recognize legal concepts. FORBIDDEN words/patterns: "waiv" (any form), "surrender," "legal," "rights," "recourse," "argue," "dispute," "sole discretion," "no cap," "no limit," "unlimited," "adds up," "that's $X," "signing away," "give up," "lose my," "forfeit," question marks expressing concern. The reader has ZERO legal literacy — they don't know what a waiver IS. Always end with breezy certainty, never with analysis.]

[HONEY]: [OPTIONAL — only if this clause uses warm, friendly, or reassuring language immediately before or around a punitive/restrictive term. Quote the exact honey phrase from the document, then → the sting it masks. If the clause is purely neutral/technical with no emotional framing, omit this field entirely.]

[TEASER]: [One cryptic sentence that creates tension without revealing the risk. Make the reader WANT to flip. Keep under 12 words. For GREEN clauses: "No surprises here — genuinely."]

[REVEAL]: [One punchy analytical sentence (max 15 words) that hits the reader when the card flips. The sharp truth that contrasts the reassurance on the front. NEVER vague: no "some", "certain", "conditions", "limitations". Be specific. Test: Would someone feel a gut reaction reading this? Examples: "Your deposit funds their legal fees" / "Uncapped daily penalties: $2,250 in fees from one missed month". For GREEN clauses: "This one is genuinely what it promises."]

[GREEN/YELLOW/RED] · Score: [0-100]/100 · Trick: [CATEGORY]
Confidence: [HIGH/MEDIUM/LOW] — [one short reason]

**Bottom line:** [One sentence. Be concrete, not vague.]

**What the small print says:** [One sentence. Plain restatement of what this clause literally says.]

**What you should read:** [One sentence. What this ACTUALLY means. If alarming, be alarming.]

**What does this mean for you:**
[FIGURE]: [The single worst-case number or deadline — just the stat with brief label. Examples: "$4,100 total debt from one missed payment" / "30 days or you lose all rights".]
[EXAMPLE]: [One concrete scenario using the document's own figures. Walk through step by step. 2-3 sentences max.]

---

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

## GREEN CLAUSE GROUPING (MANDATORY)
NEVER create individual cards for GREEN clauses. ALL green/fair/benign clauses go into ONE summary card.
After all RED and YELLOW cards, add exactly ONE final block:

---
### Fair Clauses Summary
[REASSURANCE]: These clauses are what they promise
[READER]: [List each fair clause by section ref and one-line summary]
[TEASER]: These are actually what they look like.
[REVEAL]: These clauses are genuinely what they promise.
[GREEN] · Score: 10/100 · Trick: None
Confidence: HIGH — Standard fair language
**Bottom line:** These clauses are straightforward and fair as written.

This is the ONLY green card allowed. Any clause that is obviously fair must go here, not as a separate card.

## RULES
1. Output each clause immediately — do NOT wait to analyze all clauses before outputting
2. Every clause MUST end with --- on its own line
3. Every clause MUST have ALL fields: title, [REASSURANCE], quote, [READER], [TEASER], [REVEAL], risk+score+trick, confidence, bottom line, small print, should read, [FIGURE], [EXAMPLE]. [HONEY] is OPTIONAL
4. Quotes must be EXACT text from the document — copy-paste, do not paraphrase
5. Keep each field to ONE sentence. Cards must be scannable, not essays
6. The [READER] is GULLIBLE with ZERO legal literacy. The reader signs without reading twice
7. Do NOT include cross-clause interactions — identify each clause independently
8. The [REVEAL] is the TITLE of the card back — make it sharp, specific, gut-punching
9. "What you should read" is the core insight — make it visceral
10. Confidence: HIGH = clear language; MEDIUM = some ambiguity; LOW = multiple interpretations
11. The Document Profile must appear BEFORE the first clause, followed by ---
12. The section reference in parentheses MUST provide document context
13. If the document has NO terms or obligations (e.g. a recipe, novel, news article), output ONLY the Document Profile with **Not Applicable**: [1-sentence explanation]. Do NOT output any clauses.
14. GREEN clauses: Score 0-30, Trick: None. YELLOW/RED clauses MUST have a trick from the 18 categories above — NEVER leave it blank or write "N/A"
15. The risk line format is MANDATORY for every clause: [LEVEL] · Score: [N]/100 · Trick: [CATEGORY] — all three parts, always
16. [FIGURE] and [EXAMPLE] must be mathematically consistent — the headline number in [FIGURE] MUST be derivable from the step-by-step calculation in [EXAMPLE]. Write [EXAMPLE] first in your head, THEN extract the summary number for [FIGURE]. Never round differently between the two"""


def build_clause_id_prompt():
    """Phase 1: Lightweight identification scan. Minimal output for speed."""
    return """You are a contract analyst. Quickly scan this document and identify the most significant clauses that a consumer should worry about.

## LANGUAGE RULE
ALWAYS respond in ENGLISH regardless of the document's language.

## OUTPUT FORMAT

First, output the Document Profile:

## Document Profile
- **Document Type**: [type of document]
- **Drafted By**: [who drafted it]
- **Your Role**: [the non-drafting party's role]
- **Jurisdiction**: [jurisdiction if identifiable, otherwise "Not specified"]
- **Language**: [language of the document]
- **Sections**: [number of major sections]

Then list each significant clause (maximum 12 RED/YELLOW), one per line:

CLAUSE: [Descriptive Title] ([Context — Section/Product/Coverage]) | RISK: [RED/YELLOW] | SCORE: [0-100] | TRICK: [category] | QUOTE: "[copy-paste the single most revealing sentence from this clause]"

After all RED/YELLOW clauses, list ALL fair/benign clauses on one line:

GREEN_CLAUSES: [Section ref]: [one-line description]; [Section ref]: [one-line description]; ...

## TRICK CATEGORIES (pick exactly one per clause):
Silent Waiver, Burden Shift, Time Trap, Escape Hatch, Moving Target, Forced Arena, Phantom Protection, Cascade Clause, Sole Discretion, Liability Cap, Reverse Shield, Auto-Lock, Content Grab, Data Drain, Penalty Disguise, Gag Clause, Scope Creep, Ghost Standard

## RULES
1. Maximum 12 RED/YELLOW clauses — pick the highest-impact ones
2. Output in order of severity (worst first)
3. Quotes must be EXACT text from the document — copy-paste, do not paraphrase
4. If the document has NO terms or obligations (e.g. a recipe, novel, news article), output ONLY the Document Profile followed by: **Not Applicable**: [1-sentence explanation]
5. The section reference in parentheses MUST provide document context (e.g., "Early Termination, §4.2" not just "§4.2")
6. Be fast — this is a speed scan, not deep analysis"""


def build_single_card_system(doc_text):
    """Phase 2: System prompt for per-clause card generation.
    Includes document text so prompt caching is shared across parallel calls."""
    return f"""You are a contract analyst generating a SINGLE complete flip card. Output ONLY the card content — no preamble, no "Here is the card", no --- separators.

## LANGUAGE RULE
ALWAYS respond in ENGLISH regardless of the document's language. When quoting text from the document, keep quotes in the original language and add an English translation in parentheses if the quote is not in English.

## CARD FORMAT

### [Descriptive Title] ([Context — Section/Product/Coverage])

The section reference MUST anchor the clause to the document structure so the reader knows WHERE they are. Examples:
- Insurance policy: "Travel Cancellation Coverage, Article 4.2" not just "Article 4.2"
- Coupon booklet: "Danone Alpro coupon — Carrefour hypermarkt only" not just "Page 3"
- Lease: "Maintenance & Repairs, §2(b)" not just "§2(b)"
For multi-product documents (coupon books, product bundles): specify WHICH product or offer.

[REASSURANCE]: [One short, warm, positive headline (max 8 words) that frames this clause as beneficial, protective, or fair — how the drafter WANTS you to feel. Must sound genuinely reassuring, not sarcastic. Examples: "Your home is fully protected" / "Clear and simple payment terms" / "Comprehensive coverage for your peace of mind".]

> "[Copy-paste the most revealing sentence or phrase from this clause exactly as written in the document. Do NOT paraphrase.]"

[READER]: [2-4 sentences. You ARE a trusting person who just skims and signs. Think out loud in FIRST PERSON ("I") and SHRUG EVERYTHING OFF. You see basic facts but they don't worry you at all. You NEVER do math, NEVER calculate totals, NEVER question fairness, NEVER express doubt, NEVER recognize legal concepts. FORBIDDEN words/patterns: "waiv" (any form), "surrender," "legal," "rights," "recourse," "argue," "dispute," "sole discretion," "no cap," "no limit," "unlimited," "adds up," "that's $X," "signing away," "give up," "lose my," "forfeit," question marks expressing concern. The reader has ZERO legal literacy — they don't know what a waiver IS. Always end with breezy certainty, never with analysis.]

[HONEY]: [OPTIONAL — only if this clause uses warm, friendly, or reassuring language immediately before or around a punitive/restrictive term. Quote the exact honey phrase from the document, then → the sting it masks. If the clause is purely neutral/technical with no emotional framing, omit this field entirely.]

[TEASER]: [One cryptic sentence that creates tension without revealing the risk. Make the reader WANT to flip. Keep under 12 words. For GREEN clauses: "No surprises here — genuinely."]

[REVEAL]: [One punchy analytical sentence (max 15 words) that hits the reader when the card flips. The sharp truth that contrasts the reassurance on the front. NEVER vague: no "some", "certain", "conditions", "limitations". Be specific. Test: Would someone feel a gut reaction reading this? Examples: "Your deposit funds their legal fees" / "Uncapped daily penalties: $2,250 in fees from one missed month". For GREEN clauses: "This one is genuinely what it promises."]

[GREEN/YELLOW/RED] · Score: [0-100]/100 · Trick: [CATEGORY]
Confidence: [HIGH/MEDIUM/LOW] — [one short reason]

**Bottom line:** [One sentence. Be concrete, not vague.]

**What the small print says:** [One sentence. Plain restatement of what this clause literally says.]

**What you should read:** [One sentence. What this ACTUALLY means. If alarming, be alarming.]

**What does this mean for you:**
[FIGURE]: [The single worst-case number or deadline — just the stat with brief label. Examples: "$4,100 total debt from one missed payment" / "30 days or you lose all rights".]
[EXAMPLE]: [One concrete scenario using the document's own figures. Walk through step by step. 2-3 sentences max.]

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
1. Every field is MANDATORY: title, REASSURANCE, quote, READER, TEASER, REVEAL, risk+score+trick, confidence, bottom line, small print, should read, FIGURE, EXAMPLE. HONEY is optional.
2. Quotes must be EXACT text from the document — copy-paste, do not paraphrase
3. Keep each field to ONE sentence. Cards must be scannable, not essays
4. The [READER] is GULLIBLE with ZERO legal literacy. The reader signs without reading twice
5. The [REVEAL] is the TITLE of the card back — make it sharp, specific, gut-punching
6. "What you should read" is the core insight — make it visceral
7. Confidence: HIGH = clear language; MEDIUM = some ambiguity; LOW = multiple interpretations
8. Do NOT output --- separators or any text outside the card format
9. YELLOW/RED clauses MUST have a trick from the 18 categories above — NEVER leave it blank or write "N/A"

## DOCUMENT:

---BEGIN DOCUMENT---

{doc_text}

---END DOCUMENT---"""


def build_green_summary_user(green_clauses_text):
    """User message for the GREEN summary card worker."""
    return f"""Generate the GREEN summary card for these fair clauses:

{green_clauses_text}

Use EXACTLY this format:

### Fair Clauses Summary

[REASSURANCE]: These clauses are what they promise

[READER]: [List each fair clause by section ref and one-line summary]

[TEASER]: These are actually what they look like.

[REVEAL]: These clauses are genuinely what they promise.

[GREEN] · Score: 10/100 · Trick: None
Confidence: HIGH — Standard fair language

**Bottom line:** These clauses are straightforward and fair as written.

**What the small print says:** Standard fair terms with no hidden catches.

**What you should read:** These clauses are genuinely what they promise.

**What does this mean for you:**
[FIGURE]: No hidden costs or risks
[EXAMPLE]: These clauses work as advertised — fair terms for both parties."""


def parse_identification_output(text):
    """Parse Phase 1 identification scan into profile, clauses, and green text."""
    lines = text.strip().split('\n')

    profile_lines = []
    clauses = []
    green_text = ''
    in_profile = False
    profile_ended = False

    for line in lines:
        stripped = line.strip()

        # Start of profile section
        if '## Document Profile' in stripped or (not profile_ended and '**Document Type**' in stripped):
            in_profile = True

        # End of profile section
        if in_profile and (stripped.startswith('CLAUSE:') or stripped.startswith('GREEN_CLAUSES:')
                           or stripped.startswith('**Not Applicable**')):
            in_profile = False
            profile_ended = True

        if in_profile:
            profile_lines.append(line)
            continue

        # Clause lines
        if stripped.startswith('CLAUSE:'):
            clause = _parse_clause_line(stripped)
            if clause:
                clauses.append(clause)

        # Green clauses
        if stripped.startswith('GREEN_CLAUSES:') or stripped.startswith('GREEN:'):
            green_text = stripped.split(':', 1)[1].strip() if ':' in stripped else ''

        # Not Applicable — add to profile
        if '**Not Applicable**' in stripped:
            profile_lines.append(line)

    profile_text = '\n'.join(profile_lines).strip()

    # Ensure profile has header
    if profile_text and '## Document Profile' not in profile_text:
        profile_text = '## Document Profile\n' + profile_text

    return profile_text, clauses, green_text


def _parse_clause_line(line):
    """Parse a single CLAUSE: line into a dict."""
    try:
        content = line[len('CLAUSE:'):].strip()
        parts = [p.strip() for p in content.split('|')]

        result = {'title': '', 'section': '', 'risk': 'RED', 'score': 50, 'trick': '', 'quote': ''}

        # First part: Title (Section)
        title_part = parts[0] if parts else ''
        paren_match = re.search(r'\(([^)]+)\)\s*$', title_part)
        if paren_match:
            result['section'] = paren_match.group(1)
            result['title'] = title_part[:paren_match.start()].strip()
        else:
            result['title'] = title_part

        for part in parts[1:]:
            if part.startswith('RISK:'):
                result['risk'] = part[5:].strip()
            elif part.startswith('SCORE:'):
                try:
                    result['score'] = int(re.search(r'\d+', part).group())
                except (AttributeError, ValueError):
                    pass
            elif part.startswith('TRICK:'):
                result['trick'] = part[6:].strip()
            elif part.startswith('QUOTE:'):
                quote = part[6:].strip().strip('"').strip('\u201c').strip('\u201d')
                result['quote'] = quote

        return result if result['title'] else None
    except Exception as e:
        print(f'[parse_clause] Error: {e} — line: {line[:100]}')
        return None




def build_interactions_prompt(has_images=False):
    """Opus thread 1: Cross-clause compound risks. Findings + deep content."""
    visual_block = ""
    if has_images:
        visual_block = """

## VISUAL FORMATTING ANALYSIS
Page images are included. Look for visual tricks: fine print, buried placement, dense tables, light-gray disclaimers. Include visual tricks as cross-clause interactions with trick categories. Reference page numbers."""

    return f"""You are a senior attorney. Find clause COMBINATIONS that create compound risks invisible when reading linearly. This is your ONLY job — cross-clause interactions.
{visual_block}
## LANGUAGE RULE
ALWAYS respond in ENGLISH regardless of the document's language. When quoting text from the document, keep quotes in the original language and add an English translation in parentheses if the quote is not in English.

## OUTPUT FORMAT — TAGGED SECTIONS

You MUST use the exact tags below. The frontend parses these tags to build a layered report.

[SUMMARY_CONTRIBUTION]
One sentence summarizing cross-clause risks for a non-expert. Example: "Three clause combinations create compounding penalties that could cost you thousands if you're ever late on a single payment." No jargon. No clause numbers. Concrete consequence.
[/SUMMARY_CONTRIBUTION]

For each cross-clause interaction, emit a [FINDING] block:

[FINDING id="interactions_1"]
[FINDING_TITLE]Human-readable title that passes the "would you text this to a friend?" test. NOT legal jargon. Example: "If you're late once, you might never catch up"[/FINDING_TITLE]
[FINDING_SOURCE]Quote the EXACT text from EACH clause involved. Label each:
Clause A (Section X): "verbatim text..."
Clause B (Section Y): "verbatim text..."
Use the document's actual words, not a paraphrase.[/FINDING_SOURCE]
[FINDING_EXPLANATION]2-3 sentences in plain language. Concrete. With numbers from the document. Example: "Separately, each clause looks normal — a $50 late fee and a payment priority order. Together, your late fee gets paid BEFORE your rent, so next month you're 'short' again. The cycle never ends."[/FINDING_EXPLANATION]
[FINDING_SEVERITY]standard | aggressive | unusual[/FINDING_SEVERITY]
[FINDING_SEVERITY_CONTEXT]One sentence: why this severity. "Standard" = typical for this document type. "Aggressive" = goes further than usual. "Unusual" = rarely seen.[/FINDING_SEVERITY_CONTEXT]
[FINDING_ACTION]One concrete action. The most effective thing the reader can do about THIS specific risk.[/FINDING_ACTION]
[/FINDING]

Emit one [FINDING] block per interaction. Find at least 3.

[DEEP_CONTENT]
## Cross-Clause Interactions — Deep Analysis

For each interaction above, provide the deep read:

### [Same title as the FINDING]

**Read separately, you'd see:** What these clauses appear to say independently. One sentence.

**Read together, you'd realize:** What they ACTUALLY do when combined. One sentence, visceral.

**Clauses involved:** [list specific sections WITH context]

**How they interact:** [2-3 sentences. The mechanism.]

[RED/YELLOW] · Trick: [TRICK_CATEGORY]

**If they meant well:** [1-2 sentences, generous interpretation]

**If they meant every word:** [2-3 sentences, adversarial, villain voice — deliberately exaggerated, the user expects this framing]

→ YOUR MOVE: [One concrete action]

---
[/DEEP_CONTENT]

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
- Every [FINDING] MUST include verbatim source text from the document — this is non-negotiable
- [FINDING_TITLE] must be human language a friend would understand — NO legal jargon
- [FINDING_SEVERITY] must be exactly one of: standard, aggressive, unusual
- [DEEP_CONTENT] contains the villain voice — NEVER put villain voice in [FINDING] blocks
- The bad intentions voice is deliberately adversarial and exaggerated — the user expects this framing
- Use your full extended thinking budget to reason across the entire document
- Be thorough — connect clauses that the reader would never connect on their own
"""


def build_asymmetry_prompt(has_images=False):
    """Opus thread 2: Power asymmetry + fair standard comparison. Findings + deep content."""
    visual_block = ""
    if has_images:
        visual_block = "\n\nPage images are included. Reference visual tricks (fine print, buried placement) in your analysis."

    return f"""You are a senior attorney. Measure the power imbalance in this document and compare its worst clauses against industry norms. This is your ONLY job.
{visual_block}
## LANGUAGE RULE
ALWAYS respond in ENGLISH regardless of the document's language. When quoting text from the document, keep quotes in the original language and add an English translation in parentheses if the quote is not in English.

## OUTPUT FORMAT — TAGGED SECTIONS

You MUST use the exact tags below. The frontend parses these tags to build a layered report.

[SUMMARY_CONTRIBUTION]
One sentence about the power balance. Include the power ratio as one number. Example: "They have 4× more rights than you, and 3 clauses go further than what's standard for this type of agreement." No jargon.
[/SUMMARY_CONTRIBUTION]

For each unfair clause compared against industry norms, emit a [FINDING] block:

[FINDING id="asymmetry_1"]
[FINDING_TITLE]Human-readable title. NOT "Unlimited Indemnification Flowing One Way Against a $100 Wall". YES: "If you get hurt on their trip, you pay their lawyer"[/FINDING_TITLE]
[FINDING_SOURCE]Quote the EXACT clause text from the document. Use the document's actual words, not a paraphrase. If multiple clauses are involved, label each.[/FINDING_SOURCE]
[FINDING_EXPLANATION]2-3 sentences. What this means in concrete terms. With numbers from the document where possible. Example: "If you trip on their trip and break your leg, you pay their legal bills — not the other way around. There's no cap on what you'd owe. Meanwhile, if they cancel the trip entirely, the most they'd give you is $100."[/FINDING_EXPLANATION]
[FINDING_SEVERITY]standard | aggressive | unusual[/FINDING_SEVERITY]
[FINDING_SEVERITY_CONTEXT]One sentence. For "standard": "This is typical for [document type]. Most [type] have this." For "aggressive": "This goes further than usual. A fair version would [what's standard]." For "unusual": "This is rarely seen. In a fair version, [what you'd expect]."[/FINDING_SEVERITY_CONTEXT]
[FINDING_ACTION]One concrete action the reader can take about THIS specific imbalance.[/FINDING_ACTION]
[/FINDING]

Emit 2-3 [FINDING] blocks for the worst imbalances.

[DEEP_CONTENT]
## Power Balance — Deep Analysis

**Your rights:** [count] · **Your obligations:** [count] · **Their rights:** [count] · **Their obligations:** [count] · **"Sole discretion" (them):** [count]×

**Power Ratio: [Their rights]:[Your rights]** — [one sentence]

## Fair Standard Comparison

For each comparison (2-3 max):

### [Clause/Area]
**This document says:** [what the clause actually states — one sentence]
**A fair version would say:** [what a balanced, industry-standard clause would look like — one sentence]
**The gap:** [why the difference matters to the reader — one sentence]

This section answers: "Is this document UNUSUALLY aggressive, or is this just how these documents work?"
[/DEEP_CONTENT]

## RULES
- Every [FINDING] MUST include verbatim source text from the document — this is non-negotiable
- [FINDING_TITLE] must be human language a friend would understand — NO legal jargon
- [FINDING_SEVERITY] must be exactly one of: standard, aggressive, unusual
- Power Asymmetry: count precisely from the document, don't estimate or round
- Fair Standard: be specific about industry norms — cite what's standard
- Use your full extended thinking budget
"""


def build_archaeology_prompt(has_images=False):
    """Opus thread 3: Document archaeology (boilerplate vs custom) + drafter profile. Findings + deep content."""
    visual_block = ""
    if has_images:
        visual_block = "\n\nPage images are included. Look for visual formatting differences between boilerplate and custom sections."

    return f"""You are a senior attorney. Analyze this document's construction: which parts are boilerplate vs custom-drafted, and profile the type of entity that created it. This is your ONLY job.
{visual_block}
## LANGUAGE RULE
ALWAYS respond in ENGLISH regardless of the document's language. When quoting text from the document, keep quotes in the original language and add an English translation in parentheses if the quote is not in English.

## OUTPUT FORMAT — TAGGED SECTIONS

You MUST use the exact tags below. The frontend parses these tags to build a layered report.

[SUMMARY_CONTRIBUTION]
One sentence about the document's construction. Example: "Most of this contract is standard boilerplate, but 3 custom-added clauses reveal the drafter's real priorities — and they all favor the landlord." No jargon.
[/SUMMARY_CONTRIBUTION]

If any custom-drafted clauses reveal deliberate risk-shifting, emit [FINDING] blocks:

[FINDING id="archaeology_1"]
[FINDING_TITLE]Human-readable title about what the custom clause does. Example: "They added a clause specifically to limit your deposit refund"[/FINDING_TITLE]
[FINDING_SOURCE]Quote the EXACT custom clause text from the document. Use the document's actual words, not a paraphrase.[/FINDING_SOURCE]
[FINDING_EXPLANATION]2-3 sentences. Why this was custom-added and what it reveals about the drafter's intent. What does a boilerplate version of this clause look like?[/FINDING_EXPLANATION]
[FINDING_SEVERITY]standard | aggressive | unusual[/FINDING_SEVERITY]
[FINDING_SEVERITY_CONTEXT]One sentence. Is this custom addition typical? How does it compare to what's standard?[/FINDING_SEVERITY_CONTEXT]
[FINDING_ACTION]One concrete action the reader can take.[/FINDING_ACTION]
[/FINDING]

Only emit [FINDING] blocks for CUSTOM clauses that shift risk. Boilerplate sections do NOT need findings — they go in [DEEP_CONTENT].

[DEEP_CONTENT]
## Document Archaeology — Deep Analysis

For each major section, one word: **Boilerplate** or **Custom**. Then 1-2 sentences naming which clauses got custom attention and what that reveals about the drafter's priorities.

## Who Drafted This

[2-3 sentences profiling what TYPE of drafter produces this document structure and what it signals about how they will behave. The drafter profile should predict BEHAVIOR, not just describe structure. Example: "This lease pattern is typical of high-volume property management companies optimizing for automated enforcement and minimal tenant interaction. Expect slow repair responses, aggressive deposit deductions, and form-letter communication."]
[/DEEP_CONTENT]

## RULES
- Every [FINDING] MUST include verbatim source text from the document — this is non-negotiable
- [FINDING_TITLE] must be human language a friend would understand — NO legal jargon
- [FINDING_SEVERITY] must be exactly one of: standard, aggressive, unusual
- Only create [FINDING] blocks for CUSTOM clauses that shift risk — not for boilerplate
- Document Archaeology: be honest — if most clauses are boilerplate, say so. The custom clauses are the signal
- Use your full extended thinking budget
"""


def build_verdict_prompt(has_images=False):
    """Single Opus verdict thread: one-screen report for normal people.
    Covers cross-clause interactions, power balance, drafter profile, and overall assessment
    in one coherent pass. Auto-detects jurisdiction from document text."""
    visual_block = ""
    if has_images:
        visual_block = "\n\nPage images are included. Look for visual tricks: fine print, buried placement, dense tables, light-gray disclaimers."

    return f"""You are a senior attorney writing a verdict for someone who NEVER reads contracts. They will read ONE screen and then close the tab. Make every word count.

Your job: analyze this ENTIRE document — cross-clause interactions, power balance, drafter intent, and overall risk — in ONE coherent report. You are the only expert. Be thorough in your thinking, ruthlessly concise in your output.
{visual_block}
## LANGUAGE RULE
ALWAYS respond in ENGLISH regardless of the document's language. When quoting text from the document, keep quotes in the original language and add an English translation in parentheses if the quote is not in English.

## OUTPUT FORMAT — TAGGED SECTIONS

You MUST use the exact tags below. The frontend parses these tags.

[VERDICT_TIER]
EXACTLY ONE of these — the tier name must appear verbatim:
- SIGN WITH CONFIDENCE
- READ THE FLAGGED CLAUSES
- NEGOTIATE BEFORE SIGNING
- SEEK LEGAL REVIEW
- DO NOT SIGN
[/VERDICT_TIER]

[WHAT_IS_THIS]
One sentence. What is this document, who are the parties, what's the deal?
Example: "This is a Coca-Cola sweepstakes — a lottery for a trip worth $57,000."
Example: "This is a 12-month residential lease between you and GreenTree Property Management."
[/WHAT_IS_THIS]

[SHOULD_YOU_WORRY]
One sentence. Calibrated to actual severity. NOT always alarming.
For a clean document: "This is a standard agreement with typical protections."
For a conditional risk: "If you only enter: low risk. If you WIN: read on."
For a bad document: "This contract has serious problems you need to address before signing."
[/SHOULD_YOU_WORRY]

[THE_MAIN_THING]
The single worst risk in this document. 2-3 sentences MAX.
Must name a concrete consequence: a dollar amount, a time limit, a right you lose.
Must quote or reference the actual clause text so the user can verify.
NOT: "Unlimited Indemnification Flowing One Way Against a $100 Wall"
YES: "If you get hurt on their trip, YOU pay their lawyer — not the other way around. There's no cap on what you'd owe. Meanwhile, the most they'd pay you for anything is $100."
If jurisdiction is provided and this clause violates local law, say so: "This may actually be illegal under [statute]."
[/THE_MAIN_THING]

[ONE_ACTION]
One sentence. The single most effective thing the user should do.
For negotiable docs: "Ask to change [specific thing] to [specific alternative]."
For non-negotiable docs: "Before signing, check whether [specific thing]."
For already-accepted docs: "If [trigger], your first step is [action]."
[/ONE_ACTION]

[POWER_RATIO]
One line: "Their rights: N — Your rights: N" or "They have Nx more rights than you."
[/POWER_RATIO]

[RISKS]
2-4 additional risks beyond the main thing, each as ONE sentence.
Order by impact on the reader's wallet/rights, worst first.
Each risk names a concrete consequence.
Separate risks with newlines.
[/RISKS]

[CHECKLIST]
Chronological action list. Things to DO, in ORDER.
Adapt sections to document type:
- "Before you sign:" / "After you sign:" / "If something goes wrong:"
- Or: "If you win:" / "If something changes:"
Max 5 items per section. Max 3 sections.
Each item references something SPECIFIC from the document.
For fair documents: "No unusual actions needed."
[/CHECKLIST]

[FLAGGED_CLAIMS]
List EVERY flagged (RED/YELLOW) clause. For EACH one, output exactly:
- **Clause title (section reference)** — ONE sentence: what this means for YOU, the consumer. Concrete consequence.

Order by risk score (highest first). Include ALL flagged clauses — do not skip any.
If pre-analyzed claims are provided after the document text, use those as your source and cover every one.
If no pre-analyzed claims are available, identify them yourself from the document.
For fair documents with no flagged clauses: "No clauses were flagged."
[/FLAGGED_CLAIMS]

[COLOPHON]
2-3 sentences about how you analyzed this document. Be specific about what reasoning you used.
End with: "This is not legal advice."
[/COLOPHON]

[JURISDICTION]
Auto-detect the jurisdiction from the document text.
Look for: governing law clauses, addresses, state/country references, regulatory bodies mentioned, court jurisdictions named.
Output format:
- Line 1: The jurisdiction (e.g., "California, USA" or "Netherlands, EU" or "Unknown")
- Line 2+: If jurisdiction is identified, note any clauses that VIOLATE local law — cite the specific statute.
  Distinguish ILLEGAL (void/unenforceable under local law) from merely UNFAIR (bad but legal).
  Warn about MISSING required clauses for this jurisdiction.
  If uncertain about a specific law, say "check with a local attorney" rather than guessing.
- If no jurisdiction can be determined: "Jurisdiction could not be determined from the document text. The analysis above is jurisdiction-neutral."
[/JURISDICTION]

## ANALYSIS INSTRUCTIONS
Before writing your output, use your full extended thinking budget to:
1. Read the ENTIRE document — every clause, every section
2. Find cross-clause COMBINATIONS that create compound risks invisible when reading linearly
3. Count the power balance: your rights vs their rights, your obligations vs theirs
4. Identify which sections are boilerplate vs custom-drafted — custom sections reveal the drafter's real priorities
5. Assess overall severity — calibrate to real-world stakes, not just the count of red flags
6. Self-check: any false positives? Any blind spots? Standard language incorrectly flagged?
7. Identify the jurisdiction — look for governing law clauses, addresses, regulatory references

## TRICK CATEGORIES (use in your thinking, not in output):
Silent Waiver, Burden Shift, Time Trap, Escape Hatch, Moving Target, Forced Arena,
Phantom Protection, Cascade Clause, Sole Discretion, Liability Cap, Reverse Shield,
Auto-Lock, Content Grab, Data Drain, Penalty Disguise, Gag Clause, Scope Creep, Ghost Standard

## RULES
- The user will read ONE screen. Every word must earn its place.
- [THE_MAIN_THING] is the heart of the report. Get this right.
- NEVER use legal jargon in the output. Write like you're texting a friend.
- Calibrate severity: a fair document should say "you're fine." Don't invent problems.
- Bold only dollar amounts and time limits — nothing else.
- Do NOT repeat information across sections. Each tag has ONE job.
- Use your full extended thinking budget — thorough thinking, concise output.
"""


def build_synthesis_prompt():
    """Opus thread 5: Expert Panel Synthesis — reads all 4 expert reports and produces a 4-voice synthesis."""
    return """You are the SYNTHESIS CHAIR of a 4-expert panel that just analyzed a legal document. You have access to ALL four expert reports. Your job: produce a unified synthesis that NO individual expert could write alone.

## LANGUAGE RULE
ALWAYS respond in ENGLISH regardless of the document's language.

## YOUR 4 VOICES — output ALL four sections in this exact order:

## What You Need to Know

Plain-language briefing for a non-expert. 8th-grade reading level. THIS IS YOUR LARGEST SECTION (400-600 words).

Structure:
1. **One-sentence verdict** — what this document IS, in plain terms
2. **The 3 biggest risks** — explain each in simple language. No jargon. Cite which expert flagged it.
3. **What to do right now** — numbered action list (5-7 items), specific and concrete
4. **Email you can send** — a ready-to-copy paragraph the reader can send to the other party. Professional tone, cites specific clause numbers, requests specific changes. Start with "Dear [Other Party],"

## If They Meant Well

Good-faith interpretation. Steelman the drafter's position (200-300 words).
- For each major flagged clause, explain WHY it might exist for legitimate business reasons
- Reference which expert flagged it and provide the charitable counter-reading
- Acknowledge industry norms that might explain harsh-looking language
- End with: "The most charitable reading of this document is that..."

## If They Meant Every Word

Bad-faith interpretation — villain voice applied to the WHOLE DOCUMENT as a system (200-300 words).
- Do NOT go clause-by-clause — treat the document as one coordinated strategy
- What is the document DESIGNED to achieve if every clause is enforced to maximum effect?
- Use vivid, specific language: "This isn't a lease — it's a revenue optimization machine with a bed attached"
- Reference findings from multiple experts to build the systemic picture
- End with the single most devastating sentence about what signing means

## Cross-Expert Connections

Where the 4 expert reports converge, contradict, or reveal hidden patterns (200-300 words).
- **Convergences**: Which risks did multiple experts independently flag? (This strengthens the signal)
- **Contradictions**: Did experts disagree on severity or interpretation? Why?
- **Hidden patterns**: What emerges ONLY when you read all 4 reports together? (e.g., custom-drafted sections correlating with the harshest terms, boilerplate providing cover for bespoke traps)
- **The one thing everyone missed**: Is there a risk that falls between expert domains?

## RULES
- DO NOT repeat or summarize the 4 expert reports — the user has already read them
- Every claim MUST reference specific findings from specific experts (e.g., "The Archaeology expert found...", "Both the Interactions and Asymmetry experts flagged...")
- "What You Need to Know" MUST be the longest section
- Total output target: 1000-1500 words
- COMPLETION IS MANDATORY — never truncate
- Use your full extended thinking budget to find cross-expert patterns before writing
"""


def build_synthesis_user_content(user_msg, thread_texts):
    """Build user message for synthesis: original document + all 4 expert reports."""
    parts = [user_msg]
    labels = {
        'interactions': 'CROSS-CLAUSE INTERACTIONS EXPERT',
        'asymmetry': 'POWER ASYMMETRY EXPERT',
        'archaeology': 'DOCUMENT ARCHAEOLOGY EXPERT',
        'overall': 'OVERALL ASSESSMENT EXPERT',
    }
    for source in ['interactions', 'asymmetry', 'archaeology', 'overall']:
        text = thread_texts.get(source, '').strip()
        if text:
            parts.append(f"\n\n---BEGIN {labels[source]} REPORT---\n\n{text}\n\n---END {labels[source]} REPORT---")
    return '\n'.join(parts)


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
                    text, _ = extract_pdf(file)
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
        store_document(doc_id, {
            'text': texts[0],
            'text2': texts[1],
            'filename': filenames[0],
            'filename2': filenames[1],
            'depth': depth,
            'mode': 'compare',
        })

        return jsonify({
            'doc_id': doc_id,
            'filename': filenames[0] + ' vs ' + filenames[1],
            'text_length': len(texts[0]) + len(texts[1]),
            'preview': texts[0][:150] + '\n---\n' + texts[1][:150],
            'full_text': texts[0],
            'mode': 'compare',
        })
    except Exception as e:
        print(f'[upload/compare] Error: {e}')
        return jsonify({'error': 'An internal error occurred. Please try again.'}), 500


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
            block = event.content_block
            state['current_block'] = block.type
            if block.type == 'tool_use':
                state['current_tool_name'] = block.name
                state['current_tool_input_json'] = ''
                chunks.append(sse('tool_start', json.dumps({'name': block.name})))
            else:
                chunks.append(sse(f'{block.type}_start'))
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
            elif event.delta.type == 'input_json_delta':
                state['current_tool_input_json'] += event.delta.partial_json
        elif event.type == 'content_block_stop':
            if state['current_block'] == 'tool_use':
                tool_name = state.get('current_tool_name', '')
                try:
                    tool_input = json.loads(state['current_tool_input_json'])
                except json.JSONDecodeError:
                    tool_input = {}
                state['tool_results'].append({'name': tool_name, 'data': tool_input})
                chunks.append(sse('tool_result', json.dumps({'name': tool_name, 'data': tool_input})))
                state['current_tool_name'] = None
                state['current_tool_input_json'] = ''
            elif state['current_block']:
                chunks.append(sse(f'{state["current_block"]}_done'))
            state['current_block'] = None
        return chunks

    def run_single_stream(client, user_msg, system_prompt, preset):
        """Single API call — used for comparison mode."""
        state = {
            'current_block': None,
            'phase_buffer': '',
            'detected_phases': set(),
            'current_tool_name': None,
            'current_tool_input_json': '',
            'tool_results': [],
        }
        stream = None
        try:
            yield sse('phase', 'thinking')
            create_kwargs = {
                'model': MODEL,
                'max_tokens': preset['max_tokens'],
                'thinking': {'type': 'adaptive'},
                'system': [{'type': 'text', 'text': system_prompt, 'cache_control': {'type': 'ephemeral'}}],
                'messages': [{'role': 'user', 'content': user_msg}],
                'stream': True,
            }
            stream = client.messages.create(**create_kwargs)
            for event in stream:
                for chunk in process_stream_event(event, state):
                    yield chunk
                if event.type == 'message_stop':
                    yield sse('done')
        finally:
            if stream:
                stream.close()

    def run_parallel(client, user_msg, preset):
        """Two parallel API calls: Haiku full cards + single Opus verdict."""
        q = queue_module.Queue()
        timings = {}
        cancel = threading.Event()  # Signal to cancel Opus threads (e.g. doc not applicable)

        def worker(label, system_prompt, max_out,
                   model=MODEL, use_thinking=True, user_content=None, tools=None):
            stream = None
            t0 = time.time()
            try:
                msg_content = user_content if user_content is not None else user_msg
                create_kwargs = {
                    'model': model,
                    'max_tokens': max_out,
                    'system': [{'type': 'text', 'text': system_prompt, 'cache_control': {'type': 'ephemeral'}}],
                    'messages': [{'role': 'user', 'content': msg_content}],
                    'stream': True,
                }
                if use_thinking:
                    create_kwargs['thinking'] = {'type': 'adaptive'}
                if tools:
                    create_kwargs['tools'] = tools
                stream = client.messages.create(**create_kwargs)
                for event in stream:
                    if cancel.is_set():
                        break
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

        # Deep analysis token budget
        deep_max_tokens = max(preset['max_tokens'], 80000)

        # Build vision content for deep analysis if page images exist
        page_images = doc.get('page_images', [])
        deep_user_content = None
        if page_images:
            deep_user_content = [{'type': 'text', 'text': user_msg}]
            for i, img_b64 in enumerate(page_images):
                deep_user_content.append({'type': 'text', 'text': f'[Page {i + 1} visual layout:]'})
                deep_user_content.append({
                    'type': 'image',
                    'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': img_b64},
                })

        has_images = bool(page_images)

        yield sse('phase', 'thinking')

        # ── Non-blocking check: are pre-generated cards ready? ──
        precards_event = doc.get('_precards_event')
        claims_summary = ''
        if precards_event and precards_event.is_set():
            ps = doc.get('_prescan')
            pc = doc.get('_precards')
            if (ps and ps.get('clauses') and pc and pc.get('cards')):
                claims_summary = _build_claims_summary(ps, pc)

        # ── Start Opus verdict at t=0 — enriched with card data if available ──
        verdict_max = max(deep_max_tokens, 80000)
        opus_user = deep_user_content
        if claims_summary:
            if isinstance(opus_user, list):
                # Image mode: replace first text block with enriched version
                opus_user = [{'type': 'text', 'text': user_msg + '\n\n' + claims_summary}] + opus_user[1:]
            else:
                opus_user = (opus_user or user_msg) + '\n\n' + claims_summary
            print(f'[verdict] Opus enriched with {len(claims_summary)} chars of card context')
        t_opus = threading.Thread(
            target=worker,
            args=('overall', build_verdict_prompt(has_images=has_images),
                  verdict_max, MODEL, True),
            kwargs={'user_content': opus_user},
            daemon=True,
        )
        t_opus.start()

        # ── Check for pre-generated cards (fastest path) ──
        if precards_event:
            precards_event.wait(timeout=25)
        prescan = doc.get('_prescan')
        precards = doc.get('_precards')

        if (prescan and prescan.get('clauses') and precards
                and precards.get('cards')
                and '**Not Applicable**' not in prescan.get('scan_text', '')):
            # Cards pre-generated during upload — emit instantly!
            print(f'[scan] Using pre-generated cards ({len(precards["cards"])} cards, '
                  f'ready during upload)')
            profile_text = prescan['profile_text']
            if profile_text:
                yield sse('text', profile_text + '\n\n---\n\n')
            for card_text in precards['cards']:
                card_text = card_text.strip().strip('-').strip()
                if card_text:
                    yield sse('text', card_text + '\n\n---\n\n')
            clause_count = sum(
                1 for c in precards['cards']
                if c and 'Fair Clauses Summary' not in c)
            yield sse('quick_done', json.dumps({
                'seconds': 0.1, 'model': FAST_MODEL}))
            yield sse('handoff', json.dumps({
                'tricks_found': 0, 'summary': '',
                'clause_count': clause_count,
                'not_applicable': False,
            }))
            # Only wait for Opus verdict
            yield from _run_parallel_cards(q, timings, cancel, 0)
            return

        # ── Phase 1: Use pre-scan results or fall back to blocking scan ──
        t0_scan = time.time()
        scan_text = ''
        if prescan and prescan.get('clauses'):
            # Pre-scan completed during upload — use cached results
            scan_text = prescan['scan_text']
            profile_text = prescan['profile_text']
            clauses = prescan['clauses']
            green_text = prescan['green_text']
            timings['scan'] = prescan.get('seconds', 0)
            print(f'[scan] Using pre-scan results ({len(clauses)} clauses, {timings["scan"]}s during upload)')
        elif prescan and '**Not Applicable**' in prescan.get('scan_text', ''):
            # Pre-scan found not applicable
            scan_text = prescan['scan_text']
            profile_text = prescan.get('profile_text', '')
            clauses = []
            green_text = ''
            timings['scan'] = prescan.get('seconds', 0)
        else:
            # No pre-scan or pre-scan failed — blocking scan
            try:
                scan_response = client.messages.create(
                    model=FAST_MODEL,
                    max_tokens=4000,
                    system=[{
                        'type': 'text',
                        'text': build_clause_id_prompt(),
                        'cache_control': {'type': 'ephemeral'},
                    }],
                    messages=[{'role': 'user', 'content': user_msg}],
                )
                scan_text = scan_response.content[0].text
            except Exception as e:
                print(f'[scan] Phase 1 failed: {e}, falling back to single-pass')
                quick_max = max(16000, min(32000, len(doc['text']) // 2))
                t_quick = threading.Thread(
                    target=worker,
                    args=('quick', build_card_scan_prompt(), quick_max,
                          FAST_MODEL, False),
                    daemon=True,
                )
                t_quick.start()
                yield from _run_parallel_fallback(q, timings, cancel)
                return

            timings['scan'] = round(time.time() - t0_scan, 1)
            print(f'[scan] Phase 1 complete in {timings["scan"]}s')

            # Parse identification output
            profile_text, clauses, green_text = parse_identification_output(scan_text)

        # ── Handle Not Applicable ──
        if '**Not Applicable**' in scan_text or not clauses:
            if profile_text:
                yield sse('text', profile_text + '\n')
            cancel.set()
            yield sse('quick_done', json.dumps({
                'seconds': timings['scan'], 'model': FAST_MODEL}))
            yield sse('handoff', json.dumps({
                'tricks_found': 0, 'summary': '',
                'clause_count': 0,
                'not_applicable': '**Not Applicable**' in scan_text}))
            yield sse('done', json.dumps({
                'quick_seconds': timings['scan'], 'deep_seconds': 0, 'model': MODEL}))
            return

        # ── Emit Document Profile ──
        if profile_text:
            yield sse('text', profile_text + '\n\n---\n\n')

        # ── Phase 2: Parallel per-clause card generation ──
        card_system = build_single_card_system(doc['text'])
        total_cards = len(clauses) + (1 if green_text else 0)
        print(f'[scan] Starting {total_cards} parallel card workers '
              f'({len(clauses)} clauses + {"1 green" if green_text else "0 green"})')

        for i, clause_info in enumerate(clauses):
            card_user_msg = (
                f"Generate a complete flip card for this specific clause:\n\n"
                f"Title: {clause_info['title']}\n"
                f"Section Reference: {clause_info.get('section', 'Not specified')}\n"
                f"Risk Level: {clause_info['risk']}\n"
                f"Score: {clause_info['score']}/100\n"
                f"Trick Category: {clause_info['trick']}\n"
                f"Key Quote: \"{clause_info['quote']}\"\n\n"
                f"Analyze the clause in the document and output the COMPLETE flip card."
            )
            t = threading.Thread(
                target=worker,
                args=(f'card_{i}', card_system, 4000, FAST_MODEL, False),
                kwargs={'user_content': card_user_msg},
                daemon=True,
            )
            t.start()

        # Green summary card
        if green_text:
            green_idx = len(clauses)
            t = threading.Thread(
                target=worker,
                args=(f'card_{green_idx}', card_system, 2000, FAST_MODEL, False),
                kwargs={'user_content': build_green_summary_user(green_text)},
                daemon=True,
            )
            t.start()

        yield from _run_parallel_cards(q, timings, cancel, total_cards)

    def _run_parallel_cards(q, timings, cancel, total_cards):
        """Event loop for parallel per-clause card generation + Opus verdict.
        Cards are buffered and emitted in order as they complete."""

        OPUS_SOURCES = {'overall'}

        start_time = time.time()
        card_texts = {}
        card_done_flags = {}
        next_card_to_emit = 0
        cards_all_done = (total_cards == 0)  # Pre-generated cards: already emitted
        done_flags = {s: False for s in OPUS_SOURCES}
        thread_texts = {s: '' for s in OPUS_SOURCES}

        def all_done():
            return cards_all_done and all(done_flags.values())

        while not all_done():
            # ── Wall-clock timeout ──
            if time.time() - start_time > 300:
                cancel.set()
                yield sse('error', 'Analysis timed out after 5 minutes')
                yield sse('done', json.dumps({
                    'quick_seconds': timings.get('scan', 0),
                    'deep_seconds': max((timings.get(s, 0) for s in OPUS_SOURCES), default=0),
                    'model': MODEL}))
                return

            try:
                source, event = q.get(timeout=1.0)
            except queue_module.Empty:
                continue

            # ── Error handling ──
            if source == 'error':
                error_msg = str(event)
                error_source = error_msg.split(':')[0] if ':' in error_msg else ''
                yield sse('error', error_msg)
                if error_source.startswith('card_'):
                    try:
                        idx = int(error_source.split('_')[1])
                        card_done_flags[idx] = True
                        card_texts.setdefault(idx, '')
                    except (IndexError, ValueError):
                        pass
                elif error_source in OPUS_SOURCES:
                    done_flags[error_source] = True
                continue

            # ── Card streaming events: accumulate text per card ──
            if source.startswith('card_') and not source.endswith('_done'):
                idx = int(source.split('_')[1])
                card_texts.setdefault(idx, '')
                if hasattr(event, 'type') and event.type == 'content_block_delta':
                    delta = event.delta
                    if hasattr(delta, 'type') and delta.type == 'text_delta':
                        card_texts[idx] += delta.text
                continue

            # ── Card done: buffer and emit in order ──
            if source.startswith('card_') and source.endswith('_done'):
                idx_str = source[5:-5]  # 'card_0_done' → '0'
                idx = int(idx_str)
                card_done_flags[idx] = True

                # Emit all consecutive completed cards from buffer
                while next_card_to_emit < total_cards and card_done_flags.get(next_card_to_emit):
                    card_text = card_texts.get(next_card_to_emit, '').strip()
                    if card_text:
                        # Strip any leading/trailing --- the model might add
                        card_text = card_text.strip('-').strip()
                        yield sse('text', card_text + '\n\n---\n\n')
                    next_card_to_emit += 1

                # All cards done?
                if next_card_to_emit >= total_cards:
                    cards_all_done = True
                    card_times = [timings.get(f'card_{i}', 0) for i in range(total_cards)]
                    max_card_time = max(card_times) if card_times else 0
                    # Report wall-clock time from analysis start (not cumulative)
                    total_quick = round(time.time() - start_time, 1)

                    yield sse('quick_done', json.dumps({
                        'seconds': total_quick, 'model': FAST_MODEL}))

                    # Count RED/YELLOW clauses (exclude green summary)
                    clause_count = sum(
                        1 for i in range(total_cards)
                        if card_texts.get(i, '')
                        and 'Fair Clauses Summary' not in card_texts.get(i, ''))

                    yield sse('handoff', json.dumps({
                        'tricks_found': 0,
                        'summary': '',
                        'clause_count': clause_count,
                        'not_applicable': False,
                    }))
                continue

            # ── Opus source done ──
            if source.endswith('_done') and source[:-5] in OPUS_SOURCES:
                opus_label = source[:-5]
                done_flags[opus_label] = True
                yield sse(f'{opus_label}_done', json.dumps({
                    'seconds': timings.get(opus_label, 0)}))
                continue

            # ── Opus stream events ──
            if source in OPUS_SOURCES:
                if not hasattr(event, 'type'):
                    continue
                if event.type == 'content_block_delta':
                    delta = event.delta
                    if hasattr(delta, 'type') and delta.type == 'text_delta':
                        thread_texts[source] += delta.text
                        yield sse(f'{source}_text', delta.text)
                    elif hasattr(delta, 'type') and delta.type == 'thinking_delta':
                        yield sse(f'{source}_thinking', delta.thinking)

        # ── Final done event ──
        yield sse('done', json.dumps({
            'quick_seconds': timings.get('scan', 0),
            'deep_seconds': max((timings.get(s, 0) for s in OPUS_SOURCES), default=0),
            'model': MODEL}))

    def _run_parallel_fallback(q, timings, cancel):
        """Fallback event loop: single Haiku stream + single Opus verdict.
        Used when Phase 1 identification scan fails."""

        OPUS_SOURCES = {'overall'}

        start_time = time.time()
        state_quick = _make_stream_state()
        quick_text = ''
        quick_done = False
        done_flags = {s: False for s in OPUS_SOURCES}
        thread_texts = {s: '' for s in OPUS_SOURCES}  # Accumulate for synthesis
        synthesis_started = False
        synthesis_done = False

        def all_done():
            base = quick_done and all(done_flags.values())
            if not base:
                return False
            if synthesis_started:
                return synthesis_done
            return True

        while not all_done():
            # ── Wall-clock timeout: fires even if queue has events ──
            if time.time() - start_time > 300:
                cancel.set()
                yield sse('error', 'Analysis timed out after 5 minutes')
                yield sse('done', json.dumps({
                    'quick_seconds': timings.get('quick', 0),
                    'deep_seconds': max((timings.get(s, 0) for s in OPUS_SOURCES), default=0),
                    'model': MODEL}))
                return

            try:
                source, event = q.get(timeout=1.0)
            except queue_module.Empty:
                continue

            # ── Accumulate Haiku text for suitability check ──
            if source == 'quick' and hasattr(event, 'type'):
                if event.type == 'content_block_delta':
                    delta = event.delta
                    if hasattr(delta, 'type') and delta.type == 'text_delta':
                        quick_text += delta.text

            # ── Error handling ──
            if source == 'error':
                error_msg = str(event)
                error_source = error_msg.split(':')[0] if ':' in error_msg else ''
                yield sse('error', error_msg)
                if error_source == 'quick':
                    cancel.set()
                    yield sse('done', json.dumps({
                        'quick_seconds': 0, 'deep_seconds': 0, 'model': MODEL}))
                    return
                elif error_source in OPUS_SOURCES:
                    done_flags[error_source] = True
                elif error_source == 'synthesis':
                    synthesis_done = True  # Don't block completion on synthesis failure
                continue

            # ── Quick (Haiku full cards) done ──
            if source == 'quick_done':
                quick_done = True
                qt = timings.get('quick', 0)
                yield sse('quick_done', json.dumps({
                    'seconds': qt, 'model': FAST_MODEL}))

                doc_not_applicable = '**Not Applicable**' in quick_text
                clause_count = max(0, len(re.findall(r'\n---\n', quick_text)) - 1)

                yield sse('handoff', json.dumps({
                    'tricks_found': 0,
                    'summary': '',
                    'clause_count': clause_count,
                    'not_applicable': doc_not_applicable,
                }))

                if doc_not_applicable:
                    cancel.set()
                    yield sse('done', json.dumps({
                        'quick_seconds': qt, 'deep_seconds': 0, 'model': MODEL}))
                    return
                continue

            # ── Opus source done ──
            if source.endswith('_done') and source[:-5] in OPUS_SOURCES:
                opus_label = source[:-5]
                done_flags[opus_label] = True
                yield sse(f'{opus_label}_done', json.dumps({
                    'seconds': timings.get(opus_label, 0)}))

                # Synthesis skipped — single verdict thread covers everything

                continue

            # ── Synthesis done ──
            if source == 'synthesis_done':
                synthesis_done = True
                yield sse('synthesis_done', json.dumps({
                    'seconds': timings.get('synthesis', 0)}))
                continue

            # ── Stream events ──
            if source == 'quick':
                for chunk in process_stream_event(event, state_quick):
                    yield chunk

            elif source in OPUS_SOURCES:
                # Each Opus source dispatches to its own SSE channel
                if not hasattr(event, 'type'):
                    continue
                if event.type == 'content_block_delta':
                    delta = event.delta
                    if hasattr(delta, 'type') and delta.type == 'text_delta':
                        thread_texts[source] += delta.text  # Accumulate for synthesis
                        yield sse(f'{source}_text', delta.text)
                    elif hasattr(delta, 'type') and delta.type == 'thinking_delta':
                        yield sse(f'{source}_thinking', delta.thinking)

            elif source == 'synthesis':
                # Synthesis thread streams its own SSE channel
                if not hasattr(event, 'type'):
                    continue
                if event.type == 'content_block_delta':
                    delta = event.delta
                    if hasattr(delta, 'type') and delta.type == 'text_delta':
                        yield sse('synthesis_text', delta.text)
                    elif hasattr(delta, 'type') and delta.type == 'thinking_delta':
                        yield sse('synthesis_thinking', delta.thinking)

        # ── Final done event ──
        yield sse('done', json.dumps({
            'quick_seconds': timings.get('quick', 0),
            'deep_seconds': max((timings.get(s, 0) for s in OPUS_SOURCES), default=0),
            'synthesis_seconds': timings.get('synthesis', 0),
            'model': MODEL}))

    def _make_stream_state():
        """Create a fresh state dict for stream event processing."""
        return {
            'current_block': None,
            'phase_buffer': '',
            'detected_phases': set(),
            'current_tool_name': None,
            'current_tool_input_json': '',
            'tool_results': [],
        }

    def generate():
        try:
            client = anthropic.Anthropic(
                timeout=httpx.Timeout(180.0, connect=10.0)  # 3 min per call
            )
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
            print(f'[stream] Error: {e}')
            yield sse('error', 'An internal error occurred. Please try again.')
        finally:
            # Keep document for follow-up questions
            if doc_id in documents:
                documents[doc_id]['analyzed'] = True

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


def build_followup_prompt():
    """Short system prompt for follow-up questions about an analyzed document."""
    return """You are a senior attorney who has just finished analyzing a document. The user has a follow-up question about it.

## LANGUAGE RULE
ALWAYS respond in ENGLISH regardless of the document's language. When quoting text from the document, keep quotes in the original language and add an English translation in parentheses.

## RULES
- Answer the specific question asked — do not repeat the full analysis
- Reference specific clauses, sections, or language from the document when relevant
- If the question asks about something not in the document, say so clearly
- Be direct, concrete, and practical — write for a non-lawyer audience
- If the question involves legal risk, reference the relevant trick category and risk level
- Keep your answer focused — typically 2-5 paragraphs unless the question demands more"""


@app.route('/ask/<doc_id>', methods=['POST'])
def ask(doc_id):
    if doc_id not in documents:
        return jsonify({'error': 'Document not found. Please re-upload.'}), 404

    doc = documents[doc_id]
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()

    if not question:
        return jsonify({'error': 'No question provided.'}), 400

    def sse(event_type, content=''):
        payload = json.dumps({'type': event_type, 'content': content})
        return f"data: {payload}\n\n"

    def generate():
        try:
            client = anthropic.Anthropic()
            user_msg = (
                "Here is the document:\n\n"
                "---BEGIN DOCUMENT---\n\n"
                f"{doc['text']}\n\n"
                "---END DOCUMENT---\n\n"
                f"Question: {question}"
            )
            yield sse('phase', 'thinking')
            stream = client.messages.create(
                model=MODEL,
                max_tokens=16000,
                thinking={'type': 'adaptive'},
                system=[{
                    'type': 'text',
                    'text': build_followup_prompt(),
                    'cache_control': {'type': 'ephemeral'},
                }],
                messages=[{'role': 'user', 'content': user_msg}],
                stream=True,
            )
            try:
                for event in stream:
                    if event.type == 'content_block_delta':
                        if event.delta.type == 'thinking_delta':
                            yield sse('thinking', event.delta.thinking)
                        elif event.delta.type == 'text_delta':
                            yield sse('text', event.delta.text)
                    elif event.type == 'message_stop':
                        yield sse('done')
            finally:
                stream.close()
        except anthropic.APIError as e:
            yield sse('error', f'API error: {e.message}')
        except Exception as e:
            print(f'[stream] Error: {e}')
            yield sse('error', 'An internal error occurred. Please try again.')

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


def build_counter_draft_prompt():
    """System prompt for generating fair rewrites of problematic clauses."""
    return """You are a senior attorney hired by the READER to redraft unfair contract clauses. You have analyzed the document and identified problematic terms. Now generate fair, balanced alternatives.

## LANGUAGE RULE
ALWAYS respond in ENGLISH. When showing the original clause text, keep it in the document's language with an English translation. Redrafted clauses should be in English.

## OUTPUT FORMAT

## Counter-Draft: What a Fair Version Would Say

For each YELLOW or RED clause in the document (skip GREEN clauses), output:

### [Section Name/Title]

**Original:**
> [Quote the problematic clause verbatim — copy-paste from document]

**Fair rewrite:**
> [Your redrafted version. Must be legally sound, balanced, and protect both parties. Keep similar structure and length so it could realistically be swapped in. Use plain language.]

**What changed and why:** [1-2 sentences explaining each change. Example: "Added a fee cap of $150 — the original had no ceiling. Changed 'sole discretion' to 'mutual agreement' — the original gave only the landlord power to decide."]

---

## How to Use This Counter-Draft

[3-4 bullet points of practical negotiation advice specific to THIS document type:
- When to present these changes (before signing, at renewal, etc.)
- Which changes to prioritize (the ones most likely to be accepted)
- What to do if they refuse (what's the minimum acceptable compromise)
- Whether professional legal review is recommended for this document type]

## RULES
- Only redraft clauses that are genuinely unfair (YELLOW/RED) — do not touch fair clauses
- The rewrite must be realistic — something a reasonable counterparty might actually accept
- Preserve the drafter's legitimate interests while removing exploitation
- Keep rewrites approximately the same length as originals — don't bloat them
- Use plain language but maintain legal precision
- Order clauses by severity: most problematic first
- COMPLETION IS MANDATORY — do not truncate. Cover all YELLOW/RED clauses"""


def build_timeline_prompt():
    """System prompt for worst-case timeline simulation."""
    return """You are a senior attorney. Given a document, narrate a realistic worst-case scenario using the document's ACTUAL terms, figures, and deadlines.

## LANGUAGE RULE
ALWAYS respond in ENGLISH regardless of the document's language. When quoting specific terms from the document, keep them in the original language with English translations in parentheses.

## OUTPUT FORMAT

## Worst-Case Timeline

Pick the trigger that a reasonable person would MOST LIKELY experience (missed payment, illness, schedule conflict, minor damage, late notice, etc.) — not a contrived edge case.

**Month 1 — [Trigger Event]:** [What happens. Reference actual clause figures and section names.]
**Month 2 — [Escalation]:** [How other clauses activate. Show the math.]
**Month 3 — [Compound Effect]:** [The situation the reader is now locked into.]
[Continue 3-6 months — stop when the scenario reaches its conclusion.]

**Total exposure after [N] months: [dollar figure or concrete consequence]**

## What Could Have Prevented This

[2-3 bullet points: specific actions the reader could have taken BEFORE signing to avoid this scenario. Be concrete.]

## RULES
- Use the document's OWN numbers — do not invent figures
- Pick the MOST LIKELY trigger, not the most dramatic
- Show how clauses compound — reference specific sections
- Keep it concrete and narrative — this is a story, not a legal brief
- Realism is what makes it hit"""


@app.route('/timeline/<doc_id>', methods=['GET', 'POST'])
def timeline(doc_id):
    """Generate worst-case timeline — on-demand after analysis."""
    doc = documents.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found. Please re-upload.'}), 404

    def sse(event_type, content=''):
        payload = json.dumps({'type': event_type, 'content': content})
        return f"data: {payload}\n\n"

    def generate():
        try:
            client = anthropic.Anthropic()
            user_msg = (
                "Here is the document:\n\n"
                "---BEGIN DOCUMENT---\n\n"
                f"{doc['text']}\n\n"
                "---END DOCUMENT---\n\n"
                "Generate a worst-case timeline showing how one common trigger cascades through this contract."
            )
            yield sse('phase', 'thinking')
            stream = client.messages.create(
                model=MODEL,
                max_tokens=16000,
                thinking={'type': 'adaptive'},
                system=[{
                    'type': 'text',
                    'text': build_timeline_prompt(),
                    'cache_control': {'type': 'ephemeral'},
                }],
                messages=[{'role': 'user', 'content': user_msg}],
                stream=True,
            )
            try:
                for event in stream:
                    if event.type == 'content_block_delta':
                        if event.delta.type == 'thinking_delta':
                            yield sse('thinking', event.delta.thinking)
                        elif event.delta.type == 'text_delta':
                            yield sse('text', event.delta.text)
                    elif event.type == 'message_stop':
                        yield sse('done')
            finally:
                stream.close()
        except anthropic.APIError as e:
            yield sse('error', f'API error: {e.message}')
        except Exception as e:
            print(f'[stream] Error: {e}')
            yield sse('error', 'An internal error occurred. Please try again.')

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


@app.route('/counter-draft/<doc_id>', methods=['GET', 'POST'])
def counter_draft(doc_id):
    """Generate fair rewrites of problematic clauses — on-demand after analysis."""
    doc = documents.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found. Please re-upload.'}), 404

    def sse(event_type, content=''):
        payload = json.dumps({'type': event_type, 'content': content})
        return f"data: {payload}\n\n"

    def generate():
        try:
            client = anthropic.Anthropic()
            user_msg = (
                "Here is the document:\n\n"
                "---BEGIN DOCUMENT---\n\n"
                f"{doc['text']}\n\n"
                "---END DOCUMENT---\n\n"
                "Generate a counter-draft with fair rewrites for all problematic clauses."
            )
            yield sse('phase', 'thinking')
            stream = client.messages.create(
                model=MODEL,
                max_tokens=32000,
                thinking={'type': 'adaptive'},
                system=[{
                    'type': 'text',
                    'text': build_counter_draft_prompt(),
                    'cache_control': {'type': 'ephemeral'},
                }],
                messages=[{'role': 'user', 'content': user_msg}],
                stream=True,
            )
            try:
                for event in stream:
                    if event.type == 'content_block_delta':
                        if event.delta.type == 'thinking_delta':
                            yield sse('thinking', event.delta.thinking)
                        elif event.delta.type == 'text_delta':
                            yield sse('text', event.delta.text)
                    elif event.type == 'message_stop':
                        yield sse('done')
            finally:
                stream.close()
        except anthropic.APIError as e:
            yield sse('error', f'API error: {e.message}')
        except Exception as e:
            print(f'[stream] Error: {e}')
            yield sse('error', 'An internal error occurred. Please try again.')

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


@app.route('/fetch-url', methods=['POST'])
def fetch_url():
    """Fetch a public URL and extract text content."""
    try:
        data = request.get_json(silent=True) or {}
        url = data.get('url', '').strip()
        depth = data.get('depth', 'standard')
        if not url:
            return jsonify({'error': 'No URL provided.'}), 400
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        import requests as req
        from bs4 import BeautifulSoup

        resp = req.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; FlipSide/1.0)'
        })
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()

        text = soup.get_text(separator='\n', strip=True)
        text = re.sub(r'\n{3,}', '\n\n', text)

        if len(text) < 50:
            return jsonify({'error': 'Could not extract meaningful text from this URL.'}), 400

        title_tag = soup.find('title')
        title = title_tag.string.strip() if title_tag and title_tag.string else url[:80]

        doc_id = str(uuid.uuid4())
        store_document(doc_id, {
            'text': text,
            'filename': title[:100],
            'depth': depth,
        })

        return jsonify({
            'doc_id': doc_id,
            'filename': title[:100],
            'text_length': len(text),
            'preview': text[:500],
            'full_text': text,
        })
    except Exception as e:
        print(f'[fetch-url] Error: {e}')
        return jsonify({'error': f'Could not fetch URL: {str(e)}'}), 400


if __name__ == '__main__':
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        print('\n' + '=' * 60)
        print('  WARNING: ANTHROPIC_API_KEY is not set.')
        print('  Set it in your environment or create a .env file.')
        print('=' * 60 + '\n')

    port = int(os.environ.get('FLIPSIDE_PORT', 5001))
    print('\n  FlipSide — The dark side of small print.')
    print(f'  Powered by Claude Opus 4.6 + Haiku 4.5 (fast cards).')
    print(f'  http://127.0.0.1:{port}\n')
    app.run(debug=True, port=port)
