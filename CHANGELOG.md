# 📜 Histórico de versões (Changelog)

Todas as mudanças importantes da Aury serão documentadas aqui.

O formato segue o padrão de versionamento do projeto.

## v1.2.1

### Refatoração
- Reorganização estrutural completa da Aury
- Separação entre entrada, normalização, parser, resolução e execução
- Criação de executores por domínio: sistema, rede, pacotes e arquivos
- Fallback isolado para facilitar evolução futura

### Compatibilidade
- Mantido o comportamento principal da versão 1.2
- Comandos já validados continuam funcionando

### Base futura
- Estrutura preparada para a evolução semântica da Aury 1.3
- Base pronta para expansão gradual até a 2.0

---
## v1.2

### Melhorias
- Parser de comandos mais robusto
- Melhor normalização de linguagem natural
- Preservação correta de nomes de arquivos e caminhos
- Melhor suporte a múltiplas ações

### Correções
- Corrigido problema de compatibilidade com `test` no Fish
- Corrigido escopo de variáveis que afetava operações de arquivo
- Corrigidas operações de criar, copiar, renomear e mover arquivos
- `aury reload` e `aury dev` funcionando corretamente

### Estabilidade
- Versão validada em testes reais no CachyOS com Fish shell
---

## v1.1

### Adicionado
- Proteção avançada na entrada de comandos
- Comando `aury reload`
- Modo desenvolvedor `aury dev`

### Melhorado
- Validação de entrada do usuário
- Limpeza de pontuação
- Estrutura inicial do parser

---

## v1.0

### Inicial
- Primeira versão funcional da Aury
- Instalação e remoção de pacotes
- Busca de pacotes
- Informações do sistema
- Testes de rede
- Gerenciamento básico de arquivos
