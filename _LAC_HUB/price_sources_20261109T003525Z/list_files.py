"""List every file in the output folder with origin URL (from sources.csv / country CSV local_file fields) or purpose. Writes file_inventory.csv."""
import sys, os, pandas as pd
OUT = sys.argv[1]
src = pd.read_csv(os.path.join(OUT, "sources.csv"))
url_by_name = {}
for _, r in src.iterrows():
    for part in str(r.local_file).replace("/", os.sep).split(";"):
        name = os.path.basename(part.strip())
        if name and name != "nan":
            url_by_name.setdefault(name, r.url)
for cc in ["CR", "DR", "GUA", "HON", "JAM", "ECU"]:
    d = pd.read_csv(os.path.join(OUT, "downloads", cc, f"{cc}_regulator_2024.csv"))
    for lf, u in zip(d.local_file.astype(str), d.source_url.astype(str)):
        for part in lf.split(";"):
            url_by_name.setdefault(os.path.basename(part.strip()), u)
rows = []
for root, _, files in os.walk(OUT):
    for f in files:
        p = os.path.relpath(os.path.join(root, f), OUT).replace(os.sep, "/")
        ext = f.rsplit(".", 1)[-1].lower()
        if ext == "py":
            what = "helper script"
        elif p.startswith("downloads/") and f in url_by_name:
            what = "downloaded from " + url_by_name[f]
        elif p.startswith("downloads/") and ext in ("txt", "json", "png", "md", "csv") :
            what = "derived (text extract, page render, notes or extraction table made in this session from a downloaded file in the same folder)"
        elif p.startswith("downloads/"):
            what = "downloaded public file (origin listed in the folder's notes file or sources.csv)"
        else:
            what = "output"
        rows.append(dict(path=p, bytes=os.path.getsize(os.path.join(root, f)), origin_or_purpose=what))
pd.DataFrame(rows).sort_values("path").to_csv(os.path.join(OUT, "file_inventory.csv"), index=False)
df = pd.DataFrame(rows)
print(len(df)); print(df.groupby(df.path.str.split("/").str[:2].str.join("/")).size().to_string())
print(df[df.origin_or_purpose.str.startswith("downloaded public")].path.head(30).to_string())
