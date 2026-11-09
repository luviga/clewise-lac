"""Supply-to-consumer table from the BAU InputActivityRatio/OutputActivityRatio files.
Usage: py -I consumers.py <repo_root> <out_csv>
A supply row is a technology that has outputs but no inputs and whose name starts with IMP, DIST, EXTT or PRO_COA
(fossil fuels only). Pass-through technologies (CR NGS_DTR, BLEND_*) are followed one level and their consumers
listed with the path."""
import sys, csv, pandas as pd
root, out = sys.argv[1], sys.argv[2]
F = {"CostaRica": "CostaRica/CR_ENERGY/t1_confection", "DominicanRepublic": "DominicanRepublic/RD_ENERGY",
     "Ecuador": "Ecuador/ECU_Energy", "Guatemala": "Guatemala/GUA_ENERGY", "Honduras": "Honduras/HON_ENERGY",
     "Jamaica": "Jamaica/JAM_ENERGY"}
FOSSIL = ("AVG", "COA", "COK", "FOI", "FO1", "KJF", "LPG", "NGS", "DSL", "GSL", "CRU", "KER", "JET", "OPE")
PASS = ("NGS_DTR", "BLEND_")
def ctype(tech, outs):
    if any(o.endswith("ELE") for o in outs): return "power"
    if tech.startswith(("REF_", "PROCRU", "PRONGS")): return "refinery"
    if tech.endswith("CRUEXP"): return "export"
    return "demand"
rows = []
for c, f in F.items():
    i = pd.read_csv(f"{root}/{f}/A2_Output_Params/BAU/InputActivityRatio.csv", usecols=["TECHNOLOGY", "FUEL"]).drop_duplicates()
    o = pd.read_csv(f"{root}/{f}/A2_Output_Params/BAU/OutputActivityRatio.csv", usecols=["TECHNOLOGY", "FUEL"]).drop_duplicates()
    sup = [t for t in sorted(set(o.TECHNOLOGY) - set(i.TECHNOLOGY))
           if t.startswith(("IMP", "DIST", "EXTT", "PRO_COA")) and not t.startswith(("IMP_R", "IMP_SUB", "IMP_STOR"))]
    for t in sup:
        for fu in sorted(set(o[o.TECHNOLOGY == t].FUEL)):
            if not any(k in fu for k in FOSSIL): continue
            for k in sorted(set(i[i.FUEL == fu].TECHNOLOGY)):
                outs = sorted(set(o[o.TECHNOLOGY == k].FUEL))
                if k.startswith(PASS):
                    for fu2 in outs:
                        for k2 in sorted(set(i[i.FUEL == fu2].TECHNOLOGY)):
                            outs2 = sorted(set(o[o.TECHNOLOGY == k2].FUEL))
                            rows.append([c, t, fu, k2, ctype(k2, outs2), f"via {k} ({fu2})"])
                else:
                    rows.append([c, t, fu, k, ctype(k, outs), ""])
with open(out, "w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["country", "supply_row", "fuel_code_out", "consumer_technology", "consumer_type", "path_note"])
    w.writerows(rows)
df = pd.DataFrame(rows, columns=["country", "supply_row", "fuel", "tech", "type", "note"])
print(df.groupby(["country", "supply_row", "type"]).size().unstack(fill_value=0).to_string())
