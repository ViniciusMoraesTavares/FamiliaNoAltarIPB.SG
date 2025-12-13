import json
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
FAMILIAS = os.path.join(BASE_DIR, "dados", "familias.json")

def main():
    hoje = datetime.now().strftime("%d/%m/%Y")
    with open(FAMILIAS, "r", encoding="utf-8") as f:
        familias = json.load(f)
    for f in familias:
        f["sorteado"] = True
        f["data_sorteio"] = hoje
    tmp = FAMILIAS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(familias, f, ensure_ascii=False, indent=2)
    os.replace(tmp, FAMILIAS)
    print(f"Atualizadas {len(familias)} famílias como sorteadas em {hoje}.")

if __name__ == "__main__":
    main()
