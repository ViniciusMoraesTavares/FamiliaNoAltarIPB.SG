def nao_sorteadas(familias):
    return [f for f in familias if not f.get("sorteado", False)]

def sorteadas(familias):
    return [f for f in familias if f.get("sorteado", False)]

def buscar(familias, termo):

    t = termo.strip().lower()
    if not t:
        return familias

    resultado = []
    for f in familias:
        nome = f.get("nome", "").lower()
        numero = str(f.get("numero", ""))
        if t in nome or t in numero:
            resultado.append(f)
    return resultado