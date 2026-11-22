#!/bin/bash
# Stage 0 solver runs: every _S0_0 data file of the countries and scenarios in the tables.
# stage0_run.py writes this file again on each run, with one command per run it prepared.
# The list of runs (label, model file, data file, output file) comes from lac_tables.py, which reads
# config/preparation/Config_country_codes.yaml and config/scenarios/scenario_catalogue.csv.
cd "$(dirname "$0")"

py lac_tables.py solver-runs S0 | while IFS='|' read -r label model data out; do
    echo "Running $label..."
    glpsol -m "$model" -d "$data" -o "$out"
    echo ""
done

echo ""
echo "All Stage 0 runs complete!"
