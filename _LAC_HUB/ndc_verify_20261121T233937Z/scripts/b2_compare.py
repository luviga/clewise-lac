"""Step B: compare check 1 (scout reading) with check 2 (blind reading).

For each value of values_to_verify.csv, take the blind answers of its blind item, keep those of the
same year (years compared on their four-digit parts; an answer without a year matches any year),
and compare values. Writes parts/compare_<code>.csv with check2_status:
  agree       a blind answer of the same year has the same value (equal after rounding to the
              decimals of the shorter of the two, or equal as percent and fraction)
  differs     blind answers exist for that year but none has the same value
  not found   no blind value for that item and year
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, CODES, read_csv, write_csv


def fnum(x):
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


def years(s):
    ys = re.findall(r"(?:19|20)\d\d", str(s))
    return set(ys)


def decs(s):
    s = str(s)
    return len(s.split(".")[1]) if "." in s else 0


def same(a, b, sa, sb):
    if a is None or b is None:
        return False
    d = min(decs(sa), decs(sb))
    if round(a, d) == round(b, d) or abs(a - b) <= 1e-9 * max(1, abs(a)):
        return True
    if abs(a * 100 - b) < 1e-6 or abs(a - b * 100) < 1e-6:
        return True
    if abs(abs(a) - abs(b)) < 1e-9 * max(1, abs(a)):  # sign convention (removals printed negative)
        return True
    return False


def main():
    vals = read_csv(os.path.join(JOB, "values_to_verify.csv"))
    for code in CODES:
        key = {r["value_id"]: r["blind_id"] for r in read_csv(os.path.join(JOB, "parts", f"blind_key_{code}.csv"))}
        ans = {}
        for r in read_csv(os.path.join(JOB, f"blind_answers_{code}.csv")):
            ans.setdefault(r["blind_id"], []).append(r)
        rows = []
        for v in vals:
            if v["country"] != code:
                continue
            bid = key[v["value_id"]]
            a = ans.get(bid, [])
            vy = years(v["year"])
            cand = [x for x in a if x["value"].strip() and (not vy or not years(x["year"]) or vy & years(x["year"]))]
            x1 = fnum(v["value"])
            match = [x for x in cand if same(x1, fnum(x["value"]), v["value"], x["value"])]
            if v["numeric"] == "False":
                st = "not numeric"
            elif match:
                st = "agree"
            elif cand:
                st = "differs"
            else:
                st = "not found"
            pick = match[0] if match else (cand[0] if cand else (a[0] if a else {}))
            rows.append({"value_id": v["value_id"], "blind_id": bid, "source_id": v["source_id"],
                         "check1_page": v["page"], "check1_value": v["value"], "check1_unit": v["unit"], "check1_year": v["year"],
                         "check2_page": pick.get("page_read", ""), "check2_value": pick.get("value", ""),
                         "check2_unit": pick.get("unit", ""), "check2_year": pick.get("year", ""),
                         "check2_reference": pick.get("reference", ""), "check2_note": pick.get("note", ""),
                         "check2_status": st,
                         "check2_other_answers": " | ".join(f"{x['page_read']} {x['value']} {x['unit']} {x['year']}" for x in cand if x is not pick)[:300]})
        write_csv(os.path.join(JOB, "parts", f"compare_{code}.csv"), rows)
        c = {}
        for r in rows:
            c[r["check2_status"]] = c.get(r["check2_status"], 0) + 1
        print(code, c)


if __name__ == "__main__":
    main()
