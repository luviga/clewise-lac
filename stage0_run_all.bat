@echo off
REM Stage 0 solver runs: every _S0_0 data file of the countries and scenarios in the tables.
REM stage0_run.py writes this file again on each run, with one command per run it prepared.
REM The list of runs (label, model file, data file, output file) comes from lac_tables.py, which reads
REM config/preparation/Config_country_codes.yaml and config/scenarios/scenario_catalogue.csv.
cd /d "%~dp0"

for /f "usebackq tokens=1-4 delims=|" %%a in (`py lac_tables.py solver-runs S0`) do (
    echo Running %%a...
    glpsol -m "%%b" -d "%%c" -o "%%d"
    echo.
)

echo.
echo All Stage 0 runs complete!
pause
