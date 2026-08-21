#!/usr/bin/env python3
"""
Render a Session Report JSON into a single self-contained HTML file.

    python3 build_report.py report.json -o out.html
    python3 build_report.py --example interview -o out.html

Standard library only. No network access, at build time or in the output.

Paths are resolved from this file's own location, never from the caller's working
directory, so the script works when invoked by absolute path from any project:

    python3 ~/.claude/skills/case-interview-coach/scripts/build_report.py ...

Input is validated before anything is rendered. Two classes of problem are treated
very differently:

  * Untrusted *text* (a case answer containing markup) is HTML-escaped and rendered.
    Escaping is a rendering concern and never fails the build.
  * A *validation* or *guard-rail* violation (bad enum, out-of-range score, a hiring
    verdict in a tutorial report, an unverifiable benchmark claim) aborts the build:
    no HTML is written, a specific error naming the field, its value and the legal
    range goes to stderr, and the exit status is non-zero.

Exit codes: 0 success · 2 validation/guard-rail failure · 1 usage or I/O error.
"""

import argparse, html, json, math, os, re, sys, datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
EXAMPLES_DIR = os.path.join(SKILL_ROOT, "examples")


# ---------------------------------------------------------------- palette ---
# Ordinal blue ramps: single hue, monotone lightness, adjacent-step gaps >= 0.06 L,
# and the surface-facing end clearing 2:1 contrast on its own surface. Both ramps are
# re-checked by tests/test_build_report.py::PaletteTests, which is the executable
# record of these properties.
ORDINAL_LIGHT = ["#86b6ef", "#5598e7", "#2a78d6", "#104281"]
ORDINAL_DARK  = ["#184f95", "#256abf", "#3987e5", "#9ec5f4"]

ASSIST_ORDER = ["guided", "assisted", "light", "independent"]
ASSIST_LEVEL_ORDER = ["none", "light", "moderate", "substantial"]

# ------------------------------------------------------------------ i18n ----
L = {
    "en": {
        "fmt_interviewee_led": "You drive the case", "fmt_interviewer_led": "The interviewer drives",
        "cf_head": "The three things that matter most",
        "cf_lead": "If you read nothing else, read this.",
        "cf_strength": "Strongest work",
        "cf_priority": "Biggest gap",
        "cf_next_step": "Train this next",
        "ann_source": "post-session comment",
        "transcript_lead": "The full conversation exactly as it happened, with comments on the turns worth revisiting.",
        "takeaways_h": "If you remember three things",
        "overview_h": "Capability overview",
        "overview_lead": "The score is a rough band, not a measurement. The line beside it is the real signal.",
        "mastery_lead": "What this session established, kept separate from what it did not.",
        "interview_title": "Case Interview Performance Report",
        "tutorial_title": "Case Interview Learning Report",
        "interview_q": "How would this have gone in a real consulting case interview?",
        "tutorial_q": "What was learned, and what can now be done unaided?",
        "case_type": "Case type", "industry": "Industry", "geography": "Geography",
        "difficulty": "Difficulty", "format": "Interview format", "focus": "Training focus",
        "case_prompt": "Case Prompt", "session_summary": "Session Summary",
        "transcript": "Turn-by-turn review", "transcript_open": "Open full evidence record",
        "transcript_privacy": "This transcript contains the complete user-visible conversation from this training session. Review it before sharing the HTML publicly.",
        "evidence": "Evidence", "view_turn": "View",
        "role_candidate": "Candidate", "role_interviewer": "Interviewer", "role_tutor": "Tutor",
        "event": "Session event",
        "source": "Case source", "status": "Status", "assistance": "Interviewer assistance",
        "assist_start": "Assistance at start", "assist_end": "Assistance at end",
        "independent_phase": "Independent phase",
        "complete": "Completed", "aborted": "Not completed — ended early",
        "partial": "Partially completed",
        "overall": "Overall result", "overall_score": "Overall score",
        "no_verdict": "Not enough evidence for a hiring recommendation",
        "diagnosis": "In one line", "learning_summary": "In one line",
        "dimensions": "Capability assessment",
        "not_tested": "Not tested", "of10": "/ 10",
        "independence": "Independence",
        "assessment": "Strengths and detractors",
        "strengths": "What you did well", "weaknesses": "What materially hurt your result",
        "key_moments": "Key moments", "learning_moments": "Key learning moments",
        "missed": "Insights you didn't reach",
        "assistance_h": "Interviewer assistance",
        "hints_h": "Hint dependence",
        "phases_h": "Assisted vs independent performance",
        "assisted_phase": "Assisted phase", "independent_phase_h": "Independent phase",
        "stronger_path": "A stronger line of analysis",
        "rec_compare": "Your recommendation vs a stronger one",
        "your_rec": "What you said", "rec_issues": "Where it falls short",
        "stronger_rec": "A stronger version",
        "recurring": "Recurring mistakes",
        "mastery_h": "Mastery check",
        "mastery_yes": "You can now do this unaided",
        "mastery_no": "Still needs support",
        "lessons": "The methodology that mattered here",
        "next": "What to train next", "next_plan": "Next training plan",
        "current": "Where you are", "why": "Why it matters", "target": "Target",
        "drill": "Drill", "assist_for_drill": "Suggested assistance",
        "what_you_did": "What you did", "worked": "What worked",
        "problem": "The problem", "consequence": "Downstream effect",
        "stronger": "Stronger handling",
        "evidence_avail": "Evidence available", "stopped": "Where you stopped",
        "should": "What follows from it", "why_matters": "Why it matters to the client",
        "benchmark_note": "Indicative benchmark only — not equivalent to an unassisted mock.",
        "new": "New this session", "repeat": "Seen before",
        "generated": "Generated", "no_history": "No cross-session history available yet.",
        "band": {"strong": "Strong", "solid": "Solid", "developing": "Developing",
                 "weak": "Weak", "critical": "Critical"},
        "assist_lv": {"none": "None", "light": "Light", "moderate": "Moderate",
                      "substantial": "Substantial"},
        "assist": {"guided": "Guided", "assisted": "Assisted",
                   "light": "Light assistance", "independent": "Independent"},
    },
    "zh": {
        "fmt_interviewee_led": "由你主导推进", "fmt_interviewer_led": "由面试官主导推进",
        "cf_head": "本次最重要的三件事",
        "cf_lead": "如果只看一段，看这一段。",
        "cf_strength": "做得最好的一点",
        "cf_priority": "最需要提升的一点",
        "cf_next_step": "下一步最该练什么",
        "ann_source": "复盘点评",
        "transcript_lead": "完整对话按原样保留；值得回看的几轮旁边附有点评。",
        "takeaways_h": "如果你只记住三件事",
        "overview_h": "能力概览",
        "overview_lead": "分数只是一个大致区间，不是精确测量。真正有意义的是旁边那句话。",
        "mastery_lead": "这次真正确认下来的能力，和还没确认的分开列。",
        "interview_title": "Case Interview 表现报告",
        "tutorial_title": "Case Interview 学习报告",
        "interview_q": "如果这是一次真实的咨询 Case Interview，这次表现如何？",
        "tutorial_q": "这次学会了什么？哪些已经可以独立完成？",
        "case_type": "题目类型", "industry": "行业", "geography": "地区",
        "difficulty": "难度", "format": "面试形式", "focus": "训练重点",
        "case_prompt": "本次题目", "session_summary": "本次总结",
        "transcript": "逐轮复盘", "transcript_open": "展开完整原始记录",
        "transcript_privacy": "以下是本次训练中全部你可见的对话原文。公开分享这份报告前，请先确认其中没有你不希望外传的内容。",
        "evidence": "原始证据", "view_turn": "查看",
        "role_candidate": "Candidate", "role_interviewer": "Interviewer", "role_tutor": "Tutor",
        "event": "Session 事件",
        "source": "Case 来源", "status": "完成状态", "assistance": "面试官帮助",
        "assist_start": "起始帮助强度", "assist_end": "结束帮助强度",
        "independent_phase": "独立阶段",
        "complete": "已完整完成", "aborted": "未完成 —— 提前结束",
        "partial": "部分完成",
        "overall": "总体结果", "overall_score": "总分",
        "no_verdict": "当前信息不足以形成完整招聘结论",
        "diagnosis": "一句话诊断", "learning_summary": "一句话总结",
        "dimensions": "能力评估",
        "not_tested": "未测试", "of10": "/ 10",
        "independence": "独立程度",
        "assessment": "优势与主要失分点",
        "strengths": "做得好的地方", "weaknesses": "最影响结果的问题",
        "key_moments": "关键面试节点", "learning_moments": "关键学习节点",
        "missed": "你没有抓到的关键洞察",
        "assistance_h": "Interviewer 帮助记录",
        "hints_h": "提示依赖",
        "phases_h": "教学阶段与独立阶段",
        "assisted_phase": "教学 / 提示阶段", "independent_phase_h": "独立阶段",
        "stronger_path": "更优的分析路径",
        "rec_compare": "最终建议对比",
        "your_rec": "你的最终建议", "rec_issues": "存在的问题",
        "stronger_rec": "更强的版本",
        "recurring": "反复出现的问题",
        "mastery_h": "掌握程度盘点",
        "mastery_yes": "本次已经能够独立完成",
        "mastery_no": "仍需要帮助",
        "lessons": "本次最重要的方法论",
        "next": "下一次训练重点", "next_plan": "下一阶段建议",
        "current": "当前状态", "why": "为什么重要", "target": "下一阶段目标",
        "drill": "训练方式", "assist_for_drill": "建议帮助强度",
        "what_you_did": "你当时怎么做", "worked": "做得好的地方",
        "problem": "问题在哪里", "consequence": "对后续的影响",
        "stronger": "更强的处理方式",
        "evidence_avail": "当时有哪些证据", "stopped": "你停在哪一步",
        "should": "应该进一步推出什么", "why_matters": "为什么这对客户决策重要",
        "benchmark_note": "参考性 Benchmark，不等同于完整正式 Mock 结果。",
        "new": "本次新出现", "repeat": "此前已反复出现",
        "generated": "生成于", "no_history": "暂无跨 Session 历史数据。",
        "band": {"strong": "强", "solid": "达标", "developing": "发展中",
                 "weak": "偏弱", "critical": "严重不足"},
        "assist_lv": {"none": "无帮助", "light": "轻微提示", "moderate": "中等提示",
                      "substantial": "较强引导"},
        "assist": {"guided": "Guided 大量教学", "assisted": "Assisted 先做后评",
                   "light": "Light 少量方向提示", "independent": "Independent 零辅助"},
    },
}

# ---------------------------------------------------------------- schema ---
MODES = ("interview", "tutorial")
COMPLETIONS = ("complete", "aborted", "partial")
INDEPENDENCE = ("guided", "assisted", "light", "independent")
ASSIST_LEVELS = ("none", "light", "moderate", "substantial")
HIRING_VERDICTS = ("strong hire", "hire", "borderline", "no hire")
TRANSCRIPT_TYPES = ("message", "event")
TRANSCRIPT_ROLES = ("candidate", "interviewer", "tutor")
TRANSCRIPT_FIELDS = ("id", "type", "role", "content", "stage", "tags",
                     "timestamp", "assistance_level")

# ---------------------------------------------- mode-specific field registry ---
# The single place that answers "which fields belong to which mode?".
# A field belonging to the other mode is a data-construction bug, not a stylistic
# choice: it means the report was assembled from the wrong template and would
# render misleading semantics. Adding a field means adding one line here rather
# than another `if mode == ...` branch somewhere in validate().
#
# Scopes: "top" = document root, "session" = the session object,
#         "headline" = the headline object.
# ------------------------------------------------- human-readable label layer ---
# Internal enums are a data-model convenience. They must never reach the page:
# a reader should see "need a direction hint", not "Level 2" or "assistance_start".
# Everything the renderer prints goes through humanise() or one of these maps.

ASSIST_WORDS = {
    "en": {"guided": "taught first", "assisted": "attempted first, helped when stuck",
           "light": "occasional nudge", "independent": "unaided"},
    "zh": {"guided": "先教后练", "assisted": "先自己做，卡住时给提示",
           "light": "偶尔点一下方向", "independent": "完全独立完成"},
}

# How much help a single answer needed. Ordered from most to least support.
HINT_WORDS = {
    "en": {"l4": "worked through together", "l3": "given part of the method",
           "l2": "given a direction", "l1": "small nudge", "l0": "no help",
           "independent": "unaided", "none": "no help"},
    "zh": {"l4": "带着一步步做", "l3": "给出部分方法后完成", "l2": "给了明确方向",
           "l1": "轻微提示", "l0": "无需提示", "independent": "独立完成",
           "none": "无需提示"},
}

# Legacy spellings that appeared in earlier report JSON, mapped to canonical tokens
# so old data still renders in natural language instead of leaking "Level 2".
HINT_ALIASES = {
    "level 4": "l4", "level 3": "l3", "level 2": "l2", "level 1": "l1",
    "level 0": "l0", "l4": "l4", "l3": "l3", "l2": "l2", "l1": "l1", "l0": "l0",
    "independent": "independent", "independent x5": "independent", "none": "none",
}

# Fields the turn-by-turn review absorbed. Rejected rather than ignored: silently
# dropping data the caller supplied is exactly the failure mode this validator
# exists to prevent, and the message says where the information now belongs.
SUPERSEDED_FIELDS = {
    "hints": "annotations (comment the actual turns where hint strength changed) "
             "and dimensions[].independence",
    "phases": "annotations on the turns either side of the assistance change, plus "
              "dimensions[].independence",
    "key_moments": "annotations — a key moment is a comment on the turn it happened in",
}

ANNOTATION_TYPES = ("strength", "needs_improvement", "critical", "hint_given",
                    "improved", "polish")

ANNOTATION_WORDS = {
    "en": {"strength": "Well done", "needs_improvement": "Needs work",
           "critical": "Critical error", "hint_given": "Hint given",
           "improved": "Improved after the hint", "polish": "Could go further"},
    "zh": {"strength": "做得好", "needs_improvement": "需要提升",
           "critical": "关键错误", "hint_given": "提示介入",
           "improved": "改进后", "polish": "可进一步优化"},
}

# Annotation types that carry a problem, used to order comments within a turn.
ANNOTATION_WEIGHT = {"critical": 0, "needs_improvement": 1, "polish": 2,
                     "hint_given": 3, "improved": 4, "strength": 5}

DIFFICULTY_WORDS = {
    "en": {},
    "zh": {"beginner": "入门", "intermediate": "进阶", "advanced": "高阶",
           "mbb": "最高难度", "mbb-level": "最高难度"},
}

# The hiring bands are recruiting terms of art. In a Chinese report the meaning
# leads and the original follows once, which is how these are actually spoken.
VERDICT_WORDS = {
    "en": {},
    "zh": {"strong hire": "强烈建议录用（Strong Hire）", "hire": "建议录用（Hire）",
           "borderline": "临界（Borderline）", "no hire": "不建议录用（No Hire）"},
}

ROLE_WORDS = {
    "en": {"candidate": "You", "tutor": "Coach", "interviewer": "Interviewer"},
    "zh": {"candidate": "你", "tutor": "教练", "interviewer": "面试官"},
}

# Transcript tags. Free-text tags are allowed but anything recognised is
# translated; an unrecognised tag is printed as given rather than dropped.
TAG_WORDS = {
    "en": {"case prompt": "Case prompt", "structure": "Structure", "hint": "Hint",
           "retry": "Second attempt", "critical moment": "Key moment",
           "calculation": "Calculation", "exhibit": "Exhibit",
           "insight": "Insight", "synthesis": "Final summary",
           "recommendation": "Recommendation", "clarifying": "Clarifying question",
           "assistance_change": "Assistance changed", "brainstorm": "Brainstorm",
           "quant": "Calculation", "independent": "Done unaided", "opening": "Opening",
           "structure": "Structure", "new": "New this session", "repeat": "Seen before",
           "market sizing": "Market sizing", "second attempt": "Second attempt"},
    "zh": {"case prompt": "题目", "structure": "结构", "hint": "提示",
           "retry": "第二次尝试", "critical moment": "关键节点",
           "calculation": "计算", "exhibit": "图表", "insight": "洞察",
           "synthesis": "最终总结", "recommendation": "最终建议",
           "clarifying": "澄清提问", "assistance_change": "帮助强度变化",
           "brainstorm": "发散思考",
           "quant": "计算", "independent": "独立完成", "opening": "开场",
           "new": "本次新出现", "repeat": "此前已出现",
           "market sizing": "市场规模估算", "second attempt": "第二次尝试"},
}

# The six rubric dimensions are a fixed vocabulary, so their names are translated
# rather than left to whatever the report JSON happened to write.
DIMENSION_WORDS = {
    "en": {},
    "zh": {"problem structuring": "问题结构化",
           "quantitative skills": "量化分析",
           "business judgment & insight": "商业判断与洞察",
           "business judgment and insight": "商业判断与洞察",
           "exhibit interpretation": "图表解读", "exhibit 解读": "图表解读",
           "定量分析": "定量分析", "沟通": "沟通表达",
           "communication": "沟通表达",
           "synthesis / recommendation": "总结与建议",
           "synthesis/recommendation": "总结与建议"},
}


def humanise(kind, value, lang):
    """Map an internal token to natural language. Unknown values pass through."""
    if value is None:
        return None
    key = str(value).strip().lower()
    table = {"assist": ASSIST_WORDS, "hint": HINT_WORDS,
             "annotation": ANNOTATION_WORDS, "role": ROLE_WORDS,
             "tag": TAG_WORDS, "dimension": DIMENSION_WORDS,
             "difficulty": DIFFICULTY_WORDS, "verdict": VERDICT_WORDS}[kind].get(lang, {})
    if kind == "hint":
        key = HINT_ALIASES.get(key, key)
    return table.get(key, str(value))


MODE_FIELDS = {
    "interview": {
        "top": ("missed_insights", "assistance", "stronger_path",
                "recommendation_compare"),
        "session": ("interview_format",),
        "headline": (),
    },
    "tutorial": {
        "top": ("hints", "phases", "recurring_mistakes", "mastery",
                "transferable_lessons"),
        "session": ("training_focus", "assistance_start", "assistance_end",
                    "independence_marker"),
        "headline": ("benchmark_requested",),
    },
}

# Session fields both modes may carry. Listed so the split above is auditable at
# a glance: anything here is shared, anything in MODE_FIELDS is exclusive.
SHARED_SESSION_FIELDS = ("id", "date", "mode", "case_type", "industry",
                         "geography", "difficulty", "case_source", "completion",
                         "aborted_at_stage")

JSON_TYPE_NAMES = {str: "string", bool: "boolean", int: "number", float: "number",
                   list: "array", dict: "object", type(None): "null"}


def _json_type(value):
    return JSON_TYPE_NAMES.get(type(value), type(value).__name__)


def _describe(value):
    """Human-readable 'type value' for an error message; 'null' stands alone."""
    name = _json_type(value)
    return name if value is None else "{} {!r}".format(name, value)


def _article(word):
    """'an interview' / 'a tutorial' — keeps generated messages grammatical."""
    return ("an " if word[0].lower() in "aeiou" else "a ") + word

# Claims the report has no evidence for. Scanned ONLY over evaluative prose --
# the text where the skill judges the user -- never over case content, because a
# case may legitimately discuss an industry average or a conversion rate.
FABRICATION_PATTERNS = [
    (r"percentile", "percentile ranking"),
    (r"top\s*\d+\s*%", "top-N% claim"),
    (r"better than\s+\d+\s*%", "comparative ranking"),
    (r"超过\s*\d+\s*%\s*(的)?\s*(候选人|candidates|面试者)", "comparative ranking"),
    (r"(录取|通过|offer)\s*(概率|率|possibility|probability)", "offer probability"),
    (r"\b(pass|acceptance|offer)\s+rate\b", "offer probability"),
    (r"industry average\s+score", "invented benchmark"),
    (r"行业平均分", "invented benchmark"),
    (r"\b(MBB|McKinsey|BCG|Bain)\b[^.。]{0,40}\b(benchmark|平均分|baseline)\b",
     "invented firm benchmark"),
    (r"\b(benchmark)\b[^.。]{0,20}\b(is|为|是)\s*\d", "invented benchmark"),
]

# Fields whose text is an evaluation of the user. Guard rails apply here only.
EVALUATIVE_PATHS = (
    "headline.one_line_diagnosis", "headline.learning_summary",
    "dimensions[].evidence", "strengths[]", "weaknesses[]",
    "recurring_mistakes[]", "mastery", "transferable_lessons[]",
    "next_priorities[]", "assistance.summary",
    "core_feedback.*.headline", "core_feedback.*.detail",
    "annotations[].headline", "annotations[].comment", "annotations[].improvement",
    "takeaways[]",
)


class ValidationError(Exception):
    """A problem in the input data. Aborts the build; no HTML is produced."""


def _err(field, value, expected):
    raise ValidationError(
        "{} must be {}; received {!r}".format(field, expected, value))


def _check_enum(value, allowed, field, optional=True):
    if value is None:
        if optional:
            return
        _err(field, value, "one of " + ", ".join(allowed))
    if not isinstance(value, str) or value.strip().lower() not in allowed:
        _err(field, value, "one of " + ", ".join(allowed))


def _check_score(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _err(field, value, "a number between 0 and 10")
    if math.isnan(value) or math.isinf(value):
        _err(field, value, "a finite number between 0 and 10")
    if not (0 <= value <= 10):
        _err(field, value, "a finite number between 0 and 10")


def _walk_evaluative(d):
    """Yield (path, text) for every evaluative string in the document."""
    def strings(obj, path):
        if isinstance(obj, str):
            yield path, obj
        elif isinstance(obj, dict):
            for k, v in obj.items():
                yield from strings(v, "{}.{}".format(path, k))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from strings(v, "{}[{}]".format(path, i))

    head = d.get("headline") or {}
    for key in ("one_line_diagnosis", "learning_summary"):
        if head.get(key):
            yield "headline." + key, head[key]
    for i, dim in enumerate(d.get("dimensions") or []):
        if isinstance(dim, dict) and dim.get("evidence"):
            yield "dimensions[{}].evidence".format(i), dim["evidence"]
    for key in ("strengths", "weaknesses", "recurring_mistakes",
                "transferable_lessons", "next_priorities", "mastery", "phases"):
        if d.get(key):
            yield from strings(d[key], key)
    asst = d.get("assistance") or {}
    if asst.get("summary"):
        yield "assistance.summary", asst["summary"]
    # Added with the redesign: core feedback and inline comments are the most
    # prominent evaluative text on the page, so they are scanned first-class.
    core = d.get("core_feedback") or {}
    for key, item in core.items():
        if isinstance(item, dict):
            for sub in ("headline", "detail"):
                if item.get(sub):
                    yield "core_feedback.{}.{}".format(key, sub), item[sub]
    for i, ann in enumerate(d.get("annotations") or []):
        if isinstance(ann, dict):
            for sub in ("headline", "comment", "improvement"):
                if ann.get(sub):
                    yield "annotations[{}].{}".format(i, sub), ann[sub]
    for i, tk in enumerate(d.get("takeaways") or []):
        if isinstance(tk, str):
            yield "takeaways[{}]".format(i), tk


def validate(d):
    """Raise ValidationError on the first problem found. Returns the mode."""
    if not isinstance(d, dict):
        _err("document root", type(d).__name__, "a JSON object")

    session = d.get("session")
    if not isinstance(session, dict):
        _err("session", session, "an object")

    mode = session.get("mode")
    _check_enum(mode, MODES, "session.mode", optional=False)
    mode = mode.strip().lower()
    tutorial = mode == "tutorial"

    completion = session.get("completion", "complete")
    _check_enum(completion, COMPLETIONS, "session.completion", optional=False)
    completion = completion.strip().lower()

    for key in ("assistance_start", "assistance_end"):
        _check_enum(session.get(key), INDEPENDENCE, "session." + key)

    lang = d.get("language", "en")
    if lang not in L:
        _err("language", lang, "one of " + ", ".join(sorted(L)))

    # --- original prompt and user-visible session record -----------------
    case_prompt = d.get("case_prompt")
    if not isinstance(case_prompt, str) or not case_prompt.strip():
        _err("case_prompt", case_prompt, "a non-empty string containing the exact candidate-facing prompt")

    transcript = d.get("transcript")
    if not isinstance(transcript, list) or not transcript:
        _err("transcript", transcript, "a non-empty array of user-visible messages and session events")

    record_ids = set()
    for i, record in enumerate(transcript):
        base = "transcript[{}]".format(i)
        if not isinstance(record, dict):
            _err(base, record, "an object")
        unknown = set(record) - set(TRANSCRIPT_FIELDS)
        if unknown:
            _err(base, sorted(unknown), "only user-visible transcript fields: " + ", ".join(TRANSCRIPT_FIELDS))
        record_id = record.get("id")
        if not isinstance(record_id, str) or not re.match(r"^[A-Za-z][A-Za-z0-9_-]*$", record_id):
            _err(base + ".id", record_id, "a stable HTML-safe ID beginning with a letter")
        if record_id in record_ids:
            _err(base + ".id", record_id, "a unique transcript ID")
        record_ids.add(record_id)

        record_type = record.get("type")
        _check_enum(record_type, TRANSCRIPT_TYPES, base + ".type", optional=False)
        content = record.get("content")
        if not isinstance(content, str) or not content.strip():
            _err(base + ".content", content, "a non-empty string")
        for key in ("stage", "timestamp"):
            if key in record and (not isinstance(record[key], str) or not record[key].strip()):
                _err(base + "." + key, record[key], "a non-empty string")
        tags = record.get("tags")
        if tags is not None and (not isinstance(tags, list) or
                                 any(not isinstance(tag, str) or not tag.strip() for tag in tags)):
            _err(base + ".tags", tags, "an array of non-empty strings")
        _check_enum(record.get("assistance_level"), INDEPENDENCE,
                    base + ".assistance_level")

        role = record.get("role")
        if record_type == "message":
            _check_enum(role, TRANSCRIPT_ROLES, base + ".role", optional=False)
            allowed_roles = ("candidate", "tutor") if tutorial else ("candidate", "interviewer")
            if role.strip().lower() not in allowed_roles:
                _err(base + ".role", role,
                     "one of " + ", ".join(allowed_roles) + " for this mode")
        elif role is not None:
            _err(base + ".role", role, "absent for a session event")

    # Any analysis object may cite transcript records with `turn_refs`. Validate
    # recursively so a new report section cannot create a dead evidence link.
    def validate_turn_refs(obj, path=""):
        if isinstance(obj, dict):
            if "turn_refs" in obj:
                refs = obj["turn_refs"]
                field = (path + ".turn_refs").lstrip(".")
                if not isinstance(refs, list) or not refs or any(
                        not isinstance(ref, str) or not ref for ref in refs):
                    _err(field, refs, "a non-empty array of transcript IDs")
                missing = [ref for ref in refs if ref not in record_ids]
                if missing:
                    _err(field, missing, "IDs present in transcript")
            for key, value in obj.items():
                if key != "transcript":
                    validate_turn_refs(value, (path + "." + key).lstrip("."))
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                validate_turn_refs(value, "{}[{}]".format(path, i))

    validate_turn_refs(d)

    # --- dimensions -------------------------------------------------------
    dims = d.get("dimensions")
    if dims is not None and not isinstance(dims, list):
        _err("dimensions", dims, "an array")
    for i, dim in enumerate(dims or []):
        base = "dimensions[{}]".format(i)
        if not isinstance(dim, dict):
            _err(base, dim, "an object")
        if not dim.get("name"):
            _err(base + ".name", dim.get("name"), "a non-empty string")
        tested = dim.get("tested", True)
        if not isinstance(tested, bool):
            _err(base + ".tested", tested, "true or false")
        score = dim.get("score")
        if tested:
            if score is not None:
                _check_score(score, base + ".score")
        elif score is not None:
            # An untested dimension must never carry a number: rendering one would
            # assert an assessment that was never made.
            _err(base + ".score", score,
                 "null when tested is false (an untested dimension cannot hold a score)")
        _check_enum(dim.get("independence"), INDEPENDENCE, base + ".independence")

    # --- assistance -------------------------------------------------------
    asst = d.get("assistance")
    if asst is not None:
        if not isinstance(asst, dict):
            _err("assistance", asst, "an object")
        _check_enum(asst.get("level"), ASSIST_LEVELS, "assistance.level")

    # --- headline / verdict ----------------------------------------------
    head = d.get("headline")
    if head is not None and not isinstance(head, dict):
        _err("headline", head, "an object")
    head = head or {}

    verdict = head.get("verdict")
    available = head.get("verdict_available")
    overall = head.get("overall_score")
    # A JSON boolean, never a coerced truthy value. bool("false") is True in
    # Python, so accepting a string here would silently unlock the hiring verdict
    # a tutorial report must never carry.
    benchmark = head.get("benchmark_requested", False)
    if not isinstance(benchmark, bool):
        raise ValidationError(
            "headline.benchmark_requested must be a JSON boolean (true or false); "
            "received {}. Values are never coerced: a string, number or null is "
            "rejected rather than interpreted.".format(_describe(benchmark)))

    # --- mode-specific field isolation (one pass, driven by MODE_FIELDS) ---
    foreign = "tutorial" if mode == "interview" else "interview"
    for scope, container in (("top", d), ("session", session), ("headline", head)):
        for key in MODE_FIELDS[foreign][scope]:
            if container.get(key):
                path = key if scope == "top" else "{}.{}".format(scope, key)
                raise ValidationError(
                    "{} is {} field and must not appear in {} report; received "
                    "{!r}. Its presence means the report object was assembled "
                    "from the wrong template.".format(
                        path, _article(foreign) + "-only",
                        _article(mode), container.get(key)))

    if overall is not None:
        _check_score(overall, "headline.overall_score")

    if verdict is not None:
        if not isinstance(verdict, str) or verdict.strip().lower() not in HIRING_VERDICTS:
            _err("headline.verdict", verdict,
                 "one of Strong Hire, Hire, Borderline, No Hire (or null)")

    if tutorial:
        # A tutorial session is taught, hinted and retried; a hiring band asserts an
        # unassisted judgment that this session cannot support.
        if verdict is not None and not benchmark:
            raise ValidationError(
                "headline.verdict is not permitted in a tutorial report "
                "(received {!r}). A tutorial session measures learning, not hiring "
                "readiness. Set headline.benchmark_requested to true only when the "
                "user explicitly asked to be benchmarked.".format(verdict))
    else:
        if benchmark:
            _err("headline.benchmark_requested", benchmark,
                 "absent in an interview report (an interview report is already an assessment)")

        if available is not None and not isinstance(available, bool):
            _err("headline.verdict_available", available, "true or false")
        if available is False and verdict is not None:
            raise ValidationError(
                "headline.verdict must be null when headline.verdict_available is false; "
                "received {!r}. A report cannot both decline and issue a verdict.".format(verdict))
        if available is False and not head.get("verdict_unavailable_reason"):
            _err("headline.verdict_unavailable_reason", None,
                 "a non-empty explanation when verdict_available is false")
        if verdict is not None and available is False:
            _err("headline.verdict", verdict, "null when verdict_available is false")
        if completion == "aborted" and verdict is not None and available is not True:
            raise ValidationError(
                "headline.verdict is set on an aborted session without "
                "headline.verdict_available: true. An aborted case must state explicitly "
                "that enough was observed to support a verdict.")

    for key, replacement in SUPERSEDED_FIELDS.items():
        if d.get(key):
            raise ValidationError(
                "{} is no longer rendered; the turn-by-turn review carries this "
                "information now. Move it to: {}. It is rejected rather than "
                "ignored so the content is not silently lost.".format(key, replacement))

    # --- core feedback: the top-of-report block, at most three items ---
    core = d.get("core_feedback")
    if core is not None:
        if not isinstance(core, dict):
            _err("core_feedback", core, "an object")
        allowed = ("strength", "priority", "next_step")
        extra = [k for k in core if k not in allowed]
        if extra:
            _err("core_feedback", ", ".join(sorted(extra)),
                 "only " + ", ".join(allowed) + " (at most three items)")
        for key, item in core.items():
            base = "core_feedback." + key
            if not isinstance(item, dict):
                _err(base, item, "an object")
            if not item.get("headline"):
                _err(base + ".headline", item.get("headline"),
                     "a short specific claim, not a generic label")
            if not item.get("detail"):
                _err(base + ".detail", item.get("detail"),
                     "one or two sentences of concrete evidence")

    # --- transcript annotations: inline coach comments ---
    annotations = d.get("annotations")
    if annotations is not None:
        if not isinstance(annotations, list):
            _err("annotations", annotations, "an array")
        for i, a in enumerate(annotations):
            base = "annotations[{}]".format(i)
            if not isinstance(a, dict):
                _err(base, a, "an object")
            turn = a.get("turn_id")
            if not turn or turn not in record_ids:
                raise ValidationError(
                    "{}.turn_id must reference a turn that exists in transcript; "
                    "received {!r}. A comment cannot annotate a turn the session "
                    "does not contain.".format(base, turn))
            _check_enum(a.get("type"), ANNOTATION_TYPES, base + ".type", optional=False)
            if not a.get("comment"):
                _err(base + ".comment", a.get("comment"),
                     "a concrete explanation, not a verdict on its own")

    # --- takeaways: the closing three-line memory aid ---
    takeaways = d.get("takeaways")
    if takeaways is not None:
        if not isinstance(takeaways, list):
            _err("takeaways", takeaways, "an array of short strings")
        if len(takeaways) > 3:
            _err("takeaways", "{} items".format(len(takeaways)),
                 "at most 3 — the point is what survives, not a summary")
        for i, tk in enumerate(takeaways):
            if not isinstance(tk, str) or not tk.strip():
                _err("takeaways[{}]".format(i), tk, "a non-empty string")

    return mode


def check_guard_rails(d):
    """Raise ValidationError on claims the session cannot evidence."""
    hits = []
    for path, text in _walk_evaluative(d):
        for pattern, label in FABRICATION_PATTERNS:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                hits.append((path, label, m.group(0)))
    if hits:
        lines = ["Guard-rail violation: the report asserts claims this session has no "
                 "evidence for. No HTML was written."]
        for path, label, snippet in hits:
            lines.append("  - {}: {} ({!r})".format(path, label, snippet))
        lines.append("Remove the claim, or replace it with an observation from this "
                     "session, and regenerate.")
        raise ValidationError("\n".join(lines))


def esc(x):
    return html.escape(str(x), quote=True) if x is not None else ""


def para(x):
    """Escape, then honour blank-line paragraph breaks."""
    if not x:
        return ""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", str(x)) if b.strip()]
    return "".join(f"<p>{esc(b)}</p>" for b in blocks)


def band_for(score):
    if score is None:
        return None
    if score >= 8.5: return "strong"
    if score >= 7:   return "solid"
    if score >= 5:   return "developing"
    if score >= 3:   return "weak"
    return "critical"


# ------------------------------------------------------------- components ---
def score_bar(t, dim, lang="en"):
    """Meter: length carries magnitude, text carries the band. No colour-only meaning."""
    name = esc(humanise("dimension", dim.get("name"), lang))
    if not dim.get("tested", True) or dim.get("score") is None:
        return f"""<div class="dim dim--untested">
  <div class="dim__head"><span class="dim__name">{name}</span>
    <span class="dim__na">{t['not_tested']}</span></div>
  <div class="meter meter--empty"><div class="meter__track"></div></div>
  {f'<p class="dim__ev">{esc(dim.get("evidence"))}</p>' if dim.get("evidence") else ''}
{evidence_links(t, dim.get('turn_refs'))}
</div>"""

    score = float(dim["score"])
    pct = max(0.0, min(100.0, score * 10.0))
    band = dim.get("band") or t["band"][band_for(score)]
    indep = dim.get("independence")
    indep_html = f"  {independence_chip(t, indep, lang)}" if indep else ""
    return f"""<div class="dim">
  <div class="dim__head"><span class="dim__name">{name}</span>
    <span class="dim__val"><b>{score:g}</b> <span class="dim__of">{t['of10']}</span>
      <span class="dim__band">{esc(band)}</span></span></div>
  <div class="meter"><div class="meter__track"><div class="meter__fill" style="width:{pct:.1f}%"></div></div></div>
{indep_html}
  {f'<p class="dim__ev">{esc(dim.get("evidence"))}</p>' if dim.get("evidence") else ''}
{evidence_links(t, dim.get('turn_refs'))}
</div>"""


def independence_chip(t, level, lang="en"):
    """4-step ordinal indicator. Filled segments + text label; readable in greyscale."""
    key = str(level).lower()
    idx = ASSIST_ORDER.index(key) if key in ASSIST_ORDER else None
    if idx is None:
        return f'<div class="indep"><span class="indep__label">{t["independence"]}: {esc(level)}</span></div>'
    segs = "".join(
        f'<i class="seg{" seg--on" if i <= idx else ""}" style="--s:{i}"></i>' for i in range(4)
    )
    return (f'<div class="indep"><span class="indep__steps" aria-hidden="true">{segs}</span>'
            f'<span class="indep__label">{t["independence"]}: '
            f'<b>{esc(humanise("assist", key, lang))}</b></span></div>')


def hint_track(t, item):
    seq = item.get("sequence") or []
    steps = []
    for i, s in enumerate(seq):
        last = (i == len(seq) - 1)
        cls = "hstep hstep--end" if last else "hstep"
        steps.append(f'<span class="{cls}">{esc(s)}</span>')
    arrow = '<span class="harrow" aria-hidden="true">→</span>'
    return f"""<div class="hint">
  <div class="hint__topic">{esc(item.get('topic'))}</div>
  <div class="hint__seq">{arrow.join(steps)}</div>
  {f'<p class="hint__note">{esc(item.get("note"))}</p>' if item.get("note") else ''}
</div>"""


def core_feedback_block(t, core, lang):
    """The top-of-report answer to: what went well, what hurt, what to train next.

    Deliberately the visually heaviest block on the page. A reader who stops here
    should still know their most important problem and their next step.
    """
    if not core:
        return ""
    order = [("strength", "cf--good"), ("priority", "cf--work"), ("next_step", "cf--next")]
    cards = []
    for key, cls in order:
        item = core.get(key)
        if not item:
            continue
        links = evidence_links(t, item.get("turn_refs"))
        cards.append(
            '<article class="cf {cls}">'
            '<div class="cf__kind">{kind}</div>'
            '<h3 class="cf__head">{head}</h3>'
            '<p class="cf__detail">{detail}</p>{links}</article>'.format(
                cls=cls, kind=esc(t["cf_" + key]), head=esc(item.get("headline")),
                detail=esc(item.get("detail")), links=links))
    if not cards:
        return ""
    return '<div class="cfwrap">{}</div>'.format("".join(cards))


def annotation_block(t, ann, lang):
    """One coach comment, rendered beside the turn it is about.

    Written after the session by the system, never styled to look like part of the
    original conversation -- the label says so explicitly.
    """
    kind = str(ann.get("type", "")).strip().lower()
    label = humanise("annotation", kind, lang)
    cat = ann.get("category")
    head = ann.get("headline")
    cat_html = '<span class="ann__cat">{}</span>'.format(esc(cat)) if cat else ""
    head_html = '<p class="ann__head">{}</p>'.format(esc(head)) if head else ""
    imp_html = ('<p class="ann__imp">{}</p>'.format(esc(ann.get("improvement")))
                if ann.get("improvement") else "")
    return (
        '<aside class="ann ann--{k}">'
        '<div class="ann__meta"><span class="ann__badge">{label}</span>{cat}'
        '<span class="ann__src">{src}</span></div>'
        '{head}<p class="ann__body">{body}</p>{imp}</aside>'.format(
            k=esc(kind), label=esc(label), cat=cat_html, src=esc(t["ann_source"]),
            head=head_html, body=esc(ann.get("comment")), imp=imp_html))


def section(title, body, cls="", lead=""):
    if not body or not body.strip():
        return ""
    lead_html = '<p class="sec__lead">{}</p>'.format(esc(lead)) if lead else ""
    return ('<section class="sec {cls}"><h2>{title}</h2>{lead}{body}</section>'
            .format(cls=cls, title=esc(title), lead=lead_html, body=body))


def evidence_links(t, refs):
    """Stable, printable links from analysis back to the original session record."""
    if not refs:
        return ""
    links = " ".join(
        f'<a class="evidence__link" href="#{esc(ref)}">{esc(t["view_turn"])} {esc(ref)}</a>'
        for ref in refs)
    return f'<p class="evidence"><span>{esc(t["evidence"])}:</span> {links}</p>'


def kv_strip(pairs):
    cells = "".join(
        f'<div class="kv"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k, v in pairs if v
    )
    return f'<dl class="strip">{cells}</dl>' if cells else ""


def bullets(t, items, key=None):
    if not items:
        return ""
    out = []
    for it in items:
        if isinstance(it, dict):
            title = it.get("title") or it.get("label") or ""
            detail = it.get("detail") or it.get("note") or ""
            tag = it.get("status")
            tag_html = ('<span class="tag tag--{k}">{v}</span>'.format(
                k=esc(tag), v=esc(humanise("tag", tag, t.get("_lang", "en"))))
                if tag else "")
            out.append(f'<li><span class="blist__h"><b>{esc(title)}</b>{tag_html}</span>'
                       f'{para(detail)}{evidence_links(t, it.get("turn_refs"))}</li>')
        else:
            out.append(f"<li>{esc(it)}</li>")
    return f'<ul class="blist">{"".join(out)}</ul>'


def moment_block(t, m, tutorial=False):
    rows = [
        (t["what_you_did"], m.get("what_you_did")),
        (t["worked"], m.get("worked")),
        (t["problem"], m.get("problem")),
        (t["consequence"], m.get("consequence")),
        (t["stronger"], m.get("stronger")),
    ]
    if tutorial:
        rows = [
            (t["what_you_did"], m.get("what_you_did")),
            ("Hint / 教学介入" , m.get("intervention")),
            ("Retry / 第二次尝试", m.get("retry")),
            ("Learning / 学习结果", m.get("learning")),
        ]
    quote = (f'<blockquote class="quote">{esc(m.get("quote"))}</blockquote>'
             if m.get("quote") else "")
    body = "".join(f'<div class="mrow"><dt>{esc(k)}</dt><dd>{para(v)}</dd></div>'
                   for k, v in rows if v)
    return f"""<article class="moment">
  <h3>{esc(m.get('stage'))}</h3>{quote}<dl class="mgrid">{body}</dl>
  {evidence_links(t, m.get('turn_refs'))}</article>"""


def transcript_block(t, records, annotations=None, lang="en"):
    """The turn-by-turn review: the full conversation, with comments in place.

    Two rules hold this together. The transcript text is reproduced verbatim --
    never summarised, tidied, re-worded or filtered, including turns nobody
    commented on -- because its whole value is being a faithful record. And a
    comment is always a separate element with its own label, so the reader can
    never mistake post-session commentary for something said at the time.
    """
    by_turn = {}
    for ann in (annotations or []):
        by_turn.setdefault(ann["turn_id"], []).append(ann)
    for turn_anns in by_turn.values():
        turn_anns.sort(key=lambda a: ANNOTATION_WEIGHT.get(
            str(a.get("type", "")).lower(), 9))

    out = []
    for record in records:
        rid = record["id"]
        tags = "".join('<span class="tag">{}</span>'.format(
            esc(humanise("tag", tag, lang))) for tag in (record.get("tags") or []))

        if record["type"] == "event":
            stage = ('<span class="transcript__stage">{}</span>'.format(
                esc(humanise("tag", record.get("stage"), lang)))
                if record.get("stage") else "")
            assistance = record.get("assistance_level")
            assist_html = ('<span class="tag">{}</span>'.format(
                esc(humanise("assist", assistance, lang))) if assistance else "")
            out.append(
                '<div class="transcript__event" id="{rid}">'
                '<span class="transcript__id">{rid}</span>{stage}{a}'
                '<span>{c}</span></div>'.format(
                    rid=esc(rid), stage=stage, a=assist_html,
                    c=esc(record["content"])))
            continue

        role = record["role"].lower()
        stage = ('<span class="transcript__stage">{}</span>'.format(
            esc(humanise("tag", record.get("stage"), lang)))
            if record.get("stage") else "")
        anns = "".join(annotation_block(t, a, lang) for a in by_turn.get(rid, []))
        flag = " transcript__item--noted" if anns else ""
        out.append(
            '<article class="transcript__item transcript__item--{role}{flag}" id="{rid}">'
            '<header><span class="transcript__id">{rid}</span>'
            '<b>{who}</b>{stage}{tags}</header>'
            '<div class="transcript__content">{content}</div>{anns}</article>'.format(
                role=esc(role), flag=flag, rid=esc(rid),
                who=esc(humanise("role", role, lang)), stage=stage, tags=tags,
                content=esc(record["content"]), anns=anns))

    return ('<section class="sec transcript"><h2>{title}</h2>'
            '<p class="sec__lead">{lead}</p>'
            '<div class="transcript__body">'
            '<p class="privacy-note">{priv}</p>{body}</div></section>'.format(
                title=esc(t["transcript"]), lead=esc(t["transcript_lead"]),
                priv=esc(t["transcript_privacy"]), body="".join(out)))


def tree_nodes(nodes, depth=0):
    if not nodes:
        return ""
    out = []
    for n in nodes:
        kids = tree_nodes(n.get("children"), depth + 1)
        detail = f'<span class="tnode__d">{esc(n.get("detail"))}</span>' if n.get("detail") else ""
        out.append(f'<li><span class="tnode__l">{esc(n.get("label"))}</span>{detail}{kids}</li>')
    return f'<ul class="tree tree--d{min(depth,3)}">{"".join(out)}</ul>'


# ------------------------------------------------------------------- CSS ----
CSS = """
:root{color-scheme:light;
--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--rule:#e1e0d9;--axis:#c3c2b7;--ring:rgba(11,11,11,.10);
--fill:#2a78d6;--track:#cde2fb;
--o1:#86b6ef;--o2:#5598e7;--o3:#2a78d6;--o4:#104281;
--good:#0ca30c;--warn:#fab219;--crit:#d03b3b;}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme=light])){
color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--muted:#898781;
--rule:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);
--fill:#3987e5;--track:#184f95;
--o1:#184f95;--o2:#256abf;--o3:#3987e5;--o4:#9ec5f4;}}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);
font:16px/1.55 system-ui,-apple-system,"Segoe UI","Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif;
-webkit-font-smoothing:antialiased}
.wrap{max-width:52rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}
h1{font-size:1.6rem;line-height:1.25;margin:0 0 .3rem;letter-spacing:-.01em}
h2{font-size:1.05rem;margin:0 0 .9rem;letter-spacing:.01em;text-transform:uppercase;
color:var(--ink2);font-weight:650}
h3{font-size:1rem;margin:0 0 .5rem}
p{margin:0 0 .6rem}
.sub{color:var(--ink2);margin:0 0 1.4rem;font-size:.95rem}
.sec{background:var(--surface);border:1px solid var(--ring);border-radius:10px;
padding:1.4rem 1.5rem;margin:0 0 1rem}
.hero{padding:1.6rem 1.5rem}
.badge{display:inline-block;font-size:.78rem;font-weight:650;letter-spacing:.03em;
padding:.22rem .55rem;border-radius:4px;border:1px solid var(--ring);margin-left:.5rem;vertical-align:2px}
.badge--ok{background:var(--track);color:var(--ink)}
.badge--warn{background:transparent;border-color:var(--crit);color:var(--crit)}
.strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(8.5rem,1fr));
gap:.85rem 1.2rem;margin:0 0 1.2rem;padding:0}
.kv dt{font-size:.72rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin:0 0 .12rem}
.kv dd{margin:0;font-size:.94rem;font-weight:600}
.result{display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap;
border-top:1px solid var(--rule);padding-top:1.1rem;margin-top:.2rem}
.result__score{font-size:2.9rem;font-weight:680;line-height:1;letter-spacing:-.02em}
.result__of{font-size:1rem;color:var(--muted);font-weight:400}
.result__verdict{font-size:1.35rem;font-weight:650}
.result__none{font-size:1.05rem;font-weight:600;color:var(--crit);line-height:1.4}
.note{font-size:.85rem;color:var(--ink2);margin:.5rem 0 0;
border-left:3px solid var(--axis);padding-left:.7rem}
.lede{font-size:1.06rem;line-height:1.6;margin:1.1rem 0 0;padding-top:1rem;
border-top:1px solid var(--rule)}
.case-prompt__text{white-space:pre-wrap;font-size:.96rem;line-height:1.65;margin:0}
.evidence{font-size:.78rem;color:var(--muted);margin:.4rem 0 0}
.evidence__link{display:inline-block;color:var(--fill);font-weight:650;text-decoration:none;
border-bottom:1px solid currentColor;margin-right:.35rem}
.evidence__link:focus,.evidence__link:hover{outline:2px solid var(--track);outline-offset:2px}
.dim{padding:.7rem 0;border-bottom:1px solid var(--rule)}
.dim:last-child{border-bottom:0}
.dim__head{display:flex;justify-content:space-between;align-items:baseline;gap:1rem;margin:0 0 .38rem}
.dim__name{font-weight:600}
.dim__val b{font-size:1.05rem;font-variant-numeric:tabular-nums}
.dim__of{color:var(--muted);font-size:.85rem}
.dim__band{margin-left:.5rem;font-size:.85rem;color:var(--ink2)}
.dim__na{font-size:.85rem;color:var(--muted);font-style:italic}
.dim__ev{font-size:.88rem;color:var(--ink2);margin:.42rem 0 0}
.meter__track{height:8px;border-radius:4px;background:var(--track);overflow:hidden}
.meter--empty .meter__track{background:transparent;border:1px dashed var(--axis);height:8px}
.meter__fill{height:100%;background:var(--fill);border-radius:4px;
box-shadow:inset 0 0 0 1px rgba(0,0,0,.16)}
.indep{display:flex;align-items:center;gap:.5rem;margin:.42rem 0 0}
.indep__steps{display:inline-flex;gap:2px}
.seg{width:14px;height:8px;border-radius:2px;background:transparent;
border:1px solid var(--axis);display:inline-block}
.seg--on{border-color:transparent}
.seg--on[style*="--s:0"]{background:var(--o1)}
.seg--on[style*="--s:1"]{background:var(--o2)}
.seg--on[style*="--s:2"]{background:var(--o3)}
.seg--on[style*="--s:3"]{background:var(--o4)}
.indep__label{font-size:.83rem;color:var(--ink2)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
.blist{margin:0;padding-left:1.05rem}
.blist li{margin:0 0 .8rem}
.blist__h{display:flex;align-items:baseline;gap:.45rem;flex-wrap:wrap;margin:0 0 .18rem}
.blist li b{font-weight:650}
.blist li p{font-size:.93rem;color:var(--ink2);margin:0 0 .35rem}
.tag{display:inline-block;font-size:.68rem;letter-spacing:.04em;text-transform:uppercase;
border:1px solid var(--ring);border-radius:3px;padding:.05rem .35rem;color:var(--ink2);white-space:nowrap}
.moment{border-top:1px solid var(--rule);padding:1rem 0 .3rem}
.moment:first-of-type{border-top:0;padding-top:0}
.mgrid{margin:0}
.mrow{display:grid;grid-template-columns:9.5rem 1fr;gap:.3rem 1rem;margin:0 0 .5rem}
.mrow dt{font-size:.76rem;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);padding-top:.18rem}
.mrow dd{margin:0;font-size:.94rem}
.mrow dd p{margin:0 0 .4rem}
.quote{margin:0 0 .8rem;padding:.45rem .8rem;border-left:3px solid var(--o2);
background:var(--page);font-style:italic;color:var(--ink2);font-size:.93rem;border-radius:0 4px 4px 0}
.hint{padding:.65rem 0;border-bottom:1px solid var(--rule)}
.hint:last-child{border-bottom:0}
.hint__topic{font-weight:600;margin:0 0 .35rem}
.hint__seq{display:flex;align-items:center;gap:.4rem;flex-wrap:wrap}
.hstep{font-size:.83rem;border:1px solid var(--axis);border-radius:4px;padding:.13rem .5rem;color:var(--ink2)}
.hstep--end{border-color:transparent;background:var(--o4);color:#fff;font-weight:600}
.harrow{color:var(--muted);font-size:.85rem}
.hint__note{font-size:.88rem;color:var(--ink2);margin:.35rem 0 0}
.phase{border:1px solid var(--ring);border-radius:8px;padding:1rem 1.1rem;background:var(--page)}
.phase h3{margin:0 0 .6rem;font-size:.95rem}
.phase dt{font-size:.74rem;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);margin:.55rem 0 .1rem}
.phase dd{margin:0;font-size:.93rem}
.marker{font-size:.85rem;color:var(--ink2);margin:0 0 .9rem;padding:.45rem .7rem;
border:1px dashed var(--axis);border-radius:6px}
.tree{list-style:none;margin:.2rem 0 0;padding:0 0 0 .1rem}
.tree ul{margin:.3rem 0 .3rem .2rem;padding:0 0 0 1rem;border-left:1px solid var(--axis)}
.tree li{margin:.3rem 0;padding:0 0 0 .1rem}
.tnode__l{font-weight:600;font-size:.94rem}
.tnode__d{display:block;font-size:.88rem;color:var(--ink2)}
.rec{border:1px solid var(--ring);border-radius:8px;padding:.9rem 1.05rem;margin:0 0 .8rem;background:var(--page)}
.rec h3{font-size:.8rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin:0 0 .45rem}
.rec--strong{border-left:3px solid var(--o3)}
.issue{display:grid;grid-template-columns:12rem 1fr;gap:.25rem 1rem;margin:0 0 .45rem;font-size:.92rem}
.issue dt{color:var(--ink2)}
.issue dd{margin:0}
.pri{border-top:1px solid var(--rule);padding:.95rem 0 .2rem}
.pri:first-of-type{border-top:0;padding-top:0}
.pri h3{margin:0 0 .5rem}
.transcript__body{padding:0}
.privacy-note{font-size:.82rem;color:var(--ink2);border-left:3px solid var(--axis);
padding-left:.7rem;margin:0 0 1rem}
.transcript__item{border:1px solid var(--ring);border-radius:7px;padding:.75rem .9rem;
margin:0 0 .65rem;background:var(--page);scroll-margin-top:1rem}
.transcript__item--candidate{border-left:3px solid var(--o3)}
.transcript__item header{display:flex;align-items:center;gap:.45rem;flex-wrap:wrap;margin:0 0 .35rem;
font-size:.8rem;color:var(--ink2)}
.transcript__id{font-variant-numeric:tabular-nums;font-weight:700;color:var(--fill)}
.transcript__stage{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.transcript__content{white-space:pre-wrap;font-size:.93rem;line-height:1.6}
.transcript__event{display:flex;align-items:center;gap:.45rem;flex-wrap:wrap;margin:.9rem 0;
padding:.55rem .75rem;border:1px dashed var(--axis);border-radius:6px;color:var(--ink2);font-size:.84rem;
scroll-margin-top:1rem}
/* --- section lead + prominence tiers ------------------------------------ */
.sec__lead{font-size:.88rem;color:var(--ink2);margin:-.35rem 0 1rem}
.sec--lead{border-color:var(--o3);border-width:1px;box-shadow:0 1px 0 var(--ring)}
.sec--lead>h2{color:var(--ink);font-size:1.15rem;text-transform:none;letter-spacing:0}
.sec--compact .dim{padding:.55rem 0}
.sec--compact .dim__ev{margin:.3rem 0 0}
.sec--takeaway{background:var(--page);border-style:solid}

/* --- core feedback ------------------------------------------------------ */
.cfwrap{display:grid;gap:.7rem}
.cf{border:1px solid var(--ring);border-left:4px solid var(--axis);border-radius:8px;
padding:.9rem 1.1rem;background:var(--page)}
.cf--good{border-left-color:var(--o3)}
.cf--work{border-left-color:var(--crit)}
.cf--next{border-left-color:var(--o1)}
.cf__kind{font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;
color:var(--muted);margin:0 0 .3rem;font-weight:650}
.cf__head{font-size:1.05rem;margin:0 0 .35rem;line-height:1.35}
.cf__detail{font-size:.95rem;line-height:1.6;margin:0;color:var(--ink)}
.cf .evidence{margin-top:.5rem}

/* --- inline coach comments --------------------------------------------- */
.ann{margin:.7rem 0 0;padding:.65rem .85rem;border-radius:6px;
background:var(--surface);border:1px solid var(--ring);border-left:3px solid var(--axis)}
.ann--strength{border-left-color:var(--good)}
.ann--improved{border-left-color:var(--good)}
.ann--needs_improvement{border-left-color:var(--warn)}
.ann--critical{border-left-color:var(--crit)}
.ann--hint_given{border-left-color:var(--o2)}
.ann--polish{border-left-color:var(--axis)}
.ann__meta{display:flex;align-items:baseline;gap:.45rem;flex-wrap:wrap;margin:0 0 .3rem}
.ann__badge{font-size:.75rem;font-weight:700;letter-spacing:.02em}
.ann__cat{font-size:.75rem;color:var(--ink2)}
.ann__src{font-size:.68rem;color:var(--muted);text-transform:uppercase;
letter-spacing:.05em;margin-left:auto}
.ann__head{font-size:.92rem;font-weight:650;margin:0 0 .25rem;line-height:1.45}
.ann__body{font-size:.9rem;line-height:1.6;margin:0;color:var(--ink2)}
.ann__imp{font-size:.9rem;line-height:1.6;margin:.4rem 0 0;color:var(--ink2);
padding-left:.7rem;border-left:2px solid var(--rule)}
.transcript__item--noted{background:var(--surface)}

/* --- takeaways ---------------------------------------------------------- */
.takeaways{margin:0;padding-left:1.3rem}
.takeaways li{margin:0 0 .55rem;font-size:1rem;line-height:1.6}
.takeaways li::marker{font-weight:700;color:var(--fill)}

.foot{color:var(--muted);font-size:.8rem;margin:1.6rem 0 0;text-align:center}
@media (max-width:640px){
.wrap{padding:1.5rem .9rem 3rem}.cols{grid-template-columns:1fr}
.mrow{grid-template-columns:1fr;gap:.1rem}.issue{grid-template-columns:1fr;gap:.05rem}
.result__score{font-size:2.3rem}}
@media print{
:root{color-scheme:light !important;--page:#fff;--surface:#fff;--ink:#000;--ink2:#333;
--rule:#ddd;--axis:#999;--ring:#ccc;--fill:#2a78d6;--track:#e6eef8}
*{-webkit-print-color-adjust:exact;print-color-adjust:exact}
@page{size:A4;margin:14mm}
body{font-size:10.5pt;background:#fff}
.wrap{max-width:none;padding:0}
.sec{border:1px solid #ddd;margin:0 0 8pt;padding:10pt 12pt}
h2,h3{break-after:avoid;page-break-after:avoid}
.hero{break-inside:avoid;page-break-inside:avoid}
.cols>div{break-inside:avoid;page-break-inside:avoid}
.moment,.pri,.hint,.dim{break-inside:avoid;page-break-inside:avoid}
.transcript__body{display:block!important;padding:0}
.cf,.ann,.takeaways li{break-inside:avoid;page-break-inside:avoid}
.sec--lead{border-width:1px}
.transcript__item,.transcript__event{break-inside:avoid;page-break-inside:avoid}
h2{font-size:9pt}.foot{margin-top:10pt}
.hstep--end{background:#104281 !important;color:#fff !important}}
"""


# --------------------------------------------------------------- assembly ---
def build(d):
    lang = d.get("language", "en")
    t = dict(L.get(lang, L["en"]))
    t["_lang"] = lang
    s = d.get("session", {})
    mode = s.get("mode", "interview")
    tutorial = (mode == "tutorial")
    head = d.get("headline", {}) or {}

    # Validation and guard rails already ran (see main); build() renders only
    # data that has been accepted. Nothing is silently dropped here.
    completion = s.get("completion", "complete")

    title = t["tutorial_title"] if tutorial else t["interview_title"]
    subq = t["tutorial_q"] if tutorial else t["interview_q"]

    # --- hero --------------------------------------------------------------
    badge_cls, badge_txt = ("badge--ok", t["complete"])
    if completion == "aborted":
        badge_cls, badge_txt = "badge--warn", t["aborted"]
    elif completion == "partial":
        badge_cls, badge_txt = "badge--warn", t["partial"]
    if completion == "aborted" and s.get("aborted_at_stage"):
        badge_txt = f'{badge_txt} · {s["aborted_at_stage"]}'

    pairs = [(t["case_type"], s.get("case_type")), (t["industry"], s.get("industry")),
             (t["geography"], s.get("geography")), (t["difficulty"], humanise("difficulty", s.get("difficulty"), lang))]
    if tutorial:
        pairs += [(t["focus"], s.get("training_focus")),
                  (t["assist_start"], humanise("assist", s.get("assistance_start"), lang)),
                  (t["assist_end"], humanise("assist", s.get("assistance_end"), lang))]
    else:
        fmt = s.get("interview_format")
        fmt = t["fmt_" + str(fmt)] if ("fmt_" + str(fmt)) in t else fmt
        pairs += [(t["format"], fmt),
                  (t["assistance"], t["assist_lv"].get(
                      str((d.get("assistance") or {}).get("level")).lower(),
                      (d.get("assistance") or {}).get("level")))]

    result = ""
    if not tutorial:
        if head.get("verdict"):
            sc = head.get("overall_score")
            sc_html = (f'<span class="result__score">{float(sc):g}</span>'
                       f'<span class="result__of">{t["of10"]}</span>' if sc is not None else "")
            result = (f'<div class="result">{sc_html}'
                      f'<span class="result__verdict">'
                      f'{esc(humanise("verdict", head["verdict"], lang))}</span></div>')
        else:
            reason = head.get("verdict_unavailable_reason") or ""
            result = (f'<div class="result"><span class="result__none">{t["no_verdict"]}</span></div>'
                      + (f'<p class="note">{esc(reason)}</p>' if reason else ""))
    elif head.get("verdict") and head.get("benchmark_requested"):
        result = (f'<div class="result"><span class="result__verdict">'
                  f'{esc(humanise("verdict", head["verdict"], lang))}</span></div>'
                  f'<p class="note">{t["benchmark_note"]}</p>')

    lede = head.get("one_line_diagnosis") or head.get("learning_summary")
    lede_html = f'<p class="lede">{esc(lede)}</p>' if lede else ""

    hero = f"""<section class="sec hero">
  <h1>{esc(title)}<span class="badge {badge_cls}">{esc(badge_txt)}</span></h1>
  <p class="sub">{esc(subq)}</p>
  {kv_strip(pairs)}
</section>"""

    prompt_html = section(
        t["case_prompt"],
        f'<div class="case-prompt__text">{esc(d["case_prompt"])}</div>',
        "case-prompt")
    summary_html = section(t["session_summary"], result + lede_html, "summary")
    body = [hero, prompt_html, summary_html]

    # --- core feedback: deliberately the heaviest block on the page --------
    core_html = core_feedback_block(t, d.get("core_feedback"), lang)
    if core_html:
        body.append(section(t["cf_head"], core_html, cls="sec--lead", lead=t["cf_lead"]))

    # --- capability overview: compact. The detail lives in the transcript --
    dims = d.get("dimensions") or []
    if dims:
        body.append(section(t["overview_h"],
                            "".join(score_bar(t, x, lang) for x in dims),
                            cls="sec--compact", lead=t["overview_lead"]))

    # --- the turn-by-turn review, with comments in place ------------------
    body.append(transcript_block(t, d["transcript"], d.get("annotations"), lang))

    # --- what is established, versus what is not --------------------------
    if tutorial:
        mas = d.get("mastery") or {}
        rm = d.get("recurring_mistakes") or []
        # A recurring mistake IS something that still needs support. Listing it
        # in its own section made one finding look like two.
        needs = list(mas.get("needs_help") or []) + list(rm)
        if mas.get("independent") or needs:
            left = ('<div><h3>{}</h3>{}</div>'.format(
                esc(t["mastery_yes"]), bullets(t, mas.get("independent")))
                if mas.get("independent") else "")
            right = ('<div><h3>{}</h3>{}</div>'.format(
                esc(t["mastery_no"]), bullets(t, needs)) if needs else "")
            body.append(section(t["mastery_h"],
                                '<div class="cols">{}{}</div>'.format(left, right),
                                lead=t["mastery_lead"]))
    else:
        mi = d.get("missed_insights") or []
        if mi:
            rows = []
            for m in mi:
                pairs2 = [(t["evidence_avail"], m.get("evidence_available")),
                          (t["stopped"], m.get("where_you_stopped")),
                          (t["should"], m.get("should_have_concluded")),
                          (t["why_matters"], m.get("why_it_matters"))]
                inner = "".join(
                    '<div class="mrow"><dt>{}</dt><dd>{}</dd></div>'.format(esc(k), para(v))
                    for k, v in pairs2 if v)
                rows.append(
                    '<article class="moment"><h3>{}</h3><dl class="mgrid">{}</dl>{}</article>'
                    .format(esc(m.get("title")), inner,
                            evidence_links(t, m.get("turn_refs"))))
            body.append(section(t["missed"], "".join(rows)))

        rc = d.get("recommendation_compare") or {}
        if rc.get("yours") or rc.get("stronger"):
            blocks = ""
            if rc.get("yours"):
                blocks += '<div class="rec"><h3>{}</h3>{}</div>'.format(
                    esc(t["your_rec"]), para(rc["yours"]))
            if rc.get("issues"):
                iss = "".join('<div class="issue"><dt>{}</dt><dd>{}</dd></div>'.format(
                    esc(i.get("criterion")), esc(i.get("note"))) for i in rc["issues"])
                blocks += '<div class="rec"><h3>{}</h3>{}</div>'.format(
                    esc(t["rec_issues"]), iss)
            if rc.get("stronger"):
                blocks += '<div class="rec rec--strong"><h3>{}</h3>{}</div>'.format(
                    esc(t["stronger_rec"]), para(rc["stronger"]))
            body.append(section(t["rec_compare"], blocks))

    # --- next training plan -----------------------------------------------
    np_ = d.get("next_priorities") or []
    if np_:
        rows = []
        for pr in np_:
            kk = [(t["current"], pr.get("current")), (t["why"], pr.get("why")),
                  (t["target"], pr.get("target")), (t["drill"], pr.get("drill")),
                  (t["assist_for_drill"], pr.get("assistance"))]
            inner = "".join(
                '<div class="mrow"><dt>{}</dt><dd>{}</dd></div>'.format(esc(k), para(v))
                for k, v in kk if v)
            rows.append('<div class="pri"><h3>{}</h3><dl class="mgrid">{}</dl></div>'.format(
                esc(pr.get("title")), inner))
        body.append(section(t["next_plan"] if tutorial else t["next"], "".join(rows)))

    # --- the closing memory aid -------------------------------------------
    tk = d.get("takeaways") or []
    if tk:
        items = "".join('<li>{}</li>'.format(esc(x)) for x in tk)
        body.append(section(t["takeaways_h"],
                            '<ol class="takeaways">{}</ol>'.format(items),
                            cls="sec--takeaway"))

    stamp = s.get("date") or datetime.date.today().isoformat()
    sid = s.get("id") or ""
    foot = f'<p class="foot">{t["generated"]} {esc(stamp)}{" · " + esc(sid) if sid else ""}</p>'

    doc = f"""<!doctype html>
<html lang="{ 'zh-CN' if lang=='zh' else 'en' }">
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<style>{CSS}</style></head>
<body><main class="wrap">
{''.join(body)}
{foot}
</main></body></html>"""
    return doc


def resolve_input(args):
    """Resolve the input path from --example or a positional path."""
    if args.example:
        path = os.path.join(EXAMPLES_DIR, "{}-report.json".format(args.example))
        if not os.path.exists(path):
            raise SystemExit(
                "error: bundled example not found at {}\n"
                "The skill directory may be incomplete; re-clone it.".format(path))
        return path
    if not args.json_path:
        raise SystemExit("error: give a report JSON path, or --example interview|tutorial")
    return args.json_path


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Render a Session Report JSON into a self-contained HTML file.",
        epilog="Paths resolve from the script's own location, so an absolute "
               "invocation works from any working directory.")
    ap.add_argument("json_path", nargs="?", help="path to a Session Report JSON file")
    ap.add_argument("--example", choices=("interview", "tutorial"),
                    help="render a bundled example instead of a file (smoke test)")
    ap.add_argument("-o", "--out", required=True, help="output HTML path")
    ap.add_argument("--skill-root", action="store_true",
                    help="print the resolved skill directory and exit")
    args = ap.parse_args(argv)

    if args.skill_root:
        print(SKILL_ROOT)
        return 0

    path = resolve_input(args)

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("error: no such file: {}".format(path), file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print("error: {} is not valid JSON: {}".format(path, e), file=sys.stderr)
        return 1

    try:
        validate(data)
        check_guard_rails(data)
    except ValidationError as e:
        print("ValidationError: {}".format(e), file=sys.stderr)
        print("No HTML was written.", file=sys.stderr)
        return 2

    doc = build(data)
    try:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(doc)
    except OSError as e:
        print("error: could not write {}: {}".format(args.out, e), file=sys.stderr)
        return 1

    print("Wrote {} ({:,} bytes)".format(args.out, len(doc)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
