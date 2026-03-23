#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() {
    printf 'FAIL: %s\n' "$1" >&2
    exit 1
}

is_allowed_public_path() {
    case "$1" in
        README.md|CHANGELOG.md|VERSION|install.sh|uninstall.sh|LICENSE.md)
            return 0
            ;;
        bin/*|python/*|resources/*|tests/*|docs/*)
            return 0
            ;;
    esac
    return 1
}

command -v git >/dev/null 2>&1 || fail "git não está disponível"
command -v fish >/dev/null 2>&1 || fail "fish não está disponível"
command -v python3 >/dev/null 2>&1 || fail "python3 não está disponível"

cd "$ROOT"

staged="$(git diff --cached --name-only)"
[[ -n "$staged" ]] || fail "nenhum arquivo staged; rode o gate depois do staging explícito"

blocked_regex='^(\.aury-private/|README_V15_PREP\.md|V15_CODEX_PROMPT\.md|PROJETO_TRIPLE_A\.md|TRIPLE_A_RESUMO\.md|ROADMAP_ESTRATEGICO_PRIVADO_AURY_V1\.6_A_V1\.9\.md|DIRECAO_SEGURANCA_FUTURA_AURY\.md|docs/V1\.5_MEGA_DICIONARIO_INICIAL\.md|docs/V1\.5_CORPUS_CONVERSACIONAL_INICIAL\.md)$'
blocked="$(printf '%s\n' "$staged" | grep -E "$blocked_regex" || true)"
if [[ -n "$blocked" ]]; then
    printf 'FAIL: stage contém arquivo privado/sensível:\n%s\n' "$blocked" >&2
    exit 1
fi

unexpected=()
while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    if ! is_allowed_public_path "$path"; then
        unexpected+=("$path")
    fi
done <<<"$staged"

if ((${#unexpected[@]} > 0)); then
    printf 'FAIL: stage contém arquivo fora do recorte público esperado:\n' >&2
    printf '%s\n' "${unexpected[@]}" >&2
    exit 1
fi

git diff --cached --check >/dev/null || fail "stage pública contém erros de whitespace ou conflito textual"

bash "$ROOT/tests/preflight_canonico.sh"
python3 "$ROOT/tests/audit_exit_surfaces.py"

printf 'release_gate_minimo: ok\n'
