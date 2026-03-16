# Changelog

Todas as mudanças importantes deste projeto serão documentadas neste arquivo.

## v1.4.0

### Adicionado
- interpretação de frases mais naturais
- suporte a auxiliares como `quero`, `pode`
- suporte ao vocativo `Aury,`
- suporte a pontuação estilo chat
- suporte a conectores como `para` e `em`

### Melhorado
- interpretação de múltiplas intenções
- interpretação de múltiplos alvos compartilhados
- extração de argumentos para comandos de arquivo
- naturalidade geral do parser

### Compatibilidade
- mantida compatibilidade com os comandos da série 1.3

---

## v1.3.1

Melhorias de naturalidade no parser e preparação para a série 1.4.

### Adicionado
- suporte a vocativo "Aury,"
- suporte a pontuação estilo chat (. ! ? :)
- comando `Aury` com letra maiúscula

### Melhorado
- limpeza de argumentos com pontuação
- base interna preparada para interpretação mais avançada

### Compatibilidade
Nenhuma quebra de compatibilidade com a 1.3.0.

---

## v1.3.0

### Adicionado

- parser mais natural para comandos
- expansão de sinônimos de intenção
- melhor suporte a variações de linguagem
- suporte a frases como:
  - `aury instala firefox`
  - `aury mostrar cpu`
  - `aury checar memória`
  - `aury criar teste.txt`

### Melhorado

- detecção de intenção mais robusta
- inferência automática de operações de arquivo
- suporte aprimorado para múltiplas ações em um único comando

Exemplo:

```
aury ver cpu e mostrar memória
```

### Corrigido

- funcionamento dos comandos internos `ajuda`, `reload` e `dev`
- fluxo de instalação de pacotes para evitar fallbacks desnecessários quando o pacote já está instalado

---

## v1.2.1

Refatoração estrutural completa.

### Mudanças

- reorganização da arquitetura
- separação de responsabilidades
- executores por domínio
- base preparada para expansão futura

---

## v1.2

Melhorias no parser.

### Mudanças

- normalização de linguagem
- correções no processamento de arquivos
- suporte a múltiplas ações
- melhorias no escopo de variáveis

---

## v1.1

Melhorias estruturais.

### Adicionado

- proteção de entrada
- limpeza de pontuação
- comando `reload`
- comando `dev`

---

## v1.0

Primeira versão funcional da Aury.

### Recursos

- gerenciamento de pacotes
- informações do sistema
- operações de rede
- operações básicas de arquivos