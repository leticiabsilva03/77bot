# 77bot - Automacao de Presenca para Discord

O **77bot** é um bot para Discord desenvolvido em Python, projetado para automatizar o registro de presença em eventos de um servidor. Ele monitora canais de texto específicos, analisa mensagens com um formato predefinido que contenham anexos de imagem e registra os dados (nickname, horário, evento e URL da imagem) em uma planilha do Google Sheets de forma silenciosa e eficiente.

## 📈 Principais Funcionalidades

* **🔍 Monitoramento de Canais**: Escuta ativamente por novas mensagens nos canais designados.
* **📅 Extração de Dados**: Utiliza regex para extrair o nickname e o horário da mensagem.
* **📷 Validação de Anexo**: Aceita apenas mensagens com anexos de imagem, salvando a URL da imagem.
* **⏰ Lógica de Eventos Baseada em Tempo**: Associa presenças a eventos com base no horário da mensagem, usando fuso horário BRT.
* **✨ Gerenciamento de Eventos Especiais**: Lida com eventos semanais que se sobrepõem à programação.
* **🌈 Operação Silenciosa**: Sem respostas nos canais, mantendo a limpeza do servidor.
* **📄 Integração com Google Sheets**: Registra dados automaticamente em uma planilha.

## 🧪 Tecnologias Utilizadas

* **Linguagem**: Python 3.9+
* **Discord API**: `discord.py`
* **Google API**: `google-api-python-client`, `google-auth-oauthlib`
* **Variáveis de Ambiente**: `python-dotenv`
* **Fuso Horário**: `zoneinfo`

## ⚙️ Configuração e Instalação

### 1. Pré-requisitos

* Python 3.9 ou superior
* Conta no Discord para criar aplicações
* Conta Google com acesso ao Google Cloud Console

### 2. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/77bot.git
cd 77bot
```

### 3. Ambiente Virtual e Dependências

```bash
python -m venv venv
# Ativar
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
# Instalar dependências
pip install -r requirements.txt
```

### 4. Configuração do Bot no Discord

* Crie uma aplicação em [https://discord.com/developers/applications](https://discord.com/developers/applications)
* Na aba **Bot**, clique em **Add Bot** e gere o token
* Ative:

  * SERVER MEMBERS INTENT
  * MESSAGE CONTENT INTENT

### 5. Configuração da API do Google Sheets

1. Crie um projeto no Google Cloud Console
2. Ative a "Google Sheets API"
3. Crie uma conta de serviço com papel de **Editor**
4. Gere e baixe a chave JSON (mova para `credentials/`)
5. Compartilhe sua planilha com o e-mail da conta de serviço

### 6. Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto:

```ini
DISCORD_TOKEN="SEU_TOKEN_DO_DISCORD"
GOOGLE_SHEET_ID="ID_DA_SUA_PLANILHA"
GOOGLE_APPLICATION_CREDENTIALS="credentials/seu-arquivo.json"
```

### 7. Convidar o Bot para o Servidor

* Use o **OAuth2 URL Generator** para gerar um link com os escopos `bot` e `applications.commands`
* Permissões recomendadas:

  * View Channels
  * Read Message History

## ▶️ Executar o Bot

```bash
python main.py
```

## 📁 Estrutura Sugerida do Projeto

```
77bot/
├── credentials/
│   └── seu-arquivo-de-credenciais.json
├── venv/
├── .env
├── .gitignore
├── main.py                # Lógica principal
├── sheets_client.py       # Integração com Google Sheets
└── requirements.txt
```

Sinta-se à vontade para contribuir com melhorias ou abrir issues!

> Feito com ❤ por Leticia
