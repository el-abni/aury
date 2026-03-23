#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() {
    printf 'FAIL: %s\n' "$1" >&2
    exit 1
}

command -v fish >/dev/null 2>&1 || fail "fish não está disponível"
command -v python3 >/dev/null 2>&1 || fail "python3 não está disponível"

fish --no-execute "$ROOT/bin/aury.fish" >/dev/null
fish --no-execute "$ROOT/bin/ay.fish" >/dev/null

python3 "$ROOT/tests/audit_public_coherence.py"
python3 "$ROOT/tests/audit_dev_parity.py"
bash "$ROOT/tests/public_ux_smoke.sh"
python3 "$ROOT/tests/python_core_smoke.py"

printf 'preflight_canonico: ok\n'
