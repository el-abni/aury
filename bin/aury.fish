# ==========================================================
# 💜 Aury 1.3.1-dev2
# Terminal Assistant for CachyOS
# Shell: fish
# ==========================================================

# -------------------------------------------------
# mensagens
# -------------------------------------------------

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

function __aury_intents
    printf '%s\n' ajuda reload dev atualizar otimizar status procurar instalar remover criar copiar mover renomear ping ver internet abrir
end

function __aury_internal_intents
    printf '%s\n' ajuda reload dev
end

function __aury_file_intents
    printf '%s\n' criar copiar mover renomear
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

function __aury_show_help
    echo "
💜 Aury 1.3.1-dev2

PACOTES
aury instalar firefox
aury instala firefox
aury Aury, instala o obs studio.
aury remover vlc
aury procurar steam

SISTEMA
aury atualizar sistema
aury otimizar sistema
aury status
aury mostrar cpu
aury checar memória

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

EXTRAS
aury reload
aury dev
"
end

# -------------------------------------------------
# linguagem / normalização
# -------------------------------------------------

function __aury_normalize_token --argument-names tok
    set -l t (string lower -- $tok)
    set t (string replace -ra '^[[:punct:]]+|[[:punct:]]+$' '' -- $t)

    switch $t
        case ''
            echo __IGNORE__

        case o a os as um uma uns umas de do da dos das no na nos nas em com sobre ao aos à às pra para por pro me mim ai aí favor porfavor gentileza pode poderia poderiame poderia-me porgentileza pfvr porfa comigo aury
            echo __IGNORE__

        case e
            echo e

        case ajuda help socorro manual comandos comando
            echo ajuda

        case reload recarregar reiniciar
            echo reload

        case dev developer desenvolvedor diagnostico diagnóstico validar verificar debug
            echo dev

        case instalar instala instale instalaram adicionar adiciona adicione add instalr isntalar instal botar colocar
            echo instalar

        case remover remove remov deletar delete excluir apagar apague desinstalar desinstala desinstale uninstall removr remvoe tirar
            echo remover

        case procurar procura buscar busca pesquise pesquisar acha achar encontrar localizar procra procuar pesquisr consultar pesquisa
            echo procurar

        case criar cria crie gerar fazer monte montar
            echo criar

        case copiar copia cp duplicar copar copiarr clone clonar
            echo copiar

        case mover move mv movr moevr enviar deslocar
            echo mover

        case renomear renomeia renomeie rename renomar renoemar renomea nomear
            echo renomear

        case status estado info infos informação informacoes informações situacao situação
            echo status

        case ver veja mostra mostrar exibir listar checar checa consulte consultar visualizar olhar olhe monitorar
            echo ver

        case atualizar atualiza update upgrade sincronizar atualizara
            echo atualizar

        case otimizar otimiza limpar limpa melhorar acelerar
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

function __aury_is_command_token --argument-names tok
    set -l normalized (__aury_normalize_token $tok)

    if contains -- $normalized (__aury_intents)
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

function __aury_tokens_after --argument-names index
    set -e argv[1]
    set -l words $argv

    if test (count $words) -le $index
        return 0
    end

    printf '%s\n' $words[(math $index + 1)..-1]
end

function __aury_interpret_action
    set -l norm_words $norm_words_global
    set -l orig_words $orig_words_global

    set -l intent (__aury_detect_intent $norm_words)
    set -l domain (__aury_detect_domain $intent $norm_words)

    echo "INTENT:$intent"
    echo "DOMAIN:$domain"
end

# -------------------------------------------------
# entrada
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

        if test "$norm" = "e"
            continue
        end

        set -l clean_orig (string replace -ra '^[[:punct:]]+|[[:punct:]]+$' '' -- $tok)

        if test -z "$clean_orig"
            continue
        end

        set norm_words $norm_words $norm
        set orig_words $orig_words $clean_orig
    end

    echo "NORM:"(string join \t -- $norm_words)
    echo "ORIG:"(string join \t -- $orig_words)
end

function __aury_detect_intent
    set -l norm_words $argv

    for candidate in ajuda reload dev atualizar otimizar procurar instalar remover criar copiar mover renomear ping internet ver status abrir
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

    if test "$intent" = "criar"; or test "$intent" = "copiar"; or test "$intent" = "mover"; or test "$intent" = "renomear"
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

            set -l interpreted (__aury_interpret_action)
            set -l intent unknown
            set -l domain geral

            for line in $interpreted
                if string match -q 'INTENT:*' -- $line
                    set intent (string replace 'INTENT:' '' -- $line)
                else if string match -q 'DOMAIN:*' -- $line
                    set domain (string replace 'DOMAIN:' '' -- $line)
                end
            end

            if contains -- $intent (__aury_internal_intents)
                __aury_exec_internal $intent
                set current_action
                continue
            end

            switch $domain
                case sistema
                    if __aury_exec_system $intent $norm_words_global
                        set current_action
                        continue
                    end

                case rede
                    if __aury_exec_network $intent $norm_words_global
                        set current_action
                        continue
                    end

                case arquivo pasta
                    if __aury_exec_files $intent $norm_words_global
                        set current_action
                        continue
                    end

                case pacote
                    if __aury_exec_packages $intent $norm_words_global
                        set current_action
                        continue
                    end
            end

            __aury_fallback $current_action
            set current_action
        else
            set current_action $current_action $item
        end
    end

    set -e norm_words_global
    set -e orig_words_global
    set -e __aury_arg_type
    set -e __aury_arg_target
    set -e __aury_arg_source
    set -e __aury_arg_dest
    set -e __aury_arg_newname
end

function Aury
    aury $argv
end
