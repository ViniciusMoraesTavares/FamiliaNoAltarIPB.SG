# src/sorteio.py

import json
import random

CAMINHO_DADOS = "dados/familias.json"
CAMINHO_SORTEIO = "dados/sorteio.json"

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
        return None  # Todas as famílias já foram sorteadas

    sorteada = random.choice(disponiveis)
    sorteada["sorteado"] = True

    # Atualiza a lista de famílias
    for i, f in enumerate(familias):
        if f["id"] == sorteada["id"]:
            familias[i] = sorteada
            break

    salvar_familias(familias)
    salvar_sorteio(sorteada)

    return sorteada
