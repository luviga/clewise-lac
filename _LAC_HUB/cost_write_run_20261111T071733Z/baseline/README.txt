Phase B baseline of LAC_OVERNIGHT_COST_RUN (one folder per country, A2 and B1).

A2/cand1_python312_pandas3: first try with python.org Python 3.12.0 and pandas 3.0.2 (the machine's `py`).
  The DR and Guatemala compilers fail under pandas 3 (run.log). The first driver version also compared
  folders keyed on the Scenario label and read folders the failed compiler had not rewritten, so its
  diff listings were removed; the produced CSV files and run logs are kept.
A2/cand2_anaconda_pandas2: chosen. Anaconda Python 3.12.4, pandas 2.2.2 (Guatemala through
  scripts/run_with_append_shim.py). produced/ holds what the compiler wrote, installed/ the
  BAU, NDCNEW and LTSNEW folders after the overlay step; installed/ is the Phase D reference.
B1/cand1_anaconda: chosen B1 run on the cand2 A2 output. B1_Output_Params/ and data_files/ are
  the Phase D reference; solve_log.jsonl has each solve's status and objective.
CostaRica/B1/cand0_anaconda_no_LTSOPT_input: B1 stops because the config activates LTSOPT.

Line endings of every text file in this folder were normalised to LF and trailing blanks removed before committing (the repository diff check); values and keys are unchanged.
