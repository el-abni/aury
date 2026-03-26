# Changelog

Todas as mudanças importantes da **💜 Aury** são documentadas neste arquivo.

A linha pública da **💜 Aury** continua incremental na série **v1.9.x**. Este changelog registra apenas versões lançadas.

---

## v1.9.4

### Consolidado
- fechamento público da **v1.9.4** como consolidação pós-OpenSUSE do domínio de pacote por família/host, sem abrir nova frente geral de compatibilidade
- versão, narrativa, arquitetura, ajuda e metadados passam a refletir a **v1.9.4** como continuação incremental contida da base pública já expandida na **v1.9.3**

### Domínio de pacote por família/host
- a política de pacote fica mais coerente entre detecção do host, classificação de suporte, plano de execução e runtime real nas famílias mutáveis já abertas
- `aury dev` passa a expor OpenSUSE mutável de forma alinhada à narrativa pública como **Tier 2 útil contido**
- backend ausente e ferramenta auxiliar de confirmação ausente passam a sair com superfícies distintas e honestas
- o recorte RPM da linha continua explícito: Fedora mutável e OpenSUSE mutável confirmam estado com `rpm -q` em `instalar` e `remover`

### Compatibilidade e limites
- Arch e derivadas, Debian/Ubuntu e derivadas, e Fedora mutável permanecem como Tier 1 inicial de pacote
- OpenSUSE mutável permanece como ganho útil contido, sem ser descrito como paridade total com o Tier 1
- Atomic, Universal Blue e perfis equivalentes permanecem em suporte limitado com bloqueio honesto de pacote do host
- continuam fora desta release: `update` multi-distro, `optimize` multi-distro, `rpm-ostree`, toolbox, distrobox, tradução de nomes de pacote e suporte cross-distro amplo

---

## v1.9.3

### Consolidado
- fechamento público da **v1.9.3** como retomada contida da saga de compatibilidade Linux, sem abrir nova frente geral de feature
- versão, narrativa, arquitetura, ajuda e metadados passam a refletir a **v1.9.3** como continuidade incremental da base pública já endurecida na **v1.9.2**

### OpenSUSE mutável
- OpenSUSE mutável deixa o bloqueio honesto puro e passa a entrar com execução real contida de pacote do host para `procurar`, `instalar` e `remover`
- `zypper` entra como backend explícito de busca; `sudo + zypper` entra como backend explícito de instalação e remoção
- instalação e remoção em OpenSUSE mutável passam a confirmar estado com `rpm -q`, mantendo a mesma filosofia honesta já usada no recorte RPM desta linha

### Compatibilidade e limites
- Arch e derivadas, Debian/Ubuntu e derivadas, e Fedora mutável permanecem como Tier 1 inicial de pacote
- OpenSUSE mutável entra como recorte útil contido, sem ser descrito como paridade total com as famílias Tier 1
- Atomic, Universal Blue e perfis equivalentes permanecem em suporte limitado com bloqueio honesto de pacote do host
- continuam fora desta release: `update` multi-distro, `optimize` multi-distro, `rpm-ostree`, toolbox, distrobox, tradução de nomes de pacote e suporte cross-distro amplo

---

## v1.9.2

### Consolidado
- fechamento público da **v1.9.2** como hardening representacional incremental do `aury dev`, sem abrir nova frente de produto
- versão, narrativa, arquitetura e metadados passam a refletir a **v1.9.2** como continuação contida da base pública já fechada na **v1.9.1**

### Paridade local curta do `aury dev`
- entra o fechamento curto de renomeação localizada no relatório `dev`
- entra `copiar -> mover` com anáfora local segura
- entra `copiar -> renomear` com artigo explícito e anáfora local
- entra `mover -> renomear` com destino explícito seguro

### Compatibilidade e limites
- a compatibilidade Linux inicial de pacote aberta na **v1.9.1** permanece como base pública vigente desta release
- fica conscientemente fora a inferência representacional de `mover arquivo ... para destino nu` quando a leitura correta depende do estado do filesystem
- não entram frentes adjacentes de auditoria nem expansão nova de produto neste fechamento

---

## v1.9.1

### Consolidado
- fechamento público da **v1.9.1** como primeira release incremental de compatibilidade Linux da linha **1.x**
- versão, narrativa, arquitetura, ajuda e metadados passam a refletir a **v1.9.1** como continuidade incremental da base híbrida pública, sem sugerir encerramento na **v1.9.0**

### Perfil mínimo de host
- entra um contrato mínimo de host Linux no núcleo Python com família, mutabilidade e backends centrais de pacote detectados
- `aury dev <frase>` passa a expor esse perfil quando a ação entra no domínio de pacote

### Pacote por família Linux
- `procurar`, `instalar` e `remover` deixam de depender do hardcode puro de `pacman` e passam a usar política explícita por família Linux
- Arch e derivadas, Debian/Ubuntu e derivadas, e Fedora mutável entram como Tier 1 inicial
- OpenSUSE entra apenas com detecção e bloqueio honesto nesta fase
- Atomic permanece em suporte limitado com bloqueio honesto de pacote do host
- a entrada pública continua em Fish, mas a política canônica de pacote deixa de voltar a fallback localista fora do runtime Python

### Endurecimento operacional
- busca sem resultado, backend ausente, host fora do recorte e host Atomic passam a sair com superfície pública mais previsível e honesta
- `instalar` e `remover` passam a verificar estado antes de agir e a confirmar o resultado quando o backend Tier 1 permite isso
- `aury dev <frase>` permanece alinhado ao comportamento real desse domínio, sem prometer compatibilidade total entre famílias

### Compatibilidade e limites
- `atualizar` e `otimizar` continuam fora da compatibilidade multi-distro nesta release
- não entra toolbox, distrobox, rpm-ostree, tradução de nomes de pacote nem paridade total entre famílias

---

## v1.9.0

### Consolidado
- fechamento público da base híbrida contida da linha **1.x** da **💜 Aury** no repositório canônico
- versão, narrativa, arquitetura e metadados passam a refletir a **v1.9.0** como fechamento deliberado dessa base antes da abertura incremental da v1.9.1

### Linguagem pública e enquadramento final
- `aury dev <frase>` deixa de insinuar roadmap implícito de migração e passa a expor, no presente, quando uma rota é sustentada pelo núcleo Python, atendida pelo adaptador Fish ou fica fora do recorte do runtime Python
- `aury dev` sem frase permanece disponível apenas como verificação local curta e utilitário secundário do adaptador Fish

### Gate e fechamento estrutural
- `tests/release_gate_minimo.sh` fica explicitado como gate final mínimo canônico da linha 1.x
- `README.md`, `docs/ARCHITECTURE.md` e `tests/README.md` passam a contar a mesma história final da superfície pública já endurecida

### Compatibilidade e limites
- a entrada pública continua em Fish e o núcleo Python permanece rastreando `help`, `version`, `aury dev <frase>` e o subconjunto explícito de rotas normais já sustentadas diretamente
- o restante do híbrido permanece no adaptador Fish por decisão final da linha 1.x, sem abrir nova migração estrutural nesta release

---

## v1.8.0

### Consolidado
- fechamento público da **💜 Aury v1.8.0** como versão de congelamento semântico e endurecimento incremental
- narrativa pública, arquitetura e metadados passam a refletir o estado real alcançado pela base após as Fases 2 e 3

### Observabilidade e regressão
- `aury dev <frase>` fica mais contratual: plano da sequência, decisão por ação, motivos de fallback/bloqueio e lacunas explícitas ficam mais auditáveis
- a regressão pública mínima é fortalecida para blindar melhor paridade, superfícies de saída e o contrato observável da transição Fish → Python

### Micro-migração madura
- `criar arquivo` e `criar pasta` deixam de ser apenas leitura diagnóstica consistente e passam a executar no runtime Python
- a entrada pública continua em Fish e o restante do híbrido segue explícito no adaptador

### Compatibilidade e limites
- compactação local simples permanece no Fish, com o mesmo recorte curto herdado da v1.7.0
- extração, fluxos destrutivos e o restante do domínio de arquivos não ganham migração ampla nesta release

---

## v1.7.0

### Consolidado
- fechamento público canônico da **💜 Aury v1.7.0** no repositório principal
- abertura operacional e fechamento estrutural da superfície pública agora contam a mesma história da base ativa

### Melhorado
- `VERSION`, `README.md`, `resources/help.txt`, `docs/ARCHITECTURE.md` e os scripts públicos de instalação passam a refletir a versão pública `v1.7.0`
- coerência mínima de workflow, auditoria pública, paridade de `aury dev` e superfícies de saída fica registrada como parte do fechamento estrutural da release

### Compactação local simples
- entra como o único corte funcional novo da v1.7.0
- cobre um único arquivo ou uma única pasta, com saída explícita obrigatória
- aceita apenas `.zip` e `.tar.gz`, inferidos pelo sufixo da saída

### Compatibilidade e limites
- a entrada pública continua em Fish, com `help`, `version`, `dev <frase>` e as rotas Python já suportadas no núcleo Python
- a execução real da compactação continua no adaptador Fish, sem lote, overwrite automático, formatos extras ou integração com rede

---

## v1.6.3

### Consolidado
- fechamento público final da linha 1.6.x no repositório canônico

### Documentação e apresentação pública
- `README.md`, instalação pública e documentação de apoio passam a refletir `# 💜 Aury`, a versão pública `v1.6.3` e o fluxo real atual
- o estado público da linha `v1.6.1` / `v1.6.2` / `v1.6.3` fica registrado de forma explícita, sem sugerir `v1.6` como etapa futura

### Compatibilidade e limites
- sem ampliação de escopo funcional da Aury neste bloco
- o contrato operacional segue o recorte já entregue pela linha 1.6.x

## v1.6.2

### Consolidado
- fechamento local curto de alinhamento entre `aury dev` e o que o modo normal já sustenta no adaptador Fish

### Melhorado
- `aury dev <frase>` passa a fechar também leituras simples de instalar pacote, ping com host explícito, velocidade da rede, criar arquivo/pasta, copiar/mover/renomear arquivo e remoções explícitas já sustentadas pelo modo normal
- remoção destrutiva anafórica no diagnóstico passa a distinguir com mais precisão falta de antecedente seguro, contexto anterior insuficiente/incompatível e lacuna real de alinhamento com o runtime legado atual
- o relatório `dev` passa a expor `referência local` e `lacunas` de forma mais auditável

### Testes e regressão
- `tests/python_core_smoke.py` amplia a cobertura do alinhamento curto da v1.6.2, inclusive nos casos destrutivos prudentes

### Compatibilidade e limites
- a v1.6.2 não amplia o runtime destrutivo nem força migração nova de execução
- o objetivo desta versão é reduzir a distância entre diagnóstico e execução real, mantendo a prudência do legado

## v1.6.1

### Consolidado
- núcleo Python canonizado em `python/aury`
- `help` e `version` passam a refletir a mesma base ativa via `resources/help.txt` e `VERSION`
- `bin/aury.fish` assume explicitamente o papel de adaptador público entre Fish e o núcleo Python

### Melhorado
- `aury dev <frase>` passa a expor o relatório canônico do núcleo Python para a transição Fish → Python
- rotas explícitas do runtime Python passam a sustentar busca de pacote, leituras simples de rede, leituras simples de sistema e execução multi-ação quando toda a sequência já tem rota suportada
- `install.sh` e `uninstall.sh` passam a assumir a base instalada em `~/.local/share/aury`
- `README.md`, `docs/ARCHITECTURE.md` e `tests/README.md` deixam de descrever a Aury como se a linha pública ainda fosse exclusivamente Fish

### Testes e regressão
- `tests/python_core_smoke.py` passa a proteger o núcleo Python já rastreado
- `tests/public_ux_smoke.sh` absorve o contrato público mínimo de `help`, `version`, `ay` e do adaptador Fish

### Compatibilidade e limites
- a entrada pública continua em Fish, com fallback controlado para o que ainda não migrou ao runtime Python
- `aury dev` sem frase permanece como utilitário mínimo do adaptador Fish
- a v1.6.1 fecha coerência pública e estrutural da transição atual, sem prometer expansão de recorte funcional

## v1.6.0

### Consolidado
- caminhada comum de pipeline entre execução real e `aury dev`
- `aury dev <frase>` com leitura por ação, blocos auditáveis e diagnóstico público
- `aury dev` sem frase com validação sintática do arquivo carregado e uso básico

### Melhorado
- domínio de arquivos reaproveita melhor o alvo efetivo em `copiar`, `mover`, `renomear` e `extrair`, inclusive para referência local da ação seguinte
- leitura de localização conversacional e continuidade local ficaram mais observáveis no modo `dev`
- medição de velocidade de rede passou a depender de gatilho explícito com `velocidade` junto de `internet` ou `rede`

### UX pública
- fallback agora assume fronteira honesta e oferece dica de ajuda
- ambiguidades de alvo ou destino deixam de ser executadas silenciosamente e passam a ser expostas ao usuário
- remoção pede confirmação explícita e nega por padrão
- remoção destrutiva sem alvo seguro deixa de reutilizar anáfora frouxa como `ela`
- saída de velocidade da internet passou a expor métricas legíveis em vez de JSON cru

### Compatibilidade e limites
- `aury testar internet` continua sendo um teste simples de conectividade
- pedidos fora do recorte atual, como `abrir arquivo`, continuam em fallback honesto
- `aury dev` ficou mais auditável, mas a paridade com toda formulação conversacional da superfície runtime ainda segue incremental

---

## v1.5.0

### Adicionado
- alias real de shell `ay` além do comando oficial `aury`
- corretor conservador inicial para variações erradas seguras de comandos e estruturas conversacionais
- proteção tipada de tokens sensíveis para caminhos, arquivos e hosts
- suporte inicial e conservador a anáforas locais como `ele`, `ela` e `isso`
- suporte a localização conversacional como `que está em`, `que fica em`, `que tá em`, `dentro de` e variações próximas já cobertas pela base atual
- expansão real do `aury dev` para inspeção de frase original, corrigida, normalizada, tokens sensíveis, intenção, domínio e argumentos

### Melhorado
- parser conversacional com mais imperativos, conectores e vocativos de prefixo
- encadeamento de ações com maior robustez em frases naturais
- coerência entre `aury`, `ay` e `aury dev`
- UX conversacional com respostas mais naturais e mais claras
- exibição do destino efetivo final em operações de copiar e mover

### Corrigido
- correções de classificação entre arquivo, pasta, item, nomes ocultos e caminhos com barra final
- correções em localização conversacional para evitar interpretar o diretório inteiro como alvo indevido
- correções em encadeamentos com imperativos como `copie`, `mova`, `remova` e variantes relacionadas já cobertas
- remoção de intenções fantasma e alinhamento entre observabilidade e execução real

### UX
- mensagens padronizadas no estilo `Pronto, eu...`, `Feito, eu...` e `Tudo certo, eu...`
- cancelamento mais natural e claro
- distinção mais consistente entre arquivo e pasta nas respostas

### Compatibilidade
- mantida compatibilidade com a base funcional da v1.4.3
- mantida a linha 1.x com expansão conservadora e segura

---

---

## v1.4.3

### Corrigido
- corrigido o encadeamento de ações de sistema e pacote em frases como `aury atualiza, otimiza e baixa o firefox`
- corrigido o tratamento de intenções únicas de sistema sem alvo explícito durante a expansão interna de ações
- mantida a execução correta de sequências como `aury atualiza e otimiza` e `aury otimiza e atualiza`

### Compatibilidade
- mantida compatibilidade com a base funcional da v1.4.2

---

## v1.4.2

### Adicionado
- suporte inicial e seguro para extração/descompactação de arquivos `.zip`, `.7z`, `.tar`, `.tar.gz` e `.tgz`
- destino padrão previsível para arquivos compactados sem pasta explícita
- validação prévia de conteúdo para bloquear caminhos absolutos e tentativas de path traversal
- mensagens dedicadas para formato não suportado, arquivo ausente, dependência ausente e destino já existente

### Melhorado
- expansão conversacional incremental também aplicada aos comandos já existentes
- suporte melhor a partículas como `que` e `você` em frases naturais
- interpretação de destinos mais conversacionais em comandos de arquivo, como `para a pasta que fica em /usr/steam`
- integração da nova intenção `extrair` ao parser existente sem quebrar o fluxo da v1.4.1

### Compatibilidade
- mantida compatibilidade com a base funcional da v1.4.1
- mantido o modelo incremental de evolução do parser e dos executores

---

## v1.4.1

### Adicionado
- refinamento global de conversacionalidade do parser
- suporte melhor a partículas como `que`, `você`, `por favor`, `pra mim` e similares
- suporte a formas conversacionais como:
  - `pinga`
  - `pingar`
  - `pingue`
  - `recarrega`
  - `verifica o código`
  - `valida o código`
  - `confere o código`

### Melhorado
- preservação de intenções intermediárias em frases longas
- interpretação de frases polidas e mais naturais
- estabilidade dos comandos internos em modo conversacional
- estabilidade dos comandos de pacote em modo conversacional
- estabilidade dos comandos de sistema em modo conversacional
- estabilidade dos comandos de rede em modo conversacional

### Corrigido
- `Aury, pode instalar o firefox?`
- `Aury, por favor, me mostra o status do sistema.`
- `Aury, pinga o google.com.`
- `Aury, quero que você atualize, otimize o sistema e baixe o firefox.`
- `Aury, me ajuda a copiar base/origem.txt para backup3.txt.`
- `Aury, me ajuda a mover base/origem.txt para final.txt.`

### Resultado
A versão **v1.4.1** da Aury fecha a fase de refinamento conversacional da série v1.4, mantendo compatibilidade com a base da **v1.4.0** e preparando o terreno para a **v1.5.0**.

---

## v1.4.0

### Adicionado
- interpretação de frases mais naturais
- suporte a auxiliares como `quero`, `pode` e similares
- suporte ao vocativo `Aury,`
- suporte a pontuação estilo chat
- suporte a conectores como `para` e `em`

### Melhorado
- interpretação de múltiplas intenções em um único comando
- interpretação de múltiplos alvos compartilhados
- extração de argumentos para comandos de arquivo
- naturalidade geral do parser

### Exemplos

```text
aury quero instalar obs studio
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
aury mover arquivo teste.txt para pasta/teste.txt
```

---

## v1.3.1

### Adicionado
- suporte a vocativo `Aury,`
- suporte a pontuação estilo chat (`.`, `!`, `?`, `:`)
- suporte ao comando `Aury` com letra maiúscula

### Melhorado
- limpeza de argumentos com pontuação final
- base interna preparada para a linha 1.4

### Compatibilidade
- mantida compatibilidade com os comandos da 1.3.0

---

## v1.3.0

### Adicionado
- parser mais natural para comandos comuns
- expansão de sinônimos de intenção
- melhor suporte a frases como:
  - `aury instala firefox`
  - `aury mostrar cpu`
  - `aury checar memória`
  - `aury criar teste.txt`

### Melhorado
- detecção de intenção
- inferência de domínio para arquivos sem exigir a palavra `arquivo`
- compatibilidade com múltiplas ações no mesmo comando

### Corrigido
- comandos internos como `ajuda`, `reload` e `dev`
- fluxo de instalação para não tentar fallbacks desnecessários quando o pacote já está instalado

---

## v1.2.1

### Refatoração
- reorganização da arquitetura
- separação de responsabilidades
- executores por domínio
- base preparada para expansão futura

---

## v1.2

### Melhorado
- normalização de linguagem
- correções no processamento de arquivos
- suporte a múltiplas ações
- melhorias no escopo de variáveis

---

## v1.1

### Adicionado
- proteção de entrada
- limpeza de pontuação
- comando `reload`
- comando `dev`

---

## v1.0

### Primeira versão funcional

### Recursos
- gerenciamento de pacotes
- informações do sistema
- operações de rede
- operações básicas de arquivos
