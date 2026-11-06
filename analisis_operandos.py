"""Análisis de operandos del segmento de código: registros, inmediatos y memoria."""

import re

from configuracion import REGISTROS_8, REGISTROS_16, REGISTROS_SEG, ER_PREFIJO_PTR, ER_SIMBOLO
from constantes import leer_caracter, leer_numero
from operandos_memoria import ER_INICIA_NUMERO, leer_memoria
from operando import Operando
from tabla_simbolos import TablaSimbolos


def leer_operando(texto: str, tabla: TablaSimbolos) -> tuple[Operando | None, str]:
    """Clasifica el texto de un operando -> (Operando, error)."""
    cruda = texto.strip()
    if not cruda:
        return None, "operando vacío (coma de más o falta un operando)"
    mayus = cruda.upper()
    if mayus in REGISTROS_8:
        return Operando("reg", 8, None, mayus), ""
    if mayus in REGISTROS_16:
        return Operando("reg", 16, None, mayus), ""
    if mayus in REGISTROS_SEG:
        return None, f"el registro de segmento {mayus} no se admite en estas instrucciones"
    ptr = ER_PREFIJO_PTR.match(cruda)
    if ptr:
        resto = ptr.group(2).strip()
        if not resto:
            return None, f"falta el operando de memoria después de '{ptr.group(1)} ptr'"
        _, error = leer_memoria(resto, tabla)
        if error:
            return None, error
        return Operando("mem", 8 if ptr.group(1).lower() == "byte" else 16, None, cruda), ""
    antes_corchete = cruda.split("[", 1)[0].strip()
    if "[" in cruda and (not antes_corchete or ER_SIMBOLO.match(antes_corchete)):
        return leer_memoria(cruda, tabla)          # [..] o variable[..]
    if cruda[0] in "'\"":
        contenido, error = leer_caracter(cruda)
        if error:
            return None, error
        if len(contenido) != 1:
            return None, f"{cruda} tiene {len(contenido)} caracteres: como operando solo se admite uno"
        return Operando("inm", None, ord(contenido), cruda), ""
    if ER_INICIA_NUMERO.match(cruda):
        valor, error = leer_numero(cruda)
        return (None, error) if error else (Operando("inm", None, valor, cruda), "")
    if ER_SIMBOLO.match(cruda):
        fila = tabla.buscar(cruda)
        if fila is None:
            return None, f"el símbolo '{cruda}' no está definido (se define antes de usarse)"
        if fila["clase"] == "equ":
            return Operando("inm", None, fila["numero"], cruda), ""
        if fila["clase"] == "etiqueta":
            return Operando("etiqueta", None, None, cruda), ""
        return Operando("mem", fila["elem"], None, cruda), ""
    if re.search(r"\s", cruda):
        return None, f"'{cruda}' no es un operando válido (¿falta una coma entre operandos?)"
    return None, f"'{cruda}' no es un operando válido"
