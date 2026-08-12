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

A 41 x 41 x 34 cm box (vacuum boundary) layered along z. The slab front
face is at z = 0 and the point source sits on the slab axis at z = -10, so
z is directly the depth into the slab:

```
z:  -15    -10 (source)    0    0.1          4             19
     |   void      *        | W    | first wall | breeder    |
     |                      | 0.1  | 3.9 cm     | 15 cm      |
```

x and y span -20.5..20.5 cm so that 1 cm mesh voxels are centered on the
source axis (x = y = 0).

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

- a point source at (0, 0, -10) — on the slab axis, 10 cm in front of the
  coating — with a Muir DT energy spectrum (14.08 MeV, kt = 20 keV),
  isotropic
- fixed-source run settings: 100 batches x 500000 particles
- two `H3-production` tallies: `tbr` (whole model, the mean is the TBR per
  source neutron) and `tbr_mesh` (41x41x19 regular mesh of 1 cm3 voxels
  covering just the slab, z = 0..19; voxel centers sit at integer x and y,
  including exactly x = y = 0 on the source axis)

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
Runs the simulation and writes the mesh tally to
`results/tbr_mesh.csv` (`-o` to change) with columns
`breeder, enrichment, x_cm, y_cm, z_cm, tbr, tbr_std_dev` — one row per
1 cm3 voxel (coordinates are voxel centers). Also prints the total TBR.
`-p`/`-b` override particles per batch and batches (useful for quick
tests):

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

- `results/tbr_heatmap.png` — x-z slice through the source axis (y = 0)
- `results/tbr_heatmap_xy.png` — x-y slice in the first breeder voxel
  layer (z = 4.5 cm)

```bash
julia analysis/plot_tbr_heatmap.jl
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
