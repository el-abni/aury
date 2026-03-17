# Changelog

Todas as mudanças importantes da **💜 Aury** são documentadas neste arquivo.

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
- mantida a linha 1.x com expansão conservadora e segura, preparando a base para a v2.0

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
