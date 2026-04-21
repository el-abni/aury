#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/tests/_gate_common.sh"

gate_require_commands git fish python3

cd "$ROOT"

staged="$(gate_require_public_stage)"
gate_assert_public_stage_scope "$staged"
gate_assert_clean_staged_diff

bash "$ROOT/tests/worktree_gate_minimo.sh"

printf 'release_gate_minimo: ok (gate final canônico da linha 1.x)\n'
