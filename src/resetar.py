import random
import json
import os
import sys
from src.utils import carregar_familias, salvar_familias

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath('.')

sorteio_file_path = os.path.join(BASE_PATH, 'dados', 'sorteio.json')

def resetar_sorteio():
    familias = carregar_familias()

    for f in familias:
        f["sorteado"] = False

    numeros = list(range(1, len(familias) + 1))
    random.shuffle(numeros)
    for f, num in zip(familias, numeros):
        f["numero"] = num

    salvar_familias(familias)
    
    try:
        if not os.path.exists(sorteio_file_path):
            with open(sorteio_file_path, 'w') as sorteio_file:
                json.dump({"ultimo_sorteado": 0}, sorteio_file)
        else:
            with open(sorteio_file_path, 'r+') as sorteio_file:
                try:
                    data = json.load(sorteio_file)
                    data["ultimo_sorteado"] = 0
                    sorteio_file.seek(0)
                    json.dump(data, sorteio_file)
                    sorteio_file.truncate()
                except json.JSONDecodeError:
                    sorteio_file.seek(0)
                    json.dump({"ultimo_sorteado": 0}, sorteio_file)
    except Exception as e:
        print(f"Erro ao resetar o arquivo sorteio.json: {e}")