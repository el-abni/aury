# 💜 Aury

![version](https://img.shields.io/badge/version-v1.9.8-purple)
![shell](https://img.shields.io/badge/shell-fish-blue)
![platform](https://img.shields.io/badge/platform-Linux-orange)
![license](https://img.shields.io/badge/license-MIT-green)

**Aury** é uma assistente de terminal para **Linux**, com foco explícito da linha 1.x em **Arch**, **Debian/Ubuntu**, **Fedora mutável** e **OpenSUSE mutável** no recorte contido de pacote do host.

Ela permite executar tarefas do sistema usando **linguagem natural**, traduzindo frases humanas em ações reais no terminal. A proposta do projeto é reduzir fricção, acelerar tarefas comuns e tornar o uso do terminal mais natural sem perder o poder das ferramentas tradicionais.

---

> Estado público real da **v1.9.8**: a linha **1.x** encerra canonicamente a compatibilidade Linux da Aury. `procurar`, `instalar` e `remover` significam **pacote do host por família/host**, não software do usuário, app store, múltiplas rotas nem política de origem. A matriz final fica congelada assim: Arch, Debian/Ubuntu e Fedora mutável seguem como suporte **agora**; OpenSUSE mutável termina como suporte **contido**; Atomic, Universal Blue, `opensuse-microos`, `microos` e equivalentes continuam **bloqueados por política**. `flatpak` e `rpm-ostree` podem ser observados no ambiente, mas ficam fora do contrato ativo e não viram rota operacional nesta linha. Em manutenção do host, `atualizar` e `otimizar` continuam locais em Arch/derivadas mutáveis, ficam fora do recorte equivalente em Debian/Fedora/OpenSUSE e permanecem bloqueados por política em Atomic/imutáveis. O handoff também fica explícito: software do usuário, múltiplas origens, política de origem/source/trust e suporte operacional real a hosts imutáveis pertencem à Aurora, não à Aury 1.x. O gate final mínimo canônico da linha 1.x continua sendo `bash tests/release_gate_minimo.sh`.

## O que é a Aury

Aury funciona como uma camada de interpretação entre o usuário e o sistema.

Em vez de depender apenas de comandos tradicionais, você pode escrever o que quer fazer de um jeito mais humano, por exemplo:

```fish
aury quero instalar obs studio
aury ver cpu e memória
aury atualiza e otimiza
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
- perfil mínimo de host Linux para política de pacote por família
- micro-recorte operacional em Python para `criar arquivo` e `criar pasta`
- medição explícita de velocidade da internet via `librespeed-cli`

---

## Instalação

A instalação pública atual da v1.9.8 usa o script do próprio repositório:

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
💜 Aury v1.9.8
```

A Aury entende tanto comandos diretos quanto frases mais naturais, como:

```fish
aury instalar firefox
ay instalar firefox
aury pode instalar o firefox
aury Aury, instala o obs studio.
aury ver cpu e memória
aury atualiza e otimiza
```

Para inspecionar a leitura atual sem executar a ação:

```fish
aury dev ver cpu e memória
aury dev copiar arquivo teste.txt para backup.txt
```

## Contrato público mínimo da v1.9.8

- `aury ajuda` e `ay ajuda` renderizam `resources/help.txt` usando a `VERSION` da base ativa.
- `aury --version` e `ay --version` imprimem `💜 Aury <VERSION>` a partir da mesma base ativa.
- `aury dev <frase>` usa o núcleo Python e expõe plano da sequência, leitura por ação, plano de execução e decisão de sequência de forma mais auditável.
- na v1.9.8, `aury dev <frase>` continua sendo o relatório canônico da linha 1.x sem prometer paridade total com toda formulação histórica do legado.
- na v1.9.8, `criar arquivo` e `criar pasta` seguem com rota Python explícita no modo normal, inclusive quando a leitura `dev` fecha esse mesmo micro-recorte como suportado.
- na v1.9.8, a frente curta local de `aury dev` fechada na v1.9.2 permanece incorporada, sem abrir nova rodada ampla de hardening de arquivos.
- na v1.9.8, `procurar`, `instalar` e `remover` significam explicitamente **pacote do host por família/host**.
- na v1.9.8, esse trio não significa software do usuário, app store, múltiplas rotas, política de origem nem instalação cross-source.
- na v1.9.8, a taxonomia pública final de compatibilidade de pacote fica explícita: **suportado agora**, **suportado contido**, **bloqueado por política** e **impossibilidade operacional**.
- na v1.9.8, Arch, Debian/Ubuntu e Fedora mutável ficam como **Tier 1 canônico** e suporte agora; OpenSUSE mutável termina como **Tier 2 útil contido**; Atomic, Universal Blue, `opensuse-microos`, `microos` e equivalentes imutáveis continuam bloqueados por política de host.
- na v1.9.8, `flatpak` e `rpm-ostree` podem aparecer apenas como ferramentas observadas no ambiente, fora do contrato ativo; eles não viram instalação operacional nesta linha.
- na v1.9.8, `atualizar` e `otimizar` aparecem explicitamente como **manutenção do host**: continuam locais em Arch/derivadas mutáveis no adaptador Fish, ficam fora do recorte equivalente em Debian/Fedora/OpenSUSE e seguem bloqueados por política em Atomic/imutáveis.
- na v1.9.8, backend ausente, ferramenta auxiliar de confirmação ausente e erro operacional continuam explícitos como limitação operacional; pacote não volta a improvisar fallback localista fora desse contrato.
- na v1.9.8, a compatibilidade Linux da Aury 1.x fica declaradamente encerrada, sem promessa implícita de expansão dentro da própria Aury.
- `aury dev` sem frase fica mantido como verificação local curta e utilitário secundário do adaptador Fish; ele não substitui o relatório canônico da linha 1.x.
- `bin/aury.fish` é o ponto de entrada público: ele tenta o runtime Python primeiro e volta ao Fish quando a ação não fecha numa rota Python explícita desta linha.
- o gate final mínimo canônico da linha 1.x é `bash tests/release_gate_minimo.sh`.
- a compactação local simples herdada da v1.7.0 continua cobrindo um único arquivo ou uma única pasta, com saída explícita e apenas `.zip` ou `.tar.gz`.
- Em desenvolvimento, ao fazer `source bin/aury.fish`, a base ativa é o próprio root do repositório. Na instalação, a base ativa é `~/.local/share/aury`.

## Matriz final de compatibilidade da v1.9.8

- Contrato final: `procurar`, `instalar` e `remover` significam pacote do host por família/host.
- Suportado agora e Tier 1 canônico de pacote: Arch e derivadas mutáveis, Debian/Ubuntu e derivadas mutáveis, Fedora e derivadas mutáveis.
- Tier 2 útil contido: OpenSUSE mutável entra com `procurar`, `instalar` e `remover` pacote do host via `zypper`, sem promessa de paridade total com o Tier 1.
- Bloqueado por política: Atomic Fedora, Universal Blue, `opensuse-microos`, `microos` e perfis equivalentes imutáveis permanecem fora para pacote do host.
- Observado, mas fora do contrato ativo: `flatpak` e `rpm-ostree` podem existir no ambiente, mas não entram como rota operacional pública nesta linha.
- Impossibilidade operacional: backend ausente, ferramenta auxiliar de confirmação ausente e erro operacional em host já suportado continuam saindo como limitação operacional honesta, não como política de host.
- Manutenção do host: `atualizar` e `otimizar` continuam locais em Arch/derivadas mutáveis, ficam fora do recorte equivalente em Debian/Fedora/OpenSUSE e seguem bloqueados por política em Atomic/imutáveis.
- A v1.9.8 não promete tradução de nomes de pacote, paridade total entre famílias, software do usuário, app store nem suporte cross-distro amplo.

## Handoff para a Aurora

- A Aury 1.x encerra o contrato de host, o contrato de pacote do host, o contrato de manutenção do host, a fronteira com hosts imutáveis e a taxonomia pública estável da compatibilidade Linux.
- Software do usuário, múltiplas origens, política de origem/source/trust, suporte operacional real a hosts imutáveis e rotas mais altas de decisão/mediação já pertencem à Aurora.
- A v1.9.8 não planeja a Aurora nem abre ponte operacional nova; ela apenas deixa o handoff limpo e auditável.

## Limites honestos

- pedidos fora do recorte atual, como `abrir arquivo`, continuam em fallback honesto
- o runtime Python atual cobre `help`, `version`, `dev <frase>`, algumas leituras simples de rede/sistema, o micro-recorte de `criar arquivo` / `criar pasta` e a política de pacote por host Linux; o restante continua voltando ao adaptador Fish
- `aury dev` sem frase fica restrito à verificação local curta do adaptador Fish e não deve ser tratado como relatório canônico amplo
- a v1.9.8 encerra a compatibilidade Linux da linha 1.x sem abrir backend, família, operação ou host novo
- a v1.9.8 não promete compatibilidade simétrica entre famílias Linux nem update/optimize multi-distro
- a v1.9.8 não trata Atomic como host mutável normal de pacote
- a v1.9.8 não abre software do usuário, app store, múltiplas rotas nem política pública de origem de software
- a v1.9.8 não infere representacionalmente `mover arquivo ... para destino nu` quando a leitura correta depende do estado do filesystem
- a v1.9.8 não reabre dentro da Aury o que já foi entregue como handoff para a Aurora
- `aury velocidade da internet` depende de `librespeed-cli` e `python3` disponíveis no ambiente
- a compactação herdada da v1.7.0 não cobre lote, overwrite automático, nome derivado automaticamente nem formatos extras

---

## Estado público da v1.9.8

- a linha 1.6.x já foi fechada e permanece como referência histórica já entregue da base híbrida pública anterior
- a v1.9.0 fechou a base híbrida pública contida; a v1.9.1 abriu a primeira release pública de compatibilidade Linux; a v1.9.2 fechou o hardening representacional curto de `aury dev`; a v1.9.3 abriu OpenSUSE mutável no pacote do host; a v1.9.4 consolidou esse domínio; a v1.9.5 endureceu a fronteira de compatibilidade dos hosts imutáveis; a v1.9.6 enquadrou honestamente `atualizar` e `otimizar` como manutenção do host; a v1.9.7 congelou explicitamente o contrato final de pacote do host; a v1.9.8 fecha canonicamente a compatibilidade Linux da Aury 1.x
- `aury dev <frase>` continua com linguagem pública auditável: rotas sustentadas pelo núcleo Python, atendidas pelo adaptador Fish, bloqueadas honestamente por política de host ou fora do recorte do runtime Python
- `aury dev` sem frase permanece apenas como verificação local curta e secundária do adaptador Fish
- `criar arquivo` e `criar pasta` permanecem como o micro-recorte operacional já fechado no runtime Python
- a frente curta local de `aury dev` fica encerrada com renomeação localizada, `copiar -> mover`, `copiar -> renomear` e `mover -> renomear` nos recortes explícitos seguros
- a política de pacote parte de um perfil mínimo de host Linux: família, mutabilidade, backends ativos do contrato e ferramentas observadas fora do contrato
- `atualizar` e `otimizar` deixam de soar como compatibilidade Linux portátil: passam a aparecer como manutenção do host, com rota local em Arch/derivadas, sem equivalência prometida em Debian/Fedora/OpenSUSE e com bloqueio por política em Atomic/imutáveis
- a fronteira híbrida segue explícita: Fish continua como entrada pública e camada de compatibilidade; Python sustenta `help`, `version`, `dev <frase>` e o subconjunto explícito de rotas normais já sustentadas diretamente
- o domínio de pacote permanece endurecido: busca sem resultado, backend ausente, ferramenta auxiliar de confirmação ausente, erro operacional, no-op e confirmação de estado saem com superfície pública honesta; o Fish não volta a concentrar política de pacote
- `flatpak` e `rpm-ostree` deixam de soar como suporte parcial implícito: quando observados, aparecem apenas como ferramentas fora do contrato ativo
- a matriz final da linha fica congelada como suporte agora em Arch, Debian/Ubuntu e Fedora mutável; suporte contido em OpenSUSE mutável; bloqueio por política em Atomic, Universal Blue, `opensuse-microos` e `microos`
- o handoff final fica explícito: software do usuário, múltiplas origens, política de origem/source/trust e suporte operacional real a hosts imutáveis pertencem à Aurora, não à Aury 1.x
- a inferência de `mover arquivo ... para destino nu`, quando dependente do filesystem, permanece conscientemente fora da v1.9.8 por honestidade representacional
- o workflow canônico de auditoria pública mínima da linha 1.x fica explicitado como `bash tests/release_gate_minimo.sh`

## Linha 1.x encerrada

- a v1.9.0 fechou a base híbrida pública contida da linha 1.x
- a v1.9.1 abriu compatibilidade Linux inicial no domínio de pacote
- a v1.9.2 endureceu `aury dev` no recorte curto já auditado
- a v1.9.3 abriu OpenSUSE mutável no pacote do host
- a v1.9.4 consolidou esse domínio por família/host
- a v1.9.5 endureceu a fronteira entre famílias mutáveis abertas e hosts imutáveis conscientemente bloqueados, sem abrir compatibilidade ampla nem nova frente geral de produto
- a v1.9.6 enquadra `atualizar` e `otimizar` como manutenção do host, sem abrir equivalência multi-distro
- a v1.9.7 congela explicitamente `procurar`, `instalar` e `remover` como contrato final de pacote do host por família/host
- a v1.9.8 fecha a matriz final, o gate final e o handoff canônico para a Aurora
- a v2.0 da Aury é a Aurora; a linha 1.x pode ser considerada encerrada

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
