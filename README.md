# Aury

💜 Terminal Assistant for CachyOS (Fish shell)

A Aury é uma assistente de terminal criada para simplificar tarefas comuns no CachyOS e Arch Linux usando comandos em linguagem natural.

![Version](https://img.shields.io/badge/version-1.2.1-purple)
![Shell](https://img.shields.io/badge/shell-fish-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

# Sobre

A Aury funciona como uma assistente inteligente para o terminal, permitindo executar operações comuns do sistema com comandos simples e naturais.

Ela foi projetada para ser:

- simples
- rápida
- amigável para iniciantes
- útil para usuários avançados
- pronta para evoluir de forma modular

Tudo rodando diretamente no Fish shell.

---

# Versão atual

1.2.1 (stable)

A versão 1.2.1 é uma refatoração estrutural da base da Aury.  
Ela mantém compatibilidade com a 1.2, mas reorganiza o código para preparar as próximas versões até a futura 2.0 com IA.

---

# Recursos

## Pacotes

aury instalar firefox  
aury remover vlc  
aury procurar steam  

A Aury gerencia pacotes usando:

- pacman
- paru (se disponível)
- flatpak (fallback)

---

## Sistema

aury atualizar sistema  
aury otimizar sistema  
aury status  

A Aury pode:

- atualizar o sistema
- limpar cache
- remover pacotes órfãos
- mostrar visão geral do sistema

---

## Informações do sistema

aury ver cpu  
aury ver memória  
aury ver disco  
aury ver gpu  
aury ver processos  

---

## Rede

aury ver ip  
aury testar internet  
aury ping google.com  

---

## Arquivos

aury criar arquivo teste.txt  
aury criar pasta projetos  
aury copiar arquivo teste.txt backup.txt  
aury mover arquivo teste.txt pasta/teste.txt  
aury renomear arquivo teste.txt novo.txt  
aury remover arquivo teste.txt  

Para nomes com espaço use aspas:

aury criar arquivo "Minha Pasta/Meu Arquivo.txt"

---

## Utilidades internas

aury reload  
aury dev  

reload → recarrega A Aury  
dev → verifica se o código da Aury contém erros

---

# Instalação

git clone https://github.com/el-abni/aury.git  
cd aury  

Execute o instalador:

./install.sh

---

# Requisitos

- CachyOS ou Arch Linux
- Fish shell

---

# Estrutura do projeto

aury  
├── bin/  
│   └── aury.fish  
├── install.sh  
├── uninstall.sh  
├── README.md  
├── CHANGELOG.md  
└── VERSION  

---

# Filosofia do projeto

A evolução da Aury segue esta ideia:

1.x → fortalecer o núcleo interno  
2.0 → adicionar IA para conversação e fallback inteligente

Antes da IA, A Aury busca ser o mais natural e poderosa possível usando regras bem estruturadas.

---

# Licença

MIT License

---

Projeto criado por Abni
