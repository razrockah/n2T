#!/bin/bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_dir/models/liquid_breeder_models/flibe"
python flibe_slab.py
openmc
mv statepoint.*.h5 "$repo_dir/analysis/flibe_statepoint.h5"
