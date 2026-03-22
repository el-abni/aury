# tests/

Esta pasta guarda a base pública mínima de regressão auditável da **💜 Aury v1.6.2**.

Ela nasceu como **Fase 0** e continua pequena de propósito. O papel atual não é virar framework: é proteger o miolo público que a v1.6 consolidou e deixar o estado observável do projeto auditável.

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
bash tests/public_ux_smoke.sh
python3 tests/python_core_smoke.py
```

Na prática:

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

Este script protege o recorte público mais estável da v1.6.

Hoje ele cobre de forma executável:

- fallback honesto
- bloqueio destrutivo explícito
- confirmação destrutiva segura
- ambiguidade mínima exposta no runtime
- encadeamento pequeno com referência local
- recorte público da medição de velocidade de rede
- `help`, `version`, `ay` e o contrato mínimo do adaptador Fish

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

Este smoke cobre o núcleo Python rastreado da v1.6.2.

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
