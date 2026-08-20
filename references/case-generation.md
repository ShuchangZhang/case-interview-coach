# Case Generation

A case is designed before it is delivered. **Never improvise numbers turn by turn** — that is how
cases become internally inconsistent, and inconsistency destroys the exercise.

---

## 1. Blueprint first

Build the complete blueprint internally **before** the opening prompt. Do not show it to the user.

```
CLIENT
  name (fictional), industry, business model, scale (revenue, volume, employees, footprint)
  geography, competitive position, ownership
SITUATION
  what changed, when, over what period; who is asking and why now
OBJECTIVE
  the decision or target, with a metric and a time frame
  (the candidate's recommendation must be answerable in these terms)
CORE PROBLEM
  one sentence
ROOT CAUSE
  the true underlying driver — fixed, never changes mid-case
DIAGNOSTIC PATH
  the chain of questions that leads from the prompt to the root cause
CANDIDATE-FACING FACTS
  what's in the prompt; what's given on a reasonable clarification
HIDDEN FACTS
  released only when the candidate's analysis reaches them, tagged with the trigger
EXHIBITS
  1–3 for a full case; each with title, axes, units, full data, and the intended insight
QUANT MODULES
  1–3; each with question, given inputs, required assumptions, solution path, answer,
  acceptable range, and the business implication
EXPECTED INSIGHTS
  what a strong candidate concludes at each stage
ALTERNATIVE HYPOTHESES
  plausible wrong paths, and the data that disproves each
RED HERRINGS
  facts that look decisive and aren't; each must have a real, checkable resolution
BRANCH LOGIC
  if the candidate goes to A → give X; to B → give Y; to C (blind alley) → give the honest
  unhelpful data
FINAL RECOMMENDATION
  the model answer: verdict, 2–3 evidenced reasons, risks, next steps
RISKS / NEXT STEPS
INTERVIEWER PROMPTS
  the minimal nudge available at each stage, phrased as direction not conclusion
EVALUATION EXPECTATIONS
  what distinguishes a 4, a 7 and a 9 answer at each stage of this specific case
```

---

## 2. Design the case backwards

1. Choose the **insight** you want the candidate to reach — the "aha" that makes the case worth
   solving. (E.g. "the cost increase is entirely a volume-driven fixed-cost effect; the real
   problem is on the demand side.")
2. Choose the **root cause** that produces it.
3. Build the **numbers** that make the root cause true and the alternatives false.
4. Build the **exhibits** that carry the evidence, without stating the conclusion.
5. Build the **prompt** that hides it in plain sight.
6. Add **alternative hypotheses** that are genuinely plausible from the prompt and are killed by
   specific data.
7. Add a **red herring** only if it has a clean resolution.

A case designed forwards ends with numbers that don't add up. A case designed backwards ends with
a real insight.

---

## 3. Objective design

The objective must be:

- **Specific** — "decide whether to enter the Indonesian market" not "look at growth."
- **Measurable** — a target, threshold, hurdle rate, or decision criterion.
- **Answerable** — a yes/no or a number, so the final recommendation can be judged against it.
- **Time-bound** where it matters.

Good: *"Our client wants to know whether to acquire Meridian at the €340m asking price, given a
minimum 3-year payback on their acquisitions."*
Weak: *"Our client wants to improve their business."*

---

## 4. Exhibit design

- One exhibit answers one question. Don't stack three insights in one chart.
- **Title states what is plotted, never what it means.** "Gross margin by customer segment,
  FY2025 (%)" — not "Segment C is unprofitable."
- Units, currency, time period and axis labels always present. Footnote when a definition matters.
- Include a small number of data points the candidate must *use* — not decoration.
- Require a calculation from the exhibit (a share, a growth rate, a per-unit figure) at
  intermediate difficulty and above.
- Exhibit numbers must reconcile with every number already given and with the final answer.
- Vary form across the case: table, bar, stacked bar, line, waterfall, scatter, 100% stacked,
  Mekko, bubble, pie (sparingly), histogram.
- Vary **what the exhibit contains**, not just its shape. The usable content types:

  | Content type | Typical use |
  |---|---|
  | P&L / income statement | profitability, turnaround, due diligence |
  | Cost breakdown or bridge | profitability, cost reduction, operations |
  | Customer segmentation | growth, pricing, market entry, new product |
  | Competitor data (share, price, cost position) | competitive response, entry, pricing |
  | Market data (size, growth, profit pool) | entry, growth, transformation |
  | Operational metrics (capacity, utilisation, yield, cycle time) | operations, supply chain |
  | Survey / voice-of-customer data | pricing, new product, satisfaction |
  | Geographic / store-level data | footprint, network design, turnaround |
  | Time series (trend, cohort, adoption curve) | growth, disruption, retention |
  | Benchmark comparison | cost reduction, performance diagnosis |
- At advanced/MBB difficulty, include one exhibit whose obvious reading is wrong (an axis
  truncation, a mix effect, a base-rate trap) — but make the correct reading fully derivable.

---

## 5. Quant module design

Each module needs: a business question (not "compute X"), the inputs, the path, the answer, an
acceptable range, and the implication.

- The question should arise naturally from where the case is: "How much would volume need to grow
  to offset the price cut?" beats "Calculate the breakeven volume."
- Numbers should be workable without a calculator: round figures, clean divisions, results that
  land on recognisable values.
- Difficulty comes from **setup complexity**, not arithmetic ugliness (`case-math.md` §8).
- Every module ends with an interpretation question, explicit or implied.
- Check the answer twice before opening the case.

---

## 6. Consistency check — run before delivering

Verify all of the following. If any fails, fix the blueprint before the case starts.

- [ ] Revenue = Price × Volume everywhere it appears
- [ ] Profit = Revenue − Cost everywhere it appears
- [ ] Margins recompute correctly from the underlying figures
- [ ] Percentages sum to 100 where they should; segment values sum to the stated total
- [ ] Market shares are ≤ 100% and consistent with the market size given
- [ ] Growth rates are consistent with start and end values
- [ ] Units and currency are consistent across prompt, exhibits and dialogue
- [ ] Every exhibit reconciles with every fact already stated
- [ ] The quant answers actually come out of the given inputs
- [ ] The root cause is genuinely provable from the released data
- [ ] Each alternative hypothesis is genuinely disprovable from data the candidate can obtain
- [ ] The final recommendation is supported by numbers that appear in the case
- [ ] The scale is plausible for the industry (margins, headcount, price points, market size)
- [ ] Nothing in the prompt gives away the root cause

**During the case:** if a candidate asks for data that was never designed, either derive it
consistently from the blueprint or say it isn't available. Never invent a figure that contradicts
the blueprint, and never adjust the root cause or the data to match the candidate's hypothesis.

---

## 7. User-provided cases

When the user supplies a case (PDF, screenshot, pasted text, casebook page, interviewer guide,
answer key):

1. **Read it fully first**, before any interaction.
2. **Partition the content** explicitly:

   | Candidate-facing | Interviewer-only |
   |---|---|
   | opening prompt, background | interviewer guide and instructions |
   | data released on request | the answer key and solution |
   | exhibits, at their proper moment | expected insights and framework |
   | the questions asked | math solutions and hidden data |
   |  | evaluation guidance |

3. **Interview Mode** — release strictly by the guide's own trigger points. Never quote or
   paraphrase the answer key before Feedback or Debrief. If the material also contains "what a
   good answer looks like," it is scoring material, not case material.
4. **Tutorial Mode** — use interviewer-only material progressively as teaching requires. Even
   here, do not dump the full solution at the start; the user's attempt must come first.
5. **Gaps** — if the material lacks something needed (an exhibit is unreadable, the guide is
   missing, math is incomplete), say so once, and either fill the gap with clearly-labelled
   generated material or run the case without that module. Don't silently invent.
6. **Contradictions in the source** — if the user's material is internally inconsistent, run it as
   written, note the inconsistency at Feedback/Debrief, and don't let it corrupt the scoring.
7. **Copyright** — work from the material the user supplies for their own practice. Do not
   reproduce large verbatim extracts of copyrighted casebooks into the session beyond what the
   exercise needs, and do not use material the user flags as prohibited from AI input.

---

## 8. Difficulty calibration

Difficulty is a property of ambiguity and structure, not of arithmetic.

| Dimension | Beginner | Intermediate | Advanced | MBB |
|---|---|---|---|---|
| Objective clarity | explicit, single | clear, one metric | some ambiguity | ambiguous; must be defined |
| Structure | 2–3 obvious branches | 3–4, some tailoring | tailoring required | non-obvious economics |
| Data | all given | mostly given | must be requested | must be requested and derived |
| Exhibits | 1 simple | 1–2 | 2–3, one requires calc | 2–3, one misleads on first read |
| Math | 1 step, clean | 2–3 steps | multi-step, path choice | path not obvious + sensitivity |
| Competing hypotheses | none | one | two plausible | two plausible + a red herring |
| Irrelevant info | none | little | some | substantial |
| Prioritisation | not required | light | required | required and defended |
| Synthesis | prompted | prompted | expected unprompted | expected, and challenged |
| Interviewer challenge | none | gentle | real pushback | sustained; strong answers challenged too |

Natural-language mapping: "第一次练"/"first time" → Beginner. "简单一点" → drop one level.
"quant 多一点" → keep level, add a module. "final round" → Advanced/MBB with sustained challenge.
"图表难一点" → raise exhibit dimension only. "少提示" → reduce prompt availability, not difficulty.

---

## 9. Generating a replacement case after a debrief

When a user has debriefed a case and wants a genuine re-test:

- **Same or adjacent archetype**, **comparable difficulty**, so the skill being tested is the same.
- **Different industry, different client, different numbers, different root cause.** If the first
  case's answer was "channel mix," the new one must not be channel mix.
- Different exhibit forms and a different quant module type.
- Check the learner profile's "Avoid repeating" list first.

The point is to test the same capability without testing recall of a known answer.

---

## 10. Geography and localisation

Geography is a real setup dimension, not decoration. Ask for it only when it isn't obvious and
would change the case; otherwise pick one that fits the archetype and say so in the prompt.

Options: **Global · China · US · Europe · Southeast Asia · India · Middle East · user-specified.**

Once chosen, it must be carried through consistently:

- **Currency and units** — RMB/¥ and 万/亿 for China; $ for US; € for Europe; metric vs imperial;
  local units of trade (square metres vs square feet, litres vs gallons).
- **Market scale** — population, GDP per capita and category penetration must be plausible for
  that market. A "national" market size in China and in Sweden differ by two orders of magnitude,
  and a candidate with real business sense will notice if they don't.
- **Competitive landscape** — the archetypal competitor set differs: platform-dominated
  e-commerce and super-app distribution in China; fragmented retail and franchise models in the
  US; regulatory fragmentation across European markets.
- **Channel and consumer behaviour** — livestream and social commerce, mobile payment penetration,
  tier-1 to tier-4 city structure in China; suburban big-box and drive-time catchments in the US.
- **Regulation and structure** — data rules, labour law, licensing, state ownership, tariffs —
  where they materially affect the decision, and only then.
- **Language of the case** is set separately (`SKILL.md` §3.3). A Chinese-language session may run
  a US case, and an English session may run a China case.

Market sizing modules are where geography bites hardest: the population, income and penetration
assumptions must be right for the stated market, and a sanity check against the local GDP or
comparable category is expected.

Default when unspecified: choose the geography where the case's economics are most natural, name
it explicitly in the opening prompt, and keep every number consistent with it.

---

## 11. Realism guardrails

- Fictional client names and fictional data. Do not attribute invented figures to real,
  identifiable companies. Real companies may be named as *context* (competitors, market
  conditions) only where the statements are general and accurate.
- Scale figures to real industry norms — a regional grocery chain does not have a 40% net margin.
- Prefer concrete, textured detail (channel names, SKU counts, plant locations) over generic
  filler; it makes the case feel real and gives the candidate something to grip.
