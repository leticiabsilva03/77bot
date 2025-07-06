# log_manager.py
import discord
import logging

log_channel = None

def setup_log_channel(bot: discord.Client, channel_id: int):
    """
    Encontra e armazena o objeto do canal de log para uso futuro.
    """
    global log_channel
    try:
        channel = bot.get_channel(channel_id)
        if isinstance(channel, discord.TextChannel):
            log_channel = channel
            logging.info(f"Canal de log '{log_channel.name}' configurado com sucesso.")
        else:
            logging.error(f"O ID fornecido para o canal de log ({channel_id}) não corresponde a um canal de texto.")
    except Exception as e:
        logging.error(f"Não foi possível encontrar o canal de log com ID {channel_id}: {e}")

async def log_to_channel(title: str, description: str, color: discord.Color):
    """
    Envia uma mensagem de log formatada em um embed para o canal configurado.
    """
    if not log_channel:
        # Se o canal de log não foi configurado, apenas registra no console.
        logging.warning(f"Canal de log não configurado. Log não enviado para o Discord: {title} - {description}")
        return

    try:
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        await log_channel.send(embed=embed)
    except discord.Forbidden:
        logging.error(f"O bot não tem permissão para enviar mensagens no canal de log '{log_channel.name}'.")
    except Exception as e:
        logging.error(f"Falha ao enviar mensagem para o canal de log: {e}")