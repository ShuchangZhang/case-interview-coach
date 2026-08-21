# HTML Report System

Every session — complete or ended early — produces one self-contained HTML file. That file, not
the chat message, is the session's deliverable.

One data object, two templates. `session.mode` decides which sections render and what the numbers
mean. The two reports answer different questions and must not read as the same document with
different words:

| | Interview report | Tutorial report |
|---|---|---|
| Answers | "If this had been a real case interview, how did I do?" | "What did I learn, and what can I now do unaided?" |
| Unit of judgment | independent performance against a hiring bar | progress, and the gap between assisted and independent |
| Headline | overall score + Strong Hire / Hire / Borderline / No Hire | one-line learning summary — **no hiring band** |
| Centre of gravity | what cost you the result, and the stronger path | where learning happened, and what to train next |

**Nothing in this file changes how a session is run, what is taught, how cases are generated, or
how performance is scored.** It governs only what happens after the session ends.

---

## 1. Workflow

1. Session reaches its terminal state (`SKILL.md` §10).
2. Produce the assessment content exactly as `interview-mode.md` §8/§9 or `tutorial-mode.md` §8
   already specify. **The rubric and the content rules are unchanged** — this system changes the
   container, not the judgment.
3. Write that content into a **Session Report JSON** (§3).
4. Render:
   ```bash
   python3 scripts/build_report.py report.json -o case_interview_report_<id>.html
   ```
5. Read any `WARNING:` the script prints and fix the data — warnings mean a rule was violated.
6. Deliver the HTML (§8), then update the learner profile as usual.

**Never hand-assemble the HTML from prose.** The JSON step is what keeps the two report types
structurally consistent and keeps the guard rails enforceable.

### File naming

`case_interview_report_<YYYY-MM-DD>_<mode>_<short-slug>.html`
e.g. `case_interview_report_2026-08-20_interview_grocery-profitability.html`

Adapt to the environment if a different convention fits better; keep the date and mode in the name.

---

## 2. Guard rails the script enforces

Do not try to work around these — they exist because the two reports mean different things.

- **A Tutorial report emits no hiring band.** Setting `headline.verdict` without
  `headline.benchmark_requested: true` gets it stripped and warned. With the flag, it renders
  behind a visible "indicative benchmark only" disclaimer.
- **An aborted session is always badged incomplete**, with the stage it ended at.
- **Untested dimensions render as "not tested"** — no bar, no number. Never invent a score to
  fill the row.
- **Empty in, absent out.** A section with no data does not render. A short honest report beats a
  padded one.
- **Fabricated-benchmark detector**: percentile claims, "top N%", acceptance/pass rates, industry
  averages, "better than X% of MBB candidates" trigger a warning. Remove them — see §7.

---

## 3. Session Report JSON

Shared skeleton. Fields marked **[I]** are interview-only, **[T]** tutorial-only; the rest are
shared. Omit anything you have no real data for.

```jsonc
{
  "language": "zh" | "en",

  "session": {
    "id": "S-2026-08-20-A",
    "date": "2026-08-20",
    "mode": "interview" | "tutorial",
    "case_type": "Profitability + Pricing",
    "industry": "...", "geography": "...", "difficulty": "Advanced",
    "case_source": "original" | "user_provided",
    "completion": "complete" | "aborted" | "partial",
    "aborted_at_stage": "structure",              // when aborted
    "interview_format": "interviewee_led",        // [I]
    "training_focus": "structuring + case math",  // [T]
    "assistance_start": "guided",                 // [T]
    "assistance_end": "independent",              // [T]
    "independence_marker": {                      // [T] only if it actually happened
      "at": "rep 3 of the structuring drill",
      "note": "you asked for no more hints from here"
    }
  },

  "headline": {
    "verdict": "Hire",                    // [I]; [T] only with benchmark_requested
    "verdict_available": true,            // [I] false when the sample is too thin
    "verdict_unavailable_reason": "...",  // [I] required when verdict_available is false
    "overall_score": 7.4,                 // [I]
    "benchmark_requested": false,         // [T] true only if the user explicitly asked
    "one_line_diagnosis": "...",          // [I]
    "learning_summary": "..."             // [T]
  },

  "dimensions": [
    { "name": "Problem Structuring", "score": 8, "tested": true,
      "band": "Strong",                   // optional; derived from score if omitted
      "independence": "assisted",         // [T] guided | assisted | light | independent
      "evidence": "one line of what you actually observed" }
  ],

  "strengths":  [ { "title": "...", "detail": "..." } ],
  "weaknesses": [ { "title": "...", "detail": "...", "impact": "..." } ],

  "key_moments": [
    // [I] shape
    { "stage": "Initial structure", "quote": "…what the candidate actually said…",
      "what_you_did": "...", "worked": "...", "problem": "...",
      "consequence": "...", "stronger": "..." },
    // [T] shape — error → hint → retry → principle
    { "stage": "First structure attempt", "quote": "...",
      "what_you_did": "...", "intervention": "...", "retry": "...", "learning": "..." }
  ],

  "missed_insights": [                    // [I]
    { "title": "...", "evidence_available": "...", "where_you_stopped": "...",
      "should_have_concluded": "...", "why_it_matters": "..." }
  ],

  "assistance": {                         // [I]
    "level": "none" | "light" | "moderate" | "substantial",
    "summary": "...",
    "events": [ { "stage": "...", "prompt": "...", "effect": "..." } ]
  },

  "hints": {                              // [T]
    "by_topic": [
      { "topic": "Structuring", "sequence": ["Level 3","Level 2","Level 1","Independent"],
        "note": "hint strength fell across four reps — learning happened" }
    ]
  },

  "phases": {                             // [T]
    "assisted":    { "covered": "...", "hints": "...", "corrected": "..." },
    "independent": { "covered": "...", "performance": "...",
                     "mastered": "...", "still_recurring": "..." }
  },

  "stronger_path": {                      // [I]
    "note": "why this line is tighter than the one you took",
    "nodes": [ { "label": "...", "detail": "...", "children": [ … ] } ]
  },

  "recommendation_compare": {             // [I]
    "yours": "...",
    "issues": [ { "criterion": "Answers the client question", "note": "..." } ],
    "stronger": "..."
  },

  "recurring_mistakes": [                 // [T]
    { "label": "...", "status": "new" | "repeat", "note": "..." }
  ],
  "mastery": {                            // [T]
    "independent": [ "..." ],
    "needs_help":  [ "..." ]
  },
  "transferable_lessons": [ "..." ],      // [T]

  "next_priorities": [
    { "title": "...", "current": "...", "why": "...",      // why → [I]
      "target": "...", "drill": "...", "assistance": "..." } // target/assistance → [T]
  ]
}
```

---

## 4. Interview report — what each section must contain

**First screen** (case strip + result + one-liner) must let the reader understand the outcome
without scrolling.

1. **Case strip** — type, industry, geography, difficulty, format, completion badge, assistance
   level.
2. **Overall result** — score and band. If the case was aborted and the sample is thin, set
   `verdict_available: false` and give a real reason. **Do not manufacture a verdict.**
3. **One-line diagnosis** — specific and causal. The test: could this sentence be pasted into a
   different candidate's report? If yes, rewrite it.
   - Bad: "Overall solid, with room to improve."
   - Good: "Math was accurate and the structure was sound, but the data work stayed descriptive,
     so the key insight and the final recommendation both landed without evidence behind them."
4. **Capability assessment** — all six dimensions; untested ones marked as such. One line of
   observed evidence per dimension.
5. **Strengths / detractors** — 2–4 each. Every item quotes a real behaviour from this session.
   Detractors are ordered **by impact on the result**, not chronologically. The question each one
   answers is: what actually downgraded this case?
6. **Key moments** — 3–7, only ones with teaching value. Not a transcript.
7. **Missed insights** — for each: evidence that was available, where they stopped, what follows
   from it, why it matters to the client's decision. Not a printed answer key.
8. **Interviewer assistance** — the level, and where the decisive prompts landed. This must be
   consistent with the verdict: the same conclusion reached unaided and reached after three
   prompts are not the same performance, and the report should say so.
9. **Stronger path** — a tree/chain showing a tighter line of analysis, with *why* it is tighter.
   Do not re-solve the whole case.
10. **Recommendation comparison** — what they said, where it falls short (answers the question?
    evidence? risks? next steps? length? top-down?), and a stronger version. The stronger version
    may use **only facts that appeared in this case**.
11. **What to train next** — 1–3, each with a concrete drill.
    - Bad: "Practise structuring more."
    - Good: "Do 3–5 structuring reps; after listing top-level branches you must state which one
      you'd investigate first and why, and delete any branch you can't justify."

### Aborted sessions

Same container, different centre of gravity: where the case lost momentum, why, what was observed
up to that point, the more workable direction, and the transferable lesson. Everything untested is
marked untested. If the sample is too thin for a verdict, say so — and if there *is* enough to say
something, bound it explicitly ("on the structuring segment alone, this was tracking Borderline;
nothing else was sampled").

---

## 5. Tutorial report — what each section must contain

**Never** a hiring band by default. This report is about progress, not selection.

1. **Session strip** — topic/focus, case type, difficulty, assistance at start and at end,
   whether an independent phase happened, completion.
2. **Learning summary** — one specific sentence about the most important progress.
   - Bad: "You learned a lot today."
   - Good: "You can now do the first-level profit breakdown and the percentage work unaided, and
     stopped needing hints from the third rep on; second-level structure still falls back on
     generic buckets."
3. **Capability assessment with independence** — every dimension carries **both** a level of
   performance and how much help it took. A 7 reached under Level-3 hints and a 7 reached unaided
   are different facts, and the report must show which one it is.
4. **Hint dependence** — per topic, the sequence across reps (`Level 3 → Level 2 → Level 1 →
   Independent`). The point is whether learning happened, not how many hints were used in total.
   A flat `Level 3 → Level 3` is the most useful thing on the page: it names what to train next.
5. **Assisted vs independent phases** — if an `independence_marker` exists, state where it was and
   evaluate the two stretches separately. **Never merge them into one score.**
6. **Key learning moments** — error → intervention → retry → principle. Only moments with real
   teaching value.
7. **Recurring mistakes** — `status: "repeat"` is permitted **only** when a learner profile
   actually records it. With no history, everything is `new`. Do not invent a trend.
8. **Mastery check** — two lists: can do unaided / still needs support. This is the section the
   user will come back for.
9. **Transferable lessons** — 1–3 that this session actually touched. Not a dump of the
   methodology.
10. **Next training plan** — 1–3, each with current state, target, drill, and suggested
    assistance level.

If the user explicitly asked for a benchmark: set `benchmark_requested: true`, and say in the
disclaimer which parts were done with help.

---

## 6. Visual system (shared)

Both reports use one design language — a restrained analyst document, not a scoreboard. It is
implemented in `scripts/build_report.py`; do not hand-roll a different one.

- **Self-contained**: one file, inline CSS, no JS required, no fonts, no CDN, no network. Opens by
  double-click, works offline. There is no hover-only content — every value is directly labelled.
- **Colour**: from a validated palette (light and dark both checked with the data-viz validator).
  Ink and greys carry the document; one blue carries magnitude. Status colour is used only for the
  incomplete badge and the "no verdict" line, always with text beside it — never colour alone.
- **Score meter**: length encodes the score; the band is a **text** label. No traffic lights.
  Untested renders as a dashed empty track.
- **Independence indicator**: a four-segment ordinal step block plus its text label — legible in
  greyscale and in print.
- **Hint track**: labelled chips with arrows; the final state is emphasised.
- **Print**: A4/Letter, dark backgrounds avoided, cards and moments kept off page breaks, colours
  preserved, headings never orphaned.
- **Responsive**: two-column blocks collapse below 640px; label/value grids stack.
- Permitted: cards, columns, meters, chips, small trees, timelines, emphasised numbers.
  Not permitted: gradients, animation, emoji, decorative iconography, dashboard chrome.

---

## 7. No fabricated data

Only what this session actually produced may appear: real scores, real hint records, real
assistance level, real phases, and real learner history when it exists.

Never render, under any framing: global percentiles · "better than X% of candidates" · offer or
pass probabilities · industry average scores · firm-internal benchmarks · trend lines across
sessions that never happened.

Cross-session comparisons ("this error is down from last time", "hint dependence has fallen") are
allowed **only** when the learner profile actually contains that history. With no history, say
nothing about trends. Never put personal information unrelated to case training into the report.

---

## 8. Delivering it in chat

After the file renders, the chat message is short:

1. The report has been generated (name the file).
2. Send the file.
3. **2–4 sentences** of the most important conclusions.

Do not restate the report in chat. The whole point is that the HTML is the artifact.

If the render fails, fall back to the structured text report defined in `interview-mode.md` §8/§9
or `tutorial-mode.md` §8, and say the HTML step failed.

---

## 9. Quoting the user

Both reports may quote a few of the user's actual words (`quote` on a key moment) to anchor a
diagnosis — then analyse why that phrasing worked or didn't. Short quotes only; never a
transcript.
