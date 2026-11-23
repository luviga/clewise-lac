# Gates LAC_VEHICLE_PRICES

| Gate | Result | Detail |
| --- | --- | --- |
| 1 Coverage | PASS | 2892 proposal rows for 2892 cells in scope (expected 2892); missing 0, duplicate 0, extra 0 |
| 2 Current values | PASS | 2892 cells read from the workbooks of the checked-out tree; 0 differ |
| 3 Source type | PASS | 36 non-ASSUMPTION rows; 0 cite a source of another type |
| 4 Recompute | PASS | clean run reproduces the class prices of all five countries; 175 base-year cells checked; 0 differ |
| 5 Files | PASS | 50 downloaded files named in the sources files; 0 missing or unreadable |
| 6 Currency | PASS | 660 line-year rows: year, exchange rate (WDI PA.NUS.FCRF, 1 for US$ values) and CPI factor (BLS CPI-U) equal the downloaded tables; 0 differ |
| 7 Read-only | PASS | 38 files differ from origin/main; 0 outside the job folder |
| 8 Hygiene | PASS | 38 tracked job files and the branch's commit messages scanned; 0 hits |

Gate 8 on the pull request body is checked when the pull request is opened (see the REPORT).
