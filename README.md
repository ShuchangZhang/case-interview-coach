# Case Interview Coach

A Claude skill for consulting case interview training, with two strictly separated session modes
on one shared methodology base.

- **Interview Mode** — a realistic MBB-style mock. No hints, no mid-case feedback, no tone tells.
  Ends in a six-dimension scorecard and a Strong Hire / Hire / Borderline / No Hire recommendation.
- **Tutorial Mode** — teaching. Methodology, guided practice, a Socratic hint ladder, error-type
  diagnosis, retries, and assistance that can be dialled from Guided down to fully independent.

Every session ends in a **self-contained HTML report** — one visual system, two report types.

Bilingual at runtime (中文 / English); the instruction files are English.

## The core design rule

> **Mode** determines the purpose of the session and the semantics of its evaluation, so it stays
> fixed for the whole session. **State** and **Assistance Level** describe what is happening right
> now and how much help is allowed, and they may change during the session at the user's request.

```
INTERVIEW
Setup → Active Interview → Final Recommendation → Feedback → Complete
          └─(user aborts)─→ Debrief → Complete ─(opt)→ Post-Debrief Practice  [not a valid mock]

TUTORIAL
Setup → Guided ⇄ Assisted ⇄ Light ⇄ Independent → Session Review → Complete
```

`Active Interview → Debrief` is the one one-way edge. Once answers have been revealed the case is
spent: a genuine re-test needs a new session and a newly generated case — same archetype and
difficulty, different industry, data and root cause.

Tutorial Mode's zero-assistance state is **still Tutorial Mode**. It never produces a hiring
verdict, and the session review reports assisted and independent performance separately rather
than averaging them into one misleading number.

## The report system

Both modes end in an HTML file built from one structured Session Report object, rendered by
`scripts/build_report.py`. Shared design language, different content logic:

| | Interview report | Tutorial report |
|---|---|---|
| Answers | "If this had been real, how did I do?" | "What did I learn, what can I do unaided?" |
| Headline | overall score + hiring band | one-line learning summary, **no hiring band** |
| Focus | what cost you the result, the stronger path | assisted vs independent, hint dependence, mastery |

Three rules are enforced in code rather than prose: a Tutorial report cannot emit a hiring band
without an explicit benchmark request, untested dimensions cannot receive a number, and
fabricated benchmarks (percentiles, offer probabilities, industry averages) raise a warning.

Single file, inline CSS, no JS required, no fonts, no CDN, no network. Opens offline by
double-click; prints to A4/Letter without splitting cards.

## Layout

| File | What's in it |
|---|---|
| `SKILL.md` | Router. Mode/State/Assistance model, both state machines, setup, session boundaries, mode-change handling, time budgets |
| `references/case-methodology.md` | Case arc, structuring, hypothesis loop, exhibits, brainstorming, synthesis, communication, mistake checklist |
| `references/case-math.md` | Six-step quant discipline, formulas, mental math, path choice, sanity checks, market sizing |
| `references/case-taxonomy.md` | 14 archetypes + mixed cases; objective, signals, modules, diagnostic tree, quant, exhibits, insights, mistakes, combinations |
| `references/case-generation.md` | Blueprint-first protocol, backwards design, exhibit and quant design, 14-point consistency check, user-supplied cases, difficulty matrix, geography localisation |
| `references/interview-mode.md` | Interviewer protocol, prohibitions, information release, allowed moves, tone, both format spines, feedback and debrief reports |
| `references/tutorial-mode.md` | Teaching loop, six-block beginner curriculum, progression ladder, drills, hint ladder L0–L4, error diagnosis, session review, learner profile |
| `references/evaluation-rubric.md` | Six dimensions × behavioural anchors at 1–2/3–4/5–6/7–8/9–10, non-averaging hire bands, incomplete-case rules, mastery levels |
| `references/report-system.md` | Session Report schema, per-mode report specs, guard rails, visual system, anti-fabrication rules |
| `scripts/build_report.py` | Session Report JSON → self-contained HTML |
| `references/research-notes.md` | Source tiers, and which principles are official vs convergent vs this skill's own design abstraction |
| `docs/design-and-validation-notes.md` | Architecture rationale, scenario validation tables, risk checks, audit history |

## Install

```bash
git clone <this-repo> ~/.claude/skills/case-interview-coach
```

## Usage

Just say what you want; the skill settles the mode before anything starts.

```
"给我做一次正式 mock，interviewee-led，advanced profitability case"
"I'm new to case interviews — teach me from scratch"
"market sizing drill, five reps"
"here's a casebook PDF — run case 3 as an interview"
```

If the mode is ambiguous it asks once, then locks it for the session.

## Methodology sources

Built from firm-official recruiting material (McKinsey's interviewing pages and four published
sample cases; BCG Careers' case interview guidance; Bain), convergent conclusions across
established preparation resources, and case-architecture study of publicly available casebooks.
No casebook content is reproduced. `references/research-notes.md` records what came from where,
and explicitly separates sourced principles from this skill's own design decisions.

Not affiliated with or endorsed by any consulting firm. The scoring bands are a training
instrument, not any firm's real hiring process.
