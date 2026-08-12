"""Slab blanket models: three breeder options, plasma point source, TBR tallies."""
import argparse

import openmc
import neutronics_material_maker as nmm


def make_breeder(breeder, enrichment):
    """One of the breeder material options: 'pbli', 'li' or 'flibe'."""
    if breeder == 'pbli':
        # lithium lead: PbLi (84-16)
        mat = openmc.Material(name='PbLi', temperature=900)
        mat.add_element('Pb', 84)
        mat.add_element('Li', 16, enrichment=enrichment, enrichment_target='Li6', enrichment_type='ao')
        mat.set_density('g/cm3', 11)
    elif breeder == 'li':
        # lithium: Li
        mat = openmc.Material(name='Li', temperature=900)
        mat.add_element('Li', 100, enrichment=enrichment, enrichment_target='Li6', enrichment_type='ao')
        mat.set_density('g/cm3', 0.472)
    elif breeder == 'flibe':
        # FLiBe: LiF-BeF2 (67-33)
        mat = openmc.Material(name='FLiBe', temperature=900)
        mat.add_element('Li', 67, enrichment=enrichment, enrichment_target='Li6', enrichment_type='ao')
        mat.add_element('Be', 33)
        mat.add_element('F', 133)
        mat.set_density('g/cm3', 1.96)
    else:
        raise ValueError(f"unknown breeder '{breeder}', expected 'pbli', 'li' or 'flibe'")
    return mat


def make_first_wall():
    eurofer = nmm.Material.from_library('eurofer').openmc_material

    helium = openmc.Material(name='He')
    helium.add_element('He', 1.0)
    helium.set_density('g/cm3', 0.0015)

    eurofer_he = openmc.Material.mix_materials([eurofer, helium], [0.77, 0.23], 'vo')
    eurofer_he.name = 'FW Eurofer + He'
    return eurofer_he


def make_coating():
    tungsten = openmc.Material(name='W')
    tungsten.add_element('W', 1.0)
    tungsten.set_density('g/cm3', 19.25)
    return tungsten


def _slab_model(breeder_mat):
    """Slab along z: void | thin W coating | first wall | breeder."""
    fw_mat = make_first_wall()
    coating_mat = make_coating()

    box = openmc.model.RectangularParallelepiped(-20, 20, -20, 20, -20, 20, boundary_type='vacuum')

    coating_front = openmc.ZPlane(10.0)
    fw_front = openmc.ZPlane(10.1)
    breeder_front = openmc.ZPlane(12)

    void_cell = openmc.Cell(name='void', region=-box & -coating_front)
    coating_cell = openmc.Cell(name='coating', fill=coating_mat, region=-box & +coating_front & -fw_front)
    fw_cell = openmc.Cell(name='first wall', fill=fw_mat, region=-box & +fw_front & -breeder_front)
    breeder_cell = openmc.Cell(name='breeder', fill=breeder_mat, region=-box & +breeder_front)

    geometry = openmc.Geometry([void_cell, coating_cell, fw_cell, breeder_cell])

    # point source at the origin, 10 cm in front of the coating
    point = openmc.stats.Point((0, 0, 0))
    plasma_source = openmc.IndependentSource( space= point,energy=openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0))

    my_settings = openmc.Settings()
    my_settings.batches = 100
    my_settings.particles = 500000
    my_settings.run_mode = 'fixed source'
    my_settings.source = plasma_source

    mesh = openmc.RegularMesh()
    mesh.dimension = [40, 40, 40]
    mesh.lower_left = (-20, -20, -20)
    mesh.upper_right = (20, 20, 20)

    tbr_tally = openmc.Tally(name='tbr')
    tbr_tally.scores = ['H3-production']

    tbr_mesh_tally = openmc.Tally(name='tbr_mesh')
    tbr_mesh_tally.filters = [openmc.MeshFilter(mesh)]
    tbr_mesh_tally.scores = ['H3-production']

    return openmc.Model(geometry=geometry, settings=my_settings,
                        tallies=openmc.Tallies([tbr_tally, tbr_mesh_tally]))


def pbli_slab_model(enrichment=90):
    return _slab_model(make_breeder('pbli', enrichment))


def li_slab_model(enrichment=90):
    return _slab_model(make_breeder('li', enrichment))


def flibe_slab_model(enrichment=90):
    return _slab_model(make_breeder('flibe', enrichment))


SLAB_MODELS = {'pbli': pbli_slab_model, 'li': li_slab_model, 'flibe': flibe_slab_model}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-m', '--breeder', choices=SLAB_MODELS, default='pbli',
                        help='breeder material (default: pbli)')
    parser.add_argument('-e', '--enrichment', type=float, default=90,
                        help='Li-6 enrichment in atom percent (default: 90)')
    parser.add_argument('-o', '--output', default='model.xml',
                        help='output XML path (default: model.xml)')
    args = parser.parse_args()

    SLAB_MODELS[args.breeder](args.enrichment).export_to_model_xml(args.output)
    print(f'exported {args.output} -- view it with: openmc-plotter {args.output}')


if __name__ == '__main__':
    main()
