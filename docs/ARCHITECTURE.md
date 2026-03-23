# Arquitetura da 💜 Aury

Este documento descreve o estado público real sustentado pela **💜 Aury v1.7.0** no repositório canônico local.

A proposta do projeto não mudou: Aury continua recebendo frases humanas, fechando uma leitura segura e escolhendo entre executar, bloquear ou cair em fallback honesto. O que a linha 1.6.x consolidou foi a distribuição de responsabilidade entre o adaptador Fish e o núcleo Python, com um alinhamento curto extra de `aury dev` ao que o modo normal já sustenta. A `v1.7.0` fecha publicamente a abertura operacional e o bloco estrutural remanescente sem reabrir arquitetura; o único corte funcional novo da versão é a compactação local simples.

## Entrada pública e base instalada

Na v1.7.0, a entrada pública continua sendo Fish:

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
- `aury dev <frase>` usa o núcleo Python e já expõe plano da sequência, enquadramento por ação e decisão de execução.
- `aury dev` sem frase continua sendo um utilitário mínimo do adaptador Fish e ainda deve ser tratado como provisório.
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

Na prática, o adaptador Fish deixou de ser a única implementação da Aury. Ele agora coordena a execução pública, preserva compatibilidade e segura o que ainda não migrou.

## Escopo Python atual

No recorte atual da v1.7.0, o núcleo Python já cobre `help`, `version`, `dev`, preparação/análise interna, múltiplas ações no diagnóstico e um conjunto inicial de execuções normais já migradas.
Entre elas estão, por exemplo, busca de pacote, IP, teste simples de internet, velocidade da internet e algumas leituras simples de sistema.
Na leitura diagnóstica de `aury dev`, a v1.7.0 preserva esse alinhamento curto e também expõe a compactação local simples como rota ainda híbrida, sem implicar migração operacional equivalente de runtime.
Casos fora desse recorte ainda podem retornar integralmente ao adaptador Fish, de forma explícita e sem execução parcial obscura.

## O que continua no Fish

Neste ponto da v1.7.0, continuam no adaptador Fish:

- atualização e otimização
- instalação e remoção operacionais de pacotes
- arquivos, extração e compactação local simples
- confirmação destrutiva
- bloqueios e ambiguidades públicas do legado
- fallback honesto fora do recorte atual

Isso é deliberado. A v1.7.0 não promete rewrite total; ela fecha a superfície pública da release sem empurrar o runtime além do necessário.

A compactação da v1.7.0 também nasce com recorte curto de propósito: um único arquivo ou uma única pasta, saída explícita obrigatória e apenas `.zip` ou `.tar.gz`.

## Limites honestos

- a linha pública 1.6.x já é híbrida; documentá-la como “só Fish” ficou incorreto
- `aury dev <frase>` já é o relatório canônico da transição, mas não deve ser tratado como garantia de paridade total com toda formulação conversacional histórica do legado
- `aury dev` sem frase permanece provisório
- a instalação pública precisa manter `~/.local/share/aury` coerente com o conteúdo canônico do repositório
- dependências operacionais como `pacman`, `ping`, `ip`, `lscpu`, `free`, `df`, `uptime`, `lspci` e `librespeed-cli` continuam sendo responsabilidades do host

## Resumo

A **💜 Aury v1.7.0** continua tendo entrada pública em Fish, mas já não pode ser descrita como uma base exclusivamente Fish. O estado real agora é:

- Fish como adaptador e camada de compatibilidade
- Python como núcleo rastreado para `help`, `version`, `dev` e rotas explícitas de runtime
- share root instalado como fonte pública de versão e recursos
- fallback controlado para o que ainda não migrou
