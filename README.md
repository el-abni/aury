# 💜 Aury

![version](https://img.shields.io/badge/version-1.4.0-purple)
![shell](https://img.shields.io/badge/shell-fish-blue)
![platform](https://img.shields.io/badge/platform-CachyOS-orange)

**Aury** é uma assistente de terminal feita especificamente para **CachyOS**.

Ela permite executar tarefas do sistema usando **linguagem natural**, traduzindo frases humanas para comandos reais do sistema.

Exemplo:

```bash
aury quero instalar obs studio
aury ver cpu e memória
aury atualiza, otimiza e baixa o firefox
aury mover arquivo teste.txt para pasta/teste.txt
```

---

# O que a Aury faz

### 📦 Pacotes

```bash
aury instalar firefox
aury baixar obs studio
aury remover vlc
aury procurar steam
```

### ⚙ Sistema

```bash
aury atualizar sistema
aury otimizar sistema
aury mostrar cpu
aury checar memória
aury status
```

### 🌐 Rede

```bash
aury ver ip
aury testar internet
aury ping google.com
```

### 📄 Arquivos

```bash
aury criar arquivo teste.txt
aury criar pasta projetos
aury copiar arquivo teste.txt backup.txt
aury mover arquivo teste.txt pasta/teste.txt
aury renomear arquivo teste.txt novo.txt
aury remover arquivo teste.txt
```

---

# Instalação

```bash
git clone https://github.com/el-abni/aury.git
cd aury
cp bin/aury.fish ~/.config/fish/functions/aury.fish
```

Depois disso:

```bash
aury ajuda
```

---

# Documentação

Documentação mais detalhada está na pasta:

```
docs/
```

Arquivos:

- `architecture.md`
- `commands.md` (futuro)
- `roadmap.md` (futuro)

---

# Roadmap

O roadmap mostra **apenas versões futuras planejadas**.

## 1.5

- interpretação de caminhos mais inteligente
- expansão de sinônimos
- melhor contexto de arquivos

## 1.6

- contexto entre comandos
- melhor inferência de intenção

## 2.0

- integração com IA
- interpretação semântica avançada
- assistente mais conversacional

---

# Filosofia

Aury não substitui o terminal.

Ela existe para:

- reduzir fricção
- acelerar tarefas comuns
- tornar o terminal mais natural
