"""National (route 1) and manual import statistics, read into one record format.

Each record: country, source_id, file, year, line, hs6, line_description, value, currency,
value_basis, units (None when the source gives no count), new_used, note, and for statistics
by vehicle type instead of tariff line, type_label (matched in national_type_map.csv).
"""
import csv
import glob
import os
import re

import pdfplumber

TYPE_LABELS_DR = ["Automóviles", "Jeepetas", "Vehículos De Carga", "Vehículos de carga",
                  "Furgonetas Y Minivans", "Furgonetas y Minivans", "Autobuses",
                  "Vehículos De Turismo", "Vehículos de turismo", "Otros"]

NUM = r"-?[\d,]+(?:\.\d+)?"


def _num(s):
    return float(s.replace(",", ""))


def page_lines(page, gap=6.0):
    """Rebuild text lines from the characters of a PDF page: characters on the same height are
    joined, with a space where the horizontal gap exceeds `gap` points (the DGA tables place
    characters one by one, which defeats the default word grouping)."""
    rows = {}
    for c in page.chars:
        rows.setdefault(round(c["top"] / 3), []).append(c)
    out = []
    for k in sorted(rows):
        s, prev = "", None
        for c in sorted(rows[k], key=lambda c: c["x0"]):
            if prev is not None and c["x0"] - prev > gap:
                s += " "
            s += c["text"]
            prev = c["x1"]
        out.append(s)
    return out


def dga_vehicle_bulletins(job):
    """DGA (Dominican Republic) annual vehicle bulletins: units and FOB (US$ million) by vehicle
    type for the year of the bulletin and the year before."""
    out = []
    for fn in sorted(glob.glob(os.path.join(job, "downloads", "DR", "DGA_*vehiculos_*.pdf"))):
        with pdfplumber.open(fn) as pdf:
            lines = [ln.strip() for p in pdf.pages for ln in page_lines(p)]
        section = None
        years = None
        got = {}
        for i, ln in enumerate(lines):
            low = ln.lower()
            if "por tipo de veh" in low or "según tipo" in low or "segun tipo" in low:
                section = "pending"
                years = None
                continue
            if section == "pending":
                if "cantidad" in low:
                    section = "units"
                elif "valor fob" in low:
                    section = "value"
                continue
            if section in ("units", "value") and years is None:
                ys = re.findall(r"\b(20\d\d)\b", ln)
                if len(ys) >= 2 and not re.search(r"enero|diciembre", low):
                    years = (int(ys[0]), int(ys[1]))
                continue
            if section in ("units", "value") and years:
                if low.startswith("total"):
                    section = None
                    continue
                for lab in TYPE_LABELS_DR:
                    if ln.startswith(lab + " "):
                        nums = re.findall(NUM, ln[len(lab):])
                        if len(nums) >= 2:
                            key = lab.lower()
                            for y, v in zip(years, nums[:2]):
                                got.setdefault((key, y), {})[section] = _num(v)
                        break
        rel = os.path.relpath(fn, job).replace("\\", "/")
        for (key, y), d in sorted(got.items()):
            if "units" not in d or "value" not in d:
                continue
            label = next(l for l in TYPE_LABELS_DR if l.lower() == key)
            out.append({
                "country": "DR", "source_id": "DR-DGA-" + ("2020" if "2020-12" in fn else "2024"),
                "file": rel, "year": y, "line": "DGA type: " + label, "hs6": "", "type_label": label,
                "line_description": f"DGA vehicle type {label} (headings 8702 to 8705, despacho a consumo)",
                "value": d["value"] * 1e6, "currency": "USD", "value_basis": "FOB",
                "units": d["units"], "new_used": "all",
                "note": "FOB only (the bulletin gives no CIF); new and used together; all fuels together",
            })
    return out


# ---------------------------------------------------------------- manual files (generic tables)
UNIT_KEYS = ("unidades", "cantidad", "quantity", "units", "unit count", "num")
VALUE_KEYS_CIF = ("cif",)
VALUE_KEYS = ("valor", "value", "usd", "us$", "fob")
CODE_KEYS = ("inciso", "partida", "codigo", "código", "code", "hs", "sac", "tariff", "arancel")
YEAR_KEYS = ("año", "ano", "year", "periodo", "period")
STATE_KEYS = ("estado", "condicion", "condición", "new", "nuevo", "usado", "used")


def _find(header, keys, exclude=()):
    for j, h in enumerate(header):
        hl = str(h or "").strip().lower()
        if any(k in hl for k in keys) and not any(x in hl for x in exclude):
            return j
    return None


def _table_rows(path):
    if path.lower().endswith((".xlsx", ".xlsm")):
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        for ws in wb.worksheets:
            yield ws.title, [list(r) for r in ws.iter_rows(values_only=True)]
    elif path.lower().endswith((".csv", ".txt")):
        with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
            sample = f.read(4096)
            f.seek(0)
            delim = ";" if sample.count(";") > sample.count(",") else ","
            yield "csv", list(csv.reader(f, delimiter=delim))


def manual_records(cc, job):
    """Tables saved by hand under downloads/manual/<CC>/ (xlsx or csv). The parser looks for a
    header row with a tariff-code column, a units column and a value column (CIF preferred);
    the year comes from a year column or from the file name; the currency is local when the
    value header or the file name says so (for example JMD, CRC, GTQ, HNL, DOP, 'local'),
    otherwise US$."""
    out = []
    local = {"CR": "CRC", "DR": "DOP", "GUA": "GTQ", "HON": "HNL", "JAM": "JMD"}[cc]
    for path in sorted(glob.glob(os.path.join(job, "downloads", "manual", cc, "*"))):
        if not path.lower().endswith((".xlsx", ".xlsm", ".csv", ".txt")):
            continue
        rel = os.path.relpath(path, job).replace("\\", "/")
        fname_year = re.findall(r"(20\d\d)", os.path.basename(path))
        found = False
        for sheet, rows in _table_rows(path):
            for hi, header in enumerate(rows[:40]):
                cu = _find(header, UNIT_KEYS, exclude=("kg", "kilo", "peso", "weight"))
                cc_ = _find(header, CODE_KEYS, exclude=("descrip",))
                cv = _find(header, VALUE_KEYS_CIF) or _find(header, VALUE_KEYS, exclude=("kg", "unit"))
                if cu is None or cc_ is None or cv is None:
                    continue
                found = True
                cy = _find(header, YEAR_KEYS)
                cs = _find(header, STATE_KEYS)
                vh = str(header[cv]).lower()
                cur = local if (local.lower() in vh or "local" in vh or local.lower() in path.lower()) else "USD"
                basis = "CIF" if "cif" in vh else ("FOB" if "fob" in vh else "value as published")
                for r in rows[hi + 1:]:
                    if r is None or len(r) <= max(cu, cc_, cv):
                        continue
                    code = re.sub(r"[^0-9]", "", str(r[cc_] or ""))
                    if not code[:4] in ("8702", "8703", "8704", "8711") or len(code) < 6:
                        continue
                    try:
                        units = float(str(r[cu]).replace(",", ""))
                        value = float(str(r[cv]).replace(",", ""))
                    except (TypeError, ValueError):
                        continue
                    year = None
                    if cy is not None and r[cy] is not None:
                        m = re.search(r"(20\d\d)", str(r[cy]))
                        year = int(m.group(1)) if m else None
                    if year is None and len(fname_year) == 1:
                        year = int(fname_year[0])
                    if year is None:
                        continue
                    state = "all"
                    if cs is not None and r[cs] is not None:
                        s = str(r[cs]).lower()
                        state = "used" if ("usad" in s or "used" in s) else ("new" if ("nuev" in s or "new" in s) else "all")
                    out.append({
                        "country": cc, "source_id": f"{cc}-MANUAL", "file": rel, "year": year,
                        "line": code, "hs6": code[:6], "line_description": f"national line {code} ({sheet})",
                        "value": value, "currency": cur, "value_basis": basis, "units": units,
                        "new_used": state, "note": "file saved by hand under downloads/manual",
                    })
                break
        if not found:
            print(f"WARNING {rel}: no header row with a tariff code, a units and a value column; not read")
    # aggregate national lines per line and year (a table may list months or origins)
    agg = {}
    for r in out:
        k = (r["file"], r["year"], r["line"], r["new_used"])
        if k in agg:
            agg[k]["value"] += r["value"]
            agg[k]["units"] += r["units"]
        else:
            agg[k] = dict(r)
    return list(agg.values())


def records(cc, job):
    recs = manual_records(cc, job)
    if cc == "DR":
        recs += dga_vehicle_bulletins(job)
    return recs
