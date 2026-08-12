# n2T documentation

OpenMC slab model of a fusion breeder blanket, for Li-6 enrichment analysis.
Python builds and runs the neutronics; Julia makes the plots.

## Quick start

```bash
conda activate openmc-env              # OpenMC environment
python src/run_tbr.py                  # run the simulation -> results/*.csv
julia analysis/plot_tbr_heatmap.jl     # TBR heat maps -> results/*.png
julia analysis/plot_flux_heatmap.jl    # flux heat map -> results/*.png
```

Then open the results notebook (see [RESULTS.jl](#resultsjl-pluto-notebook)).

## The model

An 80 x 80 x 34 cm box (vacuum boundary). The slab front face is at z = 0,
so z is the depth into the slab. The source is a uniform box in the void:
the full 80 x 80 cm face, 4 cm thick, centered 10 cm in front of the slab,
emitting isotropically with a Muir DT spectrum (14.08 MeV, kt = 20 keV).

```
z:  -15   -12..-8 (source)   0    0.1          4             19
     |  void [========]       | W    | first wall | breeder    |
     |                        | 0.1  | 3.9 cm     | 15 cm      |
```

| layer      | material                  | density |
|------------|---------------------------|---------|
| coating    | W                         | 19.25 g/cm3 |
| first wall | Eurofer + He, 77/23 vol%  | mixed |
| breeder    | chosen with `--breeder`:  | |
|            | `pbli` — PbLi (84-16)     | 11 g/cm3 |
|            | `li` — pure Li            | 0.472 g/cm3 |
|            | `flibe` — LiF-BeF2 (67-33)| 1.96 g/cm3 |

Breeders are at 900 K, Li-6 enriched to the requested at%. Runs are fixed
source, 100 batches x 500000 particles.

Tallies (mesh voxels are 2 x 2 x 1 cm):

| tally       | score           | where |
|-------------|-----------------|-------|
| `tbr`       | `H3-production` | whole model — the mean is the TBR |
| `tbr_mesh`  | `H3-production` | mesh over the slab (z = 0..19) |
| `flux_mesh` | `flux`          | mesh over everything (z = -15..19) |

## Scripts

All Python scripts accept `-m/--breeder` (`pbli`/`li`/`flibe`) and
`-e/--enrichment` (Li-6 at%, default 90).

| script | what it does |
|--------|--------------|
| `src/run_tbr.py` | runs OpenMC, writes `results/tbr_mesh.csv` and `results/flux_mesh.csv`, prints the total TBR |
| `src/slab_model.py` | exports the model to `model.xml` for openmc-plotter |
| `src/plot_model.py` | same export, then opens openmc-plotter on it |
| `analysis/plot_tbr_heatmap.jl` | TBR heat maps: x-z slice and x-y slice at z = 4.5 cm |
| `analysis/plot_flux_heatmap.jl` | flux heat map: x-z slice, log color scale |
| `analysis/load_tbr.jl` | loads `tbr_mesh.csv` into a DataFrame `df` |

Useful extras for `run_tbr.py`: `-p`/`-b` override particles/batches
(e.g. `-p 5000 -b 10` for a quick test); `-o` changes the output directory.
The CSVs have one row per voxel:
`breeder, enrichment, x_cm, y_cm, z_cm, <value>, <value>_std_dev`.
OpenMC run files go to `runs/` (git-ignored).

## RESULTS.jl (Pluto notebook)

All results in one reactive page: the CSVs as browsable DataFrames, TBR
slices, the TBR depth profile, and the flux map.

To run it:

1. Start Pluto from the repo root:

   ```bash
   julia -e 'using Pluto; Pluto.run(notebook="RESULTS.jl")'
   ```

   (Or start `julia`, then `using Pluto` and `Pluto.run()`, and open
   `RESULTS.jl` from the file picker.)

2. A browser tab opens and the notebook starts running. The first open
   takes a minute or two while Pluto sets up its package environment;
   after that it is fast.

3. Cells run automatically and stay live: after a new `python
   src/run_tbr.py` run, re-running the two `CSV.read` cells (click the
   play button on each, or Ctrl+Shift+Enter for all) refreshes every
   table and plot.

## Viewing the geometry in openmc-plotter

1. `python src/plot_model.py` (exports and opens the GUI).
2. The window opens on an x-y slice at the origin — all void, one color.
3. Set **Basis** to `xz` and **Color By** to `material`, then click
   **Apply Changes**.
4. The slab shows as horizontal bands at z = 0..19: coating, first wall,
   breeder. Zoom with the scroll wheel; right-click a point to see its
   cell and material.
