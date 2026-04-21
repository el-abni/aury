# tests/

Esta pasta guarda a base pública mínima de regressão auditável que sustenta o fechamento canônico da linha **1.x** da **💜 Aury**.

Ela nasceu como **Fase 0** na linha 1.6.x e continua pequena de propósito. Na abertura operacional da v1.7.0, essa mesma base ganhou um tooling inicial curto de preflight e auditoria para blindar melhor o chão público já herdado, sem virar framework.

Para a leitura pública da ladder, o documento primário é `docs/WORKFLOW.md`.
Este README explica a base executável e como cada audit/gate entra nessa ladder.

## Leitura pública desta pasta

Abra este arquivo depois de:

- `README.md`, para a superfície pública curta do repositório
- `docs/COMPATIBILITY.md`, para o contrato host-centric da linha
- `docs/WORKFLOW.md`, para a ladder e a diferença entre worktree hygiene e release hygiene
- `docs/ARCHITECTURE.md`, para ownership e fronteira Fish/Python

Este README existe para a base executável: audits, smokes, gates e o papel de cada um.

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
bash tests/worktree_gate_minimo.sh
bash tests/public_ux_smoke.sh
python3 tests/python_core_smoke.py
```

Na prática:

- `preflight_canonico.sh` junta a checagem mínima de sintaxe, coerência pública, paridade normal vs `aury dev` e os dois smokes já canonizados, sem inspecionar a stage pública
- `worktree_gate_minimo.sh` sobe um degrau e valida a worktree atual sem exigir stage pública
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
- `worktree_gate_minimo.sh`

Ferramentas de suporte do gate final, úteis quando houver iteração direta no contrato de saída ou na superfície pública:

```bash
bash tests/preflight_canonico.sh
bash tests/worktree_gate_minimo.sh
python3 tests/audit_exit_surfaces.py
```

Esses checks continuam importantes, mas não mudam a semântica do gate final: `release_gate_minimo.sh` continua sendo o degrau stage-based da ladder.

## Tipos de hygiene

- **worktree hygiene**: worktree sem erro textual, `preflight_canonico.sh` já aprovado, `audit_exit_surfaces.py` e unittests canônicos do `core_api` aprovados, ainda sem depender de stage pública.
- **release hygiene**: `worktree_gate_minimo.sh` já aprovado, stage pública explícita e coerente, nenhum arquivo privado/sensível staged e `git diff --cached --check` limpo.

Sem stage pública explícita, `release_gate_minimo.sh` deve falhar cedo. Esse fail não indica regressão funcional; só indica que a rodada ainda não entrou no degrau final da release hygiene.

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

Este auditor pequeno verifica o chão público mínimo que o encerramento canônico da v1.9.9 precisa manter coerente:

- `VERSION` preenchida
- `resources/help.txt` com placeholder de versão, chamada curta (`aury` / `ay`) e superfície prática sem virar mini-doc
- `README.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/COMPATIBILITY.md`, `docs/WORKFLOW.md` e `tests/README.md` alinhados à versão pública atual, à matriz final da linha 1.x e ao handoff limpo para a Aurora
- contrato curto de voz pública alinhado entre Fish e Python
- ausência de hardcode de versão no runtime público e nos scripts de instalação
- renderização real de `help` e `version` via entrada pública Fish

### `audit_canonical_layout.py`

Este auditor pequeno protege a canonização estrutural mínima da Onda 0:

- raiz viva resolvida pelo adaptador Fish e pelo runtime Python
- isolamento do artefato histórico `./aury/` no root Git
- existência da superfície canônica `python/aury/core_api.py`
- coerência mínima entre `docs/ARCHITECTURE.md`, `docs/COMPATIBILITY.md` e `docs/WORKFLOW.md`

### `audit_hybrid_boundary.py`

Este auditor pequeno protege a classificação estrutural da Onda 1:

- `bin/aury.fish` como entrypoint vivo
- `python/aury/fish_bridge.py` como bridge Python vivo da fronteira Fish/Python
- `python/aury/cli.py` como shim de compatibilidade, e não como fronteira canônica
- coerência mínima de `docs/ARCHITECTURE.md` e `docs/WORKFLOW.md` sobre `entrypoint`, `bridge`, `runtime`, `host` e `helpers`

### `audit_docs_pv_workflow.py`

Este auditor pequeno protege a consolidação documental da Onda 2:

- `README.md` como entrada pública mínima do checkout canônico
- `docs/WORKFLOW.md` distinguindo worktree hygiene e release hygiene
- `tests/README.md` refletindo a ladder sem disputar papel com `docs/WORKFLOW.md`
- `PV_VIVO_E_HISTORICO.md` e `arquivo/contexto/README.md` deixando operacional a leitura da PV viva vs histórica
- `WORKFLOW_CANONICO_RELEASE_AURY.md`, `CHECKLIST_RELEASE_SEGURA_AURY.md` e `FLUXO_FECHAMENTO_DE_VERSAO_AURY.md` com papéis explícitos e não conflitantes

### `audit_gate_ladder.py`

Este auditor pequeno protege a composição executável da ladder:

- `preflight_canonico.sh` continua sendo stage-agnostic e curto
- `worktree_gate_minimo.sh` continua compondo `preflight`, `audit_exit_surfaces.py` e os unittests canônicos do `core_api`
- `release_gate_minimo.sh` continua sendo o degrau stage-based e compõe o gate de worktree, em vez de duplicar seus checks
- `tests/_gate_common.sh` continua concentrando apenas o helper mínimo compartilhado entre os gates

### `audit_dev_parity.py`

Este auditor pequeno verifica um recorte de paridade operacional entre:

- a decisão do plano que `aury dev` expõe
- o executor realmente observado no modo normal

O foco é manter auditáveis as rotas já assumidas como Python e as que seguem canonicamente no adaptador Fish.
Na v1.9.9, isso inclui o enquadramento de `atualizar` / `otimizar` como manutenção do host local, sem paridade portátil com o domínio de pacote, e a distinção entre backends ativos do contrato e ferramentas apenas observadas.

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
- falha no gate de worktree já composto

Os checks abaixo continuam existindo, mas entram no gate final por composição e não como itens paralelos da régua canônica:

- `audit_public_coherence.py`
- `audit_canonical_layout.py`
- `audit_hybrid_boundary.py`
- `audit_docs_pv_workflow.py`
- `audit_dev_parity.py`
- `public_ux_smoke.sh`
- `python_core_smoke.py`
- `audit_exit_surfaces.py`
- `tests.test_canonical_core_surface`
- `tests.test_core_api_characterization`

### `worktree_gate_minimo.sh`

Este é o gate canônico de worktree da linha 1.x. Ele roda sem exigir stage pública e reúne:

- `preflight_canonico.sh`
- `audit_exit_surfaces.py`
- `tests.test_canonical_core_surface`
- `tests.test_core_api_characterization`

Ele existe para separar claramente:

- iteração local e validação da worktree
- gate final público em cima da stage explícita

O `preflight_canonico.sh` continua sendo o degrau curto da rodada e não inspeciona a stage pública.

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
