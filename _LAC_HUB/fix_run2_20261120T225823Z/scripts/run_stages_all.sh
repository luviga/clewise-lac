#!/bin/bash
# Phase D full run: Stage 0, DS1 (Guatemala hydro shares from the new denominators), Stages 1, 2, 3, solve headers.
cd /c/clw_fix
J=_LAC_HUB/fix_run2_20261120T225823Z
py -I $J/scripts/stage_runner.py 0
py -I $J/scripts/solve_headers.py S0
py -I $J/scripts/ds1_gua_hydro.py
py -I $J/scripts/stage_runner.py 1
py -I $J/scripts/stage_runner.py 2
py -I $J/scripts/stage_runner.py 3
py -I $J/scripts/solve_headers.py FINAL
echo DONE
