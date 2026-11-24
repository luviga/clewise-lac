import json, sys
d = json.load(open(r"C:\clw_align\_LAC_HUB\align_20261124T021708Z\work\hb_scripts\hb_dump.json", encoding="utf-8"))
country = sys.argv[1]
only = sys.argv[2].split(",") if len(sys.argv) > 2 else None
YRS = [str(y) for y in range(2018, 2028)]
c = d[country]
KEEP = ("Residual", "ActivityLower", "ActivityUpper", "MaxCapacity", "MinCapacity", "CapacityFactor", "Availab", "CapacityToActivity")


def fmt(x):
    try:
        return f"{float(x):.5g}"
    except Exception:
        return str(x)


for t, rows in sorted(c["ao"].items()):
    if only and t not in only:
        continue
    print("=====", t)
    for r in [x for x in rows if any(s in str(x["param"]) for s in KEEP)]:
        cells = r["cells"]
        ys = [y for y in YRS if y in cells]
        vals = [cells[y] for y in ys]
        if all(v[1] in (None, "") for v in vals):
            print(f"  r{r['row']} {r['param']} [{cells.get('Projection.Mode', [None])[0]}] empty")
            continue
        s = " ".join(f"{y[2:]}:{fmt(v[1])}{'*' if isinstance(v[0], str) and str(v[0]).startswith('=') else ''}" for y, v in zip(ys, vals))
        print(f"  {r['sheet'][:3]} r{r['row']} {r['param']} [{cells.get('Projection.Mode', [None])[0]}] {s}")
        fs = [f"{y[2:]}:{v[0]}" for y, v in zip(ys, vals) if isinstance(v[0], str) and str(v[0]).startswith('=')]
        if fs:
            print("       formulas: " + " ".join(fs)[:400])
    for b in c["b1"]:
        v = b["vals"]
        ts = [x.strip() for x in str(v.get("Tech_Set")).replace(";", ",").split(",")]
        if t in ts and v.get("Scenario") == "BAU":
            print(f"  B1 r{b['row']}: {v.get('Parameter')} | Tech_Set={v.get('Tech_Set')} | " +
                  "; ".join(f"{k}={str(v[k])[:160]}" for k in v if k not in ("Scenario", "Parameter", "Tech_Set") and v[k] not in (None, "None")))
    for k, v in sorted(c["comp"].items()):
        p = k.split("|")
        if p[2] == t and p[0] == "B1" and any(s in p[1] for s in KEEP):
            vs = {y: x for y, x in v.items() if y == "-" or 2018 <= int(y) <= 2027}
            print("  C", p[1], "|".join(p[3:]), " ".join(f"{y[2:]}:{fmt(x)}" for y, x in sorted(vs.items())))
