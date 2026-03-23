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

dev_diag_speed_extract_output="$(ROOT="$ROOT" fish -c 'source $ROOT/bin/aury.fish; aury dev velocidade da rede; echo ---CASE2---; aury dev extrair pacote.zip' 2>&1 || true)"
require_in_output "$dev_diag_speed_extract_output" "trecho original:               velocidade da rede" "'aury dev velocidade da rede' precisa expor o trecho original correto"
require_in_output "$dev_diag_speed_extract_output" "intenção:                      velocidade" "'aury dev velocidade da rede' precisa restaurar a intenção de velocidade"
require_in_output "$dev_diag_speed_extract_output" "domínio:                       rede" "'aury dev velocidade da rede' precisa restaurar o domínio de rede"
require_in_output "$dev_diag_speed_extract_output" "alvo principal:                velocidade da rede" "'aury dev velocidade da rede' precisa restaurar o alvo consolidado"
require_in_output "$dev_diag_speed_extract_output" "resumo:                        Medir a velocidade da rede." "'aury dev velocidade da rede' precisa restaurar o resumo de speedtest"
require_in_output "$dev_diag_speed_extract_output" "trecho original:               extrair pacote.zip" "'aury dev extrair pacote.zip' precisa expor o trecho original correto"
require_in_output "$dev_diag_speed_extract_output" "estado:                        CONSISTENTE" "'aury dev extrair pacote.zip' não pode voltar a parcial"
require_in_output "$dev_diag_speed_extract_output" "arquivo compactado:            pacote.zip" "'aury dev extrair pacote.zip' precisa expor o arquivo compactado"
require_in_output "$dev_diag_speed_extract_output" "destino:                       ./pacote" "'aury dev extrair pacote.zip' precisa restaurar o destino padrão"
require_in_output "$dev_diag_speed_extract_output" "Extrair 'pacote.zip' para './pacote'." "'aury dev extrair pacote.zip' precisa restaurar o resumo com destino padrão"

dev_diag_regression_output="$(ROOT="$ROOT" fish -c 'source $ROOT/bin/aury.fish; aury dev copie a pasta Aury que fica em origem para destino e renomeie ela para Aury-backup; echo ---CASE4---; aury dev remova a pasta projetos/ em Downloads; echo ---CASE5---; aury dev remova teste.txt em Downloads' 2>&1 || true)"
require_in_output "$dev_diag_regression_output" "trecho original:               copie a pasta Aury que fica em origem para destino" "a cópia localizada em aury dev precisa manter o trecho original da regressão"
require_in_output "$dev_diag_regression_output" "origem:                        origem/Aury" "a cópia localizada em aury dev precisa restaurar a origem recomposta"
require_in_output "$dev_diag_regression_output" "destino:                       destino/Aury" "a cópia localizada em aury dev precisa restaurar o destino recomposto"
require_in_output "$dev_diag_regression_output" "trecho original:               renomeie ela para Aury-backup" "a renomeação anafórica em aury dev precisa preservar a segunda ação"
require_in_output "$dev_diag_regression_output" "referência local:              destino/Aury" "a renomeação anafórica em aury dev precisa preservar a referência local específica"
require_in_output "$dev_diag_regression_output" "destino:                       destino/Aury-backup" "a renomeação anafórica em aury dev precisa restaurar a base final correta"
require_in_output "$dev_diag_regression_output" "trecho original:               remova a pasta projetos/ em Downloads" "'aury dev remova a pasta projetos/ em Downloads' precisa expor o trecho original correto"
require_in_output "$dev_diag_regression_output" "alvo principal:                Downloads/projetos/" "'aury dev remova a pasta projetos/ em Downloads' precisa recompor a base correta"
require_in_output "$dev_diag_regression_output" "origem:                        Downloads/projetos/" "'aury dev remova a pasta projetos/ em Downloads' precisa expor a origem recomposta"
require_in_output "$dev_diag_regression_output" "trecho original:               remova teste.txt em Downloads" "'aury dev remova teste.txt em Downloads' precisa expor o trecho original correto"
require_in_output "$dev_diag_regression_output" "tipo:                          arquivo" "'aury dev remova teste.txt em Downloads' precisa permanecer enquadrada como arquivo"
require_in_output "$dev_diag_regression_output" "alvo principal:                Downloads/teste.txt" "'aury dev remova teste.txt em Downloads' precisa recompor o alvo final"
require_in_output "$dev_diag_regression_output" "origem:                        Downloads/teste.txt" "'aury dev remova teste.txt em Downloads' precisa expor a origem recomposta"

dev_diag_anaphoric_output="$(ROOT="$ROOT" fish -c 'source $ROOT/bin/aury.fish; aury dev remover ela; echo ---CASE6B---; aury dev procurar steam e depois remover ele; echo ---CASE6C---; aury dev remova a pasta Aury que fica em Downloads e depois remova ela' 2>&1 || true)"
require_in_output "$dev_diag_anaphoric_output" "trecho original:               remover ela" "'aury dev remover ela' precisa expor o trecho original correto"
require_in_output "$dev_diag_anaphoric_output" "referência local:              ela (não resolvida)" "'aury dev remover ela' precisa manter a referência local explícita"
require_in_output "$dev_diag_anaphoric_output" "não há antecedente seguro nesta ação destrutiva isolada" "'aury dev remover ela' precisa manter o bloqueio honesto"
require_in_output "$dev_diag_anaphoric_output" "trecho original:               remover ele" "'aury dev procurar steam e depois remover ele' precisa preservar a segunda ação destrutiva"
require_in_output "$dev_diag_anaphoric_output" "referência local:              ele" "'aury dev procurar steam e depois remover ele' precisa manter a referência local explícita"
require_in_output "$dev_diag_anaphoric_output" "contexto anterior insuficiente ou incompatível" "'aury dev procurar steam e depois remover ele' precisa expor o contexto anterior incompatível"
require_in_output "$dev_diag_anaphoric_output" "trecho original:               remova ela" "'aury dev remova a pasta Aury que fica em Downloads e depois remova ela' precisa preservar a segunda ação infletida"
require_in_output "$dev_diag_anaphoric_output" "referência local:              Downloads/Aury" "'aury dev remova a pasta Aury que fica em Downloads e depois remova ela' precisa manter a referência local resolvida"
require_in_output "$dev_diag_anaphoric_output" "Remoção de 'Downloads/Aury' reconhecida, mas bloqueada no estado atual." "'aury dev remova ... e depois remova ela' precisa manter o bloqueio prudente com diagnóstico rico"
require_in_output "$dev_diag_anaphoric_output" "runtime legado atual ainda bloqueia continuação destrutiva anafórica equivalente" "'aury dev remova ... e depois remova ela' precisa manter a observabilidade fina"
require_not_in_output "$dev_diag_anaphoric_output" "alvo principal:                ele" "anáfora destrutiva incompatível não pode regredir para alvo genérico"

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

create_located_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$create_located_tmp")
mkdir -p "$create_located_tmp/Downloads"

create_located_output="$(ROOT="$ROOT" TMP="$create_located_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury criar pasta Relatorios em Downloads; aury criar arquivo teste.txt em Downloads; echo ---DEV1---; aury dev criar pasta Relatorios em Downloads; echo ---DEV2---; aury dev crie a pasta Relatorios em Downloads; echo ---DEV3---; aury dev criar arquivo teste.txt em Downloads; echo ---DEV4---; aury dev crie um arquivo teste.txt em Downloads' 2>&1 || true)"
require_in_output "$create_located_output" "eu criei a pasta 'Downloads/Relatorios'" "criação localizada de pasta no modo normal deve materializar o alvo recomposto"
require_in_output "$create_located_output" "eu criei o arquivo 'Downloads/teste.txt'" "criação localizada de arquivo no modo normal deve materializar o alvo recomposto"
require_in_output "$create_located_output" "trecho original:               criar pasta Relatorios em Downloads" "'aury dev criar pasta ... em Downloads' precisa fechar a leitura localizada"
require_in_output "$create_located_output" "trecho original:               crie a pasta Relatorios em Downloads" "'aury dev crie a pasta ... em Downloads' precisa fechar a leitura localizada"
require_in_output "$create_located_output" "trecho original:               criar arquivo teste.txt em Downloads" "'aury dev criar arquivo ... em Downloads' precisa fechar a leitura localizada"
require_in_output "$create_located_output" "trecho original:               crie um arquivo teste.txt em Downloads" "'aury dev crie um arquivo ... em Downloads' precisa fechar a leitura localizada"
require_in_output "$create_located_output" "alvo principal:                Downloads/Relatorios" "criação localizada de pasta em aury dev precisa recompor o alvo final"
require_in_output "$create_located_output" "alvo principal:                Downloads/teste.txt" "criação localizada de arquivo em aury dev precisa recompor o alvo final"
require_in_output "$create_located_output" "destino:                       Downloads" "criação localizada em aury dev precisa expor a base de destino"
require_in_output "$create_located_output" "localização conversacional:    nome: Relatorios | base: Downloads | conector: em" "criação localizada de pasta em aury dev precisa expor a localização conversacional"
require_in_output "$create_located_output" "localização conversacional:    nome: teste.txt | base: Downloads | conector: em" "criação localizada de arquivo em aury dev precisa expor a localização conversacional"
require_in_output "$create_located_output" "Criar 'Downloads/Relatorios'." "criação localizada de pasta em aury dev precisa resumir o alvo recomposto"
require_in_output "$create_located_output" "Criar 'Downloads/teste.txt'." "criação localizada de arquivo em aury dev precisa resumir o alvo recomposto"

if [[ ! -d "$create_located_tmp/Downloads/Relatorios" || ! -f "$create_located_tmp/Downloads/teste.txt" ]]; then
    fail "criação localizada precisa materializar apenas os alvos esperados dentro de Downloads"
fi

create_implicit_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$create_implicit_tmp")
mkdir -p "$create_implicit_tmp/Downloads"

create_implicit_output="$(ROOT="$ROOT" TMP="$create_implicit_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury criar teste.txt; aury crie teste.txt; aury criar teste.txt em Downloads; aury crie teste.txt em Downloads; echo ---DEV1---; aury dev criar teste.txt; echo ---DEV2---; aury dev crie teste.txt; echo ---DEV3---; aury dev criar teste.txt em Downloads; echo ---DEV4---; aury dev crie teste.txt em Downloads' 2>&1 || true)"
require_in_output "$create_implicit_output" "eu criei o arquivo 'teste.txt'" "criação implícita simples no modo normal deve continuar tratando o alvo como arquivo"
require_in_output "$create_implicit_output" "eu criei o arquivo 'Downloads/teste.txt'" "criação implícita localizada no modo normal deve continuar tratando o alvo como arquivo"
require_in_output "$create_implicit_output" "trecho original:               criar teste.txt" "'aury dev criar teste.txt' precisa fechar a leitura implícita de arquivo"
require_in_output "$create_implicit_output" "trecho original:               crie teste.txt" "'aury dev crie teste.txt' precisa fechar a leitura implícita de arquivo"
require_in_output "$create_implicit_output" "trecho original:               criar teste.txt em Downloads" "'aury dev criar teste.txt em Downloads' precisa fechar a leitura implícita localizada"
require_in_output "$create_implicit_output" "trecho original:               crie teste.txt em Downloads" "'aury dev crie teste.txt em Downloads' precisa fechar a leitura implícita localizada"
require_in_output "$create_implicit_output" "tipo:                          arquivo" "criação implícita em aury dev precisa permanecer enquadrada como arquivo"
require_in_output "$create_implicit_output" "alvo principal:                teste.txt" "criação implícita simples em aury dev precisa preservar o alvo do arquivo"
require_in_output "$create_implicit_output" "alvo principal:                Downloads/teste.txt" "criação implícita localizada em aury dev precisa recompor o alvo final"
require_in_output "$create_implicit_output" "destino:                       Downloads" "criação implícita localizada em aury dev precisa expor a base de destino"
require_in_output "$create_implicit_output" "localização conversacional:    nome: teste.txt | base: Downloads | conector: em" "criação implícita localizada em aury dev precisa expor a localização conversacional"
require_in_output "$create_implicit_output" "Criar 'teste.txt'." "criação implícita simples em aury dev precisa resumir o arquivo"
require_in_output "$create_implicit_output" "Criar 'Downloads/teste.txt'." "criação implícita localizada em aury dev precisa resumir o alvo recomposto"

if [[ ! -f "$create_implicit_tmp/teste.txt" || ! -f "$create_implicit_tmp/Downloads/teste.txt" ]]; then
    fail "criação implícita precisa materializar apenas os arquivos esperados"
fi

create_implicit_folder_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$create_implicit_folder_tmp")
mkdir -p "$create_implicit_folder_tmp/Downloads"

create_implicit_folder_output="$(ROOT="$ROOT" TMP="$create_implicit_folder_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury criar projetos/; aury crie projetos/; aury criar projetos/ em Downloads; aury crie projetos/ em Downloads; aury criar pasta projetos/ em Downloads; echo ---DEV1---; aury dev criar projetos/; echo ---DEV2---; aury dev crie projetos/; echo ---DEV3---; aury dev criar projetos/ em Downloads; echo ---DEV4---; aury dev crie projetos/ em Downloads; echo ---DEV5---; aury dev criar pasta projetos/ em Downloads' 2>&1 || true)"
require_in_output "$create_implicit_folder_output" "eu criei a pasta 'projetos/'" "criação implícita simples de pasta no modo normal deve continuar inferindo pasta"
require_in_output "$create_implicit_folder_output" "eu criei a pasta 'Downloads/projetos/'" "criação implícita localizada de pasta no modo normal deve recompôr a base correta"
require_in_output "$create_implicit_folder_output" "trecho original:               criar projetos/" "'aury dev criar projetos/' precisa fechar a inferência implícita de pasta"
require_in_output "$create_implicit_folder_output" "trecho original:               crie projetos/" "'aury dev crie projetos/' precisa fechar a inferência implícita de pasta"
require_in_output "$create_implicit_folder_output" "trecho original:               criar projetos/ em Downloads" "'aury dev criar projetos/ em Downloads' precisa fechar a inferência implícita localizada de pasta"
require_in_output "$create_implicit_folder_output" "trecho original:               crie projetos/ em Downloads" "'aury dev crie projetos/ em Downloads' precisa fechar a inferência implícita localizada de pasta"
require_in_output "$create_implicit_folder_output" "trecho original:               criar pasta projetos/ em Downloads" "'aury dev criar pasta projetos/ em Downloads' precisa preservar a base localizada com barra final"
require_in_output "$create_implicit_folder_output" "tipo:                          pasta" "criação implícita de pasta em aury dev precisa permanecer enquadrada como pasta"
require_in_output "$create_implicit_folder_output" "alvo principal:                projetos/" "criação implícita de pasta em aury dev precisa preservar o alvo inferido"
require_in_output "$create_implicit_folder_output" "alvo principal:                Downloads/projetos/" "criação implícita localizada de pasta em aury dev precisa recompor o alvo final"
require_in_output "$create_implicit_folder_output" "destino:                       Downloads" "criação implícita localizada de pasta em aury dev precisa expor a base de destino"
require_in_output "$create_implicit_folder_output" "localização conversacional:    nome: projetos/ | base: Downloads | conector: em" "criação implícita localizada de pasta em aury dev precisa expor a localização conversacional"
require_in_output "$create_implicit_folder_output" "Criar 'projetos/'." "criação implícita de pasta em aury dev precisa resumir o alvo efetivamente fechado"
require_in_output "$create_implicit_folder_output" "Criar 'Downloads/projetos/'." "criação implícita localizada de pasta em aury dev precisa resumir o alvo recomposto"

if [[ ! -d "$create_implicit_folder_tmp/projetos" || ! -d "$create_implicit_folder_tmp/Downloads/projetos" ]]; then
    fail "criação implícita de pasta precisa refletir o comportamento canônico atual do Fish com e sem base localizada"
fi

confirm_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$confirm_tmp")

confirm_output="$(ROOT="$ROOT" TMP="$confirm_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; touch teste.txt; printf "n\n" | aury remover arquivo teste.txt; if test -e teste.txt; echo STILL_PRESENT; else; echo REMOVED; end' 2>&1 || true)"
require_in_output "$confirm_output" "Confirma? [s/N]" "remoção precisa pedir confirmação explícita"
require_in_output "$confirm_output" "eu não removi 'teste.txt'." "negação de confirmação deve cancelar a remoção"
require_in_output "$confirm_output" "STILL_PRESENT" "arquivo deve permanecer quando a confirmação não for positiva"

remove_simple_file_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$remove_simple_file_tmp")

remove_simple_file_output="$(ROOT="$ROOT" TMP="$remove_simple_file_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; touch teste.txt; printf \"n\n\" | aury remover teste.txt; printf \"n\n\" | aury remova teste.txt; if test -e teste.txt; echo STILL_PRESENT; else; echo REMOVED; end; echo ---DEV1---; aury dev remover teste.txt; echo ---DEV2---; aury dev remova teste.txt' 2>&1 || true)"
require_in_output "$remove_simple_file_output" "Confirma? [s/N]" "remoção curta simples de arquivo precisa continuar exigindo confirmação destrutiva"
require_in_output "$remove_simple_file_output" "eu não removi 'teste.txt'." "negação de confirmação precisa cancelar a remoção curta simples de arquivo"
require_in_output "$remove_simple_file_output" "STILL_PRESENT" "remoção curta simples negada precisa preservar o arquivo local"
require_in_output "$remove_simple_file_output" "trecho original:               remover teste.txt" "'aury dev remover teste.txt' precisa fechar a leitura curta simples de arquivo"
require_in_output "$remove_simple_file_output" "trecho original:               remova teste.txt" "'aury dev remova teste.txt' precisa fechar a leitura curta simples de arquivo"
require_in_output "$remove_simple_file_output" "domínio:                       arquivo" "remoção curta simples de arquivo em aury dev não pode continuar enquadrada como pacote"
require_in_output "$remove_simple_file_output" "tipo:                          arquivo" "remoção curta simples de arquivo em aury dev precisa permanecer enquadrada como arquivo"
require_in_output "$remove_simple_file_output" "alvo principal:                teste.txt" "remoção curta simples de arquivo em aury dev precisa preservar o alvo do arquivo"
require_in_output "$remove_simple_file_output" "Remover 'teste.txt'." "remoção curta simples de arquivo em aury dev precisa resumir o alvo do arquivo"
require_in_output "$remove_simple_file_output" "confirmação no adaptador Fish" "remoção curta simples de arquivo em aury dev precisa manter a prudência destrutiva no adaptador"
require_not_in_output "$remove_simple_file_output" "domínio:                       pacote" "remoção curta simples de arquivo em aury dev não pode recair para pacote"

remove_simple_folder_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$remove_simple_folder_tmp")

remove_simple_folder_output="$(ROOT="$ROOT" TMP="$remove_simple_folder_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; mkdir -p projetos; printf \"n\n\" | aury remover projetos/; printf \"n\n\" | aury remova projetos/; if test -d projetos; echo STILL_PRESENT; else; echo REMOVED; end; echo ---DEV1---; aury dev remover projetos/; echo ---DEV2---; aury dev remova projetos/' 2>&1 || true)"
require_in_output "$remove_simple_folder_output" "Confirma? [s/N]" "remoção curta simples de pasta precisa continuar exigindo confirmação destrutiva"
require_in_output "$remove_simple_folder_output" "eu não removi 'projetos/'." "negação de confirmação precisa cancelar a remoção curta simples de pasta"
require_in_output "$remove_simple_folder_output" "STILL_PRESENT" "remoção curta simples negada precisa preservar a pasta local"
require_in_output "$remove_simple_folder_output" "trecho original:               remover projetos/" "'aury dev remover projetos/' precisa fechar a leitura curta simples de pasta"
require_in_output "$remove_simple_folder_output" "trecho original:               remova projetos/" "'aury dev remova projetos/' precisa fechar a leitura curta simples de pasta"
require_in_output "$remove_simple_folder_output" "domínio:                       arquivo" "remoção curta simples de pasta em aury dev não pode continuar enquadrada como pacote"
require_in_output "$remove_simple_folder_output" "tipo:                          pasta" "remoção curta simples de pasta em aury dev precisa permanecer enquadrada como pasta"
require_in_output "$remove_simple_folder_output" "alvo principal:                projetos/" "remoção curta simples de pasta em aury dev precisa preservar o alvo da pasta"
require_in_output "$remove_simple_folder_output" "Remover 'projetos/'." "remoção curta simples de pasta em aury dev precisa resumir o alvo da pasta"
require_in_output "$remove_simple_folder_output" "confirmação no adaptador Fish" "remoção curta simples de pasta em aury dev precisa manter a prudência destrutiva no adaptador"
require_not_in_output "$remove_simple_folder_output" "domínio:                       pacote" "remoção curta simples de pasta em aury dev não pode recair para pacote"

remove_located_file_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$remove_located_file_tmp")
mkdir -p "$remove_located_file_tmp/Downloads"
touch "$remove_located_file_tmp/Downloads/teste.txt"

remove_located_file_output="$(ROOT="$ROOT" TMP="$remove_located_file_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; printf \"n\n\" | aury remover teste.txt em Downloads; printf \"n\n\" | aury remova teste.txt em Downloads; echo ---DEV1---; aury dev remover teste.txt em Downloads; echo ---DEV2---; aury dev remova teste.txt em Downloads' 2>&1 || true)"
require_in_output "$remove_located_file_output" "Confirma? [s/N]" "remoção localizada curta de arquivo precisa continuar exigindo confirmação destrutiva"
require_in_output "$remove_located_file_output" "eu não removi 'Downloads/teste.txt'." "negação de confirmação precisa cancelar a remoção localizada curta recomposta"
require_in_output "$remove_located_file_output" "trecho original:               remover teste.txt em Downloads" "'aury dev remover teste.txt em Downloads' precisa fechar a leitura localizada curta de arquivo"
require_in_output "$remove_located_file_output" "trecho original:               remova teste.txt em Downloads" "'aury dev remova teste.txt em Downloads' precisa fechar a leitura localizada curta de arquivo"
require_in_output "$remove_located_file_output" "domínio:                       arquivo" "remoção localizada curta de arquivo em aury dev não pode continuar enquadrada como pacote"
require_in_output "$remove_located_file_output" "tipo:                          arquivo" "remoção localizada curta de arquivo em aury dev precisa permanecer enquadrada como arquivo"
require_in_output "$remove_located_file_output" "alvo principal:                Downloads/teste.txt" "remoção localizada curta de arquivo em aury dev precisa recompor o alvo final"
require_in_output "$remove_located_file_output" "origem:                        Downloads/teste.txt" "remoção localizada curta de arquivo em aury dev precisa expor a origem recomposta"
require_in_output "$remove_located_file_output" "Remover 'Downloads/teste.txt'." "remoção localizada curta de arquivo em aury dev precisa resumir o alvo recomposto"
require_in_output "$remove_located_file_output" "localização conversacional simples usada para recompor a base 'Downloads'" "remoção localizada curta de arquivo em aury dev precisa registrar a recomposição da base"

if [[ ! -f "$remove_located_file_tmp/Downloads/teste.txt" ]]; then
    fail "remoção localizada curta de arquivo com confirmação negada precisa preservar o alvo recomposto em Downloads"
fi

remove_located_folder_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$remove_located_folder_tmp")
mkdir -p "$remove_located_folder_tmp/Downloads/projetos"

remove_located_folder_output="$(ROOT="$ROOT" TMP="$remove_located_folder_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; printf \"n\n\" | aury remover projetos/ em Downloads; printf \"n\n\" | aury remova projetos/ em Downloads; printf \"n\n\" | aury remover a pasta projetos/ em Downloads; echo ---DEV1---; aury dev remover projetos/ em Downloads; echo ---DEV2---; aury dev remova projetos/ em Downloads; echo ---DEV3---; aury dev remover a pasta projetos/ em Downloads' 2>&1 || true)"
require_in_output "$remove_located_folder_output" "Confirma? [s/N]" "remoção localizada de pasta precisa continuar exigindo confirmação destrutiva"
require_in_output "$remove_located_folder_output" "eu não removi 'Downloads/projetos/'." "negação de confirmação precisa cancelar a remoção localizada recomposta"
require_in_output "$remove_located_folder_output" "trecho original:               remover projetos/ em Downloads" "'aury dev remover projetos/ em Downloads' precisa fechar a leitura localizada de pasta"
require_in_output "$remove_located_folder_output" "trecho original:               remova projetos/ em Downloads" "'aury dev remova projetos/ em Downloads' precisa fechar a leitura localizada de pasta"
require_in_output "$remove_located_folder_output" "trecho original:               remover a pasta projetos/ em Downloads" "'aury dev remover a pasta projetos/ em Downloads' precisa preservar a base localizada"
require_in_output "$remove_located_folder_output" "domínio:                       arquivo" "remoção localizada de pasta em aury dev não pode continuar enquadrada como pacote"
require_in_output "$remove_located_folder_output" "tipo:                          pasta" "remoção localizada de pasta em aury dev precisa permanecer enquadrada como pasta"
require_in_output "$remove_located_folder_output" "alvo principal:                Downloads/projetos/" "remoção localizada de pasta em aury dev precisa recompor o alvo final"
require_in_output "$remove_located_folder_output" "origem:                        Downloads/projetos/" "remoção localizada de pasta em aury dev precisa expor a origem recomposta"
require_in_output "$remove_located_folder_output" "Remover 'Downloads/projetos/'." "remoção localizada de pasta em aury dev precisa resumir o alvo recomposto"
require_in_output "$remove_located_folder_output" "localização conversacional simples usada para recompor a base 'Downloads'" "remoção localizada de pasta em aury dev precisa registrar a recomposição da base"

if [[ ! -d "$remove_located_folder_tmp/Downloads/projetos" ]]; then
    fail "remoção localizada de pasta com confirmação negada precisa preservar o alvo recomposto em Downloads"
fi

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

compact_zip_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$compact_zip_tmp")
mkdir -p "$compact_zip_tmp/bin"
printf 'abc\n' > "$compact_zip_tmp/teste.txt"

cat > "$compact_zip_tmp/bin/zip" <<'EOF'
#!/usr/bin/env bash
archive="$2"
printf 'zip\n' > "$archive"
EOF
chmod +x "$compact_zip_tmp/bin/zip"

compact_zip_output="$(ROOT="$ROOT" TMP="$compact_zip_tmp" PATH="$compact_zip_tmp/bin:$PATH" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury compactar arquivo teste.txt para teste.zip; if test -f teste.zip; echo ZIP_CREATED; else; echo ZIP_MISSING; end' 2>&1 || true)"
require_in_output "$compact_zip_output" "Pronto, eu compactei 'teste.txt' em 'teste.zip'." "compactação simples em zip precisa materializar a mensagem pública de sucesso"
require_in_output "$compact_zip_output" "ZIP_CREATED" "compactação simples em zip precisa criar o arquivo final"

if compgen -G "$compact_zip_tmp/.aury-compact.*" >/dev/null; then
    fail "compactação simples em zip não pode deixar artefato temporário aparente"
fi

compact_tar_tmp="$(mktemp -d /tmp/aury-public-ux-XXXXXX)"
tmpdirs+=("$compact_tar_tmp")
mkdir -p "$compact_tar_tmp/bin" "$compact_tar_tmp/projetos"

cat > "$compact_tar_tmp/bin/tar" <<'EOF'
#!/usr/bin/env bash
archive="$2"
printf 'tar\n' > "$archive"
EOF
chmod +x "$compact_tar_tmp/bin/tar"

compact_tar_output="$(ROOT="$ROOT" TMP="$compact_tar_tmp" PATH="$compact_tar_tmp/bin:$PATH" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury compactar pasta projetos/ para projetos.tar.gz; if test -f projetos.tar.gz; echo TAR_CREATED; else; echo TAR_MISSING; end' 2>&1 || true)"
require_in_output "$compact_tar_output" "Pronto, eu compactei 'projetos/' em 'projetos.tar.gz'." "compactação simples em tar.gz precisa materializar a mensagem pública de sucesso"
require_in_output "$compact_tar_output" "TAR_CREATED" "compactação simples em tar.gz precisa criar o arquivo final"

compact_missing_output="$(ROOT="$ROOT" TMP="$compact_zip_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury compactar arquivo ausente.txt para teste.zip' 2>&1 || true)"
require_in_output "$compact_missing_output" "não encontrei o arquivo 'ausente.txt' para compactar." "compactação com origem inexistente precisa falhar com mensagem honesta"

compact_invalid_output="$(ROOT="$ROOT" TMP="$compact_zip_tmp" fish -c 'source $ROOT/bin/aury.fish; cd $TMP; aury compactar arquivo teste.txt para saida/teste.zip' 2>&1 || true)"
require_in_output "$compact_invalid_output" "o arquivo de saída precisa ser um caminho válido terminado em .zip ou .tar.gz." "compactação com saída inválida precisa falhar com mensagem honesta"


help_output="$(fish -c "source '$ROOT/bin/aury.fish'; aury ajuda" 2>&1 || true)"
require_in_output "$help_output" "💜 Aury" "ajuda precisa continuar disponível"
require_in_output "$help_output" "aury dev <frase> continua como relatório canônico da linha 1.x." "ajuda precisa manter 'aury dev <frase>' como relatório principal"
require_in_output "$help_output" "aury dev sem frase fica como verificação local curta do adaptador Fish, em uso secundário nesta linha." "ajuda precisa declarar o enquadramento final de 'aury dev' sem frase"
require_not_in_output "$help_output" "provisório" "ajuda não deve mais tratar 'aury dev' sem frase como provisório"

version_expected="$(cat "$ROOT/VERSION")"
version_output="$(fish -c "source '$ROOT/bin/aury.fish'; aury --version" 2>&1 || true)"
require_in_output "$version_output" "$version_expected" "version precisa refletir VERSION"

dev_usage_output="$(fish -c "source '$ROOT/bin/aury.fish'; aury dev" 2>&1 || true)"
require_in_output "$dev_usage_output" "🛠 verificação local do adaptador Fish" "'aury dev' sem frase precisa continuar disponível como verificação local"
require_in_output "$dev_usage_output" "Escopo: verificação local curta do adaptador Fish, em uso secundário nesta linha. O relatório canônico exige uma frase." "'aury dev' sem frase precisa declarar o escopo real do adaptador"
require_in_output "$dev_usage_output" "Use: aury dev <frase>" "'aury dev' sem frase precisa orientar o uso correto"
require_not_in_output "$dev_usage_output" "provisório" "'aury dev' sem frase não deve soar provisório"

ay_help_output="$(fish -c "source '$ROOT/bin/aury.fish'; source '$ROOT/bin/ay.fish'; ay ajuda" 2>&1 || true)"
require_in_output "$ay_help_output" "💜 Aury" "ay ajuda precisa continuar disponível"

ay_version_output="$(fish -c "source '$ROOT/bin/aury.fish'; source '$ROOT/bin/ay.fish'; ay --version" 2>&1 || true)"
require_in_output "$ay_version_output" "$version_expected" "ay --version precisa refletir VERSION"

alias_check_output="$(fish -c "source '$ROOT/bin/aury.fish'; functions -q Aury; and echo ALIAS_PRESENT; or echo ALIAS_ABSENT" 2>&1 || true)"
require_in_output "$alias_check_output" "ALIAS_ABSENT" "alias extra Aury não deve continuar exposto"

printf 'public_ux_smoke: ok\n'
