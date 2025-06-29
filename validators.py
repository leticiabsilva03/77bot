# validators.py
import logging
from datetime import time, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# --- CONFIGURAÇÕES DE VALIDAÇÃO ---
TIMEZONE_STR = 'America/Sao_Paulo'

# 0=Seg, 1=Ter, 2=Qua, 3=Qui, 4=Sex, 5=Sáb, 6=Dom
ALL_DAYS = [0, 1, 2, 3, 4, 5, 6]

# Estrutura de dados que define todos os eventos
EVENTS = [
    # Eventos Diários
    {"name": "WB 10:00", "days": ALL_DAYS, "start": time(10, 0), "end": time(10, 15)},
    {"name": "WB 12:00", "days": ALL_DAYS, "start": time(12, 0), "end": time(12, 15)},
    {"name": "WB 20:00", "days": ALL_DAYS, "start": time(20, 0), "end": time(20, 15)},
    {"name": "WB 22:00", "days": ALL_DAYS, "start": time(22, 0), "end": time(22, 15)},
    {"name": "WB 00:00", "days": ALL_DAYS, "start": time(0, 0), "end": time(0, 15)},
    # Eventos Semanais
    {"name": "Krukan", "days": [1], "start": time(20, 30), "end": time(20, 55)},       # Terça-feira
    {"name": "Guerra de Vale", "days": [2], "start": time(22, 15), "end": time(23, 0)}, # Quarta-feira
    {"name": "Defesa de Cristal", "days": [3], "start": time(22, 15), "end": time(23, 0)},# Quinta-feira
    {"name": "Saque do Castelo", "days": [4], "start": time(22, 15), "end": time(23, 0)}, # Sexta-feira
]

def get_current_event(message_time: datetime):
    """
    Verifica a data e hora da mensagem e retorna o evento correspondente, se houver.
    Retorna o nome do evento em caso de sucesso, ou None se não estiver em um horário de evento.
    """
    try:
        target_tz = ZoneInfo(TIMEZONE_STR)
        local_time = message_time.astimezone(target_tz)
        current_weekday = local_time.weekday()
        current_time_obj = local_time.time()

        for event in EVENTS:
            if current_weekday in event["days"]:
                if event["start"] <= current_time_obj <= event["end"]:
                    logging.info(f"Horário corresponde ao evento: {event['name']}")
                    return event["name"]
        
        # Se o loop terminar sem encontrar um evento
        logging.warning(f"Mensagem ignorada: fora do horário de qualquer evento ({local_time.strftime('%H:%M:%S')}).")
        return None

    except ZoneInfoNotFoundError:
        logging.error(f"Fuso horário '{TIMEZONE_STR}' não encontrado.")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado na validação de tempo: {e}")
        return None

def has_image_attachment(message):
    """Verifica se a mensagem contém um anexo que é uma imagem."""
    if not message.attachments:
        logging.warning(f"Mensagem de '{message.author.display_name}' ignorada: sem anexo.")
        return False
        
    attachment = message.attachments[0]
    if not attachment.content_type or not attachment.content_type.startswith('image/'):
        logging.warning(f"Mensagem de '{message.author.display_name}' ignorada: anexo não é uma imagem.")
        return False
        
    return True