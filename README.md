# 💜Aury

**Terminal Assistant for CachyOS (Fish shell)**

A Aury é uma assistente de terminal criada para simplificar tarefas comuns no CachyOS e Arch Linux usando comandos em linguagem natural.

![Version](https://img.shields.io/badge/version-1.2-purple)
![Shell](https://img.shields.io/badge/shell-fish-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

# Sobre

A Aury funciona como uma **assistente inteligente para o terminal**, permitindo executar operações comuns do sistema com comandos simples e naturais.

Ela foi projetada para ser:

* simples
* rápida
* amigável para iniciantes
* útil para usuários avançados

Tudo rodando diretamente no **Fish shell**.

---

# Recursos

## Pacotes

```bash
aury instalar firefox
aury remover vlc
aury procurar steam
```

A Aury gerencia pacotes usando:

* pacman
* paru (se disponível)
* flatpak (fallback)

---

## Sistema

```bash
aury atualizar sistema
aury otimizar sistema
aury status
```

A Aury pode:

* atualizar o sistema
* limpar cache
* remover pacotes órfãos
* mostrar uma visão geral do sistema

---

## Informações do sistema

```bash
aury ver cpu
aury ver memória
aury ver disco
aury ver gpu
aury ver processos
```

A Aury mostra informações úteis do sistema diretamente no terminal.

---

## Rede

```bash
aury ver ip
aury testar internet
aury ping google.com
```

A Aury também pode ajudar no diagnóstico de conectividade.

---

## Arquivos

```bash
aury criar arquivo teste.txt
aury criar pasta projetos
aury copiar arquivo teste.txt backup.txt
aury mover arquivo teste.txt pasta/teste.txt
aury renomear arquivo teste.txt novo.txt
aury remover arquivo teste.txt
```

A Aury permite gerenciar arquivos e pastas usando linguagem natural.

---

## Utilidades internas

```bash
aury reload
aury dev
```

* **reload** → recarrega a Aury
* **dev** → verifica se o código da Aury contém erros

---

# Instalação

Clone o repositório:

```bash
git clone https://github.com/el-abni/aury.git
cd aury
```

Execute o instalador:

```bash
./install.sh
```

---

# Requisitos

* CachyOS ou Arch Linux
* Fish shell

---

# Estrutura do projeto

```
aury
 ├── bin/
 │   └── aury.fish
 ├── install.sh
 ├── uninstall.sh
 ├── README.md
 ├── CHANGELOG.md
 └── VERSION
```

---

# Licença

MIT License

---

Projeto criado por **Abni**
