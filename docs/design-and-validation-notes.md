# Case Interview Coach — Skill Design & Validation Notes

Built 2026-08-20. Deliverable: `case-interview-coach.skill`.
**Rev 2 (same day):** completeness audit against the original spec after an interrupted run —
four gaps found and closed (see "Rev 2 audit" at the end).

## Architecture

| File | Lines | Purpose |
|---|---|---|
| `SKILL.md` | ~415 | Router. Mode/State/Assistance separation, both state machines, setup, session boundaries, mode-change handling, soft time budgets |
| `references/case-methodology.md` | ~290 | Shared base: case arc, structuring, hypothesis loop, exhibits, brainstorming, synthesis, communication, mistake checklist |
| `references/case-math.md` | ~230 | Quant toolkit: six-step discipline, formulas, mental math, path choice, sanity checks, market sizing, difficulty calibration |
| `references/case-taxonomy.md` | ~453 | 14 archetypes + mixed cases, each with objective/signals/modules/diagnostic tree/quant/exhibits/insights/mistakes/combinations |
| `references/case-generation.md` | ~225 | Blueprint protocol, backwards design, exhibit & quant design, 14-point consistency checklist, user-provided cases, difficulty matrix, replacement-case rules |
| `references/interview-mode.md` | ~243 | Interviewer protocol, prohibitions, information release, allowed moves, error handling, tone, both format spines, feedback report, incomplete/debrief report |
| `references/tutorial-mode.md` | ~273 | Teaching loop, beginner curriculum, drills, hint ladder L0–L4, error-type diagnosis, demonstration, assistance levels, session review, learner profile schema |
| `references/evaluation-rubric.md` | ~253 | Six dimensions × behavioural anchors at 1–2/3–4/5–6/7–8/9–10, non-averaging hire bands, incomplete-case rules, Tutorial mastery levels |
| `references/research-notes.md` | ~144 | Source tiers; what came from official material vs convergent prep sources vs design abstraction |

Validated by `skill-creator/scripts/package_skill.py` — passes.

## Core state design (post-iteration)

Three orthogonal concepts, never conflated:

- **Mode** — purpose + evaluation semantics. Fixed for the session.
- **State** — current phase. Mutable.
- **Assistance Level** — help allowed right now. Mutable.

```
INTERVIEW
Setup ─▶ Active Interview ─▶ Final Recommendation ─▶ Feedback ─▶ Complete
             └─(abort)─▶ Debrief ─▶ Complete ─(opt)─▶ Post-Debrief Practice [not a valid mock]

TUTORIAL
Setup ─▶ Guided ⇄ Assisted ⇄ Light ⇄ Independent ─▶ Session Review ─▶ Complete
```

One-way edge: **Active Interview → Debrief**. Once answers are revealed the case is spent; a real
re-test requires a new session and a newly generated case (same archetype and difficulty,
different industry, data and root cause).

## Scenario validation

| # | Scenario | Handled by | Result |
|---|---|---|---|
| 1 | Beginner + Tutorial | tutorial §2 (11-step curriculum, diagnostic mini-prompt first) | ✅ |
| 2 | Tutorial + structuring drill | tutorial §3, methodology §2.4 quality bar | ✅ |
| 3 | Tutorial + quant | tutorial §3, case-math §1 setup-first drill | ✅ |
| 4 | Tutorial + exhibit | tutorial §3, methodology §4.1–4.2 | ✅ |
| 5 | Tutorial + full guided case | tutorial §1 loop + case-generation blueprint | ✅ |
| 6 | Tutorial + independent practice | tutorial §7.1–7.2, `independence_marker` | ✅ |
| 7 | Interview + interviewee-led | interview §7.1 (no summarising for candidate, no next-step suggestions) | ✅ |
| 8 | Interview + interviewer-led | interview §7.2 (9-step spine, explicit "not a quiz" guard) | ✅ |
| 9 | Chinese case | SKILL §3.3 (mirror language, keep practitioner terms in English) | ✅ |
| 10 | English case | SKILL §3.3 | ✅ |
| 11 | User-uploaded case | case-generation §7 (read fully first, then partition) | ✅ |
| 12 | User-uploaded interviewer guide | case-generation §7 partition table + per-mode release rules | ✅ |
| 13 | Interview + realtime feedback request | SKILL §4.3 three-option response, said once in full | ✅ |
| 14 | Interview + hint request | SKILL §4.3; distinguished from abort in §4.1 | ✅ |
| 15 | Interview → Tutorial request | SKILL §4.3 — refuse the switch, offer the debrief | ✅ |
| 16 | Tutorial → Interview request | SKILL §5.4 — finish session, new session, new case | ✅ |
| 17 | Early termination | SKILL §4.1 + interview §9 (6-part debrief + incomplete assessment) | ✅ |
| 18 | New session, different mode | SKILL §3.6 session boundaries; carry profile + seen-cases, not state | ✅ |
| 19 | Full setup already given | SKILL §3.1 — never re-ask; "random formal mock" is complete | ✅ |
| 20 | Multi-turn data consistency | case-generation §1 blueprint-first + §6 14-point check + "case does not bend" (interview §5) | ✅ |

## Targeted risk checks

- **Mode genuinely fixed?** Yes. Debrief and Independent Practice are explicitly *within* their
  mode (SKILL §1 consequences list, tutorial §7.2, interview file header).
- **Hidden mode switching?** Blocked at three points: SKILL §0 rule 1, §4.3, §5.4. Tutorial never
  issues a hiring band even on request (rubric §9.2); Interview never teaches while live
  (interview §2 explicit prohibition list, including tone words).
- **Interview Mode teaching leakage?** interview §2 bans the specific phrases; §6 bans affect
  ("candidate must not infer their score from your tone"); §5 bans correction and specifies the
  softest realistic intervention for a poisoning math error, logged as an assist.
- **Tutorial actually teaches?** Loop mandates user attempt before explanation; explicit
  anti-pattern named ("writing the model answer and asking 'make sense?'"); retry-after-diagnosis
  called out as the most-skipped step.
- **Hidden info leakage?** interview §3 whitelist; "never invent a number not in the blueprint";
  red herrings resolved honestly rather than steered away from.
- **Data consistency?** 14-point pre-flight; explicit rule that the root cause does not move to
  match the candidate's hypothesis.
- **Scoring behaviourally grounded?** All 30 anchor bands describe observable behaviour; verdict
  explicitly non-averaging with fatal-mistake caps and an assist-count input.
- **Framework templating avoided?** methodology §2.1 principle, §2.3 15-industry driver table,
  §2.5 failure modes; research-notes §5 records the deliberate refusal to ship a framework library.

## Open items for a future iteration

- No firm-name → format lookup by design; if you want "McKinsey mode" as a shortcut it would be a
  one-line setup mapping, but the underlying setting stays Interview Format.
- Written-case / presentation format (BCG-style) is not implemented as a distinct format.
- Behavioural/PEI/fit interviews are out of scope.


---

## Rev 2 audit — completeness re-check against the original spec

Triggered by an interrupted first run. Every numbered requirement of the original brief was
re-checked against the files on disk.

### Confirmed already complete

- §22 blueprint fields — all 23 present.
- §23 consistency check — all 10 required checks present, plus 4 more.
- §14 Tutorial focus areas — all 16 present.
- §16 error-diagnosis types — all 10 present, plus 2.
- §15 hint ladder L0–L4, §17 demonstration tiers, §18 progressive independence — present.
- §28 Interview feedback components — all 7 present, plus an interviewer-assistance log.
- §29 Tutorial session summary — all 7 present.
- §31 difficulty system incl. natural-language mapping — present.
- §32 anti-templating incl. all five named industries — present, extended to 15.
- §3.1 case taxonomy — all 13 named archetypes + mixed cases, all 9 required fields each.
- §5 case math — all 24 named concepts present.
- §36 research documentation — present.

### Gaps found and closed

| # | Gap | Spec ref | Fix |
|---|---|---|---|
| 1 | Beginner curriculum was an 11-item list; missing the **Business fundamentals** block (revenue, cost, profitability, customer, competition, market, business models) and the **practice progression ladder** | §30 | `tutorial-mode.md` §2 rewritten: six named blocks, 32 items, plus §2.1 six-rung progression ladder (Guided modules → Guided full case → Assisted full case → Light → Independent Tutorial case → separate Interview session), with rung 6 explicitly outside Tutorial Mode |
| 2 | Geography existed as a state field with no behavioural consequence | §20 | New `case-generation.md` §10 — option list, and what geography must change: currency/units, market scale plausibility, competitive landscape, channel and consumer behaviour, regulation; explicitly independent of session language; called out as biting hardest in market sizing. Wired into `SKILL.md` §3.1 |
| 3 | Exhibit design covered chart *forms* only, not the required *content* types | §26 | `case-generation.md` §4 — added a 10-row content-type table (P&L, cost bridge, customer segmentation, competitor data, market data, operational metrics, survey, geographic, time series, benchmark) and extended the form list |
| 4 | `evaluation-rubric.md` header pointed at §5/§6/§7 after sections were renumbered — a live mis-navigation bug | — | Corrected to §7/§8/§9 |

### Automated checks run

- Cross-reference resolver over all 9 files: every `file.md §n` and `SKILL.md §n` pointer
  resolves to an existing section. (First run of this check is what surfaced gap 4.)
- Contradiction scan on the two highest-risk rule families — who may give hints/teaching, and who
  may issue a hiring verdict. No conflicting statements across files.
- `skill-creator/scripts/package_skill.py` validation: passes.

Final size: 2,638 lines across SKILL.md + 8 reference files.

---

# Iteration 3 — HTML Report System

**Scope check.** The six methodology files (`case-methodology`, `case-math`, `case-taxonomy`,
`case-generation`, `evaluation-rubric`, `research-notes`) are byte-identical to the previous
revision — verified by diff, 0 changed lines. `interview-mode.md` and `tutorial-mode.md` each
gained a delivery-step pointer only (3 lines / 4 lines); no in-session rule, teaching rule or
scoring anchor was touched. `SKILL.md` gained one file-table row and one bullet in §10.

**Note on framing.** The request described this as upgrading "the existing Interview-Mode-only
HTML requirement". There was no HTML requirement in the skill before this iteration — session
deliverables were text. This is a new subsystem, not a widening of an old one.

## Added

- `references/report-system.md` — the spec: workflow, guard rails, Session Report JSON schema
  (shared / [I] / [T] field marks), per-mode section requirements, visual system, anti-fabrication
  rules, chat delivery.
- `scripts/build_report.py` — JSON → single self-contained HTML. Two templates, one design system.

## Why a renderer instead of prose instructions

Three requirements are only enforceable in code: Tutorial reports must never carry a hiring band,
untested dimensions must never get a number, and no fabricated benchmarks. Prose rules degrade
under generation pressure; a script that strips an illegal verdict and prints a warning does not.
The script is also what keeps the two report types visually one system while structurally
different.

## Design decisions

- **Score = magnitude, so length encodes it and text carries the band.** No traffic-light colour
  on scores — that is what makes a report read as a game page rather than an analyst document.
- **Independence is a 4-segment ordinal block plus its label**, legible in greyscale and print.
- **Palette validated, not eyeballed.** Ordinal blue ramps run through the data-viz validator:
  light `#86b6ef → #104281` and dark `#184f95 → #9ec5f4`, ALL CHECKS PASS in both modes.
- **No hover-only content.** Every value is directly labelled, so the print/PDF requirement and
  the no-JS requirement fall out for free rather than needing a fallback.
- **Print pagination**: `break-inside: avoid` on inner blocks (`.dim`, `.moment`, `.hint`, `.pri`,
  `.hero`) rather than on whole sections — sections were being pushed wholesale to the next page,
  wasting ~1 page in 6. Headings carry `break-after: avoid` so none are orphaned.

## Scenario coverage

| # | Scenario | Fixture | Result |
|---|---|---|---|
| 1 | Interview, complete, strong | `iv_strong` (zh) | 7.4 / Hire, six dimensions, full sections |
| 2 | Interview, complete, weak | `iv_weak` (en) | 3.8 / No Hire |
| 3 | Untested dimensions | `iv_untested` | dashed empty track, "not tested", no number |
| 4 | Heavy interviewer assistance | `iv_weak` | 4 logged prompts, level = substantial |
| 5 | User aborts mid-case | `iv_abort` | red incomplete badge + stage |
| 6 | Too thin for a verdict | `iv_abort` | "insufficient information" + reason, no band |
| 7–9 | Beginner / guided / assisted tutorial | `tu_mix` | guided→independent, no hiring band |
| 10 | Switches to zero-assistance mid-session | `tu_mix` | marker rendered, phases split |
| 11 | Fully independent tutorial | `tu_solo` (en) | independent-only phase card |
| 12 | Recurring errors | `tu_mix` | recurring list, all `new` (no history to claim) |
| 13 | Hint → independent progression | `tu_mix` | `L3 → L2 → L1 → Independent` track |
| 14 | Single-module session | `tu_solo` | 2 dimensions only, rest absent |
| 15–16 | zh / en | both | full label sets |
| 17–18 | Mobile 390px / desktop 1100px | rendered | columns collapse, grids stack |
| 19 | Offline | grep | zero external refs — no URL, CDN, font, script |
| 20 | Print / PDF | Chromium | A4, 5 and 4 pages, no split cards, colour retained |

**Guard-rail tests (must fail loudly):**

| Test | Fixture | Result |
|---|---|---|
| Tutorial with a hiring verdict, no benchmark flag | `tu_bad` | verdict stripped, warning printed, 0 occurrences of "Hire" in output |
| Fabricated benchmark in diagnosis text | `iv_fab` | 2 warnings raised (`超过 N%`, `录取概率`) |

## Known limits

- The fabrication detector is a regex list — it catches the named patterns, not every possible
  invented statistic. It is a backstop for §7, not a substitute for it.
- Dark mode is implemented but print always forces light, per the "no large dark areas" rule.

---

# Iteration 4 — Public release readiness

Scope: licensing, install experience, runtime robustness, input validation, reproducible tests,
environment compatibility, source verifiability, documentation. Case methodology, mode/state
mechanics, teaching logic, case generation and the scoring anchors are unchanged.

## The central change: warnings became failures

The previous iteration detected guard-rail violations and *warned* while still writing the HTML at
exit 0. That is the wrong default for a tool whose output a person will read as an assessment of
themselves: a warning on stderr is invisible to the reader of the report, and an agent that
ignores stderr delivers the violating report anyway.

Validation now runs before rendering, and any failure aborts the build: no file, a `ValidationError`
naming the field, its value and the legal range, exit code 2.

The distinction that makes this workable is between **escaping** and **rejecting**:

- *Untrusted text* — a case answer containing `<script>` — is escaped and rendered. This is a
  rendering concern, is always safe, and never fails the build.
- *Unsupported claims* — a percentile, an offer probability, an invented firm benchmark — abort
  the build. No amount of escaping makes the sentence true.

The guard-rail scan was also re-scoped. Previously it searched the whole document, which would
have rejected a case that legitimately discusses an industry average. It now searches only
evaluative prose — the text where the skill judges the user — because that is where an unsupported
claim actually does damage. `GuardRailScopeTests` pins both halves of that behaviour.

## Validation surface

Enums (mode, completion, assistance level, independence, verdict), score type and range (finite,
0–10, no strings, no `NaN`), and five semantic rules: untested dimensions cannot carry a score; a
tutorial report cannot carry a hiring band without an explicit benchmark request; mode-specific
fields must appear only in their own report type; `verdict_available: false` cannot coexist with a
verdict and requires a written reason; an aborted session cannot carry a verdict without an
explicit availability flag.

The mode-specific field check is worth noting: an interview-only key in a tutorial report is not a
cosmetic problem, it means the report object was assembled from the wrong template and would
render misleading semantics. Rejecting it catches that class of bug at the boundary.

## Working-directory independence

The renderer previously appeared in docs as `python3 scripts/build_report.py`, which silently
assumed the process was running from the skill root. In real use the working directory is the
user's own project. Fixed on both sides: the script anchors `SKILL_ROOT` to `__file__` and gained
`--example` and `--skill-root`, and `report-system.md` §1 now specifies absolute invocation with a
resolution recipe. `test_example_flag_is_cwd_independent` and `test_skill_root_resolves_from_script_location`
run from a temporary directory to keep it honest.

## Reproducibility

The previous notes named fixtures (`iv_strong`, `tu_mix`, …) that existed only in a scratch
directory, and the renderer's provenance comment cited `scripts/validate_palette.js`, which was a
tool in a different skill and was never part of this repository. Both were claims a reader could
not check.

Fixed by committing the material rather than deleting the claims: 6 valid and 18 invalid fixtures
under `tests/fixtures/`, and `tests/test_build_report.py` (20 tests, stdlib `unittest`). The
palette assertions the JS validator used to cover are now `PaletteTests`, computed in Python from
the ramps the CSS actually uses — so the property is verified in the repository that depends on it,
without adding a Node.js dependency.

## Sources

Every cited URL was fetched and confirmed before being written down. One casualty:
`bain.com/careers/hiring-process/interviewing/coffee-shop-co/` — a plausible-looking URL inferred
from the case name — returns 404. The real Bain practice-case path is `fashion-case-study`. That is
exactly the failure mode the "verify, never infer" rule exists to prevent.

The Tier 3 claim was also corrected. The earlier notes cited "openly published university
consulting-club casebooks"; the case-architecture knowledge that is actually traceable comes from
the firm-published sample cases in Tier 1, so Tier 3 now says that. Sources that cannot be linked
and opened are explicitly excluded rather than listed for weight.

## Graceful degradation

`project_search` / `project_read` / `project_write` are not universal. `SKILL.md` §3.4 now treats
them as optional: absent, the skill skips profile persistence silently — no error, no prompt to
enable anything, no effect on the session, the case, the scoring or the report. The only loss is
cross-session continuity, and the existing rule against claiming untracked trends already covers
the reporting consequence.

## Test results

`python3 -m unittest discover -s tests` — 20 tests, all passing. Coverage: both examples render;
cwd independence; all six valid fixtures render at exit 0; untested dimensions show N/A; aborted
sessions carry no verdict; tutorial reports never show a hiring band; independence and hint tracks
render; markup is escaped not executed; output has no external references; all 18 invalid fixtures
exit 2 with no file written; error messages name the offending field; malformed JSON and missing
files exit 1; guard-rail scope; palette ramp properties.

## Deliberately not done

- **No new dependencies.** Validation, tests and palette checks are all stdlib. The repository
  still has nothing to install.
- **No `--strict` flag.** A bypass that exists will eventually be used. Strict is the only mode.
- **No generated HTML committed.** The examples are JSON; the HTML is one command away and would
  otherwise drift out of sync with the renderer.
