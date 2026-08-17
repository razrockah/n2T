eurofer = nmm.Material.from_library('eurofer').openmc_material

helium = openmc.Material(name='He')
helium.add_element('He', 1.0)
helium.set_density('g/cm3', 0.0015)

eurofer_he = openmc.Material.mix_materials([eurofer, helium], [0.77, 0.23], 'vo')
eurofer_he.name = 'FW Eurofer + He'

tungsten = openmc.Material(name='W')
tungsten.add_element('W', 1.0)
tungsten.set_density('g/cm3', 19.25)