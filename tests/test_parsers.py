"""Unit tests for pure parsing functions in app.py."""

import sys
import os
import pytest

# Add project root to path so we can import app functions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions under test — these are pure parsers, no Flask needed
from app import _parse_clause_line, _has_garbled_text, parse_identification_output, _build_claims_summary


# ── _parse_clause_line ────────────────────────────────────────────

class TestParseClauseLine:
    """Tests for _parse_clause_line: CLAUSE: line parser."""

    def test_basic_title_and_section(self):
        result = _parse_clause_line('CLAUSE: Late Fees (Section 1)')
        assert result['title'] == 'Late Fees'
        assert result['section'] == 'Section 1'
        assert result['risk'] == 'RED'  # default when no RISK field
        assert result['trick'] == ''

    def test_title_without_section(self):
        result = _parse_clause_line('CLAUSE: Unlimited Liability')
        assert result['title'] == 'Unlimited Liability'
        assert result['section'] == ''

    def test_pipe_format_with_risk_and_trick(self):
        result = _parse_clause_line('CLAUSE: Late Fees (§1) | RISK: YELLOW | TRICK: Penalty Disguise')
        assert result['title'] == 'Late Fees'
        assert result['section'] == '§1'
        assert result['risk'] == 'YELLOW'
        assert result['trick'] == 'Penalty Disguise'

    def test_descriptive_section_reference(self):
        result = _parse_clause_line('CLAUSE: Uncapped Daily Penalties (Rent and Late Fees, §1)')
        assert result['title'] == 'Uncapped Daily Penalties'
        assert result['section'] == 'Rent and Late Fees, §1'

    def test_legacy_pipe_format(self):
        result = _parse_clause_line('CLAUSE: Late Fees (§1) | RISK: RED | SCORE: 85 | TRICK: Penalty Disguise')
        assert result['title'] == 'Late Fees'
        assert result['section'] == '§1'

    def test_empty_title_returns_none(self):
        result = _parse_clause_line('CLAUSE: ')
        assert result is None

    def test_only_section_no_title_returns_none(self):
        result = _parse_clause_line('CLAUSE: (Section 3)')
        assert result is None

    def test_whitespace_handling(self):
        result = _parse_clause_line('CLAUSE:   Binding Arbitration   (§7)  ')
        assert result['title'] == 'Binding Arbitration'
        assert result['section'] == '§7'

    def test_nested_parentheses(self):
        """Only the last parenthesized group should be the section."""
        result = _parse_clause_line('CLAUSE: IP Assignment (all work product) (§4)')
        assert result['section'] == '§4'

    def test_special_characters_in_title(self):
        result = _parse_clause_line('CLAUSE: Non-Compete & Non-Solicitation (§5)')
        assert result['title'] == 'Non-Compete & Non-Solicitation'
        assert result['section'] == '§5'


# ── _has_garbled_text ─────────────────────────────────────────────

class TestHasGarbledText:
    """Tests for _has_garbled_text: detects reversed/garbled PDF text."""

    def test_clean_english_text(self):
        text = "This is a normal sentence with common English words.\nAnother line of text."
        assert _has_garbled_text(text) is False

    def test_clean_dutch_text(self):
        text = "De huurder is verplicht het gehuurde in goede staat te houden."
        assert _has_garbled_text(text) is False

    def test_reversed_english_text(self):
        # "the quick brown fox" reversed character-by-character
        text = ".sdrow hsilgnE nommoc htiw ecnetnes lamron a si sihT"
        assert _has_garbled_text(text) is True

    def test_short_lines_ignored(self):
        """Lines with fewer than 4 words should be skipped."""
        text = "ABC DEF\nGHI"
        assert _has_garbled_text(text) is False

    def test_empty_text(self):
        assert _has_garbled_text('') is False

    def test_mixed_clean_and_garbled(self):
        """Even one garbled line should return True."""
        text = "This is a normal sentence.\n.sdrow hsilgnE nommoc htiw ecnetnes lamron a si sihT"
        assert _has_garbled_text(text) is True


# ── parse_identification_output ───────────────────────────────────

class TestParseIdentificationOutput:
    """Tests for parse_identification_output: Phase 1 scan parser."""

    SAMPLE_OUTPUT = """CLAUSE: Uncapped Late Fees (Rent and Late Fees, §1)
CLAUSE: Mandatory Arbitration (Dispute Resolution, §8)
CLAUSE: Landlord Entry Rights (Entry and Inspection, §3)
GREEN_CLAUSES: §2: Standard maintenance terms; §5: Normal utility provisions
## Document Profile
- **Document Type**: Residential Lease
- **Drafted By**: QuickRent Property Management
- **Your Role**: Tenant
- **Jurisdiction**: Portland, Oregon
- **Language**: English
- **Sections**: 4"""

    def test_extracts_clauses(self):
        profile, clauses, green = parse_identification_output(self.SAMPLE_OUTPUT)
        assert len(clauses) == 3
        assert clauses[0]['title'] == 'Uncapped Late Fees'
        assert clauses[0]['section'] == 'Rent and Late Fees, §1'

    def test_extracts_green_text(self):
        _, _, green = parse_identification_output(self.SAMPLE_OUTPUT)
        assert '§2: Standard maintenance terms' in green
        assert '§5: Normal utility provisions' in green

    def test_extracts_profile(self):
        profile, _, _ = parse_identification_output(self.SAMPLE_OUTPUT)
        assert '## Document Profile' in profile
        assert 'Residential Lease' in profile
        assert 'QuickRent' in profile

    def test_not_applicable_document(self):
        text = """## Document Profile
- **Document Type**: Recipe
- **Drafted By**: Chef
- **Your Role**: Reader
- **Jurisdiction**: Not specified
- **Language**: English
- **Sections**: 3
**Not Applicable**: This is a cooking recipe, not a legal document."""
        profile, clauses, green = parse_identification_output(text)
        assert len(clauses) == 0
        assert green == ''
        assert '**Not Applicable**' in profile

    def test_empty_input(self):
        profile, clauses, green = parse_identification_output('')
        assert profile == ''
        assert clauses == []
        assert green == ''

    def test_profile_header_added_when_missing(self):
        """If profile text exists but has no ## header, it should be added."""
        text = """CLAUSE: Test Clause (§1)
- **Document Type**: Contract
- **Drafted By**: Company"""
        profile, clauses, _ = parse_identification_output(text)
        assert len(clauses) == 1
        assert '## Document Profile' in profile

    def test_clauses_first_format(self):
        """Optimized format: CLAUSE lines appear before the profile."""
        text = """CLAUSE: Fee Escalation (Payment Terms, §3)
CLAUSE: Auto-Renewal (Subscription, §6)
GREEN_CLAUSES: §1: Standard definitions; §4: Normal delivery terms
## Document Profile
- **Document Type**: SaaS Agreement
- **Drafted By**: CloudVault Inc.
- **Your Role**: Customer
- **Jurisdiction**: San Francisco, California
- **Language**: English
- **Sections**: 8"""
        profile, clauses, green = parse_identification_output(text)
        assert len(clauses) == 2
        assert clauses[0]['title'] == 'Fee Escalation'
        assert clauses[1]['title'] == 'Auto-Renewal'
        assert 'SaaS Agreement' in profile


# ── _build_claims_summary ─────────────────────────────────────────

class TestBuildClaimsSummary:
    """Tests for _build_claims_summary: card data → verdict summary."""

    def test_empty_prescan_returns_empty(self):
        assert _build_claims_summary(None, None) == ''
        assert _build_claims_summary({}, {}) == ''
        assert _build_claims_summary({'clauses': []}, {'cards': []}) == ''

    def test_basic_card_extraction(self):
        prescan = {'clauses': [{'risk': 'RED', 'score': '85', 'trick': 'Penalty Disguise'}]}
        cards = {'cards': [
            """### Uncapped Late Fees (Rent, §1)

[REASSURANCE]: Clear and simple payment terms

> "A late fee of $75 per day shall be assessed"

[READER]: Seems standard, whatever.

[TEASER]: The meter never stops.

[REVEAL]: Uncapped daily penalties from one missed deadline.

[RED] · Score: 85/100 · Trick: Penalty Disguise
Confidence: HIGH — Clear language

**Bottom line:** One late payment triggers unlimited daily fees with no ceiling.

**What the small print says:** Late fees of $75/day with no maximum.

**What you should read:** A single missed deadline can cost thousands.

**What does this mean for you:**
[FIGURE]: $2,250 in fees from one missed month
[EXAMPLE]: Miss rent by one day. $75/day × 30 days = $2,250 in fees on top of rent."""
        ]}

        result = _build_claims_summary(prescan, cards)
        assert '## PRE-ANALYZED FLAGGED CLAIMS' in result
        assert 'Uncapped Late Fees' in result
        assert 'RED' in result
        assert '85/100' in result
        assert 'Penalty Disguise' in result
        assert 'Uncapped daily penalties' in result  # REVEAL
        assert '$2,250' in result  # FIGURE
        assert 'unlimited daily fees' in result  # Bottom line

    def test_skips_green_summary_card(self):
        prescan = {'clauses': []}
        cards = {'cards': [
            "### Fair Clauses Summary\n[GREEN] · Score: 10/100 · Trick: None"
        ]}
        result = _build_claims_summary(prescan, cards)
        assert 'Fair Clauses Summary' not in result

    def test_multiple_cards(self):
        prescan = {'clauses': [
            {'risk': 'RED', 'score': '85', 'trick': 'Penalty Disguise'},
            {'risk': 'YELLOW', 'score': '60', 'trick': 'Sole Discretion'},
        ]}
        cards = {'cards': [
            "### Late Fees (§1)\n[RED] · Score: 85/100 · Trick: Penalty Disguise\n**Bottom line:** Bad fees.",
            "### Entry Rights (§3)\n[YELLOW] · Score: 60/100 · Trick: Sole Discretion\n**Bottom line:** They decide.",
        ]}
        result = _build_claims_summary(prescan, cards)
        assert 'Claim 1: Late Fees' in result
        assert 'Claim 2: Entry Rights' in result

    def test_fallback_to_prescan_when_no_risk_line(self):
        """If a card doesn't have the [RED] · Score line, use prescan data."""
        prescan = {'clauses': [{'risk': 'YELLOW', 'score': '55', 'trick': 'Time Trap'}]}
        cards = {'cards': ["### Deadline Issue (§4)\n**Bottom line:** Tight timeline."]}
        result = _build_claims_summary(prescan, cards)
        assert 'YELLOW' in result
        assert '55/100' in result
        assert 'Time Trap' in result
