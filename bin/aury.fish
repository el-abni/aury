# ==========================================================
# 💜 Aury v1.1
# Terminal Assistant for CachyOS
# Shell: fish
# ==========================================================

function aury

# -------------------------------------------------
# 0. proteção
# -------------------------------------------------

# sem argumentos
if test (count $argv) -eq 0
    echo "💜 Aury"
    echo "Digite: aury ajuda"
    return
end

# juntar argumentos
set raw (string join " " $argv)

# remover espaços extras
set raw (string trim $raw)

# remover quebras de linha
set raw (string replace -a "\n" " " $raw)

# se entrada ficou vazia
if test -z "$raw"
    echo "💜 Aury"
    echo "Digite: aury ajuda"
    return
end

# proteger contra apenas pontuação
set test_clean (string replace -ra "[[:punct:]]" "" $raw)

if test -z (string trim $test_clean)
    echo "❌ comando inválido"
    return
end

# -------------------------------------------------
# 1. parser base
# -------------------------------------------------

# normalizar texto
set lower (string lower $raw)

# remover pontuações comuns
set lower (string replace -a "," "" $lower)
set lower (string replace -a "." "" $lower)
set lower (string replace -a "?" "" $lower)
set lower (string replace -a "!" "" $lower)

# remover múltiplos espaços
set lower (string replace -ra "\s+" " " $lower)

# separar múltiplas ações
# exemplo: "instalar firefox e abrir pasta"
set actions (string split " e " $lower)

for action in $actions

    # limpar espaços laterais
    set action (string trim $action)

    # ignorar ação vazia
    if test -z "$action"
        continue
    end

    # transformar frase em palavras
    set words (string split " " $action)

# -------------------------------------------------
# 2. normalização inteligente
# -------------------------------------------------

set normalized

for w in $words

# correção de digitação
switch $w
case instalr isntalar instal
set w instalar
case removr remvoe
set w remover
case procra procuar
set w procurar
end


switch $w

# palavras ignoradas
case o a os as um uma de do da pra para por favor porfavor poderia pode poderia-me me mim ai aí
continue

# instalar
case instala instalar instale instalaram adicionar add
set normalized $normalized instalar

# remover
case remover remove remov deletar excluir apagar desinstalar desinstala desinstale uninstall
set normalized $normalized remover

# procurar
case procurar procura buscar busca pesquise pesquisar acha achar encontrar
set normalized $normalized procurar

# criar
case criar cria crie gerar
set normalized $normalized criar

# ver
case ver veja mostra mostrar exibir
set normalized $normalized ver

# atualizar
case atualizar atualiza update upgrade
set normalized $normalized atualizar

# otimizar
case limpar limpa otimizar otimiza
set normalized $normalized otimizar

# rede
case testar teste
set normalized $normalized internet

# arquivos
case pasta diretório diretorio folder
set normalized $normalized pasta

case arquivo file
set normalized $normalized arquivo

case "*"
set normalized $normalized $w

end

end

set words $normalized

if test (count $words) -eq 0
continue
end

set last $words[-1]


# -------------------------------------------------
# 3. ajuda
# -------------------------------------------------

if contains ajuda $words

echo "
💜 Aury 1.1

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
"

continue
end

# -------------------------------------------------
# 3.1 recarregar aury
# -------------------------------------------------

if string match -q "*reload*" $raw

    set file ~/.config/fish/functions/aury.fish

    if not test -f $file
        echo "❌ arquivo da Aury não encontrado"
        return
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
# 3.2 modo desenvolvedor
# -------------------------------------------------

if string match -q "*dev*" $raw

    set file ~/.config/fish/functions/aury.fish

    if not test -f $file
        echo "❌ arquivo da Aury não encontrado"
        return
    end

    echo "🛠 verificando código da Aury..."

    set result (fish --no-execute $file 2>&1)

    if test $status -eq 0
        echo "✅ código válido"
    else
        echo "❌ erro detectado"

        set line (string match -r "linha [0-9]+" $result)

        if test -n "$line"
            echo "📍 erro encontrado na $line"
        end

        echo ""
        echo $result
    end

    return
end

# -------------------------------------------------
# 4. atualizar sistema
# -------------------------------------------------

if contains atualizar $words

echo "📦 atualizando sistema"

if type -q paru
paru -Syu
else
sudo pacman -Syu
end

continue
end


# -------------------------------------------------
# 5. otimizar sistema
# -------------------------------------------------

if contains otimizar $words

echo "🚀 otimizando sistema"

sudo paccache -ruk1
sudo journalctl --vacuum-time=7d

set orphans (pacman -Qtdq)

if test -n "$orphans"
sudo pacman -Rns $orphans
end

continue
end


# -------------------------------------------------
# 6. status
# -------------------------------------------------

if contains status $words

echo "CPU"
lscpu | grep -i model

echo ""
echo "RAM"
free -h

echo ""
echo "DISCO"
df -h /

continue
end


# -------------------------------------------------
# 7. informações sistema
# -------------------------------------------------

if contains cpu $words
lscpu
continue
end

if contains memória $words
free -h
continue
end

if contains disco $words
df -h
continue
end

if contains gpu $words
lspci | grep -i vga
continue
end

if contains processos $words
ps aux | head
continue
end


# -------------------------------------------------
# 8. rede
# -------------------------------------------------

if contains ip $words
ip a
continue
end

if contains internet $words
ping -c 2 8.8.8.8
continue
end

if contains ping $words

if test -z "$last"
echo "❌ especifique host"
else
ping -c 2 $last
end

continue
end


# -------------------------------------------------
# 9. procurar pacote
# -------------------------------------------------

if contains procurar $words

set idx (contains -i procurar $words)

if test (count $words) -gt $idx
set search (string join " " $words[(math $idx + 1)..-1])
pacman -Ss $search
else
echo "❌ termo não especificado"
end

continue
end


# -------------------------------------------------
# 10. instalar pacote
# -------------------------------------------------

if contains instalar $words

set idx (contains -i instalar $words)

if test (count $words) -gt $idx

set pkg_words $words[(math $idx + 1)..-1]
set pkg (string join "-" $pkg_words)

echo "📦 instalando $pkg"

sudo pacman -S $pkg

if test $status -ne 0
if type -q paru
paru -S $pkg
end
end

if test $status -ne 0
if type -q flatpak
flatpak install -y flathub $pkg
end
end

else
echo "❌ pacote não especificado"
end

continue
end


# -------------------------------------------------
# 11. remover pacote
# -------------------------------------------------

if contains remover $words; and not contains arquivo $words

set idx (contains -i remover $words)

if test (count $words) -gt $idx

set pkg_words $words[(math $idx + 1)..-1]
set pkg (string join "-" $pkg_words)

echo "🗑 removendo $pkg"

sudo pacman -Rns $pkg

if test $status -ne 0
if type -q paru
paru -Rns $pkg
end
end

else
echo "❌ pacote não especificado"
end

continue
end


# -------------------------------------------------
# 12. criar arquivos
# -------------------------------------------------

if contains criar $words

if contains pasta $words
mkdir -p $last
echo "📁 pasta criada"
else
touch $last
echo "📄 arquivo criado"
end

continue
end


# -------------------------------------------------
# 13. remover arquivo
# -------------------------------------------------

if contains remover $words; and contains arquivo $words

echo "⚠ confirmar exclusão (s/n)"
read confirm

if test "$confirm" = "s"
rm $last
echo "🗑 removido"
else
echo "❌ cancelado"
end

continue
end


# -------------------------------------------------
# fallback
# -------------------------------------------------

echo "❓ Não entendi: $action"
echo "Digite: aury ajuda"

end

end
