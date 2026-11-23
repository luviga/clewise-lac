"""Download UN Comtrade annual imports (reporter = the country itself, partner = World)
for the HS 6-digit vehicle lines of vehicle_class_map.csv, 2019 to 2023.

Saves one raw JSON per country into downloads/comtrade/ and appends every request to
<CC>/search_log_<CC>.csv. Public preview API, no key. Waits at least 10 seconds between
requests and retries after HTTP 429.
"""
import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.request
import urllib.error

JOB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPORTERS = {"CR": 188, "DR": 214, "GUA": 320, "HON": 340, "JAM": 388}
YEARS = [2019, 2020, 2021, 2022, 2023]  # the preview API takes one period per request
BASE = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"


def hs_codes():
    codes = set()
    with open(os.path.join(JOB, "vehicle_class_map.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for col in ("hs2017_codes", "hs2022_codes"):
                for c in r[col].split(";"):
                    if c.strip():
                        codes.add(c.strip())
    return sorted(codes)


def log(cc, url, status, result):
    path = os.path.join(JOB, cc, f"search_log_{cc}.csv")
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(["date_utc", "route", "url", "http_status", "result"])
        w.writerow([dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "2 UN Comtrade (reporter)", url, status, result])


def main():
    out = os.path.join(JOB, "downloads", "comtrade")
    os.makedirs(out, exist_ok=True)
    codes = ",".join(hs_codes())
    only = sys.argv[1:] or list(REPORTERS)
    for cc in only:
        for year in YEARS:
            url = (f"{BASE}?reporterCode={REPORTERS[cc]}&period={year}&partnerCode=0"
                   f"&flowCode=M&cmdCode={codes}&includeDesc=true")
            for attempt in range(6):
                try:
                    with urllib.request.urlopen(url, timeout=120) as r:
                        body = r.read()
                        status = r.status
                    data = json.loads(body)
                    fn = os.path.join(out, f"comtrade_{cc}_imports_{year}.json")
                    with open(fn, "wb") as f:
                        f.write(body)
                    recs = data.get("data", [])
                    est = sum(1 for x in recs if x.get("isQtyEstimated"))
                    log(cc, url, status, f"{len(recs)} records saved as downloads/comtrade/{os.path.basename(fn)}; "
                                         f"{est} with the quantity estimated by the UN, not reported")
                    print(cc, year, status, len(recs), "records,", est, "qty estimated", flush=True)
                    break
                except urllib.error.HTTPError as e:
                    log(cc, url, e.code, "HTTP 429, retried after 30 s" if e.code == 429 else "HTTP error")
                    print(cc, year, "HTTP", e.code, flush=True)
                    if e.code != 429:
                        break
                    time.sleep(30)
            time.sleep(12)

if __name__ == "__main__":
    main()
