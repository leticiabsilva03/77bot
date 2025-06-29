# main.py
import discord
from discord.ext import tasks
import os
import logging
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import datetime

import sheets_client
import validators

# --- CARREGAMENTO E CONFIGURAÇÃO INICIAL ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# --- CONFIGURAÇÕES GERAIS ---
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_CHANNEL_NAME = 'off-topic' # Nome do canal a ser monitorado

# --- CACHE EM MEMÓRIA ---
# A chave do cache agora é uma tupla (user_id, event_name) para permitir presença em múltiplos eventos.
posted_today_cache = set()

# --- INICIALIZAÇÃO DO BOT ---
bot = discord.Client(intents=intents)
target_channel = None # Variável global para armazenar o objeto do canal

# --- TAREFA AGENDADA PARA LIMPAR O CACHE ---
# Define a hora específica para o reset do cache
cache_reset_time = datetime.time(23, 59, tzinfo=ZoneInfo(validators.TIMEZONE_STR))

@tasks.loop(time=cache_reset_time)
async def clear_daily_cache():
    logging.info("Horário de reset atingido. Limpando o cache de presença diária.")
    posted_today_cache.clear()

# --- EVENTOS DO BOT ---
@bot.event
async def on_ready():
    """Chamado quando o bot se conecta."""
    global target_channel
    # Procura o canal 'off-topic' em todos os servidores onde o bot está
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=TARGET_CHANNEL_NAME)
        if channel:
            target_channel = channel
            logging.info(f"Bot conectado e monitorando o canal '{TARGET_CHANNEL_NAME}' no servidor '{guild.name}'")
            break
    
    if not target_channel:
        logging.error(f"Não foi possível encontrar o canal '{TARGET_CHANNEL_NAME}' em nenhum servidor.")

    clear_daily_cache.start()
    logging.info('------')

@bot.event
async def on_message(message: discord.Message):
    """Processa as mensagens para registro de presença."""
    if not target_channel or message.channel.id != target_channel.id or message.author.bot:
        return

    # 1. Valida se tem imagem
    if not validators.has_image_attachment(message):
        return

    # 2. Valida se está em um horário de evento e obtém o nome do evento
    event_name = validators.get_current_event(message.created_at)
    if not event_name:
        return

    # 3. Valida se o usuário já postou para ESTE evento específico hoje
    cache_key = (message.author.id, event_name)
    if cache_key in posted_today_cache:
        logging.warning(f"Usuário {message.author.display_name} já postou para o evento '{event_name}'. Post duplicado ignorado.")
        return

    # --- Se todas as validações passaram ---
    logging.info(f"Mensagem válida de '{message.author.display_name}' para o evento '{event_name}'. Processando...")
    
    attachment = message.attachments[0]
    message_time_in_timezone = message.created_at.astimezone(ZoneInfo(validators.TIMEZONE_STR))

    success = sheets_client.record_presence(
        nickname=message.author.display_name,
        event_name=event_name, # Passamos o nome do evento
        post_time=message_time_in_timezone,
        image_url=attachment.url
    )
    
    if success:
        posted_today_cache.add(cache_key)
        logging.info(f"Usuário {message.author.display_name} adicionado ao cache para o evento '{event_name}'.")

# --- INICIAR O BOT ---
if __name__ == "__main__":
    if not TOKEN:
        logging.critical("TOKEN do Discord não encontrado! Verifique seu arquivo .env")
    else:
        bot.run(TOKEN)