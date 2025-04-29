import os
import sys
import json
import random

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath('.')

CAMINHO_DADOS = os.path.join(BASE_PATH, "dados", "familias.json")
CAMINHO_SORTEIO = os.path.join(BASE_PATH, "dados", "sorteio.json")

def carregar_familias():
    with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_familias(familias):
    with open(CAMINHO_DADOS, "w", encoding="utf-8") as f:
        json.dump(familias, f, indent=4, ensure_ascii=False)

def salvar_sorteio(ultima_familia):
    with open(CAMINHO_SORTEIO, "w", encoding="utf-8") as f:
        json.dump({"ultimo_sorteado": ultima_familia["numero"]}, f, indent=4, ensure_ascii=False)

def sortear_familia():
    familias = carregar_familias()
    disponiveis = [f for f in familias if not f.get("sorteado", False)]

    if not disponiveis:
        return None 

    sorteada = random.choice(disponiveis)
    sorteada["sorteado"] = True

    for i, f in enumerate(familias):
        if f["id"] == sorteada["id"]:
            familias[i] = sorteada
            break

    salvar_familias(familias)
    salvar_sorteio(sorteada)

    return sorteada