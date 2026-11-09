# 9-minute video — time split and script

Target 8:40–9:00. Speak ≈145 words/min. Open `video/interfor_story.html`, press **H** to hide the controls, **Space** to auto-play (its timing = this split) or **→** to step so each speaker controls their own pace. Record at 1920×1080 with webcams as picture-in-picture. The page itself carries no "part / speaker" labels; the split below is for the team only.

| Time | Who | Section | HTML scenes (in order) |
|---|---|---|---|
| 0:00–2:45 | Speaker 1 | Scenario, decision, costs, constraints | Context · The decision (animated road fork) · Cost per lane · Driver rules · Why it's hard |
| 2:45–5:30 | Speaker 2 | Model, variables, objective, approach, **code walkthrough** | Mathematical model (0:50) · Code 1 rules/data (0:30) · Code 2 beam search (0:35) · Code 3 Pyomo master (0:30) · Code 4 solve loop + validation (0:20) |
| 5:30–8:15 | Speaker 3 | Results, route map, fleet-size extension | Headline results · Route explorer (click trucks, toggle weeks) · Fleet size |
| 8:15–9:00 | All | Takeaways, one line each | Takeaways |

The code scenes are abridged copies of `interfor_routing.py`; each step highlights the lines being discussed. If you prefer to show the real file, switch to VS Code at the same moments.

---

## Speaker 1 (0:00–2:45) — scenario and constraints

**[0:00 · scene 1]** "Interfor is one of North America's biggest lumber producers, with about 4.7 billion board feet of annual capacity. In the US South, its logistics team has 20 dedicated trucks and 1,000 orders over two delivery weeks, due January 17th and 24th. Every lane between 218 cities is priced."

**[0:25 · scene 2 · trucks leave the mill and split onto two roads]** "Each order has two ways to travel. Either one of our dedicated trucks hauls it, in a multi-stop weekly route that ends near the driver's home, or we tender it on the open market. Our job: decide the split *and* every truck's route, to minimise total freight cost."

**[0:50 · scene 3]** "Cost is lane-by-lane. But some lanes are 'difficult' because trucks are scarce. Take this Statesboro-to-Fort-Worth load: a base cost of about $2,700, plus a surcharge of $1.75 per mile, another $1,800, if we tender it. Ninety-four orders sit on difficult lanes, and together they carry about $82,000 of surcharge. That's the savings pool. A dedicated truck doesn't pay that surcharge."

**[1:20 · scene 4]** "But dedicated trucks come with driver rules. One: every driver earns at least $4,000 a week. Two: the final delivery must be within 100 miles of home. Three: two consecutive days off, and only *after* the last delivery and the drive home. Four: no more than 450 miles a day, which, with two days off, caps a week at 2,250 miles. Five: empty, or deadhead, miles can be at most half of all miles."

**[2:30 · scene 5]** "So we're deciding three things at once: who gets which order, in what sequence, and on which day. With millions of possible weekly routes per truck, this is a hard combinatorial problem. Over to [Speaker 2] for the model."

---

## Speaker 2 (2:45–5:30) — model and code

**[2:45 · scene 6]** "The natural model has binary variables for every truck, every pair of orders, every day, far too big for 1,000 orders. So we use Dantzig-Wolfe decomposition and choose among *routes*. A route is an ordered list of orders for one truck, starting and ending at its home. The decision variable z-r is one if we operate route r; idle-k is one if truck k isn't used that week."

"The objective: start from the cost of sending everything to the open market, then add, for each chosen route, the deadhead miles times a cost rate, minus the surcharge that route avoids. A route only pays if the surcharge it dodges beats the empty miles it adds. Constraints: every order is in at most one route; every truck takes exactly one route or sits idle. The driver rules (pay, 2,250 miles, 50% deadhead, 100-mile finish) live inside route generation, so no infeasible route ever reaches the model."

**[3:35 · code scenes 1–4]** "Walking through the code. `load_data` reads the Excel sheets, builds the lane matrix and computes each order's difficult-lane surcharge. `is_feasible` is the five rules in four lines. `beam_price` is the route generator: a beam search that extends partial routes order by order, keeping the best few hundred, scored by dual prices. `build_master` is the Pyomo model: a binary `z`, a binary `idle`, one cover constraint per order, one constraint per truck, and the objective. `solve_week` loops: solve the LP, read the duals from the Pyomo suffix, price new routes, repeat until none improves, then solve the integer model with Gurobi, or HiGHS if Gurobi isn't installed. Last, `validate` re-checks every driver rule on the final plan: zero violations. Two weeks solve in about a minute."

*(Be upfront: pricing is heuristic, so the plan is very good, not proven optimal. Widening the search moved week 1 from $12.6k to $14.7k, then it flattened.)*

---

## Speaker 3 (5:30–9:00) — results, extension, takeaways

**[5:30 · scene 7]** "The optimal plan costs $1.342 million versus $1.372 million sending everything to the open market: a saving of $30,092, 2.2%. 106 orders go dedicated. We avoid $53,800 of the $81,600 surcharge, and pay about $23,700 in extra empty miles. Drivers average $5,173 a week, at 22% deadhead, and all constraints hold. Four trucks stay idle: their homes in Ashford, Opelousas, Mount Olive and Henderson have no delivery lane within 100 miles."

**[6:00 · scene 8]** "Here is EastGate Express from Sylvania, Georgia, week one. it loads in Statesboro on day one and hauls 955 miles to New Waverly, Texas, a difficult lane. It then repositions 139 empty miles to Pineland and hauls 926 miles back to Pooler, near Savannah, on day five, 57 miles from home. It drives 450 miles a day, and the last two days are off. Click another truck: the day bars show every driver is mileage-bound, using all five driving days."

**[7:20 · scene 9]** "Extension: how many drivers are worth it? Letting the best-placed N trucks run: five trucks save $13.4k, ten $24.0k, fifteen $29.8k, and twenty only $30.1k. The last five trucks add about $300. The savings pool is limited by how many difficult-lane loads also finish near a home terminal. And the answer depends on our empty-mile cost: at $0.75 a mile savings reach $41.9k, at $2.12 they fall to $21.6k, with the same story."

**[8:15 · scene 10 · one line each]**
- S1: "Point dedicated trucks at difficult lanes."
- S2: "Home terminals matter: some can't legally earn $4,000 and should be repositioned."
- S3: "About 15 drivers capture 99% of the value, and every plan respects pay and home time, so cost cuts don't cost driver retention."

---

## Q&A prep
- *Is it optimal?* Integer master is solved to <0.3% gap over the generated routes; route generation is a beam-search heuristic, so we call it near-optimal.
- *Why is the saving only ~2%?* Dedicated trucks are paid the lane rate, so the gain is the surcharge avoided minus deadhead; the data gives no cheaper dedicated rate. Honest assumption, stated in the README.
- *Why week 1 / week 2 separately?* Orders due Jan 17 must deliver Jan 11–17, those due Jan 24 on Jan 18–24; the weeks don't interact.
- *Extra costs for the extension?* A real dedicated-fleet cost (fixed driver pay, fuel, maintenance), time-window penalties, and the idle-truck cost.
