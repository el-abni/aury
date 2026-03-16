# Arquitetura da 💜 Aury

Aury é construída como uma **camada de interpretação de linguagem natural para o terminal**.

Fluxo geral:

```
Entrada do usuário
↓
Normalização de texto
↓
Parser de intenção
↓
Parser de alvos
↓
Executor de domínio
↓
Comando real do sistema
```

---

# Componentes

## 1. Normalização

Responsável por:

- remover pontuação irrelevante
- normalizar texto
- tratar variações como:

```
Aury,
aury
aury,
``

Também remove palavras auxiliares como:

```
quero
pode
por favor
```

---

## 2. Parser de intenção

Detecta o que o usuário quer fazer.

Exemplos:

```
instalar
baixar
remover
criar
copiar
mover
renomear
ver
mostrar
```

Também suporta **múltiplas intenções**:

```
aury atualiza e otimiza
```

---

## 3. Parser de alvos

Detecta o objeto da ação.

Exemplos:

```
firefox
obs studio
teste.txt
pasta/teste.txt
```

Também entende conectores:

```
para
em
```

---

## 4. Executor de domínio

Dependendo da intenção, Aury direciona para um executor:

### Pacotes

usa `pacman`

### Sistema

usa ferramentas como:

```
lscpu
free
df
```

### Rede

```
ip
ping
```

### Arquivos

```
cp
mv
rm
touch
mkdir
```

---

# Objetivo da arquitetura

Permitir que Aury evolua para:

- parser mais inteligente
- contexto entre comandos
- interpretação semântica
- integração futura com IA
