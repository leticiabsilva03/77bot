# sheets_client.py
import gspread
import logging
from datetime import datetime

# --- CONFIGURAÇÕES ---
SERVICE_ACCOUNT_FILE = 'credentials/bot-integration-464319-78fb375d86ee.json'
SPREADSHEET_NAME = 'CONTROLE PRESENÇA'

def record_presence(worksheet_name: str, dia: str, evento: str, hora: str, nick: str):
    """Registra a presença na aba (worksheet) correta da planilha principal."""
    try:
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
        sh = gc.open(SPREADSHEET_NAME)
        worksheet = sh.worksheet(worksheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        logging.critical(f"PLANILHA NÃO ENCONTRADA: Verifique se a planilha com o nome '{SPREADSHEET_NAME}' existe e foi compartilhada com o e-mail do bot.")
        return False
    except gspread.exceptions.WorksheetNotFound:
        logging.critical(f"ABA NÃO ENCONTRADA: O bot não encontrou uma aba com o nome exato de '{worksheet_name}' na planilha. Crie a aba ou corrija o nome na configuração.")
        return False
    except Exception as e:
        logging.error(f"Um erro inesperado ocorreu ao acessar a planilha/aba: {e}")
        return False
        
    try:
        # Novo formato de linha: DIA; EVENTO; HORA; NICK
        row_to_add = [dia, evento, hora, nick]
        
        # --- CORREÇÃO PRINCIPAL: Método de escrita mais robusto ---
        # Em vez de 'append_row', encontramos a próxima linha vazia baseada apenas na coluna A.
        # Isso ignora qualquer dado ou fórmula nas colunas de ranking.
        list_of_values = worksheet.col_values(1)  # Pega todos os valores da coluna A (DIA)
        next_row = len(list_of_values) + 1
        
        # Define o intervalo para atualizar (ex: A5:D5)
        update_range = f'A{next_row}:D{next_row}'
        
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
