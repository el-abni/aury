# Changelog

Todas as mudanças importantes da **💜 Aury** são documentadas neste arquivo.

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
A versão **1.4.1** da Aury fecha a fase de refinamento conversacional da série 1.4, mantendo compatibilidade com a base da **1.4.0** e preparando o terreno para a **1.5.0**.

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
