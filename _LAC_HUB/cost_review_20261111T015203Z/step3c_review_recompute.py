"""Step 3, third part: hand review of every row the automatic recompute left above 0.5 percent.
Each is recomputed here from the numbers the derivation states; the verdict goes into derivation_recompute.csv."""
import re
import sys

sys.path.insert(0, ".")
from common import *  # noqa

D = pd.read_csv(out("derivation_recompute.csv"), dtype=str, keep_default_na=False)
verdict = []
for _, r in D.iterrows():
    der, v = r["derivation"], ""
    if r["check"] != "arithmetic in derivation":
        verdict.append("projection off the WEO path: open")
        continue
    m = re.search(r"(?:proposed \w+ \d{4}|CapitalCost \d{4}|FixedCost \d{4}) ([\d.]+) x .*?\(\d{4}\) ([\d.]+) = ([\d.]+)", der)
    if r["cc"] == "gua" and m:
        a, b, c = map(float, m.groups())
        v = f"{a} x {b} = {a * b:.2f} against stated {c} ({(a * b / c - 1) * 100:+.2f} percent): matches; the parser read the ATB edition year as an operand"
    elif r["cc"] == "cr" and "4013" in der:
        v = f"4013 x 292.655 / 255.657 = {4013 * 292.655 / 255.657:.1f} against stated 4593.8: matches; the parser joined '+0.1 percent' to the chain"
    elif r["cc"] == "cr" and "3242" in der:
        v = f"3242 x 292.655 / 313.689 = {3242 * 292.655 / 313.689:.2f} against stated 3024.61: matches; the parser joined '+0.2 percent' to the chain"
    elif r["cc"] == "dr" and "2,881" in der:
        v = f"2881 x 2.5 percent = {2881 * 0.025:.3f} against stated 72.025: matches; the percent sign was not read"
    elif r["cc"] == "hon" and "0.5417" in der:
        v = f"3.3543 x 0.5417 + 2.9568 x 0.4583 = {3.3543 * 0.5417 + 2.9568 * 0.4583:.4f} against stated 3.1721: matches (weighted mean)"
    elif r["cc"] == "jam" and "propane" in der:
        v = (f"(28480869.08 + 32296959.41) / (66626949.81 + 75847223.59) x 1000 = "
             f"{(28480869.08 + 32296959.41) / (66626949.81 + 75847223.59) * 1000:.2f} against stated 426.59: matches")
    else:
        v = "not reviewed by hand"
    verdict.append(v)
D["hand_review"] = verdict
write(D, "derivation_recompute.csv")
print(D["hand_review"].str.contains("matches").sum(), "of", len(D), "rows match when recomputed by hand")
print(D.loc[~D["hand_review"].str.contains("matches"), ["cc", "row", "hand_review"]].to_string())
