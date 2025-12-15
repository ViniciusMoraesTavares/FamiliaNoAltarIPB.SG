import unicodedata
import re

def _normalize(text: str) -> str:
    if not isinstance(text, str):
        text = str(text or "")
    text = text.strip().lower()
    # remove acentos
    nf = unicodedata.normalize('NFD', text)
    without_accents = ''.join(ch for ch in nf if unicodedata.category(ch) != 'Mn')
    # simplificar espaços e remover pontuação irrelevante
    simplified = re.sub(r"[^a-z0-9\s]", " ", without_accents)
    simplified = re.sub(r"\s+", " ", simplified).strip()
    return simplified

def nao_sorteadas(familias):
    return [f for f in familias if not f.get("sorteado", False)]

def sorteadas(familias):
    return [f for f in familias if f.get("sorteado", False)]

def buscar(familias, termo):
    t = _normalize(termo)
    if not t:
        return familias

    tokens = t.split(" ")
    resultado = []
    for f in familias:
        nome = _normalize(f.get("nome", ""))
        numero = _normalize(f.get("numero", ""))
        base = f"{nome} {numero}".strip()
        # todos os tokens devem estar presentes (busca por semelhança, sem acentos)
        if all(tok in base for tok in tokens):
            resultado.append(f)
    return resultado
