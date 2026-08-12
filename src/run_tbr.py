"""Run a TBR simulation and write the mesh tally to a CSV."""
import argparse
from pathlib import Path

import numpy as np
import openmc
import pandas as pd

from slab_model import SLAB_MODELS


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
    parser.add_argument('-o', '--output', type=Path, default=Path('results/tbr_mesh.csv'),
                        help='output CSV path (default: results/tbr_mesh.csv)')
    args = parser.parse_args()

    model = SLAB_MODELS[args.breeder](args.enrichment)
    if args.particles:
        model.settings.particles = args.particles
    if args.batches:
        model.settings.batches = args.batches

    run_dir = Path('runs')
    run_dir.mkdir(exist_ok=True)
    statepoint_file = model.run(cwd=run_dir)

    with openmc.StatePoint(statepoint_file) as sp:
        total = sp.get_tally(name='tbr')
        mesh_tally = sp.get_tally(name='tbr_mesh')
        mesh = mesh_tally.filters[0].mesh

        mesh_df = mesh_tally.get_pandas_dataframe()
        # mesh indices (1-based) -> bin-center coordinates in cm
        widths = (np.array(mesh.upper_right) - np.array(mesh.lower_left)) / np.array(mesh.dimension)
        df = pd.DataFrame({
            'breeder': args.breeder,
            'enrichment': args.enrichment,
            'x_cm': mesh.lower_left[0] + (mesh_df[(f'mesh {mesh.id}', 'x')] - 0.5) * widths[0],
            'y_cm': mesh.lower_left[1] + (mesh_df[(f'mesh {mesh.id}', 'y')] - 0.5) * widths[1],
            'z_cm': mesh.lower_left[2] + (mesh_df[(f'mesh {mesh.id}', 'z')] - 0.5) * widths[2],
            'tbr': mesh_df['mean'],
            'tbr_std_dev': mesh_df['std. dev.'],
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)

    tbr = float(total.mean.flatten()[0])
    std_dev = float(total.std_dev.flatten()[0])
    print(f'{args.breeder}, enrichment {args.enrichment} at% -> TBR = {tbr:.4f} +/- {std_dev:.4f}')
    print(f'mesh tally written to {args.output}')


if __name__ == '__main__':
    main()
