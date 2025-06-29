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
intents.guilds = True

# --- CONFIGURAÇÕES GERAIS ---
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_CHANNEL_NAME = 'off-topic'

# --- CACHE EM MEMÓRIA ---
posted_today_cache = set()

# --- INICIALIZAÇÃO DO BOT ---
bot = discord.Client(intents=intents)
target_channel = None

# --- TAREFA AGENDADA PARA LIMPAR O CACHE ---
cache_reset_time = datetime.time(23, 59, tzinfo=ZoneInfo(validators.TIMEZONE_STR))
@tasks.loop(time=cache_reset_time)
async def clear_daily_cache():
    logging.info("Horário de reset atingido. Limpando o cache de presença diária.")
    posted_today_cache.clear()

# --- FUNÇÃO CENTRAL DE PROCESSAMENTO ---
async def process_presence_message(message: discord.Message):
    global target_channel
    if not target_channel or message.channel.id != target_channel.id or message.author.bot:
        return

    # 1. Valida a mensagem e o horário
    is_valid_time, result = validators.validate_presence_message(message)
    
    if not is_valid_time:
        # Se a validação de anexo ou horário falhou, envia o motivo via DM
        try:
            await message.author.send(f"Olá! Sua postagem no canal #{target_channel.name} não pôde ser registrada. Motivo: {result}")
            logging.warning(f"DM enviada para {message.author.display_name} com o motivo: {result}")
        except discord.Forbidden:
            logging.error(f"Falha ao enviar DM para {message.author.display_name}. O usuário pode ter DMs desativadas.")
        return

    event_name = result # Se a validação passou, o resultado é o nome do evento

    # 2. Valida se o usuário já postou para este evento (verificação de duplicata)
    cache_key = (message.author.id, event_name)
    if cache_key in posted_today_cache:
        error_msg = f"Você já registrou presença para o evento '{event_name}' hoje."
        try:
            await message.author.send(f"Olá! Sua postagem no canal #{target_channel.name} não pôde ser registrada. Motivo: {error_msg}")
            logging.warning(f"DM de post duplicado enviada para {message.author.display_name}.")
        except discord.Forbidden:
            logging.error(f"Falha ao enviar DM de post duplicado para {message.author.display_name}.")
        return

    # --- Se todas as validações passaram, registra e reage ---
    logging.info(f"Mensagem válida de '{message.author.display_name}' para o evento '{event_name}'. Processando...")
    
    message_time_in_timezone = message.created_at.astimezone(ZoneInfo(validators.TIMEZONE_STR))

    success = sheets_client.record_presence(
        nickname=message.author.display_name,
        event_name=event_name,
        post_time=message_time_in_timezone,
        image_url=message.attachments[0].url
    )
    
    if success:
        # Adiciona a reação de sucesso na mensagem original
        await message.add_reaction("✅")
        # Adiciona ao cache
        posted_today_cache.add(cache_key)
        logging.info(f"Usuário {message.author.display_name} adicionado ao cache para o evento '{event_name}'.")

# --- EVENTOS DO BOT (on_ready, on_message, on_message_edit) ---
# ... (o resto do seu arquivo main.py continua igual)
@bot.event
async def on_ready():
    global target_channel
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
    await process_presence_message(message)

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    await process_presence_message(after)

# --- INICIAR O BOT ---
if __name__ == "__main__":
    if not TOKEN:
        logging.critical("TOKEN do Discord não encontrado! Verifique seu arquivo .env")
    else:
        bot.run(TOKEN)