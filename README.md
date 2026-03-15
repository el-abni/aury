# 💜 Aury
![Versão](https://img.shields.io/badge/versão-1.1-purple)
![Licença](https://img.shields.io/badge/licença-MIT-green)
![Shell](https://img.shields.io/badge/shell-fish-blue)

Assistente de terminal para Linux.

Aury é uma assistente de linha de comando criada para **CachyOS e sistemas baseados em Arch Linux**.  
Ela ajuda a executar tarefas comuns do sistema usando comandos simples e diretos.

---

## ✨ Recursos

- 📦 Instalar e remover pacotes  
- 🔎 Procurar pacotes  
- 🚀 Otimizar o sistema  
- 📊 Ver informações do sistema  
- 🌐 Testar conexão de rede  
- 📁 Criar e remover arquivos ou pastas  
- 🛠 Ferramentas para desenvolvimento (`aury dev`)

---

## ⚙️ Requisitos

- Linux  
- Fish Shell  
- Sistema baseado em Arch Linux (pacman / paru)

---

## 📦 Instalação

Clone o repositório:

git clone https://github.com/el-abni/aury.git

Entre na pasta do projeto:

cd aury

Execute o instalador:

./install.sh

---

## 🚀 Uso

Alguns exemplos de comandos:

aury instalar firefox  
aury remover vlc  
aury procurar steam  

aury ver cpu  
aury ver memória  
aury ver disco  

aury testar internet  
aury ping google.com  

---

## 🛠 Desenvolvimento

Verificar o código da Aury:

aury dev

Recarregar a assistente após alterações:

aury reload

---

## 📂 Estrutura do projeto

aury
├─ bin/
│  └─ aury.fish
├─ install.sh
├─ uninstall.sh
├─ README.md
├─ CHANGELOG.md
└─ VERSION

---

## 📜 Licença

Este projeto está licenciado sob a licença MIT.
