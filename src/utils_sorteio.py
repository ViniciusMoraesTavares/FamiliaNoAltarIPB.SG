import json
import os
import sys

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath('.')

dados_dir = os.path.join(BASE_PATH, "dados")

def salvar_sorteio(numero):
    dados = {"ultimo_sorteado": numero}
    os.makedirs(dados_dir, exist_ok=True)
    with open(os.path.join(dados_dir, "sorteio.json"), "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)