# Case Math

Formulas are the smallest part of this file. Setup, path selection, sanity checking and
interpretation are what actually get scored.

---

## 1. The six-step discipline

Applies to every quantitative module, in both modes.

1. **Restate the question and the unit of the answer.** "You want the annual profit impact in
   euros." Wrong-unit answers are common and fatal.
2. **State the equation before touching a number.** "Payback = upfront investment ÷ annual
   incremental profit. I need the investment, the incremental revenue, and the incremental cost."
   This is the step that separates a quant score of 7 from a 4 — and it lets the interviewer
   correct the path before three minutes are wasted.
3. **Ask for or state the inputs**, including assumptions, with a one-line justification for each
   assumption.
4. **Compute, narrating.** Round deliberately and say so ("I'll use 250 instead of 248").
5. **Sanity check.** Order of magnitude, per-unit reasonableness, benchmark comparison,
   or an independent second route to the same number.
6. **Interpret.** "So payback is 3.4 years. Against their stated 3-year hurdle, this doesn't
   clear on the base case — which means the decision hinges on whether the revenue uplift can be
   pulled forward." A number without a "so what" is an incomplete answer.

---

## 2. Formula reference

### Profitability
```
Profit            = Revenue − Cost
Revenue           = Price × Volume
Gross margin %    = (Revenue − COGS) / Revenue
Operating margin  = EBIT / Revenue
Contribution margin/unit = Price − Variable cost/unit
Contribution margin %    = (Price − VC) / Price
Blended margin    = revenue-weighted average of segment margins   (NOT a simple average)
```

### Breakeven
```
Breakeven volume  = Fixed cost / Contribution margin per unit
Breakeven revenue = Fixed cost / Contribution margin %
Breakeven price   = VC/unit + (Fixed cost / expected volume)
Margin of safety  = (Actual volume − Breakeven volume) / Actual volume
Incremental breakeven for a change: Δ fixed cost / new contribution margin per unit
```
Most common error: dividing fixed cost by *price*.

### Growth
```
% change    = (New − Old) / Old
YoY growth  = (This year − Last year) / Last year
CAGR        = (End / Start)^(1/n) − 1
Rule of 72  : years to double ≈ 72 / growth rate (%)
Compounding shortcut: g% for n years ≈ n·g% + small correction upward
              (5% for 3 years ≈ 15.8%, not 15%)
```
Common error: averaging annual growth rates instead of compounding.

### Market
```
Market share       = Company revenue (or units) / Total market
Market size        = # target customers × purchase frequency × average price
Relative share     = Our share / Largest competitor's share
Share of growth    = Our incremental revenue / Total market incremental revenue
```

### Investment returns
```
ROI             = (Gain − Cost) / Cost
Payback (years) = Investment / Annual net cash inflow
NPV             = Σ [CFt / (1+r)^t] − Investment
Perpetuity      = CF / r
Growing perpetuity = CF / (r − g)
Simple valuation   = EBITDA × multiple,  or  Earnings × P/E
```
Common error: computing the present value of the cash flows and forgetting to subtract the
initial investment.

### Unit economics / subscription
```
CAC          = Sales & marketing spend / New customers acquired
LTV          = (ARPU × gross margin %) / churn rate      [per matching period]
LTV:CAC      = healthy ≈ 3:1;  <1:1 destroys value;  >5:1 may mean under-investment in growth
CAC payback  = CAC / (ARPU × gross margin %)   [months]
ARR          = MRR × 12
Net revenue retention = (start ARR + expansion − churn − downgrade) / start ARR
```
Common error: LTV computed on revenue instead of gross profit.

### Operations
```
Capacity        = units per hour × hours per period × # of lines/staff/machines
Utilisation     = actual output / maximum capacity
Throughput      = limited by the bottleneck step, never by the average
Yield           = good units / total units started
Productivity    = output / input (units per labour hour, revenue per employee)
Cost per unit   = total cost / units — always separate a total-cost move from a per-unit move
```

### Pricing
```
Price elasticity     = % change in quantity / % change in price
Revenue rises with a price cut only if |elasticity| > 1
Value-based price ceiling = customer's economic value (cost saved or revenue gained) from using it
Cannibalisation      = incremental units × margin_new − cannibalised units × margin_old
Net price            = list − discounts − rebates − returns − channel fees
```

### M&A
```
Cost synergies    = overlapping cost base × capture %
Revenue synergies = cross-sell base × attach rate × margin   (discount these; they rarely land)
Deal payback      = purchase price / (target profit + annual synergies)
Accretion test    = combined earnings / combined shares vs standalone EPS
```

### Sensitivity
```
Always ask: which single input, if wrong by ±20%, flips the decision?
Run the case on the pessimistic value of that input before recommending.
```

---

## 3. Mental math technique

- **Strip and reattach zeros.** 4,000 × 250 → 4 × 25 = 100 → add five zeros → 1,000,000.
- **×5 is ×10 ÷2.** ×25 is ×100 ÷4. ×15 is ×10 + half of that. ÷5 is ×2 ÷10.
- **Fraction ↔ percent:** 1/2=50, 1/3≈33, 1/4=25, 1/5=20, 1/6≈17, 1/7≈14, 1/8=12.5, 1/9≈11,
  1/12≈8.3, 1/20=5, 3/8=37.5, 2/3≈67.
- **Anchor and correct.** 97 × 43 → 100 × 43 = 4,300, minus 3 × 43 = 129 → 4,171.
- **Percent of a percent by multiplying decimals**, once, at the end — not sequentially.
- **Growth over few years:** add and correct upward, don't multiply out.
- **Track units in writing:** $/unit, units/year, $m. Most catastrophic errors are unit errors,
  not arithmetic errors.
- **Round in a stated direction** and remember which way you rounded so you can qualify the
  answer ("so at least 4.2 million").
- **Keep it in millions/billions** rather than writing out zeros.

---

## 4. Choosing the calculation path

When there are two ways to get the answer, prefer the one that:

- uses numbers already given rather than requiring new assumptions;
- keeps the arithmetic in round numbers;
- produces an intermediate quantity that is itself informative (e.g. contribution margin per unit,
  which will be reused);
- can be sanity-checked against something known.

State the choice out loud: "I could work this per-customer or in total; per-customer is cleaner
because we already have ARPU, so I'll do that."

---

## 5. Sanity checks

- **Order of magnitude** — does the answer have a plausible number of zeros for this industry?
- **Per-capita** — divide by population. A $4tn national toothbrush market against a $30tn GDP is
  absurd on sight.
- **Share check** — is the implied market share above 100%? Above the largest incumbent's?
- **Margin check** — does the implied margin fit the industry (SaaS 70–80% gross, retail 25–40%,
  grocery 2–4% net, airlines low single-digit net)?
- **Reconcile with the case** — does this contradict a number given earlier?
- **Second route** — recompute a different way if it's cheap.

Saying the sanity check out loud is worth points on its own.

---

## 6. Market sizing

**Choose an approach and say why.**

- **Top-down** — start from a population/total and filter down. Good for broad consumer products.
  Risk: stacked percentages compound error.
- **Bottom-up** — start from one unit (one store, one customer, one machine) and scale up. Good
  for location- or transaction-driven markets, and usually more defensible.

**Method**

1. **Scope** — units or currency? Annual or installed base? Which geography? What counts as the
   product? Get this confirmed; it's where most sizing answers go wrong.
2. **Build the tree before any arithmetic.**
3. **Segment only where behaviour genuinely differs** (age bands, urban/rural, B2B/B2C,
   income). Do not segment for decoration.
4. **Round assumptions**, justify each in half a sentence.
5. **Replacement logic for durables:** annual sales = installed base ÷ useful life.
   Forgetting this turns a replacement market into an installed base.
6. **Sanity check and interpret** — the number is not the answer; what it means for the client is.

The interviewer is scoring structure, assumption quality and sense-checking. Precision is close
to irrelevant; a well-reasoned answer 30% off beats an unjustified answer that happens to be right.

---

## 7. Communicating math

- Say the equation before the numbers.
- Narrate each step so an error is caught at the step, not at the end.
- Announce roundings.
- Give the final number **with its unit and its comparison**: "€48m, which is about 12% of their
  current operating profit."
- If you make an arithmetic error and catch it: say so, correct it, move on in one sentence.
  Recovering cleanly costs almost nothing. Silently continuing on a wrong number costs a lot.

---

## 8. Difficulty calibration for generated math modules

| Level | Characteristics |
|---|---|
| Beginner | One step, clean numbers, all inputs given, formula obvious |
| Intermediate | 2–3 steps, one assumption to make, some rounding needed |
| Advanced | Multi-step; the candidate must choose the path; some inputs must be requested or derived; one distractor number present |
| MBB | Path is not obvious; requires an intermediate quantity that was never named; contains a plausible wrong route; the interpretation matters more than the number; a sensitivity question follows |

Difficulty is raised by making the **setup** harder, not by making the arithmetic uglier. Ugly
arithmetic is a bad case, not a hard one.
