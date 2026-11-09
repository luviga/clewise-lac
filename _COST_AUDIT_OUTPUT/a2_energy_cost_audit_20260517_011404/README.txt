A2 structure list and BAU cost audit

Cost sector analyzed: energy
A2 structure list workbooks copied: 24
Sector model roots analyzed: 6
Technology rows with review flags: 497

Main files:
- A2_Structure_Lists_collected/: copied A2 workbooks, grouped by country.
- a2_structure_lists_index.csv: source and copied path for every gathered A2 workbook.
- a2_structure_list_values.csv: long-form IDs from Year/Tech/Fuel/Emission/MOO/Region lists.
- model_inventory.csv: sector model roots and BAU cost file presence.
- id_dictionary.csv and id_name_sources.csv: names inferred from A1_Outputs.
- fuel_dictionary.csv: A2 fuel IDs with inferred names where available.
- country_cost_file_summary.csv: file-level cost value patterns.
- energy_cost_parameter_summary.csv: one row per technology and cost parameter.
- energy_cost_technology_matrix.csv: capital/fixed/variable side by side per technology.
- energy_cost_anomalies.csv: technologies with any review flag, including flat/repeated values.
- energy_cost_high_priority_anomalies.csv: zeros, ones, missing, blank/null, or nonnumeric values.
- energy_cost_value_distribution.csv: exact value counts by technology and parameter.

Flags are review prompts, not automatic errors. Zero, one, or flat values can be valid.
