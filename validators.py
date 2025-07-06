# validators.py
import logging
from datetime import datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

TIMEZONE_STR = 'America/Sao_Paulo'

def find_active_event(message_time: datetime, event_list: list) -> dict | None:
    """
    Verifica a hora da mensagem contra uma lista de eventos fornecida.
    Retorna o dicionário do evento ativo, ou None se nenhum for encontrado.
    """
    try:
        target_tz = ZoneInfo(TIMEZONE_STR)
        local_time = message_time.astimezone(target_tz)
        current_weekday = local_time.weekday()
        current_time_obj = local_time.time()

        for event in event_list:
            if current_weekday in event["days"]:
                for start_time, end_time in event["slots"]:
                    # Lógica para eventos que viram a noite (ex: 23:00 - 01:00)
                    if start_time > end_time:
                        if current_time_obj >= start_time or current_time_obj <= end_time:
                            return event
                    # Lógica para eventos no mesmo dia
                    else:
                        if start_time <= current_time_obj <= end_time:
                            return event
        
        return None # Nenhum evento ativo encontrado

    except Exception as e:
        logging.error(f"Erro inesperado na validação de tempo: {e}")
        return None