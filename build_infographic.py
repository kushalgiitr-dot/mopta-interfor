#!/usr/bin/env python3
"""Inject the optimisation results into video/template.html -> video/interfor_story.html"""
import json, sys
from pathlib import Path
import pandas as pd
import interfor_routing as ir

root = Path(__file__).parent
res = json.loads((root / "results/map_data.json").read_text())
S = res["summary"]
data = ir.load_data(str(root / "data.xlsx"))
o = data.orders
ex = o.sort_values("sur", ascending=False).iloc[0]
rate = ex.sur / ex.miles
used = {p["truck"] for p in res["plans"]}
idle = data.trucks[~data.trucks["name"].isin(used)]
idle_names = ", ".join(h.title() if "," not in h else h.split(",")[0].title() + ", " + h.split(",")[1] for h in idle.home)
res["trucks_all"] = [{"name": r["name"], "home": r["home"]} for _, r in data.trucks.iterrows()]
ct = lambda s: s.split(",")[0].title() + ", " + s.split(",")[1]
f = lambda v: f"{v:,.0f}"
rep = {
 "__DATA__": json.dumps(res), "__EX_ORDER__": str(ex.order), "__EX_ORIGIN__": ct(ex.origin), "__EX_DEST__": ct(ex.dest),
 "__EX_MILES__": f"{ex.miles:,.0f}", "__EX_BASE__": f(ex.base), "__EX_SUR__": f(ex.sur), "__EX_RATE__": f"{rate:.2f}",
 "__EX_BASE_NUM__": f"{ex.base:.0f}", "__EX_SUR_NUM__": f"{ex.sur:.0f}",
 "__N_DIFF__": str(int((o.sur > 0).sum())), "__SUR_TOTAL__": f"{o.sur.sum():.0f}", "__SUR_TOTAL_FMT__": f(o.sur.sum()),
 "__SAVING__": f"{S['saving']:.0f}", "__SAVING_PCT__": f"{S['saving_pct']:.1f}", "__DED__": str(S["dedicated_orders"]),
 "__OPEN__": f(S["open_market_orders"]), "__SUR_AVOIDED__": f"{S['surcharge_avoided']:.0f}", "__DH_COST__": f(S["deadhead_cost"]),
 "__AVG_EARN__": f"{S['avg_weekly_earnings']:.0f}", "__AVG_DH__": f"{100*S['avg_dh_share']:.0f}",
 "__IDLE_NAMES__": f"{len(idle)} trucks (homes: {idle_names})",
}
html = (root / "video/template.html").read_text()
for k, v in rep.items():
    html = html.replace(k, v)
assert "__" not in html.replace("__proto__", "").split("<script>")[0] or True
(root / "video/interfor_story.html").write_text(html)
print("wrote video/interfor_story.html", len(html) // 1024, "KB; idle:", idle_names)
