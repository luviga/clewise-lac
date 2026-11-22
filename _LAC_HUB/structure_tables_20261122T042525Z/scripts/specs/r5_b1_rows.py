T = 'config/scenarios/technology_types.csv'
F = 'config/scenarios/fuel_types.csv'
E = 'config/scenarios/emission_labels.csv'
B1 = 'B1 runner'


def t(group, names, country='all', desc='', match='name', values=None, used=B1):
    out = []
    for i, n in enumerate(names):
        out.append(dict(group=group, technology=n, match=match, country=country,
                        value='' if values is None else values[i], used_by=used, description=desc))
    return out


def e(group, pairs, country='all', desc='', used=B1):
    return [dict(group=group, item=i + 1, technology=tech, emission=em, country=country, used_by=used, description=desc)
            for i, (tech, em) in enumerate(pairs)]


IGN_GH = ['TRANRAILFREINF', 'TRANOMOTWalk', 'TRANOMOTBike', 'TRXTRAIELE', 'TRXTRAIFREELE', 'TRANRAILINF', 'TRANPUB', 'TRANRAILCAR']
IGN_DR = IGN_GH + ['LATR', 'PROD_CLK_TRAD', 'NO_CONTR_OD', 'AG_TRVEG']
EXT6 = ['Accidents', 'Health', 'Congestion', 'CONVAR', 'CONHICK', 'REHAB']
EXT_DR = ['Accidents', 'Health', 'Congestion', 'RM', 'FERT_ORG', 'salud_residuos', 'contam_agua', 'turismo_residuos',
          'turismo_residuos', 'CONHAB', 'CONTUR', 'CONVAR', 'CONHICK', 'RESHID', 'DAPANI']
G4 = ['CO2e', 'CO2', 'CH4', 'N2O']
ROWS = {
    T: t('transport_cap_ignore', IGN_DR, 'DominicanRepublic', 'technologies whose maximum capacity the transport rewrite leaves as is')
       + t('transport_cap_ignore', IGN_GH, 'Guatemala', 'technologies whose maximum capacity the transport rewrite leaves as is')
       + t('transport_cap_ignore', IGN_GH, 'Honduras', 'technologies whose maximum capacity the transport rewrite leaves as is')
       + t('freight_rail_complement_share', ['Techs_He_Freight'], 'DominicanRepublic',
           'fleet group that complements freight rail; value = its share in percent', values=['100'])
       + t('bus_efficiency_complement_share', ['Techs_Auto', 'Techs_Buses_Micro', 'Techs_Buses_Pub', 'Techs_Buses_Tur',
                                               'Techs_Motos', 'Techs_SUV', 'Techs_Taxi'], 'DominicanRepublic',
           'fleet groups that complement efficient buses; value = share in percent',
           values=['15.5', '5', '0', '0', '70.7', '8.5', '0.3'])
       + t('gasoline_blend', ['T4GSL_LIG', 'T4GSL_PRI', 'DIST_GSL'], 'Guatemala', 'gasoline technologies whose emission factors follow the ethanol blend')
       + t('gasoline_blend', ['T4GSL_LIG', 'T4GSL_PRI', 'T4GSL_PUB', 'T4GSL_TUR', 'DIST_GSL'], 'Honduras', 'gasoline technologies whose emission factors follow the ethanol blend')
       + t('rail_passenger_tech', ['TRNPASRAI'], 'CostaRica', 'passenger rail technology')
       + t('microbus_tech', ['TRNMIC'], 'CostaRica', 'microbus technology')
       + t('security_special_tech', ['TRAUTHG'], 'Honduras', 'technology whose upper capacity margin uses the special security factor')
       + t('import_token', ['IMP'], desc='name token of import technologies (left out of technology lists)', match='token')
       + t('electric_set_token', ['ELE'], desc='name token of electric fleet sets', match='token')
       + t('rail_freight_set', ['Techs_Trains_Freight'], desc='fleet group of freight rail')
       + t('rail_passenger_set', ['Techs_Trains'], desc='fleet group of passenger rail')
       + t('heavy_freight_set', ['Techs_He_Freight'], desc='fleet group of heavy freight trucks')
       + t('cable_car_set', ['Techs_Telef'], desc='fleet group of cable cars')
       + t('efficient_bus_set', ['Techs_Bus_Efi'], desc='fleet group of efficient buses')
       + t('public_bus_set', ['Techs_Buses_Pub'], desc='fleet group of public buses')
       + t('minibus_set', ['Techs_Buses_Micro'], desc='fleet group of minibuses')
       + t('tourism_bus_set', ['Techs_Buses_Tur'], desc='fleet group of tourism buses')
       + t('car_set', ['Techs_Auto'], desc='fleet group of cars')
       + t('motorcycle_set', ['Techs_Motos'], desc='fleet group of motorcycles')
       + t('suv_set', ['Techs_SUV'], desc='fleet group of sport utility vehicles')
       + t('taxi_set', ['Techs_Taxi'], desc='fleet group of taxis'),
    F: [dict(group=g, fuel=n, match='name', country='all', used_by=B1, description=d) for g, n, d in [
        ('passenger_private_demand', 'E6TDPASPRI', 'private passenger transport demand'),
        ('passenger_public_demand', 'E6TDPASPUB', 'public passenger transport demand'),
        ('freight_heavy_demand', 'E6TDFREHEA', 'heavy freight transport demand'),
        ('freight_light_demand', 'E6TDFRELIG', 'light freight transport demand'),
        ('nonmotorised_demand', 'E6TRNOMOT', 'non-motorised transport demand'),
        ('passenger_tourism_demand', 'E6TDPASTUR', 'tourism passenger transport demand'),
    ]],
    E: e('externality', [('', x) for x in EXT_DR], 'DominicanRepublic', 'externality labels of the output tables')
       + e('externality', [('', x) for x in EXT6], 'Ecuador', 'externality labels whose penalties are discounted in the outputs')
       + e('externality', [('', x) for x in ['Accidents', 'Health', 'Congestion']], 'Guatemala', 'externality labels whose penalties are discounted in the outputs')
       + e('externality', [('', x) for x in EXT6], 'Honduras', 'externality labels whose penalties are discounted in the outputs')
       + e('externality', [('', x) for x in EXT6], 'Jamaica', 'externality labels whose penalties are discounted in the outputs')
       + e('gasoline_blend', [('T4GSL_LIG', 'CO2e'), ('T4GSL_PRI', 'CO2e'), ('DIST_GSL', 'CO2e_sources')], 'Guatemala',
           'emissions of the gasoline technologies scaled by the ethanol blend')
       + e('gasoline_blend', [(tt, g) for tt in ['T4GSL_LIG', 'T4GSL_PRI', 'T4GSL_PUB', 'T4GSL_TUR'] for g in G4]
           + [('DIST_GSL', 'CO2e_sources')], 'Honduras', 'emissions of the gasoline technologies scaled by the ethanol blend')
       + e('co2_token', [('', 'CO2')], desc='name token of carbon dioxide emissions'),
}
