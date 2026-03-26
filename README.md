# 💜 Aury

![version](https://img.shields.io/badge/version-v1.9.2-purple)
![shell](https://img.shields.io/badge/shell-fish-blue)
![platform](https://img.shields.io/badge/platform-Linux-orange)
![license](https://img.shields.io/badge/license-MIT-green)

**Aury** é uma assistente de terminal para **Linux**, com foco inicial em **Arch**, **Debian/Ubuntu** e **Fedora mutável**.

Ela permite executar tarefas do sistema usando **linguagem natural**, traduzindo frases humanas em ações reais no terminal. A proposta do projeto é reduzir fricção, acelerar tarefas comuns e tornar o uso do terminal mais natural sem perder o poder das ferramentas tradicionais.

---

> Estado público real da **v1.9.2**: a linha **1.x** continua incremental como base híbrida deliberadamente contida. Esta release não abre nova frente de produto; ela fecha o hardening representacional curto de `aury dev` no domínio local já sustentado pelo legado, cobrindo renomeação localizada, `copiar -> mover` com anáfora local, `copiar -> renomear` com artigo explícito e anáfora local, e `mover -> renomear` com destino explícito seguro. A compatibilidade Linux inicial de pacote aberta na **v1.9.1** permanece como base pública vigente. A inferência representacional de `mover arquivo ... para destino nu`, quando a leitura correta depende do estado do filesystem, continua conscientemente fora desta release. O gate final mínimo canônico da linha 1.x continua sendo `bash tests/release_gate_minimo.sh`.

## O que é a Aury

Aury funciona como uma camada de interpretação entre o usuário e o sistema.

Em vez de depender apenas de comandos tradicionais, você pode escrever o que quer fazer de um jeito mais humano, por exemplo:

```fish
aury quero instalar obs studio
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
aury mover arquivo teste.txt para pasta/teste.txt
aury extraia teste.tar para a pasta que fica em /usr/steam
```

A ideia não é substituir o terminal, mas tornar o uso dele mais confortável, direto e acessível.

---

## Exemplos rápidos

### Pacotes

```fish
aury instalar firefox
aury instala firefox
aury baixa o vlc
aury quero instalar obs studio
aury remover vlc
aury procurar steam
```

### Sistema

```fish
aury atualizar sistema
aury otimizar sistema
aury atualiza e otimiza
aury mostrar cpu
aury checar memória
aury mostrar o status do sistema
aury ver cpu e memória
```

### Rede

```fish
aury ver ip
aury testar internet
aury velocidade da internet
aury ping google.com
```

### Arquivos

```fish
aury criar arquivo teste.txt
aury cria um arquivo teste.txt
aury criar pasta projetos
aury copiar arquivo teste.txt para backup.txt
aury mover arquivo teste.txt para pasta/teste.txt
aury renomear arquivo teste.txt para novo.txt
aury remover o arquivo teste.txt
```

### Extração

```fish
aury extrair teste.zip
aury descompacte backup.tar.gz
aury extraia teste.tar para a pasta que fica em /usr/steam
```

### Compactação

```fish
aury compactar arquivo teste.txt para teste.zip
aury compactar pasta projetos/ para projetos.tar.gz
```

---

## Funcionalidades

A versão atual da **💜 Aury** já oferece:

- interpretação de frases mais naturais
- suporte a múltiplas intenções no mesmo comando
- suporte a múltiplos alvos compartilhados
- comandos de pacote
- comandos de sistema
- comandos de rede
- comandos de arquivo
- extração segura de arquivos `.zip`, `.7z`, `.tar`, `.tar.gz` e `.tgz`
- compactação local simples de um único arquivo ou uma única pasta, com saída explícita em `.zip` ou `.tar.gz`
- conectores como `e`, `para`, `pra` e `em`
- suporte a vocativo como `Aury,`
- suporte a pontuação estilo chat
- corretor conservador com proteção de tokens sensíveis
- localização conversacional em fluxos de arquivo e extração
- anáforas locais seguras com `ele`, `ela` e `isso`
- fallback honesto com dica de ajuda quando o pedido sai do recorte atual
- confirmação destrutiva explícita para remoção e bloqueio de alvo anafórico inseguro
- ambiguidade pública de alvo/destino em vez de execução silenciosa
- observabilidade mais contratual com `aury dev <frase>`
- perfil mínimo de host Linux para política inicial de pacote por família
- micro-recorte operacional em Python para `criar arquivo` e `criar pasta`
- medição explícita de velocidade da internet via `librespeed-cli`

---

## Instalação

A instalação pública atual da v1.9.2 usa o script do próprio repositório:

```fish
git clone https://github.com/el-abni/aury.git
cd aury
./install.sh
```

O script instala a superfície pública em:

- `~/.config/fish/functions/aury.fish`
- `~/.config/fish/functions/ay.fish`
- `~/.local/share/aury/python/`
- `~/.local/share/aury/resources/`
- `~/.local/share/aury/VERSION`
- `~/.local/share/aury/LICENSE.md`

A instalação pública assume **Fish** e **python3** disponíveis no ambiente.

Depois da instalação, abra um novo shell Fish ou recarregue as funções:

```fish
source ~/.config/fish/functions/aury.fish
source ~/.config/fish/functions/ay.fish
```

A partir daí, `aury` e `ay` passam a usar a base instalada em `~/.local/share/aury`.

---

## Como usar

Para ver os exemplos e comandos disponíveis:

```fish
aury ajuda
ay ajuda
```

No código, a identidade visual da assistente é:

```text
💜 Aury
```

No comando de ajuda, a versão deve aparecer no formato:

```text
💜 Aury v1.9.2
```

A Aury entende tanto comandos diretos quanto frases mais naturais, como:

```fish
aury instalar firefox
ay instalar firefox
aury pode instalar o firefox
aury Aury, instala o obs studio.
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
```

Para inspecionar a leitura atual sem executar a ação:

```fish
aury dev ver cpu e memória
aury dev copiar arquivo teste.txt para backup.txt
```

## Contrato público mínimo da v1.9.2

- `aury ajuda` e `ay ajuda` renderizam `resources/help.txt` usando a `VERSION` da base ativa.
- `aury --version` e `ay --version` imprimem `💜 Aury <VERSION>` a partir da mesma base ativa.
- `aury dev <frase>` usa o núcleo Python e expõe plano da sequência, leitura por ação, plano de execução e decisão de sequência de forma mais auditável.
- na v1.9.2, `aury dev <frase>` continua sendo o relatório canônico da linha 1.x sem prometer paridade total com toda formulação histórica do legado.
- na v1.9.2, `criar arquivo` e `criar pasta` seguem com rota Python explícita no modo normal, inclusive quando a leitura `dev` fecha esse mesmo micro-recorte como suportado.
- na v1.9.2, `aury dev` fecha a frente curta local já sustentada pelo legado com renomeação localizada, `copiar -> mover`, `copiar -> renomear` e `mover -> renomear` nos recortes seguros já auditados.
- na v1.9.2, `procurar`, `instalar` e `remover` no domínio de pacote continuam dependendo do perfil mínimo do host Linux e de um backend explícito por família.
- na v1.9.2, o recorte inicial útil de pacote continua cobrindo Arch e derivadas, Debian/Ubuntu e derivadas, e Fedora mutável; OpenSUSE entra apenas com detecção e bloqueio honesto; Atomic permanece bloqueado com honestidade.
- na v1.9.2, a política canônica de pacote continua no núcleo Python; a entrada pública segue em Fish, mas pacote não volta a improvisar fallback localista fora desse contrato.
- `aury dev` sem frase fica mantido como verificação local curta e utilitário secundário do adaptador Fish; ele não substitui o relatório canônico da linha 1.x.
- `bin/aury.fish` é o ponto de entrada público: ele tenta o runtime Python primeiro e volta ao Fish quando a ação não fecha numa rota Python explícita desta linha.
- o gate final mínimo canônico da linha 1.x é `bash tests/release_gate_minimo.sh`.
- a compactação local simples herdada da v1.7.0 continua cobrindo um único arquivo ou uma única pasta, com saída explícita e apenas `.zip` ou `.tar.gz`.
- Em desenvolvimento, ao fazer `source bin/aury.fish`, a base ativa é o próprio root do repositório. Na instalação, a base ativa é `~/.local/share/aury`.

## Compatibilidade Linux atual na v1.9.2

- Tier 1 inicial de pacote: Arch e derivadas mutáveis, Debian/Ubuntu e derivadas mutáveis, Fedora e derivadas mutáveis.
- Tier 2 contido: OpenSUSE entra só com detecção e bloqueio honesto nesta release.
- Suporte limitado: Atomic Fedora, Universal Blue e perfis equivalentes permanecem bloqueados honestamente para pacote do host.
- O recorte portátil vigente continua em `procurar`, `instalar` e `remover`; `atualizar` e `otimizar` permanecem fora da compatibilidade multi-distro.
- A v1.9.2 não promete tradução de nomes de pacote, paridade total entre famílias nem suporte cross-distro amplo.

## Limites honestos

- pedidos fora do recorte atual, como `abrir arquivo`, continuam em fallback honesto
- o runtime Python atual cobre `help`, `version`, `dev <frase>`, algumas leituras simples de rede/sistema, o micro-recorte de `criar arquivo` / `criar pasta` e a política inicial de pacote por host Linux; o restante continua voltando ao adaptador Fish
- `aury dev` sem frase fica restrito à verificação local curta do adaptador Fish e não deve ser tratado como relatório canônico amplo
- a v1.9.2 não promete compatibilidade simétrica entre famílias Linux nem update/optimize multi-distro
- a v1.9.2 não infere representacionalmente `mover arquivo ... para destino nu` quando a leitura correta depende do estado do filesystem
- `aury velocidade da internet` depende de `librespeed-cli` e `python3` disponíveis no ambiente
- a compactação herdada da v1.7.0 não cobre lote, overwrite automático, nome derivado automaticamente nem formatos extras

---

## Estado da linha 1.6.x

- a linha 1.6.x permanece fechada publicamente como etapa já entregue
- `v1.6.1`: base pública híbrida entre adaptador Fish e núcleo Python
- `v1.6.2`: alinhamento diagnóstico curto extra de `aury dev` com fluxos já sustentados pelo modo normal
- `v1.6.3`: fechamento público da linha 1.6.x, sem ampliar o escopo funcional da Aury

## Estado público da v1.9.2

- a v1.8.0 fechou a etapa de congelamento semântico e endurecimento incremental sem reabrir expansão estrutural
- a v1.9.0 fechou a base híbrida pública contida; a v1.9.1 abriu a primeira release pública de compatibilidade Linux sem reescrever a Aury; a v1.9.2 fecha o hardening representacional curto de `aury dev`
- `aury dev <frase>` continua com linguagem pública auditável: rotas sustentadas pelo núcleo Python, atendidas pelo adaptador Fish, bloqueadas honestamente por política de host ou fora do recorte do runtime Python
- `aury dev` sem frase permanece apenas como verificação local curta e secundária do adaptador Fish
- `criar arquivo` e `criar pasta` permanecem como o micro-recorte operacional já fechado no runtime Python
- a frente curta local de `aury dev` fica encerrada com renomeação localizada, `copiar -> mover`, `copiar -> renomear` e `mover -> renomear` nos recortes explícitos seguros
- a política de pacote agora parte de um perfil mínimo de host Linux: família, mutabilidade e backends centrais detectados
- a fronteira híbrida segue explícita: Fish continua como entrada pública e camada de compatibilidade; Python sustenta `help`, `version`, `dev <frase>` e o subconjunto explícito de rotas normais já sustentadas diretamente
- o domínio de pacote foi endurecido no recorte atual: busca sem resultado, no-op e bloqueios fora do suporte saem com superfície pública honesta; o Fish não volta a concentrar política de pacote
- Arch, Debian/Ubuntu e Fedora mutável entram como Tier 1 inicial de pacote; OpenSUSE fica em Tier 2 apenas com detecção/bloqueio honesto; Atomic continua em suporte limitado com bloqueio honesto
- a inferência de `mover arquivo ... para destino nu`, quando dependente do filesystem, permanece conscientemente fora da v1.9.2 por honestidade representacional
- o workflow canônico de auditoria pública mínima da linha 1.x fica explicitado como `bash tests/release_gate_minimo.sh`

## Continuidade da linha 1.x

- a v1.9.0 fechou a base híbrida pública contida da linha 1.x
- a v1.9.1 abriu compatibilidade Linux inicial no domínio de pacote
- a v1.9.2 continua a mesma linha com hardening representacional curto de `aury dev`, sem abrir nova frente técnica pública
- não existe v2.0 pública da Aury neste momento

---

## Filosofia do projeto

Aury não tenta substituir o terminal tradicional.

Ela existe para:

- reduzir a fricção do uso diário
- acelerar tarefas comuns
- permitir comandos mais humanos
- tornar o terminal mais acessível para quem está começando no Linux

O terminal continua poderoso. Aury apenas adiciona uma camada de conforto e interpretação.

---

## Documentação

A documentação complementar do projeto fica em:

```text
docs/ARCHITECTURE.md
```
Base pública de testes:

- `tests/README.md`

---

## Licença

Este projeto é distribuído sob a licença **MIT**.
