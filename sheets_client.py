import gspread
import logging
from datetime import datetime

# --- CONFIGURAÇÕES ---
SERVICE_ACCOUNT_FILE = 'credentials/bot-integration-464319-78fb375d86ee.json'
SPREADSHEET_NAME = 'CONTROLE PRESENÇA'

# Mapeamento das seções → colunas na planilha
SECTION_COLUMNS = {
    "wb_semana": ("H", "J"),       # Colunas H:J
    "wb_mes": ("K", "M"),          # Colunas K:M
    "praca_pico": ("O", "Q"),      # Colunas O:Q
    "eventos": ("T", "V"),         # Colunas T:V
    "torre": ("X", "Z")            # Colunas X:Z (nova seção Torre)
}

def record_presence(worksheet_name: str, dia: str, evento: str, hora: str, nick: str, section: str = None):
    """Registra a presença na aba (worksheet) correta da planilha principal."""
    try:
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
        sh = gc.open(SPREADSHEET_NAME)
        worksheet = sh.worksheet(worksheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        logging.critical(f"PLANILHA NÃO ENCONTRADA: '{SPREADSHEET_NAME}'")
        return False
    except gspread.exceptions.WorksheetNotFound:
        logging.critical(f"ABA NÃO ENCONTRADA: '{worksheet_name}'")
        return False
    except Exception as e:
        logging.error(f"Erro inesperado ao acessar planilha: {e}")
        return False
        
    try:
        # Novo formato de linha: DIA; EVENTO; HORA; NICK
        row_to_add = [dia, evento, hora, nick]
        
        list_of_values = worksheet.col_values(2)  # Pega todos os valores da coluna A (DIA)
        next_row = len(list_of_values) + 1
        
        # Define o intervalo para atualizar (ex: A5:D5)
        update_range = f'B{next_row}:E{next_row}'
        
        worksheet.update(
            update_range,
            [row_to_add], # Os dados precisam estar dentro de uma lista
            value_input_option='USER_ENTERED'
        )
        
        logging.info(f"Presença para '{evento}' registrada com sucesso na aba '{worksheet_name}' para: {nick}")
        return True
    except Exception as e:
        logging.error(f"Falha ao escrever na aba '{worksheet_name}' para o usuário {nick}: {e}")
        return False
