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
    try:
        with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Arquivo de famílias não encontrado.")
        return []
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo de famílias.")
        return []

def salvar_familias(familias):
    try:
        with open(CAMINHO_DADOS, "w", encoding="utf-8") as f:
            json.dump(familias, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar as famílias: {e}")

def salvar_sorteio(ultima_familia):
    try:
        with open(CAMINHO_SORTEIO, "w", encoding="utf-8") as f:
            json.dump({"ultimo_sorteado": ultima_familia["numero"]}, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar sorteio: {e}")

def sortear_familia():
    familias = carregar_familias()
    if not familias:
        return None
        
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