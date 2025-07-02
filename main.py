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

# --- CONFIGURAÇÃO CENTRAL (NOVO!) ---
TOKEN = os.getenv('DISCORD_TOKEN')

# Nome exato do canal de texto que existirá dentro de cada categoria
TARGET_CHANNEL_NAME_IN_CATEGORY = "presença"

# Mapeamento das divisões: NOME DA CATEGORIA -> NOME DA PLANILHA
# ATENÇÃO: Os nomes das categorias e planilhas aqui devem ser EXATAMENTE como no Discord/Google.
DIVISION_CONFIG = {
    "SOUTH AMERICA 23": "Controle SA23 - Presença",
    "SOUTH AMERICA 43": "Controle SA43 - Presença",
    "SOUTH AMERICA 63": "Controle SA63 - Presença",
    "SOUTH AMERICA 71": "Controle SA71 - Presença",
}

# --- CACHE E VARIÁVEIS GLOBAIS ---
posted_today_cache = set()
channel_to_sheet_map = {} # Mapeia ID do canal para nome da planilha

bot = discord.Client(intents=intents)

# --- TAREFA AGENDADA ---
cache_reset_time = datetime.time(23, 59, tzinfo=ZoneInfo(validators.TIMEZONE_STR))
@tasks.loop(time=cache_reset_time)
async def clear_daily_cache():
    logging.info("Horário de reset atingido. Limpando o cache de presença diária.")
    posted_today_cache.clear()

# --- FUNÇÃO CENTRAL DE PROCESSAMENTO ---
async def process_presence_message(message: discord.Message):
    if message.channel.id not in channel_to_sheet_map:
        return

    target_sheet_name = channel_to_sheet_map[message.channel.id]

    is_valid_time, result = validators.validate_presence_message(message)
    if not is_valid_time:
        try:
            await message.author.send(f"Olá! Sua postagem no canal #{message.channel.name} não pôde ser registrada. Motivo: {result}")
        except discord.Forbidden:
            pass
        return

    event_name = result
    # O cache agora inclui o ID do canal para diferenciar presenças em diferentes divisões
    cache_key = (message.author.id, event_name, message.channel.id)
    if cache_key in posted_today_cache:
        error_msg = f"Você já registrou presença para o evento '{event_name}' na divisão do canal #{message.channel.name}."
        try:
            await message.author.send(f"Olá! Sua postagem não pôde ser registrada. Motivo: {error_msg}")
        except discord.Forbidden:
            pass
        return

    logging.info(f"Mensagem válida de '{message.author.display_name}' para '{event_name}' no canal '{message.channel.name}'.")
    
    success = sheets_client.record_presence(
        sheet_name=target_sheet_name,
        nickname=message.author.display_name,
        event_name=event_name,
        post_time=message.created_at.astimezone(ZoneInfo(validators.TIMEZONE_STR)),
        image_url=message.attachments[0].url
    )
    
    if success:
        await message.add_reaction("✅")
        posted_today_cache.add(cache_key)

# --- EVENTOS DO BOT ---
@bot.event
async def on_ready():
    global channel_to_sheet_map
    logging.info(f"Bot conectado como {bot.user.name}")

    # Assumindo que o bot está em apenas um servidor
    if not bot.guilds:
        logging.critical("O bot não está em nenhum servidor!")
        return
        
    guild = bot.guilds[0]
    logging.info(f"Verificando canais no servidor: '{guild.name}'")

    for category_name, sheet_name in DIVISION_CONFIG.items():
        # Passo 1: Encontrar a categoria pelo nome
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            logging.error(f"AVISO: Categoria '{category_name}' não foi encontrada no servidor.")
            continue

        # Passo 2: Encontrar o canal 'Presença' DENTRO da categoria encontrada
        channel = discord.utils.get(category.text_channels, name=TARGET_CHANNEL_NAME_IN_CATEGORY)
        if channel:
            channel_to_sheet_map[channel.id] = sheet_name
            logging.info(f"OK: Monitorando canal '{channel.name}' na categoria '{category.name}' -> Planilha '{sheet_name}'")
        else:
            logging.error(f"AVISO: Canal '{TARGET_CHANNEL_NAME_IN_CATEGORY}' não foi encontrado na categoria '{category_name}'.")
    
    clear_daily_cache.start()
    logging.info('------ Iniciação completa, aguardando mensagens ------')

# Os eventos de mensagem continuam os mesmos
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot: return
    await process_presence_message(message)

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if after.author.bot: return
    await process_presence_message(after)

# --- INICIAR O BOT ---
if __name__ == "__main__":
    if not TOKEN:
        logging.critical("TOKEN do Discord não encontrado!")
    else:
        bot.run(TOKEN)