import json

def carregar_familias():
    try:
        with open("dados/familias.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def salvar_familias(familias):
    try:
        with open("dados/familias.json", "w", encoding="utf-8") as f:
            json.dump(familias, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")