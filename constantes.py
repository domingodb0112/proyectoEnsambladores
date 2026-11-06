"""Lectura de constantes para las Fases 2 y 3: números con signo, caracteres y revisión de rangos."""

from configuracion import (
    PERMITIR_INTERROGACION,
    RANGO_BYTE,
    RANGO_CANTIDAD,
    ER_BINARIO_INVALIDO,
    ER_BINARIO_VALIDO,
    ER_DECIMAL,
    ER_HEX_INVALIDO,
    ER_HEX_VALIDO,
    ER_CADENA,
    ER_SIMBOLO,
    RANGO_PALABRA,
)


def leer_numero(texto: str, con_signo: bool = True) -> tuple[int | None, str]:
    """Lee una constante decimal/hex/binaria con signo opcional -> (valor, error)."""
    cruda = texto.strip()
    if not cruda:
        return None, "falta la constante"
    signo, cuerpo = 1, cruda
    if cruda[0] in "+-":
        if not con_signo:
            return None, f"'{cruda}' no puede llevar signo: se espera una constante sin signo"
        signo = -1 if cruda[0] == "-" else 1
        cuerpo = cruda[1:]
    mayus = cuerpo.upper()
    if ER_HEX_VALIDO.match(mayus):
        return signo * int(mayus[:-1], 16), ""
    if ER_HEX_INVALIDO.match(mayus):
        return None, f"'{cuerpo}' es un hexadecimal inválido: debe iniciar con un dígito (use 0{cuerpo})"
    if ER_BINARIO_VALIDO.match(mayus):
        return signo * int(mayus[:-1], 2), ""
    if ER_BINARIO_INVALIDO.match(mayus):
        return None, f"'{cuerpo}' es un binario inválido: solo admite los dígitos 0 y 1"
    if ER_DECIMAL.match(mayus):
        return signo * int(mayus.rstrip("D"), 10), ""
    return None, f"'{cruda}' no es una constante numérica válida"


def leer_caracter(texto: str) -> tuple[str | None, str]:
    """Lee una constante carácter entre comillas ('A', "hola") -> (contenido, error)."""
    cruda = texto.strip()
    if not cruda or cruda[0] not in "'\"":
        return None, f"'{cruda}' no es una constante carácter (va entre comillas)"
    if not ER_CADENA.match(cruda):
        return None, f"falta cerrar las comillas ({cruda[0]}) de la constante carácter"
    contenido = cruda[1:-1]
    if not contenido:
        return None, "la constante carácter está vacía"
    if any(ord(car) > 255 for car in contenido):
        return None, f"{cruda} contiene caracteres que no caben en un byte"
    return contenido, ""


def texto_rango(limites: tuple[int, int]) -> str:
    """Rango legible, p. ej. '-128 a 255'."""
    return f"{limites[0]} a {limites[1]}"


def leer_cantidad(texto: str) -> tuple[int | None, str]:
    """Lee la cantidad de repeticiones de dup: constante de palabra sin signo."""
    valor, error = leer_numero(texto, con_signo=False)
    if error:
        return None, f"cantidad de dup: {error}"
    if not RANGO_CANTIDAD[0] <= valor <= RANGO_CANTIDAD[1]:
        return None, f"la cantidad {valor} excede una palabra sin signo ({texto_rango(RANGO_CANTIDAD)})"
    return valor, ""


def leer_elemento(texto: str, clase: str, in_dup: bool = False) -> tuple[str | None, int, str]:
    """Lee un valor inicial de db/dw -> (literal tal como se escribió, bytes, error)."""
    cruda = texto.strip()
    es_byte = clase == "db"
    limites, etiqueta, unidad = (RANGO_BYTE, "un byte", 1) if es_byte else (RANGO_PALABRA, "una palabra", 2)
    if cruda == "?":
        if PERMITIR_INTERROGACION:
            return "?", unidad, ""
        return None, 0, "'?' (sin inicializar) no forma parte de la sintaxis: use una constante"
    if cruda and cruda[0] in "'\"":
        if not es_byte:
            return None, 0, f"dw solo admite constantes numéricas; {cruda} es un carácter"
        contenido, error = leer_caracter(cruda)
        if error:
            return None, 0, error
        if in_dup and len(contenido) != 1:
            return None, 0, f"dentro de dup solo se admite un carácter, no la cadena {cruda}"
        return cruda, len(contenido), ""
    valor, error = leer_numero(cruda)
    if error:
        if es_byte and ER_SIMBOLO.match(cruda) and error.endswith("válida"):
            error += " (si es texto, escríbalo entre comillas)"
        return None, 0, error
    if not limites[0] <= valor <= limites[1]:
        return None, 0, (f"el valor {valor} no cabe en {etiqueta} "
                         f"({clase} admite {texto_rango(limites)})")
    return cruda, unidad, ""
