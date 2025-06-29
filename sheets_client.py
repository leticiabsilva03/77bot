# sheets_client.py
import gspread
import logging
from datetime import datetime

# --- CONFIGURAÇÕES ---
SERVICE_ACCOUNT_FILE = 'credentials/bot-integration-464319-78fb375d86ee.json'
SHEET_NAME = '77 Team - Presença'
WORKSHEET_NAME = 'Presentes' # O nome da aba específica

def record_presence(nickname: str, event_name: str, post_time: datetime, image_url: str):
    """Registra a presença, incluindo o nome do evento, em uma nova linha."""
    try:
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
        sh = gc.open(SHEET_NAME)
        worksheet = sh.worksheet(WORKSHEET_NAME)
    except Exception as e:
        logging.error(f"Erro ao acessar a planilha/aba '{WORKSHEET_NAME}': {e}")
        return False
        
    try:
        # Formata a data e hora para um formato legível
        formatted_time = post_time.strftime('%d/%m/%Y %H:%M:%S')
        
        # A ordem deve ser: Nickname, Evento, Horário, URL
        row_to_add = [nickname, event_name, formatted_time, image_url]
        worksheet.append_row(row_to_add)
        logging.info(f"Presença para o evento '{event_name}' registrada com sucesso para: {nickname}")
        return True
    except Exception as e:
        logging.error(f"Falha ao escrever na planilha para o usuário {nickname}: {e}")
        return False