# 💜 Aury

![version](https://img.shields.io/badge/version-v1.6.2-purple)
![shell](https://img.shields.io/badge/shell-fish-blue)
![platform](https://img.shields.io/badge/platform-CachyOS-orange)
![license](https://img.shields.io/badge/license-MIT-green)

**Aury** é uma assistente de terminal feita especificamente para **CachyOS**.

Ela permite executar tarefas do sistema usando **linguagem natural**, traduzindo frases humanas em ações reais no terminal. A proposta do projeto é reduzir fricção, acelerar tarefas comuns e tornar o uso do terminal mais natural sem perder o poder das ferramentas tradicionais.

---

> Estado público real da **v1.6.2**: a entrada continua em Fish, mas `help`, `version`, `dev <frase>` e as rotas Python já suportadas passam por um núcleo Python; nesta versão, `aury dev` reduz a distância diagnóstica para um conjunto curto de fluxos que o modo normal já sustenta, sem forçar nova migração de runtime.

## O que é a Aury

Aury funciona como uma camada de interpretação entre o usuário e o sistema.

Em vez de depender apenas de comandos tradicionais, você pode escrever o que quer fazer de um jeito mais humano, por exemplo:

```fish
aury quero instalar obs studio
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
aury mover arquivo teste.txt para pasta/teste.txt
aury extraia teste.tar para a pasta que fica em /usr/steam
```

A ideia não é substituir o terminal, mas tornar o uso dele mais confortável, direto e acessível.

---

## Exemplos rápidos

### Pacotes

```fish
aury instalar firefox
aury instala firefox
aury baixa o vlc
aury quero instalar obs studio
aury remover vlc
aury procurar steam
```

### Sistema

```fish
aury atualizar sistema
aury otimizar sistema
aury atualiza e otimiza
aury mostrar cpu
aury checar memória
aury mostrar o status do sistema
aury ver cpu e memória
```

### Rede

```fish
aury ver ip
aury testar internet
aury velocidade da internet
aury ping google.com
```

### Arquivos

```fish
aury criar arquivo teste.txt
aury cria um arquivo teste.txt
aury criar pasta projetos
aury copiar teste.txt para backup.txt
aury mover teste.txt para pasta/teste.txt
aury renomear teste.txt para novo.txt
aury apaga o arquivo teste.txt
```

### Extração

```fish
aury extrair teste.zip
aury descompacte backup.tar.gz
aury extraia teste.tar para a pasta que fica em /usr/steam
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
- extração segura de arquivos `.zip`, `.7z`, `.tar`, `.tar.gz` e `.tgz`
- conectores como `e`, `para`, `pra` e `em`
- suporte a vocativo como `Aury,`
- suporte a pontuação estilo chat
- corretor conservador com proteção de tokens sensíveis
- localização conversacional em fluxos de arquivo e extração
- anáforas locais seguras com `ele`, `ela` e `isso`
- fallback honesto com dica de ajuda quando o pedido sai do recorte atual
- confirmação destrutiva explícita para remoção e bloqueio de alvo anafórico inseguro
- ambiguidade pública de alvo/destino em vez de execução silenciosa
- observabilidade expandida com `aury dev <frase>`
- medição explícita de velocidade da internet via `librespeed-cli`

---

## Instalação

A instalação pública mínima da v1.6.2 é feita pelo script do repositório:

```fish
git clone https://github.com/el-abni/aury.git
cd aury
bash install.sh
```

O script instala a superfície pública em:

- `~/.config/fish/functions/aury.fish`
- `~/.config/fish/functions/ay.fish`
- `~/.local/share/aury/python/`
- `~/.local/share/aury/resources/`
- `~/.local/share/aury/VERSION`
- `~/.local/share/aury/LICENSE.md`

A instalação pública assume **Fish** e **python3** disponíveis no ambiente.

Depois da instalação, abra um novo shell Fish ou recarregue as funções:

```fish
source ~/.config/fish/functions/aury.fish
source ~/.config/fish/functions/ay.fish
```

A partir daí, `aury` e `ay` passam a usar a base instalada em `~/.local/share/aury`.

---

## Como usar

Para ver os exemplos e comandos disponíveis:

```fish
aury ajuda
ay ajuda
```

No código, a identidade visual da assistente é:

```text
💜 Aury
```

No comando de ajuda, a versão deve aparecer no formato:

```text
💜 Aury v1.6.2
```

A Aury entende tanto comandos diretos quanto frases mais naturais, como:

```fish
aury instalar firefox
ay instalar firefox
aury pode instalar o firefox
aury Aury, instala o obs studio.
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
```

Para inspecionar a leitura atual sem executar a ação:

```fish
aury dev ver cpu e memória
aury dev copiar arquivo teste.txt para backup.txt
```

## Contrato público mínimo da v1.6.2

- `aury ajuda` e `ay ajuda` renderizam `resources/help.txt` usando a `VERSION` da base ativa.
- `aury --version` e `ay --version` imprimem `💜 Aury <VERSION>` a partir da mesma base ativa.
- `aury dev <frase>` usa o núcleo Python e expõe plano da sequência, leitura por ação e decisão de execução.
- na v1.6.2, `aury dev` amplia o alinhamento diagnóstico para um conjunto curto de fluxos já sustentados pelo modo normal, sem prometer paridade total nem migração equivalente de runtime.
- `aury dev` sem frase continua disponível como utilitário mínimo do adaptador Fish; hoje ele serve para checagem rápida e deve ser tratado como provisório.
- `bin/aury.fish` é o ponto de entrada público: ele tenta o runtime Python primeiro e volta ao Fish quando a ação ainda não tem rota Python explícita.
- Em desenvolvimento, ao fazer `source bin/aury.fish`, a base ativa é o próprio root do repositório. Na instalação, a base ativa é `~/.local/share/aury`.

## Limites honestos

- pedidos fora do recorte atual, como `abrir arquivo`, continuam em fallback honesto
- o runtime Python atual cobre `help`, `version`, `dev <frase>` e um subconjunto explícito de ações; o restante continua voltando ao adaptador Fish
- `aury dev` sem frase continua provisório e não deve ser tratado como relatório canônico completo
- `aury velocidade da internet` depende de `librespeed-cli` e `python3` disponíveis no ambiente

---

## Roadmap

O roadmap mostra **apenas versões futuras ainda não lançadas para o fechamento da linha principal 1.x da Aury neste repositório**.

### v1.7

- ampliação incremental da capacidade operacional local
- continuidade do refinamento seguro dos fluxos práticos da Aury

### v1.8

- refinamentos intermediários da linha 1.x com foco em robustez, previsibilidade e experiência

### v1.9

- refinamento geral
- fechamento planejado da linha principal da Aury neste repositório

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

## Documentação

A documentação complementar do projeto fica em:

```text
docs/ARCHITECTURE.md
```
Base pública de testes:

- `tests/README.md`

---

## Licença

Este projeto é distribuído sob a licença **MIT**.
