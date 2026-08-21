#!/usr/bin/env python3
"""
Render a Session Report JSON into a single self-contained HTML file.

Usage:
    python3 build_report.py report.json -o out.html

One data object, two templates. `session.mode` selects which sections render
and how the numbers are labelled. Scoring and content come from the JSON;
this script only lays them out.

Guarantees enforced here (not left to prose):
  * Tutorial reports never emit a hiring band unless benchmark_requested is true,
    and then only with a visible disclaimer.
  * Aborted sessions are always badged incomplete.
  * Untested dimensions render as "not tested" with no bar and no number.
  * No section renders from absent data — empty in, absent out.
"""

import argparse, html, json, re, sys, datetime

# ---------------------------------------------------------------- palette ---
# Values from the validated reference palette. Ordinal blue ramps verified with
# scripts/validate_palette.js (--ordinal, both modes): ALL CHECKS PASS.
ORDINAL_LIGHT = ["#86b6ef", "#5598e7", "#2a78d6", "#104281"]
ORDINAL_DARK  = ["#184f95", "#256abf", "#3987e5", "#9ec5f4"]

ASSIST_ORDER = ["guided", "assisted", "light", "independent"]
ASSIST_LEVEL_ORDER = ["none", "light", "moderate", "substantial"]

# ------------------------------------------------------------------ i18n ----
L = {
    "en": {
        "interview_title": "Case Interview Performance Report",
        "tutorial_title": "Case Interview Learning Report",
        "interview_q": "How would this have gone in a real consulting case interview?",
        "tutorial_q": "What was learned, and what can now be done unaided?",
        "case_type": "Case type", "industry": "Industry", "geography": "Geography",
        "difficulty": "Difficulty", "format": "Interview format", "focus": "Training focus",
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
        "interview_title": "Case Interview 表现报告",
        "tutorial_title": "Case Interview 学习报告",
        "interview_q": "如果这是一次真实的咨询 Case Interview，这次表现如何？",
        "tutorial_q": "这次学会了什么？哪些已经可以独立完成？",
        "case_type": "Case 类型", "industry": "行业", "geography": "地区",
        "difficulty": "难度", "format": "面试形式", "focus": "训练重点",
        "source": "Case 来源", "status": "完成状态", "assistance": "Interviewer 帮助",
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

FABRICATION_PATTERNS = [
    r"percentile", r"top\s*\d+\s*%", r"better than \d+%", r"超过\s*\d+\s*%",
    r"录取(概率|率)", r"pass rate", r"acceptance (rate|probability)",
    r"industry average", r"行业平均", r"MBB candidates",
]


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
def score_bar(t, dim):
    """Meter: length carries magnitude, text carries the band. No colour-only meaning."""
    name = esc(dim.get("name"))
    if not dim.get("tested", True) or dim.get("score") is None:
        return f"""<div class="dim dim--untested">
  <div class="dim__head"><span class="dim__name">{name}</span>
    <span class="dim__na">{t['not_tested']}</span></div>
  <div class="meter meter--empty"><div class="meter__track"></div></div>
  {f'<p class="dim__ev">{esc(dim.get("evidence"))}</p>' if dim.get("evidence") else ''}
</div>"""

    score = float(dim["score"])
    pct = max(0.0, min(100.0, score * 10.0))
    band = dim.get("band") or t["band"][band_for(score)]
    indep = dim.get("independence")
    indep_html = independence_chip(t, indep) if indep else ""
    return f"""<div class="dim">
  <div class="dim__head"><span class="dim__name">{name}</span>
    <span class="dim__val"><b>{score:g}</b> <span class="dim__of">{t['of10']}</span>
      <span class="dim__band">{esc(band)}</span></span></div>
  <div class="meter"><div class="meter__track"><div class="meter__fill" style="width:{pct:.1f}%"></div></div></div>
  {indep_html}
  {f'<p class="dim__ev">{esc(dim.get("evidence"))}</p>' if dim.get("evidence") else ''}
</div>"""


def independence_chip(t, level):
    """4-step ordinal indicator. Filled segments + text label; readable in greyscale."""
    key = str(level).lower()
    idx = ASSIST_ORDER.index(key) if key in ASSIST_ORDER else None
    if idx is None:
        return f'<div class="indep"><span class="indep__label">{t["independence"]}: {esc(level)}</span></div>'
    segs = "".join(
        f'<i class="seg{" seg--on" if i <= idx else ""}" style="--s:{i}"></i>' for i in range(4)
    )
    return (f'<div class="indep"><span class="indep__steps" aria-hidden="true">{segs}</span>'
            f'<span class="indep__label">{t["independence"]}: <b>{esc(t["assist"][key])}</b></span></div>')


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


def section(title, body, cls=""):
    if not body or not body.strip():
        return ""
    return f'<section class="sec {cls}"><h2>{esc(title)}</h2>{body}</section>'


def kv_strip(pairs):
    cells = "".join(
        f'<div class="kv"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k, v in pairs if v
    )
    return f'<dl class="strip">{cells}</dl>' if cells else ""


def bullets(items, key=None):
    if not items:
        return ""
    out = []
    for it in items:
        if isinstance(it, dict):
            title = it.get("title") or it.get("label") or ""
            detail = it.get("detail") or it.get("note") or ""
            tag = it.get("status")
            tag_html = f'<span class="tag tag--{esc(tag)}">{esc(tag)}</span>' if tag else ""
            out.append(f'<li><span class="blist__h"><b>{esc(title)}</b>{tag_html}</span>'
                       f'{para(detail)}</li>')
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
  <h3>{esc(m.get('stage'))}</h3>{quote}<dl class="mgrid">{body}</dl></article>"""


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
h2{font-size:9pt}.foot{margin-top:10pt}
.hstep--end{background:#104281 !important;color:#fff !important}}
"""


# --------------------------------------------------------------- assembly ---
def build(d):
    lang = d.get("language", "en")
    t = L.get(lang, L["en"])
    s = d.get("session", {})
    mode = s.get("mode", "interview")
    tutorial = (mode == "tutorial")
    head = d.get("headline", {}) or {}
    warnings = []

    # --- guard rails -------------------------------------------------------
    completion = s.get("completion", "complete")
    if completion == "aborted":
        head = dict(head)
        if head.get("verdict") and not head.get("verdict_available", False):
            head["verdict"] = None
    if tutorial and head.get("verdict") and not head.get("benchmark_requested"):
        warnings.append("Tutorial report: hiring verdict dropped "
                        "(benchmark_requested was not set).")
        head = dict(head); head["verdict"] = None; head["overall_score"] = None

    blob = json.dumps(d, ensure_ascii=False).lower()
    for pat in FABRICATION_PATTERNS:
        if re.search(pat, blob):
            warnings.append(f"Possible fabricated benchmark in content: /{pat}/ — remove it.")

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
             (t["geography"], s.get("geography")), (t["difficulty"], s.get("difficulty"))]
    if tutorial:
        pairs += [(t["focus"], s.get("training_focus")),
                  (t["assist_start"], t["assist"].get(str(s.get("assistance_start")).lower(),
                                                      s.get("assistance_start"))),
                  (t["assist_end"], t["assist"].get(str(s.get("assistance_end")).lower(),
                                                    s.get("assistance_end")))]
    else:
        fmt = s.get("interview_format")
        fmt = {"interviewee_led": "Interviewee-led", "interviewer_led": "Interviewer-led"}.get(fmt, fmt)
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
                      f'<span class="result__verdict">{esc(head["verdict"])}</span></div>')
        else:
            reason = head.get("verdict_unavailable_reason") or ""
            result = (f'<div class="result"><span class="result__none">{t["no_verdict"]}</span></div>'
                      + (f'<p class="note">{esc(reason)}</p>' if reason else ""))
    elif head.get("verdict") and head.get("benchmark_requested"):
        result = (f'<div class="result"><span class="result__verdict">{esc(head["verdict"])}</span></div>'
                  f'<p class="note">{t["benchmark_note"]}</p>')

    lede = head.get("one_line_diagnosis") or head.get("learning_summary")
    lede_html = f'<p class="lede">{esc(lede)}</p>' if lede else ""

    hero = f"""<section class="sec hero">
  <h1>{esc(title)}<span class="badge {badge_cls}">{esc(badge_txt)}</span></h1>
  <p class="sub">{esc(subq)}</p>
  {kv_strip(pairs)}{result}{lede_html}
</section>"""

    body = [hero]

    # --- dimensions --------------------------------------------------------
    dims = d.get("dimensions") or []
    if dims:
        body.append(section(t["dimensions"], "".join(score_bar(t, x) for x in dims)))

    # --- tutorial-only: hint dependence, phases ----------------------------
    if tutorial:
        hints = (d.get("hints") or {}).get("by_topic") or []
        if hints:
            body.append(section(t["hints_h"], "".join(hint_track(t, h) for h in hints)))

        ph = d.get("phases") or {}
        if ph.get("assisted") or ph.get("independent"):
            marker = (d.get("session") or {}).get("independence_marker") or {}
            mark_html = (f'<p class="marker">{t["independent_phase"]}: '
                         f'{esc(marker.get("at"))}'
                         f'{" — " + esc(marker.get("note")) if marker.get("note") else ""}</p>'
                         if marker.get("at") else "")
            def phase_card(h, obj, keys):
                if not obj: return ""
                rows = "".join(f"<dt>{esc(k)}</dt><dd>{para(obj.get(v))}</dd>"
                               for k, v in keys if obj.get(v))
                return f'<div class="phase"><h3>{esc(h)}</h3><dl>{rows}</dl></div>'
            a = phase_card(t["assisted_phase"], ph.get("assisted"),
                           [("Covered / 完成内容", "covered"), ("Hints / 使用的提示", "hints"),
                            ("Corrected / 教学后修正", "corrected")])
            i = phase_card(t["independent_phase_h"], ph.get("independent"),
                           [("Covered / 完成内容", "covered"), ("Performance / 独立表现", "performance"),
                            ("Mastered / 真正掌握", "mastered"),
                            ("Still recurring / 仍存在的问题", "still_recurring")])
            body.append(section(t["phases_h"], mark_html + f'<div class="cols">{a}{i}</div>'))

    # --- strengths / weaknesses -------------------------------------------
    st, wk = d.get("strengths") or [], d.get("weaknesses") or []
    if st or wk:
        left = f'<div><h3>{esc(t["strengths"])}</h3>{bullets(st)}</div>' if st else ""
        right = f'<div><h3>{esc(t["weaknesses"])}</h3>{bullets(wk)}</div>' if wk else ""
        head_txt = t["assessment"] if (st and wk) else (t["strengths"] if st else t["weaknesses"])
        body.append(section(head_txt, f'<div class="cols">{left}{right}</div>'))

    # --- key moments -------------------------------------------------------
    km = d.get("key_moments") or []
    if km:
        body.append(section(t["learning_moments"] if tutorial else t["key_moments"],
                            "".join(moment_block(t, m, tutorial) for m in km)))

    # --- interview-only: missed insights, assistance, stronger path, rec ----
    if not tutorial:
        mi = d.get("missed_insights") or []
        if mi:
            rows = []
            for m in mi:
                pairs2 = [(t["evidence_avail"], m.get("evidence_available")),
                          (t["stopped"], m.get("where_you_stopped")),
                          (t["should"], m.get("should_have_concluded")),
                          (t["why_matters"], m.get("why_it_matters"))]
                inner = "".join(f'<div class="mrow"><dt>{esc(k)}</dt><dd>{para(v)}</dd></div>'
                                for k, v in pairs2 if v)
                rows.append(f'<article class="moment"><h3>{esc(m.get("title"))}</h3>'
                            f'<dl class="mgrid">{inner}</dl></article>')
            body.append(section(t["missed"], "".join(rows)))

        asst = d.get("assistance") or {}
        if asst.get("summary") or asst.get("events"):
            lvl = t["assist_lv"].get(str(asst.get("level")).lower(), asst.get("level"))
            ev_items = []
            for e in (asst.get("events") or []):
                eff = e.get("effect")
                eff_html = "<p>{}</p>".format(esc(eff)) if eff else ""
                ev_items.append(
                    "<li><b>{}</b><p>{}</p>{}</li>".format(
                        esc(e.get("stage")), esc(e.get("prompt")), eff_html))
            ev = "".join(ev_items)
            inner = (f'<p><b>{esc(lvl)}</b></p>' if lvl else "") + para(asst.get("summary"))
            inner += f'<ul class="blist">{ev}</ul>' if ev else ""
            body.append(section(t["assistance_h"], inner))

        sp = d.get("stronger_path") or {}
        if sp.get("nodes") or sp.get("note"):
            body.append(section(t["stronger_path"],
                                para(sp.get("note")) + tree_nodes(sp.get("nodes"))))

        rc = d.get("recommendation_compare") or {}
        if rc.get("yours") or rc.get("stronger"):
            blocks = ""
            if rc.get("yours"):
                blocks += f'<div class="rec"><h3>{esc(t["your_rec"])}</h3>{para(rc["yours"])}</div>'
            if rc.get("issues"):
                iss = "".join(f'<div class="issue"><dt>{esc(i.get("criterion"))}</dt>'
                              f'<dd>{esc(i.get("note"))}</dd></div>' for i in rc["issues"])
                blocks += f'<div class="rec"><h3>{esc(t["rec_issues"])}</h3>{iss}</div>'
            if rc.get("stronger"):
                blocks += (f'<div class="rec rec--strong"><h3>{esc(t["stronger_rec"])}</h3>'
                           f'{para(rc["stronger"])}</div>')
            body.append(section(t["rec_compare"], blocks))

    # --- tutorial-only: mastery, recurring, lessons ------------------------
    if tutorial:
        rm = d.get("recurring_mistakes") or []
        if rm:
            body.append(section(t["recurring"], bullets(rm)))
        mas = d.get("mastery") or {}
        if mas.get("independent") or mas.get("needs_help"):
            l = (f'<div><h3>{esc(t["mastery_yes"])}</h3>{bullets(mas.get("independent"))}</div>'
                 if mas.get("independent") else "")
            r = (f'<div><h3>{esc(t["mastery_no"])}</h3>{bullets(mas.get("needs_help"))}</div>'
                 if mas.get("needs_help") else "")
            body.append(section(t["mastery_h"], f'<div class="cols">{l}{r}</div>'))
        tl = d.get("transferable_lessons") or []
        if tl:
            body.append(section(t["lessons"], bullets(tl)))

    # --- next priorities ---------------------------------------------------
    np_ = d.get("next_priorities") or []
    if np_:
        rows = []
        for p in np_:
            kk = [(t["current"], p.get("current")), (t["why"], p.get("why")),
                  (t["target"], p.get("target")), (t["drill"], p.get("drill")),
                  (t["assist_for_drill"], p.get("assistance"))]
            inner = "".join(f'<div class="mrow"><dt>{esc(k)}</dt><dd>{para(v)}</dd></div>'
                            for k, v in kk if v)
            rows.append(f'<div class="pri"><h3>{esc(p.get("title"))}</h3>'
                        f'<dl class="mgrid">{inner}</dl></div>')
        body.append(section(t["next_plan"] if tutorial else t["next"], "".join(rows)))

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
    return doc, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    with open(a.json_path, encoding="utf-8") as f:
        data = json.load(f)
    doc, warns = build(data)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(doc)
    for w in warns:
        print(f"WARNING: {w}", file=sys.stderr)
    print(f"Wrote {a.out} ({len(doc):,} bytes)")


if __name__ == "__main__":
    main()
