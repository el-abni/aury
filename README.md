# 💜 Aury

![version](https://img.shields.io/badge/version-v1.9.9-purple)
![shell](https://img.shields.io/badge/shell-fish-blue)
![platform](https://img.shields.io/badge/platform-Linux-orange)
![license](https://img.shields.io/badge/license-MIT-green)

**Aury** é uma assistente de terminal para **Linux** com linha pública **host-centric** e superfície deliberadamente pequena. Hoje ela continua híbrida: o entrypoint público segue em Fish, e o runtime Python rastreado já sustenta `help`, `version`, `aury dev <frase>` e as rotas normais explicitamente migradas.

## O que é

A Aury recebe pedidos de terminal em português, tenta enquadrar a ação com segurança e então executa, bloqueia ou volta para o adaptador Fish de forma explícita. O foco público da linha `1.x` é utilidade local pequena: pacote do host, leituras simples de sistema/rede, arquivos básicos, extração e compactação local simples.

A linha 1.x encerrada canonicamente mantém esse recorte. A `v1.9.9` não abre backend, família Linux ou domínio operacional novo.

## Uso rápido

```fish
aury ajuda
ay ajuda
aury --version
aury dev "instalar firefox"
```

`ay` é o alias curto de `aury`. A saída pública curta usa `✅ | 💜`, `❌ | 💜` e `ℹ️ | 💜`, com mensagens práticas como `Pronto, eu ...`, `Não consegui ...` e `Bloqueado ...`.

## Exemplos

Pacotes do host:

```fish
aury instalar firefox
ay procurar steam
aury remover vlc
```

Sistema e rede:

```fish
aury atualizar sistema
aury otimizar sistema
aury mostrar cpu
aury ver cpu e memória
aury testar internet
aury velocidade da internet
```

Arquivos:

```fish
aury criar arquivo teste.txt
aury criar pasta Relatorios em Downloads
aury copie a pasta Aury que fica em Documentos para Downloads
aury mova o arquivo teste.txt que fica em Documentos para Downloads
aury renomeie o arquivo teste.txt que fica em Downloads para teste-final.txt
```

Extração, compactação e leitura técnica:

```fish
aury extraia pacote.tar.gz para extracao
aury compactar pasta projetos/ para projetos.tar.gz
aury dev "instalar firefox"
aury dev "copie a pasta Aury que fica em Documentos para Downloads"
```

## Linguagem natural

A Aury aceita algumas frases naturais conservadoras, principalmente quando a ação e o alvo estão claros. Ela não promete entender qualquer frase.

Use `aury dev <frase>` quando quiser uma leitura técnica antes de confiar numa frase maior. Esse relatório mostra o enquadramento da ação e se a rota fica no runtime Python, volta para o adaptador Fish ou sai do recorte atual.

`aury dev` sem frase é só uma verificação local curta do adaptador Fish, em uso secundário nesta linha.

## Recorte da linha 1.x

- `procurar`, `instalar` e `remover` significam **pacote do host por família/host**.
- `atualizar` e `otimizar` pertencem à manutenção local do host no recorte sustentado.
- sistema e rede cobrem leituras simples como CPU, memória, IP, ping e velocidade da internet.
- arquivos cobrem criação, cópia, movimento, renomeação e remoção nos casos seguros já sustentados.
- extração e compactação continuam locais e simples.

Limites honestos:

- a linha não cobre software do usuário, app store, múltiplas rotas, múltiplas fontes nem política pública de origem;
- a linha não promete flatpak, rpm-ostree, AUR, hosts imutáveis ou equivalência multi-distro;
- `aury velocidade da internet` depende de `librespeed-cli` e `python3` disponíveis no ambiente;
- frases ambíguas ou fora do recorte devem falhar, bloquear ou voltar para fallback honesto.

Quando o pedido já envolve software do usuário, múltiplas origens, política de origem/source/trust, suporte real a hosts imutáveis ou rotas mais altas de decisão, o domínio pertence à Aurora, não à Aury 1.x.

## Instalação

```fish
git clone https://github.com/el-abni/aury.git
cd aury
./install.sh
```

A instalação pública assume **Fish** e **python3** disponíveis no host. Depois de instalar, use `aury ajuda` para ver a superfície operacional curta.

## Mais detalhes

- [Compatibilidade](docs/COMPATIBILITY.md): contrato host-centric, matriz final, manutenção do host e handoff para a Aurora.
- [Workflow](docs/WORKFLOW.md): gates, worktree hygiene e release hygiene.
- [Arquitetura](docs/ARCHITECTURE.md): fronteira Fish/Python, ownership e base instalada.
- [Base de testes](tests/README.md): audits, smokes e gates públicos.
- [Changelog](CHANGELOG.md): histórico das releases públicas.

Ordem de leitura pública: `README.md` -> `docs/COMPATIBILITY.md` -> `docs/WORKFLOW.md` -> `docs/ARCHITECTURE.md` -> `tests/README.md` -> `CHANGELOG.md`.

## Licença

Este projeto é distribuído sob a licença **MIT**.
