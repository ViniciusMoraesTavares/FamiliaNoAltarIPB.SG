import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
FAMILIAS = os.path.join(BASE_DIR, "dados", "familias.json")
SORTEIO = os.path.join(BASE_DIR, "dados", "sorteio.json")

def main():
    with open(FAMILIAS, "r", encoding="utf-8") as f:
        familias = json.load(f)
    for f in familias:
        f["sorteado"] = False
        if "data_sorteio" in f:
            f.pop("data_sorteio")
    tmp = FAMILIAS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(familias, f, ensure_ascii=False, indent=2)
    os.replace(tmp, FAMILIAS)
    if os.path.exists(SORTEIO):
        os.remove(SORTEIO)
    print(f"Reset concluído: {len(familias)} famílias definidas como aguardando.")

if __name__ == "__main__":
    main()
