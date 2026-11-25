"""Step 3.1: compare every regenerated A2_Output_Params and B1_Output_Params file with its tracked copy (the index
of git), keyed by all index columns. A difference is staleness when a value, a key or a file differs by more than
float noise (1e-9 relative); row order, formatting and float noise below that are compiler nondeterminism.
Writes stale_compare.csv (one row per changed file) in the job folder.
Usage: py -I stale_compare.py [path prefix ...]"""
import sys as _Msys, os as _Mos  # noqa: E401
_Msys.path.insert(0, _Mos.path.dirname(_Mos.path.abspath(__file__)))
import machine as M  # noqa: E402
import csv
import io
import subprocess
import sys

ROOT, JOB = M.ROOT, M.JOB
NOISE = 1e-9


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")


def rows_of(text):
    rd = csv.DictReader(io.StringIO(text))
    return rd.fieldnames or [], list(rd)


def keyed(fields, rows):
    vcol = "Value" if "Value" in fields else fields[-1]
    keys = [f for f in fields if f not in (vcol, "Scenario")]  # the scenario label is compared on its own
    out, dup = {}, 0
    for r in rows:
        k = tuple((r.get(c) or "").strip() for c in keys)
        k = tuple(x[:-2] if x.endswith(".0") and x[:-2].lstrip("-").isdigit() else x for x in k)
        if k in out:
            dup += 1
        out[k] = r.get(vcol)
    return keys, out, dup


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    pref = sys.argv[1:]
    st = git("status", "--porcelain", "--untracked-files=all").stdout.splitlines()
    files = []
    for ln in st:
        code, path = ln[:2], ln[3:].strip().strip('"')
        if ("A2_Output_Params/" in path or "B1_Output_Params/" in path) and path.endswith(".csv") and not path.startswith("_LAC_HUB/"):
            if not pref or any(path.startswith(p) for p in pref):
                files.append((code.strip(), path))
    out = []
    for code, path in sorted(files):
        new_text = open(ROOT / path, encoding="utf-8", errors="replace").read()
        old = git("show", f"HEAD:{path}")
        old_text = old.stdout if old.returncode == 0 else None
        nf, nr = rows_of(new_text)
        rec = dict(path=path, git_status=code, rows_tracked="", rows_new=len(nr), keys_only_tracked=0,
                   keys_only_new=0, values_changed=0, noise_only=0, max_abs_change="", example="", kind="",
                   scenario_label="")
        if old_text is None:
            rec.update(kind="staleness", example="file not tracked (new compiled file)")
            out.append(rec)
            continue
        of, orows = rows_of(old_text)
        rec["rows_tracked"] = len(orows)
        _, ko, _ = keyed(of, orows)
        _, kn, _ = keyed(nf, nr)
        lab_o = sorted({(r.get("Scenario") or "") for r in orows})
        lab_n = sorted({(r.get("Scenario") or "") for r in nr})
        rec["scenario_label"] = "" if lab_o == lab_n else f"{'/'.join(lab_o)} -> {'/'.join(lab_n)}"
        only_o = [k for k in ko if k not in kn]
        only_n = [k for k in kn if k not in ko]
        changed, noise, mx, ex = 0, 0, 0.0, ""
        for k in ko.keys() & kn.keys():
            a, b = ko[k], kn[k]
            if a == b:
                continue
            fa, fb = num(a), num(b)
            if fa is not None and fb is not None:
                d = abs(fa - fb)
                if d <= NOISE * max(abs(fa), abs(fb), 1.0):
                    noise += 1
                    continue
                mx = max(mx, d)
            changed += 1
            if not ex:
                ex = f"{'|'.join(x for x in k if x)}: {a} -> {b}"
        if not ex and only_o:
            ex = f"row only in tracked: {'|'.join(x for x in only_o[0] if x)} = {ko[only_o[0]]}"
        if not ex and only_n:
            ex = f"row only in new: {'|'.join(x for x in only_n[0] if x)} = {kn[only_n[0]]}"
        rec.update(keys_only_tracked=len(only_o), keys_only_new=len(only_n), values_changed=changed, noise_only=noise,
                   max_abs_change=f"{mx:.6g}" if changed else "", example=ex,
                   kind="staleness" if (changed or only_o or only_n or rec["scenario_label"]) else "nondeterminism")
        out.append(rec)
    with open(JOB / "stale_compare.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]) if out else ["path"], lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(r["kind"], r["path"], r["values_changed"], r["keys_only_tracked"], r["keys_only_new"], r["example"][:120])


if __name__ == "__main__":
    main()
