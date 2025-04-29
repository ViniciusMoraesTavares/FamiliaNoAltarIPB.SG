import json
import os
import shutil
import random
import sys
import logging
from uuid import uuid4

# Configuração de logging (pode ser adaptado para exibir na interface se quiser)
logging.basicConfig(level=logging.INFO)

def get_resource_path(*paths):
    """Retorna o caminho absoluto ao recurso, considerando empacotamento."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base_path, *paths)

class DataManager:
    _instance = None
    _familias_cache = None
    _ultimo_sorteio_cache = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.familias_file = get_resource_path("dados", "familias.json")
        self.sorteio_file = get_resource_path("dados", "sorteio.json")

        os.makedirs(get_resource_path("dados"), exist_ok=True)
        os.makedirs(get_resource_path("imagens", "familias"), exist_ok=True)

    def carregar_familias(self, force_reload=False):
        if self._familias_cache is not None and not force_reload:
            return self._familias_cache

        try:
            if not os.path.exists(self.familias_file):
                self._familias_cache = []
                return []

            with open(self.familias_file, "r", encoding="utf-8") as f:
                dados = json.load(f)
                # Validação mínima
                self._familias_cache = [
                    f for f in dados if "nome" in f and "numero" in f
                ]
                return self._familias_cache
        except json.JSONDecodeError:
            logging.error(f"Erro ao decodificar {self.familias_file}")
            return []
        except Exception as e:
            logging.error(f"Erro ao carregar famílias: {str(e)}")
            return []

    def salvar_familias(self, familias):
        try:
            with open(self.familias_file, "w", encoding="utf-8") as f:
                json.dump(familias, f, ensure_ascii=False, indent=2)
            self._familias_cache = familias
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar famílias: {str(e)}")
            return False

    def carregar_ultimo_sorteio(self, force_reload=False):
        if self._ultimo_sorteio_cache is not None and not force_reload:
            return self._ultimo_sorteio_cache

        try:
            if not os.path.exists(self.sorteio_file):
                return None

            with open(self.sorteio_file, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self._ultimo_sorteio_cache = dados.get("ultimo_sorteado")
                return self._ultimo_sorteio_cache
        except json.JSONDecodeError:
            logging.error(f"Erro ao decodificar {self.sorteio_file}")
            return None
        except Exception as e:
            logging.error(f"Erro ao carregar último sorteio: {str(e)}")
            return None

    def salvar_sorteio(self, numero):
        try:
            with open(self.sorteio_file, "w", encoding="utf-8") as f:
                json.dump({"ultimo_sorteado": numero}, f)
            self._ultimo_sorteio_cache = numero
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar sorteio: {str(e)}")
            return False

    def resetar_sorteio(self):
        familias = self.carregar_familias()
        total_familias = len(familias)

        numeros_disponiveis = list(range(1, total_familias + 1))
        random.shuffle(numeros_disponiveis)

        for i, familia in enumerate(familias):
            familia["sorteado"] = False
            familia["numero"] = numeros_disponiveis[i]
            familia.pop("data_sorteio", None)

        if self.salvar_familias(familias):
            if os.path.exists(self.sorteio_file):
                os.remove(self.sorteio_file)
            self._ultimo_sorteio_cache = None
            return True
        return False

    def adicionar_familia(self, nome, caminho_foto):
        familias = self.carregar_familias()
        novo_id = max([f.get("id", 0) for f in familias], default=0) + 1
        numero = max([f.get("numero", 0) for f in familias], default=0) + 1

        extensao = os.path.splitext(caminho_foto)[-1]
        nome_arquivo = f"{uuid4().hex[:8]}{extensao}"
        destino = get_resource_path("imagens", "familias", nome_arquivo)
        shutil.copy2(caminho_foto, destino)

        nova_familia = {
            "id": novo_id,
            "numero": numero,
            "nome": nome,
            "foto": os.path.join("imagens", "familias", nome_arquivo).replace("\\", "/"),
            "sorteado": False
        }

        familias.append(nova_familia)
        return self.salvar_familias(familias)
