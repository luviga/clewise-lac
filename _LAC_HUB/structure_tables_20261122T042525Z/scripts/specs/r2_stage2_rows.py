C = 'config/scenarios/rules/stage_controller.csv'
S2 = 'stage2_apply_v2.py'


def ctl(stage, name, value, unit, used, desc, country='all'):
    return dict(stage=stage, name=name, country=country, value=value, unit=unit, used_by=used, description=desc)


ROWS = {
    C: [
        ctl('2', 'own_rule_country_names', 'CostaRica', 'names', S2, 'names of the country with its own rule set (Costa Rica)'),
        ctl('2', 'year_min', '2018', 'year', S2, 'first year read from the Stage 1 controller'),
        ctl('2', 'year_max', '2055', 'year', S2, 'last year read from the Stage 1 controller'),
        ctl('2', 'full_override_tolerance', '0.02', 'share', S2, 'an override file year whose shares sum to 1 within this tolerance replaces all shares'),
        ctl('2', 'mincap_share_tolerance', '0.0001', 'share', S2, 'minimum-capacity share above the current share by more than this lifts the share'),
        ctl('2', 'renorm_tolerance', '0.002', 'share', S2, 'share total further than this from 1 is renormalised'),
        ctl('2', 'renorm_check_tolerance', '0.01', 'share', S2, 'share total after renormalisation further than this from 1 is logged'),
        ctl('2', 'target_match_tolerance', '0.002', 'share', S2, 'renewable share within this of the target needs no rebalancing'),
        ctl('2', 'sentinel_detect_threshold', '9990', 'PJ', S2, 'a Stage 1 upper limit at or above this is the no-limit sentinel'),
        ctl('2', 'audit_digits', '6', 'digits', S2, 'rounding of the share sums written to the Stage 2 audit table'),
        ctl('2', 'limit_digits', '4', 'digits', S2, 'rounding of the lower and upper limits written by Stage 2'),
        ctl('2', 'share_digits', '6', 'digits', S2, 'rounding of the shares written by Stage 2'),
        ctl('2', 'trend_start_year', '2024', 'year', S2, 'first year of the printed generation trend'),
        ctl('2', 'trend_end_year', '2050', 'year', S2, 'last year of the printed generation trend'),
        ctl('2', 'check_years', '2024|2026|2030|2050', 'years', S2, 'years of the printed share sum check'),
        ctl('2', 'check_renewable_years', '2024|2050', 'years', S2, 'years of the printed renewable share check'),
        ctl('2', 'share_check_tolerance', '0.01', 'share', S2, 'share total within this of 1 is printed as OK'),
    ],
}
