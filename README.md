# Interfor Dedicated Truck Routing — AIMMS-MOPTA 2026 (Pyomo)

BMN 616 AOTM · Project Submission, Option C (real competition data).
Problem: assign 20 dedicated trucks to 1,000 orders (what to haul vs. tender on the open market) and route each truck's week, minimising total freight cost under driver rules.

## Run

```bash
pip install -r requirements.txt
python interfor_routing.py --data data.xlsx          # ~1 min with Gurobi; HiGHS works too
python build_infographic.py                          # rebuilds video/interfor_story.html from results/
```

Useful options: `--dh-rate 1.0` (cost of empty miles, $/mi), `--fleet 15`, `--require-all-trucks`, `--time-limit 120`, `--sens 0,5,10,15,20`.

Outputs in `results/`: `summary.json`, `routing_plan.json` (per truck/week: legs, days, miles, earnings), `routing_plan_legs.csv`, `order_assignment.csv` (all 1,000 orders → truck or OPEN MARKET).

## Model (see docstring in `interfor_routing.py`)

Route-based set-packing master solved per delivery week (orders due Jan 17 → week 1, Jan 24 → week 2), with column generation:
`z[r]` = route r operated, `idle[k]` = truck k unused; min `Σ OpenCost + Σ z[r]·(DHrate·Deadhead[r] − SurchargeAvoided[r])`; each order in ≤ 1 route, each truck exactly one route or idle.
Route feasibility (earnings ≥ $4,000, ≤ 2,250 mi = 5 × 450 with 2 days off, deadhead ≤ 50 %, last stop ≤ 100 mi from home) is enforced when a route is generated, and every rule is **re-checked on the final plan** by `validate()`.

## Results (base case, DH rate $1.50/mi)

| | |
|---|---|
| Cost if everything goes to the open market | $1,371,810 |
| Optimised total cost | $1,341,717 |
| Saving | **$30,092 (2.2 %)** |
| Orders on dedicated routes | 106 (894 open market) |
| Difficult-lane surcharge avoided | $53,774 of $81,645 |
| Avg driver week | $5,173 earned, 22 % deadhead |
| Constraint violations | 0 |
| Fleet-size curve (best N trucks) | N=5 $13.4k · 10 $24.0k · 15 $29.8k · 20 $30.1k |
| DH-rate robustness | $0.75 → $41.9k · $1.50 → $30.1k · $2.12 → $21.6k |

## Assumptions (please state them in the video)

1. **Dedicated cost.** A dedicated truck is paid the same lane cost per loaded move that the open market would charge (without the difficult-lane surcharge), plus `DHrate` per empty mile. The data gives no dedicated rate, so savings come from avoided surcharges minus deadhead. Driver "earnings" = sum of lane costs of loaded moves.
2. **Time.** Each delivery week is Sun–Sat ending on the due date; trucks start at home on day 1 and drive up to 450 mi/day, so a route may use at most 5 driving days and the last 2 days are off at home. Pick-ups can happen any day (no pick-up windows in the data).
3. **Difficult lanes.** State codes (TX, WV, VA, AR, OK) are matched on destination state. ZIP-3 codes (e.g. GA_300) are matched through an approximate city→ZIP-3 table (`ZIP3` in the code) because the data has city names only — verify before quoting exact figures.
4. **Route search is heuristic.** Pricing uses beam search, so the result is a very good feasible plan, not a proven optimum. A wider search lifted week 1 from $12.6k → $14.5k → $14.7k and then flattened, so the reported plan is close to converged; the final integer master gap is < 0.3 % of the restricted master.
5. **Idle trucks.** Four carriers (homes Ashford AL, Opelousas LA, Mount Olive MS, Henderson TX) have no order destination within 100 miles of home, so no compliant route exists; they stay idle (`--require-all-trucks` reports this as infeasible).
6. **Fleet sensitivity** reuses the 20-truck route pool and lets the best N trucks work; only 20 carriers exist in the data (the brief mentions up to 30).
7. Not implemented: AIMMS interface (the course uses Pyomo), pick-up/delivery time-of-day, driver-specific costs.
