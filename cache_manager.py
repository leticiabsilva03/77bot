# cache_manager.py
import json
import logging

CACHE_FILE = "presence_cache.json"

def load_cache() -> set:
    """
    Carrega o cache de um arquivo JSON no início.
    Se o arquivo não existir, retorna um cache vazio.
    """
    try:
        with open(CACHE_FILE, 'r') as f:
            # JSON não salva tuplas, então convertemos as listas de volta para tuplas
            list_of_lists = json.load(f)
            return {tuple(item) for item in list_of_lists}
    except FileNotFoundError:
        logging.info("Arquivo de cache não encontrado. Iniciando com um cache vazio.")
        return set()
    except json.JSONDecodeError:
        logging.warning("Arquivo de cache corrompido. Iniciando com um cache vazio.")
        return set()

def save_cache(cache_to_save: set):
    """
    Salva o cache atual em um arquivo JSON.
    Converte as tuplas em listas para serem compatíveis com JSON.
    """
    try:
        with open(CACHE_FILE, 'w') as f:
            list_of_lists = [list(item) for item in cache_to_save]
            json.dump(list_of_lists, f)
    except Exception as e:
        logging.error(f"Falha ao salvar o cache no arquivo: {e}")