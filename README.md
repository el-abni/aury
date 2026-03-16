# 💜 Aury

![version](https://img.shields.io/badge/version-1.4.0-purple)
![shell](https://img.shields.io/badge/shell-fish-blue)
![platform](https://img.shields.io/badge/platform-CachyOS-orange)
![license](https://img.shields.io/badge/license-MIT-green)

**Aury** é uma assistente de terminal feita especificamente para **CachyOS**.

Ela permite executar tarefas do sistema usando **linguagem natural**, traduzindo frases humanas em ações reais no terminal. A proposta do projeto é reduzir fricção, acelerar tarefas comuns e tornar o uso do terminal mais natural sem perder o poder das ferramentas tradicionais.

---

## O que é a Aury

Aury funciona como uma camada de interpretação entre o usuário e o sistema.

Em vez de depender apenas de comandos tradicionais, você pode escrever o que quer fazer de um jeito mais humano, por exemplo:

```bash
aury quero instalar obs studio
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
aury mover arquivo teste.txt para pasta/teste.txt
```

---

## Exemplos rápidos

### Pacotes

```bash
aury instalar firefox
aury instala firefox
aury baixa o vlc
aury quero instalar obs studio
aury remover vlc
aury procurar steam
```

### Sistema

```bash
aury atualizar sistema
aury otimizar sistema
aury atualiza e otimiza
aury mostrar cpu
aury checar memória
aury mostrar o status do sistema
aury ver cpu e memória
```

### Rede

```bash
aury ver ip
aury testar internet
aury ping google.com
```

### Arquivos

```bash
aury criar arquivo teste.txt
aury cria um arquivo teste.txt
aury criar pasta projetos
aury copiar teste.txt para backup.txt
aury mover teste.txt para pasta/teste.txt
aury renomear teste.txt para novo.txt
aury apaga o arquivo teste.txt
```

---

## Funcionalidades

A versão atual da **💜 Aury** já oferece:

- interpretação de frases mais naturais
- suporte a múltiplas intenções no mesmo comando
- suporte a múltiplos alvos compartilhados
- comandos de pacote
- comandos de sistema
- comandos de rede
- comandos de arquivo
- conectores como `e`, `para`, `pra` e `em`
- suporte a vocativo como `Aury,`
- suporte a pontuação estilo chat

---

## Instalação

Clone o repositório:

```bash
git clone https://github.com/el-abni/aury.git
cd aury
```

Copie a função para o Fish:

```bash
cp bin/aury.fish ~/.config/fish/functions/aury.fish
```

Recarregue o shell:

```bash
source ~/.config/fish/functions/aury.fish
```

Agora o comando `aury` já pode ser usado no terminal.

---

## Como usar

Para ver os exemplos e comandos disponíveis:

```bash
aury ajuda
```

No código, a identidade visual da assistente é:

```text
💜 Aury
```

No comando de ajuda, a versão deve aparecer no formato:

```text
💜 Aury v1.4.0
```

A Aury entende tanto comandos diretos quanto frases mais naturais, como:

```bash
aury instalar firefox
aury pode instalar o firefox
aury Aury, instala o obs studio.
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
```

---

## Roadmap

O roadmap mostra **apenas versões futuras planejadas**.

### 1.5

- melhorias em argumentos
- caminhos complexos

### 1.6

- melhorias de rede

### 1.7

- melhorias de pacotes

### 1.8

- fallback inteligente

### 1.9

- refinamento geral

### 2.0

- IA local
- conversação natural
- fallback de comandos complexos

---

## Filosofia do projeto

Aury não tenta substituir o terminal tradicional.

Ela existe para:

- reduzir a fricção do uso diário
- acelerar tarefas comuns
- permitir comandos mais humanos
- tornar o terminal mais acessível para quem está começando no CachyOS

O terminal continua poderoso. Aury apenas adiciona uma camada de conforto e interpretação.

---

## Licença

Este projeto é distribuído sob a licença **MIT**.
