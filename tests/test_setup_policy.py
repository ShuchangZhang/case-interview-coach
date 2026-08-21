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
        "ambiguous_tutorial": ("tutorial", None),
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
        authorised = setup_policy.random_authorisations("Surprise me")
        self.assertEqual(authorised, set(setup_policy.RANDOM_FIELDS))
        self.assertEqual(setup_policy.random_authorisations("随机来一道正式 mock"),
                         {"case_type"})

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


class SessionKindIntentTests(unittest.TestCase):
    """Topic selection never silently changes the product shape."""

    def test_topic_only_phrases_do_not_trigger_focused_drill(self):
        for phrase in ("market sizing", "sizing", "math", "quant", "exhibit",
                       "structure", "synthesis", "profitability", "pricing"):
            with self.subTest(phrase=phrase):
                self.assertIsNone(setup_policy.infer_session_kind(phrase))

    def test_explicit_multi_rep_phrases_trigger_focused_drill(self):
        for phrase in ("连续练 5 道 sizing", "sizing 专项训练",
                       "来几道 sizing 小题", "five market sizing drills",
                       "exhibit reps", "只练计算"):
            with self.subTest(phrase=phrase):
                self.assertEqual(setup_policy.infer_session_kind(phrase),
                                 "focused_drill")

    def test_explicit_one_or_complete_case_phrases_trigger_full_case(self):
        for phrase in ("做一道 sizing case", "完整 sizing tutorial case",
                       "give me one market sizing case", "run a full pricing case"):
            with self.subTest(phrase=phrase):
                self.assertEqual(setup_policy.infer_session_kind(phrase), "full_case")

    def test_beginner_wording_triggers_beginner_curriculum(self):
        for phrase in ("我是完全新手，从头教", "teach me from scratch"):
            with self.subTest(phrase=phrase):
                self.assertEqual(setup_policy.infer_session_kind(phrase),
                                 "beginner_curriculum")

    def test_tutorial_plus_sizing_requires_session_kind_confirmation(self):
        fields = setup("ambiguous_tutorial", case_type="market_sizing",
                       geography_relevant=True, geography="China",
                       assistance_level="guided", assistance_needed=True)
        self.assertEqual(fields, ("session_kind",))
        question = setup_policy.setup_question(fields, "zh")
        self.assertIn("完整 Case", question)
        self.assertIn("专项练习", question)

    def test_real_failure_path_cannot_start_a_drill(self):
        request = "开始mock → sizing → China → Tutorial → Guided"
        self.assertIsNone(setup_policy.infer_session_kind(request))
        fields = setup("ambiguous_tutorial", case_type="market_sizing",
                       geography="China", geography_relevant=True,
                       assistance_level="guided", assistance_needed=True)
        self.assertEqual(fields, ("session_kind",))

    def test_guided_does_not_change_session_kind(self):
        self.assertIsNone(setup_policy.infer_session_kind("guided"))
        self.assertIsNone(setup_policy.infer_session_kind(
            "Tutorial Mode, market sizing, China, Guided"))

    def test_conflicting_shape_signals_require_confirmation(self):
        self.assertIsNone(setup_policy.infer_session_kind(
            "one complete market sizing case as a focused drill"))

    def test_bare_casual_delegation_is_not_blanket_random(self):
        for phrase in ("随便", "你决定"):
            with self.subTest(phrase=phrase):
                self.assertEqual(setup_policy.random_authorisations(
                    phrase, asked_fields=("case_type", "geography")), set())

    def test_bare_delegation_can_answer_one_clear_pending_question(self):
        self.assertEqual(setup_policy.random_authorisations(
            "随便", asked_fields=("interview_format",)), {"interview_format"})

    def test_random_case_scope_does_not_expand(self):
        self.assertEqual(setup_policy.random_authorisations("随便来一道"),
                         {"case_type"})

    def test_explicit_everything_random_remains_broad(self):
        self.assertEqual(setup_policy.random_authorisations("全部随机"),
                         set(setup_policy.RANDOM_FIELDS))

    def test_ambiguity_is_not_random_authorisation(self):
        self.assertIsNone(setup_policy.infer_session_kind("sizing"))
        self.assertEqual(setup_policy.random_authorisations("sizing"), set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
