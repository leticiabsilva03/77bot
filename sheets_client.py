# sheets_client.py
import gspread
import logging
from datetime import datetime

# --- CONFIGURAÇÕES ---
# O caminho para o arquivo de credenciais
SERVICE_ACCOUNT_FILE = 'credentials/bot-integration-464319-78fb375d86ee.json'
# O nome da aba (worksheet) dentro de cada planilha. Assumimos que é o mesmo para todas.
WORKSHEET_NAME = 'Presentes'

def record_presence(sheet_name: str, nickname: str, event_name: str, post_time: datetime, image_url: str):
    """
    Registra a presença na planilha e aba corretas.
    A planilha a ser usada é determinada pelo parâmetro 'sheet_name'.
    """
    try:
        # Autentica com a conta de serviço
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
        
        # Abre a planilha correta usando o nome recebido como parâmetro
        sh = gc.open(sheet_name)
        
        # Acessa a aba específica dentro da planilha
        worksheet = sh.worksheet(WORKSHEET_NAME)

    except gspread.exceptions.SpreadsheetNotFound:
        logging.critical(f"PLANILHA NÃO ENCONTRADA: Verifique se o nome '{sheet_name}' está correto e se a planilha foi compartilhada com o e-mail do bot.")
        return False
    except gspread.exceptions.WorksheetNotFound:
        logging.critical(f"ABA NÃO ENCONTRADA: O bot não encontrou uma aba com o nome exato de '{WORKSHEET_NAME}' na planilha '{sheet_name}'. Verifique o nome da aba.")
        return False
    except Exception as e:
        logging.error(f"Um erro inesperado ocorreu ao acessar a planilha '{sheet_name}': {e}")
        return False
        
    try:
        # Formata a hora para um formato legível
        formatted_time = post_time.strftime('%d/%m/%Y %H:%M:%S')
        
        # Prepara a linha a ser adicionada. A ordem deve corresponder às colunas da sua planilha.
        row_to_add = [nickname, event_name, formatted_time, image_url]
        
        # Adiciona a nova linha ao final da planilha
        worksheet.append_row(row_to_add)
        
        logging.info(f"Presença para '{event_name}' registrada com sucesso em '{sheet_name}' para: {nickname}")
        return True
    except Exception as e:
        logging.error(f"Falha ao escrever na planilha '{sheet_name}' para o usuário {nickname}: {e}")
        return False