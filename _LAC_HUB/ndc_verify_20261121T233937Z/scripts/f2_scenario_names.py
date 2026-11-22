"""Step F: scenario_names.csv, every scenario name in code, folder names, workbook sheets and cells.

Workbooks are read as zip archives (read-only): sheet names from xl/workbook.xml; cell text from
xl/sharedStrings.xml and inline strings, counted per cell by the shared-string index in each sheet.
A scenario name is a token of the list below, matched as a whole token after splitting on
non-alphanumeric characters and underscores.
Usage: python -I f2_scenario_names.py <repo root>
"""
import collections
import html
import os
import re
import subprocess
import sys
import zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, read_csv, write_csv

REPO = sys.argv[1]
NAMES = ["BAU", "NDCNEW", "LTSNEW", "NDCcond", "NDCincond", "NDP", "NDPAMB", "NDCINC", "LTSOPT", "Default", "NDC", "LTS",
         "NDCCOND", "NDCINCOND", "LTSNEW2", "NDCNEW2", "NDC_cond", "NDCAMB", "LTSAMB", "CN", "NDCINCOND"]
NAMESET = set(NAMES)


def tokens(s):
    out = set()
    for t in re.split(r"[^A-Za-z0-9_]+", s):
        if not t:
            continue
        out.add(t)
        out |= set(t.split("_"))
    return out & NAMESET


files = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
files = [f for f in files if not f.startswith("_LAC_HUB/")]
places = collections.defaultdict(collections.Counter)  # name -> Counter(place kind:place)
count = collections.Counter()

# code literals (from f1)
for r in read_csv(os.path.join(JOB, "parts", "scenario_names_code.csv")):
    places[r["name"]]["code: " + r["place"].rsplit(":", 1)[0]] += 1
    count[(r["name"], "code literal")] += 1

# folder names
seen_dirs = set()
for f in files:
    parts = f.split("/")[:-1]
    for i, p in enumerate(parts):
        d = "/".join(parts[: i + 1])
        if d in seen_dirs:
            continue
        seen_dirs.add(d)
        for n in tokens(p):
            places[n]["folder: " + d] += 1
            count[(n, "folder name")] += 1

# workbooks
bad = []
for f in files:
    if not f.lower().endswith((".xlsx", ".xlsm")):
        continue
    try:
        z = zipfile.ZipFile(os.path.join(REPO, f))
    except Exception as e:
        bad.append(f)
        continue
    with z:
        names = z.namelist()
        try:
            wb = z.read("xl/workbook.xml").decode("utf-8", "replace")
        except KeyError:
            bad.append(f)
            continue
        sheets = [html.unescape(s) for s in re.findall(r'<sheet [^>]*name="([^"]+)"', wb)]
        for s in sheets:
            for n in tokens(s):
                places[n][f"sheet: {f} [{s}]"] += 1
                count[(n, "workbook sheet")] += 1
        ss = []
        if "xl/sharedStrings.xml" in names:
            x = z.read("xl/sharedStrings.xml").decode("utf-8", "replace")
            for si in re.findall(r"<si>(.*?)</si>", x, re.S):
                ss.append(html.unescape("".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S))))
        hit_idx = {i: tokens(s) for i, s in enumerate(ss)}
        hit_idx = {i: t for i, t in hit_idx.items() if t}
        sheet_files = sorted(n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        for sf in sheet_files:
            x = z.read(sf).decode("utf-8", "replace")
            if hit_idx:
                for idx in re.findall(r'<c [^>]*t="s"[^>]*>\s*<v>(\d+)</v>', x):
                    t = hit_idx.get(int(idx))
                    if t:
                        for n in t:
                            places[n][f"cells: {f}"] += 1
                            count[(n, "workbook cell")] += 1
            for s in re.findall(r'<c [^>]*t="inlineStr"[^>]*>.*?<t[^>]*>(.*?)</t>', x, re.S):
                for n in tokens(html.unescape(s)):
                    places[n][f"cells: {f}"] += 1
                    count[(n, "workbook cell")] += 1

rows = []
for n in sorted(places, key=lambda k: (-sum(places[k].values()), k)):
    pl = places[n]
    by_kind = {k: count[(n, k)] for k in ["code literal", "folder name", "workbook sheet", "workbook cell"]}
    top = sorted(pl.items(), key=lambda kv: -kv[1])
    rows.append({"scenario_name": n, "count_total": sum(by_kind.values()),
                 "count_code_literals": by_kind["code literal"], "count_folder_names": by_kind["folder name"],
                 "count_workbook_sheets": by_kind["workbook sheet"], "count_workbook_cells": by_kind["workbook cell"],
                 "n_places": len(pl),
                 "final_name": {"BAU": "BAU", "NDCNEW": "NDC", "LTSNEW": "LTS"}.get(n, "not used (old or other name)"),
                 "places_top20": "; ".join(f"{k} ({v})" for k, v in top[:20])})
write_csv(os.path.join(JOB, "scenario_names.csv"), rows)
# full place list in parts
full = [{"scenario_name": n, "place": k, "count": v} for n in places for k, v in places[n].items()]
write_csv(os.path.join(JOB, "parts", "scenario_names_places.csv"), sorted(full, key=lambda r: (r["scenario_name"], r["place"])))
print("names", len(rows), "places", len(full), "unreadable workbooks", len(bad), bad[:5])
for r in rows:
    print(r["scenario_name"], r["count_total"], r["count_code_literals"], r["count_folder_names"], r["count_workbook_sheets"], r["count_workbook_cells"])
