#!/bin/bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_dir/models/liquid_breeder_models/lead_lithium"
python pbli_slab.py
openmc
mv statepoint.*.h5 "$repo_dir/analysis/pbli_statepoint.h5"
