# Arquitetura da 💜 Aury

Este documento descreve o estado público real sustentado pela **💜 Aury v1.9.1** no repositório canônico local.

A proposta do projeto não mudou: Aury continua recebendo frases humanas, fechando uma leitura segura e escolhendo entre executar, bloquear ou cair em fallback honesto. O que a linha 1.6.x consolidou foi a distribuição de responsabilidade entre o adaptador Fish e o núcleo Python. A v1.7.0 abriu e estabilizou a superfície pública híbrida atual; a v1.8.0 endureceu o contrato observável dessa mesma base; a v1.9.0 fechou a base híbrida contida; e a v1.9.1 abre a frente inicial de compatibilidade Linux com perfil mínimo de host e política de pacote por família, sem reabrir parser nem prometer suporte total entre distros.

## Entrada pública e base instalada

Na v1.9.1, a entrada pública continua sendo Fish:

- `aury` é exposto por `bin/aury.fish`
- `ay` continua sendo um atalho fino para `aury`

Quando instalada pelo fluxo público, a base ativa fica em:

```text
~/.config/fish/functions/aury.fish
~/.config/fish/functions/ay.fish
~/.local/share/aury/python/
~/.local/share/aury/resources/
~/.local/share/aury/VERSION
~/.local/share/aury/LICENSE.md
```

Quando o adaptador é carregado direto do checkout com `source bin/aury.fish`, ele usa o próprio root do repositório como share root ativo. No modo instalado, ele usa `~/.local/share/aury`. Essa base é passada ao núcleo Python via `PYTHONPATH` e `AURY_SHARE_DIR`.

## Contratos públicos explícitos

- `aury ajuda` e `ay ajuda` renderizam `resources/help.txt` com a `VERSION` da base ativa.
- `aury --version` e `ay --version` imprimem `💜 Aury <VERSION>` a partir da mesma base.
- `aury dev <frase>` usa o núcleo Python e já expõe plano da sequência, enquadramento por ação, plano de execução e decisão de sequência.
- `aury dev` sem frase fica mantido como verificação local curta e utilitário secundário do adaptador Fish.
- o gate final mínimo canônico da linha 1.x é `bash tests/release_gate_minimo.sh`.
- `reload` continua sendo responsabilidade do adaptador Fish.

## Fluxo real de execução

```text
Entrada do usuário
↓
Adaptador Fish (`aury`)
↓
Resolução do share root e do interpretador Python
↓
Tentativa no núcleo Python
↓
Se houver rota Python suportada: execução ou relatório no Python
↓
Se o Python devolver 120: volta controlada ao Fish
↓
Se faltar interpretador: fallback local de help/version ou execução Fish
↓
Se o Python devolver erro operacional próprio: erro exposto ao usuário
```

Na prática, o adaptador Fish deixou de ser a única implementação da Aury. Ele agora coordena a execução pública, preserva compatibilidade e atende o recorte que permanece nele nesta linha.

## Escopo Python atual

No recorte atual da v1.9.1, o núcleo Python já cobre `help`, `version`, `dev`, preparação/análise interna, múltiplas ações no diagnóstico e um conjunto explícito de execuções normais já sustentadas diretamente.
Entre elas estão IP, teste simples de internet, velocidade da internet, algumas leituras simples de sistema, `criar arquivo` / `criar pasta` e, agora, a política inicial de pacote por host Linux para `procurar`, `instalar` e `remover`.
Nesse domínio, o runtime Python já concentra a decisão de backend, o bloqueio honesto por perfil de host e o endurecimento operacional mínimo da v1.9.1: ausência de resultado em busca, no-op honesto e confirmação de estado quando o backend Tier 1 permite isso.
Na leitura diagnóstica de `aury dev`, a v1.9.1 preserva a linguagem pública auditável e passa a expor também o perfil mínimo do host quando a ação entra no domínio de pacote.
Compactação local simples continua sendo uma rota híbrida: o relatório `dev` a observa com honestidade, mas a execução normal permanece no adaptador Fish.
Casos fora desse recorte podem retornar integralmente ao adaptador Fish, de forma explícita e sem execução parcial obscura.

## O que continua no Fish

Na v1.9.1, continuam no adaptador Fish:

- atualização e otimização
- copiar, mover, renomear, remover e a maior parte do domínio de arquivos
- extração e compactação local simples
- confirmação destrutiva
- bloqueios e ambiguidades públicas do legado
- fallback honesto fora do recorte atual

Isso é deliberado. A v1.9.1 abre compatibilidade inicial no domínio de pacote sem prometer migração ampla do domínio de arquivos e sem empurrar o runtime além do necessário.

No domínio de pacote, porém, o Fish não volta a concentrar política: ele continua sendo a entrada pública, mas a política canônica de backend e suporte vive no Python. Se essa política não puder subir, a superfície pública bloqueia honestamente em vez de improvisar fallback localista.

A compactação herdada da v1.7.0 também permanece com recorte curto de propósito: um único arquivo ou uma única pasta, saída explícita obrigatória e apenas `.zip` ou `.tar.gz`.

## Limites honestos

- a linha pública 1.6.x já é híbrida; documentá-la como “só Fish” ficou incorreto
- `aury dev <frase>` já é o relatório canônico do recorte híbrido atual, mas não deve ser tratado como garantia de paridade total com toda formulação conversacional histórica do legado
- `aury dev` sem frase fica restrito a verificação local curta e secundária do adaptador Fish
- a instalação pública precisa manter `~/.local/share/aury` coerente com o conteúdo canônico do repositório
- o perfil mínimo de host Linux ainda cobre só família, mutabilidade e backends centrais de pacote; OpenSUSE entra apenas com detecção/bloqueio honesto e Atomic permanece bloqueado nesta fase
- a v1.9.1 fecha compatibilidade Linux inicial só no domínio de pacote; ela não deve ser descrita como suporte cross-distro amplo nem como paridade total entre famílias
- dependências operacionais como `pacman`, `paru`, `apt-cache`, `apt-get`, `dnf`, `ping`, `ip`, `lscpu`, `free`, `df`, `uptime`, `lspci` e `librespeed-cli` continuam sendo responsabilidades do host

## Resumo

A **💜 Aury v1.9.1** continua a linha 1.x com entrada pública em Fish, mas já não pode ser descrita como uma base exclusivamente Fish. O estado real atual é:

- Fish como adaptador e camada de compatibilidade
- Python como núcleo rastreado para `help`, `version`, `dev` e rotas explícitas de runtime
- perfil mínimo de host Linux centralizado no núcleo Python para pacote
- política inicial de pacote por família Linux: Arch, Debian/Ubuntu e Fedora mutável como Tier 1; OpenSUSE detectado com bloqueio honesto; Atomic bloqueado com honestidade
- pacote endurecido no recorte atual: busca honesta, no-op explícito e ausência de fallback localista de política no Fish
- micro-recorte de criação simples (`criar arquivo` / `criar pasta`) já executando no runtime Python
- share root instalado como fonte pública de versão e recursos
- fallback controlado para o que permanece fora do núcleo Python nesta linha
- gate final mínimo canônico explicitado em `bash tests/release_gate_minimo.sh`
