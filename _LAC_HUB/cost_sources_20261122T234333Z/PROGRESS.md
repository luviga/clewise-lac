# PROGRESS LAC_COST_SOURCES

Stamp: 20261122T234333Z
Branch: job/cost-sources, from b51f24b

## Done
- Setup: clone, venv, job folder with country subfolders and downloads.
- Phase 1, steps 1.1 to 1.5: cost_inventory.csv, fixed_horizon_sources.csv, choice_sets.csv, tech_status.csv, vehicle_cost_chain.md, vehicle_chain_check.csv, vehicle_chain_inputs.csv, penalty.csv, sources_GEN.csv, cpi_u.csv; REPORT Phase 1 summary.

- Draft pull request luviga/clewise-lac#16 opened at the first push.
- Phase 2 setup: `<CC>/cells_<CC>.csv` (one row per A-O cell to propose against), `scripts/p2_cells.py`.
- Step 2.4 extraction: the Data in Brief draft is readable and copied to `downloads/paper/`; its cost tables are docx tables 29 to 51 (paper Tables 49 to 71).

- Phase 2 shared packages in `GEN/` (vehicles GEN-101 to 104, sector GEN-201 to 207).
- Phase 2 Costa Rica and Dominican Republic: proposals, sources, search logs, manual lists; REPORT sections 2.1 and 2.2.

## Now
- Phase 2 Guatemala and Honduras (agents running), then Jamaica and Ecuador.

## Next
- Phase 2: Guatemala, Honduras, Jamaica, Ecuador, one commit and push per country.
- Step 2.4 paper trace.
- Phase 3 gates, Phase 4 pull request body.
