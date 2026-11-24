"""Build register_history.csv and history_plan.csv (read-only on workbooks)."""
import io, csv, re, os
import openpyxl

ROOT = r"C:\clw_align"
WORK = r"C:\clw_align\_LAC_HUB\align_20261124T021708Z\work"
MODELS = {
    "CostaRica": r"CostaRica\CR_ENERGY\t1_confection",
    "DominicanRepublic": r"DominicanRepublic\RD_ENERGY",
    "Ecuador": r"Ecuador\ECU_Energy",
    "Jamaica": r"Jamaica\JAM_ENERGY",
}
MODEL_LABEL = {k: v.replace("\\t1_confection", "").replace("\\", "/") for k, v in MODELS.items()}
K = 31.536  # PJ per GW-year

# ---------------------------------------------------------------- sources (new ids)
SRC = {
    "HB-CENCE-2021": "ICE CENCE, Informe Anual de la Operacion del SEN 2021, https://apps.grupoice.com/CenceWeb/documentos/3/3008/16/Informe%20%20Anual%20CENCE%202021.pdf",
    "HB-CENCE-2022": "ICE DOCSE, Informe Anual 2022, https://apps.grupoice.com/CenceWeb/documentos/3/3008/19/Informe%20Anual%20DOCSE%202022.pdf",
    "HB-CENCE-2023": "ICE DOCSE, Informe Anual 2023, https://apps.grupoice.com/CenceWeb/documentos/3/3008/21/Informe%20Anual%202023.pdf",
    "HB-CENCE-2024": "ICE DOCSE, Informe Anual 2024, https://apps.grupoice.com/CenceWeb/documentos/3/3008/24/Informe%20Anual%202024.pdf",
    "HB-OC-2024": "OC-SENI, Memoria Anual 2024, https://www.oc.do/DesktopModules/Bring2mind/DMX/API/Entries/Download?EntryId=200289&PortalId=0",
    "HB-OC-2021": "OC-SENI, Memoria Anual 2021, https://www.oc.do/DesktopModules/Bring2mind/DMX/API/Entries/Download?EntryId=176192&PortalId=0",
    "HB-OC-2022": "OC-SENI, Memoria Anual 2022, https://www.oc.do/DesktopModules/Bring2mind/DMX/API/Entries/Download?EntryId=187274&PortalId=0",
    "HB-OC-2023": "OC-SENI, Memoria Anual 2023, https://www.oc.do/DesktopModules/Bring2mind/DMX/API/Entries/Download?EntryId=194910&PortalId=0",
    "FR2-D3-CNEGEN": "CNE DataCNE, GeneracionFuenteSENI.xlsx, https://datacne.gob.do/api/dropbox/pdf-proxy?path=/generaci%C3%B3n%20y%20consumo%20por%20central/generaci%C3%B3n%20por%20fuente/generacionfuenteseni.xlsx",
    "HB-CNE-MEM2024": "CNE, Memoria Institucional 2024, listed at https://cne.gob.do/transparencia/planes-estrategicos-institucion/memoria-institucional/",
    "HB-ARCONEL-2021": "ARCONEL, Estadistica Anual y Multianual del Sector Electrico Ecuatoriano 2021 (publisher site arconel.gob.ec, statistics page)",
    "HB-ARCONEL-2022": "ARCONEL, Estadistica Anual y Multianual del Sector Electrico Ecuatoriano 2022 (publisher site arconel.gob.ec, statistics page)",
    "HB-ARCONEL-2023": "ARCONEL, Estadistica Anual y Multianual del Sector Electrico Ecuatoriano 2023 (publisher site arconel.gob.ec, statistics page)",
    "HB-ARCONEL-2024": "ARCONEL, Estadistica Anual y Multianual del Sector Electrico Ecuatoriano 2024, https://arconel.gob.ec/wp-content/uploads/downloads/2025/04/Estadistica2024_abr.pdf",
    "HB-OUR-AR2425": "Office of Utilities Regulation, Annual Report 2024-2025, https://our.org.jm/wp-content/uploads/2025/12/Annual-Report-2024-2025-low-res-compressed.pdf",
    "HB-OUR-AR2324": "Office of Utilities Regulation, Annual Report 2023-2024, https://our.org.jm/wp-content/uploads/2024/11/OUR-Annual-Report-2023-24.pdf",
    "HB-IRP2022": "MSETT, 2022 Jamaica Integrated Resource Plan, https://www.mset.gov.jm/wp-content/uploads/2024/11/2022-Jamaica-Integrated-Resource-Plan.pdf",
    "HB-OUR-DET2023": "OUR, JPS Annual Review 2023 Determination Notice, https://our.org.jm/wp-content/uploads/2023/08/JPS-2023-Annual-Tariff-Review-Determination-Notice.pdf",
}


def load(p, data_only=False):
    return openpyxl.load_workbook(io.BytesIO(open(p, "rb").read()), data_only=data_only)


WB = {}


def wb(country, fname):
    key = (country, fname)
    if key not in WB:
        WB[key] = load(os.path.join(ROOT, MODELS[country], *fname.split("/")))
    return WB[key]


def ao_cell(country, sheet, tech, param, year):
    w = wb(country, "A1_Outputs/A-O_Parametrization.xlsx")[sheet]
    hdr = [c.value for c in w[1]]
    ti, pi = hdr.index("Tech"), hdr.index("Parameter")
    col = [str(h) for h in hdr].index(str(year))
    for r in range(2, w.max_row + 1):
        if w.cell(r, ti + 1).value == tech and w.cell(r, pi + 1).value == param:
            return w.cell(r, col + 1).value, r
    raise KeyError((country, sheet, tech, param, year))


def b1_cell(country, tech, param, header):
    w = wb(country, "B1_Scenario_Config.xlsx")["Electrical"]
    hdr = [str(c.value) for c in w[1]]
    si, ti, pi, ci = hdr.index("Scenario"), hdr.index("Tech_Set"), hdr.index("Parameter"), hdr.index(header)
    yi = hdr.index("Exact_Years")
    hits = []
    for r in range(2, w.max_row + 1):
        if w.cell(r, si + 1).value == "BAU" and str(w.cell(r, ti + 1).value).strip() == tech and w.cell(r, pi + 1).value == param:
            hits.append(r)
    assert len(hits) == 1, (country, tech, param, hits)
    r = hits[0]
    return w.cell(r, ci + 1).value, w.cell(r, yi + 1).value, r


def replace_years(values_text, years_text, newvals):
    """Replace the tokens of the given years in an Exact_Values text, keeping every other character."""
    ys = [t.strip() for t in str(years_text).split(";")]
    parts = re.split(r"(;)", str(values_text))
    # tokens are parts at even positions
    tok_idx = [i for i in range(0, len(parts), 2)]
    out = list(parts)
    for y, v in newvals.items():
        k = ys.index(str(y))
        i = tok_idx[k]
        old = parts[i]
        lead = old[: len(old) - len(old.lstrip())]
        trail = old[len(old.rstrip()):]
        out[i] = f"{lead}{v}{trail}"
    return "".join(out)


ROWS = []


def fmtv(v):
    if isinstance(v, float):
        return repr(round(v, 6)) if abs(v) >= 1e-4 else repr(v)
    return str(v)


def add(country, file, sheet, tech, param, year, before, after, unit, sid, page, deriv, assume="", lo="", hi=""):
    ROWS.append({
        "model": MODEL_LABEL[country], "file": file, "sheet": sheet, "tech": tech, "parameter": param,
        "year": year, "before": before if before is not None else "", "after": after, "unit": unit,
        "source_id": sid, "page": page, "derivation": deriv, "assumption_sentence": assume,
        "range_low": lo, "range_high": hi})


AO = "A1_Outputs/A-O_Parametrization.xlsx"
B1 = "B1_Scenario_Config.xlsx"


def ao(country, sheet, tech, param, year, after, unit, sid, page, deriv, **kw):
    before, r = ao_cell(country, sheet, tech, param, year)
    if isinstance(before, (int, float)) and not isinstance(after, str) and abs(float(before) - float(after)) < 1e-9:
        return
    add(country, AO, sheet, tech, param, str(year), before, after, unit, sid, page, deriv, **kw)


def ao_carry(country, sheet, tech, param, y0, y1, old, new, unit, sid, page, deriv):
    """Carry a new flat value into later years whose cell is the literal old value."""
    for y in range(y0, y1 + 1):
        before, r = ao_cell(country, sheet, tech, param, y)
        if isinstance(before, (int, float)) and abs(float(before) - old) < 1e-9:
            add(country, AO, sheet, tech, param, str(y), before, new, unit, sid, page, deriv)


def b1(country, tech, param, newvals, unit, sid, page, deriv, divide=1.0):
    before, years, r = b1_cell(country, tech, param, "Exact_Values")
    nv = {y: (f"{v / divide:.6f}".rstrip("0").rstrip(".") if isinstance(v, float) else v) for y, v in newvals.items()}
    after = replace_years(before, years, nv)
    add(country, B1, "Electrical", f"BAU|{tech}", param, "Exact_Values", before, after, unit, sid, page, deriv)
    return before, years


PLAN = []


def plan(country, tech, cap, builds, res_b, res_a, ll_b, ll_a, cf, cf_src, status, note):
    d = {"country": country, "tech": tech}
    for i, y in enumerate(range(2021, 2025)):
        d[f"recorded_capacity_gw_{y}"] = cap[i] if cap else ""
    for i, y in enumerate(range(2021, 2025)):
        d[f"recorded_builds_gw_{y}"] = builds[i] if builds else ""
    for i, y in enumerate(range(2021, 2025)):
        d[f"residual_before_gw_{y}"] = res_b[i] if res_b else ""
        d[f"residual_after_gw_{y}"] = res_a[i] if res_a else ""
    for i, y in enumerate(range(2021, 2025)):
        d[f"lower_limit_before_pj_{y}"] = ll_b[i] if ll_b else ""
        d[f"lower_limit_after_pj_{y}"] = ll_a[i] if ll_a else ""
    for i, y in enumerate(range(2021, 2025)):
        d[f"max_producible_pj_{y}"] = round(cap[i] * K * cf, 4) if (cap and cf and cap[i] != "") else ""
    d["published_cf"] = cf if cf else ""
    d["cf_source"] = cf_src
    d["status_expected"] = status
    d["note"] = note
    PLAN.append(d)


# ================================================================ COSTA RICA
C = "CostaRica"
S = "Secondary Techs"; P = "Primary Techs"
cr_cap_src = "HB-CENCE-2021|HB-CENCE-2022|HB-CENCE-2023|HB-CENCE-2024"
cr_cap_page = "p.29; p.29; p.27; p.25 (Capacidad Instalada en placa)"

# PWRFOI: bunker plate 227.661 MW every year (Guapiles 14.267 + Orotina 10.686 + Garabito 202.708)
foi = 0.227661
cf_foi = 836959.433 / (227.661 * 8760)  # CENCE 2024 bunker generation / plate capacity
d_foi = "Bunker plants Guapiles 14,267 + Orotina 10,686 + Garabito 202,708 kW plate = 227,661 kW in each year 2021-2024 (CENCE capacity tables); no bunker plant added or retired 2021-2024"
ao(C, S, "PWRFOI", "ResidualCapacity", 2021, foi, "GW", cr_cap_src, cr_cap_page, d_foi)
for y in (2022, 2023, 2024):
    ao(C, S, "PWRFOI", "ResidualCapacity", y, foi, "GW", cr_cap_src, cr_cap_page, d_foi)
ao_carry(C, S, "PWRFOI", "ResidualCapacity", 2025, 2050, 0.214, foi, "GW", cr_cap_src, cr_cap_page,
         d_foi + "; the end-2024 stock is held in later years where the row held the 2024 value")
b1(C, "PWRFOI", "TotalAnnualMaxCapacity", {2021: foi, 2022: foi, 2023: foi, 2024: foi}, "GW", cr_cap_src, cr_cap_page,
   d_foi + "; history years 2021-2024 capped at the recorded capacity so no plant is built; later years unchanged")
ll_foi24 = round(836959.433 * 0.0036 / 1000 * 0.99, 6)
d_ll = (f"2024 lower limit 3.2008 PJ exceeds what 0.227661 GW can produce at the highest published bunker capacity factor "
        f"{cf_foi:.4f} (CENCE 2024: 836,959.433 MWh / (227.661 MW x 8,760 h)), 0.227661 x 31.536 x {cf_foi:.4f} = {foi*K*cf_foi:.4f} PJ; "
        f"the 3.2008 PJ includes the 52,560.939 MWh of PTA Garabito (rented block, diesel per ARESEP fuel records). "
        f"Corrected to bunker generation 836,959.433 MWh x 0.0036 PJ/GWh / 1000 x 0.99 (the model's history band) = {ll_foi24} PJ")
bv, by = b1(C, "PWRFOI", "TotalTechnologyAnnualActivityLowerLimit", {2024: ll_foi24}, "PJ", "HB-CENCE-2024", "p.20 (Por Fuente and plant columns)", d_ll)
ao(C, S, "PWRFOI", "TotalTechnologyAnnualActivityLowerLimit", 2024, ll_foi24, "PJ", "HB-CENCE-2024", "p.20", d_ll + "; A-O cell feeds the 2024 capacity factor formula")
ao(C, S, "PWRFOI", "TotalAnnualMaxCapacity", 2024, foi, "GW", "HB-CENCE-2024", "p.25", d_foi + "; A-O cell feeds the 2024 capacity factor formula (=lower / (cap x 8760 x 0.9 x 0.0036)), giving 0.4621")
plan(C, "PWRFOI", [foi] * 4, [0, 0, 0, 0], [0.227242, 0.214, 0.214, 0.214], [foi] * 4,
     [0.0074, 0.327, 1.845, 3.2008], [0.0074, 0.327, 1.845, ll_foi24], round(cf_foi, 4),
     "CENCE Informe Anual 2024 p.20 (bunker 836,959.433 MWh) and p.25 (227.661 MW plate): 0.4197, highest of 2021-2024",
     "explained by record",
     "No bunker plant added 2021-2024; the 76 MW 2024 build came from a 2024 lower limit that included PTA Garabito (diesel). After: cap = recorded capacity, model CF 2024 becomes 0.4621 by its formula, 0.227661 x 0.4621 x 31.536 = 3.318 PJ >= 2.9829 PJ.")

# PWRGEO: plate 258.84 (2021), 262.66 (2022-2024); rating changes only
geo = [0.25884, 0.26266, 0.26266, 0.26266]
d_geo = "Geothermal plate capacity 258,840 kW (2021) and 262,660 kW (2022-2024), CENCE capacity tables; no plant commissioned 2021-2024 (Pailas II rating updates only)"
for y, v in zip(range(2021, 2025), geo):
    ao(C, P, "PWRGEO", "ResidualCapacity", y, v, "GW", cr_cap_src, cr_cap_page, d_geo)
ao_carry(C, P, "PWRGEO", "ResidualCapacity", 2025, 2050, 0.229, 0.26266, "GW", cr_cap_src, cr_cap_page,
         d_geo + "; the end-2024 stock is held in later years where the row held the 2024 value")
b1(C, "PWRGEO", "TotalAnnualMaxCapacity", dict(zip(range(2021, 2025), geo)), "GW", cr_cap_src, cr_cap_page,
   d_geo + "; history years capped at the recorded capacity (before 0.455 to 0.516 GW); later years unchanged")
cf_geo = 1601729.159 / (258.84 * 8760)
plan(C, "PWRGEO", geo, [0, 0, 0, 0], [0.229] * 4, geo, [5.7341, 5.6929, 5.2323, 5.2229], [5.7341, 5.6929, 5.2323, 5.2229],
     round(cf_geo, 4), "CENCE Informe 2021 p.23 and p.29: 1,601,729.159 MWh / (258.84 MW x 8,760 h) = 0.7064, highest of 2021-2024",
     "explained by record", "Builds 61-64 MW removed: residual = plate capacity, cap = residual. Model CF x AF 0.9 with the plate capacity gives 6.52, 5.82, 5.33, 5.33 PJ >= lower limits.")

# PWRWNONS: plate 390.215 (2021-2022), 407.615 (2023), 402.335 (2024); Tilaran +17.4 Nov 2023; Tejona -5.28 2024
wnd_cap = [0.390215, 0.390215, 0.407615, 0.402335]
wnd_res = [0.390215, 0.390215, 0.390215, 0.384935]
d_w = "Wind plate capacity 390,215 kW (2021, 2022), 407,615 kW (2023, PE Tilaran 17,400 kW from 25 Nov 2023), 402,335 kW (2024, Tejona 8 units removed, -5,280 kW); residual = stock existing at end 2020 less retirements = 390.215, 390.215, 390.215, 384.935 MW"
ao(C, P, "PWRWNONS", "ResidualCapacity", 2021, 0.390215, "GW", cr_cap_src, cr_cap_page, d_w + "; 2022-2023 cells follow by formula")
ao(C, P, "PWRWNONS", "ResidualCapacity", 2024, 0.384935, "GW", "HB-CENCE-2024", "p.25 notes 13-14", d_w + "; later years follow by formula")
b1(C, "PWRWNONS", "TotalAnnualMaxCapacity", dict(zip(range(2021, 2025), wnd_cap)), "GW", cr_cap_src, cr_cap_page,
   d_w + "; history capped at recorded capacity (before 0.748 to 0.806 GW), which allows only the Tilaran 17.4 MW build in 2023")
cf_w = 1573299.593 / (390.215 * 8760)
plan(C, "PWRWNONS", wnd_cap, [0, 0, 0.0174, 0], [0.3761] * 4, wnd_res, [5.2012, 4.9012, 5.2014, 4.4487], [5.2012, 4.9012, 5.2014, 4.4487],
     round(cf_w, 4), "CENCE Informe 2021 p.23 and p.29: 1,573,299.593 MWh / (390.215 MW x 8,760 h) = 0.4603",
     "explained by record", "Cap allows at most the 17.4 MW Tilaran build in 2023; the build is not forced (no minimum investment row in use), the lower limits are met by the residual at model CF.")

# PWRSPVTRN: 5.4 MW (2021-2023), 15.487 MW (2024: Huacas 5.1 + Valle Escondido 4.987)
pv_cap = [0.0054, 0.0054, 0.0054, 0.015487]
d_pv = "Solar plate capacity 5,400 kW (Miravalles 1,000 + Juanilama 4,400) in 2021-2023 and 15,487 kW in 2024 (P.S. Huacas 5,100 kW from 22 Mar 2024 and Valle Escondido 4,987 kW from Aug 2024)"
b1(C, "PWRSPVTRN", "TotalAnnualMaxCapacity", dict(zip(range(2021, 2025), pv_cap)), "GW", cr_cap_src, cr_cap_page,
   d_pv + "; history capped at recorded capacity (before 0.0107 and 0.0311 GW): builds only the 10.087 MW of 2024")
ll_pv24 = round(25836.160 * 0.0036 / 1000 * 0.99, 6)
b1(C, "PWRSPVTRN", "TotalTechnologyAnnualActivityLowerLimit", {2024: ll_pv24}, "PJ", "HB-CENCE-2024", "p.20",
   f"2024 solar generation 25,836.160 MWh x 0.0036 / 1000 x 0.99 (the 0.99 band of the 2021-2023 formulas) = {ll_pv24} PJ; before 0.0927512 PJ (no band), which 15.487 MW at the model capacity factor 0.21025 x availability 0.9 cannot reach (0.0924 PJ)")
cf_pv = 9163.733 / (5.4 * 8760)
plan(C, "PWRSPVTRN", pv_cap, [0, 0, 0, 0.010087], [0.0054] * 4, [0.0054] * 4, [0.0328, 0.0307, 0.0318, 0.0928], [0.0328, 0.0307, 0.0318, ll_pv24],
     round(cf_pv, 4), "CENCE Informe 2021 p.23 and p.29: 9,163.733 MWh / (5.4 MW x 8,760 h) = 0.1937",
     "explained by record", "Residual already 5.4 MW plate. Build 2024 = 10.087 MW forced by the 2024 lower limit; cap stops the extra 2.9 MW.")

# PWRHYDROR: not written (no history capacity cap row in use; class split not printed)
plan(C, "PWRHYDROR", [2.330889, 2.330553, 2.37192, 2.35297], [0, 0, 0, 0], [1.23] * 4, [1.23] * 4,
     [20.742, 20.811, 16.07, 16.041], [20.742, 20.811, 16.07, 16.041], round(9285714.15 / (2330.889 * 8760), 4),
     "CENCE Informe 2021 p.23 and p.29, all hydro: 9,285,714.150 MWh / (2,330.889 MW x 8,760 h) = 0.4548",
     "not settled",
     "Recorded capacities are all hydro (CENCE prints no reservoir or run-of-river split). The 2023 'additions' (Platanar, Don Pedro, Volcan, 46.84 MW) are existing plants returning, so no build is recorded. The model's run-of-river residual 1.23 GW already exceeds PEG's 476.5 MW (Dec 2023) and covers the lower limit; the 105 MW BAU build is economic because A-O TotalAnnualMaxCapacity (Primary Techs row 166) is EMPTY and the B1 cap row 10 is not built in (unit PJ). Needs an active history cap row; no cell written.")

# ================================================================ DOMINICAN REPUBLIC
D = "DominicanRepublic"
# PPPVT: model 2020 cap 0.18746 (OC 2020 first published 187.46 MW) + commissioning (OC Tabla 2)
pvt_build = [0.150, 0.100, 0.2696, 0.2584]
base = 0.18746
pvt_cap = []
acc = base
for b in pvt_build:
    acc = round(acc + b, 5)
    pvt_cap.append(acc)
gen = {2020: 307.3355884562601, 2021: 489.37475675967437, 2022: 742.9994649021336, 2023: 1103.1165411453785, 2024: 1490.5264980181785}
d_pvt = ("Utility PV path = 2020 capacity of the row (0.18746 GW, OC-SENI 2020 as first published) + plants entered per OC Tabla 2: "
         "2021 Bayahonda 50 + Girasol 100; 2022 El Soco 50 + Santanasol 50; 2023 Esperanza 76 + Cumayasa 80 + Calabaza 50.6 + Matrisol 46 + Los Negros 17 = 269.6; "
         "2024 Maranatha 10 + Sajoma 68.4 + La Victoria 50 + Mirasol 100 + Monte Plata +30 = 258.4 MW (OC 2024 synthesis: 258.4 MW solar); "
         "OC 2024 Tabla 36 restates solar on inverter-net basis (305.48, 405.48, 675.08, 933.48 MW), whose yearly differences equal the same builds")
for y, v in zip(range(2021, 2025), pvt_cap):
    ao(D, P, "PPPVT", "TotalAnnualMaxCapacity", y, v, "GW", "HB-OC-2021|HB-OC-2022|HB-OC-2023|HB-OC-2024",
       "OC21 p.31; OC22 p.37; OC23 p.37-38; OC24 p.38, p.41 Tabla 2, p.127 Tabla 36", d_pvt + ("; 2025 on follow the 2024 cell by formula" if y == 2024 else ""))
cf_new = {}
for y, v in zip(range(2021, 2025), pvt_cap):
    cf_new[y] = round(gen[y] / (v * 1000 * 8.76), 5)
    ao(D, P, "PPPVT", "CapacityFactor", y, cf_new[y], "fraction", "FR2-D3-CNEGEN", "sheet Hoja1 row 10 (Sol)",
       f"CNE SENI solar generation {y} {gen[y]:.3f} GWh / ({v} GW x 8,760 h) = {cf_new[y]}; the row's lower-limit formula (cap x CF x 8760 x 0.0036 x 0.999) needs CF on the same capacity basis" + ("; 2025 on follow by formula" if y == 2024 else ""))
ll_pvt = [1.7146, 2.5825, 3.909, round(pvt_cap[3] * cf_new[2024] * 8760 * 0.0036 * 0.999, 4)]
cf_pvt_pub = gen[2020] / (155.48 * 8.76)
plan(D, "PPPVT", [0.30548, 0.40548, 0.67508, 0.93348], pvt_build, [0.08796] * 4, [0.08796] * 4,
     [1.7146, 2.5825, 3.909, 3.9848], ll_pvt, round(cf_pvt_pub, 4),
     "CNE GeneracionFuenteSENI 2020 solar 307.34 GWh / OC 2024 Tabla 36 solar 155.48 MW (x 8,760 h) = 0.2257, highest of 2020-2024",
     "explained by record",
     "Recorded capacity column = OC Tabla 36 (inverter-net). Model path keeps its 2020 value (187.46 MW, first-published basis) and adds the dated commissioning, so 2024 is 965.46 MW (3.4 percent above Tabla 36). Lower 2024 becomes cap x CF formula = recorded 1,490.53 GWh x 0.999. 2025 on: cap and lower carry the 2024 values by formula (BAU capacity after 2024 rises from 0.675 to 0.965 GW).")

# PPPVD: CNE net metering cumulative MW
pvd_cap = [0.2197, 0.28588, 0.34698, 0.42432]
d_pvd = "Net metering cumulative capacity at year end, CNE Memoria Institucional 2024 table Periodo/Acumulativos: 219.70 (2021), 285.88 (2022), 346.98 (2023), 424.32 MW (2024); 2018-2021 cells already equal this series"
for y, v in zip((2022, 2023, 2024), pvd_cap[1:]):
    ao(D, P, "PPPVD", "TotalAnnualMaxCapacity", y, v, "GW", "HB-CNE-MEM2024", "p.30 (printed 26)", d_pvd + ("; 2025 on follow the 2024 cell by formula" if y == 2024 else ""))
ll_pvd24 = round(0.42432 * 0.215 * 8760 * 0.0036 * 0.999, 4)
plan(D, "PPPVD", pvd_cap, [0.04264, 0.06618, 0.0611, 0.07734], [0.09302] * 4, [0.09302] * 4,
     [1.4598, 1.8747, 2.1263, 2.1675], [1.4598, 1.8747, 2.1263, ll_pvd24], round(cf_pvt_pub, 4),
     "no published capacity factor of net-metering PV; SENI utility PV 0.2257 (CNE 2020 generation / OC Tabla 36 capacity) used",
     "explained by record",
     "Builds now equal the CNE cumulative differences (CNE prints 138.44 MW 'added' in 2024 against a cumulative difference of 77.34 MW; the cumulative series is used). Lower 2024 follows the row formula (cap x 0.215 flat CF) and rises with the cap; 2025 on carry it.")

# PPICEFOI: B1 BAU cap row (Security_Multiplier 1.05) 9999 -> recorded stock + builds
ice = {2021: 0.61259, 2022: 0.49555, 2023: 0.49555, 2024: round(0.49555 + 0.18866 + 0.03626, 5)}
b1(D, "PPICEFOI", "TotalAnnualMaxCapacity", ice, "GW", "HB-OC-2023|HB-OC-2024", "OC23 p.37-38 Tabla 2; OC24 p.38, p.41 Tabla 2",
   "History cap = the row's own residual (0.61259, 0.49555, 0.49555 GW, the A-O path after the CEPP retirement of 2022) plus fuel-oil engines entered: "
   "Karpowership Azua KPS 26 + KPS 60 108.78 + 79.88 = 188.66 MW (commercial operation 20 Jan 2024) and Pimentel 4 36.26 MW (23 May 2024); "
   "each value divided by the row's Security_Multiplier 1.05 so the compiled cap equals the recorded value; years after 2024 unchanged (9999)", divide=1.05)
plan(D, "PPICEFOI", [round(v, 5) for v in ice.values()], [0, 0, 0, 0.22492], [0.61259, 0.49555, 0.49555, 0.49555], [0.61259, 0.49555, 0.49555, 0.49555],
     [9.652, 12.135, 9.1011, 0.0], [9.652, 12.135, 9.1011, 0.0], round(2987.208 / (1416.96 * 8.76), 4),
     "CNE GeneracionFuenteSENI fuel oil 2024 2,987.21 GWh / OC Tabla 36 ICE 1,416.96 MW: 0.2407 (fuel oil also burns in steam units, so an upper bound for engines is not printed)",
     "explained by record",
     "Cap allows exactly the 224.92 MW of 2024; the build is not forced because the 2024 lower limit is 0 (A-O Secondary Techs row 118 holds 0 from 2024). Sultana del Este derate (-17.4 MW, Oct 2023) is not taken: the 2023 lower limit 9.1011 PJ needs 0.4955 GW at CF 0.59426.")

# PPICEGASFOI: no dual-fuel engine added 2021-2024
for y in (2021, 2022, 2023):
    ao(D, S, "PPICEGASFOI", "TotalAnnualMaxCapacity", y, 0.6732, "GW", "HB-OC-2021|HB-OC-2022|HB-OC-2023|HB-OC-2024",
       "Tabla 2 of each memoria (OC21 p.31; OC22 p.37; OC23 p.37-38; OC24 p.41)",
       "No dual-fuel engine entered the SENI 2021-2024 (OC Tabla 2 lists): path held at the row's 2020 value 0.6732 GW; 2024 on follow by formula" )
plan(D, "PPICEGASFOI", [0.6732] * 4, [0, 0, 0, 0], [0.17195] * 4, [0.17195] * 4, [9.2678, 14.278, 12.373, 10.613], [9.2678, 14.278, 12.373, 10.605],
     "", "no type-specific factor printed; model CF 0.445-0.686 with 0.6732 GW covers every lower limit", "explained by record",
     "Builds 2021-2022 of 0.5 MW removed. Lower 2024 formula moves from 10.613 to 10.605 PJ with the cap.")

# PPHDAM: +7.56 MW dated 2019 -> residual from 2019; cap 2023-2025 back to 0.62328
d_h = "SENI hydro 615.72 MW (2018) and 623.28 MW from 2019 to 2024 (OC 2024 Tabla 36); the last addition (+7.56 MW) is dated 2019, so it is residual (existing) capacity in 2021-2024, not a build"
add(D, AO, P, "PPHDAM", "ResidualCapacity", "Projection.Mode", ao_cell(D, P, "PPHDAM", "ResidualCapacity", "Projection.Mode")[0], "User defined", "", "HB-OC-2024", "p.127 Tabla 36", d_h + "; mode changed so the year cells are read")
for y in range(2019, 2051):
    ao(D, P, "PPHDAM", "ResidualCapacity", y, 0.62328, "GW", "HB-OC-2024", "p.127 Tabla 36", d_h)
for y in (2023, 2024, 2025):
    ao(D, P, "PPHDAM", "TotalAnnualMaxCapacity", y, 0.62328, "GW", "HB-OC-2024", "p.127 Tabla 36", d_h + "; cap must not fall below the residual (0.62326 before)" + ("; 2026 on follow by formula" if y == 2025 else ""))
plan(D, "PPHDAM", [0.62328] * 4, [0, 0, 0, 0], [0.61572] * 4, [0.62328] * 4, [5.3802, 5.24, 4.1574, 4.1574], [5.3802, 5.24, 4.1574, 4.1574],
     round(1772.82 / (615.72 * 8.76), 4), "CNE GeneracionFuenteSENI hydro 2018 1,772.82 GWh / OC Tabla 36 615.72 MW = 0.3287, highest of 2018-2024",
     "explained by record", "The 7.56 MW (2019) becomes residual from 2019; model 2018 residual 0.61572 kept in the 2018 cell. Lower limits are cap x CF formulas and change by less than 0.0001 PJ.")

# DR no-record cases (plan only)
for t, rb, ll, note in [
    ("PPAFOI", 0.27036, [3.0951, 4.1003, 4.1003, 4.1003], "Self-producer fuel oil: no per-fuel self-producer capacity is printed (PEN 2022 Tabla 70 by user type for 2018; UN self-producer combustible capacity 705-1,255 MW in aggregate). Residual 0.27036 GW at the row CF 0.39838 gives 3.40 PJ against the 4.10 PJ lower limit from 2022, which forces the build."),
    ("PPANGS", 0.019353, [1.3209, 2.2084, 2.2084, 2.2084], "Self-producer natural gas: no capacity record. UN fuel input to autoproducer plants is 519-771 TJ of natural gas (2019-2023), which at any engine efficiency gives at most about 0.3 PJ of electricity against a lower limit of 2.21 PJ; the history generation itself looks too high, but no per-fuel self-producer generation record exists to replace it."),
    ("PPDGSL", 0.017719, [0.057, 0.0579, 0.0626, 0.0626], "Self-producer gasoline: no capacity record; UN gasoline input 5-14 thousand t a year. Build 3 MW over 2021-2023 is below the 5 percent / 2 MW scale of other cases."),
]:
    plan(D, t, None, None, [rb] * 4, [rb] * 4, ll, ll, "", "", "no record", note)

# ================================================================ ECUADOR
E = "Ecuador"
arc_ent = "HB-ARCONEL-2021|HB-ARCONEL-2022|HB-ARCONEL-2023|HB-ARCONEL-2024"
# PPHRORPM: Toachi-Pilaton complex: Sarapullo 48.45 (2022), Alluriquin 204 (2024)
d_pm = ("Toachi-Pilaton complex (Pacific slope run-of-river, 253 MW): Sarapullo 48.45 MW entered Feb 2022 (ARCONEL 2022 Tabla 27; experimental 2022, commercial 1 Mar 2023) "
        "and Alluriquin 204.00 MW counted in end-2024 capacity (ARCONEL 2024 Tabla 27 p.44, experimental Dec 2024)")
ao(E, P, "PPHRORPM", "TotalAnnualMinCapacityInvestment", 2022, 0.04845, "GW", "HB-ARCONEL-2022|HB-ARCONEL-2023", "E2022 Tabla 27 p.45; E2023 Tabla 27 p.44", d_pm + "; before 0.27 GW (no record of a 270 MW plant in 2022)")
ao(E, P, "PPHRORPM", "TotalAnnualMinCapacityInvestment", 2024, 0.204, "GW", "HB-ARCONEL-2024", "Tabla 27 p.44, Nota 1", d_pm)
add(E, AO, P, "PPHRORPM", "TotalAnnualMaxCapacity", "Projection.Mode", ao_cell(E, P, "PPHRORPM", "TotalAnnualMaxCapacity", "Projection.Mode")[0], "User defined", "", arc_ent, "E2022 p.45; E2024 p.44", d_pm + "; row activated so history capacity is capped (years after 2024 keep 9999)")
pm_cap = [0.288, 0.33645, 0.33645, 0.54045]
for y, v in zip(range(2021, 2025), pm_cap):
    ao(E, P, "PPHRORPM", "TotalAnnualMaxCapacity", y, v, "GW", arc_ent, "E2022 p.45; E2024 p.44", d_pm + "; cap = residual 0.288 GW + recorded builds")
plan(E, "PPHRORPM", pm_cap, [0, 0.04845, 0, 0.204], [0.288] * 4, [0.288] * 4, [6.0364] * 4, [6.0364] * 4,
     round(25574.61 / (5106.85 * 8.76), 4), "ARCONEL 2021 Tabla 4 p.27, all hydro: 25,574.61 GWh / (5,106.85 MW x 8,760 h) = 0.5717",
     "explained by record", "Basin and dam/run-of-river class are not printed; Toachi-Pilaton is taken as one medium Pacific run-of-river project (Sarapullo alone is 48.45 MW). Residual 0.288 kept (class totals not printed). Model CF x AF covers 6.04 PJ in every year with the capped capacity (6.05, 6.25, 7.07, 11.36 PJ).")

# PPHRORAS: Sabanilla 36 (2022), Abanico +15.38, Huayquichuma 6.5, Mira 0.99 (2024)
d_as = "Small Amazon run-of-river: Sabanilla 36.00 MW (Oct 2022, ARCONEL 2022 Tabla 27); 2024: Abanico +15.38 MW (May), Huayquichuma 6.50 MW (Jan), Mira 0.99 MW (Apr) (ARCONEL 2024 Tabla 27 p.44) = 22.87 MW"
ao(E, P, "PPHRORAS", "TotalAnnualMinCapacityInvestment", 2022, 0.036, "GW", "HB-ARCONEL-2022", "Tabla 27 p.45", d_as + "; before 0.18 GW")
ao(E, P, "PPHRORAS", "TotalAnnualMinCapacityInvestment", 2024, 0.02287, "GW", "HB-ARCONEL-2024", "Tabla 27 p.44", d_as)
add(E, AO, P, "PPHRORAS", "TotalAnnualMaxCapacity", "Projection.Mode", ao_cell(E, P, "PPHRORAS", "TotalAnnualMaxCapacity", "Projection.Mode")[0], "User defined", "", arc_ent, "E2022 p.45; E2024 p.44", d_as + "; row activated so history capacity is capped (years after 2024 keep 9999)")
as_cap = [0.062, 0.098, 0.098, 0.12087]
for y, v in zip(range(2021, 2025), as_cap):
    ao(E, P, "PPHRORAS", "TotalAnnualMaxCapacity", y, v, "GW", arc_ent, "E2022 p.45; E2024 p.44", d_as + "; cap = residual 0.062 GW + recorded builds")
plan(E, "PPHRORAS", as_cap, [0, 0.036, 0, 0.02287], [0.062] * 4, [0.062] * 4, [1.6534] * 4, [1.6534] * 4,
     round(25574.61 / (5106.85 * 8.76), 4), "ARCONEL 2021 Tabla 4 p.27, all hydro: 0.5717",
     "explained by record", "Basin and class not printed; plant list as in the earlier mapping. 2021 is tight: 0.062 x 0.89075 x 0.95 x 31.536 = 1.6545 PJ >= 1.6534 PJ. The lower limit 1.6534 PJ is above 0.062 GW x 31.536 x 0.5717 (1.118 PJ, all-hydro CF) but run-of-river small plants reach higher factors; not corrected (no class generation printed).")

# PPHDAMPS: Chalpi 8.10 (2021), Ulba 1.00 (2023)
d_ps = "Small hydro: Chalpi 8.10 MW (Apr 2021, ARCONEL 2021 Tabla 27 p.54; CENACE 12 Apr 2021) and Ulba 1.00 MW (Apr 2023, ARCONEL 2023 Tabla 27 p.44)"
for y, v in zip(range(2021, 2025), [0.0081, 0.0, 0.001, 0.0]):
    ao(E, P, "PPHDAMPS", "TotalAnnualMinCapacityInvestment", y, v, "GW", "HB-ARCONEL-2021|HB-ARCONEL-2023", "E2021 p.54; E2023 p.44", d_ps + "; before 0.016333 GW a year 2022-2024 (no record)")
add(E, AO, P, "PPHDAMPS", "TotalAnnualMaxCapacity", "Projection.Mode", ao_cell(E, P, "PPHDAMPS", "TotalAnnualMaxCapacity", "Projection.Mode")[0], "User defined", "", "HB-ARCONEL-2021|HB-ARCONEL-2023", "E2021 p.54; E2023 p.44", d_ps + "; row activated (years after 2024 keep 9999)")
ps_cap = [0.0503, 0.0503, 0.0513, 0.0513]
for y, v in zip(range(2021, 2025), ps_cap):
    ao(E, P, "PPHDAMPS", "TotalAnnualMaxCapacity", y, v, "GW", "HB-ARCONEL-2021|HB-ARCONEL-2023", "E2021 p.54; E2023 p.44", d_ps + "; cap = residual 0.0422 GW + recorded builds")
plan(E, "PPHDAMPS", ps_cap, [0.0081, 0, 0.001, 0], [0.0422] * 4, [0.0422] * 4, [0.5305] * 4, [0.5305] * 4,
     round(25574.61 / (5106.85 * 8.76), 4), "ARCONEL 2021 Tabla 4 p.27, all hydro: 0.5717", "explained by record",
     "Dam or run-of-river not printed for Chalpi and Ulba; kept in this class as in the earlier mapping.")

# PPPVD: SGDA distributed generation 2.35 (2020) -> 54.78 MW (2024)
sg = {2020: 2.35, 2021: 5.90, 2022: 20.22, 2023: 38.38, 2024: 54.78}
d_sg = "Distributed self-supply systems (SGDA) cumulative nominal MW: 2.35 (2020), 5.90, 20.22, 38.38, 54.78 (2021-2024), ARCONEL 2024 Tabla 108 p.108; builds = yearly differences"
pvd_b = [round((sg[y] - sg[y - 1]) / 1000, 5) for y in range(2021, 2025)]
for y, v in zip(range(2021, 2025), pvd_b):
    ao(E, P, "PPPVD", "TotalAnnualMinCapacityInvestment", y, v, "GW", "HB-ARCONEL-2024", "Tabla 108 p.108", d_sg)
add(E, AO, P, "PPPVD", "TotalAnnualMaxCapacity", "Projection.Mode", ao_cell(E, P, "PPPVD", "TotalAnnualMaxCapacity", "Projection.Mode")[0], "User defined", "", "HB-ARCONEL-2024", "Tabla 108 p.108", d_sg + "; row activated (years after 2024 keep 9999)")
ecu_pvd_cap = []
acc = 0.026
for v in pvd_b:
    acc = round(acc + v, 5)
    ecu_pvd_cap.append(acc)
for y, v in zip(range(2021, 2025), ecu_pvd_cap):
    ao(E, P, "PPPVD", "TotalAnnualMaxCapacity", y, v, "GW", "HB-ARCONEL-2024", "Tabla 108 p.108", d_sg + "; cap = residual 0.026 GW + cumulative SGDA additions")
plan(E, "PPPVD", ecu_pvd_cap, pvd_b, [0.026] * 4, [0.026] * 4, [0.0123] * 4, [0.0123] * 4,
     round(36.87 / (27.65 * 8.76), 4), "ARCONEL 2021 Tabla 4 p.27, PV: 36.87 GWh / (27.65 MW x 8,760 h) = 0.1522",
     "explained by record", "The 115 MW 2021 build was economic (no cap). Residual 0.026 GW is the model's PV-in-plants stock (national PV 27.65 MW in 2021); SGDA systems are taken as distributed PV.")

# PPNGS: residual jump 2023 (0.27536 -> 0.52428) has no record
d_ng = "No gas plant entered operation 2021-2024 (ARCONEL Tabla 27 of 2021-2024); Termogas Machala I and II 138.56 + 136.80 = 275.36 MW nominal (ARCONEL 2020 Annex A.1 p.212; ARCONEL 2024 Tabla 36 p.50, El Oro 275.36 MW)"
for y in (2023, 2024):
    ao(E, S, "PPNGS", "ResidualCapacity", y, 0.27536, "GW", "HB-ARCONEL-2024", "Tabla 27 p.44; Tabla 36 p.50", d_ng + "; years after 2024 unchanged (0.52428)")
plan(E, "PPNGS", [0.27536] * 4, [0, 0, 0, 0], [0.27536, 0.27536, 0.52428, 0.52428], [0.27536] * 4, [2.0845, 1.9665, 1.9665, 1.9665], [2.0845, 1.9665, 1.9665, 1.9665],
     round(1021.54 / (943.85 * 8.76), 4), "ARCONEL 2022 Tabla 4 p.21, Turbogas: 1,021.54 GWh / (943.85 MW x 8,760 h) = 0.1235; Machala-only factor not printed",
     "not settled", "Residual 2023-2024 set to Machala 275.36 MW. The 117 MW 2021 build is economic: lower 2.08 PJ is met by 0.275 GW at CF 0.2527; Secondary Techs row 76 (TotalAnnualMaxCapacity) is empty in every year, so no cap could be activated without writing 30 years. Max producible at 0.1235 is 1.07 PJ < 2.08 PJ, but turbogas includes diesel turbines; Machala ran near 0.6 in other years, not printed here.")

# PPWNDON: Huascachaca 32.00 (Dec 2022) + 17.98 (Mar 2023); CF 0.1488 flat forces a 2021 build
d_wd = "Minas de Huascachaca wind: 32.00 MW nominal at end 2022 (first group Dec 2022) and +17.98 MW to 49.98 MW in Mar 2023 (ARCONEL 2022 Tabla 27 p.45; ARCONEL 2023 Tabla 27 p.44; commercial operation 31 Mar 2023)"
ao(E, P, "PPWNDON", "TotalAnnualMinCapacityInvestment", 2022, 0.032, "GW", "HB-ARCONEL-2022", "Tabla 27 p.45", d_wd)
ao(E, P, "PPWNDON", "TotalAnnualMinCapacityInvestment", 2023, 0.01798, "GW", "HB-ARCONEL-2023", "Tabla 27 p.44", d_wd)
plan(E, "PPWNDON", [0.0165, 0.0485, 0.06648, 0.06648], [0, 0.032, 0.01798, 0], [0.0165] * 4, [0.0165] * 4, [0.2162] * 4, [0.2162] * 4,
     round(79.98 / (16.5 * 8.76), 4), "ARCONEL 2019 Tabla 80 p.129, SNI wind (Villonaco 16.5 MW): 79.98 GWh / (16.5 MW x 8,760 h) = 0.5533",
     "not settled", "Residual 0.0165 GW = Villonaco and the lower limit 0.2162 PJ = SNI wind 2021 (60.06 GWh) are both recorded and producible (max 0.288 PJ). The model CF 0.1488 (Flat, every year) x AF 0.95 gives 0.074 PJ, so the model still adds about 32 MW in 2021. Recorded CF 2021 is 0.4155 (60.06 GWh / 16.5 MW); changing the Flat CF row changes every future year, so it was not written. Huascachaca builds are now dated.")

# Ecuador not settled / no record (plan only)
plan(E, "PPRDSL", None, [0.0484, 0, 0, 0], [0.23452] * 4, [0.23452] * 4, [7.4855, 7.5118, 7.5118, 7.5118], [7.4855, 7.5118, 7.5118, 7.5118],
     round(7156.96 / (2163.60 * 8.76), 4), "ARCONEL 2024 Tabla 30 p.46 and Tabla 4 p.21, all engines (MCI): 7,156.96 GWh / (2,163.60 MW x 8,760 h) = 0.3776",
     "not settled", "Engine capacity is printed only in total (MCI 2,020.67 MW in 2021; 1,264.47 MW non-incorporated in 2024), not by fuel. 7.49 PJ at 0.3776 needs 0.629 GW of diesel engines; the residual 0.2345 GW cannot be checked against a diesel-only record. Cuyabeno Crudo Diesel 25.60 MW and Shushufindi Gas 22.80 MW (2021) are the only dated additions.")
plan(E, "PPPVT", [0.0, 0.001, 0.001, 0.001], [0, 0.001, 0, 0], [0.000018, 0, 0, 0], [0.000018, 0, 0, 0], [0.0245] * 4, [0.0245] * 4,
     round(36.87 / (27.65 * 8.76), 4), "ARCONEL 2021 Tabla 4 p.27, PV: 0.1522", "not settled",
     "The model puts the 26 MW of PV in plants under PPPVD and none under PPPVT, but gives PPPVT a lower limit of 0.0245 PJ (6.8 GWh), which forces a 5 MW build in 2021. Recorded: San Cristobal Solar 1.00 MW (Jan 2022, Galapagos). Settling it needs a split of the 27.65 MW between the two classes; no cell written.")
for t, rb, ll, note in [
    ("PPCRU", 0.24244, [4.0613, 4.0872, 4.0872, 4.0872], "Crude-fired engines: capacity by fuel not printed. Cuyabeno Crudo Diesel 25.60 MW (2021, isolated) may be crude-fired; build 11 MW in 2021."),
    ("PPHRORAM", 0.487, [7.1009] * 4, "Medium Amazon run-of-river: no plant of 50-450 MW entered 2021-2024 on the Amazon slope (Alluriquin is Pacific); build 17 MW 2021 is economic (cap row EMPTY). A zero-build cap was not written because the class residual cannot be checked."),
    ("PPIHD", 0.24089, [6.4614, 6.1605, 6.1605, 6.1605], "Isolated hydro: no addition recorded; build 9-12 MW in 2021."),
    ("PPWNDD", 0.0, [0.007, 0.0097, 0.0, 0.0], "Distributed wind (Galapagos San Cristobal 2.4 MW and Baltra 2.25 MW, national wind 21.15 MW less Villonaco 16.5): residual 0 although the plants exist since before 2021; build 2.3 MW in 2021-2022 below the 2 MW scale per year."),
]:
    plan(E, t, None, None, [rb] * 4, [rb] * 4, ll, ll, "", "", "no record", note)

# ================================================================ JAMAICA
J = "Jamaica"
d_dsl = ("No JPS unit retired 2021-2024: the 171.5 MW of units due in 2023 (Rockfort 1 and 2, GT5, GT10, GT3, GT6, GT7, GT9) were moved to 2026 "
         "(2022 IRP Table 5-2 p.40); the MCR tables list the same diesel (ADO) gas turbines in 2021-2023 (131.5 MW) and the OUR 2024-2025 report lists no 2024 retirement; "
         "residual kept at the row's 2021 value 0.1405 GW")
ao(J, S, "PPDSL", "ResidualCapacity", 2023, 0.1405, "GW", "HB-IRP2022|HB-OUR-DET2023", "IRP p.40 Table 5-2; determination p.95 Table 7.12", d_dsl + "; before =0.1405-0.0685-0.017")
ao(J, S, "PPDSL", "ResidualCapacity", 2024, 0.1405, "GW", "HB-IRP2022|HB-OUR-AR2425", "IRP p.40 Table 5-2; OUR 2024-2025 p.48", d_dsl + "; years after 2024 unchanged (0)")
cf_ado = 285.59 / (131.5 * 8.76)
plan(J, "PPDSL", [0.1315] * 4, [0, 0, 0, 0], [0.1405, 0.1405, 0.055, 0.0], [0.1405] * 4, [0.576, 0.5754, 0.2255, 0.0348], [0.576, 0.5754, 0.2255, 0.0348],
     round(cf_ado, 4), "OUR Annual Report 2024-2025 Table 21 p.54, ADO 2022 285.59 GWh / 131.5 MW ADO turbines (OUR determination Table 7.12) x 8,760 h = 0.2479",
     "explained by record", "The 8.5 MW build of 2024 came from a retirement schedule (85.5 MW in 2023, 46.5 MW in 2024) that IRP-2 moved to 2026. Recorded ADO capacity is 131.5 MW against the model's 140.5 MW (difference kept: no dated change). Lower limits are cap x CF formulas of the 2021 residual and do not change.")

d_hy = ("JPS hydro generation, OUR Annual Report 2024-2025 Table 23 p.57: 137,687.56 (2021), 118,929.86 (2022), 110,280.43 (2023), 122,470.31 MWh (2024); "
        "x 0.0036 / 1000 x 0.999 (the row's band)")
hy_gen = {2021: 137687.56, 2022: 118929.86, 2023: 110280.43, 2024: 122470.31}
hy_ll = {y: round(g * 0.0036 / 1000 * 0.999, 6) for y, g in hy_gen.items()}
cf_hy = 137687.56 / (28.66 * 8760)
mp = 0.02866 * K * cf_hy
add(J, AO, P, "PPHDAM", "TotalTechnologyAnnualActivityLowerLimit", "Projection.Mode", ao_cell(J, P, "PPHDAM", "TotalTechnologyAnnualActivityLowerLimit", "Projection.Mode")[0], "User defined", "", "HB-OUR-AR2425", "p.57 Table 23",
    f"The Flat lower limit 0.49786 PJ (residual x 2021 CF) exceeds what 28.66 MW can produce at the highest published hydro factor {cf_hy:.4f} (2021: 137,687.56 MWh / (28.66 MW x 8,760 h)), {mp:.4f} PJ; mode changed to read yearly values")
for y in range(2021, 2051):
    v = hy_ll[min(y, 2024)]
    ao(J, P, "PPHDAM", "TotalTechnologyAnnualActivityLowerLimit", y, v, "PJ", "HB-OUR-AR2425", "p.57 Table 23 (image page)",
       d_hy + (f" = {v} PJ" if y <= 2024 else f"; after 2024 the 2024 value {v} PJ is held"))
plan(J, "PPHDAM", [0.02866] * 4, [0, 0, 0, 0], [0.0291] * 4, [0.0291] * 4, [0.4979] * 4, [hy_ll[y] for y in range(2021, 2025)],
     round(cf_hy, 4), "OUR Annual Report 2024-2025 Table 23 p.57: 137,687.56 MWh / (28.66 MW x 8,760 h) = 0.5484, highest of 2021-2024",
     "explained by record", "History generation corrected to the regulator's plant record. With the model CF 0.46855 (2022 on), 0.0291 GW gives 0.430 PJ, so a build of about 0.7 MW remains in 2024 (0.4405 PJ), below the 2 MW scale. Later years hold the 2024 record (before 0.4979).")

plan(J, "PPNGS", [0.438] * 4, [0.010, 0, 0, 0], [0.688] * 4, [0.688] * 4, [9.0, 9.0, 9.1566, 9.38], [9.0, 9.0, 9.1566, 9.38],
     round(2810.86 / (438 * 8.76), 4), "OUR Annual Report 2024-2025 Table 21 p.54, NG 2023 2,810.86 GWh / 438 MW NG and NG/ADO (OUR determination Table 7.12) x 8,760 h = 0.7326",
     "not settled", "Recorded natural-gas capacity is 438 MW (NG 150 incl. Hill Run 10 MW of Dec 2021, NG/ADO 288), the model residual 0.688 GW. The lower limits are producible by 438 MW at 0.7326 (10.12 PJ), so no history generation correction is due. The 16.8 MW build of 2024 comes from the Flat CF 0.42202: 0.688 x 0.42202 x 31.536 = 9.157 PJ < 9.38 PJ. Setting the residual to 438 MW needs a CF of at least 0.68, and the CF row is Flat (every year); no cell written.")

# 15 matched or below-scale cases: plan rows only
hb = list(csv.DictReader(open(r"C:\clw_align\_LAC_HUB\fix_run2_20261120T225823Z\history_builds.csv", encoding="utf-8")))
done = {(p["country"], p["tech"]) for p in PLAN}
for c in hb:
    if (c["country"], c["tech"]) in done:
        continue
    st = "matched"
    plan(c["country"], c["tech"], None, None, None, None, None, None, "", "", st,
         f"Not changed: earlier status '{c['status_after']}' ({c['plants_and_dates'] or c['cause']})")

# ---------------------------------------------------------------- write
reg_cols = ["model", "file", "sheet", "tech", "parameter", "year", "before", "after", "unit", "source_id", "page", "derivation", "assumption_sentence", "range_low", "range_high"]
for r in ROWS:
    sids = r["source_id"].split("|") if r["source_id"] else []
    titles = "; ".join(f"{s}: {SRC[s]}" for s in sids if s in SRC)
    if titles:
        r["derivation"] = r["derivation"] + ". Sources: " + titles
with open(os.path.join(WORK, "register_history.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=reg_cols)
    w.writeheader()
    for r in ROWS:
        w.writerow(r)
order = {(c["country"], c["tech"]): i for i, c in enumerate(hb)}
PLAN.sort(key=lambda d: order.get((d["country"], d["tech"]), 999))
with open(os.path.join(WORK, "history_plan.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(PLAN[0].keys()))
    w.writeheader()
    for d in PLAN:
        w.writerow(d)
from collections import Counter
cnt = Counter((r["model"], r["tech"].replace("BAU|", ""), r["parameter"]) for r in ROWS)
for k, v in sorted(cnt.items()):
    print(k, v)
print("cells", len(ROWS), "plan rows", len(PLAN), Counter(d["status_expected"] for d in PLAN))
