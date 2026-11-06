"""Palabras reservadas y validación de nombres de símbolos, compartidas por los analizadores."""

from configuracion import (
    INSTRUCCIONES_SOPORTADAS,
    DIRECTIVAS,
    OTRAS_INSTRUCCIONES_8086,
    REGISTROS_8,
    REGISTROS_16,
    REGISTROS_SEG,
    ER_SIMBOLO,
)

TODAS_INSTRUCCIONES: frozenset[str] = INSTRUCCIONES_SOPORTADAS | OTRAS_INSTRUCCIONES_8086
TODOS_REGISTROS: frozenset[str] = REGISTROS_8 | REGISTROS_16 | REGISTROS_SEG


def clase_reservada(nombre: str) -> str:
    """Devuelve qué clase de palabra reservada es 'nombre' ('' cuando está libre)."""
    mayus = nombre.upper()
    if mayus in TODAS_INSTRUCCIONES:
        return "una instrucción"
    if mayus in TODOS_REGISTROS:
        return "un registro"
    if mayus in DIRECTIVAS:
        return "una pseudoinstrucción"
    return ""


def error_nombre(nombre: str, que: str = "símbolo") -> str:
    """Valida un nombre de usuario (variable, constante o etiqueta); '' cuando es válido."""
    if not nombre:
        return "falta el nombre de la etiqueta" if que == "etiqueta" else f"falta el nombre del {que}"
    if nombre[0].isdigit():
        return f"el nombre '{nombre}' no puede iniciar con un dígito"
    if not ER_SIMBOLO.match(nombre):
        return f"el nombre '{nombre}' tiene caracteres no permitidos (use letras, dígitos, _, @ o ?)"
    clase = clase_reservada(nombre)
    if clase:
        return f"'{nombre}' es {clase} (palabra reservada) y no puede usarse como nombre de {que}"
    return ""
