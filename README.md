# 💜 Aury

![version](https://img.shields.io/badge/version-1.4.0-purple)
![arch](https://img.shields.io/badge/arch-Arch%20%7C%20CachyOS-blue)
![shell](https://img.shields.io/badge/shell-fish-00aaff)
![license](https://img.shields.io/badge/license-MIT-green)

Aury é um assistente de terminal para **Arch Linux / CachyOS** que permite controlar o sistema usando **frases naturais**.

A ideia é simples: usar o terminal como se estivesse **falando com o sistema**.

---

# Exemplos rápidos

## Instalar programas

```text
aury instalar firefox
aury quero instalar obs studio
aury baixa o vlc
```

## Informações do sistema

```text
aury mostrar cpu
aury ver cpu e memória
aury mostrar disco e gpu
aury mostrar o status do sistema
```

## Manutenção

```text
aury atualizar sistema
aury otimizar sistema
aury atualiza e otimiza
```

## Rede

```text
aury ver ip
aury testar internet
aury ping google.com
```

## Arquivos

```text
aury criar arquivo teste.txt
aury cria um arquivo teste.txt
aury copiar teste.txt para backup.txt
aury mover teste.txt para pasta/teste.txt
aury renomear teste.txt para novo.txt
aury apaga o arquivo teste.txt
```

---

# Instalação

Clone o repositório:

```bash
git clone https://github.com/el-abni/aury.git
cd aury
```

Copie o comando para o Fish:

```bash
cp bin/aury.fish ~/.config/fish/functions/aury.fish
```

Recarregue o shell:

```bash
source ~/.config/fish/functions/aury.fish
```

---

# Como usar

Digite:

```bash
aury ajuda
```

Isso mostra os comandos disponíveis.

A Aury aceita frases naturais como:

```text
aury Aury, instala o firefox
aury quero instalar obs studio
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
```

---

# Roadmap

### 1.0
Base do assistente.

### 1.1
Estrutura inicial.

### 1.2
Refatoração estrutural.

### 1.3
Melhoria da arquitetura interna.

### 1.4
Grande melhoria na interpretação de linguagem natural.

- frases naturais
- múltiplas intenções
- múltiplos alvos
- conectores como `para` e `em`
- comandos de arquivo mais humanos

### 1.5 (planejado)

- interpretação de caminhos mais inteligentes
- melhorias na análise semântica
- argumentos mais complexos

### 2.0 (planejado)

- comandos conversacionais completos
- parser mais avançado

---

# Filosofia

Aury tenta tornar o terminal mais acessível.

Em vez de decorar comandos complexos, o usuário pode simplesmente escrever algo como:

```text
aury instala o firefox
```

---

# Licença

MIT
