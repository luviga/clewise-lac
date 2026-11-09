B1 cost consolidation audit

Requested sector analyzed for costs: energy
B1 config workbooks copied: 28
Sector model roots analyzed: 6
Technology rows with review flags: 497

Files:
- B1_Scenario_Config_collected/: copied live config workbooks, grouped by country.
- configs_index.csv: source and copied path for each gathered config workbook.
- model_inventory.csv: model roots, A1 output paths, BAU paths, and cost file presence.
- technology_dictionary.csv: unique technology IDs and names inferred from A1_Outputs.
- technology_dictionary_sources.csv: detailed source rows behind the dictionary.
- energy_cost_parameter_summary.csv: one row per technology and cost parameter.
- energy_cost_technology_matrix.csv: one row per technology with capital/fixed/variable summaries.
- energy_cost_anomalies.csv: filtered matrix rows with any review flag.
- energy_cost_value_distribution.csv: exact numeric value counts by technology and parameter.

Review flags are intentionally conservative. A repeated or zero value can be valid,
but these rows are the places worth checking before changing model inputs.
