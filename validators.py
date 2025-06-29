# validators.py
import discord
import logging
from datetime import time, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# --- CONFIGURAÇÕES DE VALIDAÇÃO ---
TIMEZONE_STR = 'America/Sao_Paulo'
ALL_DAYS = [0, 1, 2, 3, 4, 5, 6] # 0=Seg, 6=Dom
EVENTS = [
    # Eventos Diários
    {"name": "WB 10:00", "days": ALL_DAYS, "start": time(10, 0), "end": time(10, 15)},
    {"name": "WB 12:00", "days": ALL_DAYS, "start": time(11, 0), "end": time(12, 15)},
    {"name": "WB 20:00", "days": ALL_DAYS, "start": time(20, 0), "end": time(20, 15)},
    {"name": "WB 22:00", "days": ALL_DAYS, "start": time(22, 0), "end": time(22, 15)},
    {"name": "WB 00:00", "days": ALL_DAYS, "start": time(0, 0), "end": time(0, 15)},
    # Eventos Semanais
    {"name": "Krukan", "days": [1], "start": time(20, 30), "end": time(20, 55)},
    {"name": "Guerra de Vale", "days": [2], "start": time(22, 15), "end": time(23, 0)},
    {"name": "Defesa de Cristal", "days": [3], "start": time(22, 15), "end": time(23, 0)},
    {"name": "Saque do Castelo", "days": [4], "start": time(22, 15), "end": time(23, 0)},
]

def validate_presence_message(message: discord.Message) -> tuple[bool, str | None]:
    """
    Valida a mensagem de presença.
    Retorna (True, event_name) em caso de sucesso.
    Retorna (False, error_message) em caso de falha.
    """
    # 1. Validação de anexo
    if not message.attachments or not message.attachments[0].content_type.startswith('image/'):
        return (False, "Você precisa enviar uma mensagem com uma imagem (print) para registrar a presença.")

    # 2. Validação de horário
    try:
        target_tz = ZoneInfo(TIMEZONE_STR)
        local_time = message.created_at.astimezone(target_tz)
        current_weekday = local_time.weekday()
        current_time_obj = local_time.time()

        for event in EVENTS:
            if current_weekday in event["days"]:
                if event["start"] <= current_time_obj <= event["end"]:
                    # Horário válido, retorna o nome do evento
                    return (True, event["name"])
        
        # Se o loop terminar, não encontrou evento válido.
        return (False, f"Sua postagem às {local_time.strftime('%H:%M')} está fora do horário de qualquer evento ativo.")

    except Exception as e:
        logging.error(f"Erro inesperado na validação de tempo: {e}")
        return (False, "Ocorreu um erro interno ao verificar o horário, por favor, contate um administrador.")