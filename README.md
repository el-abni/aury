# 💜Aury

Assistente de terminal para Linux com suporte a comandos em linguagem natural.

Aury permite executar tarefas do sistema de forma simples e intuitiva usando frases diretamente no terminal.

Exemplos:

```
aury instalar firefox
aury ver cpu
aury criar arquivo teste.txt
```

A ideia é tornar o terminal mais natural, rápido e acessível sem perder o poder das ferramentas do sistema.

---

# Exemplo de uso

## Pacotes

```
aury instalar firefox
aury remover vlc
aury procurar steam
```

## Sistema

```
aury atualizar sistema
aury otimizar sistema
aury status
```

## Informações

```
aury ver cpu
aury ver memória
aury ver disco
aury ver gpu
aury ver processos
```

## Rede

```
aury ver ip
aury testar internet
aury ping google.com
```

## Arquivos

```
aury criar arquivo teste.txt
aury criar pasta projetos
aury copiar arquivo teste.txt backup.txt
aury mover arquivo teste.txt pasta/teste.txt
aury renomear arquivo teste.txt novo.txt
aury remover arquivo teste.txt
```

## Extras

```
aury reload
aury dev
```

---

# Exemplos com linguagem mais natural

A partir da versão **1.3.0**, a Aury aceita variações mais naturais de linguagem:

```
aury instala firefox
aury mostrar cpu
aury checar memória
aury criar teste.txt
aury ver cpu e mostrar memória
```

---

# Instalação

Clone o repositório:

```
git clone https://github.com/el-abni/aury.git
```

Entre na pasta do projeto:

```
cd aury
```

Instale a função no Fish:

```
cp bin/aury.fish ~/.config/fish/functions/aury.fish
```

Recarregue a função:

```
source ~/.config/fish/functions/aury.fish
```

Agora a Aury já pode ser usada no terminal.

---

# Filosofia do projeto

Aury busca tornar o terminal mais natural sem depender de inteligência artificial.

A evolução do projeto segue duas fases:

## Série 1.x

Fortalecer o parser interno e interpretação de comandos usando regras.

## Série 2.x

Adicionar suporte opcional a IA local para interpretar comandos mais complexos.

---

# Roadmap

### v1.3
Parser mais natural e expansão de sinônimos.

### v1.4
Melhorias de interpretação.

### v1.5
Melhor suporte a argumentos e caminhos complexos.

### v1.6
Melhorias de rede.

### v1.7
Melhorias de pacotes.

### v1.8
Fallback inteligente.

### v1.9
Refinamento geral.

### v2.0
Integração com IA local.

---

# Licença

Projeto distribuído sob a licença MIT.
