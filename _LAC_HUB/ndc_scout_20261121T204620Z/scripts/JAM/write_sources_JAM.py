"""Write parts/sources_JAM.csv and parts/sources_pending_JAM.csv (hashes and page counts computed).

Usage: python -I write_sources_JAM.py <job_dir>
"""
import csv
import hashlib
import os
import sys

import pypdf

JOB = sys.argv[1]

SOURCES = [
    dict(id="JAM-01", kind="NDC",
         URL="https://unfccc.int/sites/default/files/2025-09/Jamaica%20ICTU%20Final%20Report%20Sep19.pdf (byte-identical copy at https://cdn.climatepolicyradar.org/navigator/JAM/2025/jamaica-nationally-determined-contribution-ndc3-0_f42061f526e5be30a46bc68b28b0f622.pdf; record https://climate-laws.org/document/jamaica-nationally-determined-contribution-ndc3-0_f252)",
         title="New and Updated Nationally Determined Contribution (NDC) of Jamaica to the UNFCCC (Jamaica's NDC 3.0)",
         publisher="Government of Jamaica, Climate Change Branch, Ministry of Economic Growth and Job Creation (MEGJC)",
         date="2025-09 (PDF created 2025-09-19; Climate Policy Radar record date 2025-09-22; UNFCCC file folder 2025-09)",
         file="downloads/JAM/JAM_NDC3_2025_cpr.pdf", language="English"),
    dict(id="JAM-02", kind="LTS",
         URL="https://cdn.climatepolicyradar.org/navigator/JAM/2023/jamaica-s-long-term-emission-reduction-and-climate-resilient-strategy-lt-leds1_ed207b9e133ba9f2b9c38de52a569695.pdf (record https://climate-laws.org/document/jamaica-s-long-term-emission-reduction-and-climate-resilient-strategy-lt-leds1_a6b3; UNFCCC record https://unfccc.int/documents/649405 not opened, bot-check page)",
         title="2050 Long-term Emission Reduction and Climate Resilient Strategy for Jamaica (LT-LEDS 1)",
         publisher="Government of Jamaica, Climate Change Branch, Ministry of Economic Growth and Job Creation, with the Planning Institute of Jamaica",
         date="Cover dated November 2023; PDF created 2025-08-18 and modified 2025-08-27; submitted to the UNFCCC 2025-08-29 (brief lead, UNFCCC page not opened); NDC 3.0 says approved in 2024 (JAM-01 p.3)",
         file="downloads/JAM/JAM_LTS_cpr.pdf", language="English"),
    dict(id="JAM-03", kind="NDC",
         URL="https://unfccc.int/sites/default/files/NDC/2022-06/Updated%20NDC%20Jamaica%20-%20ICTU%20Guidance.pdf (byte-identical copy at https://cdn.climatepolicyradar.org/navigator/JAM/1900/jamaica-first-ndc-updated-submission_f2e46aeeef25c309558036f804f1c414.pdf; record https://climate-laws.org/document/jamaica-nationally-determined-contribution-ndc1-updated-submission_fad6)",
         title="Update of Nationally Determined Contribution (NDC) of Jamaica (updated first NDC, NDC 2.0)",
         publisher="Government of Jamaica, Climate Change Division, Ministry of Economic Growth and Job Creation",
         date="June 2020 (cover p.1; PDF created 2020-06-30; Climate Policy Radar record date 2020-07-01)",
         file="downloads/JAM/JAM_NDC1_update_2020.pdf", language="English"),
    dict(id="JAM-04", kind="NDC",
         URL="https://cdn.climatepolicyradar.org/navigator/JAM/1900/jamaica-first-ndc-archived_83590e2551035c3b10ca1fcd62a63932.pdf (record https://climate-laws.org/document/jamaica-nationally-determined-contribution-ndc1-archived_ff94)",
         title="Intended Nationally Determined Contribution of Jamaica (INDC; first NDC, archived)",
         publisher="Government of Jamaica (Climate Change Division, Ministry of Water, Land, Environment and Climate Change)",
         date="2015-11 (PDF created 2015-11-26); counted as first NDC, Climate Policy Radar record date 2017-04-10",
         file="downloads/JAM/JAM_NDC1_2015_archived.pdf", language="English"),
    dict(id="JAM-05", kind="BUR",
         URL="https://unfccc.int/sites/default/files/resource/JAM_BUR1.pdf",
         title="Biennial Update Report of Jamaica (first BUR; inventory 2006-2012)",
         publisher="Government of Jamaica, Ministry of Economic Growth and Job Creation",
         date="2016 (no date printed on the cover; inventory years 2006-2012; submission date not confirmed from a document)",
         file="downloads/JAM/JAM_BUR1_2016.pdf", language="English"),
    dict(id="JAM-06", kind="NC",
         URL="https://unfccc.int/sites/default/files/resource/TNC_Final_December132018.pdf",
         title="Third National Communication of Jamaica to the UNFCCC (with GHG inventory 2006-2012 and LEAP mitigation analysis)",
         publisher="Ministry of Economic Growth and Job Creation, Climate Change Division",
         date="2018 (copyright 2018, p.2; file name dated 13 December 2018)",
         file="downloads/JAM/JAM_TNC_2018.pdf", language="English"),
    dict(id="JAM-07", kind="sector plan",
         URL="https://gpe.gov.jm/wp-content/uploads/2024/11/2022-Jamaica-Integrated-Resource-Plan.pdf",
         title="2022 Jamaica Integrated Resource Plan, 2018 IRP Review and Update (IRP-2)",
         publisher="Ministry of Science, Energy, Telecommunications and Transport (MSETT), Jamaica",
         date="August 2023 (cover p.1, final, approved by Cabinet); uploaded to gpe.gov.jm 2024-11",
         file="downloads/JAM/JAM_IRP_2022_gpe.pdf", language="English"),
    dict(id="JAM-08", kind="sector plan",
         URL="https://www.mset.gov.jm/wp-content/uploads/2020/03/2018-Jamaica-Integrated-Resource-Feb-21-2020.pdf (copy reused from LAC_sources_archive cost_src_jam_20261110T025557Z/plant2, SHA-256 unchanged)",
         title="2018 Jamaica Integrated Resource Plan, A 20 Year Roadmap to Sustain and Enable Jamaica's Electricity Future (IRP-1, superseded by JAM-07)",
         publisher="Ministry of Science, Energy and Technology (MSET), Jamaica; prepared with DNV GL",
         date="Draft 8 January 2020, revised 20 January 2020 (p.1); page footers dated February 21, 2020",
         file="downloads/JAM/JAM_IRP_2018_mset_Feb2020.pdf", language="English"),
]

PENDING = [
    dict(country="Jamaica", kind="LTS",
         title="2050 Long-term Emission Reduction and Climate Resilient Strategy for Jamaica, as filed on the UNFCCC long-term strategies portal (submission 29 August 2025)",
         urls_tried="https://unfccc.int/documents/649405 (curl with browser User-Agent); https://unfccc.int/documents/649405 (WebFetch); https://climate-laws.org/documents/2050-long-term-emission-reduction-and-climate-resilient-strategy-for-jamaica_a2bc (record page, links only to the Climate Policy Radar copy)",
         errors="curl: 212-byte Incapsula bot-check page; WebFetch: empty page; climate-laws record: no UNFCCC file link",
         note="The Climate Policy Radar copy (JAM-02, 194 pages, PDF modified 2025-08-27) was used. Whether it is byte-identical to the UNFCCC file is unknown."),
    dict(country="Jamaica", kind="BTR",
         title="First Biennial Transparency Report of Jamaica and National Inventory Document",
         urls_tried="https://unfccc.int/first-biennial-transparency-reports (curl and WebFetch); https://unfccc.int/BTR1 (curl); https://unfccc.int/sites/default/files/resource/JAM_BTR1.pdf; https://unfccc.int/sites/default/files/resource/Jamaica_BTR1.pdf; https://unfccc.int/sites/default/files/resource/Jamaica%20BTR1.pdf; https://unfccc.int/sites/default/files/resource/JAM_BUR2.pdf; web searches (3) and climate-laws.org geography page",
         errors="UNFCCC listing: bot-check page (curl) and empty page (WebFetch); guessed file names: HTTP 404 HTML pages; no BTR1 or NID of Jamaica found in searches or on climate-laws.org",
         note="NDC 3.0 (September 2025) says the inventory will be updated and the BTR will be prepared (JAM-01 p.18), so a BTR1 may not exist. Newest inventory documents used: TNC 2018 (JAM-06) and BUR1 (JAM-05), both 2006-2012."),
]

COLS = ["id", "country", "kind", "URL", "title", "publisher", "date", "accessed", "SHA-256", "file", "pages", "language"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    rows = []
    for s in SOURCES:
        path = os.path.join(JOB, s["file"])
        with open(path, "rb") as fh:
            assert fh.read(5) == b"%PDF-", path
        n = len(pypdf.PdfReader(path).pages)
        r = dict(s)
        r.update({"country": "Jamaica", "accessed": "2026-11-21", "SHA-256": sha(path), "pages": n})
        rows.append(r)
    with open(os.path.join(JOB, "parts", "sources_JAM.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in COLS})
    with open(os.path.join(JOB, "parts", "sources_pending_JAM.csv"), "w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=["country", "kind", "title", "urls_tried", "errors", "note"], lineterminator="\n")
        w.writeheader()
        for r in PENDING:
            w.writerow(r)
    for r in rows:
        print(r["id"], r["pages"], r["SHA-256"])


if __name__ == "__main__":
    main()
