# Changelog

Todas as mudanças importantes deste projeto serão documentadas neste arquivo.

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