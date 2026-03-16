# ==========================================================
# 💜 Aury 1.2.1
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
# ajuda
# -------------------------------------------------

function __aury_show_help
    echo "
💜 Aury 1.2.1

PACOTES
aury instalar firefox
aury remover vlc
aury procurar steam

SISTEMA
aury atualizar sistema
aury otimizar sistema
aury status

INFO
aury ver cpu
aury ver memória
aury ver disco
aury ver gpu
aury ver processos

REDE
aury ver ip
aury testar internet
aury ping google.com

ARQUIVOS
aury criar arquivo teste.txt
aury criar pasta projetos
aury remover arquivo teste.txt
aury remover pasta projetos
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

        case o a os as um uma uns umas de do da dos das no na nos nas em com sobre ao aos à às pra para por pro me mim ai aí favor porfavor gentileza pode poderia poderiame poderia-me
            echo __IGNORE__

        case e
            echo e

        case ajuda help socorro manual comandos
            echo ajuda

        case reload recarregar reiniciar
            echo reload

        case dev developer desenvolvedor diagnostico diagnóstico validar verificar
            echo dev

        case instalar instala instale instalaram adicionar add instalr isntalar instal
            echo instalar

        case remover remove remov deletar excluir apagar desinstalar desinstala desinstale uninstall removr remvoe
            echo remover

        case procurar procura buscar busca pesquise pesquisar acha achar encontrar localizar procra procuar pesquisr
            echo procurar

        case criar cria crie gerar fazer
            echo criar

        case copiar copia cp duplicar copar copiarr
            echo copiar

        case mover move mv movr moevr enviar
            echo mover

        case renomear renomeia renomeie rename renomar renoemar renomea
            echo renomear

        case status estado info infos informação informacoes informações
            echo status

        case ver veja mostra mostrar exibir listar
            echo ver

        case atualizar atualiza update upgrade sincronizar
            echo atualizar

        case otimizar otimiza limpar limpa melhorar
            echo otimizar

        case abrir abre open
            echo abrir

        case testar teste internet rede conexão conexao conectar
            echo internet

        case ping
            echo ping

        case pasta diretório diretorio folder diretoro
            echo pasta

        case arquivo ficheiro file
            echo arquivo

        case pacote pacotes app aplicativo programa
            echo pacote

        case sistema
            echo sistema

        case processo processos
            echo processos

        case memoria memora memori ram memória
            echo memória

        case disco armazenamento hd ssd
            echo disco

        case gpu video vídeo grafico gráfico grafica gráfica
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

    if contains -- $normalized ajuda reload dev instalar remover procurar criar copiar mover renomear status ver atualizar otimizar abrir internet ping
        return 0
    end

    return 1
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

function __aury_split_actions
    set -l raw_tokens $argv
    set -l starts 1
    set -l ends
    set -l total (count $raw_tokens)
    set -l i 1

    while test $i -lt $total
        set -l current_norm (__aury_normalize_token $raw_tokens[$i])
        set -l next_token $raw_tokens[(math $i + 1)]

        if test "$current_norm" = "e"
            if __aury_is_command_token $next_token
                set ends $ends (math $i - 1)
                set starts $starts (math $i + 1)
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
            string join \n -- $raw_tokens[$start..$finish]
            echo __AURY_ACTION_BREAK__
        end

        set idx (math $idx + 1)
    end
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

        set norm_words $norm_words $norm
        set orig_words $orig_words $tok
    end

    echo "NORM:"(string join \t -- $norm_words)
    echo "ORIG:"(string join \t -- $orig_words)
end

function __aury_detect_intent
    set -l norm_words $argv

    for candidate in ajuda reload dev atualizar otimizar status procurar instalar remover criar copiar mover renomear ping ver internet abrir
        if contains -- $candidate $norm_words
            echo $candidate
            return 0
        end
    end

    echo unknown
end

function __aury_detect_domain
    set -l norm_words $argv

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

    if contains -- instalar $norm_words; or contains -- procurar $norm_words
        echo pacote
        return 0
    end

    if contains -- remover $norm_words
        echo pacote
        return 0
    end

    if contains -- reload $norm_words; or contains -- dev $norm_words; or contains -- ajuda $norm_words
        echo interno
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
    set -l idx (contains -i -- $keyword $words)

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

    if test "$intent" = "criar"; or test "$intent" = "remover"
        if test (count $orig_words) -gt $idx
            set -g __aury_arg_target (string join " " -- $orig_words[(math $idx + 1)..-1])
        end
        return 0
    end

    if test "$intent" = "copiar"; or test "$intent" = "mover"; or test "$intent" = "renomear"
        if test (count $orig_words) -gt (math $idx + 1)
            set -g __aury_arg_source $orig_words[(math $idx + 1)]
            set -g __aury_arg_dest $orig_words[(math $idx + 2)]
            set -g __aury_arg_newname $orig_words[(math $idx + 2)]
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
    set -l orig_words $orig_words_global

    if contains -- ip $norm_words
        ip a
        return 0
    end

    if test "$intent" = "internet"; and not contains -- ping $norm_words
        ping -c 2 -- 8.8.8.8
        return 0
    end

    if test "$intent" = "ping"
        set -l host (__aury_after_keyword ping $orig_words)

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
    set -l orig_words $orig_words_global

    switch $intent
        case procurar
            set -l search (__aury_after_keyword procurar $orig_words)

            if test -z "$search"
                __aury_msg_error "termo não especificado"
                return 0
            end

            pacman -Ss -- $search
            return 0

        case instalar
            set -l pkg_text (__aury_after_keyword instalar $orig_words)

            if test -z "$pkg_text"
                __aury_msg_error "pacote não especificado"
                return 0
            end

            set -l pkg_words (string split " " -- $pkg_text)
            set -l pkg (string join "-" -- $pkg_words)

            echo "📦 instalando $pkg"

            sudo pacman -S -- $pkg

            if test $status -ne 0
                if type -q paru
                    __aury_msg_info "tentando via paru..."
                    paru -S -- $pkg
                end
            end

            if test $status -ne 0
                if type -q flatpak
                    __aury_msg_info "tentando via flatpak..."
                    flatpak install -y flathub $pkg
                end
            end

            return 0

        case remover
            set -l pkg_text (__aury_after_keyword remover $orig_words)

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

    set -l raw_tokens $argv
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
            set -l norm_words
            set -g orig_words_global

            for line in $prepared
                if string match -q 'NORM:*' -- $line
                    set -l payload (string replace 'NORM:' '' -- $line)

                    if test -n "$payload"
                        set norm_words (string split \t -- $payload)
                    else
                        set norm_words
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

            if test (count $norm_words) -eq 0
                set current_action
                continue
            end

            set -l intent (__aury_detect_intent $norm_words)
            set -l domain (__aury_detect_domain $norm_words)

            if contains -- $intent ajuda reload dev
                __aury_exec_internal $intent
                set current_action
                continue
            end

            switch $domain
                case sistema
                    if __aury_exec_system $intent $norm_words
                        set current_action
                        continue
                    end

                case rede
                    if __aury_exec_network $intent $norm_words
                        set current_action
                        continue
                    end

                case arquivo pasta
                    if __aury_exec_files $intent $norm_words
                        set current_action
                        continue
                    end

                case pacote
                    if __aury_exec_packages $intent $norm_words
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

    set -e orig_words_global
    set -e __aury_arg_type
    set -e __aury_arg_target
    set -e __aury_arg_source
    set -e __aury_arg_dest
    set -e __aury_arg_newname
end