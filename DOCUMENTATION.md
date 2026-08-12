# n2T documentation

Basic OpenMC slab model of a fusion breeder blanket, for Li-6 enrichment
analysis. Julia analysis of tally CSVs will come later; for now the project
is the Python model below.

## Setup

The scripts need the `openmc-env` conda env, which has OpenMC,
neutronics_material_maker and openmc-plotter. Run them from the repo root:

```bash
conda activate openmc-env
```

## Slab geometry

A 40x40x40 cm box (vacuum boundary) layered along z. Neutrons would come
from the void side and hit the layers in this order:

```
z:  -20          10    10.2         13.2            20
     |   void     | W    | first wall | breeder      |
     |  (plasma   | 0.2  | 3 cm       | 6.8 cm       |
     |   side)    | cm   |            |              |
```

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

## Scripts (`src/`)

Both scripts take the same options: `-m/--breeder` (`pbli`/`li`/`flibe`,
default `pbli`), `-e/--enrichment` Li-6 at% (default 90), `-o/--output`
XML path (default `model.xml`, git-ignored).

### `slab_model.py`
Builds the slab model and exports it to `model.xml`:

```bash
python src/slab_model.py -m flibe -e 60
```

Also importable: `from slab_model import slab_model` gives the
`openmc.Model`.

### `plot_model.py`
Same export, then opens the result in the openmc-plotter GUI:

```bash
python src/plot_model.py
```
