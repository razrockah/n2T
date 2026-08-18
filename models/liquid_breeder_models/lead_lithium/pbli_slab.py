import openmc
import neutronics_material_maker as nmm
import math
ENRICHMENT = 90

pbli = openmc.Material(name='PbLi')
pbli.add_element('Pb', 84)
pbli.add_element('Li', 16, enrichment=ENRICHMENT, enrichment_target='Li6', enrichment_type='ao')
pbli.set_density('g/cm3', 11)

eurofer = nmm.Material.from_library('eurofer').openmc_material

helium = openmc.Material(name='He')
helium.add_element('He', 1.0)
helium.set_density('g/cm3', 0.0015)

eurofer_he = openmc.Material.mix_materials([eurofer, helium], [0.77, 0.23], 'vo')
eurofer_he.name = 'FW Eurofer + He'

tungsten = openmc.Material(name='W')
tungsten.add_element('W', 1.0)
tungsten.set_density('g/cm3', 19.25)

materials = openmc.Materials([pbli, eurofer_he, tungsten])

# GEOMETRY
outer_box = openmc.model.RectangularParallelepiped(-100, 100, -100, 100, -100, 100, boundary_type='vacuum')
coating_min = openmc.XPlane(9)
fw_min = openmc.XPlane(9.1)
breeder_min = openmc.XPlane(10)

void_cell = openmc.Cell(name='void cell', region=-outer_box & -coating_min)
coating_cell = openmc.Cell(name='coating cell', region=-outer_box & +coating_min & -fw_min, fill=tungsten)
fw_cell = openmc.Cell(name='first wall cell', region=-outer_box & +fw_min & -breeder_min, fill=eurofer_he)
breeder_cell = openmc.Cell(name='breeder cell', region=-outer_box & +breeder_min, fill=pbli)

geometry = openmc.Geometry([void_cell, coating_cell, fw_cell, breeder_cell])

# TALLIES
mesh = openmc.RegularMesh()
mesh.lower_left = (-10, -30, -0.5)
mesh.upper_right = (50, 30, 0.5)
mesh.dimension = (600, 600, 1)  # 1 mm pixels, thin slice at z=0

tbr_mesh_tally = openmc.Tally(name='tbr mesh')
tbr_mesh_tally.filters = [openmc.MeshFilter(mesh)]
tbr_mesh_tally.scores = ['(n,Xt)']

tbr_tally = openmc.Tally(name='tbr')
tbr_tally.scores = ['(n,Xt)']

tallies = openmc.Tallies([tbr_mesh_tally, tbr_tally])

# SETTINGS
source = openmc.IndependentSource()
source.particle = 'neutron'
source.space = openmc.stats.CartesianIndependent(
    x=openmc.stats.Discrete([0.0], [1.0]),
    y=openmc.stats.Uniform(-30.0, 30.0),   # line source along y
    z=openmc.stats.Discrete([0.0], [1.0]),
)

source.angle = openmc.stats.PolarAzimuthal(
    mu=openmc.stats.Uniform(0.0, 1.0),   # uniform over the +x hemisphere (180 deg span)
    phi=openmc.stats.Uniform(0.0, 2 * math.pi),
    reference_uvw=(1.0, 0.0, 0.0),
    reference_vwu=(0.0, 0.0, 1.0),
)

source.energy = openmc.stats.muir(e0=14.08e6, m_rat=5.0, kt=20_000.0) # D-T fusion spectrum at T = 20 keV

settings = openmc.Settings()
settings.run_mode = 'fixed source'
settings.batches = 100
settings.particles = 500_000
settings.source = source

pbli_model = openmc.Model(geometry=geometry, materials=materials, settings=settings, tallies=tallies)
pbli_model.export_to_model_xml()
