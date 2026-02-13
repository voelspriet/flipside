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
import anthropic

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['TEMPLATES_AUTO_RELOAD'] = True

documents = {}

MODEL = os.environ.get('FLIPSIDE_MODEL', 'claude-opus-4-6')
FAST_MODEL = os.environ.get('FLIPSIDE_FAST_MODEL', 'claude-haiku-4-5-20251001')

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

DEEP_ANALYSIS_TOOLS = [
    {
        "name": "assess_risk",
        "description": "Record a structured risk assessment for a clause. Call once per clause analyzed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "clause_ref": {"type": "string", "description": "Section reference, e.g. '§1 Rent and Late Fees'"},
                "risk_level": {"type": "string", "enum": ["green", "yellow", "red"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 100},
                "score": {"type": "integer", "minimum": 0, "maximum": 100},
                "trick_type": {"type": "string", "description": "One of the 18 trick categories"},
                "mechanism": {"type": "string", "description": "How this clause creates risk — one sentence"},
            },
            "required": ["clause_ref", "risk_level", "confidence", "score", "trick_type", "mechanism"],
        },
    },
    {
        "name": "flag_interaction",
        "description": "Flag a cross-clause interaction creating compound risk invisible when reading individually.",
        "input_schema": {
            "type": "object",
            "properties": {
                "clauses": {"type": "array", "items": {"type": "string"}, "description": "Section references involved"},
                "interaction_type": {"type": "string", "description": "Name for this interaction pattern"},
                "severity": {"type": "string", "enum": ["moderate", "serious", "critical"]},
                "explanation": {"type": "string", "description": "How these clauses compound — 1-2 sentences"},
            },
            "required": ["clauses", "interaction_type", "severity", "explanation"],
        },
    },
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

}

# Default sample for backward compatibility
SAMPLE_DOCUMENT = SAMPLE_DOCUMENTS['lease']['text']

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
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
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
                except Exception:
                    pass
    # Tag each page so the sidebar can render page dividers
    # and later clauses from page 3+ are matchable
    tagged = []
    for i, part in enumerate(text_parts):
        tagged.append(f'\n\n— Page {i + 1} —\n\n{part}')
    raw_text = ''.join(tagged).strip()
    return clean_extracted_text(raw_text), page_images


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
        page_images = []

        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = file.filename
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

            if ext == 'pdf':
                text, page_images = extract_pdf(file)
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
            'page_images': page_images,
        }

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

        return jsonify({
            'doc_id': doc_id,
            'filename': filename,
            'text_length': len(text),
            'preview': text[:300],
            'full_text': text,
            'thumbnail': thumbnail,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
        'full_text': text,
        'thumbnail': SAMPLE_THUMBNAILS.get(sample_type),
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

## BILINGUAL RULE
If the document is NOT in English, add English translations for each clause:
**[EN] What the small print says:** [English translation]
**[EN] What you should read:** [English translation]
[EN-READER]: [English translation of the READER line]
Skip these for English documents.

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

[REASSURANCE]: [One short, warm, positive headline (max 8 words) that frames this clause as beneficial or fair — how the drafter WANTS you to feel. Genuinely reassuring, not sarcastic. Examples: "Your home is fully protected" / "Clear and simple payment terms"]

> "[Quote key language from the document]"

[READER]: [2-4 sentences. You ARE a trusting person who just skims and signs. Think out loud in FIRST PERSON ("I") and SHRUG EVERYTHING OFF. You see basic facts but they don't worry you at all. You NEVER do math, NEVER calculate totals, NEVER question fairness, NEVER express doubt, NEVER recognize legal concepts. FORBIDDEN words/patterns: "waiv" (any form), "surrender," "legal," "rights," "recourse," "argue," "dispute," "sole discretion," "no cap," "no limit," "unlimited," "adds up," "that's $X," "signing away," "give up," "lose my," "forfeit," question marks expressing concern. FORBIDDEN tone: worry, suspicion, hesitation, legal awareness, calculating worst cases, recognizing power imbalances. The reader has ZERO legal literacy — they don't know what a waiver IS. GOOD: "A $75 late fee? I'd just pay on time, so it won't matter." BAD: "$75 a day adds up fast — that's $2,250 a month." BAD: "I'm waiving my right to say the fee is unreasonable" — the reader would NEVER use the word "waiving." GOOD: "They handle maintenance, nice." BAD: "But who decides what counts as an emergency?" GOOD: "OK, fees get paid first — makes sense, clear up the small stuff." BAD: "You've surrendered your only legal argument" — this is an ANALYST, not a gullible reader. Always end with breezy certainty, never with analysis.]

[GREEN/YELLOW/RED] · Score: [0-100]/100 · Trick: [TRICK_CATEGORY]

**What the small print says:** [plain restatement of what this literally says — neutral, as a drafter would present it]

**What you should read:** [what this ACTUALLY means for you — direct, specific, concrete. Show the gap between the words and reality.]

**What does this mean for you:**
[FIGURE]: [The single key number. RED/YELLOW: worst-case stat — "$4,100 total debt from one missed payment". GREEN: the protection — "24-hour notice protects your deposit" / "Full 30-day refund window".]
[EXAMPLE]: [One concrete scenario using the document's own figures. 2-3 sentences max. For GREEN: explain what makes this clause fair and how it protects you specifically.]

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
- The [READER] is GULLIBLE: sees facts, shrugs them off, never does math or questions fairness. The flip reveals what they missed
- "What you should read" reveals the reader's reality — the gap between words and what they mean
- Quote exact language from the document
- Be thorough but fast — cross-clause interactions will be analyzed separately"""


def build_card_scan_prompt():
    """Haiku fast scan — FULL flip cards (front + back). Complete card data in one pass."""
    return """You are a contract analyst. Identify the MOST SIGNIFICANT clauses and produce COMPLETE flip cards — the reassuring front AND the expert back that reveals the truth. Speed matters — output each clause as soon as you identify it.

## CLAUSE LIMIT
Output a MAXIMUM of 12 individual RED/YELLOW cards. Pick the 10-12 clauses with the highest impact on the reader. Combine ALL remaining fair/benign clauses into a single GREEN summary card. Total output: 10-12 cards + 1 green summary = 11-13 cards maximum. If you find more than 12 concerning clauses, pick the worst 12 and note any omitted ones in the green summary.

## LANGUAGE RULE
Respond in the SAME LANGUAGE as the document. If the document is in Dutch, respond entirely in Dutch. If German, German. Match the document's language for ALL output including headers and labels.

## BILINGUAL RULE
If the document is NOT in English, add these extra fields per clause:
[EN-READER]: [English translation of the READER line]
[EN-FIGURE]: [English translation of the FIGURE line]
[EN-EXAMPLE]: [English translation of the EXAMPLE line]
**[EN] What the small print says:** [English translation]
**[EN] What you should read:** [English translation]
Only add these for non-English documents. For English documents, skip them.

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
14. GREEN clauses: Score 0-30, Trick: None. YELLOW/RED: name the specific risk with numbers and deadlines"""






def build_deep_analysis_prompt(has_images=False, trick_summary=''):
    """Deep cross-clause analysis with VILLAIN voice, per-section actions, and assessment."""
    visual_block = ""
    if has_images:
        visual_block = """

## VISUAL FORMATTING ANALYSIS

Page images are included alongside the document text. Examine them for visual tricks that extracted text cannot capture:
- **Fine print**: Text in noticeably smaller font — especially clauses with high financial impact
- **Buried placement**: Critical terms on late pages, at page bottom, or in footnotes
- **Table structures**: Tables that obscure comparisons or hide fees in dense grids
- **Visual hierarchy manipulation**: Important limitations in light gray, disclaimers in condensed type

If you detect visual formatting tricks, include them as cross-clause interactions with the best-fitting trick category. Reference the page number."""

    return f"""You are a senior attorney who has read this entire document. Perform the DEEP analysis: cross-clause interactions and overall risk assessment. This requires reasoning across ALL clauses simultaneously — finding what is invisible when reading clause by clause.
{visual_block}
## LANGUAGE RULE
Respond in the SAME LANGUAGE as the document.

## BILINGUAL RULE
If the document is NOT in English, add an English summary at the very end of your output:

## English Summary

### Cross-Clause Interactions (EN)
[For each interaction: 2-3 sentence English summary of the compound risk and recommended action]

### Overall Assessment (EN)
**Overall Risk Score: [same score]/100** — [English severity label]
**Top Concerns:**
1. [English one-liner]
2. [English one-liner]
3. [English one-liner]

**Key Actions:**
- [English action item]
- [English action item]
- [English action item]

Only add this section for non-English documents. For English documents, skip it entirely.

## OUTPUT FORMAT

## Cross-Clause Interactions

Identify clause COMBINATIONS that create compound risks invisible when reading linearly.

For each interaction:

### [Descriptive Interaction Title]

**Read separately, you'd see:** What these clauses appear to say independently. One sentence.

**Read together, you'd realize:** What they ACTUALLY do when combined — the hidden compound risk. One sentence, visceral.

**Clauses involved:** [list specific sections WITH context — e.g., "Late Fees (§1), Payment Waterfall (§1), Rent Withholding Prohibition (§2)". Anchor each to its topic so the reader knows which part of the document you mean. List them here ONCE and keep them OUT of the prose below.]

**How they interact:** [2-3 sentences. The mechanism — be specific about HOW the clauses feed into each other. Write in plain English. Do NOT embed §-references in the flowing text — the clause list above handles that.]

[RED/YELLOW] · Trick: [TRICK_CATEGORY]

**If the drafter could speak as a villain:** [MAX 2-3 sentences. Keep ONLY the sharpest line that reveals the mechanism. A good villain reveals, doesn't lecture. Example: "The math does the work. Once they're two days late, the waterfall makes it impossible to get current — and we've already waived their right to challenge it."]

→ YOUR MOVE: [One concrete action the reader should take about THIS specific interaction. One sentence. Example: "Demand a flat late fee cap (e.g., 5% of monthly rent) and require payments apply to rent principal first."]

---

Find at least 3 cross-clause interactions. These are your most valuable findings.

## Who Drafted This

{f'''Trick pattern data from initial scan: {trick_summary}
Use this data to profile the drafter's strategy. Which tricks appear most? What does the combination reveal about intent? A drafter who uses Auto-Lock 4× is different from one who uses Sole Discretion 4× — explain the difference in behavioral terms.

''' if trick_summary else ''}[2-3 sentences profiling what TYPE of drafter produces this document structure and what it signals about how they will behave. Example: "This lease pattern is typical of high-volume property management companies optimizing for automated enforcement and minimal tenant interaction. Expect slow repair responses, aggressive deposit deductions, and form-letter communication. The structure is designed for a landlord who wants to manage by policy, not relationship."]

## Document Archaeology

For each major section, one word: **Boilerplate** or **Custom**. Then 1-2 sentences naming which clauses got custom attention and what that reveals about the drafter's priorities.

## Power Asymmetry

**Your rights:** [count] · **Your obligations:** [count] · **Their rights:** [count] · **Their obligations:** [count] · **"Sole discretion" (them):** [count]×

**Power Ratio: [Their rights]:[Your rights]** — [one sentence]

## Fair Standard Comparison

Compare the WORST clauses in this document against what a fair, balanced version of the same document type would contain. Use your knowledge of standard industry practices and legal norms.

For each comparison (2-3 max):

### [Clause/Area]
**This document says:** [what the clause actually states — one sentence]
**A fair version would say:** [what a balanced, industry-standard clause would look like — one sentence]
**The gap:** [why the difference matters to the reader — one sentence]

This section answers: "Is this document UNUSUALLY aggressive, or is this just how these documents work?" Ground your comparison in real-world norms for this document type.

## Overall Assessment

**Overall Risk Score: [0-100]/100** — [CONTEXT-AWARE severity label — see tiers below]

**Power Imbalance Index: [0-100]/100** — How little you can do about it.


SEVERITY TIERS — choose the label that fits the ACTUAL stakes, not just the number:
- 0-30: "Low risk — standard terms" (typical boilerplate, no red flags)
- 31-55: "Moderate risk — review flagged clauses" (some problematic terms, fixable)
- 56-75: "High risk — negotiate before signing" (significant imbalance, pushback needed)
- 76-90: "Serious risk — seek professional legal review" (document designed to exploit)
- 91-100: "Do not sign — [reason]" (unconscionable, illegal, or rights-destroying)

CRITICAL: If the document touches fundamental rights (constitutional protections, whistleblower rights, parliamentary immunity, medical consent, employment non-competes that restrict livelihood), ELEVATE the severity language regardless of score. A score of 74 on a lease = "negotiate." A score of 74 on an NDA that undermines constitutional protections = "seek legal counsel — constitutional concerns." Match the stakes, not just the math.

### Top 3 Concerns
1. **[Title]** — [one sentence]
2. **[Title]** — [one sentence]
3. **[Title]** — [one sentence]

### Recommended Actions
[Consolidated checklist — the user has already seen per-section actions above. Summarize the 3-5 most important moves. NEVER end mid-sentence — if you're running out of space, write fewer items rather than truncating.]
- [Specific, actionable item]
- [Specific, actionable item]
- [Specific, actionable item]

## How Opus 4.6 Analyzed This Document

[2-4 sentences. Describe which reasoning methods YOU actually used for THIS specific document. Be concrete and specific to what you found — not generic. Examples of methods to mention when applicable:
- **Perspective adoption**: "I read this as the drafter's attorney to reconstruct strategic intent behind [specific clause pattern]."
- **Cross-clause reasoning**: "I traced how [clause X] feeds into [clause Y] by holding the full document in context simultaneously."
- **Extended thinking**: "I used [N] reasoning steps to work through the [specific interaction] — this required sustained multi-step inference that shorter models would miss."
- **Pattern recognition against legal corpus**: "I recognized the [specific pattern] as a known tactic in [document type] contracts."
- **Multilingual analysis**: "I detected the document language as [X] and analyzed jurisdiction-specific implications."
Only mention methods you ACTUALLY used. This section is short — 2-4 sentences, not a list of every capability.]

## Quality Check

Re-read your own analysis above with fresh eyes. Check for these failure modes:

- **Possible False Positives**: Any findings where the language is actually standard for this document type but you flagged it as YELLOW or RED? If so, name them and explain. If none: "None identified — all flags appear warranted."
- **Possible Blind Spots**: Any risks you glossed over, treated as boilerplate, or failed to connect? Look for missing protections, undefined terms, and untraced cross-references. If none: "None identified — analysis appears thorough."
- **Consistency Check**: Did similar language get different scores? If so, flag it. If not: "Scoring appears consistent."

**Adjusted Confidence: [HIGH/MEDIUM/LOW]** — After self-review, how confident are you in the overall analysis?

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
- Focus exclusively on cross-clause interactions, drafter profile, and assessment
- Do NOT re-analyze individual clauses — that has been done separately
- Every cross-clause interaction MUST include a villain voice block — short and sharp, MAX 2-3 sentences
- The villain voice is deliberately adversarial and exaggerated — the user expects this framing
- Every cross-clause interaction MUST end with "→ YOUR MOVE:" — one concrete action
- LEAD each interaction with "Read separately / Read together" — that's the hook
- Keep §-references in "Clauses involved:" only — do NOT embed them in flowing prose
- The "Who Drafted This" section replaces the old Playbook — profile the drafter type, don't repeat findings
- Cross-clause interactions are your HIGHEST VALUE finding — reason deeply
- Use your full extended thinking budget to reason across the entire document
- Be thorough — connect clauses that the reader would never connect on their own
- COMPLETION IS MANDATORY: The Overall Assessment section (especially Recommended Actions) is the user's takeaway. NEVER truncate it. If you need to economize, shorten cross-clause descriptions — never cut the assessment
- Document Archaeology: be honest — if most clauses are boilerplate, say so. The custom clauses are the signal
- Power Asymmetry: count precisely from the document, don't estimate or round
- The severity label MUST match the real-world stakes of the document, not just the numerical score
- The Quality Check is your credibility section — be genuinely self-critical, brief (2-4 bullet points). Users trust analyses that acknowledge uncertainty more than false certainty

"""


def build_interactions_prompt(has_images=False):
    """Opus thread 1: Cross-clause compound risks. Villain voice + YOUR MOVE."""
    visual_block = ""
    if has_images:
        visual_block = """

## VISUAL FORMATTING ANALYSIS
Page images are included. Look for visual tricks: fine print, buried placement, dense tables, light-gray disclaimers. Include visual tricks as cross-clause interactions with trick categories. Reference page numbers."""

    return f"""You are a senior attorney. Find clause COMBINATIONS that create compound risks invisible when reading linearly. This is your ONLY job — cross-clause interactions.
{visual_block}
## LANGUAGE RULE
Respond in the SAME LANGUAGE as the document.

## BILINGUAL RULE
If the document is NOT in English, add at the end:

## English Summary
### Cross-Clause Interactions (EN)
[For each interaction: 2-3 sentence English summary of the compound risk and recommended action]

Only for non-English documents.

## OUTPUT FORMAT

## Cross-Clause Interactions

For each interaction:

### [Descriptive Interaction Title]

**Read separately, you'd see:** What these clauses appear to say independently. One sentence.

**Read together, you'd realize:** What they ACTUALLY do when combined — the hidden compound risk. One sentence, visceral.

**Clauses involved:** [list specific sections WITH context — e.g., "Late Fees (§1), Payment Waterfall (§1), Rent Withholding Prohibition (§2)". Anchor each to its topic. List them here ONCE and keep them OUT of the prose below.]

**How they interact:** [2-3 sentences. The mechanism — be specific about HOW the clauses feed into each other. Plain English. Do NOT embed §-references in flowing text.]

[RED/YELLOW] · Trick: [TRICK_CATEGORY]

**If the drafter could speak as a villain:** [MAX 2-3 sentences. Keep ONLY the sharpest line that reveals the mechanism. A good villain reveals, doesn't lecture.]

→ YOUR MOVE: [One concrete action the reader should take. One sentence.]

---

Find at least 3 cross-clause interactions. These are your most valuable findings.

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
- Every interaction MUST include a villain voice block — short and sharp, MAX 2-3 sentences
- The villain voice is deliberately adversarial and exaggerated — the user expects this framing
- Every interaction MUST end with "→ YOUR MOVE:" — one concrete action
- LEAD each with "Read separately / Read together" — that's the hook
- Keep §-references in "Clauses involved:" only — do NOT embed them in flowing prose
- Use your full extended thinking budget to reason across the entire document
- Be thorough — connect clauses that the reader would never connect on their own
"""


def build_asymmetry_prompt(has_images=False):
    """Opus thread 2: Power asymmetry + fair standard comparison."""
    visual_block = ""
    if has_images:
        visual_block = "\n\nPage images are included. Reference visual tricks (fine print, buried placement) in your analysis."

    return f"""You are a senior attorney. Measure the power imbalance in this document and compare its worst clauses against industry norms. This is your ONLY job.
{visual_block}
## LANGUAGE RULE
Respond in the SAME LANGUAGE as the document.

## BILINGUAL RULE
If the document is NOT in English, add at the end:

## English Summary
### Power Asymmetry (EN)
[Power ratio and one-sentence summary in English]
### Fair Standard (EN)
[For each comparison: one-sentence English summary of the gap]

Only for non-English documents.

## OUTPUT FORMAT

## Power Asymmetry

**Your rights:** [count] · **Your obligations:** [count] · **Their rights:** [count] · **Their obligations:** [count] · **"Sole discretion" (them):** [count]×

**Power Ratio: [Their rights]:[Your rights]** — [one sentence]

## Fair Standard Comparison

Compare the WORST clauses in this document against what a fair, balanced version of the same document type would contain. Use your knowledge of standard industry practices and legal norms.

For each comparison (2-3 max):

### [Clause/Area]
**This document says:** [what the clause actually states — one sentence]
**A fair version would say:** [what a balanced, industry-standard clause would look like — one sentence]
**The gap:** [why the difference matters to the reader — one sentence]

This section answers: "Is this document UNUSUALLY aggressive, or is this just how these documents work?" Ground your comparison in real-world norms for this document type.

## RULES
- Power Asymmetry: count precisely from the document, don't estimate or round
- Fair Standard: be specific about industry norms — cite what's standard
- Use your full extended thinking budget
"""


def build_archaeology_prompt(has_images=False):
    """Opus thread 3: Document archaeology (boilerplate vs custom) + drafter profile."""
    visual_block = ""
    if has_images:
        visual_block = "\n\nPage images are included. Look for visual formatting differences between boilerplate and custom sections."

    return f"""You are a senior attorney. Analyze this document's construction: which parts are boilerplate vs custom-drafted, and profile the type of entity that created it. This is your ONLY job.
{visual_block}
## LANGUAGE RULE
Respond in the SAME LANGUAGE as the document.

## BILINGUAL RULE
If the document is NOT in English, add at the end:

## English Summary
### Document Archaeology (EN)
[Summary of boilerplate vs custom findings in English]
### Drafter Profile (EN)
[2-3 sentence English summary of drafter type and behavior signals]

Only for non-English documents.

## OUTPUT FORMAT

## Document Archaeology

For each major section, one word: **Boilerplate** or **Custom**. Then 1-2 sentences naming which clauses got custom attention and what that reveals about the drafter's priorities.

## Who Drafted This

[2-3 sentences profiling what TYPE of drafter produces this document structure and what it signals about how they will behave. Example: "This lease pattern is typical of high-volume property management companies optimizing for automated enforcement and minimal tenant interaction. Expect slow repair responses, aggressive deposit deductions, and form-letter communication. The structure is designed for a landlord who wants to manage by policy, not relationship."]

## RULES
- Document Archaeology: be honest — if most clauses are boilerplate, say so. The custom clauses are the signal
- The drafter profile should predict BEHAVIOR, not just describe structure
- Use your full extended thinking budget
"""


def build_overall_prompt(has_images=False):
    """Opus thread 4: Overall assessment, methodology, quality check."""
    visual_block = ""
    if has_images:
        visual_block = "\n\nPage images are included. Reference any visual tricks you detect in your assessment."

    return f"""You are a senior attorney. Provide the OVERALL VERDICT: risk score, top concerns, recommended actions, methodology disclosure, and quality self-check. This is your ONLY job — a companion analysis covers cross-clause interactions separately.
{visual_block}
## LANGUAGE RULE
Respond in the SAME LANGUAGE as the document.

## BILINGUAL RULE
If the document is NOT in English, add at the end:

## English Summary
### Overall Assessment (EN)
**Overall Risk Score: [same score]/100** — [English severity label]
**Top Concerns:**
1. [English one-liner]
2. [English one-liner]
3. [English one-liner]
**Key Actions:**
- [English action item]
- [English action item]
- [English action item]

Only for non-English documents.

## OUTPUT FORMAT

## Overall Assessment

**Overall Risk Score: [0-100]/100** — [CONTEXT-AWARE severity label — see tiers below]

**Power Imbalance Index: [0-100]/100** — How little you can do about it.

SEVERITY TIERS — choose the label that fits the ACTUAL stakes, not just the number:
- 0-30: "Low risk — standard terms" (typical boilerplate, no red flags)
- 31-55: "Moderate risk — review flagged clauses" (some problematic terms, fixable)
- 56-75: "High risk — negotiate before signing" (significant imbalance, pushback needed)
- 76-90: "Serious risk — seek professional legal review" (document designed to exploit)
- 91-100: "Do not sign — [reason]" (unconscionable, illegal, or rights-destroying)

CRITICAL: If the document touches fundamental rights (constitutional protections, whistleblower rights, parliamentary immunity, medical consent, employment non-competes that restrict livelihood), ELEVATE the severity language regardless of score.

### Top 3 Concerns
1. **[Title]** — [one sentence]
2. **[Title]** — [one sentence]
3. **[Title]** — [one sentence]

### Recommended Actions
[Consolidated checklist — summarize the 3-5 most important moves. NEVER truncate.]
- [Specific, actionable item]
- [Specific, actionable item]
- [Specific, actionable item]

## How Opus 4.6 Analyzed This Document

[2-4 sentences. Describe which reasoning methods YOU actually used for THIS specific document. Be concrete — not generic. Only mention methods you ACTUALLY used.]

## Quality Check

Re-read your own analysis above with fresh eyes:

- **Possible False Positives**: Any standard language incorrectly flagged? If none: "None identified — all flags appear warranted."
- **Possible Blind Spots**: Missing protections, undefined terms, untraced references? If none: "None identified — analysis appears thorough."
- **Consistency Check**: Similar language scored differently? If not: "Scoring appears consistent."

**Adjusted Confidence: [HIGH/MEDIUM/LOW]** — After self-review, how confident are you?

## RULES
- COMPLETION IS MANDATORY: Recommended Actions is the user's takeaway. NEVER truncate
- The severity label MUST match real-world stakes, not just the number
- Quality Check: be genuinely self-critical. Users trust uncertainty over false certainty
- Use your full extended thinking budget
"""


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
            'full_text': texts[0],
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
        """Five parallel API calls: Haiku full cards + 4× Opus expert report."""
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

        # Haiku for fast card scan (no extended thinking)
        quick_max = max(16000, min(32000, len(doc['text']) // 2))
        t_quick = threading.Thread(
            target=worker,
            args=('quick', build_card_scan_prompt(), quick_max,
                  FAST_MODEL, False),
            daemon=True,
        )

        # Deep analysis token budget: each Opus call gets 40K (total 80K split)
        # Floor of 80000 for sequential mode, 40000 each for parallel
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

        # ── 5-thread: ALL start at t=0 ──
        # Haiku (full cards) + 4× Opus (interactions, asymmetry, archaeology, overall)
        parallel_max = max(deep_max_tokens // 4, 20000)

        opus_threads = {
            'interactions': build_interactions_prompt(has_images=has_images),
            'asymmetry': build_asymmetry_prompt(has_images=has_images),
            'archaeology': build_archaeology_prompt(has_images=has_images),
            'overall': build_overall_prompt(has_images=has_images),
        }

        for label, prompt in opus_threads.items():
            t = threading.Thread(
                target=worker,
                args=(label, prompt, parallel_max, MODEL, True),
                kwargs={'user_content': deep_user_content},
                daemon=True,
            )
            t.start()

        t_quick.start()

        yield from _run_parallel_5thread(q, timings, cancel)

    def _run_parallel_5thread(q, timings, cancel):
        """5-thread event loop: ALL start at t=0.
        Haiku (full flip cards) + 4× Opus (interactions, asymmetry, archaeology, overall).
        Each Opus source dispatches independently — no buffers, no gating."""

        OPUS_SOURCES = {'interactions', 'asymmetry', 'archaeology', 'overall'}

        start_time = time.time()
        state_quick = _make_stream_state()
        quick_text = ''
        quick_done = False
        done_flags = {s: False for s in OPUS_SOURCES}

        def all_done():
            return quick_done and all(done_flags.values())

        while not all_done():
            try:
                source, event = q.get(timeout=1.0)
            except queue_module.Empty:
                if time.time() - start_time > 300:
                    cancel.set()
                    yield sse('error', 'Analysis timed out after 5 minutes')
                    yield sse('done', json.dumps({
                        'quick_seconds': timings.get('quick', 0),
                        'deep_seconds': max((timings.get(s, 0) for s in OPUS_SOURCES), default=0),
                        'model': MODEL}))
                    return
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
                        yield sse(f'{source}_text', delta.text)
                    elif hasattr(delta, 'type') and delta.type == 'thinking_delta':
                        yield sse(f'{source}_thinking', delta.thinking)

        # ── Final done event ──
        yield sse('done', json.dumps({
            'quick_seconds': timings.get('quick', 0),
            'deep_seconds': max((timings.get(s, 0) for s in OPUS_SOURCES), default=0),
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
Respond in the SAME LANGUAGE as the document.

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
            yield sse('error', str(e))

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
Respond in the SAME LANGUAGE as the document. If the document is not in English, add an [EN] translation after each redrafted clause.

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
Respond in the SAME LANGUAGE as the document. If the document is not in English, add an English summary at the end.

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
        # Fallback: accept document text in POST body
        data = request.get_json(silent=True) or {}
        if data.get('text'):
            doc = {'text': data['text']}
        else:
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
            yield sse('error', str(e))

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
        data = request.get_json(silent=True) or {}
        if data.get('text'):
            doc = {'text': data['text']}
        else:
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
            yield sse('error', str(e))

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
    print('\n  FlipSide — The dark side of small print.')
    print(f'  Powered by Claude Opus 4.6 + Haiku 4.5 (fast cards).')
    print(f'  http://127.0.0.1:{port}\n')
    app.run(debug=True, port=port)
