## References
The inspiration for this simple model and material choice follow the DCLL
stellarator blanket study of Sosa & Palermo (2023). The model is built and run
with **OpenMC**, using material definitions from the **neutronics_material_maker**
/ Fusion Energy Neutronics Workshop tooling and **ENDF/B** cross-section data.

- **OpenMC** — P. K. Romano et al., "OpenMC: A State-of-the-Art Monte Carlo Code
  for Research and Development," *Ann. Nucl. Energy* **82**, 90–97 (2015).
  <https://docs.openmc.org>
- **ENDF/B nuclear data** — <https://www.nndc.bnl.gov/endf/> 
- **neutronics_material_maker / Neutronics Workshop** — Shimwell et al. (2022).
  <https://github.com/fusion-energy/neutronics-workshop>
- **model basis** — D. Sosa and I. Palermo, *Energies* **16**(11),
  4430 (2023). <https://doi.org/10.3390/en16114430>

## Scripts
All scripts live in `scripts/` and can be run from anywhere; they resolve paths
relative to their own location. They expect the `openmc-env` conda environment
to be active.

```
  li_run.sh | flibe_run.sh | pbli_run.sh
```
Full run of one model: exports the model to `model.xml`, runs OpenMC
(100 batches × 500k particles) in the model's directory, and moves the
statepoint to `analysis/<model>_statepoint.h5`.

```
  test_models.sh
  li_model_test.sh | flibe_model_test.sh | pbli_model_test.sh
```
Quick smoke tests (10 batches × 5k particles, from `tests/`). Each runs in a
throwaway temp directory and asserts the `tbr` and `tbr mesh` tallies are
present and nonzero. `test_models.sh` runs all three and stops at the first
failure.

```
  li_gplot.sh | flibe_gplot.sh | pbli_gplot.sh
```
Exports a fresh `model.xml` for the model and opens it in `openmc-plotter`.

```
  rm_output_files.sh
```
Deletes generated outputs: `model.xml`, `summary.h5`, `tallies.out` and stray
statepoints in the model directories, plus the statepoints and CSVs in
`analysis/`.
