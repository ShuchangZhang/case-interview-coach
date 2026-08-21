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
3. Write that content into a **Session Report JSON** (§3), including the exact candidate-facing
   prompt captured at session start and the ordered user-visible session transcript. Do not
   reconstruct either from memory at report time.
4. Render it. **Invoke the script by its absolute path inside the skill directory** — never as a
   bare relative path, because the working directory is the user's project, not the skill:

   ```bash
   python3 <skill-dir>/scripts/build_report.py report.json -o case_interview_report_<id>.html
   ```

   `<skill-dir>` is the directory containing this skill's `SKILL.md` — typically
   `~/.claude/skills/case-interview-coach`. If it is not known, resolve it once:

   ```bash
   SKILL_DIR=$(dirname "$(find ~/.claude/skills -name SKILL.md -path '*case-interview-coach*' \
     2>/dev/null | head -1)")
   python3 "$SKILL_DIR/scripts/build_report.py" report.json -o report.html
   ```

   The script itself resolves everything it needs from its own location, so an absolute
   invocation works from any directory. `--skill-root` prints the directory it resolved.
5. **A non-zero exit means no report exists.** The script validates before it renders: on a bad
   enum, an out-of-range score, an inconsistent verdict, or a guard-rail violation it writes no
   HTML, prints a `ValidationError` naming the field, the value and the legal range, and exits 2.
   Fix the data and re-run. **Never deliver a report after a failed render, and never work around
   a validation error by loosening the data** — the check exists because that particular claim
   would have been unsupported.
6. Deliver the HTML (§8), then update the learner profile if the host provides project memory
   (`SKILL.md` §3.4 — silently skipped when it does not).

**Never hand-assemble the HTML from prose.** The JSON step is what keeps the two report types
structurally consistent and keeps the guard rails enforceable.

### File naming

`case_interview_report_<YYYY-MM-DD>_<mode>_<short-slug>.html`
e.g. `case_interview_report_2026-08-20_interview_grocery-profitability.html`

Adapt to the environment if a different convention fits better; keep the date and mode in the name.

`case_prompt` is the exact wording the candidate saw at formal start. For a user-provided case,
copy only the candidate-facing prompt actually used in the session. Never include an interviewer
guide, answer key, hidden root cause, unrevealed exhibit, later-supplied number or generation
blueprint. The test is simple: could the candidate see this text at that moment?

---

## 2. Validation and guard rails — the build fails, it does not warn

The renderer validates before it renders. Anything below stops the build: **no HTML is written,
a `ValidationError` naming the field goes to stderr, and the exit status is 2.** Nothing is
silently corrected or quietly dropped, because a report that was quietly altered is a report
whose claims no longer match the session.

**Schema**

| Field | Must be |
|---|---|
| `session.mode` | `interview` or `tutorial` |
| `session.completion` | `complete`, `aborted` or `partial` |
| `session.assistance_start` / `_end` | `guided`, `assisted`, `light` or `independent` |
| `dimensions[].score` | a finite number in 0–10 — not a string, not `NaN`, not out of range |
| `dimensions[].independence` | one of the four assistance levels |
| `assistance.level` | `none`, `light`, `moderate` or `substantial` |
| `headline.verdict` | Strong Hire / Hire / Borderline / No Hire, or null |
| `headline.benchmark_requested` | a JSON boolean — `true` or `false`, never a string or number |
| `case_prompt` | a non-empty string: the exact prompt shown to the candidate at formal start |
| `transcript` | a non-empty ordered array of validated message and event records |
| `transcript[].id` | unique, stable, HTML-safe identifier |
| `transcript[].type` | `message` or `event` |
| message `role` | Interview: `candidate` / `interviewer`; Tutorial: `candidate` / `tutor` |
| analysis `turn_refs` | non-empty array containing only IDs that exist in `transcript` |
| `core_feedback` | at most three items, keyed `strength` / `priority` / `next_step`, each with a `headline` and a `detail` |
| `annotations[].turn_id` | an ID that exists in `transcript` |
| `annotations[].type` | `strength`, `needs_improvement`, `critical`, `hint_given`, `improved` or `polish` |
| `annotations[].comment` | a non-empty explanation |
| `takeaways` | at most three short strings |
| `hints` / `phases` / `key_moments` | **rejected** — superseded, see §10 |

**Semantic rules**

- **An untested dimension may not carry a score.** `tested: false` with a number is rejected
  rather than rendered — a number would assert an assessment that was never made.
- **A tutorial report may not carry a hiring band.** `headline.verdict` in a tutorial report is
  rejected unless `headline.benchmark_requested: true`, which is set only when the user
  explicitly asked to be benchmarked; it then renders behind a visible disclaimer.
- **Mode-specific fields stay in their mode**, at every level. A field belonging to the other
  mode means the report was assembled from the wrong template, and is rejected. The split is
  maintained in one place — `MODE_FIELDS` in `scripts/build_report.py`:

  | Scope | Interview-only | Tutorial-only |
  |---|---|---|
  | document root | `missed_insights`, `assistance`, `stronger_path`, `recommendation_compare` | `hints`, `phases`, `recurring_mistakes`, `mastery`, `transferable_lessons` |
  | `session` | `interview_format` | `training_focus`, `assistance_start`, `assistance_end`, `independence_marker` |
  | `headline` | — | `benchmark_requested` |

  Everything else in `session` is shared (`SHARED_SESSION_FIELDS`). Adding a field means adding
  one line to that registry, not another branch in the validator.
- **`headline.benchmark_requested` must be a JSON boolean.** `true` or `false` only — a string,
  number or `null` is rejected rather than coerced. This matters more than it looks: `"false"` is
  a truthy string in Python, so coercion would silently unlock the hiring verdict a tutorial
  report must never carry.
- **Verdict consistency.** `verdict_available: false` with a verdict set is a contradiction and
  is rejected; `verdict_available: false` requires a written reason; an aborted session may not
  carry a verdict without `verdict_available: true` stated explicitly.
- **Guard rails on evaluative claims.** Percentile rankings, "top N%", offer or pass
  probabilities, invented firm benchmarks and industry-average scores are rejected — see §7.

**Two things that are not failures**

- **Empty in, absent out.** A section with no data simply does not render. A short honest report
  beats a padded one.
- **Untrusted text is escaped, never rejected.** A case answer containing `<script>` or `&` is
  HTML-escaped and rendered as literal text. Escaping is a rendering concern; it is not a
  truthfulness problem and it never fails the build. Only unsupported *claims* fail.

**Reproducing this.** `tests/test_build_report.py` runs every rule above against committed
fixtures in `tests/fixtures/`, including one fixture per invalid case:

```bash
python3 -m unittest discover -s tests -v
```

---

## 3. Session Report JSON

Shared skeleton. Fields marked **[I]** are interview-only, **[T]** tutorial-only; the rest are
shared. Omit anything you have no real data for.

```jsonc
{
  "language": "zh" | "en",

  "case_prompt": "Exact candidate-facing wording shown at formal session start",
  "transcript": [
    { "id": "T01", "type": "message", "role": "interviewer",
      "content": "Exact user-visible wording", "stage": "opening",
      "tags": ["Case Prompt"] },
    { "id": "T02", "type": "message", "role": "candidate",
      "content": "Exact candidate response", "stage": "clarifying" },
    { "id": "E01", "type": "event", "stage": "formal_interview_end",
      "content": "Formal Interview Ends Here" }
  ],

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
      "consequence": "...", "stronger": "...", "turn_refs": ["T05"] },
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

  // --- the three things that matter most: the top-of-report block ---
  "core_feedback": {
    "strength":  { "headline": "...", "detail": "...", "turn_refs": ["T08"] },
    "priority":  { "headline": "...", "detail": "...", "turn_refs": ["T02","T04"] },
    "next_step": { "headline": "...", "detail": "..." }
  },

  // --- inline coach comments; see §11 ---
  "annotations": [
    { "turn_id": "T04",
      "type": "strength" | "needs_improvement" | "critical" |
              "hint_given" | "improved" | "polish",
      "category": "结构",            // optional, short
      "headline": "...",             // optional, one line
      "comment": "...",              // required
      "improvement": "..." }         // optional: how to do it differently
  ],

  // --- at most three, the closing memory aid ---
  "takeaways": [ "...", "...", "..." ],

  "next_priorities": [
    { "title": "...", "current": "...", "why": "...",      // why → [I]
      "target": "...", "drill": "...", "assistance": "..." } // target/assistance → [T]
  ]
}
```

---

## 4. Interview report — what each section must contain

> Section order and prominence are set out in §12; comments on individual turns in §11.
> The content requirements below are unchanged — only where they are shown has moved.

The opening order is title and metadata, the complete original Case Prompt, then the result and
one-line summary. This lets the reader recover the problem before interpreting the assessment.

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
6. **Key moments** — 3–7, only ones with teaching value. Include `turn_refs` to the complete
   source messages; keep the analysis concise because the full transcript is available below.
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

> Section order and prominence are set out in §12; comments on individual turns in §11.
> The content requirements below are unchanged — only where they are shown has moved.
> Hint dependence and the assisted/independent split are now shown through
> `dimensions[].independence` and comments on the turns themselves (§10.1).

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
6. **Key learning moments** — error → intervention → retry → principle. Cite the first attempt,
   hint and retry with `turn_refs`. Only moments with real teaching value.
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
- **Evidence layer**: analysis links remain readable as Turn IDs in print. The complete transcript
  may use native `<details>` on screen, but print CSS must reveal every record.
- Permitted: cards, columns, meters, chips, small trees, timelines, emphasised numbers.
  Not permitted: gradients, animation, emoji, decorative iconography, dashboard chrome.

---

## 7. No fabricated data

Only what this session actually produced may appear: real scores, real hint records, real
assistance level, real phases, and real learner history when it exists.

Never write, under any framing: global percentiles · "better than X% of candidates" · offer or
pass probabilities · industry-average scores · firm-internal benchmarks · trend lines across
sessions that never happened.

**These are enforced, not advised.** The renderer scans the *evaluative* text — the one-line
diagnosis or learning summary, dimension evidence, strengths, weaknesses, recurring mistakes,
mastery, transferable lessons, next priorities, assistance summary and phase notes — and refuses
to build if it finds such a claim.

The scan is deliberately scoped to evaluative prose and does **not** cover case content. A case
may legitimately state an industry average margin or a conversion rate; that is data the client
has. The rule is about claims made **about the user**, for which this session holds no evidence.

Cross-session comparisons ("this error is down from last time", "hint dependence has fallen") are
allowed **only** when a learner profile was actually read (`SKILL.md` §3.4 — it may be absent
entirely, in which case there is no history to compare against and every recurring mistake is
`new`). Never put personal information unrelated to case training into the report.

The transcript is a user-visible evidence record, not an internal trace. Include only natural
language shown between formal session start and the terminal review, plus visibly distinct event
markers for state transitions. Exclude system/developer prompts, SKILL instructions, hidden case
data, answer keys, reasoning, internal scoring drafts, tools, memory operations and unrelated chat.

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

## 9. Original evidence and privacy

Both reports may quote short excerpts in analysis, then link to full messages through `turn_refs`.
The complete transcript appears once at the end as the evidence layer; never duplicate it inside
the diagnosis.

The report contains the user's complete natural-language contributions within this training
session. The local renderer does not upload them or make network requests. Tell users to review the
HTML before sharing it publicly, because their own answers may contain information they do not
want to disclose.

---

## 10. Report language

A report has **one primary language**, taken from `language`. Everything the reader sees is
written in it.

**Analysis prose is written, transcript text is quoted.** These are different obligations and the
difference is absolute:

- *Analysis* — the summary, core feedback, capability evidence, comments, mastery lists, next
  steps, takeaways — is written for this reader and must read naturally in the report language. In
  a Chinese report that means 市场规模估算, 合理性校验, 计算路径, 敏感性分析, 独立完成 — not
  Market Sizing, Sanity Check, Calculation Tree, Sensitivity, Independent.
- *Transcript* — see §11 — is reproduced exactly as it was said, including whatever mixture of
  languages the session actually contained. Never translate, tidy or normalise it.

English survives in analysis prose in only two cases. First, a term that is genuinely standard in
the industry may appear glossed on first use — 敏感性分析（Sensitivity Analysis）— and unglossed
after. Second, a term with no stable natural translation may stay in English. The test is whether
the English *helps the reader understand faster*, never whether it sounds more professional. A
Chinese sentence carrying four or five English terms fails that test:

> ✗ 你已经完成 base case 和 sensitivity，但 sanity check 和 triangulation 仍然偏 weak。
> ✓ 你已经能够独立完成基准估算和敏感性分析，但合理性校验仍然依赖提示，而且还没有主动设计第二条
>   独立估算路径来交叉验证。

**Internal enums are never printed.** `guided` / `assisted` / `light` / `independent`, hint
levels, annotation types, tags and stage names are data-model tokens. The renderer maps every one
of them through `humanise()` before it reaches the page, so the reader sees 先自己做，卡住时给提示
rather than `Assisted`. Keep using the enums in the JSON — just never assume they are readable.

### 10.1 What replaced what

Three sections were folded into the turn-by-turn review, because each was restating a finding the
review already carries in context. The renderer **rejects** them rather than ignoring them, and
the error names the replacement:

`mastery.needs_help` and `recurring_mistakes` render as one list, so they must not restate each
other. A gap that shows up repeatedly belongs in `recurring_mistakes`, where it can carry the
evidence ("three of four reps"); `needs_help` is for gaps that are not recurring patterns. Writing
both is the single easiest way to make one finding look like two, and no amount of validation can
detect it — only care when writing the data.

| Removed | Now lives in |
|---|---|
| `key_moments` | `annotations` — a key moment is a comment on the turn it happened in |
| `hints` | `annotations` on the turns where hint strength changed, plus `dimensions[].independence` |
| `phases` | `annotations` either side of the assistance change, plus `dimensions[].independence` |

---

## 11. The turn-by-turn review

The transcript is not an appendix. It is the second half of the report, and the place where
detailed feedback belongs — beside the words it is about, rather than in a section the reader has
to hold in memory while scrolling.

**The transcript is verbatim.** Every user-visible turn appears, in order, in the exact words
used. Do not delete uncommented turns, summarise a long answer, fix the candidate's grammar,
translate their English, or tidy their mixed-language phrasing. Its entire value is being a
faithful record.

**Comment selectively.** Annotate a turn only when there is something to learn: a key structuring
answer, an important calculation, an exhibit reading, a real insight, a clear error, a visible
improvement, the final recommendation. Clarifying questions and transitional turns usually need
nothing. Commenting everything recreates the overload this design removed.

**Comment on strengths too**, not only errors — a reader needs to know which habits to keep, and
a report that only marks mistakes teaches the wrong lesson.

**Shape of a comment.** Claim, then why, then how to change it if that is not obvious:

```jsonc
{"turn_id": "T04",
 "type": "needs_improvement",
 "category": "结构",
 "headline": "计算链没有闭环到题目要求的单位",
 "comment": "你用人口和渗透率估出了健身用户数，但题目要的是门店数，中间缺少「每家门店服务多少用户」这个转换变量。",
 "improvement": "以后先写出最终答案的单位，再逐步检查每个变量能否连续转换到它。"}
```

Two or three sentences. Not an essay, and never a bare verdict: "这里不错" and "思路很好" say
nothing. Name the specific thing that was good and why it was good.

**Tutorial: show the arc.** The most valuable thing a tutorial report can show is
error → hint → retry → principle. Annotate all four points so the movement is visible in place.
And keep the distinction the rest of this skill depends on: *"once the calculation path was
given, you executed it accurately"* — never *"you have mastered market sizing"*.

**Interview: comments are post-session only.** Annotating a mock is fine — `strength`,
`needs_improvement`, `critical` all apply. But do not write teaching that did not happen: no
"if you had been given a hint here", no step-by-step coaching mid-case. `hint_given` belongs in an
interview report only where the interviewer actually assisted, and where it did happen, say so —
it is what separates a prompted insight from an independent one.

**Comments are visibly not part of the conversation.** The renderer puts each one in its own
element, outside the quoted content, labelled 复盘点评 / *post-session comment*. Never blur that
line.

---

## 12. Reading order

The report is built to be read twice: once in two minutes, once properly.

| | Section | Job |
|---|---|---|
| 1 | Case information | what this was |
| 2 | The prompt, verbatim | what was actually asked |
| 3 | One-line summary | the whole session in a sentence |
| 4 | **The three things that matter most** | the heaviest block on the page: best work, biggest gap, next step |
| 5 | Capability overview | scores with independence, one line each, links into the transcript |
| 6 | Turn-by-turn review | the full conversation with comments in place |
| 7 | Mastery / missed insights | what is established and what is not |
| 8 | Next training plan | 1–3 priorities |
| 9 | If you remember three things | what should survive the week |

A reader who stops after §4 still knows their most important problem and their next step. Sections
5–9 are for the reader who came back to work.

**Scores are a band, not a measurement.** Render the number with the behavioural description
beside it, and in a tutorial report give independence equal weight — `6 / 10 · 需要提示` says more
than a large `6` ever will.

