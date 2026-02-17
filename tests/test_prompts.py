"""Unit tests for prompt builder functions in prompts/ package."""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts import (
    build_card_scan_prompt,
    build_clause_id_prompt,
    build_single_card_system,
    build_green_summary_user,
    build_archaeology_prompt,
    build_scenario_prompt,
    build_walkaway_prompt,
    build_combinations_prompt,
    build_playbook_prompt,
    build_verdict_prompt,
    build_followup_prompt,
    build_counter_draft_prompt,
    build_timeline_prompt,
)


class TestCardPrompts:
    """Tests for card generation prompt builders."""

    def test_card_scan_prompt_has_trick_categories(self):
        result = build_card_scan_prompt()
        assert 'Silent Waiver' in result
        assert 'Penalty Disguise' in result
        assert 'Ghost Standard' in result

    def test_card_scan_prompt_has_language_rule(self):
        result = build_card_scan_prompt()
        assert 'LANGUAGE RULE' in result
        assert 'ENGLISH' in result

    def test_card_scan_prompt_has_all_card_fields(self):
        result = build_card_scan_prompt()
        for field in ['[REASSURANCE]', '[READER]', '[TEASER]', '[REVEAL]', '[FIGURE]', '[EXAMPLE]']:
            assert field in result, f'Missing field: {field}'

    def test_clause_id_prompt_is_minimal(self):
        result = build_clause_id_prompt()
        assert 'CLAUSE:' in result
        assert 'GREEN_CLAUSES:' in result
        assert '## Document Profile' in result

    def test_single_card_system_includes_document(self):
        doc = 'This is a test contract with terms and conditions.'
        result = build_single_card_system(doc)
        assert doc in result
        assert '---BEGIN DOCUMENT---' in result
        assert '---END DOCUMENT---' in result

    def test_single_card_system_has_trick_categories(self):
        result = build_single_card_system('test')
        assert 'Silent Waiver' in result
        assert 'TRICK CATEGORIES' in result

    def test_green_summary_includes_clauses(self):
        green_text = '§2: Standard maintenance; §5: Normal utilities'
        result = build_green_summary_user(green_text)
        assert green_text in result
        assert 'Fair Clauses Summary' in result
        assert '[GREEN]' in result


class TestDeepDivePrompts:
    """Tests for deep dive prompt builders."""

    def test_archaeology_prompt_has_finding_tags(self):
        result = build_archaeology_prompt()
        assert '[FINDING' in result
        assert '[DEEP_CONTENT]' in result
        assert '[SUMMARY_CONTRIBUTION]' in result

    def test_archaeology_prompt_with_images(self):
        result = build_archaeology_prompt(has_images=True)
        assert 'Page images' in result

    def test_archaeology_prompt_without_images(self):
        result = build_archaeology_prompt(has_images=False)
        assert 'Page images' not in result

    def test_scenario_prompt_has_timeline_tags(self):
        result = build_scenario_prompt()
        assert '[TIMELINE_STEP' in result
        assert '[SCENARIO_TOTAL]' in result
        assert '[SCENARIO_ACTIONS]' in result
        assert '[SCENARIO_MESSAGE]' in result

    def test_walkaway_prompt_has_breakdown_tags(self):
        result = build_walkaway_prompt()
        assert '[WALKAWAY_NUMBER]' in result
        assert '[WALKAWAY_BREAKDOWN]' in result
        assert '[WALKAWAY_COMPARISON]' in result

    def test_combinations_prompt_has_structure(self):
        result = build_combinations_prompt()
        assert 'Clause A' in result
        assert 'Clause B' in result
        assert 'Read separately' in result
        assert 'Read together' in result

    def test_playbook_prompt_has_strategy_sections(self):
        result = build_playbook_prompt()
        assert 'Push Hard' in result
        assert 'Mention These' in result
        assert "Don't Waste Capital" in result or 'Waste Capital' in result
        assert 'Opening Move' in result
        assert 'Ready-to-Send' in result


class TestVerdictPrompt:
    """Tests for the verdict prompt builder."""

    def test_verdict_prompt_has_all_tags(self):
        result = build_verdict_prompt()
        required_tags = [
            '[VERDICT_TIER]', '[WHAT_IS_THIS]', '[SHOULD_YOU_WORRY]',
            '[THE_MAIN_THING]', '[ONE_ACTION]', '[POWER_RATIO]',
            '[JURISDICTION]', '[RISKS]', '[CHECKLIST]',
            '[FLAGGED_CLAIMS]', '[COLOPHON]',
        ]
        for tag in required_tags:
            assert tag in result, f'Missing tag: {tag}'

    def test_verdict_prompt_tier_options(self):
        result = build_verdict_prompt()
        for tier in ['SIGN WITH CONFIDENCE', 'READ THE FLAGGED CLAUSES',
                     'NEGOTIATE BEFORE SIGNING', 'SEEK LEGAL REVIEW', 'DO NOT SIGN']:
            assert tier in result

    def test_verdict_prompt_with_images(self):
        result = build_verdict_prompt(has_images=True)
        assert 'Page images' in result

    def test_verdict_prompt_without_images(self):
        result = build_verdict_prompt(has_images=False)
        assert 'Page images' not in result


class TestFollowupPrompts:
    """Tests for follow-up prompt builders."""

    def test_followup_prompt_has_tools(self):
        result = build_followup_prompt()
        assert 'search_document' in result
        assert 'get_clause_analysis' in result
        assert 'get_verdict_summary' in result

    def test_counter_draft_prompt_has_format(self):
        result = build_counter_draft_prompt()
        assert '**Original:**' in result
        assert '**Fair rewrite:**' in result
        assert 'What changed and why' in result

    def test_timeline_prompt_has_format(self):
        result = build_timeline_prompt()
        assert 'Month 1' in result
        assert 'Total exposure' in result
        assert 'Prevented' in result


class TestAllPromptsCommon:
    """Cross-cutting tests for all prompt builders."""

    ALL_PROMPTS = [
        ('card_scan', build_card_scan_prompt, {}),
        ('clause_id', build_clause_id_prompt, {}),
        ('single_card', build_single_card_system, {'doc_text': 'test'}),
        ('green_summary', build_green_summary_user, {'green_clauses_text': 'test'}),
        ('archaeology', build_archaeology_prompt, {}),
        ('scenario', build_scenario_prompt, {}),
        ('walkaway', build_walkaway_prompt, {}),
        ('combinations', build_combinations_prompt, {}),
        ('playbook', build_playbook_prompt, {}),
        ('verdict', build_verdict_prompt, {}),
        ('followup', build_followup_prompt, {}),
        ('counter_draft', build_counter_draft_prompt, {}),
        ('timeline', build_timeline_prompt, {}),
    ]

    @pytest.mark.parametrize("name,func,kwargs", ALL_PROMPTS)
    def test_returns_nonempty_string(self, name, func, kwargs):
        result = func(**kwargs)
        assert isinstance(result, str)
        assert len(result) > 100, f'{name} returned suspiciously short prompt'

    # green_summary is a user message paired with a system prompt that has the rule
    SYSTEM_PROMPTS = [p for p in ALL_PROMPTS if p[0] != 'green_summary']

    @pytest.mark.parametrize("name,func,kwargs", SYSTEM_PROMPTS)
    def test_has_language_rule(self, name, func, kwargs):
        """All system prompts should include the English-only language rule."""
        result = func(**kwargs)
        assert 'ENGLISH' in result or 'English' in result, f'{name} missing language rule'
