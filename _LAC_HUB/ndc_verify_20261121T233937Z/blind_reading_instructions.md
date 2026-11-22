# LAC_NDC_VERIFY: instructions for the blind reading (check 2)

Job folder: `C:\clw_scout\_LAC_HUB\ndc_verify_20261121T233937Z` (Git Bash: `/c/clw_scout/_LAC_HUB/ndc_verify_20261121T233937Z`), called JOB below.

You give a second, independent reading of published values in climate policy documents (NDCs, long-term strategies, transparency reports, sector plans) of Latin American and Caribbean countries. Another reader has already read them; you must not see that reading.

## Files you may open

- `JOB/blind_<code>.csv` for your countries. Columns: `blind_id, source_id, pdf_file, pages, what_to_read`.
- The PDF named in `pdf_file`, and only the pages listed in `pages`, rendered as images.
- Nothing else. Do not open any CSV, MD or TXT file in `C:\clw_scout\_LAC_HUB\ndc_scout_20261121T204620Z\` (the PDFs under its `downloads\` folder are the only exception), do not open `JOB/values_to_verify.csv`, `JOB/verification_*.csv` or anything under `JOB/parts/`, and do not use any text cache (`text/`, `text_all/` folders). Do not search the web.

## How to read

1. Render each listed page to PNG with pdfplumber and look at the image with the Read tool. Page numbers in `pages` are physical PDF pages counted from 1 (`p.13` is `pdf.pages[12]`). Script (write it with the file tool into `JOB/scripts/blind/`, never with a shell heredoc):
   `/c/clw_scout_venv/Scripts/python.exe -I render.py <pdf_file> <page> <out.png> [resolution]`
   using `pdfplumber.open(pdf).pages[n-1].to_image(resolution=150).save(out)`. Save images to `JOB/downloads/<code>/img_blind/<source_id>_p<N>.png`. For dense tables, render at 200 to 250 or crop the region (`page.crop(bbox).to_image(...)`) and read the crop.
2. Find what `what_to_read` describes. `[year]`, `[n]` and `[unit]` mark a year, number or unit that was removed on purpose. Read from the image: the value exactly as printed (keep the printed decimals), the unit as printed, the year (or period) it refers to, and where on the page it is (table or figure name, printed page number, row or column label).
3. If several years or values are printed for the same description on the page (for example 2030 and 2035, or a series of years), report one row per year and value. For a projected emissions series, report every year printed on that page for that scenario and sector.
4. Read all pages listed until you find it; report the page where you read it. If it is on several listed pages, report each (one row each).
5. If you cannot find it on any listed page, write one row with `value` empty and `note` = `not found on listed pages` (and what you saw). Never guess, never write a value from memory, never compute a value that is not printed. If the page is unreadable, say so.
6. Conditionality: if the page says the value is conditional or unconditional, put that in `note`.

## What you write

`JOB/blind_answers_<code>.csv`, UTF-8, LF line endings (`newline="\n"`), columns exactly:
`blind_id,page_read,value,unit,year,reference,note`

- `page_read`: `p.N` (physical page).
- `value`: plain number with a dot decimal and no thousands separators (convert `75.738,0` or `75 738,0` to `75738.0`, keep the printed decimals). If the printed figure is text such as "1 000 MW", value `1000`, unit `MW`.
- `unit`: as printed (for example `Gg CO2e`, `kt CO2 eq`, `%`, `MW`, `GWh`).
- `year`: the year or period (for example `2035` or `2026-2035`).
- `reference`: table or figure name and printed page, row or column label.
- Plain English, no em dashes.

Write the file per country as you go (append), so that work is not lost. Keep a short log of anything odd in `JOB/blind_log_<code>.md`.

## Final message

Under 200 words: files written, items read, items not found, anything that looked wrong in the blind file (wrong page, unreadable). Do not paste values.
