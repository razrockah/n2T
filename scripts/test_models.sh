#!/bin/bash
set -euo pipefail

scripts_dir="$(cd "$(dirname "$0")" && pwd)"
"$scripts_dir/li_model_test.sh"
"$scripts_dir/flibe_model_test.sh"
"$scripts_dir/pbli_model_test.sh"
echo "all model tests passed"
