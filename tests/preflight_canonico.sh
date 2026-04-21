#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/tests/_gate_common.sh"

gate_require_commands fish python3

fish --no-execute "$ROOT/bin/aury.fish" >/dev/null
fish --no-execute "$ROOT/bin/ay.fish" >/dev/null

python3 "$ROOT/tests/audit_canonical_layout.py"
python3 "$ROOT/tests/audit_hybrid_boundary.py"
python3 "$ROOT/tests/audit_public_coherence.py"
python3 "$ROOT/tests/audit_docs_pv_workflow.py"
python3 "$ROOT/tests/audit_gate_ladder.py"
python3 "$ROOT/tests/audit_dev_parity.py"
bash "$ROOT/tests/public_ux_smoke.sh"
python3 "$ROOT/tests/python_core_smoke.py"

printf 'preflight_canonico: ok\n'
