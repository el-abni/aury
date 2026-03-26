# tests/

Esta pasta guarda a base pública mínima de regressão auditável que sustenta o fechamento canônico da linha **1.x** da **💜 Aury**.

Ela nasceu como **Fase 0** na linha 1.6.x e continua pequena de propósito. Na abertura operacional da v1.7.0, essa mesma base ganhou um tooling inicial curto de preflight e auditoria para blindar melhor o chão público já herdado, sem virar framework.

## Papel atual

Esta pasta existe para:

- manter um piso mínimo de regressão pública
- registrar casos observáveis que importam para o pipeline e para a UX pública
- proteger a superfície mais sensível sem inflar infraestrutura

Ela **não** existe para:

- virar suíte completa
- virar framework genérico
- prometer cobertura total do projeto
- substituir validação manual quando o caso ainda é fronteira de parser

## Fechamento final auditado

Esta base mínima protege a leitura final da linha 1.x:

- suportado agora: Arch/derivadas mutáveis, Debian/Ubuntu/derivadas mutáveis e Fedora mutável
- suportado contido: OpenSUSE mutável
- bloqueado por política: Atomic, Universal Blue, `opensuse-microos`, `microos` e equivalentes
- observado, mas fora do contrato ativo: `flatpak` e `rpm-ostree`
- handoff para a Aurora: software do usuário, múltiplas origens, política de origem/source/trust e suporte operacional real a hosts imutáveis pertencem à Aurora, não à Aury 1.x

## Execução mínima hoje

Para iteração local curta, os comandos mínimos continuam sendo:

```bash
bash tests/preflight_canonico.sh
bash tests/public_ux_smoke.sh
python3 tests/python_core_smoke.py
```

Na prática:

- `preflight_canonico.sh` junta a checagem mínima de sintaxe, coerência pública, paridade normal vs `aury dev` e os dois smokes já canonizados
- `public_ux_smoke.sh` protege a superfície pública do adaptador Fish
- `python_core_smoke.py` protege o núcleo Python já canonizado

## Gate final canônico da linha 1.x

O gate final mínimo canônico da linha 1.x é:

```bash
bash tests/release_gate_minimo.sh
```

Se você precisar validar esse gate sem tocar na stage real do usuário, use um índice Git temporário com `GIT_INDEX_FILE` e faça o staging só nesse índice descartável.

Esse wrapper é o gate final porque ele já reúne, em cima da stage pública explícita:

- higiene da stage pública
- `preflight_canonico.sh`
- `audit_exit_surfaces.py`

Ferramentas de suporte do gate final, úteis quando houver iteração direta no contrato de saída ou na superfície pública:

```bash
bash tests/preflight_canonico.sh
python3 tests/audit_exit_surfaces.py
```

Esses dois checks continuam importantes, mas não entram como itens separados da régua final quando `release_gate_minimo.sh` já está sendo usado.

## Arquivos atuais

### `casos.yaml`

Este arquivo continua sendo o contrato incremental de casos da v1.6.

Hoje ele funciona como:

- catálogo mínimo de casos
- ordem sugerida de leitura e execução
- referência curta de comportamento esperado
- base de auditoria humana para o miolo público

Ele ainda **não** é:

- runner sofisticado
- suíte fechada
- prova automática de paridade total entre runtime e `aury dev`

Essa última distinção importa: alguns casos de `modo: dev`, especialmente os mais conversacionais, ainda descrevem a direção desejada de paridade e não devem ser lidos como garantia de que toda formulação já fecha hoje com a mesma robustez.

### `public_ux_smoke.sh`

Este script protege o recorte público mais estável herdado da v1.6.3.

Hoje ele cobre de forma executável:

- fallback honesto
- bloqueio destrutivo explícito
- confirmação destrutiva segura
- ambiguidade mínima exposta no runtime
- encadeamento pequeno com referência local
- compactação local simples no recorte mínimo da v1.7.0
- recorte público da medição de velocidade de rede
- `help`, `version`, `ay` e o contrato mínimo do adaptador Fish

### `audit_public_coherence.py`

Este auditor pequeno verifica o chão público mínimo que o encerramento canônico da v1.9.8 precisa manter coerente:

- `VERSION` preenchida
- `resources/help.txt` com placeholder de versão e nota honesta sobre `aury dev`
- `README.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md` e `tests/README.md` alinhados à versão pública atual, à matriz final da linha 1.x e ao handoff limpo para a Aurora
- ausência de hardcode de versão no runtime público e nos scripts de instalação
- renderização real de `help` e `version` via entrada pública Fish

### `audit_dev_parity.py`

Este auditor pequeno verifica um recorte de paridade operacional entre:

- a decisão do plano que `aury dev` expõe
- o executor realmente observado no modo normal

O foco é manter auditáveis as rotas já assumidas como Python e as que seguem canonicamente no adaptador Fish.
Na v1.9.8, isso inclui o enquadramento de `atualizar` / `otimizar` como manutenção do host local, sem paridade portátil com o domínio de pacote, e a distinção entre backends ativos do contrato e ferramentas apenas observadas.

### `audit_exit_surfaces.py`

Este auditor pequeno verifica um recorte canônico de status de saída e superfície de erro:

- sucesso público simples
- fallback honesto
- bloqueio destrutivo explícito
- fronteira `120` do runtime Python direto contra `0` na entrada pública com fallback para o Fish
- fronteira equivalente da compactação local simples ainda híbrida
- falha operacional do speedtest
- fallback técnico de `help`, `version` e `aury dev <frase>` quando o Python devolve `127`
- OpenSUSE mutável com execução real contida de `procurar`, `instalar` e `remover`
- OpenSUSE mutável com busca sem resultado honesta e distinção entre backend ausente e sonda auxiliar ausente
- Atomic preservado em bloqueio honesto de pacote do host, distinto de backend ausente e de sonda auxiliar ausente
- `flatpak` / `rpm-ostree` observados apenas fora do contrato ativo, sem parecer instalação operacional implícita
- manutenção do host em Arch preservada como rota local no Fish, sem fingir rota Python portátil
- manutenção do host em Debian saindo como fora do recorte equivalente, e não como backend ausente
- manutenção do host em Atomic preservada como bloqueio por política
- help público com matriz final explícita da linha 1.x e handoff limpo para a Aurora

### `release_gate_minimo.sh`

Este é o gate final mínimo canônico da linha 1.x. Ele roda em cima da stage pública atual e bloqueia cedo:

- stage vazia ou fora do recorte público esperado
- arquivo privado/sensível staged
- erro textual em `git diff --cached --check`
- falha no preflight canônico
- falha no auditor de exit status

Os checks abaixo continuam existindo, mas entram no gate final por composição e não como itens paralelos da régua canônica:

- `audit_public_coherence.py`
- `audit_dev_parity.py`
- `public_ux_smoke.sh`
- `python_core_smoke.py`
- `audit_exit_surfaces.py`

Esses auditores e o gate não substituem o `casos.yaml`. Os papéis continuam separados:

- `casos.yaml` registra o contrato incremental
- `public_ux_smoke.sh` valida a parte já estabilizada da UX pública

## Ordem de leitura útil

Para esta base mínima, a ordem mais útil continua sendo:

1. `aury dev`
2. fallback
3. arquivos
4. anáfora local
5. extração
6. destrutivos por último

## Limites deliberados

Para manter a pasta saudável, esta rodada continua evitando:

- framework novo
- runner complexo
- infraestrutura grande de testes
- crescimento rápido sem ganho claro de auditoria
- edição de `casos.yaml` sem motivo estrutural real

## Critério de sanidade

Se esta pasta crescer rápido demais, ela provavelmente está tentando resolver arquitetura com volume de teste em vez de proteger a superfície certa.

O foco aqui continua sendo:

- pequeno
- auditável
- útil
- disciplinado


### `python_core_smoke.py`

Este smoke cobre o núcleo Python rastreado herdado do fechamento da v1.6.3.

Hoje ele protege:

- `help`
- `version`
- `aury dev <frase>` no núcleo novo
- alinhamento curto adicional de `aury dev` com fluxos já sustentados pelo modo normal
- parser e contrato mínimo de `aury dev` para a compactação local simples da v1.7.0
- leituras simples de rede no runtime Python
- busca de pacote e leitura de GPU no runtime Python
- política de pacote por família Linux, inclusive OpenSUSE mutável no recorte contido e a fronteira explícita dos hosts imutáveis bloqueados por política
- preparação de frase, ações e tokens sensíveis
- plano de execução por ação e por sequência
- regressão mínima da virada Fish -> Python
