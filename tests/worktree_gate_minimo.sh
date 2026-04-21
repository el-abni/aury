#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/tests/_gate_common.sh"

gate_require_commands git fish python3

cd "$ROOT"

gate_assert_clean_worktree_diff

bash "$ROOT/tests/preflight_canonico.sh"
python3 "$ROOT/tests/audit_exit_surfaces.py"
python3 -m unittest tests.test_canonical_core_surface tests.test_core_api_characterization

printf 'worktree_gate_minimo: ok (gate de worktree canônico da linha 1.x)\n'
