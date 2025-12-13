from src.data_manager import DataManager

_dm = DataManager()

def contar_familias():
    return len(_dm.carregar_familias())
