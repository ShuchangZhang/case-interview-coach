#!/usr/bin/env python3
"""Behavioral regression tests for adaptive pre-session setup."""

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import setup_policy  # noqa: E402


def setup(kind, **overrides):
    mode, session_kind = {
        "full_interview": ("interview", "full_case"),
        "full_tutorial": ("tutorial", "full_case"),
        "tutorial_drill": ("tutorial", "focused_drill"),
        "beginner_curriculum": ("tutorial", "beginner_curriculum"),
    }[kind]
    context = {
        "mode": mode,
        "session_kind": session_kind,
        "case_type": None,
        "geography_relevant": False,
        "geography": None,
        "interview_format": None,
        "training_focus": None,
        "random_authorized": (),
    }
    context.update(overrides)
    return setup_policy.missing_setup(context)


class CaseTypeSetupTests(unittest.TestCase):

    def test_01_full_case_explicit_type_is_not_asked_again(self):
        fields = setup("full_interview", case_type="profitability",
                       interview_format="interviewee_led")
        self.assertNotIn("case_type", fields)

    def test_02_full_case_missing_type_must_ask(self):
        self.assertIn("case_type", setup("full_interview"))

    def test_03_explicit_random_authorises_case_selection(self):
        fields = setup("full_interview", random_authorized=("case_type",),
                       interview_format="interviewee_led")
        self.assertNotIn("case_type", fields)
        self.assertEqual(setup_policy.random_authorisations("Case 类型你决定"),
                         {"case_type"})

    def test_04_surprise_me_authorises_random_material_dimensions(self):
        for phrase in ("Surprise me", "随机来一道正式 mock"):
            with self.subTest(phrase=phrase):
                authorised = setup_policy.random_authorisations(phrase)
                self.assertEqual(authorised, set(setup_policy.RANDOM_FIELDS))

    def test_05_focused_drill_does_not_reask_case_type(self):
        fields = setup("tutorial_drill", training_focus="market sizing")
        self.assertNotIn("case_type", fields)
        self.assertNotIn("training_focus", fields)


class GeographySetupTests(unittest.TestCase):

    def test_06_explicit_geography_is_not_asked_again(self):
        fields = setup("full_interview", case_type="market entry",
                       geography_relevant=True, geography="China",
                       interview_format="interviewee_led")
        self.assertNotIn("geography", fields)

    def test_07_sensitive_case_without_geography_must_ask(self):
        fields = setup("full_interview", case_type="market entry",
                       geography_relevant=True,
                       interview_format="interviewee_led")
        self.assertIn("geography", fields)

    def test_08_geography_neutral_case_may_skip(self):
        fields = setup("full_interview", case_type="profitability",
                       geography_relevant=False,
                       interview_format="interviewee_led")
        self.assertNotIn("geography", fields)

    def test_09_targeted_random_market_authorises_selection(self):
        authorised = setup_policy.random_authorisations("市场也随机")
        self.assertEqual(authorised, {"geography"})
        fields = setup("tutorial_drill", training_focus="market sizing",
                       geography_relevant=True, random_authorized=authorised)
        self.assertNotIn("geography", fields)


class InterviewFormatSetupTests(unittest.TestCase):

    def test_10_interview_full_case_supports_both_formats(self):
        for value in setup_policy.FORMAT_VALUES:
            with self.subTest(value=value):
                fields = setup("full_interview", case_type="profitability",
                               interview_format=value)
                self.assertNotIn("interview_format", fields)

    def test_11_tutorial_full_case_supports_both_formats(self):
        for value in setup_policy.FORMAT_VALUES:
            with self.subTest(value=value):
                fields = setup("full_tutorial", case_type="profitability",
                               interview_format=value)
                self.assertNotIn("interview_format", fields)

    def test_12_tutorial_drill_never_requires_format(self):
        fields = setup("tutorial_drill", training_focus="exhibit interpretation")
        self.assertNotIn("interview_format", fields)

    def test_13_beginner_curriculum_defers_format(self):
        fields = setup("beginner_curriculum")
        self.assertNotIn("interview_format", fields)
        self.assertNotIn("case_type", fields)
        self.assertNotIn("geography", fields)


class AdaptiveSetupTests(unittest.TestCase):

    def test_14_complete_request_starts_without_setup_question(self):
        fields = setup("full_interview", case_type="profitability",
                       geography_relevant=True, geography="China",
                       interview_format="interviewee_led")
        self.assertEqual(fields, ())

    def test_15_multiple_missing_items_share_one_setup_turn(self):
        fields = setup("full_tutorial", geography_relevant=True,
                       assistance_needed=True)
        self.assertEqual(fields, ("case_type", "geography", "interview_format",
                                  "assistance_level"))
        question = setup_policy.setup_question(fields, "zh")
        self.assertEqual(question.count("开始前还需要确认"), 1)
        self.assertEqual(question.count("\n"), 4)

    def test_16_setup_is_not_capped_at_two_questions(self):
        fields = setup("full_interview", geography_relevant=True)
        self.assertEqual(fields, ("case_type", "geography", "interview_format"))

    def test_17_unspecified_is_not_random_authorisation(self):
        self.assertEqual(setup_policy.random_authorisations("开始一次正式 mock"), set())
        fields = setup("full_interview", geography_relevant=True)
        self.assertEqual(fields, ("case_type", "geography", "interview_format"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
