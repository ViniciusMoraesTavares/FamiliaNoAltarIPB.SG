import os
import sys
import json

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath('.')

FAMILIAS_PATH = os.path.join(BASE_PATH, "dados", "familias.json")

def carregar_familias():
    try:
        with open(FAMILIAS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def salvar_familias(familias):
    try:
        with open(FAMILIAS_PATH, "w", encoding="utf-8") as f:
            json.dump(familias, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")