#!/bin/bash
# Pristine copy of the base commit's model inputs and outputs, outside the clone (read by the proposal builders).
# Usage: bash make_base_snapshot.sh <target_dir>
set -e
T="$1"; mkdir -p "$T"
cd /c/clw_fix
P=""
for m in CostaRica/CR_ENERGY/t1_confection DominicanRepublic/RD_ENERGY Ecuador/ECU_Energy Guatemala/GUA_ENERGY Honduras/HON_ENERGY Jamaica/JAM_ENERGY; do
  P="$P $m/A1_Outputs $m/B1_Scenario_Config.xlsx $m/B1_Output_Params $m/A2_Output_Params $m/B1_Default_Param.xlsx"
done
git archive 4ba69d6cc3e6619bcc7ee6aee968ea0c78372b2f $P _STAGE2_INPUTS _STAGE0_OUTPUT _STAGE1_OUTPUT _STAGE2_OUTPUT _STAGE3_RESULTS | tar -x -C "$T"
