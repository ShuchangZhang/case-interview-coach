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

    def test_tutorial_report_shows_independence_and_hint_track(self):
        proc, html = render(os.path.join(FIXTURES, "tutorial-independent.json"))
        self.assertIn("Independence", html)
        self.assertIn("hint__seq", html)

    def test_assistance_level_is_rendered_for_interview(self):
        proc, html = render(os.path.join(FIXTURES, "interview-weak.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Substantial", html)


class EscapingTests(unittest.TestCase):
    """Untrusted text is escaped and rendered. Escaping never fails the build."""

    def test_markup_in_user_text_is_escaped_not_executed(self):
        proc, html = render(os.path.join(FIXTURES, "html-injection.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertNotIn("<img src=x onerror=alert(2)>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&amp;", html)

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
        doc["key_moments"][0]["what_you_did"] = (
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
