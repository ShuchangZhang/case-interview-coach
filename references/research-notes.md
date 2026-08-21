# Research & Methodology Notes

What this skill's methodology rests on, and which parts are design abstraction rather than
sourced fact. Principles are recorded here, not source text.

---

## 1. Source tiers used

**Tier 1 — Firm official recruiting material.** The highest-authority input on how real
interviews behave and what they assess. McKinsey's interviewing page and its published sample
cases; BCG Careers' case interview preparation page and its interactive practice cases; Bain's
interviewing and case-interview preparation pages and its published practice cases.

**Tier 2 — Established preparation methodology.** Widely-used preparation resources, consulted to
find where independent sources *converge* on frameworks, structuring, case math, exhibits,
brainstorming, synthesis and scoring. No single provider's framework set was adopted.

**Tier 3 — Case architecture.** How a case is assembled: how an interviewer guide separates
candidate-facing from interviewer-only information, how exhibits and math modules are embedded,
how progression and insight chains are built. This came from the **firm-published sample cases in
Tier 1**, which are the openly available examples that include interviewer guidance.

No case content is reproduced in this skill. Nothing was drawn from material that prohibits
copying, redistribution, or use with generative AI.

### 1.1 Cited sources

Verified as reachable on the access date below. Where a claim in this skill rests on a specific
source, it rests on one of these.

| Source | Page | URL | Accessed | Supports |
|---|---|---|---|---|
| McKinsey & Company | Interviewing at McKinsey — Tips and Resources | https://www.mckinsey.com/careers/interviewing | 2026-08-21 | What a case interview is; what is assessed; that cases are client scenarios |
| McKinsey & Company | Talbot Trucks (sample case) | https://www.mckinsey.com/careers/interviewing/talbot-trucks | 2026-08-21 | Real case architecture; question-type sequence; interviewer-led progression |
| Boston Consulting Group | Consulting Case Study Interview Preparation | https://careers.bcg.com/global/en/case-interview-preparation | 2026-08-21 | Case interview format; that there is often no single right answer; assessed behaviours |
| Bain & Company | Interviewing | https://www.bain.com/careers/hiring-process/interviewing/ | 2026-08-21 | Case interview as assisted problem-solving; assumptions and quick math |
| Bain & Company | Preparing for the Case Interview | https://www.bain.com/careers/hiring-process/case-interview/ | 2026-08-21 | Clarify objective, structure thinking, think aloud, listen and adapt |
| Bain & Company | FashionCo. (practice case) | https://www.bain.com/careers/hiring-process/interviewing/fashion-case-study/ | 2026-08-21 | Case architecture for a revenue-decline diagnostic |
| PrepLounge | The Complete Guide to Your Case Interview Preparation | https://www.preplounge.com/en/case-interview-basics | 2026-08-21 | Case-type taxonomy; structuring and MECE; case math inventory |
| Hacking the Case Interview | Case Interview Frameworks: The Ultimate Guide (2026) | https://www.hackingthecaseinterview.com/pages/case-interview-frameworks | 2026-08-21 | Tailored-over-memorised structuring; framework quality criteria |

**Usage note.** Tier 1 and Tier 2 pages are cited as references, in the ordinary sense of citing a
publicly readable web page. No page's text, exhibits or cases are reproduced here; what is
recorded in this skill are principles restated in our own words, plus the design decisions in §4.

**On sources not cited.** Other well-known preparation material — including books consulted only
through second-hand summaries — informed general familiarity but is deliberately **not** listed
above, because a citation the reader cannot open and check is not a citation. Where this skill
states a convergent conclusion (§3), the convergence claim rests on the cited sources.

---

## 2. What comes from official firm material

These are treated as the highest-authority inputs on real interview behaviour:

- **The case is a client scenario, not a puzzle.** Firms describe it as working a realistic
  business challenge the way an engagement would.
- **There is often no single right answer**; the assessed object is the *approach and quality of
  reasoning*. (BCG states this explicitly.) → Why this skill scores process dimensions rather than
  answer-matching.
- **The behaviours firms name**: listen actively, think structurally, communicate clearly, state
  assumptions explicitly, show your thinking, ask thoughtful questions, analyse data, perform
  quick calculations, identify what matters most. → These map directly onto the six rubric
  dimensions.
- **The named failure behaviours**: panicking, rushing, overcomplicating, ignoring the
  interviewer's feedback, going silent, interrupting. → Included in the Communication anchors.
- **Real case architecture**, from the published sample cases: a business context, then a
  sequence of distinct question types — an information/structuring question, a qualitative
  judgment question, a no-calculator math question with given figures, and an exhibit
  interpretation question with a "what would you do next" follow-up. Talbot Trucks and Beautify
  both follow this shape. → The interviewer-led progression spine in `interview-mode.md` §7.2 and
  the module design in `case-generation.md` are built on it.
- **No calculators**, and explicit encouragement to talk the interviewer through each step. →
  `case-math.md` §1 and §7.
- **Structuring is given real time** — take time to organise before answering. → The soft time
  budgets.

---

## 3. What is a convergent conclusion across multiple Tier 2 sources

Adopted because independent sources agree, not because any one of them says it:

- **The five-stage case arc**: brief → clarification → structure → analysis → synthesis.
- **Structure as a tailored hypothesis tree, not a template.** Every serious source now warns
  that memorised frameworks are visible to interviewers and cap the score; modern cases are
  deliberately designed to break standard frameworks.
- **Interviewer-led vs interviewee-led as a format variable, not a firm identity.** McKinsey is
  historically interviewer-led and BCG/Bain candidate-led, but sources also report Bain moving
  toward interviewer-led for consistency and Oliver Wyman using both — which is why this skill
  makes format a **setting**, not a lookup from a firm name.
- **Interviewer-led cases are not easier.** Less room to recover; each answer scored more
  independently.
- **Structure quality = broad + deep + insightful**, with 3–4 top-level branches and 2–3
  sub-drivers, plus prioritisation and a stated hypothesis. Fourteen buckets reads as an
  inability to prioritise.
- **Exhibit work is scored on interpretation, not description** — reading data aloud earns
  nothing. Hence the observation/insight distinction, which multiple sources make in near-identical
  terms.
- **Brainstorming tests structured creativity**, not idea count: organise into MECE buckets
  first, 3–5 buckets, 2–3 specific ideas each, then prioritise.
- **Synthesis is answer-first (Minto/Pyramid): recommendation → 2–3 evidenced reasons → risks →
  next steps, in 60–90 seconds.** Sources converge tightly on both the structure and the duration.
- **The recurring fatal math errors** are consistent across sources: fixed cost ÷ price instead of
  ÷ contribution margin; averaging percentages instead of weighting; LTV on revenue instead of
  gross profit; forgetting to subtract the initial investment in NPV; simple average growth
  confused with CAGR.
- **Market sizing is graded on structure, assumptions and sanity-checking, not precision**, and
  durable-goods sizing requires replacement-cycle logic.
- **Scoring is multi-dimensional with a low floor**: a single weak dimension typically blocks an
  offer even alongside strong ones — which is why §7.1 of the rubric makes the verdict
  non-averaging.

---

## 4. What is design abstraction (this skill's own decisions)

These are not claims about how firms operate. They are choices made so the skill runs well.

- **The 1–10 scale with behavioural anchors.** Real firm forms are typically 1–4 or 1–5 with
  private descriptors. A 10-point scale was chosen for feedback granularity; the band mapping in
  `evaluation-rubric.md` §7.2 is calibrated so that ~7 corresponds to "meets the bar," matching
  the "3 of 4" threshold reported by Tier 2 sources.
- **Six dimensions.** Sources list anywhere from four to seven, with different cuts (some split
  hypothesis management and creativity out separately). Six was chosen as the smallest set that
  covers everything sources assess without producing dimensions too thin to anchor behaviourally;
  creativity is folded into Business Judgment & Insight, hypothesis management into Structuring
  and Judgment.
- **The Mode / State / Assistance Level separation**, mode locking, the one-way Debrief
  transition, and the rule that a debriefed case cannot yield a valid assessment. No source
  discusses this — it exists because an AI interviewer can trivially slide into tutoring, and
  because a candidate who has seen the answer key cannot be validly assessed on that case.
- **Soft time budgets.** Real interviews are hard-timed; text chat is not. The budgets are derived
  from reported per-stage guidance (60–90s structuring reflection, 30–60s exhibit reading,
  60–90s recommendation) and applied as observation rather than enforcement.
- **The industry-economics driver table** in `case-methodology.md` §2.3. Assembled from general
  industry knowledge to prevent framework templating; not sourced from any single prep resource.
- **The case archetype entries** in `case-taxonomy.md`. Synthesised across sources and then
  extended (diagnostic trees, red-herring design, combination patterns) beyond what any one
  source provides.
- **The blueprint-first generation protocol and the consistency checklist.** Abstracted from how
  published casebooks and firm sample cases are constructed, then formalised into a pre-flight
  check because the failure mode of an AI interviewer is improvised, mutually inconsistent numbers.
- **The Socratic hint ladder (Levels 0–4) and the error-type taxonomy.** Standard tutoring
  practice adapted to case interviewing; the specific levels and error categories are this skill's
  formulation.
- **The learner profile schema** and cross-session persistence.

---

## 5. Deliberate non-decisions

- **No firm-specific templates.** Firm differences are expressed through the Interview Format
  setting, the degree of interviewer prompting, and challenge intensity — never through a
  "McKinsey framework." Firm styles change; the underlying skills do not.
- **No canonical framework list.** Building blocks and lenses only. A skill that shipped a
  framework library would teach exactly the behaviour every source says interviewers penalise.
- **No claim of official endorsement.** Nothing here is approved by any consulting firm, and the
  scoring bands are a training instrument, not a firm's real hiring process.

---

## 6. Currency

Researched August 2026. Firm formats change — assessment games and screening tools especially.
The methodology base (structuring, math, exhibits, synthesis, evaluation) is stable; the
format-specific details in `interview-mode.md` §7 are the parts most worth re-checking over time.
