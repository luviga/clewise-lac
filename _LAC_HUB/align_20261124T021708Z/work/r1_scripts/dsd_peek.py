import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(sys.argv[1], encoding="utf-8"))
data = d["data"]
for cl in data.get("codelists", []):
    n = len(cl.get("codes", []))
    print("CL", cl["id"], n)
    if n < 150:
        for c in cl["codes"]:
            print("   ", c["id"], "|", c.get("name"))
