# Costa Rica (CR): notes for job LAC_LOCAL_PRICES 20261109T085226Z

## Summary

Closed with local evidence:

- Petroleum coke `IMPCOK` (was ASSUMPTION candidate): PROCOMER customs open data (VUCE OData), HS 271311, 2024: 98,974 t for 10,063,119.59 USD, 101.67 USD/t, 3.128 USD/GJ on the IPCC net calorific value (32.5 GJ/t). UN Comtrade carries the same record as CIF and is kept as the second row. Series 2018 to 2025 in `history_CR.csv`.
- Coal `IMPCOA` (was ASSUMPTION candidate): PROCOMER HS 270111 anthracite, 2024: 233 t for 131,404.79 USD, 562.84 USD/t, 21.08 USD/GJ (IPCC anthracite NCV 26.7 GJ/t). This is a real published import cost but for small specialty lots; see Known-limitation candidates.
- Liquids (DSL, GSL, JET, KER, LPG, FOI, AVG), re-confirmed from the 12 monthly ARESEP resolutions (re-downloaded), plus a new source: ARESEP open data on RECOPE purchase invoices, which publishes FOB, freight, insurance, CIF, trader cost, port cost, litres and mass for every 2024 cargo. Recorded per fuel: import CIF with FOB, freight and insurance split (USD/L); wholesale import parity as COA plus RECOPE margin K (CRC/L); final consumer pre-tax at the RECOPE plantel; final consumer pre-tax at road and airport service stations with the station margin and freight as separate components.
- Generator delivered (`PWRFOI`, `PWRDSL`): built from the 12-month mean plantel price without tax plus the freight ICE pays (7.045 CRC/L bunker, 6.20 CRC/L diesel) stated in the ARESEP CVG resolutions RE-0164-IE-2023 and RE-0097-IE-2024. Bunker Termico ICE 2: 280.49 CRC/L, 13.93 USD/GJ. Diesel: 385.41 CRC/L, 20.82 USD/GJ. The tax-inclusive values ARESEP published for the 2024 CVG (329.74 and 625.78 CRC/L, December 2023 prices) are kept as separate rows.
- Exchange rate: `CR_FX_2024` = 515.11 CRC/USD from World Bank WDI (official rate, period average). The BCCR daily file could not be downloaded (see Incidents); it is on the manual list.

Still open:

- Natural gas `IMPNGS`: Costa Rica imported no natural gas in 2024 (PROCOMER: no LNG under 271111, 3 kg under 271121; Comtrade the same). No Costa Rican LNG study price was found. Kept as ASSUMPTION candidate at the existing 7.763 USD/GJ (gross).
- Calorific basis: the national energy balance (MINAE/SEPSE) and the OLADE manual both refused automated access. `calorific_CR.csv` has no factors. Both are on the manual list.

Counts: 40 rows in `prices_CR.csv` (33 local regulator or operator, 2 local customs or statistics, 2 international customs (Comtrade), 2 built from published components, 1 ASSUMPTION candidate); 48 rows in `history_CR.csv`; 17 constants; 24 sources; 139 search log rows; 4 manual downloads. The sourcing check (`check_cr.py`) passes for prices, history and constants; its only failures are the two `calorific_CR.csv` rows, which have no source because neither balance could be downloaded.

## Judgement calls and reasons

- Import cost of liquids: taken from the ARESEP open data purchase records (invoice FOB, freight, insurance, CIF) rather than from the resolutions, because the records cover every 2024 cargo and split the components. A year is the ARESEP reference year (`anho`), which follows the discharge month (vessels discharged 18 Dec 2023 to 1 Jan 2025). Values are volume-weighted.
- The "Precio FOB estimado" in the resolutions' subsidy table was not used. It is a fixed share (84.88 to 89.17 percent) of the terminal price used for the subsidy decree, not an invoice FOB. The earlier job used it for bunker and LPG.
- Densities: the brief prefers a source's own density. The purchase records give mass and litres per cargo, so 2024 densities (`CR_DENS_*_2024`) come from them (diesel 0.8356, RON 91 0.7297, RON 95 0.7365, jet 0.7981, avgas 0.6929, bunker 0.9882, bunker termico ICE 2 0.9676, LPG 0.5239 kg/L). Kerosene uses the jet density (ARESEP sets kerosene COA equal to jet). The same 2024 densities are used for 2022, 2023 and 2025 history because the mass field is incomplete in some 2022 and 2023 records.
- Net calorific values: IPCC 2006 defaults (shared constants), so every USD/GJ value is on a net basis except natural gas (gross, as the hub's benchmark).
- Gasoline: two grades are reported (RON 91 regular and RON 95 super) because the model has one gasoline row. 2024 import volumes were 631.6 million litres RON 91 and 795.9 million litres RON 95, if the build job wants a weighted value.
- Jet: "Jet fuel A-1" and "Jet Fuel A" (which replaced it from late 2024) are combined.
- Monthly means: a simple mean of the 12 monthly resolutions (prices in force January to December 2024), not weighted by days in force or sales.
- LPG plantel price: the subsidised terminal price without tax from the subsidy table; for June and July that table was not readable as text, so the Por Tanto I.b price with tax per litre minus the impuesto unico was used (identical in every month where both exist).
- June 2024 station prices for Av-Gas and Jet A-1 come from the rectification RE-0044-IE-2024 in the same Alcance, which corrected a data-transfer error in RE-0043-IE-2024.
- Generator delivered is pre-tax: ARESEP values ICE fuel with the impuesto unico included; the row removes it (2024 mean 25.10 CRC/L bunker, 154.19 CRC/L diesel) to match the pre-tax convention. The plantel price of Bunker Termico ICE 2 is subsidised (mean 273.44 CRC/L against a COA plus K of 299.42 CRC/L), so the generator delivered price is below the wholesale import parity.
- Exchange rate: WDI 515.11 is the IMF IFS official period average. It equals the earlier job's 366-day mean of the BCCR buying and selling reference rates (515.10), not the selling-rate mean (518.23) that job used. ARESEP itself converts invoices at a 15-day mean of the BCCR selling rate for the non-bank public sector (503.97 to 532.99 CRC/USD by month in 2024).

## Values that could not be sourced externally

- BCCR daily reference exchange rates for 2024 (replaced by the WDI annual average).
- National energy balance conversion factors and net or gross basis (MINAE/SEPSE), and the OLADE second source.
- Any natural gas or LNG import or study price for Costa Rica.
- Separate wholesale margin: RECOPE is the only importer and wholesaler; the only distributor margin published (3.746 CRC/L for distributors without a fixed point) is embedded in a with-tax price and was not split out.
- Kerosene import CIF: RECOPE bought no kerosene in 2024.

## Differences above 10 percent from the earlier job (`adders_2024.csv`)

- COA: 21.08 USD/GJ against 5.211 (ASSUMPTION, World Bank South African coal plus 1.0): +305 percent. Costa Rica's only 2024 coal imports were 233 t of anthracite at 562.84 USD/t, a specialty product, not steam coal.
- COK: 3.128 USD/GJ against 3.606 (ASSUMPTION, US petcoke to power plants plus 0.8): minus 13 percent. Observed cement-plant petcoke CIF was 101.67 USD/t in 2024.
- The liquids' wholesale import parity is within 7 percent of the earlier pre-tax values (DSL +4.6, GSL +2.0, JET +2.2, KER +2.2, LPG +3.7, FOI -3.3, AVG +6.0 percent). Causes: the ARESEP purchase densities replace the UN gallons per tonne factors (diesel 0.8356 kg/L against about 0.869), and the exchange rate is 515.11 instead of 518.23. Comparing the new import CIF with the earlier pre-tax value gives larger gaps (JET -16.5, LPG -14.7, FOI -23.5 percent) only because CIF excludes the port cost, trader cost and RECOPE margin K.

## Known-limitation candidates

- `IMPCOA`, PROCOMER HS 270111: 2024 coal imports are 233 t of anthracite at 562.84 USD/t; unit values swing from 344 to 2,993 USD/t between 2018 and 2025 and do not describe steam coal for industry.
- `IMPCOK`, PROCOMER HS 271311: 2024 rests on three monthly records (cargoes); 2018 to 2025 unit values range from 60.89 to 201.42 USD/t.
- `IMPFOI` to `PWRFOI`: ICE burns Bunker Termico ICE 2 (low sulphur); its plantel price is subsidised by about 26 CRC/L under decree 39437-MINAE, so the regulated delivered price is below cost.
- `IMPLPG`: the plantel price for LPG is subsidised (mean 128.46 CRC/L against COA plus K 174.80 CRC/L).
- ARESEP open data purchase service (`ObtenerComprasCombustibleRecope`): the metadata date reads 2023-11-09 although records run to 2026; mass is missing or wrong in some 2022 and 2023 records.

## Left unchecked

- Retail LPG cylinder prices (bottler, distributor and retailer margins) were not converted to a per-GJ consumer price.
- ICE's actual 2024 fuel unit cost: the CVG 2025 liquidation gives 2024 spending (59,197.30 million CRC for January to October) but no litres, so no unit cost was derived.
- Weekly port and airport price bands for Jet A-1, Av-Gas and IFO 380 (separate RECOPE PDFs) were not collected; the national plantel prices were used.
- History for CRC-denominated prices (2018 to 2023 resolutions) was not collected; history covers import CIF from the ARESEP purchase service (2022 to 2025) and PROCOMER coal and petcoke (2018 to 2025).

## Incidents

- BCCR: the Cuadro 1 page is a JavaScript application. Its data service (`apim.bccr.fi.cr`) answers HTTP 500 to direct requests; inspecting the site's code to find what it needs was stopped by the permission system, and the site was not worked around. The WDI annual average was used and the page is on the manual list.
- MINAE (`www.minae.go.cr`) returns a Cloudflare challenge (HTTP 403); `energia.minae.go.cr` and `sepse.go.cr` did not resolve; OLADE's library returned HTTP 403. None were retried with other clients, per the steer on blocked sites.
- RECOPE downloads are slow (about 10 kB/s); the first attempt timed out after 180 s and all files were fetched again with a longer timeout. File sizes match the earlier job's copies.
- The Git Bash `curl` crashed (segmentation fault) on the BCCR host; the Windows `curl.exe` was used for later requests without any user-agent change.
- ARESEP resolution PDFs for the CVG are SharePoint sharing links; they download with a normal cookie-handling client using the published link plus `&download=1`.
