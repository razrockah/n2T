# n2T documentation

OpenMC slab model of a fusion breeder blanket, for Li-6 enrichment analysis.
Python builds and runs the neutronics; Julia (`analysis/`) reads the tally
CSVs.

## Setup

The Python scripts need the `openmc-env` conda env, which has OpenMC,
neutronics_material_maker and openmc-plotter. Run them from the repo root:

```bash
conda activate openmc-env
```

The Julia script uses CSV and DataFrames from the default (global) Julia
environment.

## Slab geometry

An 80 x 80 x 34 cm box (vacuum boundary) layered along z. The slab front
face is at z = 0, so z is directly the depth into the slab:

```
z:  -15   -12..-8 (source)   0    0.1          4             19
     |  void [========]       | W    | first wall | breeder    |
     |                        | 0.1  | 3.9 cm     | 15 cm      |
```

x and y span -40..40 cm (80 cm slab face).

Layer materials:

| layer      | material | notes |
|------------|----------|-------|
| coating    | W        | 19.25 g/cm3 |
| first wall | FW Eurofer + He | 77/23 vol% mix, Eurofer from the neutronics_material_maker library |
| breeder    | one of the options below | chosen with `--breeder` |

Breeder material options (all at 900 K, Li-6 enriched to the requested at%):

| option  | material | density |
|---------|----------|---------|
| `pbli`  | PbLi (84-16) | 11 g/cm3 |
| `li`    | pure Li      | 0.472 g/cm3 |
| `flibe` | FLiBe, LiF-BeF2 (67-33) | 1.96 g/cm3 |

## Source, settings and tallies

Every model comes with:

- a uniform box source in the void: the full 80 x 80 cm face, 4 cm thick,
  centered 10 cm in front of the coating (z = -12..-8), with a Muir DT
  energy spectrum (14.08 MeV, kt = 20 keV), isotropic
- fixed-source run settings: 100 batches x 500000 particles
- three tallies, all on 2 x 2 x 1 cm voxels where meshed:
  - `tbr` — whole-model `H3-production`; the mean is the TBR per source
    neutron
  - `tbr_mesh` — `H3-production` on a 40x40x19 mesh covering just the slab
    (z = 0..19)
  - `flux_mesh` — `flux` (track-length, per source neutron) on a 40x40x34
    mesh covering the whole region including the void (z = -15..19)

## Model functions (`src/slab_model.py`)

One function per breeder, each returning a ready-to-run `openmc.Model`:

```python
from slab_model import pbli_slab_model, li_slab_model, flibe_slab_model

model = pbli_slab_model(enrichment=90)
```

`SLAB_MODELS` maps the option names (`pbli`/`li`/`flibe`) to these functions.

## Scripts

All Python scripts take the same options: `-m/--breeder`
(`pbli`/`li`/`flibe`, default `pbli`) and `-e/--enrichment` Li-6 at%
(default 90).

### `src/slab_model.py`
Exports the model to `model.xml` (`-o` to change the path):

```bash
python src/slab_model.py -m flibe -e 60
```

### `src/plot_model.py`
Same export, then opens the result in the openmc-plotter GUI:

```bash
python src/plot_model.py
```

### `src/run_tbr.py`
Runs the simulation and writes both mesh tallies to
`results/tbr_mesh.csv` and `results/flux_mesh.csv` (`-o` changes the
directory) with columns
`breeder, enrichment, x_cm, y_cm, z_cm, <value>, <value>_std_dev` — one
row per voxel (coordinates are voxel centers, `<value>` is `tbr` or
`flux`). Also prints the total TBR. `-p`/`-b` override particles per
batch and batches (useful for quick tests):

```bash
python src/run_tbr.py -m pbli -e 90
python src/run_tbr.py -p 5000 -b 10   # quick low-statistics test
```

OpenMC run files (statepoint, summary, XML) go to `runs/`, git-ignored.

### `analysis/load_tbr.jl`
Reads `results/tbr_mesh.csv` into a DataFrame variable `df` and prints it:

```bash
julia analysis/load_tbr.jl
```

### `analysis/plot_tbr_heatmap.jl`
Heat maps (CairoMakie) of the TBR mesh tally, two slices:

- `results/tbr_heatmap.png` — x-z slice at the y voxel nearest the axis
- `results/tbr_heatmap_xy.png` — x-y slice in the first breeder voxel
  layer (z = 4.5 cm)

```bash
julia analysis/plot_tbr_heatmap.jl
```

### `analysis/plot_flux_heatmap.jl`
Heat map of the flux mesh tally: an x-z slice through the whole region
(void + slab) on a log color scale, saved to `results/flux_heatmap.png`:

```bash
julia analysis/plot_flux_heatmap.jl
```

### `RESULTS.jl`
Pluto notebook: introduction, the two CSVs as DataFrames, and all the
plots (TBR x-z and x-y slices, TBR depth profile, flux x-z slice) in one
reactive page. Open it with:

```bash
julia -e 'using Pluto; Pluto.run(notebook="RESULTS.jl")'
```

## Plotting the geometry in openmc-plotter

1. Export and launch (either `python src/plot_model.py`, or
   `python src/slab_model.py` followed by `openmc-plotter model.xml`).
2. The window opens on an x-y slice at the origin — that plane is all void,
   so you only see one color at first.
3. In the options dock, set **Basis** to `xz` (or `yz`) so the z axis is in
   the plot, and set **Color By** to `material`.
4. Click **Apply Changes**. The slab now shows as horizontal bands in the
   upper half of the plot (z = 0..19): thin W coating, first wall, breeder.
5. Zoom with the scroll wheel; right-click any point to list the cell and
   material under the cursor. To zoom into the layers directly, set Origin
   z to 10 and Width/Height to ~25 before applying.
