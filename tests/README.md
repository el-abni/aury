# tests/

Esta pasta guarda a base pública mínima de regressão auditável herdada do fechamento da **💜 Aury v1.6.3**.

Ela nasceu como **Fase 0** na linha 1.6.x e continua pequena de propósito. Na abertura operacional da v1.7, essa mesma base ganhou um tooling inicial curto de preflight e auditoria para blindar melhor o chão público já herdado, sem virar framework.

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

## Execução mínima hoje

Os comandos mínimos validados nesta fase são:

```bash
bash tests/preflight_canonico.sh
bash tests/public_ux_smoke.sh
python3 tests/python_core_smoke.py
```

Na prática:

- `preflight_canonico.sh` junta a checagem mínima de sintaxe, coerência pública, paridade normal vs `aury dev` e os dois smokes já canonizados
- `public_ux_smoke.sh` protege a superfície pública do adaptador Fish
- `python_core_smoke.py` protege o núcleo Python já canonizado

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
- recorte público da medição de velocidade de rede
- `help`, `version`, `ay` e o contrato mínimo do adaptador Fish

### `audit_public_coherence.py`

Este auditor pequeno verifica o chão público mínimo que a abertura da v1.7 precisa manter coerente:

- `VERSION` preenchida
- `resources/help.txt` com placeholder de versão e nota honesta sobre `aury dev`
- `README.md` e `CHANGELOG.md` alinhados à versão pública atual e à abertura operacional contida da v1.7
- ausência de hardcode de versão no runtime público e nos scripts de instalação
- renderização real de `help` e `version` via entrada pública Fish

### `audit_dev_parity.py`

Este auditor pequeno verifica um recorte de paridade operacional entre:

- a decisão do plano que `aury dev` expõe
- o executor realmente observado no modo normal

O foco é manter auditáveis as rotas já assumidas como Python e as que seguem canonicamente no adaptador Fish.

Ele não substitui o `casos.yaml`. Os dois cumprem papéis diferentes:

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
- leituras simples de rede no runtime Python
- busca de pacote e leitura de GPU no runtime Python
- preparação de frase, ações e tokens sensíveis
- plano de execução por ação e por sequência
- regressão mínima da virada Fish -> Python
