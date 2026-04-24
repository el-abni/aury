# 💜 Aury

![version](https://img.shields.io/badge/version-v1.9.9-purple)
![shell](https://img.shields.io/badge/shell-fish-blue)
![platform](https://img.shields.io/badge/platform-Linux-orange)
![license](https://img.shields.io/badge/license-MIT-green)

**Aury** é uma assistente de terminal para **Linux** com linha pública **host-centric** e superfície deliberadamente pequena. Hoje ela continua híbrida: o entrypoint público segue em Fish, e o runtime Python rastreado já sustenta `help`, `version`, `aury dev <frase>` e as rotas normais explicitamente migradas.

## O que a Aury é hoje

A Aury não tenta virar uma Aurora menor. A linha `1.x` fecha um recorte pequeno, útil e auditável: pacote do host por família, leituras simples de sistema/rede, arquivos básicos, extração e compactação local simples, com handoff explícito quando o pedido já pertence ao domínio da Aurora.

A linha 1.x encerrada canonicamente continua a mesma; a `v1.9.9` reorganiza a leitura pública sem reabrir esse contrato.

## O que a linha 1.x faz

- pacote do host: `procurar`, `instalar` e `remover`
- sistema e rede: status, CPU, memória, IP, ping e velocidade da internet
- arquivos: criar, copiar, mover, renomear e remover
- extração e compactação local simples
- leitura técnica e auditável com `aury dev <frase>`

## Contrato público mínimo

- `aury ajuda` e `ay ajuda` renderizam `resources/help.txt` com a `VERSION` da base ativa.
- `aury --version` e `ay --version` imprimem `💜 Aury <VERSION>` a partir da mesma base ativa.
- a camada curta de saída usa `✅ | 💜`, `❌ | 💜` e `ℹ️ | 💜`.
- a forma curta canônica continua sendo `Pronto, eu ...`, `Não consegui ...` e `Bloqueado ...`.
- `aury dev <frase>` continua sendo o relatório canônico da linha `1.x`.
- `aury dev` sem frase continua apenas como verificação local curta do adaptador Fish, em uso secundário nesta linha.
- `procurar`, `instalar` e `remover` continuam significando **pacote do host por família/host**, não software do usuário, app store, múltiplas rotas ou política pública de origem.
- `atualizar` e `otimizar` continuam como **manutenção do host**: locais em Arch/derivadas mutáveis, fora do recorte equivalente em Debian/Fedora/OpenSUSE e bloqueados por política em Atomic/imutáveis.

## Exemplos rápidos

```fish
aury instalar firefox
ay procurar steam
aury mostrar cpu
aury ver cpu e memória
aury criar arquivo teste.txt
aury compactar pasta projetos/ para projetos.tar.gz
aury dev "instalar firefox"
```

## Instalação

```fish
git clone https://github.com/el-abni/aury.git
cd aury
./install.sh
```

O fluxo público instala:

- `~/.config/fish/functions/aury.fish`
- `~/.config/fish/functions/ay.fish`
- `~/.local/share/aury/python/`
- `~/.local/share/aury/resources/`
- `~/.local/share/aury/VERSION`
- `~/.local/share/aury/LICENSE.md`

A instalação pública assume **Fish** e **python3** disponíveis no host.

## Uso

```fish
aury ajuda
ay ajuda
aury --version
aury dev "ver cpu e memória"
```

No checkout local, `source bin/aury.fish` usa o próprio root do repositório como base ativa. Na instalação, a base ativa passa a ser `~/.local/share/aury`.

## Limites honestos

- a `v1.9.9` encerra a compatibilidade Linux da linha `1.x` sem abrir backend, família, operação ou host novo
- o runtime Python atual cobre `help`, `version`, `dev <frase>`, algumas leituras simples de sistema/rede, `criar arquivo`, `criar pasta` e a política de pacote por host Linux; o restante continua voltando ao adaptador Fish
- a linha não promete paridade simétrica entre famílias Linux nem manutenção do host multi-distro
- a linha não abre software do usuário, app store, múltiplas rotas nem política pública de origem
- Atomic, Universal Blue, `opensuse-microos`, `microos` e equivalentes continuam fora por política de host
- `aury velocidade da internet` depende de `librespeed-cli` e `python3` disponíveis no ambiente
- a compactação local simples continua curta: um único arquivo ou uma única pasta, saída explícita e apenas `.zip` ou `.tar.gz`

## Estado público da v1.9.9

- a linha 1.6.x permanece como referência histórica já entregue e encerrada da base híbrida pública anterior
- a `v1.9.0` fechou a base híbrida contida; a `v1.9.1` até a `v1.9.8` fecharam a compatibilidade Linux host-centric; a `v1.9.9` só fecha organização pública, help curto e release hygiene sobre essa mesma superfície pública
- `aury dev <frase>` continua auditável, com fronteira explícita entre núcleo Python, adaptador Fish, política de host e fallback honesto
- `criar arquivo` e `criar pasta` permanecem como micro-recorte operacional já sustentado no runtime Python
- a compactação local simples herdada da `v1.7.0` continua curta por decisão de produto, não por esquecimento
- a matriz final permanece congelada: **suportado agora** em Arch, Debian/Ubuntu e Fedora mutável; **suportado contido** em OpenSUSE mutável; bloco **bloqueado por política** em Atomic, Universal Blue, `opensuse-microos` e `microos`
- `flatpak` e `rpm-ostree` seguem apenas como ferramentas observadas fora do contrato ativo
- o handoff final continua explícito: software do usuário, múltiplas origens, política de origem/source/trust e suporte operacional real a hosts imutáveis pertencem à Aurora, não à Aury `1.x`

## Leitura do checkout canônico

- a única raiz viva é o checkout Git de topo; `./aury/` permanece apenas como artefato histórico/aninhado
- o entrypoint público continua em `bin/aury.fish`
- o bridge Python vivo da borda híbrida fica em `python/aury/fish_bridge.py`
- `python/aury/cli.py` continua apenas como shim de compatibilidade para imports históricos

## Workflow curto

```bash
bash tests/preflight_canonico.sh
bash tests/worktree_gate_minimo.sh
bash tests/release_gate_minimo.sh
```

- `preflight_canonico.sh` é a checagem curta da rodada e não inspeciona a stage pública
- `worktree_gate_minimo.sh` fecha a **worktree hygiene** antes de qualquer staging público
- `release_gate_minimo.sh` fecha a **release hygiene** da stage pública explícita
- falha por **stage vazia** no gate final não indica regressão funcional; indica apenas que a rodada ainda não entrou no degrau final
- quando a seleção staged precisar ser validada sem tocar na stage real do usuário, a prática canônica continua sendo usar `GIT_INDEX_FILE`

## Documentação

- [Compatibilidade](docs/COMPATIBILITY.md): contrato host-centric, matriz final, manutenção do host e handoff para a Aurora
- [Workflow](docs/WORKFLOW.md): ladder mínima, worktree hygiene, release hygiene e uso de `GIT_INDEX_FILE`
- [Arquitetura](docs/ARCHITECTURE.md): ownership, entrypoint vivo e fronteira Fish/Python
- [Base de testes](tests/README.md): audits, smokes, gates e papel executável da pasta `tests/`
- [Changelog](CHANGELOG.md): histórico das releases públicas e shape atual da `v1.9.9`

Ordem de leitura pública: `README.md` -> `docs/COMPATIBILITY.md` -> `docs/WORKFLOW.md` -> `docs/ARCHITECTURE.md` -> `tests/README.md` -> `CHANGELOG.md`.

## Licença

Este projeto é distribuído sob a licença **MIT**.
