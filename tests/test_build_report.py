#!/usr/bin/env python3
"""
Test suite for the Session Report renderer. Standard library only.

    python3 -m unittest discover -s tests -v
    python3 tests/test_build_report.py

Every fixture referenced here is committed under tests/fixtures/, so the results
below are reproducible by anyone who clones the repository.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "scripts", "build_report.py")
FIXTURES = os.path.join(HERE, "fixtures")
INVALID = os.path.join(FIXTURES, "invalid")
EXAMPLES = os.path.join(ROOT, "examples")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_report  # noqa: E402


def run(args, cwd=None):
    """Invoke the renderer as a subprocess, the way a user would."""
    return subprocess.run([sys.executable, SCRIPT] + args, cwd=cwd,
                          capture_output=True, text=True)


def render(fixture_path):
    """Render to a temp file; return (CompletedProcess, html_or_None)."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "out.html")
        proc = run([fixture_path, "-o", out])
        html = None
        if os.path.exists(out):
            with open(out, encoding="utf-8") as f:
                html = f.read()
        return proc, html


class ExampleTests(unittest.TestCase):
    """The bundled examples must render — they are the public smoke test."""

    def test_interview_example_renders(self):
        proc, html = render(os.path.join(EXAMPLES, "interview-report.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Case Interview Performance Report", html)
        self.assertIn("Hire", html)

    def test_tutorial_example_renders(self):
        proc, html = render(os.path.join(EXAMPLES, "tutorial-report.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Case Interview Learning Report", html)

    def test_chinese_tutorial_example_renders(self):
        proc, html = render(os.path.join(EXAMPLES, "tutorial-report.zh-CN.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Case Interview 学习报告", html)
        self.assertIn("能力概览", html)

    def test_chinese_interview_example_renders(self):
        proc, html = render(os.path.join(EXAMPLES, "interview-report.zh-CN.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Case Interview 表现报告", html)
        self.assertIn("最终建议对比", html)

    def test_example_flag_is_cwd_independent(self):
        """--example must resolve from the script, not the caller's directory."""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out.html")
            proc = run(["--example", "interview", "-o", out], cwd=tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(os.path.exists(out))

    def test_skill_root_resolves_from_script_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run(["--skill-root", "-o", "unused"], cwd=tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), ROOT)

    def test_committed_html_previews_match_renderer_output(self):
        """Published HTML previews must stay byte-identical to the real renderer."""
        generated = os.path.join(EXAMPLES, "generated")
        names = ("interview-report", "interview-report.zh-CN",
                 "tutorial-report", "tutorial-report.zh-CN")
        for name in names:
            with self.subTest(example=name):
                source = os.path.join(EXAMPLES, name + ".json")
                committed = os.path.join(generated, name + ".html")
                proc, fresh = render(source)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                with open(committed, encoding="utf-8") as f:
                    self.assertEqual(f.read(), fresh)


class ValidInputTests(unittest.TestCase):

    def test_all_valid_fixtures_render_with_exit_zero(self):
        for name in sorted(os.listdir(FIXTURES)):
            if not name.endswith(".json"):
                continue
            with self.subTest(fixture=name):
                proc, html = render(os.path.join(FIXTURES, name))
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIsNotNone(html)

    def test_untested_dimension_shows_not_tested_and_no_score(self):
        proc, html = render(os.path.join(FIXTURES, "interview-aborted.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Not tested", html)
        self.assertIn("dim--untested", html)

    def test_aborted_session_carries_no_hiring_verdict(self):
        proc, html = render(os.path.join(FIXTURES, "interview-aborted.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Not enough evidence for a hiring recommendation", html)

    def test_tutorial_report_never_shows_a_hiring_band(self):
        for name in ("tutorial-assisted.json", "tutorial-independent.json"):
            with self.subTest(fixture=name):
                proc, html = render(os.path.join(FIXTURES, name))
                self.assertEqual(proc.returncode, 0, proc.stderr)
                for band in ("Strong Hire", "No Hire", "Borderline"):
                    self.assertNotIn(band, html)
                self.assertNotIn('class="result__verdict"', html)

    def test_tutorial_report_shows_independence(self):
        proc, html = render(os.path.join(FIXTURES, "tutorial-independent.json"))
        self.assertIn("Independence", html)

    def test_assistance_level_is_rendered_for_interview(self):
        proc, html = render(os.path.join(FIXTURES, "interview-weak.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Substantial", html)


class EscapingTests(unittest.TestCase):
    """Untrusted text is escaped and rendered. Escaping never fails the build."""

    PAYLOAD = ('<script>alert(1)</script><img src=x onerror=alert(2)>'
               '<svg onload=alert(3)> 5 < 7 & "q"')

    def test_markup_in_user_text_is_escaped_not_executed(self):
        proc, html = render(os.path.join(FIXTURES, "html-injection.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertNotIn("<img src=x onerror=alert(2)>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&amp;", html)

    def test_no_attacker_controlled_tag_survives_as_a_tag(self):
        """The threat model is tag *parsing*, not the substring appearing at all.

        An escaped payload legitimately contains the text 'onerror=', so grepping
        for that is a false positive. What matters is that no attacker string is
        parsed as an element or an event-handler attribute.
        """
        import html as html_mod
        with open(os.path.join(EXAMPLES, "interview-report.json"),
                  encoding="utf-8") as f:
            doc = json.load(f)
        doc["headline"]["one_line_diagnosis"] = self.PAYLOAD

        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "in.json")
            out = os.path.join(tmp, "out.html")
            with open(src, "w", encoding="utf-8") as f:
                json.dump(doc, f)
            proc = run([src, "-o", out])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with open(out, encoding="utf-8") as f:
                page = f.read()

        # The renderer's own inline <style> is the only tag of these kinds.
        tags = [t.lower() for t in re.findall(
            r"<\s*(script|img|svg|iframe|object|embed|link|style)\b", page, re.I)]
        self.assertEqual([t for t in tags if t != "style"], [],
                         "an attacker-controlled tag was parsed as a tag")
        self.assertIsNone(re.search(r"<[a-zA-Z][^>]*\son[a-z]+\s*=", page),
                          "an event-handler attribute reached the output")
        self.assertNotIn("javascript:", page.lower())
        self.assertNotIn(self.PAYLOAD, page, "raw payload must not appear")
        self.assertIn(html_mod.escape(self.PAYLOAD, quote=True), page,
                      "payload must appear, escaped")

    def test_output_has_no_external_references(self):
        proc, html = render(os.path.join(EXAMPLES, "interview-report.json"))
        for token in ("http://", "https://", "<script", "@import", "cdn."):
            self.assertNotIn(token, html)


class InvalidInputTests(unittest.TestCase):
    """Every invalid fixture must fail loudly: no HTML, exit code 2."""

    EXPECTED = {
        "score-too-high": "score",
        "score-negative": "score",
        "score-nan": "finite",
        "score-string": "score",
        "bad-mode": "session.mode",
        "bad-completion": "session.completion",
        "bad-assistance-level": "assistance.level",
        "bad-independence": "independence",
        "bad-verdict-value": "headline.verdict",
        "untested-with-score": "untested",
        "verdict-when-unavailable": "verdict",
        "verdict-missing-reason": "verdict_unavailable_reason",
        "interview-field-in-tutorial": "missed_insights",
        "tutorial-field-in-interview": "mastery",
        "tutorial-verdict": "tutorial report",
        "guardrail-percentile": "Guard-rail",
        "guardrail-offer-rate": "Guard-rail",
        "guardrail-firm-benchmark": "Guard-rail",
        "benchmark-string-false-bypass": "benchmark_requested",
        "benchmark-string-true": "JSON boolean",
        "benchmark-int-one": "JSON boolean",
        "benchmark-int-zero": "JSON boolean",
        "benchmark-null": "JSON boolean",
        "session-interview-format-in-tutorial": "session.interview_format",
        "session-training-focus-in-interview": "session.training_focus",
        "session-assistance-start-in-interview": "session.assistance_start",
        "session-assistance-end-in-interview": "session.assistance_end",
        "session-independence-marker-in-interview": "session.independence_marker",
    }

    def test_every_invalid_fixture_is_rejected(self):
        names = [n for n in os.listdir(INVALID) if n.endswith(".json")]
        self.assertTrue(names, "no invalid fixtures found")
        for name in sorted(names):
            with self.subTest(fixture=name):
                with tempfile.TemporaryDirectory() as tmp:
                    out = os.path.join(tmp, "out.html")
                    proc = run([os.path.join(INVALID, name), "-o", out])
                    self.assertEqual(
                        proc.returncode, 2,
                        "{} should exit 2; got {}\n{}".format(
                            name, proc.returncode, proc.stderr))
                    self.assertFalse(
                        os.path.exists(out),
                        "{} must not produce HTML".format(name))
                    self.assertIn("ValidationError", proc.stderr)

    def test_error_messages_name_the_field_and_the_value(self):
        for name, needle in sorted(self.EXPECTED.items()):
            with self.subTest(fixture=name):
                with tempfile.TemporaryDirectory() as tmp:
                    proc = run([os.path.join(INVALID, name + ".json"),
                                "-o", os.path.join(tmp, "o.html")])
                    self.assertIn(needle, proc.stderr,
                                  "{}: stderr was {!r}".format(name, proc.stderr))

    def test_malformed_json_exits_one_not_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = os.path.join(tmp, "bad.json")
            with open(bad, "w") as f:
                f.write("{not json")
            proc = run([bad, "-o", os.path.join(tmp, "o.html")])
            self.assertEqual(proc.returncode, 1)
            self.assertIn("not valid JSON", proc.stderr)

    def test_missing_file_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run([os.path.join(tmp, "nope.json"), "-o",
                        os.path.join(tmp, "o.html")])
            self.assertEqual(proc.returncode, 1)


class GuardRailScopeTests(unittest.TestCase):
    """Guard rails police evaluative prose, not case content."""

    def test_case_content_may_mention_industry_averages(self):
        with open(os.path.join(EXAMPLES, "interview-report.json"),
                  encoding="utf-8") as f:
            doc = json.load(f)
        doc["annotations"][0]["comment"] = (
            "Compared the client's 12% margin against the industry average of 18% "
            "and the 34% conversion rate in the exhibit.")
        build_report.check_guard_rails(doc)  # must not raise

    def test_evaluative_prose_may_not_claim_a_percentile(self):
        with open(os.path.join(EXAMPLES, "interview-report.json"),
                  encoding="utf-8") as f:
            doc = json.load(f)
        doc["headline"]["one_line_diagnosis"] = "You are in the top 10% of candidates."
        with self.assertRaises(build_report.ValidationError):
            build_report.check_guard_rails(doc)


class BenchmarkRequestedTests(unittest.TestCase):
    """headline.benchmark_requested must be a real JSON boolean.

    Regression guard for an audit finding: the field was read through bool(),
    so the string "false" — which is truthy in Python — unlocked the hiring
    verdict that a tutorial report must never carry.
    """

    def _doc(self, value=..., mode="tutorial"):
        name = "tutorial-report.json" if mode == "tutorial" else "interview-report.json"
        with open(os.path.join(EXAMPLES, name), encoding="utf-8") as f:
            doc = json.load(f)
        if value is not ...:
            doc["headline"]["benchmark_requested"] = value
        return doc

    def test_absent_field_defaults_to_false(self):
        doc = self._doc()
        self.assertNotIn("benchmark_requested", doc["headline"])
        build_report.validate(doc)  # must not raise
        doc["headline"]["verdict"] = "Hire"
        with self.assertRaises(build_report.ValidationError):
            build_report.validate(doc)

    def test_true_permits_a_benchmarked_tutorial_verdict(self):
        doc = self._doc(True)
        doc["headline"]["verdict"] = "Borderline"
        build_report.validate(doc)  # must not raise

    def test_false_behaves_exactly_like_absent(self):
        doc = self._doc(False)
        build_report.validate(doc)
        doc["headline"]["verdict"] = "Hire"
        with self.assertRaises(build_report.ValidationError):
            build_report.validate(doc)

    def test_non_boolean_values_are_rejected_not_coerced(self):
        for value in ("false", "true", 1, 0, None, [], {}, "yes"):
            with self.subTest(value=value):
                with self.assertRaises(build_report.ValidationError) as cm:
                    build_report.validate(self._doc(value))
                self.assertIn("JSON boolean", str(cm.exception))

    def test_string_false_cannot_unlock_a_tutorial_verdict(self):
        """The exact audit payload, end to end through the CLI."""
        path = os.path.join(INVALID, "benchmark-string-false-bypass.json")
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        self.assertEqual(doc["session"]["mode"], "tutorial")
        self.assertEqual(doc["headline"]["benchmark_requested"], "false")
        self.assertEqual(doc["headline"]["verdict"], "Hire")

        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out.html")
            proc = run([path, "-o", out])
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertFalse(os.path.exists(out), "no HTML may be written")
            self.assertIn("benchmark_requested", proc.stderr)

    def test_python_truthiness_would_have_accepted_it(self):
        """Pins why the isinstance check matters rather than restating it."""
        self.assertTrue(bool("false"))


class ModeSpecificSessionFieldTests(unittest.TestCase):
    """Shared full-case format and mode-specific fields stay correctly isolated."""

    def _doc(self, mode):
        name = "tutorial-report.json" if mode == "tutorial" else "interview-report.json"
        with open(os.path.join(EXAMPLES, name), encoding="utf-8") as f:
            return json.load(f)

    def test_registry_covers_every_mode_specific_session_field(self):
        interview = set(build_report.MODE_FIELDS["interview"]["session"])
        tutorial = set(build_report.MODE_FIELDS["tutorial"]["session"])
        shared = set(build_report.SHARED_SESSION_FIELDS)
        self.assertEqual(interview & tutorial, set(), "a field cannot belong to both modes")
        self.assertEqual((interview | tutorial) & shared, set(),
                         "a field cannot be both shared and mode-specific")
        self.assertIn("interview_format", shared)
        self.assertIn("session_kind", shared)
        for key in ("training_focus", "assistance_start", "assistance_end",
                    "independence_marker", "planned_reps", "completed_reps",
                    "session_end_reason"):
            self.assertIn(key, tutorial)

    def test_every_session_key_in_the_examples_is_classified(self):
        """A new field cannot be added without a home in the registry."""
        known = (set(build_report.SHARED_SESSION_FIELDS)
                 | set(build_report.MODE_FIELDS["interview"]["session"])
                 | set(build_report.MODE_FIELDS["tutorial"]["session"]))
        for mode in ("interview", "tutorial"):
            with self.subTest(mode=mode):
                keys = set(self._doc(mode)["session"])
                self.assertEqual(keys - known, set(),
                                 "unclassified session field(s) in the {} example".format(mode))

    def test_interview_full_case_accepts_both_formats(self):
        for value in ("interviewee_led", "interviewer_led"):
            with self.subTest(value=value):
                doc = self._doc("interview")
                doc["session"]["session_kind"] = "full_case"
                doc["session"]["interview_format"] = value
                build_report.validate(doc)

    def test_tutorial_full_case_accepts_both_formats(self):
        for value in ("interviewee_led", "interviewer_led"):
            with self.subTest(value=value):
                doc = self._doc("tutorial")
                doc["session"]["session_kind"] = "full_case"
                doc["session"]["interview_format"] = value
                for key in ("planned_reps", "completed_reps", "session_end_reason"):
                    doc["session"].pop(key, None)
                build_report.validate(doc)

    def test_full_case_requires_format_in_both_modes(self):
        for mode in ("interview", "tutorial"):
            with self.subTest(mode=mode):
                doc = self._doc(mode)
                doc["session"]["session_kind"] = "full_case"
                doc["session"].pop("interview_format", None)
                with self.assertRaises(build_report.ValidationError) as cm:
                    build_report.validate(doc)
                self.assertIn("session.interview_format", str(cm.exception))

    def test_tutorial_drill_without_format_is_valid(self):
        doc = self._doc("tutorial")
        doc["session"]["session_kind"] = "focused_drill"
        doc["session"].pop("interview_format", None)
        build_report.validate(doc)

    def test_tutorial_drill_rejects_meaningless_format(self):
        doc = self._doc("tutorial")
        doc["session"]["session_kind"] = "focused_drill"
        doc["session"]["interview_format"] = "interviewer_led"
        with self.assertRaises(build_report.ValidationError) as cm:
            build_report.validate(doc)
        self.assertIn("session.interview_format", str(cm.exception))

    def test_unknown_format_and_session_kind_are_rejected(self):
        doc = self._doc("tutorial")
        doc["session"]["session_kind"] = "workshop"
        with self.assertRaises(build_report.ValidationError) as cm:
            build_report.validate(doc)
        self.assertIn("session.session_kind", str(cm.exception))
        doc = self._doc("interview")
        doc["session"]["interview_format"] = "coach_led"
        with self.assertRaises(build_report.ValidationError) as cm:
            build_report.validate(doc)
        self.assertIn("session.interview_format", str(cm.exception))

    def test_chinese_tutorial_full_case_uses_natural_format_labels(self):
        doc = self._doc("tutorial")
        doc["language"] = "zh"
        doc["session"]["session_kind"] = "full_case"
        doc["session"]["interview_format"] = "interviewer_led"
        for key in ("planned_reps", "completed_reps", "session_end_reason"):
            doc["session"].pop(key, None)
        build_report.validate(doc)
        page = build_report.build(doc)
        self.assertIn("推进方式", page)
        self.assertIn("由面试官主导推进", page)
        self.assertNotIn("interviewer_led", page)

    def test_tutorial_fields_rejected_in_interview_session(self):
        cases = {
            "training_focus": "structuring",
            "assistance_start": "guided",
            "assistance_end": "independent",
            "independence_marker": {"at": "Exhibit 2"},
        }
        for key, value in cases.items():
            with self.subTest(field=key):
                doc = self._doc("interview")
                doc["session"][key] = value
                with self.assertRaises(build_report.ValidationError) as cm:
                    build_report.validate(doc)
                self.assertIn("session." + key, str(cm.exception))

    def test_valid_examples_keep_their_own_mode_fields(self):
        build_report.validate(self._doc("interview"))   # has interview_format
        build_report.validate(self._doc("tutorial"))    # has training_focus etc.


class FocusedDrillMetadataTests(unittest.TestCase):
    """Rep progress and normal early endings render without leaking enums."""

    @staticmethod
    def _doc(language="en"):
        name = "tutorial-report.zh-CN.json" if language == "zh" else "tutorial-report.json"
        with open(os.path.join(EXAMPLES, name), encoding="utf-8") as f:
            return json.load(f)

    def test_focused_drill_progress_renders_in_natural_english(self):
        doc = self._doc()
        build_report.validate(doc)
        page = build_report.build(doc)
        for text in ("Training format", "Focused drill", "Drill progress",
                     "4 of 4 reps completed", "Completed as planned"):
            self.assertIn(text, page)
        self.assertNotIn("completed_as_planned", page)

    def test_focused_drill_progress_renders_in_natural_chinese(self):
        doc = self._doc("zh")
        build_report.validate(doc)
        page = build_report.build(doc)
        for text in ("训练方式", "专项练习", "练习进度",
                     "计划 4 题 · 完成 4 题", "按计划完成"):
            self.assertIn(text, page)
        self.assertNotIn("focused_drill", page)

    def test_between_rep_early_end_is_complete_not_aborted(self):
        doc = self._doc()
        doc["session"].update({
            "completion": "complete",
            "completed_reps": 1,
            "session_end_reason": "ended_early_between_reps",
        })
        build_report.validate(doc)
        page = build_report.build(doc)
        self.assertIn("1 of 4 reps completed", page)
        self.assertIn("Ended normally between reps", page)
        self.assertNotIn("Not completed — ended early", page)

    def test_mid_rep_abort_requires_aborted_completion(self):
        doc = self._doc()
        doc["session"].update({
            "completion": "aborted",
            "completed_reps": 1,
            "session_end_reason": "aborted_mid_rep",
        })
        build_report.validate(doc)
        doc["session"]["completion"] = "complete"
        with self.assertRaises(build_report.ValidationError):
            build_report.validate(doc)

    def test_progress_fields_are_all_or_nothing(self):
        for missing in ("planned_reps", "completed_reps", "session_end_reason"):
            with self.subTest(missing=missing):
                doc = self._doc()
                doc["session"].pop(missing)
                with self.assertRaises(build_report.ValidationError) as cm:
                    build_report.validate(doc)
                self.assertIn("drill metadata", str(cm.exception))

    def test_full_case_rejects_drill_progress(self):
        doc = self._doc()
        doc["session"]["session_kind"] = "full_case"
        doc["session"]["interview_format"] = "interviewer_led"
        with self.assertRaises(build_report.ValidationError) as cm:
            build_report.validate(doc)
        self.assertIn("drill metadata", str(cm.exception))


class PromptTranscriptTests(unittest.TestCase):
    """The report preserves the candidate-visible evidence record verbatim."""

    def _example(self, name):
        path = os.path.join(EXAMPLES, name + ".json")
        with open(path, encoding="utf-8") as f:
            return path, json.load(f)

    def test_interview_and_tutorial_include_exact_case_prompt(self):
        import html as html_mod
        for name in ("interview-report", "tutorial-report"):
            with self.subTest(example=name):
                path, doc = self._example(name)
                proc, page = render(path)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("Case Prompt", page)
                self.assertIn(html_mod.escape(doc["case_prompt"], quote=True), page)

    def test_full_transcript_content_and_order_are_preserved(self):
        import html as html_mod
        for name in ("interview-report", "tutorial-report"):
            with self.subTest(example=name):
                path, doc = self._example(name)
                proc, page = render(path)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                positions = []
                for record in doc["transcript"]:
                    self.assertIn(html_mod.escape(record["content"], quote=True), page)
                    positions.append(page.index('id="{}"'.format(record["id"])))
                self.assertEqual(positions, sorted(positions))
                self.assertNotIn("…", "".join(r["content"] for r in doc["transcript"]))

    def test_mode_appropriate_speakers_are_rendered(self):
        interview, interview_html = render(os.path.join(EXAMPLES, "interview-report.json"))
        tutorial, tutorial_html = render(os.path.join(EXAMPLES, "tutorial-report.json"))
        self.assertEqual(interview.returncode, 0, interview.stderr)
        self.assertEqual(tutorial.returncode, 0, tutorial.stderr)
        self.assertIn("Interviewer", interview_html)
        self.assertNotIn("<b>Coach</b>", interview_html)
        self.assertIn("<b>Coach</b>", tutorial_html)
        self.assertIn("<b>Interviewer</b>", interview_html)

    def test_critical_moment_links_to_existing_turn(self):
        proc, page = render(os.path.join(EXAMPLES, "interview-report.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('href="#T04">View T04</a>', page)
        self.assertIn('id="T04"', page)

    def test_missing_turn_reference_fails_validation(self):
        _, doc = self._example("interview-report")
        doc["dimensions"][0]["turn_refs"] = ["T999"]
        with self.assertRaises(build_report.ValidationError) as cm:
            build_report.validate(doc)
        self.assertIn("T999", str(cm.exception))

    def test_case_prompt_and_transcript_markup_are_escaped(self):
        import html as html_mod
        _, doc = self._example("interview-report")
        payload = '<script>x()</script><img src=x onerror=y><svg onload=z>'
        doc["case_prompt"] = payload
        doc["transcript"][1]["content"] = payload
        build_report.validate(doc)
        page = build_report.build(doc)
        self.assertNotIn(payload, page)
        self.assertIn(html_mod.escape(payload, quote=True), page)
        self.assertNotIn("<script>x()</script>", page)

    def test_prompt_and_transcript_are_required(self):
        _, doc = self._example("interview-report")
        for field, value in (("case_prompt", ""), ("case_prompt", None),
                             ("transcript", []), ("transcript", None)):
            with self.subTest(field=field, value=value):
                altered = json.loads(json.dumps(doc))
                altered[field] = value
                with self.assertRaises(build_report.ValidationError):
                    build_report.validate(altered)

    def test_transcript_ids_are_unique_and_order_is_the_array_order(self):
        _, doc = self._example("tutorial-report")
        doc["transcript"][1]["id"] = doc["transcript"][0]["id"]
        with self.assertRaises(build_report.ValidationError) as cm:
            build_report.validate(doc)
        self.assertIn("unique transcript ID", str(cm.exception))

    def test_roles_are_mode_specific(self):
        _, doc = self._example("interview-report")
        doc["transcript"][0]["role"] = "tutor"
        with self.assertRaises(build_report.ValidationError):
            build_report.validate(doc)
        _, doc = self._example("tutorial-report")
        doc["transcript"][0]["role"] = "interviewer"
        with self.assertRaises(build_report.ValidationError):
            build_report.validate(doc)

    def test_internal_fields_cannot_enter_transcript(self):
        _, doc = self._example("interview-report")
        doc["transcript"][0]["system_prompt"] = "hidden instruction"
        with self.assertRaises(build_report.ValidationError) as cm:
            build_report.validate(doc)
        self.assertIn("user-visible transcript fields", str(cm.exception))

    def test_aborted_interview_marks_formal_end_and_debrief(self):
        proc, page = render(os.path.join(FIXTURES, "interview-aborted.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Formal Interview Ends Here", page)
        self.assertIn("Post-Interview Debrief Begins", page)
        self.assertLess(page.index("Formal Interview Ends Here"),
                        page.index("Post-Interview Debrief Begins"))

    def test_tutorial_assistance_change_is_an_event_not_a_message(self):
        proc, page = render(os.path.join(EXAMPLES, "tutorial-report.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('class="transcript__event" id="E02"', page)
        self.assertIn("no further hints", page)

    def test_long_transcript_renders_completely_and_print_css_reveals_it(self):
        _, doc = self._example("interview-report")
        doc["transcript"] = [
            {"id": "T{:02d}".format(i), "type": "message",
             "role": "candidate" if i % 2 == 0 else "interviewer",
             "content": "Complete message {} with no truncation.".format(i)}
            for i in range(1, 81)
        ]
        for item in doc.get("dimensions", []) + doc.get("strengths", []) + doc.get("weaknesses", []):
            item.pop("turn_refs", None)
        for item in doc.get("annotations", []) + doc.get("missed_insights", []) + doc.get("next_priorities", []):
            item.pop("turn_refs", None)
        for item in (doc.get("assistance") or {}).get("events", []):
            item.pop("turn_refs", None)
        (doc.get("recommendation_compare") or {}).pop("turn_refs", None)
        build_report.validate(doc)
        page = build_report.build(doc)
        self.assertIn("Complete message 80 with no truncation.", page)
        self.assertEqual(page.count('class="transcript__item '), 80)
        self.assertIn(".transcript__body{display:block!important", page)

    def test_public_examples_are_fictional_and_contain_no_internal_record_fields(self):
        for name in ("interview-report", "interview-report.zh-CN",
                     "tutorial-report", "tutorial-report.zh-CN"):
            with self.subTest(example=name):
                _, doc = self._example(name)
                self.assertIn("fictional" if doc["language"] == "en" else "虚构",
                              doc["case_prompt"])
                for record in doc["transcript"]:
                    self.assertEqual(set(record) - set(build_report.TRANSCRIPT_FIELDS), set())



class ReportLanguageTests(unittest.TestCase):
    """A Chinese report reads as Chinese. Internal enums never reach the page."""

    # Internal vocabulary that must be translated before it is rendered.
    ENUMS = ("Assisted", "Independent", "Guided", "Light", "Level 1", "Level 2",
             "Level 3", "Hint", "Retry", "Learning", "Critical Moment",
             "Case Prompt", "Mastered", "Covered", "assistance_start",
             "assistance_end", "assistance_change", "needs_improvement",
             "hint_given")

    @staticmethod
    def visible(path, drop_transcript=False):
        with open(path, encoding="utf-8") as f:
            page = f.read()
        page = re.sub(r"<style.*?</style>", "", page, flags=re.S)
        if drop_transcript:
            page = re.sub(r'<section class="sec transcript">.*?</section>', "",
                          page, flags=re.S)
            page = re.sub(r'<p class="foot">.*?</p>', "", page, flags=re.S)
        import html as html_mod
        return html_mod.unescape(re.sub(r"<[^>]+>", " ", page))

    def test_chinese_reports_render_no_internal_enum(self):
        for name in ("tutorial-report.zh-CN.html", "interview-report.zh-CN.html"):
            path = os.path.join(EXAMPLES, "generated", name)
            text = self.visible(path)
            for token in self.ENUMS:
                with self.subTest(report=name, token=token):
                    self.assertNotIn(token, text)

    def test_chinese_analysis_prose_is_chinese(self):
        """Outside the verbatim transcript, only agreed loanwords may remain."""
        allowed = {"Case Interview", "Case", "Hire"}  # product terms; verdict glossed in place
        for name in ("tutorial-report.zh-CN.html", "interview-report.zh-CN.html"):
            path = os.path.join(EXAMPLES, "generated", name)
            text = self.visible(path, drop_transcript=True)
            found = {w.strip() for w in re.findall(r"[A-Za-z][A-Za-z /&]{2,}", text)}
            with self.subTest(report=name):
                self.assertEqual(found - allowed, set())

    def test_chinese_report_uses_chinese_ui_labels(self):
        path = os.path.join(EXAMPLES, "generated", "tutorial-report.zh-CN.html")
        text = self.visible(path)
        for label in ("本次最重要的三件事", "能力概览", "逐轮复盘", "复盘点评",
                      "如果你只记住三件事", "独立程度"):
            with self.subTest(label=label):
                self.assertIn(label, text)

    def test_english_verdict_is_not_glossed(self):
        """The gloss is for Chinese only; an English report says Hire plainly."""
        with open(os.path.join(EXAMPLES, "generated", "interview-report.html"),
                  encoding="utf-8") as f:
            page = f.read()
        self.assertIn('class="result__verdict">Hire<', page)

    def test_transcript_keeps_original_wording(self):
        """Whatever was said is reproduced exactly, in either language."""
        for stem in ("tutorial-report.zh-CN", "interview-report.zh-CN",
                     "tutorial-report", "interview-report"):
            with open(os.path.join(EXAMPLES, stem + ".json"), encoding="utf-8") as f:
                doc = json.load(f)
            with open(os.path.join(EXAMPLES, "generated", stem + ".html"),
                      encoding="utf-8") as f:
                page = f.read()
            import html as html_mod
            for record in doc["transcript"]:
                with self.subTest(report=stem, turn=record["id"]):
                    self.assertIn(html_mod.escape(record["content"], quote=True), page)

    def test_no_transcript_turn_is_omitted(self):
        for stem in ("tutorial-report.zh-CN", "interview-report"):
            with open(os.path.join(EXAMPLES, stem + ".json"), encoding="utf-8") as f:
                doc = json.load(f)
            with open(os.path.join(EXAMPLES, "generated", stem + ".html"),
                      encoding="utf-8") as f:
                page = f.read()
            for record in doc["transcript"]:
                with self.subTest(report=stem, turn=record["id"]):
                    self.assertIn('id="{}"'.format(record["id"]), page)


class FeedbackProminenceTests(unittest.TestCase):
    """The most important feedback is near the top and easy to find."""

    @staticmethod
    def page(stem):
        with open(os.path.join(EXAMPLES, "generated", stem + ".html"),
                  encoding="utf-8") as f:
            return f.read()

    def test_core_feedback_block_exists(self):
        for stem in ("tutorial-report", "interview-report",
                     "tutorial-report.zh-CN", "interview-report.zh-CN"):
            with self.subTest(report=stem):
                self.assertIn('class="cfwrap"', self.page(stem))

    def test_core_feedback_holds_at_most_three_items(self):
        for stem in ("tutorial-report", "interview-report"):
            with self.subTest(report=stem):
                self.assertLessEqual(self.page(stem).count('<article class="cf '), 3)

    def test_core_feedback_precedes_the_transcript_and_the_detail(self):
        for stem in ("tutorial-report", "tutorial-report.zh-CN"):
            page = self.page(stem)
            with self.subTest(report=stem):
                self.assertLess(page.index('class="cfwrap"'),
                                page.index('class="sec transcript"'))
                self.assertLess(page.index('class="cfwrap"'),
                                page.index('class="takeaways"'))

    def test_biggest_gap_and_next_step_are_both_present(self):
        for stem in ("tutorial-report", "interview-report"):
            page = self.page(stem)
            with self.subTest(report=stem):
                self.assertIn("cf--work", page)
                self.assertIn("cf--next", page)

    def test_takeaways_close_the_report(self):
        for stem in ("tutorial-report", "tutorial-report.zh-CN"):
            page = self.page(stem)
            with self.subTest(report=stem):
                self.assertIn('class="takeaways"', page)
                self.assertGreater(page.index('class="takeaways"'),
                                   page.index('class="sec transcript"'))


class AnnotatedTranscriptTests(unittest.TestCase):
    """Comments sit beside the turn they are about, clearly marked as comments."""

    @staticmethod
    def doc_and_page(stem):
        with open(os.path.join(EXAMPLES, stem + ".json"), encoding="utf-8") as f:
            doc = json.load(f)
        with open(os.path.join(EXAMPLES, "generated", stem + ".html"),
                  encoding="utf-8") as f:
            return doc, f.read()

    def test_annotated_turns_carry_their_comment_inline(self):
        doc, page = self.doc_and_page("tutorial-report")
        for ann in doc["annotations"]:
            turn = ann["turn_id"]
            start = page.index('id="{}"'.format(turn))
            end = page.index("</article>", start)
            with self.subTest(turn=turn):
                self.assertIn('class="ann ', page[start:end],
                              "comment for {} is not inside that turn".format(turn))

    def test_unannotated_turns_get_no_comment(self):
        doc, page = self.doc_and_page("tutorial-report")
        annotated = {a["turn_id"] for a in doc["annotations"]}
        for record in doc["transcript"]:
            if record["id"] in annotated or record["type"] != "message":
                continue
            start = page.index('id="{}"'.format(record["id"]))
            end = page.index("</article>", start)
            with self.subTest(turn=record["id"]):
                self.assertNotIn('class="ann ', page[start:end])

    def test_both_praise_and_criticism_are_supported(self):
        _, page = self.doc_and_page("tutorial-report")
        self.assertIn("ann--strength", page)
        self.assertIn("ann--needs_improvement", page)
        self.assertIn("ann--critical", page)

    def test_comment_is_structurally_separate_from_the_original_words(self):
        doc, page = self.doc_and_page("tutorial-report")
        # The comment is a sibling <aside>, never inside the quoted content div.
        for match in re.finditer(r'<div class="transcript__content">(.*?)</div>',
                                 page, re.S):
            self.assertNotIn("ann__", match.group(1))
        self.assertIn("<aside class=\"ann", page)

    def test_every_comment_is_labelled_as_written_afterwards(self):
        doc, page = self.doc_and_page("tutorial-report")
        self.assertEqual(page.count('class="ann__src"'), len(doc["annotations"]))

    def test_annotation_referencing_a_missing_turn_is_rejected(self):
        proc, html = render(os.path.join(INVALID, "annotation-unknown-turn.json"))
        self.assertEqual(proc.returncode, 2)
        self.assertIsNone(html)
        self.assertIn("turn_id", proc.stderr)

    def test_annotation_type_must_be_known(self):
        proc, _ = render(os.path.join(INVALID, "annotation-bad-type.json"))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("type", proc.stderr)


class DeduplicationTests(unittest.TestCase):
    """One finding is reported once."""

    def test_superseded_sections_are_rejected_not_silently_dropped(self):
        for name in ("superseded-key-moments", "superseded-hints", "superseded-phases"):
            with self.subTest(fixture=name):
                proc, html = render(os.path.join(INVALID, name + ".json"))
                self.assertEqual(proc.returncode, 2)
                self.assertIsNone(html)
                self.assertIn("no longer rendered", proc.stderr)

    def test_each_section_heading_appears_once(self):
        for stem in ("tutorial-report", "interview-report",
                     "tutorial-report.zh-CN", "interview-report.zh-CN"):
            with open(os.path.join(EXAMPLES, "generated", stem + ".html"),
                      encoding="utf-8") as f:
                headings = re.findall(r"<h2>(.*?)</h2>", f.read())
            with self.subTest(report=stem):
                self.assertEqual(sorted(headings), sorted(set(headings)))

    def test_report_has_a_small_number_of_sections(self):
        """The redesign traded section count for prominence; keep it that way."""
        for stem in ("tutorial-report", "interview-report"):
            with open(os.path.join(EXAMPLES, "generated", stem + ".html"),
                      encoding="utf-8") as f:
                headings = re.findall(r"<h2>(.*?)</h2>", f.read())
            with self.subTest(report=stem):
                self.assertLessEqual(len(headings), 9, headings)


class PaletteTests(unittest.TestCase):
    """Executable record of the ordinal ramp properties the CSS relies on."""

    @staticmethod
    def _luminance(hex_colour):
        r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
        def lin(c):
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = lin(r), lin(g), lin(b)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def _contrast(self, a, b):
        la, lb = self._luminance(a), self._luminance(b)
        hi, lo = max(la, lb), min(la, lb)
        return (hi + 0.05) / (lo + 0.05)

    def test_light_ramp_is_monotone_and_clears_surface(self):
        ramp = build_report.ORDINAL_LIGHT
        lums = [self._luminance(c) for c in ramp]
        self.assertEqual(lums, sorted(lums, reverse=True),
                         "light ramp must read light to dark")
        self.assertGreaterEqual(self._contrast(ramp[0], "#fcfcfb"), 2.0,
                                "lightest step must clear 2:1 on the light surface")

    def test_dark_ramp_is_monotone_and_clears_surface(self):
        ramp = build_report.ORDINAL_DARK
        lums = [self._luminance(c) for c in ramp]
        self.assertEqual(lums, sorted(lums),
                         "dark ramp must read dark to light")
        self.assertGreaterEqual(self._contrast(ramp[0], "#1a1a19"), 2.0,
                                "darkest step must clear 2:1 on the dark surface")


if __name__ == "__main__":
    unittest.main(verbosity=2)
