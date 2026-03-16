# Changelog

Todas as mudanças importantes da **💜 Aury** são documentadas neste arquivo.

---

## 1.4.0

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

## 1.3.1

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

## 1.3.0

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

## 1.2.1

### Refatoração
- reorganização da arquitetura
- separação de responsabilidades
- executores por domínio
- base preparada para expansão futura

---

## 1.2

### Melhorado
- normalização de linguagem
- correções no processamento de arquivos
- suporte a múltiplas ações
- melhorias no escopo de variáveis

---

## 1.1

### Adicionado
- proteção de entrada
- limpeza de pontuação
- comando `reload`
- comando `dev`

---

## 1.0

### Primeira versão funcional

### Recursos
- gerenciamento de pacotes
- informações do sistema
- operações de rede
- operações básicas de arquivos
