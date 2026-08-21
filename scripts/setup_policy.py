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


def _normalise(text):
    return " ".join(str(text or "").strip().casefold().split())


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
