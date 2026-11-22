C = 'config/scenarios/rules/stage_controller.csv'
T = 'config/scenarios/technology_types.csv'
S1 = 'stage1_share_analyzer_v16.py'
S12 = 'stage1_share_analyzer_v16.py; stage2_apply_v2.py'


def ctl(stage, name, value, unit, used, desc, country='all'):
    return dict(stage=stage, name=name, country=country, value=value, unit=unit, used_by=used, description=desc)


def toks(group, names, desc, used=S1, match='token'):
    return [dict(group=group, technology=n, match=match, country='all', value='', used_by=used, description=desc)
            for n in names]


ROWS = {
    C: [ctl('1', 'share_column', 'Share_E_Proportional_Pct', 'column name', S1,
            'Stage 0 recommended-share column used for the country', country=c)
        for c in ['CostaRica', 'DominicanRepublic', 'Ecuador', 'Guatemala', 'Honduras', 'Jamaica']] + [
        ctl('all', 'cutoff_year', '2026', 'year', S12, 'last year of the plateau; fossil decline starts the year after'),
        ctl('all', 'plateau_years', '2025|2026', 'years', S12, 'years held at the anchor shares'),
        ctl('all', 'fossil_decline_rate', '0.01', 'fraction per year', S12, 'yearly decline of fossil shares after the cutoff year (BAU rule)'),
        ctl('all', 'target_hold_year', '2050', 'year', S12, 'year after which the renewable target is held'),
        ctl('all', 'upper_security_factor', '1.05', 'ratio', S12, 'upper limit is at least the lower limit times this factor'),
        ctl('all', 'zero_tolerance', '1e-09', 'share', S12, 'smallest share sum treated as non-zero'),
        ctl('1', 'own_rule_country_names', 'CostaRica|COSTARICA|Costa Rica|Costa_Rica', 'names', S1, 'names of the country with its own rule set (Costa Rica)'),
        ctl('1', 'renorm_trigger', '1.001', 'share', S1, 'share total above which shares are scaled back to 1'),
        ctl('1', 'audit_digits', '4', 'digits', S1, 'rounding of the values written to the Stage 1 audit table'),
        ctl('1', 'share_digits', '6', 'digits', S1, 'rounding of the shares written to the Stage 1 controller'),
        ctl('1', 'limit_digits', '4', 'digits', S1, 'rounding of the lower and upper limits written to the Stage 1 controller'),
        ctl('1', 'summary_years', '2030|2040|2050', 'years', S1, 'years printed in the Stage 1 summary after the anchor year'),
    ],
    T: toks('solar_wind_token', ['SOL', 'SUN', 'SPV', 'PV', 'CSP', 'WND', 'WIND', 'WNO', 'WNS'],
            'name token of solar and wind plants (grow in policy scenarios)')
       + toks('hydro_token', ['HYD', 'DAM', 'ROR', 'PPHD', 'PPIHD'], 'name token of hydro plants', used=S12)
       + toks('renewable_token', ['GEO', 'SOL', 'SUN', 'SPV', 'PV', 'CSP', 'WND', 'WIND', 'WNO', 'WNS',
                                  'BMS', 'BIM', 'BIO', 'BGS', 'SUG', 'REN'], 'name token of non-hydro renewable plants')
       + toks('fossil_token', ['DSL', 'DIE', 'FOI', 'HFO', 'CRU', 'COA', 'COK', 'NGS', 'GAS', 'GLP', 'LPG',
                               'GSL', 'KJF', 'OIL', 'PET', 'FOS'], 'name token of fossil plants'),
}
