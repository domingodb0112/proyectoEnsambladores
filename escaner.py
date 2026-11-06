"""Escáner: separa una línea de ensamblador en elementos y ofrece utilidades de texto comunes."""

from collections.abc import Iterator

from configuracion import ER_INICIO_DUP, ER_PALABRA_COMPUESTA

DELIMITADORES: frozenset[str] = frozenset({" ", "\t", "\r", "\n", ",", ":"})
COMILLAS: str = "\"'"


def fuera_de_comillas(texto: str, abre: str = "", cierra: str = "") -> Iterator[tuple[int, str, int]]:
    """Recorre los caracteres que están fuera de comillas -> (índice, carácter, profundidad).

    La profundidad cuenta los delimitadores abiertos con 'abre' y cerrados con 'cierra'
    (por ejemplo "([" y ")]"); ya incluye el carácter actual.
    """
    comilla: str | None = None
    profundidad = 0
    for ind, caracter in enumerate(texto):
        if comilla:
            if caracter == comilla:
                comilla = None
            continue
        if caracter in COMILLAS:
            comilla = caracter
            continue
        if caracter in abre:
            profundidad += 1
        elif caracter in cierra:
            profundidad -= 1
        yield ind, caracter, profundidad


def dividir_nivel_superior(texto: str, separador: str, abre: str = "([", cierra: str = ")]") -> list[str]:
    """Divide el texto por 'separador', sin cortar dentro de comillas, corchetes o paréntesis."""
    partes: list[str] = []
    inicio = 0
    for ind, caracter, profundidad in fuera_de_comillas(texto, abre, cierra):
        if caracter == separador and profundidad == 0:
            partes.append(texto[inicio:ind])
            inicio = ind + 1
    partes.append(texto[inicio:])
    return partes


def quitar_comentarios(linea: str) -> str:
    """Quita el comentario (desde ';') respetando los ';' que van dentro de comillas."""
    for ind, caracter, _ in fuera_de_comillas(linea):
        if caracter == ";":
            return linea[:ind]
    return linea


def extraer_encerrado(texto: str, ind_inicio: int, apertura: str, cierre: str) -> str:
    """Fragmento desde 'apertura' hasta su 'cierre' correspondiente (respeta comillas).

    Si falta el cierre devuelve el resto del texto, para que el clasificador lo marque inválido.
    """
    for ind, caracter, profundidad in fuera_de_comillas(texto[ind_inicio:], apertura, cierre):
        if caracter == cierre and profundidad == 0:
            return texto[ind_inicio : ind_inicio + ind + 1]
    return texto[ind_inicio:]


def dividir_linea(linea: str) -> list[str]:
    """Separa los elementos de una línea respetando los elementos compuestos.

    Separadores: espacio, tabulador, coma y dos puntos. Compuestos (indivisibles):
    .code/.data/.stack segment, byte/word ptr, dup(xxx), [xxx], "xxxx" y 'xxxx'.
    """
    limpia = quitar_comentarios(linea).strip()
    elementos: list[str] = []
    ind = 0
    while ind < len(limpia):
        caracter = limpia[ind]
        if caracter in DELIMITADORES:
            ind += 1
            continue

        # .xxx segment / byte ptr / word ptr (se muestran con un solo espacio)
        compuesto = ER_PALABRA_COMPUESTA.match(limpia, ind)
        if compuesto:
            elementos.append(" ".join(compuesto.group(0).split()))
            ind = compuesto.end()
            continue

        # "xxxx" / 'xxxx' (sin cierre: el resto de la línea)
        if caracter in COMILLAS:
            fin = limpia.find(caracter, ind + 1)
            fin = len(limpia) if fin == -1 else fin + 1
            elementos.append(limpia[ind:fin])
            ind = fin
            continue

        # [xxx]
        if caracter == "[":
            encerrado = extraer_encerrado(limpia, ind, "[", "]")
            elementos.append(encerrado)
            ind += len(encerrado)
            continue

        # dup(xxx) (se muestra sin espacios antes del paréntesis)
        inicio_dup = ER_INICIO_DUP.match(limpia, ind)
        if inicio_dup:
            ind_parentesis = inicio_dup.end() - 1
            encerrado = extraer_encerrado(limpia, ind_parentesis, "(", ")")
            elementos.append(limpia[ind : ind + 3] + encerrado)
            ind = ind_parentesis + len(encerrado)
            continue

        # Elemento simple: hasta un separador o el inicio de un compuesto
        inicio = ind
        while ind < len(limpia) and limpia[ind] not in DELIMITADORES and limpia[ind] not in "[\"'":
            ind += 1
        elementos.append(limpia[inicio:ind])
    return elementos
