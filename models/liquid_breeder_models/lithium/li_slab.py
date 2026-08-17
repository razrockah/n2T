import openmc
import neutronics_material_maker as nmm
ENRICHMENT = 90

lithium = openmc.Material(name='Li')
lithium.add_element('Li', 100, enrichment=ENRICHMENT, enrichment_target='Li6', enrichment_type='ao')
lithium.set_density('g/cm3', 0.472)

eurofer = nmm.Material.from_library('eurofer').openmc_material

helium = openmc.Material(name='He')
helium.add_element('He', 1.0)
helium.set_density('g/cm3', 0.0015)

eurofer_he = openmc.Material.mix_materials([eurofer, helium], [0.77, 0.23], 'vo')
eurofer_he.name = 'FW Eurofer + He'

tungsten = openmc.Material(name='W')
tungsten.add_element('W', 1.0)
tungsten.set_density('g/cm3', 19.25)

materials = openmc.Materials([lithium, eurofer_he, tungsten])

# GEOMETRY
outer_box = openmc.model.RectangularParallelepiped(0, 50, -20, 20, -20, 20, boundary_type='vacuum')
void_box = openmc.model.RectangularParallelepiped(0, 9, -20, 20, -20, 20)
coating_box = openmc.model.RectangularParallelepiped(9, 9.1, -20, 20, -20, 20)
fw_box = openmc.model.RectangularParallelepiped(9.1, 10,-20, 20, -20, 20)
breeder_box = openmc.model.RectangularParallelepiped(10, 50, -20, 20, -20, 20)

breeder_cell = openmc.Cell(name='breeder cell', region = -breeder_box, fill = lithium)
void_cell = openmc.Cell(name='void cell', region = -void_box)
coating_cell = openmc.Cell(name='coating cell', region = -coating_box, fill = tungsten)
fw_cell = openmc.Cell(name='first wall cell', region = -fw_box, fill = eurofer_he)

geometry = openmc.Geometry([void_cell, coating_cell, fw_cell, breeder_cell])

# SETTINGS 
source = openmc.IndependentSource()
source.space = openmc.stats.Point((0.0, 0.0, 0.0))
source.angle = openmc.stats.Monodirectional((1.0, 0.0, 0.0)) # +x direction
source.energy = openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0)

settings = openmc.Settings()
settings.batches = 100
settings.particles = 500_000
settings.run_mode = 'fixed source'
settings.source = source

model = openmc.Model(geometry=geometry, materials=materials, settings=settings)

model.export_to_model_xml()   