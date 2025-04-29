import json
import os
import sys

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath('.')

DADOS_PATH = os.path.join(BASE_PATH, "dados", "familias.json")

def contar_familias():
    if not os.path.exists(DADOS_PATH):
        return 0
    with open(DADOS_PATH, "r", encoding="utf-8") as f:
        familias = json.load(f)
        return len(familias)