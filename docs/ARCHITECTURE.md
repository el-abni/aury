# Arquitetura da 💜 Aury

Este documento descreve o estado público sustentado pela **💜 Aury v1.6.0**.

Aury é uma assistente de terminal para **CachyOS**. A proposta continua a mesma: receber frases humanas, fechar uma leitura segura e encaminhar a ação para executores simples por domínio.

Na superfície pública atual, a entrada pode acontecer por `aury` ou pelo atalho `ay`. A ajuda pública continua em `aury ajuda`, e a observabilidade de engenharia fica em `aury dev`.

---

## O que a v1.6 consolida

A v1.6 não reabre a proposta do projeto. Ela consolida a base pública e arquitetural já existente:

- caminhada comum de pipeline entre execução real e `aury dev`
- `aury dev <frase>` mais auditável, com leitura por ação e estados diagnósticos explícitos
- UX pública mais honesta em fallback, ambiguidade e remoção
- domínio de arquivos com continuidade melhor entre ação atual e referência local seguinte
- recorte de rede mais preciso para medir velocidade sem contaminar `aury testar internet`

Essa consolidação fortalece a superfície pública sem prometer expansão ampla de escopo.

---

## Pipeline compartilhado

O pipeline público segue esta ordem lógica:

```text
Entrada do usuário
↓
Pré-processamento
↓
Proteção de tokens sensíveis
↓
Correção conservadora e normalização
↓
Split e expansão de ações
↓
Interpretação da frase
↓
Detecção de intenção e domínio
↓
Resolução de argumentos
↓
Execução real ou relatório em modo dev
↓
Fallback ou bloqueio explícito, quando necessário
```

O ponto mais importante da v1.6 é que **runtime** e **modo dev** passaram a caminhar o mesmo miolo de ações em vez de cada um manter um fluxo grande e separado.

Na prática:

- o runtime percorre as ações finais e tenta executá-las
- o `aury dev` percorre essas mesmas ações para relatar como a leitura foi fechada
- fallback, bloqueios e ambiguidades deixam de ficar escondidos como detalhe interno

Isso não significa paridade perfeita em toda formulação possível, mas reduz divergência estrutural entre “o que a Aury tenta fazer” e “o que ela diz que entendeu”.

---

## Etapas que continuam centrais

### Pré-processamento e normalização

A Aury continua removendo ruído conversacional previsível, tratando vocativo `Aury,`, pontuação de chat e auxiliares frequentes.

Antes de corrigir ou simplificar palavras, a v1.x preserva tokens sensíveis como:

- caminhos
- nomes de arquivo
- hosts e domínios
- extensões compostas como `tar.gz`

Isso permite mexer na fala sem deformar o argumento real.

### Split e expansão

Aury continua separando ou expandindo frases com múltiplas ações e alvos compartilhados.

Exemplos sustentados pela superfície pública:

```text
aury atualiza, otimiza e baixa o firefox
aury ver cpu e memória
```

### Resolução de argumentos

O núcleo continua tentando fechar:

- tipo de alvo
- origem
- destino
- novo nome
- localização conversacional

Na v1.6, o domínio de arquivos ficou melhor em reaproveitar o **alvo efetivo final** de uma ação como referência local da ação seguinte.

---

## `aury dev` na v1.6

O `aury dev` virou a principal janela pública de observabilidade do pipeline.

Sem frase:

- valida a sintaxe do arquivo carregado
- mostra o caminho do arquivo-fonte em uso
- imprime `Use: aury dev <frase>`

Com frase:

- imprime um bloco `Entrada global`
- depois relata cada ação final emitida pelo pipeline

Os blocos por ação hoje são:

- `Entrada`
- `Enquadramento`
- `Entidades`
- `Diagnostico`
- `Acao prevista`
- `Observacoes`

Os estados diagnósticos públicos atuais são:

- `CONSISTENTE`
- `PARCIAL`
- `AMBIGUA`
- `BLOQUEADA`
- `NAO_ENQUADRADA`

Isso torna o `dev` útil para auditar:

- intenção e domínio lidos
- origem, destino e novo nome quando existirem
- uso de localização conversacional
- leitura anafórica local
- casos que caem em fronteira honesta ou bloqueio deliberado

Limite importante: o `aury dev` já está forte para frases canônicas e para parte da camada conversacional consolidada, mas **ainda não deve ser documentado como garantia de paridade total com toda frase conversacional aceita no runtime**.

---

## Domínios públicos consolidados

### Interno

O domínio interno segue pequeno:

- `ajuda`
- `reload`
- `dev`

### Pacotes e sistema

Os domínios de pacote e sistema permanecem próximos do desenho anterior: parser resolve a intenção e os executores fazem a chamada operacional correspondente.

Aqui a principal verdade arquitetural continua sendo a separação:

- interpretação e resolução antes
- executor simples depois

### Rede

Na v1.6, a superfície de rede fica mais explícita.

`aury testar internet` continua significando teste simples de conectividade por `ping`.

A medição de velocidade agora fica num recorte estreito e deliberado:

- precisa haver `velocidade`
- e também `internet` ou `rede`

Exemplos:

```text
aury velocidade da internet
aury velocidade da rede
```

Esse fluxo depende de `librespeed-cli` e de `python3` para ler o retorno com confiança. Quando o backend falta, falha ou devolve JSON insuficiente, a Aury responde com erro honesto.

### Arquivos e extração

O domínio de arquivos segue sendo o trecho mais sensível da superfície pública.

Na v1.6, ele consolida:

- localização conversacional para fechar origem ou destino
- extração segura de `.zip`, `.7z`, `.tar`, `.tar.gz` e `.tgz`
- continuidade de referência local após `copiar`, `mover`, `renomear` e `extrair`
- bloqueio público de coordenação ambígua em alvo ou destino
- confirmação destrutiva explícita para remoção

Essa camada não tenta “adivinhar” mais do que o necessário. Quando a leitura não fecha com segurança, a arquitetura prefere bloquear ou cair em fallback.

---

## Fronteiras públicas deliberadas

Algumas fronteiras ficaram mais nítidas na v1.6 e devem permanecer documentadas como tal:

- pedidos fora do recorte atual, como `abrir o arquivo relatorio.pdf`, continuam em fallback honesto
- remoção com anáfora destrutiva sem alvo seguro, como `remover ela`, é bloqueada explicitamente
- coordenação que deixa mais de um destino plausível deixa de executar e passa a ser exposta como ambiguidade pública

Arquiteturalmente, isso é intencional. A Aury continua preferindo uma recusa clara a uma execução arriscada.

---

## Tensões herdadas que continuam reais

Nem tudo virou problema resolvido na v1.6. As tensões públicas relevantes são:

- `tests/casos.yaml` continua sendo um contrato incremental de regressão, não uma prova de que toda frase listada já fecha hoje com a mesma robustez no `aury dev`
- parte das formulações conversacionais mais livres em arquivos e extração ainda é mais estável no runtime do que no relatório do `dev`
- a leitura prevista em alguns casos de rede no `dev` ainda é mais estrutural do que polida
- comandos operacionais de pacote e sistema dependem das ferramentas do host e, em muitos casos, de privilégios externos ao parser

Essas tensões não invalidam a v1.6. Elas apenas definem com honestidade onde a documentação pública deve parar.

---

## Resumo arquitetural

A **💜 Aury v1.6.0** fica arquiteturalmente mais coerente porque:

- runtime e `dev` compartilham melhor o mesmo miolo
- a superfície pública ficou mais honesta em erro, bloqueio e ambiguidade
- arquivos e extração reaproveitam melhor o alvo efetivo entre ações
- rede ganhou um recorte mais explícito para velocidade da internet

O resultado não é “uma Aury nova”. É a mesma linha 1.x com uma base pública mais alinhada ao que a implementação realmente sustenta hoje.
