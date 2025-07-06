# config.py
from datetime import time

# Dias da semana: 0=Seg, 1=Ter, 2=Qua, 3=Qui, 4=Sex, 5=Sáb, 6=Dom
ALL_DAYS = [0, 1, 2, 3, 4, 5, 6]
MON_TUE_THU_FRI = [0, 1, 3, 4]

# --- ESTRUTURA DE CONFIGURAÇÃO PRINCIPAL ---
# Mapeia NOME DA CATEGORIA -> NOME DA ABA (worksheet) e seus canais
CONFIG = {
    "NORTH AMERICA 44": {
        "worksheet_name": "NORTH AMERICA 44", # O nome da aba é o mesmo da categoria
        "channels": {
            "wb": [
                {"name": "WB 10:00 + Pico", "days": ALL_DAYS, "slots": [(time(10, 55), time(11, 15))]},
                {"name": "WB 12:00 + Praça", "days": ALL_DAYS, "slots": [(time(12, 55), time(13, 15))]},
                {"name": "WB 20:00", "days": ALL_DAYS, "slots": [(time(20, 55), time(21, 15))]},
                {"name": "WB 22:00 + Pico", "days": ALL_DAYS, "slots": [(time(22, 55), time(23, 15))]},
                {"name": "WB 00:00 + Praça", "days": ALL_DAYS, "slots": [(time(0, 55), time(1, 15))]},
            ],
            "praça-pico": [ # Nome do canal como no Discord, sem a barra
                {"name": "Pico", "days": ALL_DAYS, "slots": [(time(1, 55), time(2, 15)), (time(4, 55), time(5, 15)), (time(7, 55), time(8, 15)), (time(13, 55), time(14, 15)), (time(16, 55), time(17, 15)), (time(19, 55), time(20, 15))]},
                {"name": "Praça", "days": ALL_DAYS, "slots": [(time(3, 55), time(4, 15)), (time(6, 55), time(7, 15)), (time(9, 55), time(10, 15)), (time(15, 55), time(16, 15)), (time(18, 55), time(19, 15)), (time(21, 55), time(22, 15))]},
            ],
            "eventos": [
                {"name": "Krukan/Nerkan/Turkan/Utukan", "days": MON_TUE_THU_FRI, "slots": [(time(23, 55), time(0, 15, 59))]}, # Evento que vira a noite
                {"name": "Guerra de Vale", "days": [2], "slots": [(time(23, 45), time(0, 10, 59))]},
                {"name": "Defesa de Cristal", "days": [3], "slots": [(time(23, 45), time(0, 10, 59))]},
                {"name": "Saque do Castelo", "days": [4], "slots": [(time(23, 45), time(0, 10, 59))]},
            ],
        }
    },
    **{
        f"EUROPE {server}": {
            "worksheet_name": f"EUROPE {server}",
            "channels": {
                "wb": [
                    {"name": "WB 10:00 + Pico", "days": ALL_DAYS, "slots": [(time(4, 55), time(5, 15))]},
                    {"name": "WB 12:00 + Praça", "days": ALL_DAYS, "slots": [(time(6, 55), time(7, 15))]},
                    {"name": "WB 20:00", "days": ALL_DAYS, "slots": [(time(14, 55), time(15, 15))]},
                    {"name": "WB 22:00 + Pico", "days": ALL_DAYS, "slots": [(time(16, 55), time(17, 15))]},
                    {"name": "WB 00:00 + Praça", "days": ALL_DAYS, "slots": [(time(18, 55), time(19, 15))]},
                ],
                "praça-pico": [
                    {"name": "Pico", "days": ALL_DAYS, "slots": [(time(19, 55), time(20, 15)), (time(22, 55), time(23, 15)), (time(1, 55), time(2, 15)), (time(7, 55), time(8, 15)), (time(10, 55), time(11, 15)), (time(13, 55), time(14, 15))]},
                    {"name": "Praça", "days": ALL_DAYS, "slots": [(time(21, 55), time(22, 15)), (time(0, 55), time(1, 15)), (time(3, 55), time(4, 15)), (time(9, 55), time(10, 15)), (time(12, 55), time(13, 15)), (time(15, 55), time(16, 15))]},
                ],
                "eventos-juja" if server == 14 else "eventos": [
                    {"name": "Krukan/Nerkan/Turkan/Utukan", "days": MON_TUE_THU_FRI, "slots": [(time(17, 55), time(18, 15))]},
                    {"name": "Guerra de Vale", "days": [2], "slots": [(time(17, 45), time(18, 10))]},
                    {"name": "Defesa de Cristal", "days": [3], "slots": [(time(17, 45), time(18, 10))]},
                    {"name": "Saque do Castelo", "days": [4], "slots": [(time(17, 45), time(18, 10))]},
                ],
            }
        }
        for server in [43, 14]
    },
    **{
        f"SOUTH AMERICA {server}": {
            "worksheet_name": f"SOUTH AMERICA {server}",
            "channels": {
                "wb": [
                    {"name": "WB 10:00", "days": ALL_DAYS, "slots": [(time(9, 55), time(10, 15))]},
                    {"name": "WB 12:00", "days": ALL_DAYS, "slots": [(time(11, 55), time(12, 15))]},
                    {"name": "WB 20:00", "days": ALL_DAYS, "slots": [(time(13, 55), time(20, 15))]},
                    {"name": "WB 22:00", "days": ALL_DAYS, "slots": [(time(21, 55), time(22, 15))]},
                    {"name": "WB 00:00", "days": ALL_DAYS, "slots": [(time(23, 55), time(0, 15, 59))]},
                ],
                "eventos": [
                    {"name": "Krukan", "days": [1], "slots": [(time(21, 45), time(22, 10))]}, # Horário assumido
                    {"name": "Guerra de Vale", "days": [2], "slots": [(time(22, 45), time(23, 10))]},
                    {"name": "Defesa de Cristal", "days": [3], "slots": [(time(22, 45), time(23, 10))]},
                    {"name": "Saque do Castelo", "days": [4], "slots": [(time(22, 45), time(23, 10))]},
                ],
            }
        }
        for server in [23, 43, 63, 71]
    }
}