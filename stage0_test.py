#!/usr/bin/env python
"""stage0_test.py — 8 tests for .txt patching logic. Run: python stage0_test.py"""
import sys, tempfile, shutil, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from stage0_run import patch_txt_data_file, is_pp_tech, ANCHOR_YEAR, PLATEAU_END

MOCK = """###############
set YEAR := 2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 ;
set TECHNOLOGY := PPFOI01 PPHD01 PPPVT01 TDELE01 ;
set REGION := RD ;
###############
param SpecifiedAnnualDemand default 0 :
[RD,*,*]:
2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 :=
ELEDEM 20.0 20.5 21.0 21.5 22.0 22.5 23.0 23.5 24.0 24.5 25.0 25.5 26.0
;

param TotalTechnologyAnnualActivityLowerLimit default 0 :
[RD,*,*]:
2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 :=
PPFOI01 5.0 5.0 5.0 5.0 5.0 5.0 5.0 5.0 5.0 4.5 4.0 3.5 3.0
PPHD01 12.0 12.0 12.0 12.0 12.0 12.0 12.0 12.0 12.0 13.0 14.0 15.0 16.0
PPPVT01 0.5 0.5 0.5 0.5 0.5 0.5 2.0 2.0 2.0 4.0 6.0 8.0 10.0
TDELE01 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0
;

param TotalTechnologyAnnualActivityUpperLimit default 9999 :
[RD,*,*]:
2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 :=
PPFOI01 50 50 50 50 50 50 50 50 50 45 40 35 30
;
"""

def tmp(): d=tempfile.mkdtemp(); p=Path(d)/"t.txt"; p.write_text(MOCK); return d,p
def vals(content, param, tech):
    m=re.search(rf"param\s+{re.escape(param)}.*?;", content, re.DOTALL)
    if not m: return None
    for l in m.group().split("\n"):
        ps=l.strip().split()
        if ps and ps[0]==tech: return [float(v) for v in ps[1:]]
    return None

def t1():
    d,p=tmp()
    try:
        patch_txt_data_file(p,"TotalTechnologyAnnualActivityLowerLimit",ANCHOR_YEAR,PLATEAU_END)
        v=vals(p.read_text(),"TotalTechnologyAnnualActivityLowerLimit","PPFOI01")
        assert all(v[i]==5.0 for i in range(9))
        print("  [PASS] 1: Historical unchanged")
    finally: shutil.rmtree(d)
def t2():
    d,p=tmp()
    try:
        patch_txt_data_file(p,"TotalTechnologyAnnualActivityLowerLimit",ANCHOR_YEAR,PLATEAU_END)
        for tech,anc in [("PPFOI01",5.0),("PPHD01",12.0),("PPPVT01",2.0)]:
            v=vals(p.read_text(),"TotalTechnologyAnnualActivityLowerLimit",tech)
            assert all(v[i]==anc for i in range(9,13)), f"{tech}[2027+]!={anc}"
        print("  [PASS] 2: Projection at anchor")
    finally: shutil.rmtree(d)
def t3():
    d,p=tmp()
    try:
        patch_txt_data_file(p,"TotalTechnologyAnnualActivityLowerLimit",ANCHOR_YEAR,PLATEAU_END)
        v=vals(p.read_text(),"TotalTechnologyAnnualActivityLowerLimit","TDELE01")
        assert all(x==0.0 for x in v)
        print("  [PASS] 3: Non-PP unchanged")
    finally: shutil.rmtree(d)
def t4():
    d,p=tmp()
    try:
        patch_txt_data_file(p,"TotalTechnologyAnnualActivityLowerLimit",ANCHOR_YEAR,PLATEAU_END)
        v=vals(p.read_text(),"SpecifiedAnnualDemand","ELEDEM")
        assert v[-1]==26.0
        print("  [PASS] 4: Other params untouched")
    finally: shutil.rmtree(d)
def t5():
    d,p=tmp()
    try:
        patch_txt_data_file(p,"TotalTechnologyAnnualActivityLowerLimit",ANCHOR_YEAR,PLATEAU_END,mode="zero")
        v=vals(p.read_text(),"TotalTechnologyAnnualActivityLowerLimit","PPHD01")
        assert all(v[i]==0.0 for i in range(9,13))
        print("  [PASS] 5: Zero mode")
    finally: shutil.rmtree(d)
def t6():
    d,p=tmp()
    try:
        cr=[]; n=patch_txt_data_file(p,"TotalTechnologyAnnualActivityLowerLimit",ANCHOR_YEAR,PLATEAU_END,change_rows=cr)
        assert n==12 and len(cr)==12
        print("  [PASS] 6: Change count=12")
    finally: shutil.rmtree(d)
def t7():
    d,p=tmp()
    try:
        patch_txt_data_file(p,"TotalTechnologyAnnualActivityUpperLimit",ANCHOR_YEAR,PLATEAU_END,mode="upper_sentinel")
        v=vals(p.read_text(),"TotalTechnologyAnnualActivityUpperLimit","PPFOI01")
        assert all(v[i]==9999.0 for i in range(9,13))
        print("  [PASS] 7: Upper limit sentinel")
    finally: shutil.rmtree(d)
def t8():
    assert is_pp_tech("PPFOI01") and is_pp_tech("PPHD01")
    assert not is_pp_tech("TDELE01") and not is_pp_tech("TXTAXEV")
    print("  [PASS] 8: PP prefix detection")

def t9():
    """tech_filter: only PPHD01 gets patched, others untouched"""
    d,p=tmp()
    try:
        patch_txt_data_file(p,"TotalTechnologyAnnualActivityLowerLimit",ANCHOR_YEAR,PLATEAU_END,
                            tech_filter={"PPHD01"})
        c=p.read_text()
        # PPHD01 should be patched (held at anchor 12.0 for 2025+)
        v=vals(c,"TotalTechnologyAnnualActivityLowerLimit","PPHD01")
        assert all(v[i]==12.0 for i in range(9,13)), f"PPHD01 not held at anchor: {v[9:]}"
        # PPFOI01 should NOT be patched (not in filter) — retains original projection values
        v2=vals(c,"TotalTechnologyAnnualActivityLowerLimit","PPFOI01")
        assert v2[9]==4.5 and v2[12]==3.0, f"PPFOI01 wrongly patched: {v2[9:]}"
        print("  [PASS] 9: tech_filter restricts to subset")
    finally: shutil.rmtree(d)

def t10():
    """Bypass re-patch: sentinel first, then hold_at_anchor for filter set"""
    d,p=tmp()
    try:
        # First pass: sentinel all PP upper limits
        patch_txt_data_file(p,"TotalTechnologyAnnualActivityUpperLimit",ANCHOR_YEAR,PLATEAU_END,
                            mode="upper_sentinel")
        v=vals(p.read_text(),"TotalTechnologyAnnualActivityUpperLimit","PPFOI01")
        assert all(v[i]==9999.0 for i in range(9,13)), "sentinel not applied"
        # Second pass: re-patch PPFOI01 only with hold_at_anchor
        patch_txt_data_file(p,"TotalTechnologyAnnualActivityUpperLimit",ANCHOR_YEAR,PLATEAU_END,
                            mode="hold_at_anchor", tech_filter={"PPFOI01"})
        v=vals(p.read_text(),"TotalTechnologyAnnualActivityUpperLimit","PPFOI01")
        assert all(v[i]==50.0 for i in range(9,13)), f"re-patch failed: {v[9:]}"
        print("  [PASS] 10: Bypass re-patch overrides sentinel")
    finally: shutil.rmtree(d)

if __name__=="__main__":
    print("="*60+"\nStage 0 Tests\n"+"="*60)
    p=f=0
    for t in [t1,t2,t3,t4,t5,t6,t7,t8,t9,t10]:
        try: t(); p+=1
        except Exception as e: print(f"  [FAIL] {t.__name__}: {e}"); f+=1
    print(f"\n{'='*60}\n{p}/{p+f} passed")
    if f: sys.exit(1)
