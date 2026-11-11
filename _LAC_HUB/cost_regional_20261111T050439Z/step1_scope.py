"""Step 1: select the plant cost groups that rest only on international sources."""
import pandas as pd, re, sys
PA = "../cost_review_20261111T015203Z/proposals_all.csv"
ALLOWED = {
    "CostaRica": {"CRC-001", "CRC-010", "CRC-011", "CRC-013", "CRC-014"},
    "DominicanRepublic": {"CSD-009", "CSD-011", "CSD-012"},
    "Ecuador": {"ATB-001", "BEN-004"},
    "Guatemala": {f"INT-00{i}" for i in range(1, 10)} | {"INT-013"},
    "Honduras": {"CSH-011", "CSH-013"},
    "Jamaica": {"CSJ-006", "PSJ-001", "PSJ-002", "PSJ-006"},
}
def ids(s):
    return [x for x in re.split(r"[;,|\s]+", str(s)) if x and x != "nan"]
def select():
    d = pd.read_csv(PA, dtype=str)
    pv = pd.to_numeric(d["proposed_value"], errors="coerce")
    m = (d["fuel_scenario"] == "ALL") & pv.notna() & (pv != 0)
    m &= d.apply(lambda r: len(ids(r["source_ids"])) > 0 and set(ids(r["source_ids"])) <= ALLOWED.get(r["country"], set()), axis=1)
    return d, d[m].copy()
if __name__ == "__main__":
    d, s = select()
    print(len(s), s.groupby(["country", "Tech", "Parameter"]).ngroups, s.groupby(["country", "Tech"]).ngroups)
    print(s.groupby("country").size().to_dict())
    print(s["source_ids"].value_counts().head(30))
