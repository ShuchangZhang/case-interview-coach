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


class DifficultyResolutionTests(unittest.TestCase):

    def test_explicit_beginner_is_used(self):
        self.assertEqual(setup_policy.resolve_difficulty("Beginner"),
                         {"value": "beginner", "source": "user"})

    def test_explicit_advanced_is_used(self):
        self.assertEqual(setup_policy.resolve_difficulty("高难度"),
                         {"value": "advanced", "source": "user"})

    def test_relative_harder_request_moves_one_level(self):
        self.assertEqual(setup_policy.resolve_difficulty(
            "难一点", current="intermediate")["value"], "advanced")

    def test_dimension_specific_request_does_not_raise_overall_level(self):
        result = setup_policy.resolve_difficulty(
            "计算别太难，但商业判断难一点", current="intermediate")
        self.assertEqual(result["value"], "intermediate")
        self.assertEqual(result["modifiers"], {
            "math": "easier", "business_judgment": "harder"})

    def test_reliable_profile_can_supply_the_level(self):
        self.assertEqual(setup_policy.resolve_difficulty(
            profile_level="advanced"),
            {"value": "advanced", "source": "profile"})

    def test_no_profile_has_stable_intermediate_default(self):
        self.assertEqual(setup_policy.resolve_difficulty(),
                         {"value": "intermediate", "source": "default"})

    def test_summary_displays_final_difficulty(self):
        context = setup_policy.resolve_defaults({
            "mode": "interview", "session_kind": "full_case",
            "case_type": "market_entry", "geography": "China",
            "interview_format": "interviewee_led",
        }, automatic_industry="Consumer goods")
        self.assertIn("Intermediate", setup_policy.session_summary(context))

    def test_prestart_difficulty_edit_is_local(self):
        context = {
            "mode": "tutorial", "session_kind": "full_case",
            "case_type": "profitability", "geography": "China",
            "interview_format": "interviewee_led", "assistance_level": "light",
            "industry": "Retail", "industry_source": "automatic",
            "difficulty": "intermediate", "difficulty_source": "default",
        }
        updated = setup_policy.apply_prestart_updates(context, difficulty="难一点")
        self.assertEqual(updated["difficulty"], "advanced")
        for field in ("mode", "session_kind", "case_type", "geography",
                      "interview_format", "assistance_level", "industry"):
            self.assertEqual(updated[field], context[field])

    def test_user_choice_beats_profile(self):
        self.assertEqual(setup_policy.resolve_difficulty(
            requested="Beginner", profile_level="advanced")["value"], "beginner")


class IndustryResolutionTests(unittest.TestCase):

    def test_explicit_industry_is_used(self):
        self.assertEqual(setup_policy.resolve_industry(
            requested="Electric vehicles", automatic="Retail"),
            {"value": "Electric vehicles", "source": "user"})

    def test_unspecified_industry_uses_economic_selection(self):
        self.assertEqual(setup_policy.resolve_industry(automatic="Airlines"),
                         {"value": "Airlines", "source": "automatic"})

    def test_resolved_automatic_industry_is_stable_on_rerender(self):
        context = setup_policy.resolve_defaults({
            "mode": "interview", "session_kind": "full_case",
            "case_type": "profitability", "interview_format": "interviewer_led",
        }, automatic_industry="Airlines")
        self.assertEqual(setup_policy.resolve_defaults(context)["industry"], "Airlines")

    def test_summary_displays_final_industry(self):
        context = setup_policy.resolve_defaults({
            "mode": "interview", "session_kind": "full_case",
            "case_type": "profitability", "geography": "US",
            "interview_format": "interviewer_led",
        }, automatic_industry="Airlines")
        self.assertIn("Airlines", setup_policy.session_summary(context))

    def test_prestart_industry_edit_is_local(self):
        context = {
            "mode": "interview", "session_kind": "full_case",
            "case_type": "profitability", "geography": "US",
            "interview_format": "interviewer_led", "industry": "Airlines",
            "industry_source": "automatic", "difficulty": "intermediate",
            "difficulty_source": "default",
        }
        updated = setup_policy.apply_prestart_updates(context, industry="Retail")
        self.assertEqual(updated["industry"], "Retail")
        self.assertEqual(updated["industry_source"], "user")
        self.assertEqual(updated["case_type"], "profitability")
        self.assertEqual(updated["interview_format"], "interviewer_led")

    def test_industry_neutral_drill_omits_industry(self):
        context = setup_policy.resolve_defaults({
            "mode": "tutorial", "session_kind": "focused_drill",
            "training_focus": "mental math", "assistance_level": "guided",
            "industry_applicable": False,
        })
        self.assertIsNone(context["industry"])
        self.assertNotIn("Industry", setup_policy.session_summary(context))

    def test_started_session_rejects_silent_industry_change(self):
        with self.assertRaisesRegex(ValueError, "locked"):
            setup_policy.apply_prestart_updates(
                {"formal_started": True, "industry": "Airlines"},
                industry="Retail")


class FocusedDrillDefaultTests(unittest.TestCase):

    def test_unspecified_count_defaults_to_three(self):
        context = setup_policy.resolve_defaults({
            "mode": "tutorial", "session_kind": "focused_drill",
            "training_focus": "exhibit interpretation",
            "assistance_level": "guided", "industry_applicable": False,
        })
        self.assertEqual(context["planned_reps"], 3)
        self.assertEqual(context["planned_reps_source"], "default")

    def test_default_three_is_visible_before_rep_one(self):
        context = setup_policy.resolve_defaults({
            "mode": "tutorial", "session_kind": "focused_drill",
            "training_focus": "exhibit interpretation",
            "assistance_level": "guided", "industry_applicable": False,
        })
        self.assertIn("3 reps", setup_policy.session_summary(context))

    def test_explicit_five_is_used_and_visible(self):
        context = setup_policy.resolve_defaults({
            "mode": "tutorial", "session_kind": "focused_drill",
            "training_focus": "exhibit interpretation", "planned_reps": 5,
            "assistance_level": "guided", "industry_applicable": False,
        })
        self.assertEqual(context["planned_reps"], 5)
        self.assertIn("5 reps", setup_policy.session_summary(context))

    def test_rep_count_never_adds_a_setup_question(self):
        fields = setup("tutorial_drill", training_focus="exhibit interpretation")
        self.assertNotIn("planned_reps", fields)

    def test_resolved_count_stays_in_session_state(self):
        context = setup_policy.resolve_defaults({
            "mode": "tutorial", "session_kind": "focused_drill",
            "training_focus": "case math", "planned_reps": 5,
            "assistance_level": "assisted", "industry_applicable": False,
        })
        copied_to_session_state = dict(context)
        self.assertEqual(copied_to_session_state["planned_reps"], 5)


class SessionSummaryTests(unittest.TestCase):

    def test_full_interview_summary_has_visible_case_flavour(self):
        context = setup_policy.resolve_defaults({
            "mode": "interview", "session_kind": "full_case",
            "case_type": "profitability", "geography": "US",
            "interview_format": "interviewee_led",
        }, profile_level="advanced", automatic_industry="Airlines")
        summary = setup_policy.session_summary(context)
        for phrase in ("US", "Profitability", "Airlines", "Advanced",
                       "Formal full-case mock", "You drive", "HTML debrief"):
            self.assertIn(phrase, summary)

    def test_full_tutorial_summary_has_starting_assistance(self):
        context = setup_policy.resolve_defaults({
            "mode": "tutorial", "session_kind": "full_case",
            "case_type": "market_entry", "geography": "China",
            "interview_format": "interviewee_led", "assistance_level": "light",
        }, automatic_industry="Consumer goods")
        summary = setup_policy.session_summary(context)
        self.assertIn("Full Tutorial case", summary)
        self.assertIn("Light assistance", summary)

    def test_focused_drill_summary_has_count_and_stop_boundary(self):
        context = setup_policy.resolve_defaults({
            "mode": "tutorial", "session_kind": "focused_drill",
            "training_focus": "exhibit interpretation", "geography": "China",
            "assistance_level": "guided", "industry_applicable": False,
        })
        summary = setup_policy.session_summary(context)
        self.assertIn("Focused drill", summary)
        self.assertIn("3 reps", summary)
        self.assertIn("continue or end after each rep", summary)

    def test_summary_omits_meaningless_beginner_metadata(self):
        context = setup_policy.resolve_defaults({
            "mode": "tutorial", "session_kind": "beginner_curriculum",
            "training_focus": "MECE fundamentals", "assistance_level": "guided",
            "industry_applicable": False,
        })
        summary = setup_policy.session_summary(context)
        self.assertNotIn("Difficulty", summary)
        self.assertNotIn("Industry", summary)
        self.assertNotIn("Intermediate", summary)

    def test_chinese_summary_hides_internal_enums(self):
        context = setup_policy.resolve_defaults({
            "mode": "tutorial", "session_kind": "full_case",
            "case_type": "market_entry", "geography": "中国",
            "interview_format": "interviewee_led", "assistance_level": "light",
        }, automatic_industry="消费品")
        summary = setup_policy.session_summary(context, "zh")
        for raw in ("full_case", "interviewee_led", "minimal_realistic",
                    "intermediate", "focused_drill"):
            self.assertNotIn(raw, summary)
        for phrase in ("市场进入", "中等", "候选人主导", "轻度提示"):
            self.assertIn(phrase, summary)

    def test_local_edit_does_not_reask_resolved_structure(self):
        context = {
            "mode": "tutorial", "session_kind": "full_case",
            "case_type": "market_entry", "geography_relevant": True,
            "geography": "China", "interview_format": "interviewee_led",
            "assistance_needed": True, "assistance_level": "light",
            "difficulty": "intermediate", "difficulty_source": "default",
            "industry": "Consumer goods", "industry_source": "automatic",
        }
        self.assertEqual(setup_policy.missing_setup(context), ())
        updated = setup_policy.apply_prestart_updates(context, industry="Retail")
        self.assertEqual(setup_policy.missing_setup(updated), ())

    def test_summary_and_state_use_same_flavour_values(self):
        context = setup_policy.resolve_defaults({
            "mode": "interview", "session_kind": "full_case",
            "case_type": "market_entry", "geography": "China",
            "interview_format": "interviewer_led", "difficulty": "advanced",
            "industry": "Electric vehicles",
        }, profile_level="beginner", automatic_industry="Retail")
        summary = setup_policy.session_summary(context)
        self.assertEqual(context["difficulty"], "advanced")
        self.assertEqual(context["industry"], "Electric vehicles")
        self.assertIn("Advanced", summary)
        self.assertIn("Electric vehicles", summary)


if __name__ == "__main__":
    unittest.main(verbosity=2)
