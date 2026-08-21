#!/usr/bin/env python3
"""Regression tests for visible Session boundaries and report triggers."""

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import session_policy  # noqa: E402
import setup_policy  # noqa: E402


def completed_rep(state):
    return session_policy.complete_current_rep(
        session_policy.start_current_rep(state))


class FocusedDrillBoundaryTests(unittest.TestCase):

    def test_default_plan_is_three_visible_reps(self):
        state = session_policy.new_focused_drill()
        self.assertEqual(state["planned_reps"], 3)
        self.assertEqual(state["current_rep"], 1)
        self.assertEqual(state["rep_statuses"],
                         ["presented", "not_presented", "not_presented"])

    def test_presented_rep_is_not_started_or_evaluated(self):
        state = session_policy.new_focused_drill()
        self.assertEqual(session_policy.evaluated_reps(state), ())
        self.assertEqual(state["completed_reps"], 0)

    def test_substantive_response_marks_rep_started(self):
        state = session_policy.start_current_rep(
            session_policy.new_focused_drill())
        self.assertEqual(state["rep_statuses"][0], "started")
        self.assertEqual(session_policy.evaluated_reps(state), ())

    def test_rep_completion_pauses_instead_of_silently_presenting_rep_two(self):
        state = completed_rep(session_policy.new_focused_drill())
        self.assertTrue(state["awaiting_choice"])
        self.assertEqual(state["current_rep"], 1)
        self.assertEqual(state["rep_statuses"][1], "not_presented")
        self.assertFalse(state["report_required"])

    def test_between_rep_message_displays_progress_and_both_choices(self):
        state = completed_rep(session_policy.new_focused_drill())
        message = session_policy.boundary_message(state, "zh")
        self.assertIn("第 1 / 3 题完成", message)
        self.assertIn("继续第 2 题", message)
        self.assertIn("结束专项练习并生成报告", message)

    def test_continue_explicitly_presents_rep_two_without_starting_it(self):
        state = session_policy.continue_drill(
            completed_rep(session_policy.new_focused_drill()))
        self.assertEqual(state["current_rep"], 2)
        self.assertEqual(state["rep_statuses"][1], "presented")
        self.assertEqual(session_policy.evaluated_reps(state), (1,))

    def test_end_between_reps_is_normal_completion_and_requires_report(self):
        state = session_policy.end_between_reps(
            completed_rep(session_policy.new_focused_drill()))
        self.assertEqual(state["completion"], "complete")
        self.assertEqual(state["session_end_reason"],
                         "ended_early_between_reps")
        self.assertTrue(state["report_required"])
        self.assertTrue(state["session_complete"])

    def test_next_rep_shown_but_unanswered_remains_not_started_and_unscored(self):
        state = session_policy.continue_drill(
            completed_rep(session_policy.new_focused_drill()))
        state = session_policy.end_between_reps(state)
        self.assertEqual(state["rep_statuses"][1], "presented")
        self.assertEqual(session_policy.evaluated_reps(state), (1,))
        self.assertEqual(state["completion"], "complete")

    def test_mid_rep_abort_is_incomplete_and_requires_report(self):
        state = session_policy.start_current_rep(
            session_policy.new_focused_drill())
        state = session_policy.abort_mid_rep(state)
        self.assertEqual(state["completion"], "aborted")
        self.assertEqual(state["session_end_reason"], "aborted_mid_rep")
        self.assertEqual(session_policy.evaluated_reps(state), (1,))
        self.assertTrue(state["report_required"])

    def test_presented_rep_cannot_be_mislabeled_as_mid_rep_abort(self):
        with self.assertRaises(ValueError):
            session_policy.abort_mid_rep(session_policy.new_focused_drill())

    def test_completing_all_reps_immediately_requires_report(self):
        state = session_policy.new_focused_drill(planned_reps=2)
        state = completed_rep(state)
        state = session_policy.continue_drill(state)
        state = completed_rep(state)
        self.assertEqual(state["completed_reps"], 2)
        self.assertEqual(state["session_end_reason"], "completed_as_planned")
        self.assertTrue(state["report_required"])
        self.assertFalse(state["awaiting_choice"])


class FullCaseBoundaryTests(unittest.TestCase):

    def test_full_case_completion_requires_report(self):
        result = session_policy.full_case_completed()
        self.assertTrue(result["session_complete"])
        self.assertTrue(result["report_required"])
        self.assertEqual(result["completion"], "complete")

    def test_full_case_completion_never_auto_starts_another_case(self):
        self.assertFalse(session_policy.full_case_completed()["auto_start_next_case"])


class RealFailurePathIntegrationTests(unittest.TestCase):

    def test_full_case_branch_ends_with_report_not_case_two(self):
        self.assertEqual(setup_policy.infer_session_kind("完整 sizing tutorial case"),
                         "full_case")
        result = session_policy.full_case_completed()
        self.assertTrue(result["report_required"])
        self.assertFalse(result["auto_start_next_case"])

    def test_drill_branch_pauses_after_rep_one_and_can_generate_report(self):
        self.assertEqual(setup_policy.infer_session_kind("sizing 专项训练"),
                         "focused_drill")
        state = completed_rep(session_policy.new_focused_drill())
        self.assertTrue(state["awaiting_choice"])
        self.assertEqual(state["rep_statuses"][1], "not_presented")
        state = session_policy.end_between_reps(state)
        self.assertTrue(state["report_required"])
        self.assertEqual(state["session_end_reason"],
                         "ended_early_between_reps")


if __name__ == "__main__":
    unittest.main(verbosity=2)
