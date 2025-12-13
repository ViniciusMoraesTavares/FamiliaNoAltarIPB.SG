from src.data_manager import DataManager

_dm = DataManager()

def carregar_familias():
    return _dm.carregar_familias()

def salvar_familias(familias):
    _dm.salvar_familias(familias)
