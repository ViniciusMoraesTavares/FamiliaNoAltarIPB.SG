# src/filtro_familias.py

def nao_sorteadas(familias):
    """Retorna só as famílias cujo campo 'sorteado' é False."""
    return [f for f in familias if not f.get("sorteado", False)]

def sorteadas(familias):
    """Retorna só as famílias cujo campo 'sorteado' é True."""
    return [f for f in familias if f.get("sorteado", False)]

def buscar(familias, termo):
    """
    Filtra por nome ou número que contenha o termo (case-insensitive).
    Se termo em branco, retorna todas.
    """
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
