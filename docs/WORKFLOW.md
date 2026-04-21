# Workflow da 💜 Aury

Este documento registra a ladder mínima de validação da **💜 Aury v1.9.9** no checkout canônico atual.
O `README.md` mantém a superfície curta do repositório; este arquivo responde pela ordem de uso dos gates e pelo significado operacional de cada degrau. Fronteiras e ownership ficam em `docs/ARCHITECTURE.md`; o contrato host-centric fica em `docs/COMPATIBILITY.md`.

A `v1.9.9` não reabre a ladder: ela só fecha o micro-acabamento final de UX/persona/help/release hygiene sobre a mesma espinha canônica das Ondas 0–5.

## Raiz canônica

- a única raiz viva é o checkout Git de topo do repositório;
- `./aury/` é um **artefato histórico/aninhado** e não entra na leitura viva, nos gates nem na base ativa;
- em modo instalado, a base viva fica em `~/.local/share/aury`.

## Fronteira híbrida viva

- `bin/aury.fish` continua sendo o entrypoint público da linha.
- `python/aury/fish_bridge.py` é o bridge Python vivo chamado por `python -m aury`.
- `python/aury/cli.py` permanece apenas como shim de compatibilidade para imports históricos.
- `python/aury/runtime.py`, `python/aury/host.py` e `python/aury/resources.py` continuam sendo, respectivamente, runtime, policy do host e helper de base compartilhada.

## Papéis da ladder

- `preflight_canonico.sh` responde pela checagem curta da rodada.
- `worktree_gate_minimo.sh` responde pela **worktree hygiene** do checkout atual.
- `release_gate_minimo.sh` responde pela **release hygiene** da stage pública explícita.

## Ladder mínima

### 1. Preflight

```bash
bash tests/preflight_canonico.sh
```

Uso:

- sintaxe Fish;
- coerência pública;
- guardrail de layout canônico;
- guardrail curto de docs + PV + workflow;
- guardrail curto da própria composição da ladder;
- paridade curta `aury dev` vs modo normal;
- smokes públicos e do núcleo Python.
- não inspeciona a stage pública nem substitui os gates de worktree/release.

### 2. Gate de worktree

```bash
bash tests/worktree_gate_minimo.sh
```

Uso:

- valida a worktree atual sem exigir stage pública;
- compõe o `preflight`, o auditor de superfícies de saída e os unittests canônicos do `core_api`;
- é o degrau correto quando a rodada ainda está em iteração local;
- fecha a **worktree hygiene** antes de qualquer staging público.

### 3. Gate final público

```bash
bash tests/release_gate_minimo.sh
```

Uso:

- roda **depois** do staging público explícito;
- valida a seleção staged;
- compõe o gate de worktree já aprovado;
- fecha a **release hygiene** da stage pública.

Sem arquivos staged, esse gate deve falhar cedo. Isso não indica regressão funcional; indica apenas que a rodada ainda não entrou no degrau final da ladder.

Se você precisar validar o gate final sem tocar na stage real do usuário, use um índice Git temporário com `GIT_INDEX_FILE`.

## Tipos de hygiene

### Worktree hygiene

- `git diff --check` limpo na worktree;
- preflight já aprovado;
- `audit_exit_surfaces.py` e os unittests canônicos do `core_api` aprovados;
- rodada ainda sem depender de stage pública explícita.

### Release hygiene

- `worktree_gate_minimo.sh` já aprovado;
- stage pública explícita e coerente com o recorte da rodada;
- nenhum arquivo privado/sensível staged;
- `git diff --cached --check` limpo;
- `release_gate_minimo.sh` validando a seleção staged, e não a worktree inteira pela primeira vez.

## Regra de interpretação

- `preflight` é diagnóstico curto.
- `worktree_gate_minimo.sh` é o gate canônico de iteração.
- `release_gate_minimo.sh` é o gate final stage-based.
- `preflight` não inspeciona a stage pública e não disputa o papel dos gates.
- falha por stage vazia no gate final não é regressão funcional; é apenas ausência do degrau final de release hygiene.

Os três degraus contam a mesma história; cada um só acrescenta a trava proporcional ao estágio da rodada.
