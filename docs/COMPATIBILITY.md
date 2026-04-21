# Compatibilidade da 💜 Aury

Este documento registra o contrato público final sustentado pela **💜 Aury v1.9.9** no repositório canônico atual.
O `README.md` mantém a superfície curta do repositório; este arquivo responde apenas pelo contrato de compatibilidade da linha host-centric atual. Fronteiras e ownership ficam em `docs/ARCHITECTURE.md`; ladder e hygiene de validação ficam em `docs/WORKFLOW.md`.

Na `v1.9.9`, esse contrato não reabre a linha: ele só recebe acabamento final de UX/help/release hygiene sobre o mesmo recorte já fechado na `v1.9.8`.

## Contrato ativo

- `procurar`, `instalar` e `remover` significam **pacote do host por família/host**.
- esse trio não significa software do usuário, app store, múltiplas rotas nem política pública de origem nesta linha.
- `flatpak` e `rpm-ostree` podem ser observados no ambiente, mas ficam fora do contrato ativo.

## Matriz final da linha 1.x

- **suportado agora**: Arch/derivadas mutáveis, Debian/Ubuntu/derivadas mutáveis e Fedora mutável.
- **suportado contido**: OpenSUSE mutável no recorte útil de pacote do host.
- **bloqueado por política**: Atomic, Universal Blue, `opensuse-microos`, `microos` e equivalentes imutáveis.
- **impossibilidade operacional**: backend ausente, sonda auxiliar ausente ou erro operacional continuam distintos de política de host.

## Manutenção do host

- `atualizar` e `otimizar` pertencem à manutenção do host.
- em Arch/derivadas mutáveis, continuam locais no adaptador Fish.
- em Debian/Fedora/OpenSUSE mutáveis, continuam fora do recorte equivalente nesta linha.
- em Atomic/imutáveis, continuam bloqueados por política.

## Handoff para a Aurora

- software do usuário;
- múltiplas origens;
- política de origem/source/trust;
- suporte operacional real a hosts imutáveis;
- rotas mais altas de decisão e mediação.

Esse domínio já pertence à Aurora, não à Aury 1.x.

## Fechamento da linha

A compatibilidade Linux da Aury 1.x se encerra nesta matriz final e permanece encerrada canonicamente na v1.9.9.
O objetivo aqui é manter o recorte honesto, não reabrir a linha com novas superfícies.
