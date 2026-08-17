#!/bin/bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"

for model_dir in lithium flibe lead_lithium; do
    cd "$repo_dir/models/liquid_breeder_models/$model_dir"
    rm -fv model.xml summary.h5 tallies.out statepoint.*.h5
done

cd "$repo_dir/analysis"
rm -fv *.h5 *.csv
