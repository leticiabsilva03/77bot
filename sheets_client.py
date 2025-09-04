import gspread
import logging
from datetime import datetime

# --- CONFIGURAÇÕES ---
SERVICE_ACCOUNT_FILE = 'credentials/bot-integration-464319-78fb375d86ee.json'
SPREADSHEET_NAME = 'CONTROLE PRESENÇA SA'

# Mapeamento das seções → colunas na planilha
SECTION_COLUMNS = {
    "wb_semana": ("H", "J"),       # Colunas H:J
    "wb_mes": ("K", "M"),          # Colunas K:M
    "praca_pico": ("O", "Q"),      # Colunas O:Q
    "eventos": ("T", "V"),         # Colunas T:V
    "torre": ("X", "Z")            # Colunas X:Z (nova seção Torre)
}

def record_presence(worksheet_name: str, dia: str, evento: str, hora: str, nick: str, section: str = None):
    """
    Registra a presença na aba (worksheet) correta da planilha principal.
    Usa append_row para evitar cálculos manuais de next_row.
    """
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
    except FileNotFoundError:
        logging.critical(f"Arquivo de credenciais não encontrado: {SERVICE_ACCOUNT_FILE}")
        return False
    except Exception as e:
        logging.error(f"Erro inesperado ao acessar planilha: {e}")
        return False

    try:
        row_to_add = [dia, evento, hora, nick]

        # Usa append_row que adiciona ao final da folha automaticamente
        worksheet.append_row(row_to_add, value_input_option='USER_ENTERED')

        logging.info(f"Presença para '{evento}' registrada com sucesso na aba '{worksheet_name}' para: {nick}")
        return True
    except Exception as e:
        logging.error(f"Falha ao escrever na aba '{worksheet_name}' para o usuário {nick}: {e}")
        return False
