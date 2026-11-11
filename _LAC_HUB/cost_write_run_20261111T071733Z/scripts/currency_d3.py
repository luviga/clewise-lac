"""D3 currency classification for non-fuel cost groups (LAC_OVERNIGHT_COST_RUN).

For one proposal row, find the currency year of its value, in this order:

  1. zero         a zero value stays zero (no year needed);
  2. convention   Costa Rica: the source job states the workbook convention,
                  2021 column in 2021 USD and 2022 to 2050 in 2022 USD
                  (LAC_COST_SRC_CR REPORT line 58 and GAPS item 11); the
                  import price IMPELE is the 2024 annual price (2024 USD);
  3. 2024 shown   the derivation shows a CPI-U step to 2024 (313.689 / CPI(Y),
                  "CPI 2024/Y", the factors 1.212039 = 2024/2020 or
                  1.071873 = 2024/2022) or holds an observed 2024 price;
  4. deflated     the derivation steps away from 2024 (CPI(Y) / 313.689 or
                  CPIU_Y/CPIU_Z): the value is in the target year Y;
  5. at value     a currency year written right after the proposed number
                  ("1794.74 (2022 USD)", "1806.38, 2019 USD");
  6. stated       the last currency year written in the clause the value
                  comes from (the "newer edition" clause for upgrade rows,
                  the text before it otherwise);
  7. source       one currency year stated in the sources.csv entries of the
                  row's source ids ("Values in 2022 USD", "dolares de 2020",
                  "January 1 2010 price levels", "Dollar year 2018");
  otherwise       not stated, or ambiguous (several years), and the value is
                  left as it is.
Returns (year or None, how, evidence).
"""
from __future__ import annotations

import re

CPI = {2017: 245.12, 2018: 251.107, 2019: 255.657, 2020: 258.811, 2021: 270.97,
       2022: 292.655, 2023: 304.702, 2024: 313.689, 2025: 321.943}
_CPI_TXT = {y: f"{v:.3f}".rstrip("0").rstrip(".") for y, v in CPI.items()}
CPI_BY_VALUE = {t: y for y, t in _CPI_TXT.items()}

RE_TO_2024 = [
    re.compile(r"313\.689\s*/\s*(?:CPI(?:U)?_?\s*20\d\d\s*)?([23]\d\d\.\d+)"),
    re.compile(r"CPI(?:-U|U)?_?\s*2024\s*/\s*(?:CPI(?:-U|U)?_?\s*)?(20\d\d)"),
    re.compile(r"CPI(?:-U)?\s*(?:2024/20\d\d\s*)?(1\.212039|1\.071873)"),
    re.compile(r"x\s*(1\.212039|1\.071873)"),
    re.compile(r"CPI_FACTOR_(20\d\d)_TO_2024"),
]
RE_HELD_2024 = re.compile(r"2024 price held|held at the 2024 (?:value|volume-weighted|price|import)|"
                          r"Informe Anual 2024.*held at the 2024 value")
RE_FROM_2024 = re.compile(r"([23]\d\d\.\d+)\s*/\s*(?:CPI(?:U)?_?\s*2024\s*)?313\.689")
RE_CPIU_RATIO = re.compile(r"CPIU_(20\d\d)\s*/\s*CPIU_(20\d\d)")
RE_STATED = re.compile(r"\((?:Dec-)?(20\d\d) USD|\b(20\d\d) USD\b|\(January (?:1 )?(20\d\d) prices\)|"
                       r"real (20\d\d) USD|dolares de (20\d\d)")
RE_AFTER_VALUE = re.compile(r"^\s*(?:USD/[A-Za-z-]+\s*)?(?:\(|,\s*)(?:Dec-)?(20\d\d) USD")
RE_SOURCE = re.compile(r"[Vv]alues in (20\d\d) USD|[Cc]osts in (20\d\d) USD|\((20\d\d) USD|"
                       r"dolares de (20\d\d)|(?:January 1 )?(20\d\d) price levels|Dollar year (20\d\d)")
NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")


def _first(groups):
    return next(g for g in groups if g)


def _value_hits(d: str, v: float):
    for m in NUM.finditer(d):
        try:
            num = float(m.group().replace(",", ""))
        except ValueError:
            continue
        if v != 0 and abs(num - v) <= max(0.0051, 5e-5 * abs(v)):
            yield m


def classify(derivation: str, source_texts: dict, country: str, year: int, tech: str,
             value, change_class: str):
    d = derivation or ""
    if value is not None and value == 0:
        return None, "zero", "zero value stays zero"
    if country == "CostaRica":
        if tech == "IMPELE":
            return 2024, "2024 shown", "2024 annual import price (ICE DOCSE Informe Anual 2024), held at the 2024 value"
        return (2021 if year == 2021 else 2022), "convention", \
            "LAC_COST_SRC_CR: 2021 column in 2021 USD, 2022 to 2050 in 2022 USD (REPORT line 58, GAPS item 11)"
    m = RE_FROM_2024.search(d)
    if m:
        y = CPI_BY_VALUE.get(m.group(1).rstrip("0").rstrip("."))
        if y and y != 2024:
            return y, "deflated", m.group(0)
    m = RE_CPIU_RATIO.search(d)
    if m and m.group(1) != "2024":
        return int(m.group(1)), "deflated", m.group(0)
    for rx in RE_TO_2024:
        m = rx.search(d)
        if m:
            return 2024, "2024 shown", m.group(0)
    m = RE_HELD_2024.search(d)
    if m:
        return 2024, "2024 shown", m.group(0)
    if value is not None:
        for hit in _value_hits(d, value):
            mm = RE_AFTER_VALUE.match(d[hit.end():hit.end() + 30])
            if mm:
                return int(mm.group(1)), "at value", d[hit.start():hit.end() + mm.end()]
    i = d.find("newer edition")
    clause = (d[i:] if change_class == "upgrade" else d[:i]) if i != -1 else d
    found = [int(_first(x.groups())) for x in RE_STATED.finditer(clause)]
    if found:
        return found[-1], "stated", list(RE_STATED.finditer(clause))[-1].group(0)
    years = {}
    for sid, txt in source_texts.items():
        for x in RE_SOURCE.finditer(txt or ""):
            years.setdefault(int(_first(x.groups())), []).append(sid)
    if len(years) == 1:
        y, ids = next(iter(years.items()))
        return y, "source", f"sources.csv {';'.join(sorted(set(ids)))}"
    if len(years) > 1:
        return None, "ambiguous", "source entries state " + ", ".join(
            f"{y} ({';'.join(sorted(set(ids)))})" for y, ids in sorted(years.items()))
    return None, "not stated", "no currency year in the derivation or the source entries"
