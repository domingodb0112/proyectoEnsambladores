"""Análisis sintáctico y semántico de las líneas de los segmentos de pila y datos (Fase 2)."""

from configuracion import DIRECTIVAS, ER_INICIO_DUP, RANGO_PALABRA
from constantes import leer_cantidad, leer_elemento, leer_numero, texto_rango
from nombres import TODAS_INSTRUCCIONES, error_nombre
from escaner import dividir_linea, fuera_de_comillas
from tabla_simbolos import TablaSimbolos

Resultado = tuple[bool, str]


def _error_sobrante(limpia: str) -> str:
    """Las comas y dos puntos fuera de comillas no forman parte de las definiciones de pila y datos."""
    for _, caracter, _ in fuera_de_comillas(limpia):
        if caracter == ",":
            return "no se admiten listas con comas: use una sola constante (o 'n dup(valor)')"
        elif caracter == ":":
            return "los dos puntos solo se usan para definir etiquetas en el segmento de código"
    return ""


def leer_dup(elemento: str, clase: str) -> tuple[str | None, int, str]:
    """dup(xxx) -> (contenido mostrado, bytes de un elemento, error)."""
    inicio = ER_INICIO_DUP.match(elemento)
    if not inicio:
        if "(" in elemento:
            return None, 0, f"'{elemento}' no es dup(...): la pseudoinstrucción debe escribirse 'dup'"
        return None, 0, f"se esperaba dup(...) y se encontró '{elemento}'"
    if not elemento.endswith(")"):
        return None, 0, f"falta cerrar el paréntesis de {elemento}"
    interior = elemento[inicio.end():-1].strip()
    if not interior:
        return None, 0, "dup() está vacío: falta el valor a repetir"
    if "," in interior or "dup" in interior.lower():
        return None, 0, "dup admite una sola constante (sin listas ni dup anidados)"
    return leer_elemento(interior, clase, in_dup=True)


def analizar_pila(limpia: str, num_linea: int, tabla: TablaSimbolos) -> Resultado:
    """Línea del segmento de pila: dw <palabra sin signo> dup(<palabra con/sin signo>)."""
    error = _error_sobrante(limpia)
    if error:
        return False, error
    elems = dividir_linea(limpia)
    primero = elems[0].upper()
    if primero == "DB":
        return False, "en el segmento de pila solo se admite dw (se encontró db)"
    if primero != "DW":
        return False, f"la pila no lleva símbolo ni otro elemento: se esperaba 'dw' y se encontró '{elems[0]}'"
    if len(elems) != 3:
        return False, (f"número de elementos incorrecto: se esperaba 'dw cantidad dup(valor)' "
                     f"y se encontraron {len(elems)}")
    _, error = leer_cantidad(elems[1])
    if not error:
        _, _, error = leer_dup(elems[2], "dw")
    return (not error), error


def _definir_valor(elems: list[str], clase: str) -> tuple[str | None, int, str]:
    """Parte del valor de db/dw -> (texto mostrado, bytes totales, error)."""
    resto = elems[2:]
    if not resto:
        return None, 0, f"falta el valor inicial después de {clase}"
    if len(resto) == 1:
        if ER_INICIO_DUP.match(resto[0]):
            return None, 0, f"falta la cantidad antes de {resto[0]} (forma: n dup(valor))"
        return leer_elemento(resto[0], clase)
    if "(" in resto[1]:
        cantidad, error = leer_cantidad(resto[0])
        if error:
            return None, 0, error
        _, unidad, error = leer_dup(resto[1], clase)
        if error:
            return None, 0, error
        if len(resto) > 2:
            return None, 0, f"sobran elementos después de {resto[1]}: '{' '.join(resto[2:])}'"
        return f"{resto[0]} {resto[1]}", cantidad * unidad, ""
    _, _, error = leer_elemento(resto[0], clase)
    if error:
        return None, 0, error
    return None, 0, (f"sobran elementos después de '{resto[0]}': '{' '.join(resto[1:])}' "
                     "(solo se admite una constante o 'n dup(valor)')")


def analizar_datos(limpia: str, num_linea: int, tabla: TablaSimbolos) -> Resultado:
    """Línea del segmento de datos: símbolo db/dw/equ ... (ver la sintaxis de la Fase 2)."""
    elems = dividir_linea(limpia)
    mayus0 = elems[0].upper()
    nombra_simbolo = len(elems) > 1 and elems[1].lower() in ("db", "dw", "equ")
    if mayus0 in TODAS_INSTRUCCIONES and not nombra_simbolo:
        return False, "las instrucciones van en el segmento de código; aquí solo se definen variables y constantes"
    if mayus0 in DIRECTIVAS and not nombra_simbolo:
        return False, f"falta el nombre del símbolo antes de '{elems[0]}'"
    error = _error_sobrante(limpia) or error_nombre(elems[0])
    if error:
        return False, error
    anterior = tabla.buscar(elems[0])
    if anterior:
        return False, f"el símbolo '{elems[0]}' ya fue definido en la línea {anterior['linea']}"
    if len(elems) < 2:
        return False, f"falta la pseudoinstrucción db, dw o equ después de '{elems[0]}'"
    directiva = elems[1].lower()
    if directiva not in ("db", "dw", "equ"):
        extra = " (esa pseudoinstrucción no se admite aquí)" if elems[1].upper() in DIRECTIVAS else ""
        return False, f"se esperaba db, dw o equ y se encontró '{elems[1]}'{extra}"
    if directiva == "equ":
        if len(elems) != 3:
            return False, f"equ requiere exactamente una constante numérica (se encontraron {len(elems) - 2})"
        if elems[2][:1] in ("'", '"'):
            return False, f"equ solo admite constantes numéricas; {elems[2]} es un carácter"
        valor, error = leer_numero(elems[2])
        if error:
            return False, error
        if not RANGO_PALABRA[0] <= valor <= RANGO_PALABRA[1]:
            return False, f"el valor {valor} no cabe en una palabra (equ admite {texto_rango(RANGO_PALABRA)})"
        tabla.definir(elems[0], "equ", elems[2], 2, num_linea, numero=valor)
        return True, ""
    mostrado, tamano, error = _definir_valor(elems, directiva)
    if error:
        return False, error
    tabla.definir(elems[0], directiva, mostrado, tamano, num_linea, elem=8 if directiva == "db" else 16)
    return True, ""
