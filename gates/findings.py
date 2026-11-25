"""Rows of gate_results.csv and gate_summary.csv."""
from __future__ import annotations

import csv
from collections import Counter

FIELDS = ["check", "class", "model", "scenario", "point", "parameter", "technology", "fuel", "emission", "year",
          "timeslice", "values", "message"]


def row(ctx, check, cls, parameter="", technology="", fuel="", emission="", year="", timeslice="", values="",
        message=""):
    return {"check": check, "class": cls, "model": ctx.get("model", ""), "scenario": ctx.get("scenario", ""),
            "point": ctx.get("point", ""), "parameter": parameter, "technology": technology, "fuel": fuel,
            "emission": emission, "year": year, "timeslice": timeslice, "values": values, "message": message}


def write(rows, out_results, out_summary):
    with open(out_results, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    c = Counter((r["check"], r["class"], r["model"], r["point"]) for r in rows)
    with open(out_summary, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["check", "class", "model", "point", "count"])
        for k in sorted(c):
            w.writerow(list(k) + [c[k]])
