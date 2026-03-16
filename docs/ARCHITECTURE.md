# Arquitetura da 💜 Aury

Este documento descreve a arquitetura atual da **💜 Aury**, seu fluxo interno de processamento e a direção de evolução do projeto.

Aury é uma assistente de terminal feita especificamente para **CachyOS**, com foco em transformar frases naturais em ações reais no sistema.

---

## Objetivo da arquitetura

A arquitetura da Aury existe para permitir que o projeto cresça de forma organizada, previsível e incremental.

Os objetivos principais são:

- interpretar comandos em linguagem natural
- manter separação clara de responsabilidades
- evitar lógica excessiva dentro dos executores
- facilitar a expansão das versões 1.x
- preparar a base para a futura integração com IA na série 2.x

---

## Visão geral

Aury funciona como uma camada entre o usuário e o terminal.

Em vez de exigir que o usuário memorize comandos tradicionais, a Aury recebe uma frase, interpreta sua intenção e executa a ação apropriada.

Exemplo:

```text
aury quero instalar obs studio
```

Aury interpreta essa frase e converte a intenção em uma ação de instalação de pacote.

---

## Pipeline de processamento

O fluxo interno da Aury segue este pipeline:

```text
Entrada do usuário
↓
Validação
↓
Pré-processamento
↓
Normalização
↓
Split de ações
↓
Interpretação da frase
↓
Detecção de intenção
↓
Detecção de domínio
↓
Resolução de argumentos
↓
Execução
↓
Fallback
```

Cada etapa possui um papel específico.

---

## Etapas da arquitetura

### 1. Entrada do usuário

A Aury recebe os argumentos passados no terminal.

Exemplos:

```text
aury instalar firefox
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
```

---

### 2. Validação

A etapa de validação impede entradas inválidas ou vazias.

Ela existe para evitar processamento desnecessário e respostas inconsistentes.

Casos típicos tratados:

- comando vazio
- texto sem conteúdo útil
- entrada inválida

---

### 3. Pré-processamento

Essa etapa prepara a frase para o parser.

Exemplos do que pode acontecer aqui:

- remoção do vocativo `Aury,`
- tolerância a pontuação estilo chat
- ajuste inicial dos tokens de entrada

Exemplo:

```text
aury Aury, instala o obs studio.
```

é preparado para interpretação sem que a pontuação atrapalhe a execução.

---

### 4. Normalização

A normalização converte diferentes formas de escrever a mesma ideia em uma forma interna consistente.

Exemplos:

```text
instala   → instalar
baixar    → instalar
mostrar   → ver
checar    → ver
apagar    → remover
deletar   → remover
```

Também pode tratar palavras auxiliares e conectores.

---

### 5. Split de ações

A Aury suporta mais de uma ação em um único comando.

Exemplo:

```text
aury atualiza e otimiza
```

ou:

```text
aury instala firefox e mostra cpu
```

Essa etapa separa ou expande a frase em ações menores, quando necessário.

---

### 6. Interpretação da frase

Essa é uma das partes mais importantes da arquitetura da série 1.4.

Aqui a Aury tenta entender melhor a estrutura da frase antes da execução.

Ela já suporta:

- intenção no meio da frase
- palavras auxiliares como `quero`, `pode`
- múltiplas intenções
- múltiplos alvos compartilhados
- conectores como `para`, `pra` e `em`

Exemplos:

```text
aury quero instalar obs studio
aury ver cpu e memória
aury mover teste.txt para pasta/teste.txt
```

---

### 7. Detecção de intenção

Depois da interpretação, a Aury identifica qual ação principal deve ser executada.

Exemplos de intenção:

```text
instalar
remover
procurar
ver
criar
copiar
mover
renomear
atualizar
otimizar
ping
```

A intenção é o verbo principal que orienta a execução.

---

### 8. Detecção de domínio

Depois da intenção, a Aury identifica o domínio da ação.

Domínios atuais:

- interno
- pacote
- sistema
- rede
- arquivo
- pasta
- geral

Exemplos:

```text
aury instalar firefox     → pacote
aury mostrar cpu          → sistema
aury ping google.com      → rede
aury copiar teste.txt     → arquivo
```

---

### 9. Resolução de argumentos

A etapa de resolução de argumentos extrai os dados necessários para executar a ação.

Exemplos:

```text
aury copiar teste.txt para backup.txt
```

Resultado esperado:

- origem: `teste.txt`
- destino: `backup.txt`

Outro exemplo:

```text
aury mover arquivo teste.txt para pasta/teste.txt
```

Resultado esperado:

- tipo: arquivo
- origem: `teste.txt`
- destino: `pasta/teste.txt`

---

### 10. Execução

A execução é feita por executores especializados por domínio.

Executores atuais:

- `__aury_exec_internal`
- `__aury_exec_system`
- `__aury_exec_network`
- `__aury_exec_packages`
- `__aury_exec_files`

A responsabilidade dos executores é simples:

- receber intenção
- receber domínio
- receber argumentos já resolvidos
- executar a ação real

---

### 11. Fallback

Quando a Aury não entende o comando, ela entra em fallback.

Hoje o fallback ainda é simples, mas ele já serve como base para evoluções futuras.

No futuro, essa área pode crescer para incluir:

- sugestões automáticas
- fallback mais inteligente
- integração com IA

---

## Interpretação de linguagem natural

A versão 1.4 ampliou significativamente a capacidade de interpretação da Aury.

Ela entende melhor:

### frases mais humanas

```text
aury quero instalar obs studio
aury pode instalar o firefox
aury Aury, instala o obs studio.
```

### múltiplos alvos

```text
aury ver cpu e memória
aury mostrar disco e gpu
```

### múltiplas intenções

```text
aury atualiza e otimiza
aury instala firefox e mostra cpu
aury atualiza, otimiza e baixa o firefox
```

### conectores de arquivo

```text
aury copiar teste.txt para backup.txt
aury mover teste.txt para pasta/teste.txt
aury criar arquivo em pasta/teste.txt
```

---

## Refinamento conversacional na v1.4.1

A **💜 Aury v1.4.1** consolidou a camada conversacional da linha 1.4.

Além da base introduzida na v1.4.0, a Aury passou a lidar melhor com partículas e construções como:

- `que`
- `você`
- `por favor`
- `pra mim`
- `me mostra`
- `pinga`
- `pingar`
- `pingue`
- `recarrega`
- `verifica o código`
- `valida o código`
- `confere o código`

Também ficou mais estável em frases como:

```text
Aury, pode instalar o firefox?
Aury, por favor, me mostra o status do sistema.
Aury, pinga o google.com.
Aury, quero que você atualize, otimize o sistema e baixe o firefox.
Aury, me ajuda a copiar base/origem.txt para backup3.txt.
Aury, me ajuda a mover base/origem.txt para final.txt.
```

Essa camada não substitui o parser principal. Ela refina a entrada para que o restante do pipeline continue trabalhando de forma previsível.

---

## Filosofia arquitetural

A arquitetura da Aury segue alguns princípios importantes.

### Separação de responsabilidades

Cada etapa do pipeline deve fazer apenas o que lhe cabe.

### Inteligência antes da execução

A “inteligência” da Aury deve ficar em:

- normalização
- interpretação
- resolução de argumentos

Os executores devem permanecer simples.

### Evolução incremental

Cada versão adiciona capacidades novas sem quebrar o que já funciona.

### Preparação para o futuro

A série 1.x fortalece o núcleo sem IA.
A série 2.x poderá usar IA sobre uma base muito mais sólida.

---

## Estado atual na v1.4.1

A Aury já entrega:

- comandos mais naturais
- múltiplas intenções
- múltiplos alvos compartilhados
- conectores de argumento
- vocativo `Aury,`
- pontuação estilo chat
- partículas conversacionais mais bem tratadas
- frases polidas com melhor interpretação
- melhor estabilidade entre comandos diretos e conversacionais

Isso coloca a Aury em um estágio mais maduro dentro da série 1.x.

---

## Próximas direções

### 1.5
- melhorias em argumentos
- caminhos complexos

### 1.6
- melhorias de rede

### 1.7
- melhorias de pacotes

### 1.8
- fallback inteligente

### 1.9
- refinamento geral

### 2.0
- IA local
- conversação natural
- fallback de comandos complexos

---

## Resumo

A arquitetura da **💜 Aury** foi construída para permitir crescimento contínuo sem perder clareza.

Ela já possui:

- pipeline bem definido
- interpretação natural crescente
- separação entre parser e execução
- refinamento conversacional consolidado na v1.4.1
- base preparada para evoluções maiores

Aury continua sendo um projeto de terminal, mas com uma proposta clara: tornar o uso do terminal no **CachyOS** mais natural, confortável e poderoso.
