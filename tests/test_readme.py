#!/usr/bin/env python3
"""Public README checks for the Session mental model and working links."""

import os
import re
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")


class ReadmeMentalModelTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(README, encoding="utf-8") as f:
            cls.text = f.read()

    def test_both_languages_distinguish_mode_from_training_format(self):
        for phrase in ("**Mode** answers *assessment or teaching?*",
                       "**Training format** answers *what shape does this session take?*",
                       "**Mode** 回答的是：这次是正式测评，还是教学",
                       "**训练方式**回答的是：这次具体怎么练"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_report_timing_table_covers_all_three_training_formats(self):
        for phrase in ("Full Case", "Focused Drill", "Beginner Lesson",
                       "完整 Case", "专项练习（Focused Drill）", "基础教学",
                       "When the HTML report is generated", "什么时候生成 HTML 报告"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_quick_start_uses_explicit_full_case_and_drill_requests(self):
        for phrase in ("as one Full Case", "3 exhibit-interpretation drills",
                       "Market Sizing Tutorial Case，Guided",
                       "3 道 Exhibit Interpretation 专项练习"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_user_visible_boundary_rules_are_explained(self):
        for phrase in ("asks whether to continue", "never answered is\nnot evaluated",
                       "询问继续还是结束", "还没有回答，就\n不会被计入评价"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_local_readme_links_resolve(self):
        targets = re.findall(r"(?<!!)\[[^]]+\]\(([^)]+)\)", self.text)
        for target in targets:
            if target.startswith(("http://", "https://", "#")):
                continue
            path = target.split("#", 1)[0]
            with self.subTest(target=target):
                self.assertTrue(os.path.exists(os.path.join(ROOT, path)), target)

    def test_session_explanation_does_not_reinflate_the_readme(self):
        self.assertLessEqual(len(self.text.splitlines()), 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
