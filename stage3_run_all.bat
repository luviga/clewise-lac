@echo off
REM Stage 3D solver runs: every _FINAL_0 data file of the countries and scenarios in the tables.
REM The list of runs (label, model file, data file, output file) comes from lac_tables.py, which reads
REM config/preparation/Config_country_codes.yaml and config/scenarios/scenario_catalogue.csv.
cd /d "%~dp0"

for /f "usebackq tokens=1-4 delims=|" %%a in (`py lac_tables.py solver-runs FINAL`) do (
    echo Running %%a...
    glpsol -m "%%b" -d "%%c" -o "%%d"
    echo.
)

echo.
echo All Stage 3 FINAL runs complete!
pause
