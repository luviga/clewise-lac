| Supply row | Chosen point | 2024 value (USD/GJ net, real 2024) | Current 2024 | r | r case | STEPS 2030 | STEPS 2050 | CPS 2050 | NZE 2050 | 2025 value (case) | Step 2025 to 2026 STEPS / CPS / NZE (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `DIST_COA` | import CIF | 5.6536 | 3.4478 | 0.050379 | case 1 | 4.4475 | 3.1409 | 3.9024 | 1.8560 | 4.5860 (observed) | 9.81 / 12.45 / 3.96 |
| `DIST_COK` | import CIF | 3.1954 | 0.0 | 0.04819 | case 1 | 3.9071 | 3.7329 | 5.2065 | 1.2279 | 3.1717 (observed) | 22.62 / 25.15 / 9.39 |
| `DIST_DSL` | wholesale import parity | 20.2962 | 20.4935 | 0.258852 | case 2 | 20.9867 | 20.0513 | 27.9662 | 6.5958 | 17.4382 (history from ratio) | 19.8 / 22.27 / 6.87 |
| `DIST_FOI` | wholesale import parity | 14.8098 | 13.8373 | 0.17924 | case 2 | 14.5321 | 13.8844 | 19.3650 | 4.5672 | 12.0750 (history from ratio) | 19.8 / 22.27 / 6.87 |
| `DIST_GSL` | wholesale import parity | 22.1109 | 25.0577 | 0.282458 | case 2 | 22.9005 | 21.8798 | 30.5166 | 7.1973 | 19.0284 (history from ratio) | 19.8 / 22.27 / 6.87 |
| `DIST_KER` | final consumer pre-tax | 31.2593 | 0.0 | 0.402498 | case 1 | 32.6329 | 31.1784 | 43.4857 | 10.2561 | 27.1152 (history from ratio) | 19.8 / 22.27 / 6.87 |
| `DIST_LPG` | wholesale import parity | 13.7735 | 29.4676 | 0.189189 | case 2 | 15.3387 | 14.6550 | 20.4399 | 4.8207 | 12.7452 (history from ratio) | 19.8 / 22.27 / 6.87 |
| `DIST_NGS` | generator delivered | 8.6256 | 10.2397 | 3.93861 | case 3 | 12.2611 | 18.0353 | 19.6035 | 8.6256 | 13.5085 (history from ratio) | -27.18 / -24.01 / -36.67 |
| `EXTT_CRU` | export FOB | 9.2162 | empty | 0.130483 | case 1 | 10.5791 | 10.1075 | 14.0973 | 3.3248 | 8.4709 (observed) | 24.32 / 26.88 / 10.9 |

| Technology | CapitalCost current / proposed (USD/kW) | class | FixedCost current / proposed (USD/kW-yr) | class | VariableCost current / proposed (USD/GJ) | class | Sources |
|---|---|---|---|---|---|---|---|
| `PPBGS` | 5000 / 2600 | matched, newer edition | 7.11 / 7.11 | matched | 0.005 / 1.3889 | matched | INT-001, NAT-002, NAT-004 |
| `PPBIM` | 1929 / 1929 | matched | 77.16 / 77.16 | matched | 0.0096 / 1.1111 | replace | INT-001, INT-002, NAT-001 |
| `PPCOA` | 2562 / 2100 | replace | 61.4 / 31.6 | replace | 0.0064 / 1.6667 | replace | INT-013, NAT-002 |
| `PPDSL` | 448 / 1400 | replace | 31.6 / 20 | replace | 0.006 / 1.3889 | replace | NAT-001 |
| `PPFOI` | 1908 / 1400 | replace | 35.16 / 35.16 | matched | 0.0057 / 1.5806 | matched | INT-009, NAT-001 |
| `PPGEO` | 3900 / 4015 | replace | 150.6 / 150.6 | matched | 0 / 1.3889 | replace | INT-001, INT-002, NAT-001 |
| `PPHDAM` | 2619 / 3500 | matched, newer edition | 33.54 / 50 | replace | 0 / 0 | matched | INT-001, INT-009, NAT-001, NAT-002, NAT-004 |
| `PPHROR` | 1870 / 3444 | replace | 54 / 34 | matched, newer edition | 0 / 0 | matched | INT-001, INT-002, INT-009, NAT-001, NAT-002, NAT-004 |
| `PPNGS` | 1156 / 1000 | replace | 12.12 / 12.12 | matched | 0.0045 / 1.3889 | replace | INT-013, NAT-001 |
| `PPPVD` | 1789.62 / 1794.74 | matched, newer edition | 18.081 / 18.387 | matched, newer edition | 0 / 0 | matched | INT-003, INT-004, INT-005, INT-006, INT-009 |
| `PPPVDS` | 2959.45 / 2841.53 | ASSUMPTION | 33.944 / 52.303 | ASSUMPTION | 0 / 0 | matched | INT-003, INT-004, INT-009 |
| `PPPVT` | 949 / 1375 | replace | 20.23 / 20.23 | matched | 0 / 0 | matched | INT-001, INT-002, INT-009, NAT-001 |
| `PPPVT2` | 1289.51 / 1551.27 | matched, newer edition | 20.988 / 21.609 | matched, newer edition | 0 / 0 | matched | INT-003, INT-004, INT-005, INT-006, INT-009 |
| `PPPVTS` | 2130.08 / 2456.06 | matched, newer edition | 58.635 / 61.468 | matched, newer edition | 0 / 0 | matched | INT-003, INT-004, INT-005, INT-006, INT-009 |
| `PPWNDON` | 1518 / 1600 | matched, newer edition | 28.08 / 28.08 | matched | 0 / 0 | matched | INT-009, INT-010, NAT-001, NAT-002 |
