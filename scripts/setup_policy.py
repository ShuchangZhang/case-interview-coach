#!/usr/bin/env python3
"""Executable policy model for the adaptive pre-session setup.

The conversational model still parses the full request. This module pins the
high-risk intent boundary (whether wording explicitly chooses a Session Kind)
and answers which material setup dimensions still need the user's decision.

It is intentionally small and standard-library only. The skill does not need to
invoke it during every session; it exists as a reproducible policy oracle for
tests, audits, and future setup changes.
"""

import argparse
import json
import re
import sys


MODES = ("interview", "tutorial")
SESSION_KINDS = ("full_case", "focused_drill", "beginner_curriculum")
FORMAT_VALUES = ("interviewee_led", "interviewer_led")
RANDOM_FIELDS = ("case_type", "geography", "interview_format")
DIFFICULTIES = ("beginner", "intermediate", "advanced", "mbb")
DEFAULT_DIFFICULTY = "intermediate"
DEFAULT_DRILL_REPS = 3


DIFFICULTY_ALIASES = {
    "beginner": "beginner", "入门": "beginner", "初级": "beginner",
    "简单": "beginner", "easy": "beginner",
    "intermediate": "intermediate", "中等": "intermediate",
    "中级": "intermediate", "medium": "intermediate",
    "advanced": "advanced", "高阶": "advanced", "高难度": "advanced",
    "hard": "advanced",
    "mbb": "mbb", "mbb-level": "mbb", "mbb level": "mbb",
    "最高难度": "mbb",
}

DIFFICULTY_LABELS = {
    "en": {
        "beginner": "Beginner", "intermediate": "Intermediate",
        "advanced": "Advanced", "mbb": "MBB-level",
    },
    "zh": {
        "beginner": "入门", "intermediate": "中等",
        "advanced": "高难度（Advanced）", "mbb": "最高难度（MBB-level）",
    },
}


def _normalise(text):
    return " ".join(str(text or "").strip().casefold().split())


def _canonical_difficulty(value):
    """Return one canonical difficulty enum, or ``None`` when not recognised."""
    normalised = _normalise(value)
    if not normalised:
        return None
    if normalised in DIFFICULTY_ALIASES:
        return DIFFICULTY_ALIASES[normalised]
    # Long natural-language requests are deliberately matched from most to least
    # specific so "MBB-level" cannot collapse to a generic hard request.
    for phrase in ("mbb-level", "mbb level", "最高难度", "mbb"):
        if phrase in normalised:
            return "mbb"
    for phrase in ("advanced", "高难度", "高阶", "final round"):
        if phrase in normalised:
            return "advanced"
    for phrase in ("intermediate", "中等", "中级"):
        if phrase in normalised:
            return "intermediate"
    for phrase in ("beginner", "入门", "初级", "第一次练", "first time"):
        if phrase in normalised:
            return "beginner"
    return None


def _move_difficulty(value, steps):
    index = DIFFICULTIES.index(value)
    return DIFFICULTIES[max(0, min(len(DIFFICULTIES) - 1, index + steps))]


def _scoped_difficulty_modifiers(request):
    """Extract dimension-only requests that must not flatten into overall level."""
    modifiers = {}
    harder = any(marker in request for marker in
                 ("难一点", "更难", "提高难度", "harder", "more difficult"))
    easier = any(marker in request for marker in
                 ("别太难", "简单一点", "容易一点", "降低难度",
                  "easier", "less difficult", "not too hard"))
    if any(marker in request for marker in ("图表", "exhibit")) and harder:
        modifiers["exhibit"] = "harder"
    if any(marker in request for marker in ("计算", "数学", "math", "quant")):
        if easier:
            modifiers["math"] = "easier"
        elif harder:
            modifiers["math"] = "harder"
    if any(marker in request for marker in
           ("商业判断", "商业洞察", "business judgment", "business judgement")):
        if harder:
            modifiers["business_judgment"] = "harder"
        elif easier:
            modifiers["business_judgment"] = "easier"
    return modifiers


def resolve_difficulty(requested=None, profile_level=None, current=None):
    """Resolve difficulty with user intent above profile above a stable default.

    The return value carries provenance so a Session Summary can explain an
    automatic choice without exposing profile details. Relative user requests are
    applied to the current level, then the profile level, then Intermediate.
    """
    profile = _canonical_difficulty(profile_level)
    existing = _canonical_difficulty(current)
    baseline = existing or profile or DEFAULT_DIFFICULTY
    request = _normalise(requested)

    if request:
        scoped = _scoped_difficulty_modifiers(request)
        if scoped:
            explicit = _canonical_difficulty(request)
            return {"value": explicit or baseline, "source": "user",
                    "modifiers": scoped}
        if any(marker in request for marker in
               ("难一点", "更难", "提高难度", "harder", "more difficult")):
            return {"value": _move_difficulty(baseline, 1), "source": "user"}
        if any(marker in request for marker in
               ("简单一点", "容易一点", "降低难度", "easier", "less difficult")):
            return {"value": _move_difficulty(baseline, -1), "source": "user"}
        explicit = _canonical_difficulty(request)
        if explicit:
            return {"value": explicit, "source": "user"}
        raise ValueError("unrecognised difficulty request: " + str(requested))

    if profile:
        return {"value": profile, "source": "profile"}
    return {"value": DEFAULT_DIFFICULTY, "source": "default"}


def resolve_industry(requested=None, automatic=None, applicable=True):
    """Resolve an applicable industry without adding a setup question."""
    if not applicable:
        return {"value": None, "source": None}
    explicit = str(requested or "").strip()
    if explicit:
        return {"value": explicit, "source": "user"}
    selected = str(automatic or "").strip()
    if not selected:
        raise ValueError("an applicable generated case needs an automatic industry")
    return {"value": selected, "source": "automatic"}


def resolve_defaults(context, profile_level=None, automatic_industry=None):
    """Return Session state with all applicable visible defaults resolved.

    This does not ask questions. The conversational layer first resolves training
    structure with ``missing_setup``; this function then fills the case-flavour
    values that must be shown before formal start.
    """
    resolved = dict(context)
    kind = resolved.get("session_kind")

    difficulty_applicable = resolved.get("difficulty_applicable")
    if difficulty_applicable is None:
        difficulty_applicable = kind != "beginner_curriculum"
    if difficulty_applicable:
        difficulty_source = resolved.get("difficulty_source")
        if difficulty_source in ("default", "profile") and resolved.get("difficulty"):
            # Already resolved in this setup pass; do not reinterpret it as a
            # fresh user request or silently change it on a second render.
            difficulty = {"value": resolved["difficulty"], "source": difficulty_source}
        else:
            requested = resolved.get("difficulty") if difficulty_source in (None, "user") else None
            difficulty = resolve_difficulty(requested=requested,
                                            profile_level=profile_level)
        resolved["difficulty"] = difficulty["value"]
        resolved["difficulty_source"] = difficulty["source"]
        if difficulty.get("modifiers"):
            resolved["difficulty_modifiers"] = difficulty["modifiers"]
    else:
        resolved["difficulty"] = None
        resolved["difficulty_source"] = None

    industry_applicable = resolved.get("industry_applicable")
    if industry_applicable is None:
        industry_applicable = kind == "full_case"
    industry_source = resolved.get("industry_source")
    if (industry_applicable and industry_source == "automatic" and
            resolved.get("industry")):
        industry = {"value": resolved["industry"], "source": "automatic"}
    else:
        requested_industry = (resolved.get("industry")
                              if industry_source in (None, "user") else None)
        industry = resolve_industry(requested_industry, automatic_industry,
                                    applicable=industry_applicable)
    resolved["industry"] = industry["value"]
    resolved["industry_source"] = industry["source"]

    if kind == "focused_drill":
        reps = resolved.get("planned_reps")
        if reps is None:
            reps = DEFAULT_DRILL_REPS
            resolved["planned_reps_source"] = "default"
        else:
            if isinstance(reps, bool) or not isinstance(reps, int) or reps <= 0:
                raise ValueError("planned_reps must be a positive integer")
            resolved["planned_reps_source"] = "user"
        resolved["planned_reps"] = reps
    return resolved


def apply_prestart_updates(context, **updates):
    """Apply local edits from the visible summary without reopening setup."""
    if context.get("formal_started"):
        raise ValueError("setup is locked after the session formally starts")
    allowed = {"difficulty", "industry", "planned_reps"}
    unknown = set(updates) - allowed
    if unknown:
        raise ValueError("not a resolved-default update: " + ", ".join(sorted(unknown)))

    updated = dict(context)
    if "difficulty" in updates:
        result = resolve_difficulty(updates["difficulty"],
                                    current=context.get("difficulty"))
        updated["difficulty"] = result["value"]
        updated["difficulty_source"] = "user"
        if result.get("modifiers"):
            updated["difficulty_modifiers"] = result["modifiers"]
        else:
            updated.pop("difficulty_modifiers", None)
    if "industry" in updates:
        result = resolve_industry(updates["industry"], applicable=True)
        updated["industry"] = result["value"]
        updated["industry_source"] = "user"
    if "planned_reps" in updates:
        reps = updates["planned_reps"]
        if isinstance(reps, bool) or not isinstance(reps, int) or reps <= 0:
            raise ValueError("planned_reps must be a positive integer")
        updated["planned_reps"] = reps
        updated["planned_reps_source"] = "user"
    return updated


def _humanise(value, language, labels=None):
    if value is None:
        return None
    if labels and value in labels.get(language, {}):
        return labels[language][value]
    return str(value).replace("_", " ").strip()


def session_summary(context, language="en"):
    """Render the concise, editable contract immediately before formal start."""
    lang = "zh" if language == "zh" else "en"
    kind = context.get("session_kind")
    mode = context.get("mode")
    case_type_labels = {
        "en": {
            "profitability": "Profitability", "market_entry": "Market Entry",
            "market entry": "Market Entry", "market_sizing": "Market Sizing",
            "market sizing": "Market Sizing", "pricing": "Pricing",
            "exhibit interpretation": "Exhibit interpretation",
            "mental math": "Mental math", "case math": "Case math",
        },
        "zh": {
            "profitability": "盈利能力", "market_entry": "市场进入",
            "market entry": "市场进入", "market_sizing": "市场规模估算",
            "market sizing": "市场规模估算", "pricing": "定价",
            "exhibit interpretation": "图表解读", "mental math": "心算",
            "case math": "案例计算",
        },
    }
    format_labels = {
        "en": {"interviewee_led": "You drive", "interviewer_led": "Interviewer/Tutor-led"},
        "zh": {"interviewee_led": "候选人主导", "interviewer_led": "面试官／导师主导"},
    }
    assistance_labels = {
        "en": {"guided": "Guided", "assisted": "Assisted",
               "light": "Light assistance", "independent": "Independent"},
        "zh": {"guided": "引导练习", "assisted": "适度提示",
               "light": "轻度提示", "independent": "独立完成"},
    }

    topic = context.get("training_focus") if kind == "focused_drill" else context.get("case_type")
    first_line = [context.get("geography"),
                  _humanise(topic, lang, case_type_labels),
                  context.get("industry")]
    difficulty = context.get("difficulty")
    if difficulty:
        first_line.append(DIFFICULTY_LABELS[lang].get(difficulty, _humanise(difficulty, lang)))

    if kind == "focused_drill":
        second_line = [("Focused drill" if lang == "en" else "专项练习"),
                       (("{} reps" if lang == "en" else "共 {} 题")
                        .format(context.get("planned_reps", DEFAULT_DRILL_REPS))),
                       _humanise(context.get("assistance_level"), lang, assistance_labels)]
        timing = ("You may continue or end after each rep; one combined HTML report follows the session."
                  if lang == "en" else
                  "每题结束后都可以继续或提前结束；Session 结束后生成综合 HTML 报告。")
    elif kind == "beginner_curriculum":
        second_line = [("Beginner lesson" if lang == "en" else "基础教学"),
                       _humanise(context.get("assistance_level"), lang, assistance_labels)]
        timing = ("The HTML learning report follows this lesson."
                  if lang == "en" else "本次教学结束后生成 HTML 学习报告。")
    else:
        if mode == "interview":
            second_line = [("Formal full-case mock" if lang == "en" else "完整正式模拟"),
                           _humanise(context.get("interview_format"), lang, format_labels)]
            timing = ("The HTML debrief report follows this case."
                      if lang == "en" else "当前 Case 完成后生成 HTML 复盘报告。")
        else:
            second_line = [("Full Tutorial case" if lang == "en" else "完整教学 Case"),
                           _humanise(context.get("interview_format"), lang, format_labels),
                           _humanise(context.get("assistance_level"), lang, assistance_labels)]
            timing = ("The HTML learning report follows this case."
                      if lang == "en" else "当前 Case 完成后生成 HTML 学习报告。")

    automatic = []
    if context.get("industry_source") == "automatic" and context.get("industry"):
        automatic.append("industry" if lang == "en" else "行业")
    if context.get("difficulty_source") in ("default", "profile") and difficulty:
        automatic.append("difficulty" if lang == "en" else "难度")
    note = ""
    if automatic:
        if lang == "en":
            note = ("{} {} selected automatically; tell me now if you'd like {} changed."
                    .format(" and ".join(automatic).capitalize(),
                            "were" if len(automatic) > 1 else "was",
                            "either" if len(automatic) > 1 else "it"))
        else:
            note = "{}由系统自动确定，可直接修改。".format("和".join(automatic))

    title = "**Session setup**" if lang == "en" else "**本次设置**"
    lines = [title, " · ".join(item for item in first_line if item),
             " · ".join(item for item in second_line if item), timing]
    if note:
        lines.append(note)
    return "\n\n".join(lines)


def infer_session_kind(text):
    """Return an explicit session-kind intent, or ``None`` when ambiguous.

    A topic such as ``market sizing`` is deliberately insufficient evidence:
    it may name a full case or the focus of a multi-rep drill.  This function
    follows the minimum-commitment rule and recognises only wording that changes
    the shape of the session explicitly.
    """
    value = _normalise(text)
    if not value:
        return None

    beginner = any(marker in value for marker in (
        "从头教", "完全新手", "零基础", "基础教学", "beginner lesson",
        "complete beginner", "from scratch"))

    drill = any(marker in value for marker in (
        "专项", "专门练", "连续练", "连续做", "多做几轮", "反复练习",
        "只练计算", "只练图表", "只练结构", "只练 quant", "只练 math",
        "只练 exhibit", "只练 structure", "focused drill", "drill",
        "repetition", "repetitions", " reps", "multiple rounds"))
    drill = drill or bool(re.search(
        r"(?:[2-9]|[二三四五六七八九十]|几)\s*(?:道|题|轮)", value))
    drill = drill or bool(re.search(
        r"\b(?:two|three|four|five|six|seven|eight|nine|ten|several|\d+)\s+"
        r"(?:short\s+)?(?:drills?|exercises?|questions?|reps?|cases?)\b", value))

    full_case = any(marker in value for marker in (
        "完整 case", "完整的 case", "完整case", "完整 sizing",
        "一套 case", "一套 market sizing", "一道 case", "一道 sizing",
        "full case", "complete case", "one case"))
    full_case = full_case or bool(re.search(
        r"(?:给我|做|来)?\s*一\s*(?:道|套).{0,30}\bcase\b", value))
    full_case = full_case or bool(re.search(
        r"\b(?:a|one)\s+(?:full\s+|complete\s+)?[a-z -]*\bcase\b", value))

    matches = [kind for kind, present in (
        ("beginner_curriculum", beginner),
        ("focused_drill", drill),
        ("full_case", full_case),
    ) if present]
    return matches[0] if len(matches) == 1 else None


def random_authorisations(text, asked_fields=None):
    """Return setup dimensions for which *text* explicitly authorises choice.

    Broad phrases apply to every still-applicable material dimension. Targeted
    phrases apply only to the named dimension. Absence of a preference returns an
    empty set; it is never treated as permission to randomise.
    """
    value = _normalise(text)
    if not value:
        return frozenset()

    if asked_fields is not None:
        asked_fields = tuple(asked_fields)
        unknown = set(asked_fields) - set(RANDOM_FIELDS) - {"session_kind"}
        if unknown:
            raise ValueError("unknown asked fields: " + ", ".join(sorted(unknown)))

    authorised = set()
    delegated = any(marker in value for marker in
                    ("随机", "随便", "你决定", "由你决定", "都可以",
                     "surprise me", "random", "anything is fine"))
    if delegated and any(marker in value for marker in
                         ("case type", "case类型", "case 类型", "题型",
                          "random case", "case 随机", "随机 case")):
        authorised.add("case_type")
    if delegated and any(marker in value for marker in
                         ("geography", "market", "市场", "地区")):
        authorised.add("geography")
    if delegated and any(marker in value for marker in
                         ("format", "形式", "推进方式")):
        authorised.add("interview_format")
    broad = any(marker in value for marker in
                ("都随机", "全部随机", "全都随机", "everything random",
                 "random everything", "surprise me"))
    if broad:
        authorised.update(RANDOM_FIELDS)
    elif delegated and not authorised:
        if "来一道" in value or "give me a random case" in value:
            authorised.add("case_type")
        elif asked_fields is not None and len(asked_fields) == 1:
            only = asked_fields[0]
            if only in RANDOM_FIELDS:
                authorised.add(only)
        # Bare "随便" / "you decide" with several unresolved dimensions is
        # ambiguous, not blanket authority.  The caller must ask once.
    return frozenset(authorised)


def missing_setup(context):
    """Return applicable, unresolved fields in one batched-question order.

    ``context`` is the structured result of reading the user's request. Important
    keys are ``mode``, optional ``session_kind``, ``case_type``, ``geography_relevant``,
    ``geography``, ``interview_format``, ``training_focus`` and
    ``random_authorized``. Optional ``assistance_needed`` lets a full Tutorial
    session request its starting assistance in the same setup turn.
    """
    mode = context.get("mode")
    if mode not in MODES:
        raise ValueError("mode must be one of: " + ", ".join(MODES))
    kind = context.get("session_kind")
    if kind is not None and kind not in SESSION_KINDS:
        raise ValueError("session_kind must be one of: " + ", ".join(SESSION_KINDS))

    randomised = set(context.get("random_authorized") or ())
    unknown_random = randomised - set(RANDOM_FIELDS)
    if unknown_random:
        raise ValueError("unknown random-authorized fields: " +
                         ", ".join(sorted(unknown_random)))

    missing = []
    if kind is None:
        if mode == "interview":
            kind = "full_case"
        else:
            missing.append("session_kind")

    # Session kind changes which later questions apply.  Until a Tutorial user
    # chooses Full Case vs Focused Drill, do not silently ask a format question
    # that assumes one branch.  Other already-applicable choices may still be
    # batched into the same setup turn.
    if kind is None:
        if (context.get("geography_relevant") is True and
                not context.get("geography") and "geography" not in randomised):
            missing.append("geography")
        if (mode == "tutorial" and context.get("assistance_needed") and
                not context.get("assistance_level")):
            missing.append("assistance_level")
        return tuple(missing)

    full_case = kind == "full_case"

    if full_case and not context.get("case_type") and "case_type" not in randomised:
        missing.append("case_type")

    if (context.get("geography_relevant") is True and
            not context.get("geography") and "geography" not in randomised):
        missing.append("geography")

    if (full_case and not context.get("interview_format") and
            "interview_format" not in randomised):
        missing.append("interview_format")

    if (mode == "tutorial" and full_case and context.get("assistance_needed") and
            not context.get("assistance_level")):
        missing.append("assistance_level")

    if (mode == "tutorial" and kind == "focused_drill" and not
            (context.get("training_focus") or context.get("case_type"))):
        missing.append("training_focus")

    # Beginner curriculum deliberately defers case type, geography and format
    # until the learner reaches full-case practice.
    return tuple(missing)


def setup_question(fields, language="en"):
    """Render all unresolved fields as one concise setup turn."""
    fields = tuple(fields)
    if not fields:
        return ""
    labels = {
        "en": {
            "case_type": "Which case type would you like? You can also choose random.",
            "geography": "Which market should the case use? Global or random are also fine.",
            "interview_format": "Would you like to drive the case, or have the interviewer/tutor drive it?",
            "assistance_level": "How much help would you like at the start?",
            "training_focus": "What would you like to practise?",
            "session_kind": ("Would you like one complete case, or a focused drill "
                             "with several short reps?"),
        },
        "zh": {
            "case_type": "想练哪类 Case？也可以选随机。",
            "geography": "希望放在哪个市场？也可以选 Global 或随机。",
            "interview_format": "希望由你主导推进，还是由面试官／Tutor 按模块推进？",
            "assistance_level": "开始时希望获得多少帮助？",
            "training_focus": "这次想重点练什么？",
            "session_kind": ("想做一套完整 Case，还是围绕这个主题连续做几道"
                             "专项练习？"),
        },
    }
    lang = "zh" if language == "zh" else "en"
    lead = ("开始前还需要确认：" if lang == "zh" else
            "Before we start, please confirm:")
    return lead + "\n" + "\n".join(
        "{}. {}".format(i, labels[lang][field])
        for i, field in enumerate(fields, 1))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Show unresolved fields for a parsed case-session setup")
    parser.add_argument("context", help="JSON file containing the parsed setup context, or - for stdin")
    parser.add_argument("--language", choices=("en", "zh"), default="en")
    args = parser.parse_args(argv)
    stream = sys.stdin if args.context == "-" else open(args.context, encoding="utf-8")
    try:
        context = json.load(stream)
    finally:
        if stream is not sys.stdin:
            stream.close()
    fields = missing_setup(context)
    print(json.dumps({"ask": fields, "question": setup_question(fields, args.language)},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
