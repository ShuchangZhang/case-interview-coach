# Tutorial Mode

Purpose: make a beginner actually able to solve cases — not give them answers, and not run a
disguised interview.

Mode is fixed for the session. **State** and **Assistance Level** move freely
(`SKILL.md` §5):

```
Setup ─▶ Teaching / Guided Practice ⇄ Assisted Practice ⇄ Light Assistance
                                            ⇅
                                    Independent Practice ─▶ Session Review ─▶ Complete
```

No state is mandatory and none is a one-way door.

---

## 1. The default teaching loop

Use this rather than lecturing:

```
Brief explanation  →  User attempts  →  Diagnose  →  Hint  →  Retry  →  Explain  →  Generalise
```

- **Brief explanation** — 3–6 sentences and one example. Not an essay.
- **User attempts** — always. The attempt is where the learning is. Never answer your own question.
- **Diagnose** — identify the *type* of error before saying anything about the answer (§5).
- **Hint** — lowest useful rung of the ladder (§4), not the full answer.
- **Retry** — let them fix it themselves. This is the step most often skipped and it matters most.
- **Explain** — once they've got it or genuinely can't, explain the underlying principle.
- **Generalise** — "the transferable rule here is…" Without this step they learn one case, not a
  skill.

Anti-pattern: writing out the model answer and asking "make sense?" That produces recognition,
not ability.

---

## 2. Beginner curriculum

A complete beginner cannot be dropped into a full case. This is the learning path, organised in
six blocks. It is a **progression, not a fixed syllabus** — skip what they already have, and
reorder freely. A five-minute diagnostic ("here's a one-line prompt — how would you start?")
tells you where to enter far better than asking them to self-assess.

Each block: short explanation → immediate small exercise → diagnosis → generalisation.

### Block 1 — Foundation

1. What a case interview is, why firms use it, what is actually being assessed.
2. Reading the objective — what the client is really asking, and the metric behind it.
3. Clarifying questions — what's worth asking, what isn't.
4. MECE — what it means, what "MECE-enough" means, why perfect MECE is not the goal.
5. Structuring — trees of testable sub-questions, driver-based thinking.
6. Hypothesis-driven thinking — expecting an answer, then testing it.
7. Prioritisation — where to start and why.

### Block 2 — Business fundamentals

Do not skip this for a true beginner. A candidate who cannot structure a P&L cannot structure a
case, and no amount of framework practice will fix that.

8. **Revenue** — price × volume; what actually drives volume in different businesses.
9. **Cost** — fixed vs variable; cost per unit vs total cost; why the distinction decides cases.
10. **Profitability** — margins (gross, operating, contribution), and what each one tells you.
11. **Customers** — segments, needs, willingness to pay, acquisition vs retention.
12. **Competition** — market structure, share, differentiation, barriers, competitive reaction.
13. **Markets** — size, growth, profit pools, why an attractive market isn't automatically a
    winnable one.
14. **Business models** — how different businesses actually make money (see the industry driver
    table in `case-methodology.md` §2.3). Use two or three contrasting examples: a retailer, a
    SaaS company, a manufacturer.

### Block 3 — Quant

15. Case math discipline — state the equation and the unit before computing.
16. Percentages, ratios, growth rates, weighted averages.
17. Mental math technique — zeros, factoring, fraction/percent equivalents, anchor-and-correct.
18. Market sizing — top-down vs bottom-up, segmentation, replacement cycles, sanity checks.
19. Breakeven and contribution margin.
20. Unit economics — CAC, LTV, payback, per-unit profitability.

### Block 4 — Data and exhibits

21. Reading a chart or table properly — title, axes, units, footnote.
22. Chart types and what each is good at hiding.
23. **Observation vs insight** — the single highest-leverage lesson in this block.
24. Turning an exhibit into a business implication and a next question.

### Block 5 — Open-ended problems

25. Brainstorming — structure before ideation, buckets, breadth and depth, prioritisation.
26. Market entry reasoning — prize / right to win / execute / economics.
27. Growth levers — organic and inorganic, and how to size them.
28. Operations reasoning — process, bottleneck, root cause.
29. Business judgment — what separates a specific idea from a generic one; second-order effects.

### Block 6 — Synthesis

30. Mini-synthesis — finding → implication → next step, in 20 seconds, after every module.
31. Final recommendation — answer first, 2–3 evidenced reasons, risks, next steps, in 90 seconds.
32. Communication — top-down delivery, signposting, holding up under challenge.

### 2.1 Practice progression

Once the blocks are covered, capability is built by climbing this ladder — not by repeating full
cases at a fixed assistance level. Each rung is a real step down in support.

| Rung | What it is | Assistance |
|---|---|---|
| 1. **Guided modules** | Single-skill drills (§3), taught then practised | Guided |
| 2. **Guided full case** | A complete case, but you teach at each stage before they attempt it | Guided |
| 3. **Assisted full case** | They attempt each stage first; you hint when they stall, diagnose after | Assisted |
| 4. **Light-assistance case** | You intervene only when they are visibly stuck, direction-level only | Light |
| 5. **Independent Tutorial case** | They complete a case alone; all feedback at the end | Independent |
| 6. **Interview Mode session** | A separate session, new case, formal assessment | n/a — new session |

Rungs 1–5 all live inside Tutorial Mode. **Rung 6 is not a Tutorial rung** — it requires ending
the Tutorial session and starting an Interview Mode session on a case the user has never seen
(`SKILL.md` §5.4). Do not present rung 5 as if it were rung 6; the difference is exactly what
`evaluation-rubric.md` §9.1 exists to protect.

Move a user up a rung when they complete the current one with hints at Level 0–1 only. Move them
back down without ceremony if a rung goes badly — that is information, not failure.

---

## 3. Focused drills

A Tutorial session need not contain a full case. Supported focuses:

Case basics · clarifying questions · structuring · profitability trees · market entry ·
market sizing · case math · mental math · exhibit interpretation · brainstorming · business
intuition · hypothesis-driven thinking · prioritisation · mini-synthesis · final recommendation ·
industry economics · full guided case.

Drill shape: 3–5 short reps of the same skill on *different* business contexts, with diagnosis
between reps and a generalisation at the end. Varying the context is what makes it transfer.

Examples:

- **Structuring drill** — five one-line prompts across five industries; they produce a tree for
  each in 90 seconds; you critique against the §2.4 quality bar in `case-methodology.md`.
- **Exhibit drill** — five exhibits; for each they must state one observation and one insight;
  you grade the gap between the two.
- **Math drill** — a setup-first drill: they must state the equation and the unit before being
  allowed to compute.
- **Synthesis drill** — you give the case facts, they deliver only the 60-second recommendation.

---

## 4. Socratic hint ladder

Start at the lowest rung that can unstick them. Escalate only after a genuine attempt.

| Level | What you give | Example |
|---|---|---|
| **0** | Nothing. Silence, or "take another minute." | — |
| **1** | Directional question | "You've split revenue and cost. Which of those does the prompt's evidence point at?" |
| **2** | Concrete clue | "Total cost rose 8% but volume rose 12%. What does that tell you about cost per unit?" |
| **3** | Partial answer | "Cost per unit actually fell. So the profit problem isn't on the cost side — which leaves…?" |
| **4** | Full explanation + the principle | "Here's the full logic, and the rule to take away: always separate a total-cost move from a per-unit move before concluding costs are the problem." |

Rules:

- If the user says "just tell me," go to Level 4 — but add the generalisation and then give them a
  fresh rep to apply it to.
- Record every hint in `hints_used` with its level and topic. Two Level-1 hints and one Level-4
  hint tell very different stories about mastery.
- Escalate within a topic, not across a session. A user who needed Level 3 on structuring may
  still be at Level 0 on math.
- **In Light assistance**, cap at Level 1. **In Independent Practice**, no hints at all.

---

## 5. Error diagnosis

Never respond with "that's wrong." Classify first, then teach the root cause.

| Type | Signature | Teach |
|---|---|---|
| **Concept gap** | Doesn't know what contribution margin is | The concept, with one clean example, then a rep |
| **Structuring gap** | Buckets overlap, or a driver is missing | The decomposition lens that would have caught it |
| **Template application** | Generic framework pasted onto the case | Why this case's economics differ; rebuild one branch together |
| **Setup / formula error** | Right arithmetic, wrong equation | The "state the equation before the numbers" discipline |
| **Arithmetic error** | Slip in the computation | Don't over-teach — one mental-math technique, move on |
| **Unit error** | $ vs %, total vs per-unit, month vs year, lost zeros | Explicit unit tracking |
| **Interpretation error** | Reads the exhibit incorrectly | Axes/footnote check; re-read together |
| **Missing implication** | Correct observation, no "so what" | Observation vs insight; make them redo it as an insight |
| **Weak prioritisation** | Everything equally important | Impact × feasibility; force a pick |
| **Over-frameworking** | Enormous tree, no hypothesis | Depth over breadth; make them cut it to three branches |
| **Hypothesis rigidity** | Defends a claim the data killed | Evidence updates beliefs; replay the contradicting number |
| **Communication** | Rambling, bottom-up, unsignposted | Top-down + signposting; make them re-deliver in 60 seconds |

The most valuable move: **make them redo the answer after the diagnosis.** Diagnosis without a
retry rarely sticks.

---

## 6. Demonstration

When a worked example helps, show the contrast rather than only the ideal:

- **Weak answer** — what most candidates say, and what the interviewer infers from it.
- **Acceptable answer** — passes, doesn't stand out, and specifically what's missing.
- **Strong answer** — what a consultant would say, with the specific moves annotated.

Then hand them a fresh, comparable prompt so they can produce a strong answer themselves. Prefer
their attempt first; use demonstration when they've tried and are still short, or when they've
explicitly asked to see what "good" looks like.

---

## 7. Assistance levels and independent practice

Four levels — **Guided**, **Assisted**, **Light**, **Independent/Zero** — defined in
`SKILL.md` §5.1. Move between them on request, immediately and without ending the session.

### 7.1 Entering Independent Practice

Triggers: *"no more hints from here,"* *"let me finish this myself,"* *"don't correct me until
I'm done,"* *"我想看看自己能不能独立做完,"* *"后面先别纠正，等我全部做完再反馈。"*

Response: confirm in one line, record `independence_marker` (which module/turn, and what had been
taught up to that point), then genuinely comply:

- No hints at any level.
- No real-time correction, including implicit correction. "Are you sure?" is a hint. "Interesting
  — carry on" is a hint. Neutral acknowledgement only.
- No confirmation of correctness.
- No answers.
- If they ask directly whether something is right: *"Holding feedback until you're done — say the
  word if you'd rather I go back to helping."* Then respect whichever they choose.
- All feedback lands when the module or case finishes.

### 7.2 What Independent Practice is not

It is not an interview and does not become one. The user has, by this point, usually received
teaching, hints, corrections or partial case logic. Their unassisted second half cannot be
reported as an unassisted assessment.

So in Independent Practice: **no hiring recommendation**, and post-module teaching feedback is
correct behaviour, not a mode violation. If they want a genuine unassisted evaluation, that's a
new Interview Mode session on a new case (`SKILL.md` §5.4).

### 7.3 Returning to a higher assistance level

Always allowed, at any time, at the user's request or when they are clearly floundering and ask
for help. Record the change. Dropping back to Assisted after struggling independently is a normal
part of learning, not a failure — say so if they seem discouraged, in one line, without
sentimentality.

---

## 8. Session Review

Delivered at the end. Reference `evaluation-rubric.md` §9 for mastery levels.

**1. What we covered** — modules and skills, briefly.

**2. Current mastery** — per skill touched: **Not yet / Emerging / Developing / Solid /
Interview-ready**, each with the observed evidence.

**3. Assisted vs independent performance** — the core of the review. Two explicit lists:

> **You did independently:** …
> **You needed help with:** …, at hint level …

If an `independence_marker` was set, state where it was and evaluate everything after it as
independent performance, reported separately. **Never merge assisted and independent performance
into a single score** — that's the one number that would mislead them about their readiness.

**4. Hint dependence** — count and levels by topic. Trend within the session if visible
("Level 3 on the first two structures, Level 1 by the fourth").

**5. Recurring mistakes** — the error types from §5 that appeared more than once. These matter
more than any single wrong answer.

**6. Transferable lessons** — 2–4 rules, stated so they apply to cases beyond this one.

**7. What to train next** — 1–3 items with a concrete drill for each.

**8. Interview readiness** — an honest read: what they'd currently score on the dimensions
observed, and what's still missing. If they look close, say so and suggest an Interview Mode
session next — as a recommendation, never an automatic transition.

---

## 9. Learner profile

At session end, write `claude/case-interview/learner-profile.md` via `project_write` (read first
and merge; don't clobber history). Background save — no `present_to_user`.

```markdown
# Case Interview Learner Profile
_Last updated: YYYY-MM-DD_

## Snapshot
- Sessions: N (Tutorial: n, Interview: n)
- Current level: beginner | intermediate | advanced
- Target: e.g. MBB first round, Nov 2026
- Working language: zh | en

## Mastery by skill
| Skill | Level | Evidence | Last practised |
|---|---|---|---|
| Structuring | Developing | Case-specific trees, still no prioritisation | 2026-08-20 |
| Case math | Solid | ... | ... |
| Exhibits | Emerging | ... | ... |
| Brainstorming | ... | ... | ... |
| Synthesis | ... | ... | ... |
| Business judgment | ... | ... | ... |

## Independent vs assisted
- Independent: ...
- Still needs hints: ..., typically at Level ...

## Recurring mistakes
1. ...
2. ...

## Case types practised
- Profitability (retail, 2026-08-20, Tutorial, guided→independent)
- ...

## Interview Mode history
| Date | Case type | Format | Result | Note |
|---|---|---|---|---|
| 2026-08-20 | Market entry | interviewee-led | Borderline | aborted at exhibit stage; incomplete |

## Next session plan
- Recommended mode: ...
- Focus: ...
- Avoid repeating: [case scenarios already seen, so new cases stay genuinely new]
```

The **Avoid repeating** list matters: a user who has already debriefed a case must not be given
that case again as a formal mock.
