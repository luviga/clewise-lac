"""Run a pipeline script unchanged, with DataFrame.append, Series.append and
ExcelWriter.save restored for pandas >= 2.0 (they were removed in pandas 2.0).

Usage (from the model folder):  python run_with_append_shim.py <script.py> [args...]

The shim follows the pandas 1.5 implementation: a dict or Series is turned
into a one-row frame, a list of dicts into a frame, then pandas.concat is
called with the same ignore_index / verify_integrity / sort arguments. The
target script file is not modified.
"""
from __future__ import annotations

import runpy
import sys

import pandas as pd


def _df_append(self, other, ignore_index=False, verify_integrity=False, sort=False):
    if isinstance(other, (pd.Series, dict)):
        if isinstance(other, dict):
            if not ignore_index:
                raise TypeError("Can only append a dict if ignore_index=True")
            other = pd.Series(other)
        if other.name is None and not ignore_index:
            raise TypeError("Can only append a Series if ignore_index=True or if the Series has a name")
        index = pd.Index([other.name], name=self.index.name)
        row_df = other.to_frame().T
        other = row_df.infer_objects().rename_axis(index.names)
    elif isinstance(other, list):
        if not other:
            pass
        elif not isinstance(other[0], pd.DataFrame):
            other = pd.DataFrame(other)
            if self.index.name is not None and not ignore_index:
                other.index.name = self.index.name
    if isinstance(other, (list, tuple)):
        to_concat = [self, *other]
    else:
        to_concat = [self, other]
    return pd.concat(to_concat, ignore_index=ignore_index, verify_integrity=verify_integrity, sort=sort)


def _s_append(self, to_append, ignore_index=False, verify_integrity=False):
    if isinstance(to_append, (list, tuple)):
        to_concat = [self, *to_append]
    else:
        to_concat = [self, to_append]
    return pd.concat(to_concat, ignore_index=ignore_index, verify_integrity=verify_integrity)


if not hasattr(pd.DataFrame, "append"):
    pd.DataFrame.append = _df_append
if not hasattr(pd.Series, "append"):
    pd.Series.append = _s_append
if not hasattr(pd.ExcelWriter, "save"):
    # pandas 1.x ExcelWriter.save() wrote the workbook; in pandas 2.x close() does.
    pd.ExcelWriter.save = lambda self: self.close()

if __name__ == "__main__":
    script = sys.argv[1]
    sys.argv = sys.argv[1:]
    runpy.run_path(script, run_name="__main__")
