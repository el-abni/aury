#!/usr/bin/env bash

gate_fail() {
    printf 'FAIL: %s\n' "$1" >&2
    exit 1
}

gate_require_commands() {
    local command_name
    for command_name in "$@"; do
        command -v "$command_name" >/dev/null 2>&1 || gate_fail "$command_name não está disponível"
    done
}

gate_is_allowed_public_path() {
    case "$1" in
        README.md|CHANGELOG.md|VERSION|install.sh|uninstall.sh|LICENSE.md|.gitignore)
            return 0
            ;;
        bin/*|python/*|resources/*|tests/*|docs/*)
            return 0
            ;;
    esac
    return 1
}

gate_assert_clean_worktree_diff() {
    git diff --check >/dev/null || gate_fail "a worktree contém erro textual antes do gate canônico"
}

gate_collect_staged_paths() {
    git diff --cached --name-only
}

gate_require_public_stage() {
    local staged
    staged="$(gate_collect_staged_paths)"
    [[ -n "$staged" ]] || gate_fail "nenhum arquivo staged; o gate final canônico roda depois do staging público explícito. Para validar a worktree atual, use bash tests/worktree_gate_minimo.sh"
    printf '%s\n' "$staged"
}

gate_assert_public_stage_scope() {
    local staged="$1"
    local blocked_regex='^(\.aury-private/|README_V15_PREP\.md|V15_CODEX_PROMPT\.md|PROJETO_TRIPLE_A\.md|TRIPLE_A_RESUMO\.md|ROADMAP_ESTRATEGICO_PRIVADO_AURY_V1\.6_A_V1\.9\.md|DIRECAO_SEGURANCA_FUTURA_AURY\.md|docs/V1\.5_MEGA_DICIONARIO_INICIAL\.md|docs/V1\.5_CORPUS_CONVERSACIONAL_INICIAL\.md)$'
    local blocked
    local unexpected=()
    local path

    blocked="$(printf '%s\n' "$staged" | grep -E "$blocked_regex" || true)"
    if [[ -n "$blocked" ]]; then
        printf 'FAIL: stage contém arquivo privado/sensível:\n%s\n' "$blocked" >&2
        exit 1
    fi

    while IFS= read -r path; do
        [[ -z "$path" ]] && continue
        if ! gate_is_allowed_public_path "$path"; then
            unexpected+=("$path")
        fi
    done <<<"$staged"

    if ((${#unexpected[@]} > 0)); then
        printf 'FAIL: stage contém arquivo fora do recorte público esperado:\n' >&2
        printf '%s\n' "${unexpected[@]}" >&2
        exit 1
    fi
}

gate_assert_clean_staged_diff() {
    git diff --cached --check >/dev/null || gate_fail "stage pública contém erros de whitespace ou conflito textual"
}
