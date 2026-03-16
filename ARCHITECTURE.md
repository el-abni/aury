# Arquitetura da Aury

Este documento descreve a arquitetura interna da Aury e o fluxo de interpretação de comandos.

O objetivo é facilitar a evolução do projeto e manter o código organizado conforme novas versões são desenvolvidas.

---

# Visão geral

Aury é uma assistente de terminal baseada em Fish Shell que executa tarefas do sistema usando linguagem natural.

Exemplo:

```
aury instalar firefox
aury ver cpu
aury criar arquivo teste.txt
```

A arquitetura foi projetada para funcionar sem inteligência artificial na série **1.x**, utilizando regras internas de interpretação.

A série **2.x** introduzirá suporte opcional a IA local.

---

# Pipeline de execução

O fluxo interno da Aury segue este pipeline:

```
entrada do usuário
↓
validação de entrada
↓
normalização de linguagem
↓
divisão de múltiplas ações
↓
detecção de intenção
↓
detecção de domínio
↓
resolução de argumentos
↓
execução
↓
fallback
```

Cada etapa possui uma responsabilidade específica.

---

# Componentes principais

## 1. Validação de entrada

Função responsável por verificar se o comando digitado é válido.

Exemplos de validação:

- comando vazio
- apenas números
- apenas pontuação

---

## 2. Normalização de linguagem

Converte palavras em uma forma padrão.

Exemplo:

```
instala → instalar
mostrar → ver
checar → ver
```

Também remove palavras irrelevantes:

```
o
a
para
pra
mim
por favor
```

---

## 3. Split de ações

Permite executar múltiplas ações em um único comando.

Exemplo:

```
aury ver cpu e mostrar memória
```

Se transforma em duas ações:

```
ver cpu
mostrar memória
```

---

## 4. Detecção de intenção

Determina qual ação o usuário deseja executar.

Exemplos de intenções:

```
instalar
remover
procurar
ver
criar
copiar
mover
renomear
ping
```

A intenção é o **verbo principal da frase**.

---

## 5. Detecção de domínio

Define qual executor deve ser utilizado.

Domínios atuais:

```
interno
sistema
rede
pacote
arquivo
pasta
```

Exemplo:

```
aury ver cpu
```

Domínio detectado:

```
sistema
```

---

## 6. Resolução de argumentos

Extrai parâmetros relevantes da frase.

Exemplo:

```
aury copiar teste.txt backup.txt
```

Argumentos:

```
origem: teste.txt
destino: backup.txt
```

---

## 7. Execução

Cada domínio possui seu próprio executor.

Executores atuais:

```
__aury_exec_internal
__aury_exec_system
__aury_exec_network
__aury_exec_packages
__aury_exec_files
```

---

## 8. Fallback

Caso nenhum comando seja reconhecido, a Aury retorna:

```
Não entendi
Digite: aury ajuda
```

Nas versões futuras isso evoluirá para sugestões inteligentes.

---

# Filosofia da arquitetura

A arquitetura da Aury segue alguns princípios:

### Separação de responsabilidades

Cada parte do sistema faz apenas uma coisa.

### Parser baseado em regras

A série **1.x** utiliza apenas regras internas.

### Evolução incremental

Cada versão adiciona pequenas melhorias sem quebrar o funcionamento existente.

---

# Roadmap arquitetural

## Série 1.x

Fortalecer o motor de interpretação.

Versões planejadas:

```
1.3  parser mais natural
1.4  interpretação melhor
1.5  argumentos mais inteligentes
1.6  melhorias de rede
1.7  melhorias de pacotes
1.8  fallback inteligente
1.9  refinamento geral
```

---

## Série 2.x

Integração com IA local.

Fluxo previsto:

```
comando reconhecido?
   sim → executa
   não → IA interpreta
```

Exemplo:

```
aury meu disco está cheio
```

A IA pode transformar em:

```
aury ver disco
aury otimizar sistema
```

---

# Estrutura do projeto

```
aury/
│
├─ bin/
│   └─ aury.fish
│
├─ README.md
├─ CHANGELOG.md
├─ VERSION
├─ install.sh
└─ uninstall.sh
```

---

# Objetivo do projeto

Criar um assistente de terminal poderoso, simples e natural de usar.

Aury busca combinar:

- simplicidade de comandos
- poder do terminal Linux
- interpretação de linguagem natural
