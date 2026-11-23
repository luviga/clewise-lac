# REPORT LAC_VEHICLE_PRICES 20261123T163210Z

Pull request: #18 (draft), branch `job/vehicle-prices`, title "LAC_VEHICLE_PRICES: pre-tax vehicle prices from government import statistics (proposals)".

## What this job did

It proposes a pre-tax price per vehicle for each of the 2,892 vehicle CapitalCost cells of CR_ENERGY, RD_ENERGY, GUA_ENERGY, HON_ENERGY and JAM_TRANSPORT (176 technologies). Every base price is an average customs value from government import statistics, or an ASSUMPTION built on such an average under the brief's rules 2 and 3. The NREL ATB price path after the base year is kept from the cost-sources proposals. Nothing in the models changed.

## What the statistics allow

Five countries were searched on all three routes (logs in `<CC>/search_log_<CC>.csv`). The price needs customs value and number of vehicles by line. Only two countries publish both:

- Jamaica: its own reports to UN Comtrade carry vehicle counts for 2019, 2020 and 2021 (CIF in US$). For 2022 and 2023 the counts are UN estimates from weight, so they are not used. No Jamaican file with counts is online; STATIN holds them (manual row M-JAM-1).
- Dominican Republic: the customs office (DGA) publishes vehicle counts and FOB values by vehicle type (cars, jeepetas, cargo vehicles, buses and others) for 2019, 2020 and 2023 in its vehicle bulletins. These price cars, taxis, SUVs, buses and minibuses with combustion engines. The quantities the Dominican Republic reports to UN Comtrade are not vehicle counts (about 2 percent of DGA's count), so they are not used. DGA's transaction tables give FOB by 8-digit line but no quantity.
- Costa Rica, Guatemala and Honduras: PROCOMER, Banguat and BCH publish CIF value by national line with weight in kilograms only. The counts in UN Comtrade for these three countries are UN estimates, not reported counts. Guatemala's SAT and Honduras' customs sites block scripts and the built-in browser with a Cloudflare check; Costa Rica's customs counts need a request form with personal data. No fiscal valuation table could be downloaded as a file (Costa Rica and the Dominican Republic offer one-vehicle lookups only; Guatemala's is behind Cloudflare; none found for Honduras or Jamaica).

So, until the manual files arrive, Costa Rica, Guatemala and Honduras take the average of the same tariff lines in the other four countries (rule 2), which in practice is Jamaica's lines, since the Dominican counts are by vehicle type, not by line. Classes with no line statistic anywhere take the diesel vehicle of the class times the ATB 2022 powertrain ratio (rule 3): electric and fuel cell buses and trucks, fuel cell cars, and hybrid trucks (whose lines exist only from HS 2022).

Values are CIF (FOB for the Dominican bulletins), before import duty, excise and VAT. New and used vehicles are together everywhere: no statistic used separates them. Line-years with fewer than 10 vehicles are left out. Prices are unit-weighted averages over the years available in 2019 to 2023, each year's US$ taken to 2024 US$ with BLS CPI-U factors (2019 1.226992, 2020 1.212039, 2021 1.157652, 2022 1.071873, 2023 1.029494). Every value used is published in US$, so no exchange rate was applied (WDI rates are downloaded for files in local currency).

## Prices per technology

"How" says where the base price comes from. Lines are HS 6-digit codes with the years that entered the average; "Units counted" is the number of vehicles behind the average (for rule 3, behind the diesel price). Sources: COMTRADE-JAM (UN Comtrade, data reported by Jamaica), DR-DGA-2020 and DR-DGA-2024 (DGA vehicle bulletins); GEN-101 (ATB) enters only the ratio and the later-year path.

### CR

| Technology | Class | Powertrain | Price per vehicle (2024 US$) | How | Lines and years used | Units counted | Source |
| --- | --- | --- | ---: | --- | --- | ---: | --- |
| TRNBUSDSL | bus | diesel | 34,139 | ASSUMPTION: same lines, other four countries | JAM 870210 2019-2021 | 1,317 | COMTRADE-JAM |
| TRNBUSELE | bus | battery electric | 69,605 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 2.0389 | 1,317 | COMTRADE-JAM |
| TRNBUSHYBDSL | bus | hybrid diesel | 15,358 | ASSUMPTION: same lines, other four countries | JAM 870220 2019-2020 | 33 | COMTRADE-JAM |
| TRNBUSHYD | bus | fuel cell | 62,013 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 1.8165 | 1,317 | COMTRADE-JAM |
| TRNBUSLPG | bus | LPG | 14,954 | ASSUMPTION: same lines, other four countries | JAM 870290 2019-2021 | 445 | COMTRADE-JAM |
| TRNFREHEADSL | heavy truck | diesel | 17,904 | ASSUMPTION: same lines, other four countries | JAM 870422 2019-2021, JAM 870423 2019-2021 | 5,691 | COMTRADE-JAM |
| TRNFREHEAELE | heavy truck | battery electric | 36,503 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 2.0389 | 5,691 | COMTRADE-JAM |
| TRNFREHEAHYBDSL | heavy truck | hybrid diesel | 19,240 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 1.0747 | 5,691 | COMTRADE-JAM |
| TRNFREHEAHYD | heavy truck | fuel cell | 32,522 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 1.8165 | 5,691 | COMTRADE-JAM |
| TRNFREHEALPG | heavy truck | LPG | 12,122 | ASSUMPTION: same lines, other four countries | JAM 870432 2019-2021 | 22 | COMTRADE-JAM |
| TRNFREHEANGV | heavy truck | natural gas | 12,122 | ASSUMPTION: same lines, other four countries | JAM 870432 2019-2021 | 22 | COMTRADE-JAM |
| TRNFRELIGDSL | pickup or light truck | diesel | 18,953 | ASSUMPTION: same lines, other four countries | JAM 870421 2019-2021 | 5,874 | COMTRADE-JAM |
| TRNFRELIGELE | pickup or light truck | battery electric | 23,083 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.2179 | 5,874 | COMTRADE-JAM |
| TRNFRELIGGSL | pickup or light truck | gasoline | 9,954 | ASSUMPTION: same lines, other four countries | JAM 870431 2019-2021 | 3,509 | COMTRADE-JAM |
| TRNFRELIGHYBDSL | pickup or light truck | hybrid diesel | 19,202 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.0131 | 5,874 | COMTRADE-JAM |
| TRNFRELIGHYBGSL | pickup or light truck | hybrid gasoline | 19,202 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.0131 | 5,874 | COMTRADE-JAM |
| TRNFRELIGLPG | pickup or light truck | LPG | 9,954 | ASSUMPTION: same lines, other four countries | JAM 870431 2019-2021 | 3,509 | COMTRADE-JAM |
| TRNMICDSL | minibus | diesel | 34,139 | ASSUMPTION: same lines, other four countries | JAM 870210 2019-2021 | 1,317 | COMTRADE-JAM |
| TRNMICELE | minibus | battery electric | 44,390 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 1.3003 | 1,317 | COMTRADE-JAM |
| TRNMICHYBDSL | minibus | hybrid diesel | 15,358 | ASSUMPTION: same lines, other four countries | JAM 870220 2019-2020 | 33 | COMTRADE-JAM |
| TRNMICHYD | minibus | fuel cell | 55,808 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 1.6347 | 1,317 | COMTRADE-JAM |
| TRNMICLPG | minibus | LPG | 14,954 | ASSUMPTION: same lines, other four countries | JAM 870290 2019-2021 | 445 | COMTRADE-JAM |
| TRNMOTELE | motorcycle | battery electric | 1,297 | ASSUMPTION: same lines, other four countries | JAM 871160 2019-2021 | 113 | COMTRADE-JAM |
| TRNMOTGSL | motorcycle | gasoline | 527 | ASSUMPTION: same lines, other four countries | JAM 871110 2020-2020, JAM 871120 2019-2021, JAM 871130 2019-2021, JAM 871140 2019-2021, JAM 871150 2019-2021 | 19,844 | COMTRADE-JAM |
| TRNSEDDSL | car | diesel | 22,091 | ASSUMPTION: same lines, other four countries | JAM 870331 2019-2021, JAM 870332 2019-2020 | 1,164 | COMTRADE-JAM |
| TRNSEDELE | car | battery electric | 14,221 | ASSUMPTION: same lines, other four countries | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRNSEDGSL | car | gasoline | 8,540 | ASSUMPTION: same lines, other four countries | JAM 870321 2019-2021, JAM 870322 2019-2021, JAM 870323 2019-2021 | 106,255 | COMTRADE-JAM |
| TRNSEDHYBGSL | car | hybrid gasoline | 11,221 | ASSUMPTION: same lines, other four countries | JAM 870340 2019-2021 | 5,819 | COMTRADE-JAM |
| TRNSEDLPG | car | LPG | 8,540 | ASSUMPTION: same lines, other four countries | JAM 870321 2019-2021, JAM 870322 2019-2021, JAM 870323 2019-2021 | 106,255 | COMTRADE-JAM |
| TRNSUVDSL | SUV | diesel | 33,613 | ASSUMPTION: same lines, other four countries | JAM 870332 2019-2020, JAM 870333 2019-2021 | 2,059 | COMTRADE-JAM |
| TRNSUVELE | SUV | battery electric | 14,221 | ASSUMPTION: same lines, other four countries | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRNSUVGSL | SUV | gasoline | 10,549 | ASSUMPTION: same lines, other four countries | JAM 870323 2019-2021, JAM 870324 2019-2021 | 56,049 | COMTRADE-JAM |
| TRNSUVHYBDSL | SUV | hybrid diesel | 32,351 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870332 2019-2020, JAM 870333 2019-2021; ATB ratio 0.9625 | 2,059 | COMTRADE-JAM |
| TRNSUVHYBGSL | SUV | hybrid gasoline | 11,221 | ASSUMPTION: same lines, other four countries | JAM 870340 2019-2021 | 5,819 | COMTRADE-JAM |
| TRNSUVLPG | SUV | LPG | 10,549 | ASSUMPTION: same lines, other four countries | JAM 870323 2019-2021, JAM 870324 2019-2021 | 56,049 | COMTRADE-JAM |
| TRNTAXDSL | taxi | diesel | 22,091 | ASSUMPTION: same lines, other four countries | JAM 870331 2019-2021, JAM 870332 2019-2020 | 1,164 | COMTRADE-JAM |
| TRNTAXELE | taxi | battery electric | 14,221 | ASSUMPTION: same lines, other four countries | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRNTAXGSL | taxi | gasoline | 8,540 | ASSUMPTION: same lines, other four countries | JAM 870321 2019-2021, JAM 870322 2019-2021, JAM 870323 2019-2021 | 106,255 | COMTRADE-JAM |
| TRNTAXHYBDSL | taxi | hybrid diesel | 19,774 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870331 2019-2021, JAM 870332 2019-2020; ATB ratio 0.8951 | 1,164 | COMTRADE-JAM |
| TRNTAXHYBGSL | taxi | hybrid gasoline | 11,221 | ASSUMPTION: same lines, other four countries | JAM 870340 2019-2021 | 5,819 | COMTRADE-JAM |

### DR

| Technology | Class | Powertrain | Price per vehicle (2024 US$) | How | Lines and years used | Units counted | Source |
| --- | --- | --- | ---: | --- | --- | ---: | --- |
| TRAUTDSL | car | diesel | 6,574 | own customs counts by vehicle type | DR Automóviles 2019-2023 | 132,128 | DR-DGA-2020, DR-DGA-2024 |
| TRAUTELE | car | battery electric | 14,221 | ASSUMPTION: same lines, other four countries | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRAUTGSL | car | gasoline | 6,574 | own customs counts by vehicle type | DR Automóviles 2019-2023 | 132,128 | DR-DGA-2020, DR-DGA-2024 |
| TRAUTHG | car | hybrid gasoline | 11,221 | ASSUMPTION: same lines, other four countries | JAM 870340 2019-2021 | 5,819 | COMTRADE-JAM |
| TRAUTLPG | car | LPG | 6,574 | own customs counts by vehicle type | DR Automóviles 2019-2023 | 132,128 | DR-DGA-2020, DR-DGA-2024 |
| TRBPUDSL | bus | diesel | 27,483 | own customs counts by vehicle type | DR Autobuses 2019-2023 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRBPUELE | bus | battery electric | 56,034 | ASSUMPTION: diesel of the class x ATB ratio | DR Autobuses 2019-2023; ATB ratio 2.0389 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRBPUGSL | bus | gasoline | 27,483 | own customs counts by vehicle type | DR Autobuses 2019-2023 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRBPUHYD | bus | fuel cell | 49,922 | ASSUMPTION: diesel of the class x ATB ratio | DR Autobuses 2019-2023; ATB ratio 1.8165 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRBPULPG | bus | LPG | 27,483 | own customs counts by vehicle type | DR Autobuses 2019-2023 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRBTURDSL | bus | diesel | 27,483 | own customs counts by vehicle type | DR Autobuses 2019-2023 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRBTURELE | bus | battery electric | 56,034 | ASSUMPTION: diesel of the class x ATB ratio | DR Autobuses 2019-2023; ATB ratio 2.0389 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRBTURGSL | bus | gasoline | 27,483 | own customs counts by vehicle type | DR Autobuses 2019-2023 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRBTURHYD | bus | fuel cell | 49,922 | ASSUMPTION: diesel of the class x ATB ratio | DR Autobuses 2019-2023; ATB ratio 1.8165 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRBTURLPG | bus | LPG | 27,483 | own customs counts by vehicle type | DR Autobuses 2019-2023 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRMBSDSL | minibus | diesel | 27,483 | own customs counts by vehicle type | DR Autobuses 2019-2023 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRMBSELE | minibus | battery electric | 35,736 | ASSUMPTION: diesel of the class x ATB ratio | DR Autobuses 2019-2023; ATB ratio 1.3003 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRMBSGSL | minibus | gasoline | 27,483 | own customs counts by vehicle type | DR Autobuses 2019-2023 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRMBSLPG | minibus | LPG | 27,483 | own customs counts by vehicle type | DR Autobuses 2019-2023 | 6,032 | DR-DGA-2020, DR-DGA-2024 |
| TRMOTELE | motorcycle | battery electric | 1,297 | ASSUMPTION: same lines, other four countries | JAM 871160 2019-2021 | 113 | COMTRADE-JAM |
| TRMOTGSL | motorcycle | gasoline | 527 | ASSUMPTION: same lines, other four countries | JAM 871110 2020-2020, JAM 871120 2019-2021, JAM 871130 2019-2021, JAM 871140 2019-2021, JAM 871150 2019-2021 | 19,844 | COMTRADE-JAM |
| TRSUVDSL | SUV | diesel | 18,664 | own customs counts by vehicle type | DR Jeepetas 2019-2023 | 138,069 | DR-DGA-2020, DR-DGA-2024 |
| TRSUVELE | SUV | battery electric | 14,221 | ASSUMPTION: same lines, other four countries | JAM 870380 2020-2021 | 54 | COMTRADE-JAM, DR-DGA-2020, DR-DGA-2024 |
| TRSUVGSL | SUV | gasoline | 18,664 | own customs counts by vehicle type | DR Jeepetas 2019-2023 | 138,069 | DR-DGA-2020, DR-DGA-2024 |
| TRSUVLPG | SUV | LPG | 18,664 | own customs counts by vehicle type | DR Jeepetas 2019-2023 | 138,069 | DR-DGA-2020, DR-DGA-2024 |
| TRSUVNGS | SUV | natural gas | 18,664 | own customs counts by vehicle type | DR Jeepetas 2019-2023 | 138,069 | DR-DGA-2020, DR-DGA-2024 |
| TRTAXELE | taxi | battery electric | 14,221 | ASSUMPTION: same lines, other four countries | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRTAXGSL | taxi | gasoline | 6,574 | own customs counts by vehicle type | DR Automóviles 2019-2023 | 132,128 | DR-DGA-2020, DR-DGA-2024 |
| TRTAXLPG | taxi | LPG | 6,574 | own customs counts by vehicle type | DR Automóviles 2019-2023 | 132,128 | DR-DGA-2020, DR-DGA-2024 |
| TRYLFDSL | pickup or light truck | diesel | 18,953 | ASSUMPTION: same lines, other four countries | JAM 870421 2019-2021 | 5,874 | COMTRADE-JAM |
| TRYLFELE | pickup or light truck | battery electric | 23,083 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.2179 | 5,874 | COMTRADE-JAM |
| TRYLFGSL | pickup or light truck | gasoline | 9,954 | ASSUMPTION: same lines, other four countries | JAM 870431 2019-2021 | 3,509 | COMTRADE-JAM |
| TRYLFHD | pickup or light truck | hybrid diesel | 19,202 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.0131 | 5,874 | COMTRADE-JAM |
| TRYLFLPG | pickup or light truck | LPG | 9,954 | ASSUMPTION: same lines, other four countries | JAM 870431 2019-2021 | 3,509 | COMTRADE-JAM |
| TRYLFNGS | pickup or light truck | natural gas | 9,954 | ASSUMPTION: same lines, other four countries | JAM 870431 2019-2021 | 3,509 | COMTRADE-JAM |
| TRYTKDSL | heavy truck | diesel | 17,904 | ASSUMPTION: same lines, other four countries | JAM 870422 2019-2021, JAM 870423 2019-2021 | 5,691 | COMTRADE-JAM |
| TRYTKELE | heavy truck | battery electric | 36,503 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 2.0389 | 5,691 | COMTRADE-JAM |
| TRYTKGSL | heavy truck | gasoline | 12,122 | ASSUMPTION: same lines, other four countries | JAM 870432 2019-2021 | 22 | COMTRADE-JAM |
| TRYTKHD | heavy truck | hybrid diesel | 19,240 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 1.0747 | 5,691 | COMTRADE-JAM |
| TRYTKHYD | heavy truck | fuel cell | 32,522 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 1.8165 | 5,691 | COMTRADE-JAM |
| TRYTKLPG | heavy truck | LPG | 12,122 | ASSUMPTION: same lines, other four countries | JAM 870432 2019-2021 | 22 | COMTRADE-JAM |

### GUA

| Technology | Class | Powertrain | Price per vehicle (2024 US$) | How | Lines and years used | Units counted | Source |
| --- | --- | --- | ---: | --- | --- | ---: | --- |
| TRAUTDSL | car | diesel | 22,091 | ASSUMPTION: same lines, other four countries | JAM 870331 2019-2021, JAM 870332 2019-2020 | 1,164 | COMTRADE-JAM |
| TRAUTELE | car | battery electric | 14,221 | ASSUMPTION: same lines, other four countries | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRAUTFlex_Fuel | car | gasoline (flex fuel) | 8,540 | ASSUMPTION: same lines, other four countries | JAM 870321 2019-2021, JAM 870322 2019-2021, JAM 870323 2019-2021 | 106,255 | COMTRADE-JAM |
| TRAUTGSL | car | gasoline | 8,540 | ASSUMPTION: same lines, other four countries | JAM 870321 2019-2021, JAM 870322 2019-2021, JAM 870323 2019-2021 | 106,255 | COMTRADE-JAM |
| TRAUTHG | car | hybrid gasoline | 11,221 | ASSUMPTION: same lines, other four countries | JAM 870340 2019-2021 | 5,819 | COMTRADE-JAM |
| TRAUTLPG | car | LPG | 8,540 | ASSUMPTION: same lines, other four countries | JAM 870321 2019-2021, JAM 870322 2019-2021, JAM 870323 2019-2021 | 106,255 | COMTRADE-JAM |
| TRAUTPHG | car | plug-in hybrid gasoline | 9,523 | ASSUMPTION: same lines, other four countries | JAM 870360 2019-2021 | 244 | COMTRADE-JAM |
| TRBPRDSL | bus | diesel | 34,139 | ASSUMPTION: same lines, other four countries | JAM 870210 2019-2021 | 1,317 | COMTRADE-JAM |
| TRBPRELE | bus | battery electric | 69,605 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 2.0389 | 1,317 | COMTRADE-JAM |
| TRBPRHYD | bus | fuel cell | 62,013 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 1.8165 | 1,317 | COMTRADE-JAM |
| TRBPRLPG | bus | LPG | 14,954 | ASSUMPTION: same lines, other four countries | JAM 870290 2019-2021 | 445 | COMTRADE-JAM |
| TRBPRPHD | bus | plug-in hybrid diesel | 15,358 | ASSUMPTION: same lines, other four countries | JAM 870220 2019-2020 | 33 | COMTRADE-JAM |
| TRBPUDSL | bus | diesel | 34,139 | ASSUMPTION: same lines, other four countries | JAM 870210 2019-2021 | 1,317 | COMTRADE-JAM |
| TRBPUELE | bus | battery electric | 69,605 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 2.0389 | 1,317 | COMTRADE-JAM |
| TRBPUHYD | bus | fuel cell | 62,013 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 1.8165 | 1,317 | COMTRADE-JAM |
| TRBPULPG | bus | LPG | 14,954 | ASSUMPTION: same lines, other four countries | JAM 870290 2019-2021 | 445 | COMTRADE-JAM |
| TRBPUPHD | bus | plug-in hybrid diesel | 15,358 | ASSUMPTION: same lines, other four countries | JAM 870220 2019-2020 | 33 | COMTRADE-JAM |
| TRMBSDSL | minibus | diesel | 34,139 | ASSUMPTION: same lines, other four countries | JAM 870210 2019-2021 | 1,317 | COMTRADE-JAM |
| TRMBSELE | minibus | battery electric | 44,390 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 1.3003 | 1,317 | COMTRADE-JAM |
| TRMBSGSL | minibus | gasoline | 14,954 | ASSUMPTION: same lines, other four countries | JAM 870290 2019-2021 | 445 | COMTRADE-JAM |
| TRMBSHYD | minibus | fuel cell | 55,808 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 1.6347 | 1,317 | COMTRADE-JAM |
| TRMBSLPG | minibus | LPG | 14,954 | ASSUMPTION: same lines, other four countries | JAM 870290 2019-2021 | 445 | COMTRADE-JAM |
| TRMBSPHD | minibus | plug-in hybrid diesel | 15,358 | ASSUMPTION: same lines, other four countries | JAM 870220 2019-2020 | 33 | COMTRADE-JAM |
| TRMOTELE | motorcycle | battery electric | 1,297 | ASSUMPTION: same lines, other four countries | JAM 871160 2019-2021 | 113 | COMTRADE-JAM |
| TRMOTFlex_Fuel | motorcycle | gasoline (flex fuel) | 527 | ASSUMPTION: same lines, other four countries | JAM 871110 2020-2020, JAM 871120 2019-2021, JAM 871130 2019-2021, JAM 871140 2019-2021, JAM 871150 2019-2021 | 19,844 | COMTRADE-JAM |
| TRMOTGSL | motorcycle | gasoline | 527 | ASSUMPTION: same lines, other four countries | JAM 871110 2020-2020, JAM 871120 2019-2021, JAM 871130 2019-2021, JAM 871140 2019-2021, JAM 871150 2019-2021 | 19,844 | COMTRADE-JAM |
| TRYLFDSL | pickup or light truck | diesel | 18,953 | ASSUMPTION: same lines, other four countries | JAM 870421 2019-2021 | 5,874 | COMTRADE-JAM |
| TRYLFELE | pickup or light truck | battery electric | 23,083 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.2179 | 5,874 | COMTRADE-JAM |
| TRYLFGSL | pickup or light truck | gasoline | 9,954 | ASSUMPTION: same lines, other four countries | JAM 870431 2019-2021 | 3,509 | COMTRADE-JAM |
| TRYLFHD | pickup or light truck | hybrid diesel | 19,202 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.0131 | 5,874 | COMTRADE-JAM |
| TRYLFLPG | pickup or light truck | LPG | 9,954 | ASSUMPTION: same lines, other four countries | JAM 870431 2019-2021 | 3,509 | COMTRADE-JAM |
| TRYLFPHD | pickup or light truck | plug-in hybrid diesel | 21,350 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.1265 | 5,874 | COMTRADE-JAM |
| TRYTKDSL | heavy truck | diesel | 17,904 | ASSUMPTION: same lines, other four countries | JAM 870422 2019-2021, JAM 870423 2019-2021 | 5,691 | COMTRADE-JAM |
| TRYTKELE | heavy truck | battery electric | 36,503 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 2.0389 | 5,691 | COMTRADE-JAM |
| TRYTKHD | heavy truck | hybrid diesel | 19,240 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 1.0747 | 5,691 | COMTRADE-JAM |
| TRYTKHYD | heavy truck | fuel cell | 32,522 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 1.8165 | 5,691 | COMTRADE-JAM |
| TRYTKLPG | heavy truck | LPG | 12,122 | ASSUMPTION: same lines, other four countries | JAM 870432 2019-2021 | 22 | COMTRADE-JAM |
| TRYTKPHD | heavy truck | plug-in hybrid diesel | 28,345 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 1.5832 | 5,691 | COMTRADE-JAM |

### HON

| Technology | Class | Powertrain | Price per vehicle (2024 US$) | How | Lines and years used | Units counted | Source |
| --- | --- | --- | ---: | --- | --- | ---: | --- |
| TRAUTDSL | car | diesel | 22,091 | ASSUMPTION: same lines, other four countries | JAM 870331 2019-2021, JAM 870332 2019-2020 | 1,164 | COMTRADE-JAM |
| TRAUTELE | car | battery electric | 14,221 | ASSUMPTION: same lines, other four countries | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRAUTGSL | car | gasoline | 8,540 | ASSUMPTION: same lines, other four countries | JAM 870321 2019-2021, JAM 870322 2019-2021, JAM 870323 2019-2021 | 106,255 | COMTRADE-JAM |
| TRAUTHG | car | hybrid gasoline | 11,221 | ASSUMPTION: same lines, other four countries | JAM 870340 2019-2021 | 5,819 | COMTRADE-JAM |
| TRBPUDSL | bus | diesel | 34,139 | ASSUMPTION: same lines, other four countries | JAM 870210 2019-2021 | 1,317 | COMTRADE-JAM |
| TRBPUELE | bus | battery electric | 69,605 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 2.0389 | 1,317 | COMTRADE-JAM |
| TRBPUGSL | bus | gasoline | 14,954 | ASSUMPTION: same lines, other four countries | JAM 870290 2019-2021 | 445 | COMTRADE-JAM |
| TRBPUHYD | bus | fuel cell | 62,013 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 1.8165 | 1,317 | COMTRADE-JAM |
| TRBTURDSL | bus | diesel | 34,139 | ASSUMPTION: same lines, other four countries | JAM 870210 2019-2021 | 1,317 | COMTRADE-JAM |
| TRBTURELE | bus | battery electric | 69,605 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 2.0389 | 1,317 | COMTRADE-JAM |
| TRBTURGSL | bus | gasoline | 14,954 | ASSUMPTION: same lines, other four countries | JAM 870290 2019-2021 | 445 | COMTRADE-JAM |
| TRMBSDSL | minibus | diesel | 34,139 | ASSUMPTION: same lines, other four countries | JAM 870210 2019-2021 | 1,317 | COMTRADE-JAM |
| TRMBSELE | minibus | battery electric | 44,390 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 1.3003 | 1,317 | COMTRADE-JAM |
| TRMBSGSL | minibus | gasoline | 14,954 | ASSUMPTION: same lines, other four countries | JAM 870290 2019-2021 | 445 | COMTRADE-JAM |
| TRMOTELE | motorcycle | battery electric | 1,297 | ASSUMPTION: same lines, other four countries | JAM 871160 2019-2021 | 113 | COMTRADE-JAM |
| TRMOTGSL | motorcycle | gasoline | 527 | ASSUMPTION: same lines, other four countries | JAM 871110 2020-2020, JAM 871120 2019-2021, JAM 871130 2019-2021, JAM 871140 2019-2021, JAM 871150 2019-2021 | 19,844 | COMTRADE-JAM |
| TRSUVDSL | SUV | diesel | 22,758 | ASSUMPTION: same lines, other four countries | JAM 870332 2019-2020, JAM 870333 2019-2021, JAM 870421 2019-2021 | 7,933 | COMTRADE-JAM |
| TRSUVELE | SUV | battery electric | 14,221 | ASSUMPTION: same lines, other four countries | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRSUVGSL | SUV | gasoline | 10,514 | ASSUMPTION: same lines, other four countries | JAM 870323 2019-2021, JAM 870324 2019-2021, JAM 870431 2019-2021 | 59,558 | COMTRADE-JAM |
| TRTAXELE | taxi | battery electric | 14,221 | ASSUMPTION: same lines, other four countries | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRTAXGSL | taxi | gasoline | 8,540 | ASSUMPTION: same lines, other four countries | JAM 870321 2019-2021, JAM 870322 2019-2021, JAM 870323 2019-2021 | 106,255 | COMTRADE-JAM |
| TRTAXLPG | taxi | LPG | 8,540 | ASSUMPTION: same lines, other four countries | JAM 870321 2019-2021, JAM 870322 2019-2021, JAM 870323 2019-2021 | 106,255 | COMTRADE-JAM |
| TRYLFDSL | pickup or light truck | diesel | 18,953 | ASSUMPTION: same lines, other four countries | JAM 870421 2019-2021 | 5,874 | COMTRADE-JAM |
| TRYLFELE | pickup or light truck | battery electric | 23,083 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.2179 | 5,874 | COMTRADE-JAM |
| TRYLFGSL | pickup or light truck | gasoline | 9,954 | ASSUMPTION: same lines, other four countries | JAM 870431 2019-2021 | 3,509 | COMTRADE-JAM |
| TRYLFHD | pickup or light truck | hybrid diesel | 19,202 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.0131 | 5,874 | COMTRADE-JAM |
| TRYTKDSL | heavy truck | diesel | 17,904 | ASSUMPTION: same lines, other four countries | JAM 870422 2019-2021, JAM 870423 2019-2021 | 5,691 | COMTRADE-JAM |
| TRYTKELE | heavy truck | battery electric | 36,503 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 2.0389 | 5,691 | COMTRADE-JAM |
| TRYTKHD | heavy truck | hybrid diesel | 19,240 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 1.0747 | 5,691 | COMTRADE-JAM |
| TRYTKHYD | heavy truck | fuel cell | 32,522 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 1.8165 | 5,691 | COMTRADE-JAM |

### JAM

| Technology | Class | Powertrain | Price per vehicle (2024 US$) | How | Lines and years used | Units counted | Source |
| --- | --- | --- | ---: | --- | --- | ---: | --- |
| TRAUTDSL | car | diesel | 22,091 | own tariff lines | JAM 870331 2019-2021, JAM 870332 2019-2020 | 1,164 | COMTRADE-JAM |
| TRAUTELE | car | battery electric | 14,221 | own tariff lines | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRAUTGSL | car | gasoline | 8,540 | own tariff lines | JAM 870321 2019-2021, JAM 870322 2019-2021, JAM 870323 2019-2021 | 106,255 | COMTRADE-JAM |
| TRAUTHG | car | hybrid gasoline | 11,221 | own tariff lines | JAM 870340 2019-2021 | 5,819 | COMTRADE-JAM |
| TRBPUDSL | bus | diesel | 34,139 | own tariff lines | JAM 870210 2019-2021 | 1,317 | COMTRADE-JAM |
| TRBPUELE | bus | battery electric | 69,605 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 2.0389 | 1,317 | COMTRADE-JAM |
| TRBPUGSL | bus | gasoline | 14,954 | own tariff lines | JAM 870290 2019-2021 | 445 | COMTRADE-JAM |
| TRBPUHYD | bus | fuel cell | 62,013 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 1.8165 | 1,317 | COMTRADE-JAM |
| TRMBSDSL | minibus | diesel | 34,139 | own tariff lines | JAM 870210 2019-2021 | 1,317 | COMTRADE-JAM |
| TRMBSELE | minibus | battery electric | 44,390 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870210 2019-2021; ATB ratio 1.3003 | 1,317 | COMTRADE-JAM |
| TRMBSGSL | minibus | gasoline | 14,954 | own tariff lines | JAM 870290 2019-2021 | 445 | COMTRADE-JAM |
| TRMOTELE | motorcycle | battery electric | 1,297 | own tariff lines | JAM 871160 2019-2021 | 113 | COMTRADE-JAM |
| TRMOTGSL | motorcycle | gasoline | 527 | own tariff lines | JAM 871110 2020-2020, JAM 871120 2019-2021, JAM 871130 2019-2021, JAM 871140 2019-2021, JAM 871150 2019-2021 | 19,844 | COMTRADE-JAM |
| TRSUVDSL | SUV | diesel | 22,758 | own tariff lines | JAM 870332 2019-2020, JAM 870333 2019-2021, JAM 870421 2019-2021 | 7,933 | COMTRADE-JAM |
| TRSUVELE | SUV | battery electric | 14,221 | own tariff lines | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRSUVGSL | SUV | gasoline | 10,514 | own tariff lines | JAM 870323 2019-2021, JAM 870324 2019-2021, JAM 870431 2019-2021 | 59,558 | COMTRADE-JAM |
| TRTAXELE | taxi | battery electric | 14,221 | own tariff lines | JAM 870380 2020-2021 | 54 | COMTRADE-JAM |
| TRTAXGSL | taxi | gasoline | 8,540 | own tariff lines | JAM 870321 2019-2021, JAM 870322 2019-2021, JAM 870323 2019-2021 | 106,255 | COMTRADE-JAM |
| TRYLFDSL | pickup or light truck | diesel | 18,953 | own tariff lines | JAM 870421 2019-2021 | 5,874 | COMTRADE-JAM |
| TRYLFELE | pickup or light truck | battery electric | 23,083 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.2179 | 5,874 | COMTRADE-JAM |
| TRYLFGSL | pickup or light truck | gasoline | 9,954 | own tariff lines | JAM 870431 2019-2021 | 3,509 | COMTRADE-JAM |
| TRYLFHD | pickup or light truck | hybrid diesel | 19,202 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870421 2019-2021; ATB ratio 1.0131 | 5,874 | COMTRADE-JAM |
| TRYTKDSL | heavy truck | diesel | 17,904 | own tariff lines | JAM 870422 2019-2021, JAM 870423 2019-2021 | 5,691 | COMTRADE-JAM |
| TRYTKELE | heavy truck | battery electric | 36,503 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 2.0389 | 5,691 | COMTRADE-JAM |
| TRYTKHD | heavy truck | hybrid diesel | 19,240 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 1.0747 | 5,691 | COMTRADE-JAM |
| TRYTKHYD | heavy truck | fuel cell | 32,522 | ASSUMPTION: diesel of the class x ATB ratio | JAM 870422 2019-2021, JAM 870423 2019-2021; ATB ratio 1.8165 | 5,691 | COMTRADE-JAM |

### Ten largest changes

| Country | Technology | Base-year cell | Current price per vehicle (US$) | Proposed (2024 US$) | km per vehicle-year | Current compiled (M US$ per Gvkm) | Proposed compiled (M US$ per Gvkm) | Factor |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DR | TRYLFNGS | 2018 | 305,082,814.22 | 9,954.32 | 9,000 | 33,898,090.4694 | 1,106.0351 | 30,648.3 |
| GUA | TRAUTHG | 2018 | 2.04 | 11,221.18 | 19,220 | 0.1063 | 583.8283 | 5,494.0 |
| GUA | TRAUTPHG | 2018 | 2.04 | 9,523.01 | 19,220 | 0.1063 | 495.4740 | 4,662.6 |
| CR | TRNTAXDSL | 2024 | 248.98 | 22,091.46 | 46,880 | 5.3110 | 471.2342 | 88.7 |
| CR | TRNMICELE | 2024 | 841.99 | 44,390.48 | 32,843 | 25.6367 | 1,351.5964 | 52.7 |
| CR | TRNMICDSL | 2024 | 694.37 | 34,138.96 | 32,843 | 21.1421 | 1,039.4592 | 49.2 |
| CR | TRNTAXHYBDSL | 2024 | 429.09 | 19,774.18 | 46,880 | 9.1530 | 421.8042 | 46.1 |
| CR | TRNTAXGSL | 2024 | 248.98 | 8,539.76 | 46,880 | 5.3110 | 182.1621 | 34.3 |
| CR | TRNTAXELE | 2024 | 473.00 | 14,220.83 | 46,880 | 10.0896 | 303.3453 | 30.1 |
| CR | TRNSEDDSL | 2024 | 820.85 | 22,091.46 | 12,095 | 67.8668 | 1,826.4952 | 26.9 |

### Counts by class

| Class | How | Technologies |
| --- | --- | ---: |
| SUV | ASSUMPTION | 10 |
| SUV | own customs counts by vehicle type | 4 |
| SUV | own tariff lines | 3 |
| bus | ASSUMPTION | 28 |
| bus | own customs counts by vehicle type | 6 |
| bus | own tariff lines | 2 |
| car | ASSUMPTION | 18 |
| car | own customs counts by vehicle type | 3 |
| car | own tariff lines | 4 |
| heavy truck | ASSUMPTION | 25 |
| heavy truck | own tariff lines | 1 |
| minibus | ASSUMPTION | 16 |
| minibus | own customs counts by vehicle type | 3 |
| minibus | own tariff lines | 2 |
| motorcycle | ASSUMPTION | 9 |
| motorcycle | own tariff lines | 2 |
| pickup or light truck | ASSUMPTION | 24 |
| pickup or light truck | own tariff lines | 2 |
| taxi | ASSUMPTION | 9 |
| taxi | own customs counts by vehicle type | 2 |
| taxi | own tariff lines | 2 |

The largest changes are the three cells the hub found broken and the Costa Rica cells, whose current values are in another unit. Dominican `TRYLFNGS` held a price in a "Relative to" cell; it becomes the ratio of the gasoline (spark-ignition) to the diesel light-truck statistic. Guatemala `TRAUTHG` and `TRAUTPHG` pointed at a ratio; they become ratios to `TRAUTDSL` with `unit_introduced_proposed` "Relative to TRAUTDSL". The compiled values use the model's current base-year distance per vehicle (as checked by the cost-sources job) and 1000 x price / km.

## Change classes per country

| Country | Cells | confirmed | replace | assumption |
| --- | ---: | ---: | ---: | ---: |
| CR | 1,201 | 0 | 0 | 1,201 |
| DR | 425 | 311 | 11 | 103 |
| GUA | 518 | 359 | 0 | 159 |
| HON | 382 | 280 | 0 | 102 |
| JAM | 366 | 294 | 16 | 56 |

`confirmed` means within 25 percent of the current cell; Costa Rica is never confirmed because its unit changes. `assumption` rows carry an ASSUMPTION sentence: rule 2, rule 3, or (for every later-year multiplier and every Costa Rica year other than 2024) the ATB price path, which no government statistic gives. Only 36 rows rest on a country's own statistic with no assumption: 18 Dominican base-year cells from the DGA counts and 18 Jamaican base-year cells from its own lines.

## Rows that wait on manual files

`manual_downloads.csv` lists six items. Until they arrive the rows hold the values above.

| Item | Country | What | Rows waiting | Held until then |
| --- | --- | --- | --- | --- |
| M-GUA-1 | GUA | GUA_SAT_importacion_vehiculos_<year>.xlsx | All 518 Guatemala cells (38 technologies). | Jamaica's average customs value of the same tariff lines (rule 2), or the diesel vehicle of the class times the ATB powertrain ratio (rule 3). |
| M-GUA-2 | GUA | GUA_SAT_tabla_valores_imponibles_<year>.pdf | Guatemala classes that M-GUA-1 cannot price. | As for M-GUA-1. |
| M-DR-1 | DR | ONE_BD_IMP_<year>.xlsx | The 242 Dominican cells priced from other countries' lines or the ATB ratio, and the 183 cells priced from DGA counts by vehicle type (which would move to tariff lines). | DGA vehicle-type counts for cars, SUVs and buses (FOB, all fuels); Jamaica's lines (rule 2) or rule 3 for the rest. |
| M-CR-1 | CR | CR_DGA_import_units_<year>.xlsx (or one file for 2019_2023 with a year column) | All 1,200 Costa Rica vehicle cells (40 technologies); the rail cell is out of scope. | Jamaica's average customs value of the same tariff lines (rule 2) or rule 3, times the ATB ratio of each year. |
| M-HON-1 | HON | HON_Aduanas_import_units_<year>.xlsx | All 382 Honduras cells (30 technologies). | Jamaica's average customs value of the same tariff lines (rule 2) or rule 3. |
| M-JAM-1 | JAM | STATIN_imports_8702_8703_8704_8711_10digit_2019_2023.xlsx | The 212 Jamaica cells priced by rule 3 (electric and fuel cell buses and trucks, hybrid trucks), and every Jamaica class through 2022 and 2023 data. | Jamaica's lines 2019 to 2021 as reported to UN Comtrade; rule 3 where those lines hold too few vehicles. |

## Gates

| Gate | Result | Detail |
| --- | --- | --- |
| 1 Coverage | PASS | 2892 proposal rows for 2892 cells in scope (expected 2892); missing 0, duplicate 0, extra 0 |
| 2 Current values | PASS | 2892 cells read from the workbooks of the checked-out tree; 0 differ |
| 3 Source type | PASS | 36 non-ASSUMPTION rows; 0 cite a source of another type |
| 4 Recompute | PASS | clean run reproduces the class prices of all five countries; 175 base-year cells checked; 0 differ |
| 5 Files | PASS | 50 downloaded files named in the sources files; 0 missing or unreadable |
| 6 Currency | PASS | 660 line-year rows: year, exchange rate (WDI PA.NUS.FCRF, 1 for US$ values) and CPI factor (BLS CPI-U) equal the downloaded tables; 0 differ |
| 7 Read-only | PASS | 43 files differ from origin/main; 0 outside the job folder |
| 8 Hygiene | PASS | 43 tracked job files and the branch's commit messages scanned; 0 hits |

Gate 8 was also run on the pull request body (taken from CHANGES): no machine path, em dash, co-author or generated-with line.

## Rerun after manual downloads

Save each file under `downloads/manual/<CC>/` of the job folder as named in `manual_downloads.csv` (Excel or CSV with a tariff-code column, a units column and a value column; the year in a column or in the file name; local-currency values marked by the currency code in the value header or file name). Then, from the job folder `_LAC_HUB/vehicle_prices_20261123T163210Z`, with the job's Python environment:

```
python -I scripts/build_prices.py
python -I scripts/build_proposals.py
python -I scripts/build_sources.py
python -I scripts/gates.py 2892
```

`build_prices.py` prints a warning for any manual file whose header it cannot read. A national file replaces UN Comtrade for the years it covers in that country. A table by vehicle type instead of tariff line needs a row in `national_type_map.csv` and a reader in `national_parsers.py`. The fiscal valuation table of item M-GUA-2 (PDF) has no reader yet.
