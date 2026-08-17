import openmc

ENRICHMENT = 90

# lithium: Li
lithium = openmc.Material(name='Li')
lithium.add_element('Li', 100, enrichment=ENRICHMENT, enrichment_target='Li6', enrichment_type='ao')
lithium.set_density('g/cm3', 0.472)

# lead lithium: PbLi (84-16)
pbli = openmc.Material(name='PbLi')
pbli.add_element('Pb', 84)
pbli.add_element('Li', 16, enrichment=ENRICHMENT, enrichment_target='Li6', enrichment_type='ao')
pbli.set_density('g/cm3', 11)

# FLiBe: LiF-BeF2 (67-33)
flibe = openmc.Material(name='FLiBe')
flibe.add_element('Li', 67, enrichment=ENRICHMENT, enrichment_target='Li6', enrichment_type='ao')
flibe.add_element('Be', 33)
flibe.add_element('F', 133)
flibe.set_density('g/cm3', 1.96)

