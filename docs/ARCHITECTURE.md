# Arquitetura da 💜 Aury

Este documento descreve a arquitetura atual da **💜 Aury**, seu fluxo interno de processamento e a direção de evolução do projeto.

Aury é uma assistente de terminal feita especificamente para **CachyOS**, com foco em transformar frases naturais em ações reais no sistema.

Na v1.5.0, a entrada pública pode acontecer tanto por `aury` quanto pelo atalho `ay`, ambos apontando para o mesmo fluxo interno.

---

## Objetivo da arquitetura

A arquitetura da Aury existe para permitir que o projeto cresça de forma organizada, previsível e incremental.

Os objetivos principais são:

- interpretar comandos em linguagem natural
- manter separação clara de responsabilidades
- evitar lógica excessiva dentro dos executores
- facilitar a expansão das versões 1.x
- fortalecer o núcleo da linha 1.x até o fechamento planejado em v1.9

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
ay instalar firefox
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
aury extraia teste.tar para a pasta que fica em /usr/steam
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

- remoção do vocativo de prefixo `Aury,`
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

Na v1.5.0, essa etapa foi reforçada por um corretor conservador e por proteção explícita de tokens sensíveis antes de corrigir ou simplificar a frase.

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

Tokens sensíveis preservados nessa fase incluem principalmente:

- caminhos
- hosts e domínios
- nomes de arquivo
- extensões compostas como `tar.gz`

Isso permite corrigir estruturas conversacionais sem deformar argumentos reais.

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

Essa é uma das partes mais importantes da arquitetura da série 1.5.

Aqui a Aury tenta entender melhor a estrutura da frase antes da execução.

Ela já suporta:

- intenção no meio da frase
- palavras auxiliares como `quero`, `pode`
- partículas conversacionais como `que` e `você`
- múltiplas intenções
- múltiplos alvos compartilhados
- conectores como `para`, `pra` e `em`
- localização conversacional em padrões como `que está em`, `que fica em` e `que tá em`
- anáforas locais seguras com `ele`, `ela` e `isso`, quando existe referência local válida
- destinos descritos de forma mais natural em fluxos de arquivo e extração

Exemplos:

```text
aury quero instalar obs studio
aury ver cpu e memória
aury mover teste.txt para pasta/teste.txt
aury extraia teste.tar para a pasta que fica em /usr/steam
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

Desde a v1.4.2, e mantida na v1.5.0, a extração de arquivos compactados é tratada dentro do domínio de **arquivo**, reaproveitando a mesma base de parser, resolução de argumentos e execução segura.

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
- tratamento mais rico de casos ambíguos

---

## Interpretação de linguagem natural

A linha v1.4 ampliou significativamente a capacidade de interpretação da Aury.

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

## Refinamento conversacional na v1.5.0

A **💜 Aury v1.5.0** consolidou a camada conversacional conservadora da linha 1.x.

Além da base da linha 1.4, a Aury passou a lidar melhor com partículas e construções como:

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

Na prática, a v1.5.0 reforça quatro pontos:

- correção leve e conservadora, focada em verbos e partículas
- proteção de tokens sensíveis antes da correção
- localização conversacional para origem e destino
- resolução anafórica local quando a referência anterior é única e segura

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

### Continuidade da linha 1.x

A série 1.x fortalece o núcleo local da Aury de forma incremental, previsível e auditável.
O fechamento planejado desta linha principal neste repositório acontece na v1.9.

---

## Estado atual na v1.5.0

A Aury já entrega:

- comandos mais naturais
- múltiplas intenções
- múltiplos alvos compartilhados
- conectores de argumento
- vocativo `Aury,`
- pontuação estilo chat
- corretor conservador com foco em fala conversacional
- proteção de tokens sensíveis durante correção e normalização
- extração segura de arquivos `.zip`, `.7z`, `.tar`, `.tar.gz` e `.tgz`
- localização conversacional em frases como `para a pasta que fica em /usr/steam`
- anáforas locais seguras com `ele`, `ela` e `isso`
- atalho público `ay` para o mesmo fluxo da `aury`
- modo `aury dev` com inspeção de frase original, corrigida, normalizada, tokens sensíveis, intenção, domínio, argumentos e localização conversacional
- melhor estabilidade entre comandos diretos e conversacionais

Isso coloca a Aury em um estágio mais maduro dentro da série 1.x.

---

## Próximas direções

### v1.6
- consolidação do pipeline interno sobre a base da v1.5.0
- fortalecimento do `aury dev` como ferramenta de engenharia
- melhorias pontuais de rede e mensagens públicas
- mais robustez em parser, normalização e resolução sem romper compatibilidade

### v1.7
- ampliação incremental da capacidade operacional local
- continuidade do refinamento seguro dos fluxos práticos da Aury

### v1.8
- refinamentos intermediários da linha 1.x com foco em robustez, previsibilidade e experiência

### v1.9
- refinamento geral
- fechamento planejado da linha principal da Aury neste repositório

---

## Resumo

A arquitetura da **💜 Aury** foi construída para permitir crescimento contínuo sem perder clareza.

Ela já possui:

- pipeline bem definido
- interpretação natural crescente
- separação entre parser e execução
- refinamento conversacional consolidado até a v1.5.0
- base preparada para o fechamento sólido da linha 1.x

Aury continua sendo um projeto de terminal, mas com uma proposta clara: tornar o uso do terminal no **CachyOS** mais natural, confortável e poderoso.
