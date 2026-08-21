# Case Taxonomy

**Case types are tags, not boxes.** Real cases combine archetypes: a market entry case almost
always contains a sizing module and a profitability module; a PE due diligence case contains a
market attractiveness assessment and a competitive assessment. Never let the label select the
structure — the label only tells you which modules are likely present.

Each entry: **Objective · Signals · Modules · Diagnostic tree · Quant · Exhibits · Insights ·
Mistakes · Combines with.**

The **Quant** line lists the quantitative questions this archetype typically asks. Each item is a
question to pose, not a topic to mention — "breakeven" means *"how much additional volume would
this price cut need to pay for itself?"*, phrased from where the case actually is. Always attach
an interpretation question to it (`case-math.md` §1, step 6).

---

## Contents

- [1. Profitability](#1-profitability)
- [2. Market Entry](#2-market-entry)
- [3. Growth Strategy](#3-growth-strategy)
- [4. Pricing](#4-pricing)
- [5. New Product / New Business](#5-new-product--new-business)
- [6. M&A](#6-ma)
- [7. Private Equity / Due Diligence](#7-private-equity--due-diligence)
- [8. Operations / Process](#8-operations--process)
- [9. Supply Chain](#9-supply-chain)
- [10. Market Sizing](#10-market-sizing)
- [11. Competitive Response](#11-competitive-response)
- [12. Turnaround / Cost Reduction](#12-turnaround--cost-reduction)
- [13. Strategic Transformation / Disruption](#13-strategic-transformation--disruption)
- [14. Non-profit / Public Sector / Social Impact](#14-non-profit--public-sector--social-impact)
- [15. Mixed / integrated cases](#15-mixed--integrated-cases)
---

## 1. Profitability

**Objective** — Profit has fallen (or must rise). Find why, and fix it.

**Signals** — "Profits down X% over N years," "margins compressing," "revenue flat but profit
down," "we're less profitable than competitors."

**Modules** — Decompose profit; isolate whether revenue or cost moved; split by segment /
product / channel / geography; find the driver; quantify; recommend.

**Diagnostic tree**
```
Profit ↓
├── Revenue ↓ ?     → Price ↓ (list vs realised, discounting, mix shift)
│                   → Volume ↓ (market ↓ | share ↓ | segment mix | channel loss)
└── Cost ↑ ?        → Per-unit ↑ (inputs, labour rate, productivity, scrap, freight)
                    → Total ↑ with volume flat (fixed cost added, overhead, capacity idle)
Then: internal (we changed something) vs external (market or competitor changed)?
And:  is this whole-company or concentrated in one segment?
```
The two decisive early questions: **price or volume?** and **per-unit or total?**

**Quant** — margin, contribution margin, per-unit vs total cost, segment-weighted margins,
breakeven, sizing the profit gap.

**Exhibits** — P&L bridge, revenue/cost waterfall, margin by segment, cost per unit over time,
price vs volume trend, competitor benchmark.

**Insights** — a "cost problem" that is really a volume problem (fixed cost spread over fewer
units); one segment dragging a healthy portfolio; discounting that raised volume but destroyed
contribution; mix shift toward a low-margin product.

**Mistakes** — applying the profit tree without ever tailoring the volume branch to the industry;
concluding "costs rose" without checking per-unit; failing to segment; treating a market-wide
decline as a company problem.

**Combines with** — pricing, operations, competitive response, turnaround.

---

## 2. Market Entry

**Objective** — Should the client enter [market / geography / segment]? On what terms?

**Signals** — "considering entering," "expand into," "should we launch in X."

**Modules** — market attractiveness; right to win; entry mode; economics.

**Diagnostic tree**
```
Is the prize worth it?   size, growth, profit pool, structural attractiveness, regulation
Can we win?              customer need, competitors, our differentiated advantage, share attainable
Can we execute?          capabilities, assets, channel, brand, talent, supply, time to build
Does it pay?             revenue at plausible share, cost to serve, investment, breakeven, risk
Entry mode?              organic | acquisition | JV | licence | partnership
```

**Quant** — market sizing, attainable share, revenue projection, investment and breakeven,
payback, NPV of entry.

**Exhibits** — market size and growth, competitor share, customer segment attractiveness,
price/positioning map, cost-to-serve comparison.

**Insights** — attractive market the client has no right to win in; unattractive headline market
with an attractive niche; entry economics that only work at an implausible share; the incumbent's
likely response destroying the case.

**Mistakes** — sizing the market and declaring victory; ignoring competitor reaction; ignoring
entry mode; no "what share is realistic and why."

**Combines with** — market sizing, new product, competitive response, M&A (as entry mode).

---

## 3. Growth Strategy

**Objective** — Grow revenue/profit by X% (often to a stated target by a stated date).

**Modules** — quantify the gap; generate levers; size each; prioritise; sequence.

**Diagnostic tree**
```
Gap to target = target − trajectory
Organic:   existing customers (penetration, frequency, basket, price, upsell, retention)
           new customers  (segments, geographies, channels)
           new offers     (products, services, bundles, subscription)
Inorganic: acquisition, partnership, JV, licensing
Screen each on: size of prize × probability × time to impact × investment required
```

**Quant** — gap sizing, revenue per lever, cost to acquire, incremental margin, ROI per lever.

**Exhibits** — growth decomposition, segment growth rates, penetration by geography,
lever-vs-effort matrix.

**Insights** — the biggest lever is the least glamorous (retention, price realisation) rather
than new products; growth targets unreachable organically → forces the inorganic conversation.

**Mistakes** — listing levers without sizing them; ignoring the target; no prioritisation;
proposing only new-customer growth when retention is leaking.

**Combines with** — pricing, new product, market entry, M&A.

---

## 4. Pricing

**Objective** — Set or change price for a product, service or portfolio.

**Modules** — three lenses; elasticity; portfolio effects; implementation.

**Diagnostic tree**
```
Cost-based        floor: variable cost + required contribution
Competition-based reference: substitutes, competitor price, switching cost
Value-based       ceiling: economic value to the customer (cost saved / revenue gained / risk avoided)
Then:  segment willingness to pay; price structure (per unit, subscription, tiered, freemium,
       two-part tariff, dynamic); elasticity; cannibalisation; channel and discount leakage;
       competitor reaction; anchoring and perception
```

**Quant** — contribution margin, elasticity (revenue rises on a cut only if |E| > 1), breakeven
volume change for a price move, customer economic value, cannibalisation net effect, blended
realised price.

**Exhibits** — price/volume history, competitor price ladder, willingness-to-pay survey,
price-vs-feature scatter, discount waterfall (list → net).

**Insights** — the product is underpriced against the value it creates; realised price is far
below list because of discount leakage; a price cut needs an implausible volume increase to pay.

**Mistakes** — cost-plus only; ignoring elasticity; ignoring competitor response; ignoring the
existing portfolio (cannibalisation); confusing list and realised price.

**Combines with** — profitability, new product, competitive response.

---

## 5. New Product / New Business

**Objective** — Should we launch it? Will it make money?

**Diagnostic tree**
```
Customer:     is there a real, unmet, willing-to-pay need? which segment? how big?
Product:      does ours meet it better than the alternative — including "do nothing"?
Competition:  who else serves this need; what do they do when we launch?
Capability:   can we build, make, sell, service and support it?
Economics:    price, volume ramp, unit economics, development and launch investment, breakeven
Portfolio:    cannibalisation, brand fit, channel conflict, opportunity cost
```

**Quant** — sizing, adoption curve, unit economics, breakeven, payback, cannibalisation-adjusted
contribution.

**Exhibits** — segment need survey, competing product comparison, adoption forecast, cost build-up.

**Insights** — the product is good but cannibalises a higher-margin existing line; the real
constraint is channel, not product; adoption assumptions are the whole case.

**Mistakes** — no cannibalisation check; no competitor response; adoption assumptions never
sanity-checked.

**Combines with** — pricing, market entry, growth.

---

## 6. M&A

**Objective** — Should we acquire this target? At what price?

**Diagnostic tree**
```
Why:        strategic rationale — scale, capability, market access, defensive, vertical
Market:     is the target's market attractive?
Target:     is this a good asset — position, growth, margins, customers, management, risks?
Synergies:  cost (overlap × capture %), revenue (cross-sell base × attach × margin — discount hard)
Price:      valuation vs standalone + synergies; who captures the value
Integration:feasibility, cost, timeline, culture, retention, systems
Alternatives: build, partner, buy someone else, do nothing
```

**Quant** — multiples, synergy sizing, deal payback, accretion/dilution, simple DCF or
perpetuity, price ceiling = standalone value + synergies we can actually capture.

**Exhibits** — target P&L, overlap analysis, comparable transactions, synergy build-up,
customer overlap.

**Insights** — the deal only works on revenue synergies, which rarely materialise; the price
already prices in all the synergies; a cheaper alternative achieves 80% of the benefit.

**Mistakes** — evaluating the target without evaluating the price; taking revenue synergies at
face value; ignoring integration cost; forgetting the "do nothing" baseline.

**Combines with** — due diligence, market entry, growth.

---

## 7. Private Equity / Due Diligence

**Objective** — Should the fund invest? What return can it expect?

**Diagnostic tree**
```
Market:     size, growth, cyclicality, structural trends, fragmentation
Company:    position, moat, customer concentration, contract quality, management
Financials: revenue quality, margin trajectory, working capital, capex, cash conversion
Value creation plan: organic growth, margin expansion, buy-and-build, multiple expansion
Exit:       who buys it in 5 years, at what multiple
Risks:      what kills this — regulation, technology, key customer, key person, leverage
Returns:    entry multiple, leverage, EBITDA growth, exit multiple → MoM / IRR
```

**Quant** — EBITDA bridge, entry/exit multiple, leverage, money multiple, IRR approximation
(Rule of 72 in reverse), sensitivity to exit multiple.

**Exhibits** — market growth, customer concentration, EBITDA bridge, comparable multiples.

**Insights** — the growth is market-driven and will not persist; returns depend entirely on
multiple expansion (i.e. on hope); customer concentration is the real risk.

**Mistakes** — analysing the business but never the return; no exit thinking; ignoring
downside/sensitivity.

**Combines with** — M&A, growth, market attractiveness.

---

## 8. Operations / Process

**Objective** — Increase throughput, cut cost, improve quality or service level.

**Diagnostic tree**
```
Map the process end to end, step by step
For each step:  capacity, cycle time, yield, cost, quality, staffing
Find the bottleneck — throughput is set by the bottleneck, never by the average
Root cause at the bottleneck: machine | material | method | manpower | measurement | environment
Options: add capacity | rebalance | reduce variability | redesign | outsource | change the demand pattern
Quantify each: impact × cost × time to implement × risk
```

**Quant** — capacity, utilisation, throughput, cycle time, yield/scrap, labour productivity,
cost per unit, savings from a bottleneck fix.

**Exhibits** — process flow with cycle times, capacity vs demand by step, defect Pareto,
utilisation by shift/line, cost per unit by step.

**Insights** — adding capacity at a non-bottleneck step achieves nothing; the bottleneck is
variability, not average capacity; the constraint is demand-side, so cost cuts are the wrong lever.

**Mistakes** — optimising a non-bottleneck; using averages where variability drives the problem;
recommending automation without the payback.

**Combines with** — profitability, supply chain, turnaround.

---

## 9. Supply Chain

**Objective** — Reduce landed cost, improve service level or resilience.

**Diagnostic tree**
```
Source → Make → Move → Store → Sell → Return
Per stage: cost, lead time, reliability, capacity, risk
Levers: supplier consolidation/renegotiation, network design and footprint, mode shift,
        inventory policy (safety stock, service level), demand forecasting, SKU rationalisation,
        make-vs-buy, nearshoring, route/backhaul density
Trade-off spine: cost vs service level vs working capital vs resilience
```

**Quant** — landed cost per unit, inventory turns, days of inventory, service level vs stockout
cost, freight cost per unit, network scenario comparison.

**Exhibits** — cost-to-serve by region, network map with flows, inventory by SKU/site, supplier
spend Pareto, lead time distribution.

**Insights** — the cheapest unit cost carries the highest landed and working-capital cost; SKU
proliferation is the hidden cost driver; the service-level target is set higher than customers
value.

**Mistakes** — optimising one stage in isolation; ignoring working capital; ignoring the
resilience/cost trade-off.

**Combines with** — operations, profitability, cost reduction.

---

## 10. Market Sizing

**Objective** — Estimate a market, demand, or quantity — usually a module inside another case.

**Method** — see `case-math.md` §6. Scope → tree → segment where behaviour differs → round
assumptions → replacement logic for durables → sanity check → implication.

**Insights** — the interesting result is usually the comparison (vs the client's revenue, vs the
investment required), not the absolute number.

**Mistakes** — arithmetic before structure; unjustified assumptions; no sanity check; forgetting
replacement cycles; giving a number without saying what it means.

**Combines with** — everything. Rarely stands alone above beginner level.

---

## 11. Competitive Response

**Objective** — A competitor did something. What do we do?

**Diagnostic tree**
```
What exactly happened, and is it real / permanent / scalable?
Why did they do it — what's their strategy, cost position, incentive?
How much does it hurt us? quantify: customers at risk × value; margin at risk
What are our options?  match | differentiate | segment (defend the valuable part) |
                       attack elsewhere | change the game | do nothing | exit
For each: cost, our ability to sustain it, their likely counter-move, second-order effects
Choose on: value protected vs cost, and whether we can win a war of attrition
```

**Quant** — customers/revenue at risk, margin impact of matching a price cut, breakeven of a
defensive investment, share sensitivity.

**Exhibits** — share over time, price ladder, competitor cost position, customer switching survey.

**Insights** — matching a price cut is exactly what a lower-cost competitor wants; only one
segment is genuinely at risk; "do nothing" is sometimes right and is almost never proposed.

**Mistakes** — jumping to "match the price"; never quantifying the threat; ignoring the
competitor's next move; not considering doing nothing.

**Combines with** — pricing, profitability, growth.

---

## 12. Turnaround / Cost Reduction

**Objective** — The business is losing money or cash. Stabilise it.

**Diagnostic tree**
```
Urgency:   how much cash, how much runway? (this frames everything)
Stabilise: cash — working capital, capex deferral, discretionary spend, asset sales
Cost:      by category and by cause; fixed vs variable; benchmark vs peers;
           quick wins vs structural; what cost is actually buying revenue
Revenue:   is there a viable core? which segments/products/sites earn money?
Portfolio: what to keep, fix, shrink, close, sell
Structural:is this business viable at all at this scale, in this market?
Sequence and risk: what must happen in 90 days, 12 months, 3 years
```

**Quant** — cash burn and runway, contribution by site/product, breakeven, closure cost vs
ongoing loss, savings by lever with implementation cost.

**Exhibits** — profitability by site/SKU, cost breakdown vs benchmark, cash flow forecast,
fixed/variable split.

**Insights** — closing loss-making units removes their contribution to fixed cost and can make
things worse; the "loss-making" segment is loss-making only on a bad allocation; cutting the cost
that generates revenue accelerates the decline.

**Mistakes** — across-the-board cuts; ignoring contribution vs fully-allocated cost; no
sequencing; no cash view.

**Combines with** — profitability, operations, portfolio strategy.

---

## 13. Strategic Transformation / Disruption

**Objective** — The industry is changing (digital, regulatory, technological, sustainability).
How should the client respond?

**Diagnostic tree**
```
The shift:  what's changing, how fast, how certain, is it structural or cyclical?
Impact:     on our profit pool — which parts erode, which grow, on what timeline
Position:   assets, capabilities, customer relationships, cost position, constraints
Options:    defend the core | build the new | buy the new | partner | harvest and exit
Economics:  investment, cannibalisation of the existing business, timing
Organisation: capabilities, talent, incentives, governance, speed
```

**Quant** — profit pool shift over time, investment vs erosion, cannibalisation, breakeven timing.

**Exhibits** — profit pool by segment over time, adoption S-curve, competitor investment,
capability gap assessment.

**Insights** — the transition destroys margin before it creates it; the right question is
sequencing and timing, not whether; the incumbent's asset is a liability in the new model.

**Mistakes** — treating it as a technology question rather than an economics question; ignoring
cannibalisation; ignoring organisational feasibility.

**Combines with** — growth, M&A, operations.

---

## 14. Non-profit / Public Sector / Social Impact

**Objective** — Maximise impact, access or efficiency under a budget and political constraints.

**Diagnostic tree**
```
Objective:    define success — the metric is not profit; whose welfare, measured how
Stakeholders: beneficiaries, funders, government, staff, community — and their competing goals
Problem:      root-cause the gap (access | awareness | affordability | quality | capacity | trust)
Options:      generate, then screen on impact per dollar, reach, feasibility, sustainability
Constraints:  budget, mandate, politics, regulation, capacity, time
Measurement:  how will we know it worked
```

**Quant** — cost per beneficiary, reach, impact per dollar, capacity vs need, funding gap.

**Exhibits** — coverage map, cost per beneficiary by channel, need vs served, funding sources.

**Insights** — the binding constraint is last-mile delivery, not funding; the cheapest
intervention per person reaches the least needy people.

**Mistakes** — importing a profit tree; ignoring stakeholders; recommending something politically
impossible; no success metric.

**Combines with** — operations, market sizing.

---

## 15. Mixed / integrated cases

Most realistic cases are compounds. Common compounds worth generating:

- Profitability → root cause is pricing → pricing module → competitive response risk.
- Market entry → sizing module → entry economics → build vs buy → M&A module.
- Growth target → lever generation (brainstorm) → sizing the top two → operations constraint.
- PE diligence → market attractiveness → customer concentration exhibit → returns math.
- Turnaround → site profitability exhibit → closure math → the contribution trap.
- Digital disruption → profit pool shift → cannibalisation math → investment decision.

**When generating**, pick a primary archetype for the spine and one or two secondary archetypes
for modules. Tell the candidate nothing about which archetypes are present — recognising them is
part of the assessment.
