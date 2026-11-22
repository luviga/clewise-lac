C = 'config/scenarios/rules/stage_controller.csv'
A = 'stage3_apply.py'
R = 'stage3_results.py'


def ctl(stage, name, value, unit, used, desc, country='all'):
    return dict(stage=stage, name=name, country=country, value=value, unit=unit, used_by=used, description=desc)


ROWS = {
    C: [
        ctl('3', 'first_patch_year', '2025', 'year', A + '; ' + R, 'first year whose plant limits Stage 3 replaces with controller values'),
        ctl('3', 'reserve_margin', '1.15', 'ratio', A, 'reserve margin written for the generation fuel'),
        ctl('3', 'lower_to_upper_factor', '1.05', 'ratio', A, 'upper activity limit = lower limit times this factor'),
        ctl('3', 'uncapped_value', '99999.0', 'PJ or GW', A, 'value written for a limit that Stage 3 leaves open'),
        ctl('3', 'year_header_max', '2100', 'year', A, 'largest number read as a year in the header row of a data file block'),
        ctl('3', 'fallback_years_start', '2021', 'year', A, 'first year used when a data file block header holds no years'),
        ctl('3', 'fallback_years_stop', '2051', 'year', A, 'year after the last year used when a data file block header holds no years'),
        ctl('3', 'max_year_default', '2050', 'year', R, 'last year of the share check when the solver output gives none'),
        ctl('3', 'share_fail_deviation', '0.01', 'share', R, 'solver share further than this from the controller share fails'),
        ctl('3', 'share_warn_deviation', '0.003', 'share', R, 'solver share further than this from the controller share warns'),
        ctl('3', 'emission_print_years', '2025|2030|2035|2040|2050', 'years', R, 'years of the printed emission summary'),
        ctl('3', 're_target_tolerance', '0.02', 'share', R, 'renewable share may fall short of the target by this much and pass'),
        ctl('3', 're_print_years', '2025|2030|2035|2050', 'years', R, 'years of the printed BAU renewable share'),
    ],
}
