"""List the Stage 2 T1 share-sum failures (country, scenario, year, sum) using stage2_test_v2's own loader."""
import sys
sys.path.insert(0, 'C:/clw_fix')
import stage2_test_v2 as t  # noqa: E402
from collections import defaultdict

data, years = t.load_controller('C:/clw_fix/_STAGE2_OUTPUT/CONTROLLER_NEW_SCENARIOS.xlsx')
sums = defaultdict(float)
for (c, s, tech), rec in data.items():
    for y in years:
        sums[(c, s, y)] += rec['shares'][y]
for k, v in sorted(sums.items()):
    if abs(v - 1.0) > t.SHARE_TOL:
        print(k, round(v, 5))
        c, s, y = k
        top = sorted(((rec['shares'][y], tech) for (cc, ss, tech), rec in data.items() if cc == c and ss == s), reverse=True)[:8]
        print('   ', [(tech, round(x, 4)) for x, tech in top])
