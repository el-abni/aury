# ==========================================================
# 💜 Aury 1.2
# Terminal Assistant for CachyOS
# Shell: fish
# ==========================================================

function aury

    # -------------------------------------------------
    # helpers internos
    # -------------------------------------------------

    function __aury_norm_token --argument-names tok
        set -l t (string lower -- $tok)
        set t (string replace -ra '^[[:punct:]]+|[[:punct:]]+$' '' -- $t)

        switch $t
            case o a os as um uma uns umas de do da dos das pra para por com sobre em no na nos nas ao aos à às \
                 porfavor favor gentileza me mim ai aí pode poderia poderiame poderia-me
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
                echo __IGNORE__
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

    function __aury_is_action_start --argument-names tok
        set -l n (__aury_norm_token $tok)

        if contains -- $n ajuda reload dev instalar remover procurar criar copiar mover renomear status ver atualizar otimizar abrir internet ping
            return 0
        end

        return 1
    end

    # -------------------------------------------------
    # 0 — proteção de entrada
    # -------------------------------------------------

    if test (count $argv) -eq 0
        echo "❌ comando inválido"
        return 1
    end

    set -l raw_tokens $argv
    set -l raw_text (string join " " -- $raw_tokens)
    set raw_text (string trim -- $raw_text)

    if test -z "$raw_text"
        echo "❌ comando inválido"
        return 1
    end

    set -l clean_check (string replace -ra '[[:space:][:punct:]]' '' -- $raw_text)

    if test -z "$clean_check"
        echo "❌ comando inválido"
        return 1
    end

    if string match -rq '^[0-9 ]+$' -- $raw_text
        echo "❌ comando inválido"
        return 1
    end

    # -------------------------------------------------
    # 1 — detectar múltiplas ações com "e"
    # -------------------------------------------------

    set -l action_starts 1
    set -l action_ends

    set -l total (count $raw_tokens)
    set -l i 1

    while test $i -lt $total
        set -l current_norm (__aury_norm_token $raw_tokens[$i])
        set -l next_token $raw_tokens[(math $i + 1)]

        if test "$current_norm" = "e"
            if __aury_is_action_start $next_token
                set action_ends $action_ends (math $i - 1)
                set action_starts $action_starts (math $i + 1)
            end
        end

        set i (math $i + 1)
    end

    set action_ends $action_ends $total

    # -------------------------------------------------
    # 2 — processar cada ação
    # -------------------------------------------------

    set -l action_idx 1

    while test $action_idx -le (count $action_starts)
        set -l start $action_starts[$action_idx]
        set -l finish $action_ends[$action_idx]

        if test $finish -lt $start
            set action_idx (math $action_idx + 1)
            continue
        end

        set -l action_tokens $raw_tokens[$start..$finish]

        set -l norm_words
        set -l orig_words

        for tok in $action_tokens
            set -l norm (__aury_norm_token $tok)

            if test "$norm" = "__IGNORE__"
                continue
            end

            if test "$norm" = "e"
                continue
            end

            set norm_words $norm_words $norm
            set orig_words $orig_words $tok
        end

        if test (count $norm_words) -eq 0
            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 3 — ajuda
        # -------------------------------------------------

        if contains -- ajuda $norm_words
            echo "
💜 Aury 1.2

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
aury copiar arquivo teste.txt backup.txt
aury mover arquivo teste.txt pasta/teste.txt
aury renomear arquivo teste.txt novo.txt

EXTRAS
aury reload
aury dev
"
            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 3.1 — reload
        # -------------------------------------------------

        if contains -- reload $norm_words
            set -l file ~/.config/fish/functions/aury.fish

            if not test -f $file
                echo "❌ arquivo da Aury não encontrado"
                return 1
            end

            echo "🔄 recarregando Aury..."

            source $file

            if test $status -eq 0
                echo "✅ Aury recarregada"
            else
                echo "❌ erro ao recarregar"
            end

            return
        end

        # -------------------------------------------------
        # 3.2 — dev
        # -------------------------------------------------

        if contains -- dev $norm_words
            set -l file ~/.config/fish/functions/aury.fish

            if not test -f $file
                echo "❌ arquivo da Aury não encontrado"
                return 1
            end

            echo "🛠 verificando código da Aury..."

            set -l result (fish --no-execute $file 2>&1)

            if test $status -eq 0
                echo "✅ código válido"
            else
                echo "❌ erro detectado"

                set -l line (string match -r 'line [0-9]+|linha [0-9]+' -- $result)

                if test -n "$line"
                    echo "📍 erro encontrado em: $line"
                end

                echo ""
                echo $result
            end

            return
        end

        # -------------------------------------------------
        # 4 — atualizar sistema
        # -------------------------------------------------

        if contains -- atualizar $norm_words
            echo "📦 atualizando sistema"

            if type -q paru
                paru -Syu
            else
                sudo pacman -Syu
            end

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 5 — otimizar sistema
        # -------------------------------------------------

        if contains -- otimizar $norm_words
            echo "🚀 otimizando sistema"

            if type -q paccache
                sudo paccache -rk2
            end

            sudo journalctl --vacuum-time=7d

            set -l orphans (pacman -Qtdq 2>/dev/null)

            if test -n "$orphans"
                sudo pacman -Rns -- $orphans
            else
                echo "ℹ️ nenhum pacote órfão encontrado"
            end

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 6 — status
        # -------------------------------------------------

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

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 7 — informações do sistema
        # -------------------------------------------------

        if contains -- cpu $norm_words
            lscpu
            set action_idx (math $action_idx + 1)
            continue
        end

        if contains -- memória $norm_words
            free -h
            set action_idx (math $action_idx + 1)
            continue
        end

        if contains -- disco $norm_words
            df -h
            set action_idx (math $action_idx + 1)
            continue
        end

        if contains -- gpu $norm_words
            lspci | grep -Ei "vga|3d|display"
            set action_idx (math $action_idx + 1)
            continue
        end

        if contains -- processos $norm_words
            ps aux --sort=-%cpu | head -15
            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 8 — rede
        # -------------------------------------------------

        if contains -- ip $norm_words
            ip a
            set action_idx (math $action_idx + 1)
            continue
        end

        if contains -- internet $norm_words; and not contains -- ping $norm_words
            ping -c 2 -- 8.8.8.8
            set action_idx (math $action_idx + 1)
            continue
        end

        if contains -- ping $norm_words
            set -l idx (contains -i -- ping $norm_words)

            if test (count $orig_words) -le $idx
                echo "❌ especifique host"
            else
                set -l host (string join " " -- $orig_words[(math $idx + 1)..-1])
                ping -c 2 -- $host
            end

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 9 — procurar pacote
        # -------------------------------------------------

        if contains -- procurar $norm_words
            set -l idx (contains -i -- procurar $norm_words)

            if test (count $orig_words) -gt $idx
                set -l search (string join " " -- $orig_words[(math $idx + 1)..-1])
                pacman -Ss -- $search
            else
                echo "❌ termo não especificado"
            end

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 10 — instalar pacote
        # -------------------------------------------------

        if contains -- instalar $norm_words
            set -l idx (contains -i -- instalar $norm_words)

            if test (count $orig_words) -le $idx
                echo "❌ pacote não especificado"
                set action_idx (math $action_idx + 1)
                continue
            end

            set -l pkg_words $orig_words[(math $idx + 1)..-1]
            set -l pkg (string join "-" -- $pkg_words)

            if test -z "$pkg"
                echo "❌ pacote não especificado"
                set action_idx (math $action_idx + 1)
                continue
            end

            echo "📦 instalando $pkg"

            sudo pacman -S -- $pkg

            if test $status -ne 0
                if type -q paru
                    echo "ℹ️ tentando via paru..."
                    paru -S -- $pkg
                end
            end

            if test $status -ne 0
                if type -q flatpak
                    echo "ℹ️ tentando via flatpak..."
                    flatpak install -y flathub $pkg
                end
            end

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 11 — remover pacote
        # -------------------------------------------------

        if contains -- remover $norm_words; and not contains -- arquivo $norm_words; and not contains -- pasta $norm_words
            set -l idx (contains -i -- remover $norm_words)

            if test (count $orig_words) -le $idx
                echo "❌ pacote não especificado"
                set action_idx (math $action_idx + 1)
                continue
            end

            set -l pkg_words $orig_words[(math $idx + 1)..-1]
            set -l pkg (string join "-" -- $pkg_words)

            if test -z "$pkg"
                echo "❌ pacote não especificado"
                set action_idx (math $action_idx + 1)
                continue
            end

            echo "🗑 removendo $pkg"

            sudo pacman -Rns -- $pkg

            if test $status -ne 0
                if type -q paru
                    paru -Rns -- $pkg
                end
            end

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 12 — criar arquivo ou pasta
        # -------------------------------------------------

        if contains -- criar $norm_words
            set -l idx
            set -l target

            if contains -- pasta $norm_words
                set idx (contains -i -- pasta $norm_words)

                if test (count $orig_words) -le $idx
                    echo "❌ nome da pasta não especificado"
                    set action_idx (math $action_idx + 1)
                    continue
                end

                set target (string join " " -- $orig_words[(math $idx + 1)..-1])

                mkdir -p -- $target

                if test $status -eq 0
                    echo "📁 pasta criada: $target"
                else
                    echo "❌ erro ao criar pasta"
                end

                set action_idx (math $action_idx + 1)
                continue
            end

            if contains -- arquivo $norm_words
                set idx (contains -i -- arquivo $norm_words)

                if test (count $orig_words) -le $idx
                    echo "❌ nome do arquivo não especificado"
                    set action_idx (math $action_idx + 1)
                    continue
                end

                set target (string join " " -- $orig_words[(math $idx + 1)..-1])
            else
                set idx (contains -i -- criar $norm_words)

                if test (count $orig_words) -le $idx
                    echo "❌ nome não especificado"
                    set action_idx (math $action_idx + 1)
                    continue
                end

                set target (string join " " -- $orig_words[(math $idx + 1)..-1])
            end

            set -l parent_dir (dirname -- $target)

            if test "$parent_dir" != "."
                mkdir -p -- $parent_dir
            end

            touch -- $target

            if test $status -eq 0
                echo "📄 arquivo criado: $target"
            else
                echo "❌ erro ao criar arquivo"
            end

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 13 — remover arquivo ou pasta
        # -------------------------------------------------

        if contains -- remover $norm_words; and begin
            contains -- arquivo $norm_words; or contains -- pasta $norm_words
        end
            set -l type_word arquivo

            if contains -- pasta $norm_words
                set type_word pasta
            end

            set -l idx (contains -i -- $type_word $norm_words)

            if test (count $orig_words) -le $idx
                echo "❌ alvo não especificado"
                set action_idx (math $action_idx + 1)
                continue
            end

            set -l target (string join " " -- $orig_words[(math $idx + 1)..-1])

            if not test -e $target
                echo "❌ não encontrado: $target"
                set action_idx (math $action_idx + 1)
                continue
            end

            echo "⚠ confirmar exclusão de '$target' (s/n)"
            read -l confirm

            if test "$confirm" = "s" -o "$confirm" = "S"
                if test "$type_word" = "pasta"
                    rm -rf -- $target
                else
                    rm -f -- $target
                end

                if test $status -eq 0
                    echo "🗑 removido: $target"
                else
                    echo "❌ erro ao remover"
                end
            else
                echo "❌ cancelado"
            end

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 14 — copiar arquivo ou pasta
        # -------------------------------------------------

        if contains -- copiar $norm_words
            set -l idx
            set -l source
            set -l dest

            if contains -- arquivo $norm_words
                set idx (contains -i -- arquivo $norm_words)
            else if contains -- pasta $norm_words
                set idx (contains -i -- pasta $norm_words)
            else
                set idx (contains -i -- copiar $norm_words)
            end

            if test (count $orig_words) -lt (math $idx + 2)
                echo "❌ argumentos insuficientes"
                set action_idx (math $action_idx + 1)
                continue
            end

            set source $orig_words[(math $idx + 1)]
            set dest   $orig_words[(math $idx + 2)]

            if not test -e $source
                echo "❌ origem não encontrada: $source"
                set action_idx (math $action_idx + 1)
                continue
            end

            set -l dest_dir (dirname -- $dest)

            if test "$dest_dir" != "."
                mkdir -p -- $dest_dir
            end

            if test -d $source
                cp -r -- $source $dest
                set -l copy_type pasta
            else
                cp -- $source $dest
                set -l copy_type arquivo
            end

            if test $status -eq 0
                if test "$copy_type" = "pasta"
                    echo "📁 pasta copiada: $source → $dest"
                else
                    echo "📄 arquivo copiado: $source → $dest"
                end
            else
                echo "❌ erro ao copiar"
            end

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 15 — mover arquivo ou pasta
        # -------------------------------------------------

        if contains -- mover $norm_words
            set -l idx
            set -l source
            set -l dest

            if contains -- arquivo $norm_words
                set idx (contains -i -- arquivo $norm_words)
            else if contains -- pasta $norm_words
                set idx (contains -i -- pasta $norm_words)
            else
                set idx (contains -i -- mover $norm_words)
            end

            if test (count $orig_words) -lt (math $idx + 2)
                echo "❌ argumentos insuficientes"
                set action_idx (math $action_idx + 1)
                continue
            end

            set source $orig_words[(math $idx + 1)]
            set dest   $orig_words[(math $idx + 2)]

            if not test -e $source
                echo "❌ origem não encontrada: $source"
                set action_idx (math $action_idx + 1)
                continue
            end

            set -l dest_dir (dirname -- $dest)

            if test "$dest_dir" != "."
                mkdir -p -- $dest_dir
            end

            if test -d $source
                set -l move_type pasta
            else
                set -l move_type arquivo
            end

            mv -- $source $dest

            if test $status -eq 0
                if test "$move_type" = "pasta"
                    echo "📁 pasta movida: $source → $dest"
                else
                    echo "📄 arquivo movido: $source → $dest"
                end
            else
                echo "❌ erro ao mover"
            end

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # 16 — renomear arquivo ou pasta
        # -------------------------------------------------

        if contains -- renomear $norm_words
            set -l idx
            set -l source
            set -l newname

            if contains -- arquivo $norm_words
                set idx (contains -i -- arquivo $norm_words)
            else if contains -- pasta $norm_words
                set idx (contains -i -- pasta $norm_words)
            else
                set idx (contains -i -- renomear $norm_words)
            end

            if test (count $orig_words) -lt (math $idx + 2)
                echo "❌ argumentos insuficientes"
                set action_idx (math $action_idx + 1)
                continue
            end

            set source  $orig_words[(math $idx + 1)]
            set newname $orig_words[(math $idx + 2)]

            if not test -e $source
                echo "❌ arquivo ou pasta não encontrado: $source"
                set action_idx (math $action_idx + 1)
                continue
            end

            mv -- $source $newname

            if test $status -eq 0
                echo "✏️ renomeado: $source → $newname"
            else
                echo "❌ erro ao renomear"
            end

            set action_idx (math $action_idx + 1)
            continue
        end

        # -------------------------------------------------
        # fallback
        # -------------------------------------------------

        echo "❓ Não entendi: "(string join " " -- $action_tokens)
        echo "Digite: aury ajuda"

        set action_idx (math $action_idx + 1)
    end

end