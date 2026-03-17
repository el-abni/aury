# ==========================================================
# 💜 Aury
# Terminal Assistant for CachyOS
# Shell: fish
# ==========================================================

# -------------------------------------------------
# mensagens
# -------------------------------------------------

# ==========================================================
# Seção 1 — Metadados, mensagens e ajuda
# 1.1 Mensagens
# ==========================================================

function __aury_msg_error --argument-names text
    echo "❌ $text"
end

function __aury_msg_ok --argument-names text
    echo "✅ $text"
end

function __aury_msg_info --argument-names text
    echo "ℹ️ $text"
end

function __aury_msg_warn --argument-names text
    echo "⚠️ $text"
end

# -------------------------------------------------
# dicionários
# -------------------------------------------------

# -------------------------------------------------
# 1.2 Dicionários-base da v1.4.x
# -------------------------------------------------

function __aury_intents
    printf '%s\n' ajuda reload dev atualizar otimizar status procurar instalar remover criar copiar mover renomear extrair ping ver internet abrir
end

function __aury_internal_intents
    printf '%s\n' ajuda reload dev
end

function __aury_file_intents
    printf '%s\n' criar copiar mover renomear extrair
end

function __aury_system_keywords
    printf '%s\n' cpu memória disco gpu processos status sistema atualizar otimizar
end

function __aury_network_keywords
    printf '%s\n' ip internet ping
end

function __aury_package_keywords
    printf '%s\n' pacote instalar procurar
end

# -------------------------------------------------
# ajuda
# -------------------------------------------------

# -------------------------------------------------
# 1.3 Help
# -------------------------------------------------

function __aury_show_help
    echo "
💜 Aury v1.4.3

PACOTES
aury instalar firefox
aury instala firefox
aury baixa o firefox
aury pode instalar firefox
aury quero instalar obs studio
aury Aury, instala o obs studio.
aury remover vlc
aury procurar steam

SISTEMA
aury atualizar sistema
aury otimizar sistema
aury atualiza, otimiza e baixa o firefox
aury status
aury mostrar cpu
aury mostrar o status do sistema
aury checar memória
aury ver cpu e memória

REDE
aury ver ip
aury testar internet
aury ping google.com

ARQUIVOS
aury criar arquivo teste.txt
aury criar teste.txt
aury criar pasta projetos
aury copiar arquivo teste.txt backup.txt
aury mover arquivo teste.txt pasta/teste.txt
aury renomear arquivo teste.txt novo.txt
aury cria um arquivo teste.txt
aury cria a pasta projetos
aury apaga o arquivo teste.txt
aury deleta backup.txt
aury remove o arquivo teste.txt
aury extrair teste.zip
aury descompacte backup.tar.gz
aury extraia teste.tar para a pasta que fica em /usr/steam

EXTRAS
aury reload
aury dev
"
end

# -------------------------------------------------
# normalização de linguagem
# -------------------------------------------------

# ==========================================================
# Seção 2 — Normalização, conectores e preparação de fala
# 2.1 Normalização base
# ==========================================================

function __aury_normalize_token --argument-names tok
    set -l t (string lower -- $tok)
    set t (string replace -ra '^[[:punct:]]+|[[:punct:]]+$' '' -- $t)

    switch $t
        case ''
            echo __IGNORE__

        case o a os as um uma uns umas de dos das com sobre ao aos à às por porgentileza pfvr porfa gentileza favor porfavor me mim comigo ai aí aury você voce que isso isto esse essa este esta aquela aquele aquelas aqueles ali lá la aqui
            echo __IGNORE__

        case e
            echo e

        case quero queria preciso gostaria pode poderia poderiame poderia-me conseguimos consegue tenta tentar tente
            echo $t

        case para pra pro
            echo para

        case dentro
            echo em

        case em no na nos nas do da
            echo $t

        case ajuda help socorro manual comandos comando
            echo ajuda

        case reload recarregar reiniciar
            echo reload

        case dev developer desenvolvedor diagnostico diagnóstico validar verificar debug
            echo dev

        case instalar instala instale instalaram adicionar adiciona adicione add instalr isntalar instal botar colocar baixa baixar baixe baixarame download baixarpra
            echo instalar

        case remover remove remov deletar deleta delete excluir apagar apaga apague desinstalar desinstala desinstale uninstall removr remvoe tirar
            echo remover

        case procurar procura procure buscar busca busque pesquise pesquisar acha achar encontrar localizar procra procuar pesquisr consultar pesquisa
            echo procurar

        case criar cria crie gerar fazer monte montar
            echo criar

        case copiar copia cp duplicar copar copiarr clone clonar
            echo copiar

        case mover move mv movr moevr enviar deslocar
            echo mover

        case renomear renomeia renomeie rename renomar renoemar renomea nomear
            echo renomear

        case extrair extraia extrai extraira extrairá descompactar descompacte descompacta descomprima descomprimir desarquivar
            echo extrair

        case status estado info infos informação informacoes informações situacao situação
            echo status

        case ver veja mostra mostrar exibir listar checar checa consulte consultar visualizar olhar olhe monitorar
            echo ver

        case atualizar atualiza atualize update upgrade sincronizar atualizara
            echo atualizar

        case otimizar otimiza otimize limpar limpa melhorar acelerar
            echo otimizar

        case abrir abre open
            echo abrir

        case testar teste internet rede conexão conexao conectar online
            echo internet

        case ping
            echo ping

        case pasta diretório diretorio folder diretoro diretórios diretorios
            echo pasta

        case arquivo ficheiro file documento
            echo arquivo

        case pacote pacotes app aplicativo aplicativos programa programas
            echo pacote

        case sistema computador máquina maquina pc
            echo sistema

        case processo processos tarefa tarefas
            echo processos

        case memoria memora memori ram memória
            echo memória

        case disco armazenamento hd ssd espaço espaco
            echo disco

        case gpu video vídeo grafico gráfico grafica gráfica placa
            echo gpu

        case cpu processador
            echo cpu

        case ip endereço endereco
            echo ip

        case '*'
            echo $t
    end
end

# -------------------------------------------------
# 2.2 Classificadores rápidos de token
# -------------------------------------------------

function __aury_is_command_token --argument-names tok
    set -l normalized (__aury_normalize_token $tok)

    if contains -- $normalized (__aury_intents)
        return 0
    end

    return 1
end

function __aury_is_aux_token --argument-names tok
    if contains -- $tok quero queria preciso gostaria pode poderia poderiame poderia-me conseguimos consegue quer vamos vou iria iria-me
        return 0
    end

    return 1
end

function __aury_is_filler_token --argument-names tok
    if contains -- $tok __IGNORE__
        return 0
    end

    return 1
end

function __aury_is_connector_token --argument-names tok
    if contains -- $tok para em no na nos nas do da
        return 0
    end

    return 1
end

function __aury_can_expand_shared_intent --argument-names intent
    if contains -- $intent ver instalar remover procurar
        return 0
    end

    return 1
end


function __aury_has_any --argument-names haystack_varname
    set -l haystack $$haystack_varname
    set -e argv[1]

    for item in $argv
        if contains -- $item $haystack
            return 0
        end
    end

    return 1
end

function __aury_has_pathlike_tokens
    set -l words $argv

    for word in $words
        if string match -rq '[/~]' -- $word
            return 0
        end

        if string match -rq '\.[[:alnum:]_-]+$' -- $word
            return 0
        end
    end

    return 1
end

function __aury_is_vocative_token --argument-names tok
    set -l t (string lower -- $tok)
    set t (string replace -ra '^[[:punct:]]+|[[:punct:]]+$' '' -- $t)

    if test "$t" = "aury"
        return 0
    end

    return 1
end

# -------------------------------------------------
# 2.3 Pré-processamento bruto
# -------------------------------------------------

function __aury_preprocess_input
    set -l tokens $argv

    while test (count $tokens) -gt 0
        if __aury_is_vocative_token $tokens[1]
            set tokens $tokens[2..-1]
            continue
        end

        break
    end

    printf '%s\n' $tokens
end

# ==========================================================
# Seção 3 — Split de ações, expansão e interpretação
# 3.1 Busca e filtragem de tokens
# ==========================================================

function __aury_find_token_index --argument-names needle
    set -e argv[1]
    set -l words $argv
    set -l i 1

    while test $i -le (count $words)
        if test "$words[$i]" = "$needle"
            echo $i
            return 0
        end

        set i (math $i + 1)
    end

    return 1
end

function __aury_find_first_intent_index
    set -l words $argv
    set -l i 1

    while test $i -le (count $words)
        set -l tok $words[$i]

        if __aury_is_aux_token $tok
            set i (math $i + 1)
            continue
        end

        if contains -- $tok (__aury_intents)
            echo $i
            return 0
        end

        set i (math $i + 1)
    end

    return 1
end

function __aury_tokens_after --argument-names index
    set -e argv[1]
    set -l words $argv

    if test (count $words) -le $index
        return 0
    end

    printf '%s\n' $words[(math $index + 1)..-1]
end

function __aury_filter_interpretable_words
    set -l norm_words $argv
    set -l i 1

    while test $i -le (count $norm_words)
        set -l tok $norm_words[$i]

        if __aury_is_filler_token $tok
            set i (math $i + 1)
            continue
        end

        if test "$tok" = "e"
            echo $tok
            set i (math $i + 1)
            continue
        end

        echo $tok
        set i (math $i + 1)
    end
end

function __aury_collect_intent_indexes
    set -l words $argv
    set -l indexes
    set -l i 1

    while test $i -le (count $words)
        if contains -- $words[$i] (__aury_intents)
            set indexes $indexes $i
        end

        set i (math $i + 1)
    end

    printf '%s\n' $indexes
end

function __aury_clean_segment_edges
    set -l words $argv

    while test (count $words) -gt 0
        set -l first $words[1]
        if test "$first" = "e"; or __aury_is_connector_token $first
            set words $words[2..-1]
            continue
        end
        break
    end

    while test (count $words) -gt 0
        set -l last $words[-1]
        if test "$last" = "e"; or __aury_is_connector_token $last
            set words $words[1..-2]
            continue
        end
        break
    end

    printf '%s\n' $words
end

# -------------------------------------------------
# 3.2 Expansão de ações e alvos compartilhados
# -------------------------------------------------

function __aury_emit_expanded_action
    set -l norm_words $argv[1]
    set -l orig_words $argv[2]

    if test -z "$norm_words"
        return 1
    end

    echo "NORM:$norm_words"
    if test -n "$orig_words"
        echo "ORIG:$orig_words"
    else
        echo "ORIG:"
    end
    echo "__AURY_EXPANDED_ACTION_BREAK__"
end


function __aury_collect_system_targets_from_words
    set -l words $argv
    set -l valid cpu memória disco gpu processos status sistema
    set -l collected

    for tok in $words
        if test "$tok" = "ver"
            continue
        end

        if test "$tok" = "e"
            continue
        end

        if __aury_is_connector_token $tok
            continue
        end

        if contains -- $tok $valid
            if not contains -- $tok $collected
                set collected $collected $tok
            end
            continue
        end

        return 1
    end

    if test (count $collected) -le 1
        return 1
    end

    printf '%s\n' $collected
end

function __aury_expand_system_targets --argument-names intent
    set -e argv[1]
    set -l words $argv
    set -l targets (__aury_collect_system_targets_from_words $words)

    if test (count $targets) -le 1
        return 1
    end

    for tok in $targets
        __aury_emit_expanded_action (string join \t -- $intent $tok) (string join \t -- $intent $tok)
    end

    return 0
end


function __aury_expand_interpreted_actions
    set -l norm_words $norm_words_global
    set -l orig_words $orig_words_global
    set -l intent_indexes (__aury_collect_intent_indexes $norm_words)
    set -l intent (__aury_detect_intent $norm_words)

    # Caso 0: intenção única de sistema sem alvo explícito
    if test (count $norm_words) -eq 1
        if test "$intent" = "atualizar"
            __aury_emit_expanded_action (string join \t -- atualizar sistema) (string join \t -- $orig_words)
            return 0
        else if test "$intent" = "otimizar"
            __aury_emit_expanded_action (string join \t -- otimizar sistema) (string join \t -- $orig_words)
            return 0
        else if test "$intent" = "status"
            __aury_emit_expanded_action (string join \t -- ver status sistema) (string join \t -- $orig_words)
            return 0
        end
    end

    # Caso 1: múltiplas intenções explícitas na mesma frase
    if test (count $intent_indexes) -gt 1
        set -l idx 1

        while test $idx -le (count $intent_indexes)
            set -l start $intent_indexes[$idx]
            set -l finish (count $norm_words)

            if test $idx -lt (count $intent_indexes)
                set finish (math $intent_indexes[(math $idx + 1)] - 1)
            end

            set -l segment_norm (__aury_clean_segment_edges $norm_words[$start..$finish])
            set -l segment_orig (__aury_clean_segment_edges $orig_words[$start..$finish])

            if test (count $segment_norm) -eq 1
                if test "$segment_norm[1]" = "atualizar"
                    set segment_norm atualizar sistema
                else if test "$segment_norm[1]" = "otimizar"
                    set segment_norm otimizar sistema
                else if test "$segment_norm[1]" = "status"
                    set segment_norm ver status sistema
                end
            end

            if test (count $segment_norm) -gt 0
                __aury_emit_expanded_action (string join \t -- $segment_norm) (string join \t -- $segment_orig)
            end

            set idx (math $idx + 1)
        end

        return 0
    end

    # Caso 2A: uma intenção "ver" compartilhada por múltiplos alvos de sistema
    if test "$intent" = "ver"
        if __aury_expand_system_targets $intent $norm_words
            return 0
        end
    end

    # Caso 2B: uma intenção compartilhada por vários alvos separados por "e"
    if not __aury_can_expand_shared_intent $intent
        return 1
    end

    set -l intent_idx (__aury_find_first_intent_index $norm_words)

    if test -z "$intent_idx"
        return 1
    end

    set -l target_norm $norm_words[(math $intent_idx + 1)..-1]
    set -l target_orig $orig_words[(math $intent_idx + 1)..-1]

    if not contains -- e $target_norm
        return 1
    end

    set -l groups_norm
    set -l groups_orig
    set -l current_norm
    set -l current_orig
    set -l i 1

    while test $i -le (count $target_norm)
        set -l tok $target_norm[$i]
        set -l orig_tok ''
        if test $i -le (count $target_orig)
            set orig_tok $target_orig[$i]
        end

        if test "$tok" = "e"
            if test (count $current_norm) -gt 0
                set -l cleaned_norm (__aury_clean_segment_edges $current_norm)
                set -l cleaned_orig (__aury_clean_segment_edges $current_orig)

                if test (count $cleaned_norm) -gt 0
                    set groups_norm $groups_norm (string join \t -- $cleaned_norm)
                    if test (count $cleaned_orig) -gt 0
                        set groups_orig $groups_orig (string join \t -- $cleaned_orig)
                    else
                        set groups_orig $groups_orig ''
                    end
                end
            end

            set current_norm
            set current_orig
            set i (math $i + 1)
            continue
        end

        if contains -- $tok (__aury_intents)
            return 1
        end

        set current_norm $current_norm $tok
        if test -n "$orig_tok"
            set current_orig $current_orig $orig_tok
        end

        set i (math $i + 1)
    end

    if test (count $current_norm) -gt 0
        set -l cleaned_norm (__aury_clean_segment_edges $current_norm)
        set -l cleaned_orig (__aury_clean_segment_edges $current_orig)

        if test (count $cleaned_norm) -gt 0
            set groups_norm $groups_norm (string join \t -- $cleaned_norm)
            if test (count $cleaned_orig) -gt 0
                set groups_orig $groups_orig (string join \t -- $cleaned_orig)
            else
                set groups_orig $groups_orig ''
            end
        end
    end

    if test (count $groups_norm) -le 1
        return 1
    end

    set -l g 1
    while test $g -le (count $groups_norm)
        set -l group_norm
        set -l group_orig

        if test -n "$groups_norm[$g]"
            set group_norm (string split \t -- $groups_norm[$g])
        end

        if test $g -le (count $groups_orig); and test -n "$groups_orig[$g]"
            set group_orig (string split \t -- $groups_orig[$g])
        end

        if test (count $group_norm) -gt 0
            set -l emitted_norm $intent $group_norm
            set -l emitted_orig

            if test (count $group_orig) -gt 0
                set emitted_orig $orig_words[$intent_idx] $group_orig
            else
                set emitted_orig $orig_words[$intent_idx]
            end

            __aury_emit_expanded_action (string join \t -- $emitted_norm) (string join \t -- $emitted_orig)
        end

        set g (math $g + 1)
    end

    return 0
end

# -------------------------------------------------
# 3.3 Interpretação de ações individuais
# -------------------------------------------------

function __aury_interpret_action
    set -l norm_words $norm_words_global
    set -l orig_words $orig_words_global

    set -l filtered_norm (__aury_filter_interpretable_words $norm_words)
    set -l filtered_orig
    set -l has_connector 0
    set -l i 1

    while test $i -le (count $filtered_norm)
        set -l tok $filtered_norm[$i]

        if __aury_is_connector_token $tok
            set has_connector 1
        end

        if test $i -le (count $orig_words)
            set filtered_orig $filtered_orig $orig_words[$i]
        end

        set i (math $i + 1)
    end

    set -l interpreted_norm
    set -l interpreted_orig
    set -l j 1

    while test $j -le (count $filtered_norm)
        set -l tok $filtered_norm[$j]

        if __aury_is_aux_token $tok
            set j (math $j + 1)
            continue
        end

        set interpreted_norm $interpreted_norm $tok

        if test $j -le (count $filtered_orig)
            set interpreted_orig $interpreted_orig $filtered_orig[$j]
        end

        set j (math $j + 1)
    end

    if test (count $interpreted_norm) -eq 0
        set interpreted_norm $filtered_norm
        set interpreted_orig $filtered_orig
    end

    set -l intent_idx (__aury_find_first_intent_index $interpreted_norm)
    set -l intent unknown

    if test -n "$intent_idx"
        set intent $interpreted_norm[$intent_idx]
    else
        set intent (__aury_detect_intent $interpreted_norm)
    end

    set -l domain_hint geral
    if contains -- $intent instalar procurar remover
        set domain_hint pacote
    else if contains -- $intent criar copiar mover renomear extrair
        set domain_hint arquivo
    else if contains -- $intent ver atualizar otimizar status
        set domain_hint sistema
    else if contains -- $intent ping internet
        set domain_hint rede
    else if contains -- $intent ajuda reload dev
        set domain_hint interno
    end

    echo "INTENT:$intent"
    echo "DOMAIN_HINT:$domain_hint"
    echo "HAS_CONNECTOR:$has_connector"
    echo "NORM:"(string join \t -- $interpreted_norm)
    echo "ORIG:"(string join \t -- $interpreted_orig)
end

# -------------------------------------------------
# entrada
# -------------------------------------------------

# -------------------------------------------------
# 3.4 Validação, split e preparação final
# -------------------------------------------------

function __aury_validate_input --argument-names raw_text
    if test -z "$raw_text"
        __aury_msg_error "comando inválido"
        return 1
    end

    set -l clean_check (string replace -ra '[[:space:][:punct:]]' '' -- $raw_text)

    if test -z "$clean_check"
        __aury_msg_error "comando inválido"
        return 1
    end

    if string match -rq '^[0-9 ]+$' -- $raw_text
        __aury_msg_error "comando inválido"
        return 1
    end

    return 0
end

# -------------------------------------------------
# parser base
# -------------------------------------------------

function __aury_find_next_command_index --argument-names start_index
    set -l total (count $argv_tokens_global)
    set -l j $start_index

    while test $j -le $total
        if __aury_is_command_token $argv_tokens_global[$j]
            echo $j
            return 0
        end

        set -l norm (__aury_normalize_token $argv_tokens_global[$j])
        if test "$norm" != "__IGNORE__"; and test "$norm" != "e"
            break
        end

        set j (math $j + 1)
    end

    return 1
end

function __aury_split_actions
    set -g argv_tokens_global $argv
    set -l starts 1
    set -l ends
    set -l total (count $argv_tokens_global)
    set -l i 1

    while test $i -lt $total
        set -l current_norm (__aury_normalize_token $argv_tokens_global[$i])

        if test "$current_norm" = "e"
            set -l next_idx (__aury_find_next_command_index (math $i + 1))

            if test -n "$next_idx"
                set ends $ends (math $i - 1)
                set starts $starts $next_idx
                set i (math $next_idx - 1)
            end
        end

        set i (math $i + 1)
    end

    set ends $ends $total

    set -l idx 1
    while test $idx -le (count $starts)
        set -l start $starts[$idx]
        set -l finish $ends[$idx]

        if test $finish -ge $start
            string join \n -- $argv_tokens_global[$start..$finish]
            echo __AURY_ACTION_BREAK__
        end

        set idx (math $idx + 1)
    end

    set -e argv_tokens_global
end

function __aury_prepare_action
    set -l action_tokens $argv
    set -l norm_words
    set -l orig_words

    for tok in $action_tokens
        set -l norm (__aury_normalize_token $tok)

        if test "$norm" = "__IGNORE__"
            continue
        end

        set -l clean_orig

        if string match -rq '(^[~/]|^\./|^\.\./|/|\.[[:alnum:]_-]+$)' -- $tok
            set clean_orig (string trim -- $tok)
        else
            set clean_orig (string replace -ra '^[[:punct:]]+|[[:punct:]]+$' '' -- $tok)
        end

        if test -z "$clean_orig"
            continue
        end

        set norm_words $norm_words $norm
        set orig_words $orig_words $clean_orig
    end

    echo "NORM:"(string join \t -- $norm_words)
    echo "ORIG:"(string join \t -- $orig_words)
end

# ==========================================================
# Seção 4 — Detecção de intenção, domínio e argumentos
# 4.1 Intenção e domínio
# ==========================================================

function __aury_detect_intent
    if set -q __aury_interp_intent; and test -n "$__aury_interp_intent"; and test "$__aury_interp_intent" != "unknown"
        echo $__aury_interp_intent
        return 0
    end

    set -l norm_words $argv

    for candidate in ajuda reload dev atualizar otimizar procurar instalar remover criar copiar mover renomear extrair ping internet ver status abrir
        if contains -- $candidate $norm_words
            echo $candidate
            return 0
        end
    end

    echo unknown
end

function __aury_detect_domain --argument-names intent
    set -e argv[1]
    set -l norm_words $argv
    set -l orig_words $orig_words_global

    if contains -- ajuda $norm_words; or contains -- reload $norm_words; or contains -- dev $norm_words
        echo interno
        return 0
    end

    if contains -- arquivo $norm_words
        echo arquivo
        return 0
    end

    if contains -- pasta $norm_words
        echo pasta
        return 0
    end

    if test "$intent" = "atualizar"; or test "$intent" = "otimizar"; or test "$intent" = "status"
        echo sistema
        return 0
    end

    if contains -- cpu $norm_words; or contains -- memória $norm_words; or contains -- disco $norm_words; or contains -- gpu $norm_words; or contains -- processos $norm_words; or contains -- status $norm_words; or contains -- sistema $norm_words
        echo sistema
        return 0
    end

    if contains -- ip $norm_words; or contains -- internet $norm_words; or contains -- ping $norm_words
        echo rede
        return 0
    end

    if test "$intent" = "instalar"; or test "$intent" = "procurar"
        echo pacote
        return 0
    end

    if test "$intent" = "remover"
        if contains -- arquivo $norm_words; or contains -- pasta $norm_words
            if contains -- arquivo $norm_words
                echo arquivo
            else
                echo pasta
            end
            return 0
        end

        if test (count $orig_words) -gt 0
            set -l last_token $orig_words[-1]

            if string match -rq '/' -- $last_token; or string match -rq '\.' -- $last_token
                echo arquivo
                return 0
            end
        end

        echo pacote
        return 0
    end

    if test "$intent" = "criar"; or test "$intent" = "copiar"; or test "$intent" = "mover"; or test "$intent" = "renomear"; or test "$intent" = "extrair"
        if contains -- pasta $norm_words
            echo pasta
            return 0
        end

        if contains -- arquivo $norm_words
            echo arquivo
            return 0
        end

        if test (count $orig_words) -gt 0
            for tok in $orig_words
                if string match -rq '/' -- $tok; or string match -rq '\.' -- $tok
                    echo arquivo
                    return 0
                end
            end
        end

        echo arquivo
        return 0
    end

    echo geral
end

# -------------------------------------------------
# resolução de argumentos
# -------------------------------------------------

# -------------------------------------------------
# 4.2 Extração de argumentos e conectores
# -------------------------------------------------

function __aury_after_keyword
    set -l keyword $argv[1]
    set -e argv[1]
    set -l words $argv
    set -l idx ''
    set -l i 1

    while test $i -le (count $words)
        set -l norm (__aury_normalize_token $words[$i])

        if test "$norm" = "$keyword"
            set idx $i
            break
        end

        set i (math $i + 1)
    end

    if test -z "$idx"
        echo ""
        return 1
    end

    if test (count $words) -le $idx
        echo ""
        return 0
    end

    string join " " -- $words[(math $idx + 1)..-1]
end

function __aury_after_normalized_keyword --argument-names keyword
    set -l idx (__aury_find_token_index $keyword $norm_words_global)

    if test -z "$idx"
        echo ""
        return 1
    end

    if test (count $orig_words_global) -le $idx
        echo ""
        return 0
    end

    string join " " -- $orig_words_global[(math $idx + 1)..-1]
end

function __aury_find_first_connector_index
    set -l words $argv
    set -l i 1

    while test $i -le (count $words)
        if contains -- $words[$i] para em no na nos nas
            echo $i
            return 0
        end

        set i (math $i + 1)
    end

    return 1
end

function __aury_strip_leading_destination_noise
    set -l words $argv

    while test (count $words) -gt 0
        set -l norm (__aury_normalize_token $words[1])

        if test "$norm" = "__IGNORE__"
            set words $words[2..-1]
            continue
        end

        if contains -- $norm para em no na nos nas pasta caminho local destino lugar fica ficar
            set words $words[2..-1]
            continue
        end

        break
    end

    printf '%s\n' $words
end

# -------------------------------------------------
# 4.3 Arquivos compactados e preparação de extração
# -------------------------------------------------

function __aury_detect_archive_type --argument-names path
    set -l lower (string lower -- $path)

    if string match -rq '\.(tar\.gz|tgz)$' -- $lower
        echo tar.gz
        return 0
    end

    if string match -rq '\.tar$' -- $lower
        echo tar
        return 0
    end

    if string match -rq '\.zip$' -- $lower
        echo zip
        return 0
    end

    if string match -rq '\.7z$' -- $lower
        echo 7z
        return 0
    end

    return 1
end

function __aury_archive_default_destination --argument-names archive_path
    set -l base (basename -- $archive_path)
    set -l lower (string lower -- $base)
    set -l name $base

    if string match -rq '\.tar\.gz$' -- $lower
        set name (string replace -r -i '\.tar\.gz$' '' -- $base)
    else if string match -rq '\.tgz$' -- $lower
        set name (string replace -r -i '\.tgz$' '' -- $base)
    else if string match -rq '\.tar$' -- $lower
        set name (string replace -r -i '\.tar$' '' -- $base)
    else if string match -rq '\.zip$' -- $lower
        set name (string replace -r -i '\.zip$' '' -- $base)
    else if string match -rq '\.7z$' -- $lower
        set name (string replace -r -i '\.7z$' '' -- $base)
    end

    if test -z "$name"
        set name extracted
    end

    set -l parent (dirname -- $archive_path)

    if test -z "$parent"; or test "$parent" = "."
        echo "./$name"
    else
        echo "$parent/$name"
    end
end

function __aury_require_archive_backend --argument-names archive_type
    switch $archive_type
        case zip
            if type -q unzip
                return 0
            end

            __aury_msg_error "não consegui extrair arquivos .zip porque o utilitário 'unzip' não está disponível"
            return 1

        case 7z
            if type -q 7z
                return 0
            end

            __aury_msg_error "não consegui extrair arquivos .7z porque o utilitário '7z' não está disponível"
            return 1

        case tar tar.gz
            if type -q tar
                return 0
            end

            __aury_msg_error "não consegui extrair arquivos tar porque o utilitário 'tar' não está disponível"
            return 1
    end

    return 1
end

function __aury_list_archive_entries --argument-names archive_path archive_type
    switch $archive_type
        case zip
            unzip -Z1 $archive_path 2>/dev/null
            return $status

        case 7z
            set -l first_path 1

            for line in (7z l -slt $archive_path 2>/dev/null)
                if string match -rq '^Path = ' -- $line
                    set -l entry (string replace 'Path = ' '' -- $line)

                    if test $first_path -eq 1
                        set first_path 0
                        continue
                    end

                    echo $entry
                end
            end

            return 0

        case tar tar.gz
            tar -tf $archive_path 2>/dev/null
            return $status
    end

    return 1
end

function __aury_archive_entries_are_safe --argument-names archive_path archive_type
    set -l entries (__aury_list_archive_entries $archive_path $archive_type)
    set -l list_status $status

    if test $list_status -ne 0
        __aury_msg_error "não consegui inspecionar o conteúdo de '$archive_path' antes de extrair"
        return 1
    end

    for entry in $entries
        if test -z "$entry"; or test "$entry" = "."; or test "$entry" = "./"
            continue
        end

        set -l normalized (string replace -a '\\' '/' -- $entry)

        if string match -rq '^/' -- $normalized
            __aury_msg_error "extração bloqueada por segurança: o arquivo compactado contém caminhos absolutos"
            return 1
        end

        if test "$normalized" = ".."; or string match -rq '(^|/)\.\.(/|$)' -- $normalized
            __aury_msg_error "extração bloqueada por segurança: o arquivo compactado contém caminhos inseguros"
            return 1
        end
    end

    return 0
end

function __aury_count_extracted_items --argument-names dest
    set -l files 0
    set -l dirs 0

    if test -d $dest
        set files (find $dest -type f 2>/dev/null | wc -l | string trim)
        set dirs (find $dest -mindepth 1 -type d 2>/dev/null | wc -l | string trim)
    end

    echo "FILES:$files"
    echo "DIRS:$dirs"
end

function __aury_extract_archive_args
    set -l norm_words $argv
    set -l orig_words $orig_words_global

    set -g __aury_arg_source ''
    set -g __aury_arg_dest ''
    set -g __aury_arg_archive_type ''

    set -l intent_idx (contains -i -- extrair $norm_words)

    if test -z "$intent_idx"
        set intent_idx 1
    end

    set -l start (math $intent_idx + 1)

    while test (count $norm_words) -ge $start
        if contains -- $norm_words[$start] arquivo pacote pasta
            set start (math $start + 1)
            continue
        end

        break
    end

    if test (count $orig_words) -lt $start
        return 1
    end

    set -l rel_connector (__aury_find_first_connector_index $norm_words[$start..-1])

    if test -n "$rel_connector"
        set -l conn_idx (math $start + $rel_connector - 1)

        if test (math $conn_idx - 1) -ge $start
            set -g __aury_arg_source (string join " " -- $orig_words[$start..(math $conn_idx - 1)])
        end

        if test (count $orig_words) -gt $conn_idx
            set -l cleaned_dest (__aury_strip_leading_destination_noise $orig_words[(math $conn_idx + 1)..-1])

            if test (count $cleaned_dest) -gt 0
                set -g __aury_arg_dest (string join " " -- $cleaned_dest)
            end
        end
    else
        set -g __aury_arg_source (string join " " -- $orig_words[$start..-1])
    end

    if test -n "$__aury_arg_source"
        set -g __aury_arg_archive_type (__aury_detect_archive_type $__aury_arg_source)
    end

    return 0
end

function __aury_extract_file_args
    set -l intent $argv[1]
    set -e argv[1]
    set -l norm_words $argv
    set -l orig_words $orig_words_global

    set -g __aury_arg_type ''
    set -g __aury_arg_target ''
    set -g __aury_arg_source ''
    set -g __aury_arg_dest ''
    set -g __aury_arg_newname ''

    set -l idx

    if contains -- pasta $norm_words
        set -g __aury_arg_type pasta
        set idx (contains -i -- pasta $norm_words)
    else if contains -- arquivo $norm_words
        set -g __aury_arg_type arquivo
        set idx (contains -i -- arquivo $norm_words)
    else
        set -g __aury_arg_type arquivo
        set idx (contains -i -- $intent $norm_words)
    end

    if test -z "$idx"
        set idx 1
    end

    if test "$intent" = "criar"; or test "$intent" = "remover"
        set -l start (math $idx + 1)

        if test (count $norm_words) -ge $start
            if test "$norm_words[$start]" = "arquivo"; or test "$norm_words[$start]" = "pasta"
                set start (math $start + 1)
            end
        end

        if test (count $norm_words) -ge $start
            set -l rel_connector (__aury_find_first_connector_index $norm_words[$start..-1])

            if test -n "$rel_connector"
                set -l conn_idx (math $start + $rel_connector - 1)

                if test "$norm_words[$conn_idx]" = "em"; and test (count $orig_words) -gt $conn_idx
                    set -g __aury_arg_target (string join " " -- $orig_words[(math $conn_idx + 1)..-1])
                    return 0
                end
            end
        end

        if test (count $orig_words) -ge $start
            set -g __aury_arg_target (string join " " -- $orig_words[$start..-1])
        end
        return 0
    end

    if test "$intent" = "copiar"; or test "$intent" = "mover"; or test "$intent" = "renomear"
        set -l start (math $idx + 1)

        if test (count $norm_words) -ge $start
            if test "$norm_words[$start]" = "arquivo"; or test "$norm_words[$start]" = "pasta"
                set start (math $start + 1)
            end
        end

        if test (count $norm_words) -ge $start
            set -l rel_connector (__aury_find_first_connector_index $norm_words[$start..-1])

            if test -n "$rel_connector"
                set -l conn_idx (math $start + $rel_connector - 1)

                if test (math $conn_idx - 1) -ge $start
                    set -g __aury_arg_source (string join " " -- $orig_words[$start..(math $conn_idx - 1)])
                end

                if test (count $orig_words) -gt $conn_idx
                    set -g __aury_arg_dest (string join " " -- $orig_words[(math $conn_idx + 1)..-1])
                    set -g __aury_arg_newname $__aury_arg_dest
                end

                return 0
            end
        end

        if test (count $orig_words) -ge (math $start + 1)
            set -g __aury_arg_source $orig_words[$start]
            set -g __aury_arg_dest $orig_words[(math $start + 1)]
            set -g __aury_arg_newname $orig_words[(math $start + 1)]
        end
        return 0
    end
end

# -------------------------------------------------
# executores
# -------------------------------------------------

# ==========================================================
# Seção 5 — Executores por domínio
# 5.1 Internos
# ==========================================================

function __aury_exec_internal --argument-names intent
    switch $intent
        case ajuda
            __aury_show_help
            return 0

        case reload
            set -l file ~/.config/fish/functions/aury.fish

            if not test -f $file
                __aury_msg_error "arquivo da Aury não encontrado"
                return 1
            end

            echo "🔄 recarregando Aury..."
            source $file

            if test $status -eq 0
                __aury_msg_ok "Aury recarregada"
            else
                __aury_msg_error "erro ao recarregar"
            end
            return 0

        case dev
            set -l file ~/.config/fish/functions/aury.fish

            if not test -f $file
                __aury_msg_error "arquivo da Aury não encontrado"
                return 1
            end

            echo "🛠 verificando código da Aury..."
            set -l result (fish --no-execute $file 2>&1)

            if test $status -eq 0
                __aury_msg_ok "código válido"
            else
                __aury_msg_error "erro detectado"
                set -l line (string match -r 'line [0-9]+|linha [0-9]+' -- $result)

                if test -n "$line"
                    echo "📍 erro encontrado em: $line"
                end

                echo ""
                echo $result
            end
            return 0
    end

    return 1
end

# -------------------------------------------------
# 5.2 Sistema
# -------------------------------------------------

function __aury_exec_system
    set -l intent $argv[1]
    set -e argv[1]
    set -l norm_words $argv

    if test "$intent" = "atualizar"
        echo "📦 atualizando sistema"

        if type -q paru
            paru -Syu
        else
            sudo pacman -Syu
        end

        return 0
    end

    if test "$intent" = "otimizar"
        echo "🚀 otimizando sistema"

        if type -q paccache
            sudo paccache -rk2
        end

        sudo journalctl --vacuum-time=7d

        set -l orphans (pacman -Qtdq 2>/dev/null)

        if test -n "$orphans"
            sudo pacman -Rns -- $orphans
        else
            __aury_msg_info "nenhum pacote órfão encontrado"
        end

        return 0
    end

    if contains -- status $norm_words
        echo "CPU"
        lscpu | grep -i "model name"

        echo ""
        echo "RAM"
        free -h

        echo ""
        echo "DISCO"
        df -h /

        echo ""
        echo "UPTIME"
        uptime -p

        return 0
    end

    if contains -- cpu $norm_words
        lscpu
        return 0
    end

    if contains -- memória $norm_words
        free -h
        return 0
    end

    if contains -- disco $norm_words
        df -h
        return 0
    end

    if contains -- gpu $norm_words
        lspci | grep -Ei "vga|3d|display"
        return 0
    end

    if contains -- processos $norm_words
        ps aux --sort=-%cpu | head -15
        return 0
    end

    return 1
end

# -------------------------------------------------
# 5.3 Rede
# -------------------------------------------------

function __aury_exec_network
    set -l intent $argv[1]
    set -e argv[1]
    set -l norm_words $argv

    if contains -- ip $norm_words
        ip a
        return 0
    end

    if test "$intent" = "internet"; and not contains -- ping $norm_words
        ping -c 2 -- 8.8.8.8
        return 0
    end

    if test "$intent" = "ping"
        set -l host (__aury_after_normalized_keyword ping)

        if test -z "$host"
            __aury_msg_error "especifique host"
        else
            ping -c 2 -- $host
        end

        return 0
    end

    return 1
end

# -------------------------------------------------
# 5.4 Pacotes
# -------------------------------------------------

function __aury_exec_packages
    set -l intent $argv[1]
    set -e argv[1]

    switch $intent
        case procurar
            set -l search (__aury_after_normalized_keyword procurar)

            if test -z "$search"
                __aury_msg_error "termo não especificado"
                return 0
            end

            pacman -Ss -- $search
            return 0

        case instalar
            set -l pkg_text (__aury_after_normalized_keyword instalar)

            if test -z "$pkg_text"
                __aury_msg_error "pacote não especificado"
                return 0
            end

            set -l pkg_words (string split " " -- $pkg_text)
            set -l pkg (string join "-" -- $pkg_words)

            echo "📦 instalando $pkg"

            if pacman -Si -- $pkg >/dev/null 2>/dev/null
                sudo pacman -S --needed -- $pkg
                return 0
            end

            if type -q paru
                if paru -Si -- $pkg >/dev/null 2>/dev/null
                    __aury_msg_info "tentando via paru..."
                    paru -S --needed -- $pkg
                    return 0
                end
            end

            if type -q flatpak
                __aury_msg_info "tentando via flatpak..."
                flatpak install -y --system flathub $pkg

                if test $status -ne 0
                    flatpak install -y --user flathub $pkg
                end

                return 0
            end

            __aury_msg_error "pacote não encontrado: $pkg"
            return 0

        case remover
            set -l pkg_text (__aury_after_normalized_keyword remover)

            if test -z "$pkg_text"
                __aury_msg_error "pacote não especificado"
                return 0
            end

            set -l pkg_words (string split " " -- $pkg_text)
            set -l pkg (string join "-" -- $pkg_words)

            echo "🗑 removendo $pkg"

            sudo pacman -Rns -- $pkg

            if test $status -ne 0
                if type -q paru
                    paru -Rns -- $pkg
                end
            end

            return 0
    end

    return 1
end

# -------------------------------------------------
# 5.5 Arquivos e extração
# -------------------------------------------------

function __aury_exec_files
    set -l intent $argv[1]
    set -e argv[1]
    set -l norm_words $argv

    __aury_extract_file_args $intent $norm_words

    switch $intent
        case criar
            if test "$__aury_arg_type" = "pasta"
                if test -z "$__aury_arg_target"
                    __aury_msg_error "nome da pasta não especificado"
                    return 0
                end

                mkdir -p -- $__aury_arg_target

                if test $status -eq 0
                    echo "📁 pasta criada: $__aury_arg_target"
                else
                    __aury_msg_error "erro ao criar pasta"
                end

                return 0
            end

            if test -z "$__aury_arg_target"
                __aury_msg_error "nome do arquivo não especificado"
                return 0
            end

            set -l parent_dir (dirname -- $__aury_arg_target)

            if test "$parent_dir" != "."
                mkdir -p -- $parent_dir
            end

            touch -- $__aury_arg_target

            if test $status -eq 0
                echo "📄 arquivo criado: $__aury_arg_target"
            else
                __aury_msg_error "erro ao criar arquivo"
            end

            return 0

        case remover
            if test -z "$__aury_arg_target"
                __aury_msg_error "alvo não especificado"
                return 0
            end

            if not test -e $__aury_arg_target
                __aury_msg_error "não encontrado: $__aury_arg_target"
                return 0
            end

            echo "⚠ confirmar exclusão de '$__aury_arg_target' (s/n)"
            read -l confirm

            if test "$confirm" = "s" -o "$confirm" = "S"
                if test "$__aury_arg_type" = "pasta"
                    rm -rf -- $__aury_arg_target
                else
                    rm -f -- $__aury_arg_target
                end

                if test $status -eq 0
                    echo "🗑 removido: $__aury_arg_target"
                else
                    __aury_msg_error "erro ao remover"
                end
            else
                echo "❌ cancelado"
            end

            return 0

        case copiar
            if test -z "$__aury_arg_source" -o -z "$__aury_arg_dest"
                __aury_msg_error "argumentos insuficientes"
                return 0
            end

            if not test -e $__aury_arg_source
                __aury_msg_error "origem não encontrada: $__aury_arg_source"
                return 0
            end

            set -l dest_dir (dirname -- $__aury_arg_dest)

            if test "$dest_dir" != "."
                mkdir -p -- $dest_dir
            end

            if test -d $__aury_arg_source
                cp -r -- $__aury_arg_source $__aury_arg_dest
                set -l copy_type pasta
            else
                cp -- $__aury_arg_source $__aury_arg_dest
                set -l copy_type arquivo
            end

            if test $status -eq 0
                if test "$copy_type" = "pasta"
                    echo "📁 pasta copiada: $__aury_arg_source → $__aury_arg_dest"
                else
                    echo "📄 arquivo copiado: $__aury_arg_source → $__aury_arg_dest"
                end
            else
                __aury_msg_error "erro ao copiar"
            end

            return 0

        case mover
            if test -z "$__aury_arg_source" -o -z "$__aury_arg_dest"
                __aury_msg_error "argumentos insuficientes"
                return 0
            end

            if not test -e $__aury_arg_source
                __aury_msg_error "origem não encontrada: $__aury_arg_source"
                return 0
            end

            set -l dest_dir (dirname -- $__aury_arg_dest)

            if test "$dest_dir" != "."
                mkdir -p -- $dest_dir
            end

            if test -d $__aury_arg_source
                set -l move_type pasta
            else
                set -l move_type arquivo
            end

            mv -- $__aury_arg_source $__aury_arg_dest

            if test $status -eq 0
                if test "$move_type" = "pasta"
                    echo "📁 pasta movida: $__aury_arg_source → $__aury_arg_dest"
                else
                    echo "📄 arquivo movido: $__aury_arg_source → $__aury_arg_dest"
                end
            else
                __aury_msg_error "erro ao mover"
            end

            return 0

        case extrair
            __aury_extract_archive_args $norm_words

            if test -z "$__aury_arg_source"
                __aury_msg_error "arquivo compactado não especificado"
                return 0
            end

            if not test -f $__aury_arg_source
                __aury_msg_error "arquivo não encontrado: $__aury_arg_source"
                return 0
            end

            if test -z "$__aury_arg_archive_type"
                __aury_msg_error "tipo de arquivo não suportado. Nesta versão eu aceito: zip, 7z, tar, tar.gz e tgz"
                return 0
            end

            if not __aury_require_archive_backend $__aury_arg_archive_type
                return 0
            end

            if test -z "$__aury_arg_dest"
                set -g __aury_arg_dest (__aury_archive_default_destination $__aury_arg_source)
            end

            if test -e $__aury_arg_dest
                __aury_msg_error "a pasta de destino já existe: $__aury_arg_dest"
                return 0
            end

            if not __aury_archive_entries_are_safe $__aury_arg_source $__aury_arg_archive_type
                return 0
            end

            mkdir -p -- $__aury_arg_dest

            switch $__aury_arg_archive_type
                case zip
                    unzip -q $__aury_arg_source -d $__aury_arg_dest >/dev/null 2>/dev/null

                case 7z
                    7z x -y -o"$__aury_arg_dest" $__aury_arg_source >/dev/null 2>/dev/null

                case tar tar.gz
                    tar -xf $__aury_arg_source -C $__aury_arg_dest >/dev/null 2>/dev/null
            end

            if test $status -ne 0
                rm -rf -- $__aury_arg_dest
                __aury_msg_error "não consegui extrair '$__aury_arg_source'. O arquivo pode estar corrompido ou incompatível com esta instalação."
                return 0
            end

            set -l count_info (__aury_count_extracted_items $__aury_arg_dest)
            set -l extracted_files 0
            set -l extracted_dirs 0

            for line in $count_info
                if string match -q 'FILES:*' -- $line
                    set extracted_files (string replace 'FILES:' '' -- $line)
                else if string match -q 'DIRS:*' -- $line
                    set extracted_dirs (string replace 'DIRS:' '' -- $line)
                end
            end

            echo "📦 extraído: $__aury_arg_source → $__aury_arg_dest"
            echo "📄 arquivos: $extracted_files"
            echo "📁 pastas: $extracted_dirs"
            return 0

        case renomear
            if test -z "$__aury_arg_source" -o -z "$__aury_arg_newname"
                __aury_msg_error "argumentos insuficientes"
                return 0
            end

            if not test -e $__aury_arg_source
                __aury_msg_error "arquivo ou pasta não encontrado: $__aury_arg_source"
                return 0
            end

            mv -- $__aury_arg_source $__aury_arg_newname

            if test $status -eq 0
                echo "✏️ renomeado: $__aury_arg_source → $__aury_arg_newname"
            else
                __aury_msg_error "erro ao renomear"
            end

            return 0
    end

    return 1
end

# ==========================================================
# Seção 6 — Dispatch, fallback e função principal
# 6.1 Dispatch e fallback
# ==========================================================

function __aury_dispatch_current_action
    set -l intent (__aury_detect_intent $norm_words_global)
    set -l domain (__aury_detect_domain $intent $norm_words_global)

    if contains -- $intent (__aury_internal_intents)
        __aury_exec_internal $intent
        return 0
    end

    if test "$intent" = "ver"
        set -l shared_system_targets (__aury_collect_system_targets_from_words $norm_words_global)
        if test (count $shared_system_targets) -gt 1
            for target in $shared_system_targets
                if not __aury_exec_system $intent $intent $target
                    return 1
                end
            end
            return 0
        end
    end

    switch $domain
        case sistema
            if __aury_exec_system $intent $norm_words_global
                return 0
            end

        case rede
            if __aury_exec_network $intent $norm_words_global
                return 0
            end

        case arquivo pasta
            if __aury_exec_files $intent $norm_words_global
                return 0
            end

        case pacote
            if __aury_exec_packages $intent $norm_words_global
                return 0
            end
    end

    return 1
end

# -------------------------------------------------
# fallback
# -------------------------------------------------

function __aury_fallback
    set -l action_tokens $argv
    echo "❓ Não entendi: "(string join " " -- $action_tokens)
    echo "Digite: aury ajuda"
end

# -------------------------------------------------
# função principal
# -------------------------------------------------

# -------------------------------------------------
# 6.2 Função principal
# -------------------------------------------------

function aury
    if test (count $argv) -eq 0
        __aury_msg_error "comando inválido"
        return 1
    end

    set -l raw_tokens (__aury_preprocess_input $argv)

    if test (count $raw_tokens) -eq 0
        __aury_msg_error "comando inválido"
        return 1
    end
    set -l raw_text (string join " " -- $raw_tokens)
    set raw_text (string trim -- $raw_text)

    if not __aury_validate_input "$raw_text"
        return 1
    end

    set -l split_stream (__aury_split_actions $raw_tokens)
    set -l current_action

    for item in $split_stream
        if test "$item" = "__AURY_ACTION_BREAK__"
            if test (count $current_action) -eq 0
                continue
            end

            set -l prepared (__aury_prepare_action $current_action)
            set -g norm_words_global
            set -g orig_words_global

            for line in $prepared
                if string match -q 'NORM:*' -- $line
                    set -l payload (string replace 'NORM:' '' -- $line)

                    if test -n "$payload"
                        set -g norm_words_global (string split \t -- $payload)
                    else
                        set -g norm_words_global
                    end
                else if string match -q 'ORIG:*' -- $line
                    set -l payload (string replace 'ORIG:' '' -- $line)

                    if test -n "$payload"
                        set -g orig_words_global (string split \t -- $payload)
                    else
                        set -g orig_words_global
                    end
                end
            end

            if test (count $norm_words_global) -eq 0
                set current_action
                continue
            end

            set -e __aury_interp_intent
            set -e __aury_interp_domain_hint
            set -e __aury_interp_has_connector

            set -l interpreted (__aury_interpret_action)
            set -l interpreted_norm_words
            set -l interpreted_orig_words

            for line in $interpreted
                if string match -q 'INTENT:*' -- $line
                    set -g __aury_interp_intent (string replace 'INTENT:' '' -- $line)
                else if string match -q 'DOMAIN_HINT:*' -- $line
                    set -g __aury_interp_domain_hint (string replace 'DOMAIN_HINT:' '' -- $line)
                else if string match -q 'HAS_CONNECTOR:*' -- $line
                    set -g __aury_interp_has_connector (string replace 'HAS_CONNECTOR:' '' -- $line)
                else if string match -q 'NORM:*' -- $line
                    set -l payload (string replace 'NORM:' '' -- $line)

                    if test -n "$payload"
                        set interpreted_norm_words (string split \t -- $payload)
                    else
                        set interpreted_norm_words
                    end
                else if string match -q 'ORIG:*' -- $line
                    set -l payload (string replace 'ORIG:' '' -- $line)

                    if test -n "$payload"
                        set interpreted_orig_words (string split \t -- $payload)
                    else
                        set interpreted_orig_words
                    end
                end
            end

            if test (count $interpreted_norm_words) -gt 0
                set -g norm_words_global $interpreted_norm_words
            end

            if test (count $interpreted_orig_words) -gt 0
                set -g orig_words_global $interpreted_orig_words
            end

            set -l expanded (__aury_expand_interpreted_actions)
            set -l ran_expanded 0
            set -l expanded_norm_words
            set -l expanded_orig_words

            for line in $expanded
                if string match -q 'NORM:*' -- $line
                    set -l payload (string replace 'NORM:' '' -- $line)
                    if test -n "$payload"
                        set expanded_norm_words (string split \t -- $payload)
                    else
                        set expanded_norm_words
                    end
                else if string match -q 'ORIG:*' -- $line
                    set -l payload (string replace 'ORIG:' '' -- $line)
                    if test -n "$payload"
                        set expanded_orig_words (string split \t -- $payload)
                    else
                        set expanded_orig_words
                    end
                else if test "$line" = "__AURY_EXPANDED_ACTION_BREAK__"
                    if test (count $expanded_norm_words) -gt 0
                        set -g norm_words_global $expanded_norm_words
                        set -g orig_words_global $expanded_orig_words
                        set -e __aury_interp_intent
                        set -e __aury_interp_domain_hint
                        set -e __aury_interp_has_connector

                        if __aury_dispatch_current_action
                            set ran_expanded 1
                        else
                            __aury_fallback $current_action
                        end
                    end

                    set expanded_norm_words
                    set expanded_orig_words
                end
            end

            if test $ran_expanded -eq 1
                set current_action
                continue
            end

            if __aury_dispatch_current_action
                set current_action
                continue
            end

            __aury_fallback $current_action
            set current_action
        else
            set current_action $current_action $item
        end
    end

    set -e norm_words_global
    set -e orig_words_global
    set -e __aury_interp_intent
    set -e __aury_interp_domain_hint
    set -e __aury_interp_has_connector
    set -e __aury_arg_type
    set -e __aury_arg_target
    set -e __aury_arg_source
    set -e __aury_arg_dest
    set -e __aury_arg_newname
    set -e __aury_arg_archive_type

    return 0
end

# -------------------------------------------------
# 6.3 Alias principal
# -------------------------------------------------

function Aury
    aury $argv
end
