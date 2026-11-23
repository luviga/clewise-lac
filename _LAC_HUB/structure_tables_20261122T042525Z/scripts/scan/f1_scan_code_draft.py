"""Step F: list every value and element name written in code outside _LAC_HUB/.

Reads the repository at the job's checkout (files identical to main) and the model sets
from tracked B1_Output_Params CSVs. Writes:
  script_constants.csv          values of the system written in code
  script_constants_accepted.csv constants of the mathematics or presentation, with the reason
  parts/scenario_names_code.csv every scenario name found in code (for scenario_names.csv)
Usage: python -I f1_scan_code.py <repo root>
"""
import ast
import csv
import glob
import os
import re
import subprocess
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import JOB, write_csv

REPO = sys.argv[1]

# ---------------- vocabulary ----------------
SCENARIOS = ["BAU", "NDCNEW", "LTSNEW", "NDCcond", "NDCincond", "NDP", "NDPAMB", "NDCINC", "LTSOPT",
             "Default", "NDC", "LTS", "NDCCOND", "NDCINCOND", "NDC_cond", "NDC_incond", "NDPAMB2"]
COUNTRIES = ["CostaRica", "Costa Rica", "DominicanRepublic", "Dominican Republic", "Republica Dominicana",
             "Ecuador", "Guatemala", "Honduras", "Jamaica"]
CCODES = ["CR", "RD", "DR", "ECU", "GUA", "GTM", "HON", "HND", "JAM", "CRI", "DOM"]
PIPE_FILES_ROOT = {"stage0_run.py", "stage0_recommend_shares.py", "stage0_collect_outputs.py", "stage0_capacity_check.py",
                   "stage1_share_analyzer_v16.py", "stage2_apply_v2.py", "stage3_apply.py", "stage3_results.py",
                   "stage0_run_all.bat", "stage0_run_all.sh", "stage3_run_all.bat", "stage2_post_clean.py",
                   "stage0_clean.py", "stage1_clean.py", "ao_safe_save.py"}
PIPE_MODEL = {
    "CostaRica/CR_ENERGY/t1_confection": ["A2_Compiler_CostaRica.py", "B1_Base_Scenarios_Adj_Parallel_CostaRica.py", "setup_utils.py", "OSeMOSYS_Model.txt"],
    "DominicanRepublic/RD_ENERGY": ["A2_Compiler_DominicanRepublic.py", "B1_Base_Scenarios_Adj_Parallel_DominicanRepublic.py", "setup_utils.py", "OSeMOSYS_Model.txt"],
    "Ecuador/ECU_Energy": ["A2_Compiler_Ecuador.py", "B1_Base_Scenarios_Adj_Parallel.py", "OSeMOSYS_Model.txt"],
    "Guatemala/GUA_ENERGY": ["A2_Compiler_Guatemala.py", "B1_Base_Scenarios_Adj_Parallel_Guatemala.py", "OSeMOSYS_Model.txt"],
    "Honduras/HON_ENERGY": ["A2_Compiler_Honduras.py", "B1_Base_Scenarios_Adj_Parallel_Honduras.py", "OSeMOSYS_Model.txt"],
    "Jamaica/JAM_ENERGY": ["A2_Compiler_Jamaica.py", "B1_Base_Scenarios_Adj_Parallel_Jamaica.py", "OSeMOSYS_Model.txt"],
}
UNIT_CONV = {1000: "kilo prefix (SI)", 1e3: "kilo prefix (SI)", 1e6: "mega prefix (SI)", 1e9: "giga prefix (SI)",
             1e-3: "milli or kilo prefix (SI)", 0.001: "kilo prefix (SI)", 1e-6: "mega prefix (SI)", 1e12: "tera prefix (SI)",
             3.6: "1 kWh = 3.6 MJ (SI); 1 TWh = 3.6 PJ", 0.0036: "1 GWh = 0.0036 PJ (SI)", 277.777: "1 PJ = 277.78 GWh (SI)",
             277.78: "1 PJ = 277.78 GWh (SI)", 8760: "hours in a non-leap year", 8.76: "8760 h / 1000 (GW to PJ conversion with 3.6)",
             31.536: "GW-year to PJ: 8760 h x 3.6 PJ/TWh / 1000", 3600: "seconds per hour", 365: "days per year", 24: "hours per day",
             100: "percent to fraction"}


def git_files():
    out = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
    return [f for f in out if not f.startswith("_LAC_HUB/")]


def load_sets(files):
    tech, fuel, emis = set(), set(), set()
    for f in files:
        if "/B1_Output_Params/" not in f or not f.endswith(".csv"):
            continue
        if not re.search(r"/(InputActivityRatio|OutputActivityRatio|EmissionActivityRatio)\.csv$", f):
            continue
        try:
            with open(os.path.join(REPO, f), encoding="utf-8", errors="replace", newline="") as fh:
                rd = csv.DictReader(fh)
                for r in rd:
                    if r.get("TECHNOLOGY"):
                        tech.add(r["TECHNOLOGY"].strip())
                    if r.get("FUEL"):
                        fuel.add(r["FUEL"].strip())
                    if r.get("EMISSION"):
                        emis.add(r["EMISSION"].strip())
        except Exception:
            pass
    return tech, fuel, emis


FILES = git_files()
TECH, FUEL, EMIS = load_sets(FILES)
ALLNAMES = TECH | FUEL | EMIS
PREFIXES = {}
for n in ALLNAMES:
    for k in range(3, min(8, len(n))):
        PREFIXES.setdefault(n[:k], set()).add(n)


def name_kind(tok):
    if tok in SCENARIOS:
        return "scenario"
    if tok in COUNTRIES:
        return "country"
    if tok in CCODES:
        return "country code"
    if tok in TECH:
        return "technology"
    if tok in FUEL:
        return "fuel"
    if tok in EMIS:
        return "emission"
    if re.fullmatch(r"[A-Z][A-Z0-9_]{2,}", tok) and len(PREFIXES.get(tok, ())) >= 2:
        return "technology or fuel name prefix"
    return None


def stage_of(path):
    base = os.path.basename(path)
    d = os.path.dirname(path)
    if "/" not in path:
        if base in PIPE_FILES_ROOT:
            return "yes"
        return "no"
    for md, names in PIPE_MODEL.items():
        if d == md and base in names:
            return "yes"
    return "no"


def target_table(path, kind, value, ctx):
    base = os.path.basename(path)
    if kind == "scenario":
        return "config/scenarios/ (one folder per scenario) and scenario_catalogue.csv, column scenario"
    if kind in ("country", "country code"):
        return "config/preparation/Config_country_codes.yaml, country_data (name, code, model_dir)"
    if kind in ("technology", "technology or fuel name prefix"):
        return "config/scenarios/technology_types.csv, columns group and technology"
    if kind == "fuel":
        return "inputs/osemosys_global/FUEL.csv (set) with a fuel_groups.csv, column fuel"
    if kind == "emission":
        return "inputs/osemosys_global/EMISSION.csv (set) with an emission_labels.csv, column emission"
    # numbers
    try:
        x = float(value)
    except Exception:
        x = None
    if x is not None and float(x).is_integer() and 1990 <= x <= 2100:
        col = "years (first_year, last_year, policy_start_year, history_end_year)"
    elif x is not None and 0 < abs(x) < 1e-3:
        col = "tolerances (name, value)"
    elif x is not None and 0 < x < 1:
        col = "shares and rates (name, scenario, year, value)"
    else:
        col = "parameters (name, value, unit)"
    if base.startswith("A2_") or base.startswith("A1_"):
        return f"config/compilation/Config_MOMF_T1_A.yaml, {col}"
    if base.startswith("B1_") or base.startswith("B2_"):
        return f"config/execution/Config_MOMF_T1_AB.yaml, {col}"
    if base.startswith("stage"):
        if "share" in ctx.lower() or "target" in ctx.lower():
            return "inputs/scenarios/scenario_values.csv, columns country, scenario, lever, year, value"
        return f"config/scenarios/rules/stage_controller.csv, {col}"
    if base == "OSeMOSYS_Model.txt":
        return f"model/ (one shared model file) with config/execution/Config_MOMF_T1_AB.yaml, {col}"
    return f"config/<stage>/ yaml of the owning stage, {col}"


PRESENTATION = re.compile(r"(^|/)(config_plots|plots?_|plot_csvs|create_csv_concat|test_|.*_test|folder_size|scan_large|cleanup_audit|clean_repo|pre_copy|compare_|consolidate_|snapshot_stage)", re.I)
MSG_CALLS = {"print", "info", "warning", "warn", "error", "debug", "write", "critical", "exception", "log", "set_title",
             "set_xlabel", "set_ylabel", "title", "xlabel", "ylabel", "suptitle", "legend", "text", "annotate", "savefig"}


class Scanner(ast.NodeVisitor):
    def __init__(self, path, src):
        self.path = path
        self.lines = src.splitlines()
        self.rows, self.acc, self.scen = [], [], []
        self.stack = []
        self.parents = {}

    def ctx_name(self, node):
        p = self.parents.get(node)
        chain = []
        cur = node
        while p is not None and len(chain) < 6:
            if isinstance(p, ast.Assign):
                t = p.targets[0]
                chain.append(ast.unparse(t)[:60])
                break
            if isinstance(p, (ast.AnnAssign, ast.AugAssign)):
                chain.append(ast.unparse(p.target)[:60])
                break
            if isinstance(p, ast.keyword):
                chain.append(f"{p.arg}=")
            if isinstance(p, ast.Dict):
                for k, v in zip(p.keys, p.values):
                    if v is cur and k is not None:
                        try:
                            chain.append(f"[{ast.unparse(k)[:40]}]")
                        except Exception:
                            pass
            if isinstance(p, ast.Call):
                try:
                    chain.append(ast.unparse(p.func)[:40] + "()")
                except Exception:
                    pass
            if isinstance(p, ast.Compare):
                try:
                    chain.append("compare " + ast.unparse(p.left)[:40])
                except Exception:
                    pass
            if isinstance(p, (ast.FunctionDef, ast.ClassDef)):
                break
            cur, p = p, self.parents.get(p)
        fn = next((s for s in reversed(self.stack)), "module")
        return (" < ".join(chain) if chain else "expression") + f" (in {fn})"

    def in_msg_call(self, node):
        p = self.parents.get(node)
        depth = 0
        while p is not None and depth < 5:
            if isinstance(p, ast.Call):
                fn = p.func
                nm = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
                if nm in MSG_CALLS:
                    return True
            if isinstance(p, (ast.Raise, ast.Assert)):
                return True
            p = self.parents.get(p)
            depth += 1
        return False

    def is_subscript_index(self, node):
        p = self.parents.get(node)
        if isinstance(p, ast.UnaryOp):
            p = self.parents.get(p)
        if isinstance(p, ast.Slice):
            return True
        if isinstance(p, ast.Subscript) and p.slice is not None:
            return True
        if isinstance(p, ast.Tuple) and isinstance(self.parents.get(p), ast.Subscript):
            return True
        return False

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return  # docstring or bare string
        self.generic_visit(node)

    def visit_Constant(self, node):
        v = node.value
        line = node.lineno
        if isinstance(v, bool) or v is None:
            return
        if isinstance(v, (int, float)):
            ctx = self.ctx_name(node)
            p = self.parents.get(node)
            neg = isinstance(p, ast.UnaryOp) and isinstance(p.op, ast.USub)
            val = -v if neg else v
            reason = None
            if val in (0, 1, -1, 0.0, 1.0):
                reason = "0, 1 or -1 (identity, sign or switch)"
            elif self.is_subscript_index(node):
                reason = "index or slice position"
            elif self.in_msg_call(node):
                reason = "inside a message, plot label or file write call (no effect on results)"
            elif PRESENTATION.search(self.path):
                reason = "plotting, test, audit or housekeeping script (no effect on model results)"
            elif any(abs(val - k) < 1e-9 * max(1, abs(k)) for k in UNIT_CONV):
                k = [k for k in UNIT_CONV if abs(val - k) < 1e-9 * max(1, abs(k))][0]
                reason = "unit conversion or calendar constant: " + UNIT_CONV[k]
            elif re.search(r"(figsize|fontsize|dpi|alpha|linewidth|width|height|color|rotation|pad|bbox|loc=|ncol|marker|labelsize|indent|max_workers|n_jobs|processes|timeout|sleep|retries|col_space|precision=|encoding)", ctx, re.I):
                reason = "presentation, parallelism or I/O setting (no effect on results)"
            elif re.search(r"\b(range|enumerate|zip|len|sleep|exit|insert|pop|split|rsplit|islice)\(\)", ctx) and isinstance(v, int) and abs(v) <= 10:
                reason = "loop, list or string position"
            row = {"file": self.path, "line": line, "name": ctx, "value": val, "kind": "number"}
            if reason:
                row["reason"] = reason
                self.acc.append(row)
            else:
                row["what_it_controls"] = describe(ctx, val)
                row["stage0_3_results_depend"] = stage_of(self.path)
                row["move_to"] = target_table(self.path, "number", val, ctx)
                self.rows.append(row)
            return
        if isinstance(v, str):
            if self.in_msg_call(node):
                return
            toks = set(re.split(r"[^A-Za-z0-9_]+", v)) | {v}
            # also split on underscores for scenario/country detection in paths
            sub = set()
            for t in toks:
                sub |= set(t.split("_"))
            found = []
            for t in sorted(toks | sub):
                if not t:
                    continue
                k = name_kind(t)
                if k is None:
                    continue
                if k in ("technology", "fuel", "emission", "technology or fuel name prefix") and t not in toks:
                    continue  # only whole tokens for model elements
                if k == "country code" and t not in toks and t != v:
                    pass
                found.append((t, k))
            if not found:
                return
            ctx = self.ctx_name(node)
            for t, k in found:
                if k == "scenario":
                    self.scen.append({"name": t, "place": f"{self.path}:{line}", "kind": "code literal"})
                row = {"file": self.path, "line": line, "name": ctx, "value": t if t == v else f"{t} (in '{v[:80]}')",
                       "kind": k}
                if PRESENTATION.search(self.path) and k not in ("scenario", "country", "country code"):
                    row["reason"] = "element name in a plotting, test, audit or housekeeping script (no effect on model results)"
                    self.acc.append(row)
                    continue
                row["what_it_controls"] = f"{k} name used by {ctx}"
                row["stage0_3_results_depend"] = stage_of(self.path)
                row["move_to"] = target_table(self.path, k, t, ctx)
                self.rows.append(row)


def describe(ctx, val):
    c = ctx.lower()
    try:
        x = float(val)
    except Exception:
        x = None
    if x is not None and float(x).is_integer() and 1990 <= x <= 2100:
        return f"year {int(x)} used by {ctx}"
    for key, txt in [("share", "a share"), ("target", "a target"), ("tol", "a tolerance"), ("eps", "a tolerance"),
                     ("round", "rounding precision"), ("factor", "a factor"), ("multiplier", "a multiplier"),
                     ("bound", "a bound"), ("limit", "a limit"), ("cap", "a cap"), ("min", "a lower value"),
                     ("max", "an upper value"), ("rate", "a rate"), ("loss", "a loss value"), ("cost", "a cost"),
                     ("year", "a year"), ("price", "a price"), ("cf", "a capacity factor"), ("eff", "an efficiency")]:
        if key in c:
            return f"{txt}: {ctx}"
    return f"number used by {ctx}"


DRAFT = os.environ.get('SCAN_DRAFT', '')


def _full(path):
    d = os.path.join(DRAFT, path) if DRAFT else ''
    return d if d and os.path.exists(d) else os.path.join(REPO, path)


def scan_py(path):
    full = _full(path)
    try:
        src = open(full, encoding="utf-8").read()
    except UnicodeDecodeError:
        src = open(full, encoding="latin-1").read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    sc = Scanner(path, src)
    for p in ast.walk(tree):
        for ch in ast.iter_child_nodes(p):
            sc.parents[ch] = p
    sc.visit(tree)
    return sc


NUM_RE = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?(?:[eE]-?\d+)?(?![A-Za-z0-9_])")


def scan_text(path, comment):
    full = _full(path)
    rows, acc, scen = [], [], []
    try:
        lines = open(full, encoding="utf-8", errors="replace").read().splitlines()
    except Exception:
        return rows, acc, scen
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or re.match(comment, s):
            continue
        code = re.split(r"#", line)[0] if path.endswith("OSeMOSYS_Model.txt") else line
        for t in sorted(set(re.split(r"[^A-Za-z0-9_]+", code)) | {x for tok in re.split(r"[^A-Za-z0-9_]+", code) for x in tok.split("_")}):
            k = name_kind(t) if t else None
            if not k:
                continue
            if k in ("technology", "fuel", "emission", "technology or fuel name prefix") and t not in set(re.split(r"[^A-Za-z0-9_]+", code)):
                continue
            if k == "scenario":
                scen.append({"name": t, "place": f"{path}:{i}", "kind": "code literal"})
            rows.append({"file": path, "line": i, "name": s[:80], "value": t, "kind": k,
                         "what_it_controls": f"{k} name in a command or model line",
                         "stage0_3_results_depend": stage_of(path), "move_to": target_table(path, k, t, s)})
        for m in NUM_RE.finditer(code):
            val = m.group(0)
            x = float(val)
            r = {"file": path, "line": i, "name": s[:80], "value": val, "kind": "number"}
            if x in (0, 1, -1):
                r["reason"] = "0, 1 or -1 (identity, sign or switch)"
                acc.append(r)
            elif path.endswith((".bat", ".sh")) and re.search(r"_FINAL_" + re.escape(val) + r"\b|_" + re.escape(val) + r"\b", code):
                r["reason"] = "run index in a file name (future 0)"
                acc.append(r)
            else:
                r["what_it_controls"] = f"number in a {'model equation' if path.endswith('.txt') else 'command'} line"
                r["stage0_3_results_depend"] = stage_of(path)
                r["move_to"] = target_table(path, "number", val, s)
                rows.append(r)
    return rows, acc, scen


def main():
    rows, acc, scen, unparsed = [], [], [], []
    for f in FILES:
        if f.endswith(".py"):
            sc = scan_py(f)
            if sc is None:
                unparsed.append(f)
                continue
            rows += sc.rows
            acc += sc.acc
            scen += sc.scen
        elif f.endswith((".bat", ".sh")):
            a, b, c = scan_text(f, r"^(rem|::|#|echo)\b")
            rows += a; acc += b; scen += c
        elif f.endswith("OSeMOSYS_Model.txt"):
            a, b, c = scan_text(f, r"^#")
            rows += a; acc += b; scen += c
    for r in rows + acc:  # quoted repository text may hold an em dash; the job files carry none
        for k, v in r.items():
            if isinstance(v, str):
                r[k] = v.replace(chr(0x2014), "-").replace(chr(0x2013), "-")
    flds = ["file", "line", "name", "value", "kind", "what_it_controls", "stage0_3_results_depend", "move_to"]
    write_csv(os.path.join(JOB, "script_constants.csv"), rows, flds)
    write_csv(os.path.join(JOB, "script_constants_accepted.csv"), acc, ["file", "line", "name", "value", "kind", "reason"])
    write_csv(os.path.join(JOB, "parts", "scenario_names_code.csv"), scen)
    print("files", len(FILES), "py unparsed", len(unparsed), unparsed[:10])
    print("tech", len(TECH), "fuel", len(FUEL), "emis", len(EMIS))
    print("constants", len(rows), "accepted", len(acc), "scenario literals", len(scen))


if __name__ == "__main__":
    main()
