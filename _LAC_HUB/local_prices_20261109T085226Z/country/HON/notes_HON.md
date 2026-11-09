# Honduras (HON) notes, job LAC_LOCAL_PRICES 20261109T085226Z

## Summary

Closed with external, downloaded sources (all values 2024, USD/GJ in `prices_HON.csv`):

- Coal DIST_COA: import CIF 134.00 USD/t, 5.194 USD/GJ (UN Comtrade HS 270112, 27.5 kt). Generator delivered 140.70 USD/t, 5.453 USD/GJ, built from the Comtrade CIF plus the 5% local cost share that the system operator (ODS) uses for a coal plant in its 2026-2035 expansion plan. No longer an ASSUMPTION candidate.
- Petroleum coke DIST_COK: import CIF 81.56 USD/t, 2.509 USD/GJ (UN Comtrade HS 271311, 185.2 kt). No published delivered price. No longer an ASSUMPTION candidate.
- Natural gas DIST_NGS: generator delivered 5.8185 USD/MMBtu, 5.515 USD/GJ gross, built from the ODS published LNG cost chain (Henry Hub x 1.15, liquefaction 2.0, shipping and internacion 0.3, regasification 1.0 USD/MMBtu) and the EIA 2024 Henry Hub average 2.19. Honduras imported no gas in 2024.
- Fuel oil DIST_FOI: CREE real bunker price for generation, 12 months, 73.56 USD/bbl, 12.052 USD/GJ (refetched and confirmed). Import CIF from BCH (76.36 all importers; 76.86 generators' own imports) and SEN (76.46).
- Diesel, gasoline, kerosene: import CIF from BCH (customs based) and SEN annual report; one full SEN/DGHB weekly price structure (27 May to 2 June 2024, published by La Prensa and El Heraldo) giving PPI, wholesale margin, freight, retail margin and tax; CCHAC weekly pre-tax prices for diesel and gasoline extended to 28 weeks (31 Dec 2023 to 3 Aug 2024); CREE quarterly diesel price for generation (forecast, 266.50 USc/gal).
- LPG: CCHAC 25 lb cylinder structure, 25 weeks, every component; BCH and SEN import CIF.
- HON_FX_2024 = 24.7950 HNL/USD (BCH daily Compra mean, 247 days).

Still open:

- Full-year 2024 weekly import parity structure and margins for diesel, gasoline and kerosene (only one week is public). The CCHAC bulletins stop on 3 Aug 2024 and bulletins 9, 14 and 22 were never posted by SEN.
- Delivered coal and petcoke price at the Becosa plant and petcoke price to cement (operator reports sit behind appcnd.enee.hn:3200, which refuses connections).
- National customs (Aduanas, SIECA) source for coal and petcoke CIF (HTTP 403).

Manual list: 9 entries.

## Judgement calls and reasons

- BCH (customs SARAH based) is used as the main import CIF and the SEN annual report as a second row. Volumes agree for diesel but the SEN CIF value is 4.6% higher; BCH is the official trade statistic.
- Gasoline combines superior and regular weighted by BCH 2024 import volumes (superior share 0.5417), because the model has one gasoline row. The earlier job used regular only.
- For 2024 BCH figures the December 2025 report is used (it revises LPG 2024 to 51.26 USD/bbl from 51.56).
- The weekly SEN structure (one week) is converted with the annual BCH rate because the article gives no weekly rate; margins are fixed lempira amounts, so the annual rate is the right basis for them.
- The ODS 5% local cost is applied to coal only, as written; it is not applied to petcoke.
- Natural gas basis is recorded as gross (Henry Hub); the ODS chain components have no stated basis.
- CCHAC bulletins 1, 30 and 31 were read from page images (bulletin 1 text layer gave wrong bar order; 30 and 31 are image-only). In bulletin 30 the regular gasoline pre-tax label is blurred; 2.93 was taken as total 3.76 minus tax 0.83.
- The SEN monthly reports' weekly retail charts were not used: from May to July they print about twice the pump price.
- CREE's diesel price for generation is a quarterly forecast, not a real price; it is recorded as generator delivered with that note.

## Values that could not be sourced externally

None of the recorded values rely on internal files. Not found anywhere public: the weekly PPI structure for all 2024 weeks, a real (not forecast) diesel price for generation, any delivered coal or petcoke price, any 2024 natural gas price in Honduras.

## Differences above 10 percent from the earlier job (`adders_2024.csv`)

- COK: earlier pre-tax 3.606 (EIA US proxy plus 0.8 assumption) vs observed Honduras CIF 2.509 USD/GJ (-30%). Cause: Honduras petcoke CIF (81.56 USD/t) is below the US delivered proxy plus adder.
- NGS: earlier 7.763 vs 5.515 USD/GJ (-29%). Cause: the ODS chain uses fixed liquefaction 2.0, shipping 0.3 and regasification 1.0 USD/MMBtu instead of the observed US export spread plus small-scale shipping.
- DSL pre-tax: earlier 20.445 vs CCHAC 22.830 (+11.7%) and one-week structure 21.914 (+7.2%). Cause: published downstream margins (wholesale 2.17 + freight 1.53 + retail 7.13 HNL/gal, 3.09 USD/GJ) and importer costs inside the PPI exceed the assumed 1.958.
- GSL pre-tax: earlier 20.347 vs CCHAC 25.563 (+25.6%). Cause: published margins near 13.0 HNL/gal (wholesale 3.12, freight 1.53, retail 8.36, volume weighted), superior grade included, Jan to Aug period.
- KER pre-tax: earlier 20.342 vs one-week structure 22.956 (+12.9%). Cause: published margins (9.16 HNL/gal) instead of assumed 1.53 USD/GJ.
- LPG pre-tax: earlier 12.328 vs 19.210 (+56%). Cause: the earlier value added only the importer margin; the full 25 lb cylinder chain adds distributor, land transport, point of sale and cylinder maintenance.
- Import costs (DSL 17.676 vs 18.487, GSL 19.038 vs 18.129, KER 18.866 vs 18.813, FOI 12.052 unchanged, COA 5.194 vs 5.211) are within 10%.

## Known-limitation candidates

- CCHAC Honduras prices are before the 2024 fuel stabilisation subsidy (50% of increases for regular and diesel from mid 2024).
- Fuel for SIN generation is exempt from the ACPV tax (Decreto 100-2020), so generator prices are pre-tax by law.
- Becosa (105 MW) burns coal and petcoke; the SEN balance 2024 reports all petcoke as autoproduction, while the model's DIST_COK also feeds industry.
- First LNG cargo reached Puerto Cortes in 2026 (press), outside the 2024 scope.

## Left unchecked

- OLADE SIELAC conversion factors (manual returned HTTP 403).
- CREE informe trimestral de tarifas pages other than the six adjustment reports and the CBG 2024 review.
- Comtrade 2025 for coal and petcoke (preview API returned HTTP 429 and then no data).

## Incidents

- Mid-task rule change applied: no user-agent spoofing. All downloads used the default curl agent; 403 responses (mem.gob.gt API, aduanas.gob.hn, estadisticas.sieca.int, biblioteca.olade.org, tsc.gob.hn) were logged and not retried.
- appcnd.enee.hn:3200 and gaceta.iaip.gob.hn timed out; ENEE document links returned 404.
- Comtrade preview returned HTTP 429 on rapid queries; retried with backoff.
