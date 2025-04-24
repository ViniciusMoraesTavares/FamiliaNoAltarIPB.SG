import json
import os

DADOS_PATH = "dados/familias.json"

def contar_familias():
    if not os.path.exists(DADOS_PATH):
        return 0
    with open(DADOS_PATH, "r", encoding="utf-8") as f:
        familias = json.load(f)
        return len(familias)