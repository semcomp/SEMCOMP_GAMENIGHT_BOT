# 🐍 chupacubo-v2
O **Chupa Cubo** é um bot de Telegram criado para auxiliar o **PET Computação USP** com diversas funções automatizadas, como gerenciamento de membros, controle de chave da salinha, consulta de bolsas, marcação em grupos e integração com planilhas do Google Sheets.

---

## 📌 Tecnologias Utilizadas
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Telebot](https://img.shields.io/badge/Telebot-API--Telegram-informational)
![Google Sheets](https://img.shields.io/badge/gspread-Google%20Sheets-green)
![pandas](https://img.shields.io/badge/pandas-Análise%20de%20Dados-yellow)
![requests](https://img.shields.io/badge/requests-Requisições%20HTTP-red)
![dotenv](https://img.shields.io/badge/dotenv-Variáveis%20de%20Ambiente-lightgrey)
![threading](https://img.shields.io/badge/threading-Multithreading-orange)

---

## 🚀 Funcionalidades
O bot oferece diversos comandos para facilitar a organização interna do PET:

### Comandos Disponíveis
| Comando | Descrição |
|---------|-----------|
| `/start` | Mensagem de boas-vindas |
| `/help` ou `/ajuda` | Lista todos os comandos e explicações |
| `/chave` | Registra que você pegou a chave na portaria |
| `/info_mensagem` | Mostra informações detalhadas sobre a mensagem recebida |

---

## 📂 Estrutura do Projeto

```
.github/
src/
├── modules/
│ ├── telegram.py # Classe principal do bot que recebe e responde as mensagens do Telegram
│ ├── sheets.py # Integração com Google Sheets, acessando as planilhas do PET
lib/
├── credentials.json # Credenciais do Bot para acesso aos Sheets
└── .env # Variáveis de ambiente, como credenciais
chupacubo.py # Main que inicia o bot
Dockerfile # Arquivo criador do Container com o Bot
Makefile # Automatização com make dos comandos de Docker
requirements.txt # Txt com as bibliotecas cuja instalação é necessária
```

## ⚙️ Execução

Atualmente, o Bot está rodando em um Docker, os comandos dockers estão compilados em quatro diretrizes do `Makefile`.

### Construir a imagem

```bash
make build
```

### Execução

```bash
make run
```

### Parar e remover o container

```bash
make stop
```

### Parar e remover o container, apagando a imagem

```bash
make clean
```
