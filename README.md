# 💜 Aury

![version](https://img.shields.io/badge/version-1.4.0-purple)
![shell](https://img.shields.io/badge/shell-fish-blue)
![platform](https://img.shields.io/badge/platform-CachyOS-orange)

**Aury** é uma assistente de terminal feita para **CachyOS**.

Ela permite executar tarefas comuns do sistema usando **linguagem natural**, tornando o terminal mais acessível sem perder o poder das ferramentas tradicionais.

Em vez de decorar comandos complexos, você pode simplesmente escrever o que quer fazer.

---

# Ideia do projeto

Aury funciona como uma **camada de interpretação entre você e o sistema**.

Ela entende frases humanas e traduz isso para comandos reais do sistema.

Exemplo:

```bash
aury quero instalar obs studio
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
aury mover arquivo teste.txt para pasta/teste.txt
```

O objetivo do projeto é transformar o terminal em algo mais **natural, rápido e confortável de usar**.

---

# Funcionalidades

## 📦 Pacotes

Instalar, remover e buscar programas.

Exemplos:

```bash
aury instalar firefox
aury baixar obs studio
aury remover vlc
aury procurar steam
```

---

## ⚙ Sistema

Informações e manutenção do sistema.

```bash
aury atualizar sistema
aury otimizar sistema
aury mostrar cpu
aury checar memória
aury status
```

---

## 🌐 Rede

Ferramentas rápidas de diagnóstico.

```bash
aury ver ip
aury testar internet
aury ping google.com
```

---

## 📄 Arquivos

Operações básicas de arquivos e pastas.

```bash
aury criar arquivo teste.txt
aury criar pasta projetos
aury copiar arquivo teste.txt backup.txt
aury mover arquivo teste.txt pasta/teste.txt
aury renomear arquivo teste.txt novo.txt
aury remover arquivo teste.txt
```

---

# Linguagem natural

Aury entende frases mais humanas.

Exemplos válidos:

```bash
aury quero instalar obs studio
aury pode instalar o firefox
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
aury Aury, instala o obs studio.
```

Ela também entende:

- pontuação
- conectores como **e**, **para**, **em**
- múltiplas ações no mesmo comando

---

# Instalação

Clone o repositório:

```bash
git clone https://github.com/el-abni/aury.git
cd aury
```

Copie a função para o Fish:

```bash
cp bin/aury.fish ~/.config/fish/functions/aury.fish
```

Agora o comando `aury` estará disponível no terminal.

---

# Comando de ajuda

```bash
aury ajuda
```

Mostra todos os exemplos disponíveis.

---

# Roadmap

O roadmap mostra **apenas as próximas versões planejadas**.

## 1.5

Planejado:

- interpretação de caminhos mais inteligente
- melhor contexto de arquivos
- expansão de sinônimos
- mais robustez no parser

## 1.6

Planejado:

- sistema de contexto entre comandos
- detecção automática de intenção dominante
- melhorias na arquitetura interna

## 2.0

Grande evolução da Aury:

- integração com IA
- interpretação semântica mais avançada
- sugestões automáticas de comando
- assistente de terminal mais conversacional

---

# Filosofia

Aury não tenta substituir o terminal.

Ela existe para:

- reduzir fricção
- acelerar tarefas comuns
- tornar o terminal mais humano

O terminal continua sendo poderoso.

Aury apenas torna ele **mais natural de usar**.

---

# Licença

Projeto open source.
