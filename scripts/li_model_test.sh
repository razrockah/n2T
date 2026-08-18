#!/bin/bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

cd "$workdir"
python "$repo_dir/tests/li_model_test.py"
openmc
python - <<'EOF'
import glob
import openmc
with openmc.StatePoint(glob.glob('statepoint.*.h5')[0]) as sp:
    tbr = sp.get_tally(name='tbr').mean.item()
    mesh_sum = sp.get_tally(name='tbr mesh').mean.sum()
    flux = sp.get_tally(name='flux').mean.item()
    flux_mesh_sum = sp.get_tally(name='flux mesh').mean.sum()
assert tbr > 0, "tbr tally is zero"
assert mesh_sum > 0, "tbr mesh tally is zero"
assert flux > 0, "flux tally is zero"
assert flux_mesh_sum > 0, "flux mesh tally is zero"
print(f"li model test PASSED (TBR = {tbr:.4f})")
EOF
