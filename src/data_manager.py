import json
import os
from datetime import datetime
import shutil
import random

class DataManager:
    _instance = None
    _familias_cache = None
    _ultimo_sorteio_cache = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.familias_file = "dados/familias.json"
        self.sorteio_file = "dados/sorteio.json"
        self.backup_dir = "dados/backup"
        
        # Criar diretórios se não existirem
        os.makedirs("dados", exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def _criar_backup(self, arquivo):
        """Cria um backup do arquivo antes de modificá-lo"""
        if os.path.exists(arquivo):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(
                self.backup_dir,
                f"{os.path.basename(arquivo)}.{timestamp}.bak"
            )
            shutil.copy2(arquivo, backup_path)
            
            # Manter apenas os últimos 5 backups
            backups = sorted([
                f for f in os.listdir(self.backup_dir)
                if f.startswith(os.path.basename(arquivo))
            ])
            for old_backup in backups[:-5]:
                os.remove(os.path.join(self.backup_dir, old_backup))
    
    def carregar_familias(self, force_reload=False):
        """Carrega as famílias do arquivo, usando cache quando possível"""
        if self._familias_cache is not None and not force_reload:
            return self._familias_cache
            
        try:
            if not os.path.exists(self.familias_file):
                self._familias_cache = []
                return []
                
            with open(self.familias_file, "r", encoding="utf-8") as f:
                self._familias_cache = json.load(f)
                return self._familias_cache
        except json.JSONDecodeError:
            print(f"Erro ao decodificar {self.familias_file}")
            return []
        except Exception as e:
            print(f"Erro ao carregar famílias: {str(e)}")
            return []
    
    def salvar_familias(self, familias):
        """Salva as famílias no arquivo com backup"""
        try:
            self._criar_backup(self.familias_file)
            with open(self.familias_file, "w", encoding="utf-8") as f:
                json.dump(familias, f, ensure_ascii=False, indent=2)
            self._familias_cache = familias
            return True
        except Exception as e:
            print(f"Erro ao salvar famílias: {str(e)}")
            return False
    
    def carregar_ultimo_sorteio(self, force_reload=False):
        """Carrega o último sorteio do arquivo, usando cache quando possível"""
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
            print(f"Erro ao decodificar {self.sorteio_file}")
            return None
        except Exception as e:
            print(f"Erro ao carregar último sorteio: {str(e)}")
            return None
    
    def salvar_sorteio(self, numero):
        """Salva o número sorteado com backup"""
        try:
            self._criar_backup(self.sorteio_file)
            with open(self.sorteio_file, "w", encoding="utf-8") as f:
                json.dump({"ultimo_sorteado": numero}, f)
            self._ultimo_sorteio_cache = numero
            return True
        except Exception as e:
            print(f"Erro ao salvar sorteio: {str(e)}")
            return False
    
    def resetar_sorteio(self):
        """Reseta o estado de sorteio de todas as famílias e redistribui os números"""
        familias = self.carregar_familias()
        total_familias = len(familias)
        
        # Gera uma lista de números de 1 até o total de famílias
        numeros_disponiveis = list(range(1, total_familias + 1))
        random.shuffle(numeros_disponiveis)
        
        # Atribui os novos números às famílias
        for i, familia in enumerate(familias):
            familia["sorteado"] = False
            familia["numero"] = numeros_disponiveis[i]
            if "data_sorteio" in familia:
                del familia["data_sorteio"]
        
        if self.salvar_familias(familias):
            if os.path.exists(self.sorteio_file):
                self._criar_backup(self.sorteio_file)
                os.remove(self.sorteio_file)
            self._ultimo_sorteio_cache = None
            return True
        return False 