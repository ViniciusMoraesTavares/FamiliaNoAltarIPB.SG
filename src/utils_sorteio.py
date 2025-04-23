import json
import os

def salvar_sorteio(numero):
    dados = {"ultimo_sorteado": numero}
    os.makedirs("dados", exist_ok=True)
    with open("dados/sorteio.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
