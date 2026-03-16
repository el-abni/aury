# 💜 Aury

![Version](https://img.shields.io/badge/version-1.3.1-blue)
![Version](https://img.shields.io/badge/version-1.4.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Shell](https://img.shields.io/badge/shell-fish-4DB6AC)
![Platform](https://img.shields.io/badge/platform-Linux-orange)

Assistente de terminal para Linux com suporte a comandos em linguagem natural.

---

## Sobre

Aury é uma assistente de terminal criada para facilitar o uso do sistema através de comandos mais naturais.

Você pode executar tarefas comuns usando frases simples.

Exemplos:

```
aury instalar firefox
aury ver cpu
aury criar arquivo teste.txt
```

---

## Exemplos de uso

### Pacotes

```
aury instalar firefox
aury instala firefox
aury remover vlc
aury procurar steam
```

### Sistema

```
aury atualizar sistema
aury otimizar sistema
aury status
aury mostrar cpu
aury checar memória
```

### Rede

```
aury ver ip
aury testar internet
aury ping google.com
```

### Arquivos

```
aury criar arquivo teste.txt
aury criar teste.txt
aury criar pasta projetos
aury copiar arquivo teste.txt backup.txt
aury mover arquivo teste.txt pasta/teste.txt
aury renomear arquivo teste.txt novo.txt
```

---

## Exemplos mais naturais (1.3.1)

A versão 1.3.1 melhora o suporte a frases mais naturais.

```
Aury instala o firefox.
Aury checar memória.
aury Aury, instala o obs studio.
```

---

## Comandos internos

```
aury ajuda
aury reload
aury dev
```

---

## Instalação

Clone o repositório:

```
git clone https://github.com/el-abni/aury.git
cd aury
```

Instale:

```
./install.sh
```

---

## Desinstalação

```
./uninstall.sh
```

---

## Estrutura do projeto

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

## Licença

MIT
