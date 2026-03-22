#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FISH_BIN="$(command -v fish)"

fail() {
    printf 'FAIL: %s\n' "$1" >&2
    exit 1
}

require_in_output() {
    local output="$1"
    local expected="$2"
    local label="$3"

    if ! grep -F -- "$expected" <<<"$output" >/dev/null; then
        fail "$label"
    fi
}

require_not_in_output() {
    local output="$1"
    local unexpected="$2"
    local label="$3"

    if grep -F -- "$unexpected" <<<"$output" >/dev/null; then
        fail "$label"
    fi
}

tmpdirs=()

cleanup() {
    if ((${#tmpdirs[@]} > 0)); then
        rm -rf "${tmpdirs[@]}"
    fi
}

trap cleanup EXIT

fallback_output="$(fish -c "source '$ROOT/bin/aury.fish'; aury abra o arquivo relatorio.pdf" 2>&1 || true)"
require_in_output "$fallback_output" "não consegui entender esse pedido com segurança" "fallback precisa ser honesto"
require_in_output "$fallback_output" "aury ajuda" "fallback precisa oferecer ajuda"

blocked_output="$(fish -c "source '$ROOT/bin/aury.fish'; aury remover ela" 2>&1 || true)"
require_in_output "$blocked_output" "não vou remover nada sem um alvo explícito." "remoção sem alvo seguro deve bloquear explicitamente"

rename_chain_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$rename_chain_tmp")
mkdir -p "$rename_chain_tmp/Documentos/Aury" "$rename_chain_tmp/Downloads"

rename_chain_output="$(ROOT="$ROOT" TMP="$rename_chain_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury copie a pasta Aury que fica em Documentos para Downloads e renomeie ela para Aury-backup; echo ---DEV---; aury dev copie a pasta Aury que fica em Documentos para Downloads e renomeie ela para Aury-backup' 2>&1 || true)"
require_in_output "$rename_chain_output" "copiei a pasta 'Documentos/Aury' para 'Downloads/Aury'" "copiar pasta com localização conversacional deve fechar o destino correto"
require_in_output "$rename_chain_output" "renomeei a pasta 'Downloads/Aury' para 'Downloads/Aury-backup'" "renomear ela deve preservar a base do alvo copiado"
require_in_output "$rename_chain_output" "Ação 1" "aury dev deve expor a ação de cópia separadamente"
require_in_output "$rename_chain_output" "Ação 2" "aury dev deve expor a ação de renomeação separadamente"
require_in_output "$rename_chain_output" "referência local:              Downloads/Aury" "aury dev deve expor a referência local resolvida"
require_in_output "$rename_chain_output" "novo nome:                     Aury-backup" "aury dev deve expor o novo nome solicitado coerente"
require_in_output "$rename_chain_output" "Renomear 'Downloads/Aury' para 'Downloads/Aury-backup'." "aury dev deve resumir a renomeação com a base preservada"

if [[ ! -d "$rename_chain_tmp/Downloads/Aury-backup" || -e "$rename_chain_tmp/Aury-backup" || -e "$rename_chain_tmp/Downloads/Aury" ]]; then
    fail "copiar -> renomear ela precisa materializar apenas o destino final dentro de Downloads"
fi

confirm_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$confirm_tmp")

confirm_output="$(ROOT="$ROOT" TMP="$confirm_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; touch teste.txt; printf "n\n" | aury remover arquivo teste.txt; if test -e teste.txt; echo STILL_PRESENT; else; echo REMOVED; end' 2>&1 || true)"
require_in_output "$confirm_output" "Confirma? [s/N]" "remoção precisa pedir confirmação explícita"
require_in_output "$confirm_output" "eu não removi 'teste.txt'." "negação de confirmação deve cancelar a remoção"
require_in_output "$confirm_output" "STILL_PRESENT" "arquivo deve permanecer quando a confirmação não for positiva"

anaphoric_confirm_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$anaphoric_confirm_tmp")

anaphoric_confirm_output="$(ROOT="$ROOT" TMP="$anaphoric_confirm_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; touch alvo.txt; printf "n\n" | aury copie o arquivo alvo.txt para copia.txt e remova ele; if test -e copia.txt; echo FILE_PRESENT; else; echo FILE_REMOVED; end' 2>&1 || true)"
require_in_output "$anaphoric_confirm_output" "Confirma? [s/N]" "remoção anafórica resolvida também precisa pedir confirmação"
require_in_output "$anaphoric_confirm_output" "eu não removi 'copia.txt'." "negação de confirmação deve cancelar a remoção anafórica"
require_in_output "$anaphoric_confirm_output" "FILE_PRESENT" "remoção anafórica negada não pode apagar o alvo resolvido"

ambiguity_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$ambiguity_tmp")
touch "$ambiguity_tmp/teste.txt"

ambiguity_output="$(ROOT="$ROOT" TMP="$ambiguity_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury copiar teste.txt para backup.txt e docs/' 2>&1 || true)"
require_in_output "$ambiguity_output" "ficou ambíguo definir destino" "destino ambíguo precisa ser exposto como ambiguidade pública"

if [[ -e "$ambiguity_tmp/backup.txt" || -e "$ambiguity_tmp/docs" || -e "$ambiguity_tmp/backup.txt e docs/" ]]; then
    fail "comando ambíguo não deve materializar destino"
fi

chain_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$chain_tmp")
mkdir -p "$chain_tmp/notas"
printf 'abc\n' > "$chain_tmp/notas/teste.txt"

chain_output="$(ROOT="$ROOT" TMP="$chain_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury copie o arquivo notas/teste.txt para notas/teste3.txt e depois mova ela para notas/final2.txt' 2>&1 || true)"
require_in_output "$chain_output" "copiei o arquivo 'notas/teste.txt' para 'notas/teste3.txt'" "encadeamento deve copiar o arquivo inicial"
require_in_output "$chain_output" "movi o arquivo 'notas/teste3.txt' para 'notas/final2.txt'" "encadeamento deve reutilizar a referência local no mover"

if [[ ! -e "$chain_tmp/notas/teste.txt" || ! -e "$chain_tmp/notas/final2.txt" || -e "$chain_tmp/notas/teste3.txt" ]]; then
    fail "encadeamento copiar->mover com 'ela' precisa materializar só o destino final esperado"
fi

remove_policy_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$remove_policy_tmp")
mkdir -p "$remove_policy_tmp/bin"
printf 'x\n' > "$remove_policy_tmp/vlc"

cat > "$remove_policy_tmp/bin/sudo" <<'EOF'
#!/usr/bin/env bash
printf 'SUDO_STUB %s\n' "$*"
EOF
chmod +x "$remove_policy_tmp/bin/sudo"

remove_policy_dev_output="$(ROOT="$ROOT" TMP="$remove_policy_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury dev remover vlc' 2>&1 || true)"
require_in_output "$remove_policy_dev_output" "domínio:                       pacote" "'aury dev remover vlc' precisa assumir a política canônica de pacote"
require_in_output "$remove_policy_dev_output" "estado:                        CONSISTENTE" "'aury dev remover vlc' não pode continuar parcial"
require_in_output "$remove_policy_dev_output" "resumo:                        Remover 'vlc'." "'aury dev remover vlc' precisa expor o alvo de pacote com clareza"

remove_policy_pkg_output="$(ROOT="$ROOT" TMP="$remove_policy_tmp" PATH="$remove_policy_tmp/bin:$PATH" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury remover vlc; if test -e vlc; echo FILE_STILL_PRESENT; else; echo FILE_REMOVED; end' 2>&1 || true)"
require_in_output "$remove_policy_pkg_output" "SUDO_STUB pacman -Rns -- vlc" "'aury remover vlc' deve seguir a política determinística de pacote"
require_in_output "$remove_policy_pkg_output" "FILE_STILL_PRESENT" "'aury remover vlc' não pode apagar um arquivo local só por colisão de nome"

remove_policy_pkg_explicit_output="$(ROOT="$ROOT" TMP="$remove_policy_tmp" PATH="$remove_policy_tmp/bin:$PATH" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury remover pacote vlc' 2>&1 || true)"
require_in_output "$remove_policy_pkg_explicit_output" "SUDO_STUB pacman -Rns -- vlc" "forma explícita de pacote precisa continuar coerente mesmo com colisão local"

remove_policy_file_output="$(ROOT="$ROOT" TMP="$remove_policy_tmp" PATH="$remove_policy_tmp/bin:$PATH" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; printf "n\n" | aury remover arquivo vlc; if test -e vlc; echo FILE_STILL_PRESENT; else; echo FILE_REMOVED; end' 2>&1 || true)"
require_in_output "$remove_policy_file_output" "Confirma? [s/N]" "forma explícita de arquivo precisa passar pela confirmação destrutiva"
require_in_output "$remove_policy_file_output" "eu não removi 'vlc'." "negação de confirmação precisa cancelar a remoção explícita de arquivo"
require_not_in_output "$remove_policy_file_output" "SUDO_STUB" "forma explícita de arquivo não pode cair no backend de pacote"
require_in_output "$remove_policy_file_output" "FILE_STILL_PRESENT" "forma explícita de arquivo negada deve preservar o alvo"

network_keep_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$network_keep_tmp")
mkdir -p "$network_keep_tmp/bin"

cat > "$network_keep_tmp/bin/ping" <<'EOF'
#!/usr/bin/env bash
printf 'PING_STUB %s\n' "$*"
EOF
chmod +x "$network_keep_tmp/bin/ping"

cat > "$network_keep_tmp/bin/librespeed-cli" <<'EOF'
#!/usr/bin/env bash
printf 'LIBRESPEED_SHOULD_NOT_RUN\n'
exit 99
EOF
chmod +x "$network_keep_tmp/bin/librespeed-cli"

network_keep_output="$(ROOT="$ROOT" PATH="$network_keep_tmp/bin:$PATH" fish -c 'source $ROOT/bin/aury.fish; aury testar internet' 2>&1 || true)"
require_in_output "$network_keep_output" "PING_STUB -c 2 -- 8.8.8.8" "'aury testar internet' deve continuar em conectividade simples"
require_not_in_output "$network_keep_output" "velocidade da internet" "'aury testar internet' não pode virar speedtest"
require_not_in_output "$network_keep_output" "LIBRESPEED_SHOULD_NOT_RUN" "'aury testar internet' não pode acionar librespeed-cli"

network_keep_count="$(grep -F -c -- "PING_STUB -c 2 -- 8.8.8.8" <<<"$network_keep_output" || true)"
if [[ "$network_keep_count" -ne 1 ]]; then
    fail "'aury testar internet' não pode duplicar a saída de ping"
fi

speed_success_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$speed_success_tmp")
mkdir -p "$speed_success_tmp/bin"

cat > "$speed_success_tmp/bin/librespeed-cli" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' '{"ping":12.3,"download":245.67,"upload":58.9,"jitter":0.45}'
EOF
chmod +x "$speed_success_tmp/bin/librespeed-cli"

speed_success_output="$(ROOT="$ROOT" PATH="$speed_success_tmp/bin:$PATH" fish -c 'source $ROOT/bin/aury.fish; aury velocidade da rede' 2>&1 || true)"
require_in_output "$speed_success_output" "velocidade da internet" "gatilho estreito com rede deve ativar o speedtest"
require_in_output "$speed_success_output" "ping: 12.3 ms" "speedtest deve expor ping"
require_in_output "$speed_success_output" "download: 245.67 Mbps" "speedtest deve expor download"
require_in_output "$speed_success_output" "upload: 58.9 Mbps" "speedtest deve expor upload"
require_in_output "$speed_success_output" "jitter: 0.45 ms" "speedtest deve expor jitter numérico"
require_not_in_output "$speed_success_output" '{"ping":12.3' "speedtest não pode retransmitir JSON cru"

speed_list_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$speed_list_tmp")
mkdir -p "$speed_list_tmp/bin"

cat > "$speed_list_tmp/bin/librespeed-cli" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' '[{"ping":12.3,"download":245.67,"upload":58.9,"jitter":0.45}]'
EOF
chmod +x "$speed_list_tmp/bin/librespeed-cli"

speed_list_output="$(ROOT="$ROOT" PATH="$speed_list_tmp/bin:$PATH" fish -c 'source $ROOT/bin/aury.fish; aury velocidade da internet' 2>&1 || true)"
require_in_output "$speed_list_output" "velocidade da internet" "formato real em lista deve ativar o speedtest"
require_in_output "$speed_list_output" "ping: 12.3 ms" "lista JSON real deve expor ping"
require_in_output "$speed_list_output" "download: 245.67 Mbps" "lista JSON real deve expor download"
require_in_output "$speed_list_output" "upload: 58.9 Mbps" "lista JSON real deve expor upload"
require_in_output "$speed_list_output" "jitter: 0.45 ms" "lista JSON real deve expor jitter numérico"
require_not_in_output "$speed_list_output" '[{"ping":12.3' "speedtest não pode retransmitir JSON cru em lista"

speed_absent_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$speed_absent_tmp")
mkdir -p "$speed_absent_tmp/bin"

speed_absent_output="$(ROOT="$ROOT" PATH="$speed_absent_tmp/bin" "$FISH_BIN" -c 'source $ROOT/bin/aury.fish; aury velocidade da internet' 2>&1 || true)"
require_in_output "$speed_absent_output" "backend 'librespeed-cli' não está disponível" "ausência do backend deve falhar honestamente"

speed_nonzero_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$speed_nonzero_tmp")
mkdir -p "$speed_nonzero_tmp/bin"

cat > "$speed_nonzero_tmp/bin/librespeed-cli" <<'EOF'
#!/usr/bin/env bash
exit 12
EOF
chmod +x "$speed_nonzero_tmp/bin/librespeed-cli"

speed_nonzero_output="$(ROOT="$ROOT" PATH="$speed_nonzero_tmp/bin:$PATH" fish -c 'source $ROOT/bin/aury.fish; aury testar velocidade da internet' 2>&1 || true)"
require_in_output "$speed_nonzero_output" "retornou erro operacional" "exit code não zero deve virar erro operacional honesto"

speed_bad_json_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$speed_bad_json_tmp")
mkdir -p "$speed_bad_json_tmp/bin"

cat > "$speed_bad_json_tmp/bin/librespeed-cli" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' '{"ping":10.1,"download":88.2}'
EOF
chmod +x "$speed_bad_json_tmp/bin/librespeed-cli"

speed_bad_json_output="$(ROOT="$ROOT" PATH="$speed_bad_json_tmp/bin:$PATH" fish -c 'source $ROOT/bin/aury.fish; aury velocidade da internet' 2>&1 || true)"
require_in_output "$speed_bad_json_output" "não consegui ler o retorno do librespeed-cli com confiança" "JSON incompleto deve falhar com erro de leitura honesto"

download_guard_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$download_guard_tmp")
mkdir -p "$download_guard_tmp/bin"

cat > "$download_guard_tmp/bin/librespeed-cli" <<'EOF'
#!/usr/bin/env bash
printf 'LIBRESPEED_DOWNLOAD_GUARD\n'
EOF
chmod +x "$download_guard_tmp/bin/librespeed-cli"

download_guard_output="$(ROOT="$ROOT" PATH="$download_guard_tmp/bin:$PATH" fish -c 'source $ROOT/bin/aury.fish; aury download da internet' 2>&1 || true)"
require_not_in_output "$download_guard_output" "LIBRESPEED_DOWNLOAD_GUARD" "'download' sozinho não pode virar speedtest"


help_output="$(fish -c "source '$ROOT/bin/aury.fish'; aury ajuda" 2>&1 || true)"
require_in_output "$help_output" "💜 Aury" "ajuda precisa continuar disponível"

version_expected="$(cat "$ROOT/VERSION")"
version_output="$(fish -c "source '$ROOT/bin/aury.fish'; aury --version" 2>&1 || true)"
require_in_output "$version_output" "$version_expected" "version precisa refletir VERSION"

dev_usage_output="$(fish -c "source '$ROOT/bin/aury.fish'; aury dev" 2>&1 || true)"
require_in_output "$dev_usage_output" "🛠 modo dev da Aury" "'aury dev' sem frase precisa continuar disponível"
require_in_output "$dev_usage_output" "Use: aury dev <frase>" "'aury dev' sem frase precisa orientar o uso correto"

ay_help_output="$(fish -c "source '$ROOT/bin/aury.fish'; source '$ROOT/bin/ay.fish'; ay ajuda" 2>&1 || true)"
require_in_output "$ay_help_output" "💜 Aury" "ay ajuda precisa continuar disponível"

ay_version_output="$(fish -c "source '$ROOT/bin/aury.fish'; source '$ROOT/bin/ay.fish'; ay --version" 2>&1 || true)"
require_in_output "$ay_version_output" "$version_expected" "ay --version precisa refletir VERSION"

alias_check_output="$(fish -c "source '$ROOT/bin/aury.fish'; functions -q Aury; and echo ALIAS_PRESENT; or echo ALIAS_ABSENT" 2>&1 || true)"
require_in_output "$alias_check_output" "ALIAS_ABSENT" "alias extra Aury não deve continuar exposto"

printf 'public_ux_smoke: ok\n'
