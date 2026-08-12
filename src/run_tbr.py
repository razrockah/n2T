"""Run a simulation and write the TBR and flux mesh tallies to CSVs."""
import argparse
from pathlib import Path

import numpy as np
import openmc
import pandas as pd

from slab_model import SLAB_MODELS


def mesh_dataframe(mesh_tally, value, breeder, enrichment):
    """One row per voxel: breeder, enrichment, voxel-center x/y/z, mean, std dev."""
    mesh = mesh_tally.filters[0].mesh
    mesh_df = mesh_tally.get_pandas_dataframe()
    widths = (np.array(mesh.upper_right) - np.array(mesh.lower_left)) / np.array(mesh.dimension)
    return pd.DataFrame({
        'breeder': breeder,
        'enrichment': enrichment,
        'x_cm': mesh.lower_left[0] + (mesh_df[(f'mesh {mesh.id}', 'x')] - 0.5) * widths[0],
        'y_cm': mesh.lower_left[1] + (mesh_df[(f'mesh {mesh.id}', 'y')] - 0.5) * widths[1],
        'z_cm': mesh.lower_left[2] + (mesh_df[(f'mesh {mesh.id}', 'z')] - 0.5) * widths[2],
        value: mesh_df['mean'],
        f'{value}_std_dev': mesh_df['std. dev.'],
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-m', '--breeder', choices=SLAB_MODELS, default='pbli',
                        help='breeder material (default: pbli)')
    parser.add_argument('-e', '--enrichment', type=float, default=90,
                        help='Li-6 enrichment in atom percent (default: 90)')
    parser.add_argument('-p', '--particles', type=int,
                        help='override particles per batch (default: model setting, 500000)')
    parser.add_argument('-b', '--batches', type=int,
                        help='override number of batches (default: model setting, 100)')
    parser.add_argument('-o', '--outdir', type=Path, default=Path('results'),
                        help='directory for the output CSVs (default: results)')
    args = parser.parse_args()

    model = SLAB_MODELS[args.breeder](args.enrichment)
    if args.particles:
        model.settings.particles = args.particles
    if args.batches:
        model.settings.batches = args.batches

    run_dir = Path('runs')
    run_dir.mkdir(exist_ok=True)
    statepoint_file = model.run(cwd=run_dir)

    args.outdir.mkdir(parents=True, exist_ok=True)
    with openmc.StatePoint(statepoint_file) as sp:
        total = sp.get_tally(name='tbr')
        for name, value in [('tbr_mesh', 'tbr'), ('flux_mesh', 'flux')]:
            df = mesh_dataframe(sp.get_tally(name=name), value, args.breeder, args.enrichment)
            csv_path = args.outdir / f'{name}.csv'
            df.to_csv(csv_path, index=False)
            print(f'{name} written to {csv_path}')

    tbr = float(total.mean.flatten()[0])
    std_dev = float(total.std_dev.flatten()[0])
    print(f'{args.breeder}, enrichment {args.enrichment} at% -> TBR = {tbr:.4f} +/- {std_dev:.4f}')


if __name__ == '__main__':
    main()
