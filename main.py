# main.py
import discord
from discord.ext import commands, tasks
import os
import logging
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import datetime

# --- IMPORTS ---
import cache_manager 
import log_manager
from config import CONFIG
import sheets_client
import validators

# --- CONFIGURAÇÃO INICIAL ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
TOKEN = os.getenv('DISCORD_TOKEN')
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID')) if os.getenv('LOG_CHANNEL_ID') else None

bot = commands.Bot(command_prefix="!", intents=intents)

# --- CACHE E MAPAS GLOBAIS ---
posted_today_cache = cache_manager.load_cache()
channel_config_map = {}

# --- TAREFAS AGENDADAS ---
cache_reset_time = datetime.time(0, 25, tzinfo=ZoneInfo(validators.TIMEZONE_STR))
@tasks.loop(time=cache_reset_time)
async def clear_daily_cache():
    logging.info("Horário de reset atingido (00:25). Limpando o cache de presença diária.")
    posted_today_cache.clear()
    cache_manager.save_cache(posted_today_cache)
    # Limpa também o cache de jogadores do Cog de relatórios
    reports_cog = bot.get_cog('ReportsCog')
    if reports_cog:
        reports_cog.clear_player_cache()


@tasks.loop(minutes=5)
async def save_cache_periodically():
    logging.info("Salvando cache de presença no arquivo...")
    cache_manager.save_cache(posted_today_cache)

# --- FUNÇÃO CENTRAL DE PROCESSAMENTO ---
async def process_presence_message(message: discord.Message):
    if message.channel.id not in channel_config_map:
        return

    channel_config = channel_config_map[message.channel.id]
    
    active_event = validators.find_active_event(message.created_at, channel_config["events"])
    if not active_event:
        # Apenas para este caso, não enviamos DM para não poluir os usuários
        # que conversam normalmente fora do horário.
        return

    # Validação de anexo
    if not message.attachments or not message.attachments[0].content_type.startswith('image/'):
        error_msg = "Você precisa enviar uma mensagem com uma imagem (print) para registrar a presença."
        try:
            await message.author.send(f"Olá! Sua postagem no canal #{message.channel.name} não pôde ser registrada. Motivo: {error_msg}")
        except discord.Forbidden:
            pass # Ignora se o usuário tiver DMs fechadas
        await log_manager.log_to_channel(
            title="⚠️ Post Ignorado: Sem Imagem",
            description=f"**Autor:** {message.author.mention}\n**Canal:** {message.channel.mention}",
            color=discord.Color.orange()
        )
        return

    # Validação de menção
    if not message.mentions:
        error_msg = "Você precisa marcar o usuário (@nick) que está recebendo a presença na mensagem."
        try:
            await message.author.send(f"Olá! Sua postagem no canal #{message.channel.name} não pôde ser registrada. Motivo: {error_msg}")
        except discord.Forbidden:
            pass
        await log_manager.log_to_channel(
            title="⚠️ Post Ignorado: Sem Menção",
            description=f"**Autor:** {message.author.mention}\n**Canal:** {message.channel.mention}\n**Motivo:** A mensagem não continha uma menção `@user`.",
            color=discord.Color.orange()
        )
        return
    
    mentioned_user = message.mentions[0]
    nick_to_save = mentioned_user.display_name
    
    # Validação de duplicata
    cache_key = (mentioned_user.id, active_event['name'], message.channel.id)
    if cache_key in posted_today_cache:
        error_msg = f"A presença para '{nick_to_save}' no evento '{active_event['name']}' já foi registrada hoje."
        try:
            await message.author.send(f"Olá! Sua postagem no canal #{message.channel.name} não pôde ser registrada. Motivo: {error_msg}")
        except discord.Forbidden:
            pass
        await log_manager.log_to_channel(
            title="❌ Post Ignorado: Duplicado",
            description=f"**Autor:** {message.author.mention}\n**Jogador Mencionado:** {mentioned_user.mention}\n**Evento:** {active_event['name']}\n**Canal:** {message.channel.mention}",
            color=discord.Color.red()
        )
        return

    # Se todas as validações passaram
    logging.info(f"Processando presença para '{nick_to_save}' no evento '{active_event['name']}'")
    
    local_time = message.created_at.astimezone(ZoneInfo(validators.TIMEZONE_STR))
    
    success = sheets_client.record_presence(
        worksheet_name=channel_config["worksheet_name"],
        dia=local_time.strftime('%d/%m/%Y'),
        evento=active_event['name'],
        hora=local_time.strftime('%H:%M:%S'),
        nick=nick_to_save
    )
    
    if success:
        await message.add_reaction("✅")
        posted_today_cache.add(cache_key)
        
        # Atualiza o cache do autocomplete dinamicamente
        reports_cog = bot.get_cog('ReportsCog')
        if reports_cog:
            reports_cog.add_player_to_cache(channel_config["worksheet_name"], nick_to_save)
            
        await log_manager.log_to_channel(
            title="✅ Presença Registrada com Sucesso",
            description=f"**Jogador:** {nick_to_save}\n**Evento:** {active_event['name']}\n**Divisão:** {channel_config['worksheet_name']}\n**Registrado por:** {message.author.mention}",
            color=discord.Color.green()
        )

# --- EVENTOS DO BOT ---
@bot.event
async def on_ready():
    global channel_config_map
    logging.info(f"Bot conectado como {bot.user.name}")
    
    if LOG_CHANNEL_ID:
        log_manager.setup_log_channel(bot, LOG_CHANNEL_ID)
    else:
        logging.warning("Nenhum ID de canal de log foi fornecido no arquivo .env. O log no Discord está desativado.")

    if not bot.guilds:
        logging.critical("O bot não está em nenhum servidor!")
        return
        
    guild = bot.guilds[0]
    logging.info(f"Verificando configurações para o servidor: '{guild.name}'")

    for category_name, category_config in CONFIG.items():
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            logging.error(f"AVISO: Categoria '{category_name}' não encontrada.")
            continue
        
        for channel_name, events in category_config["channels"].items():
            channel = discord.utils.get(category.text_channels, name=channel_name)
            if channel:
                channel_config_map[channel.id] = {
                    "worksheet_name": category_config["worksheet_name"],
                    "events": events
                }
                logging.info(f"OK: Monitorando canal '{channel.name}' -> Aba '{category_config['worksheet_name']}'")
            else:
                logging.error(f"AVISO: Canal '{channel_name}' não foi encontrado na categoria '{category_name}'.")

    if not clear_daily_cache.is_running():
        clear_daily_cache.start()
    if not save_cache_periodically.is_running():
        save_cache_periodically.start()

    try:
        synced = await bot.tree.sync()
        logging.info(f"Sincronizados {len(synced)} comandos de barra.")
    except Exception as e:
        logging.error(f"Falha ao sincronizar comandos: {e}")

    logging.info('------ Iniciação completa, aguardando mensagens ------')

@bot.listen('on_message')
async def message_listener(message: discord.Message):
    if message.author.bot: return
    await process_presence_message(message)

@bot.listen('on_message_edit')
async def edit_listener(before: discord.Message, after: discord.Message):
    if after.author.bot: return
    await process_presence_message(after)

# --- INICIAR O BOT ---
async def main():
    async with bot:
        await bot.load_extension('cogs.reports_cog')
        await bot.start(TOKEN)

if __name__ == "__main__":
    if not TOKEN:
        logging.critical("TOKEN do Discord não encontrado!")
    else:
        import asyncio
        asyncio.run(main())
