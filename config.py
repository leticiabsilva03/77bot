from datetime import time

# Dias da semana: 0=Seg, 1=Ter, 2=Qua, 3=Qui, 4=Sex, 5=Sáb, 6=Dom
ALL_DAYS = [0, 1, 2, 3, 4, 5, 6]

# ---------------------------
# Slots de World Boss (WB) + Praça/Pico
# ---------------------------
WB_SLOTS = [
    {"name": "WB 10:00 + Pico", "days": ALL_DAYS, "slots": [(time(9, 55), time(10, 35))]},
    {"name": "WB 12:00 + Praça", "days": ALL_DAYS, "slots": [(time(11, 55), time(12, 35))]},
    {"name": "WB 20:00",        "days": ALL_DAYS, "slots": [(time(19, 55), time(20, 35))]},
    {"name": "WB 22:00 + Pico", "days": ALL_DAYS, "slots": [(time(21, 55), time(22, 35))]},
    {"name": "WB 00:00 + Praça","days": ALL_DAYS, "slots": [(time(23, 55), time(0, 35))]},
]

# ---------------------------
# Eventos fixos (semanais)
# ---------------------------
EVENTOS_SLOTS = [
    {"name": "Krukan",          "days": [1], "slots": [(time(21, 45), time(22, 35))]},
    {"name": "Guerra de Vale",  "days": [2], "slots": [(time(22, 45), time(23, 35))]},
    {"name": "Defesa de Cristal","days": [3], "slots": [(time(22, 45), time(23, 35))]},
    {"name": "Saque do Castelo","days": [4], "slots": [(time(22, 45), time(23, 35))]},
]

# ---------------------------
# Evento Torre
# ---------------------------
TORRE_SLOTS = [
    {"name": "Torre 11:00", "days": ALL_DAYS, "slots": [(time(10, 55), time(11, 35))]},
    {"name": "Torre 17:00", "days": ALL_DAYS, "slots": [(time(16, 55), time(17, 35))]},
    {"name": "Torre 23:00", "days": ALL_DAYS, "slots": [(time(22, 55), time(23, 35))]},
]

# ---------------------------
# Eventos de Praça / Pico (somente os que NÃO coincidem com WB)
# ---------------------------
PRACA_PICO_SLOTS = [
    {"name": "Pico", "days": ALL_DAYS, "slots": [
        (time(1, 55), time(2, 35)),
        (time(7, 55), time(8, 35)),
        (time(12, 55), time(13, 35)),
        (time(18, 55), time(19, 35)),
    ]},
    {"name": "Praça", "days": ALL_DAYS, "slots": [
        (time(3, 55), time(4, 35)),
        (time(9, 55), time(10, 35)),
        (time(15, 55), time(16, 35)),
    ]},
]

# ---------------------------
# Configuração principal
# ---------------------------
CONFIG = {
    **{
        f"SOUTH AMERICA {server}": {
            "worksheet_name": f"SOUTH AMERICA {server}",
            "channels": {
                "wb": WB_SLOTS,
                "eventos": EVENTOS_SLOTS,
                "torre": TORRE_SLOTS,
                "praca_pico": PRACA_PICO_SLOTS,
            }
        }
        for server in [11, 12, 13, 14, 21, 22, 23, 31, 32, 33]
    }
}
