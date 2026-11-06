"""Análisis sintáctico y semántico de las líneas del segmento de código."""

import re

from configuracion import INSTRUCCIONES_SOPORTADAS, DIRECTIVAS, OTRAS_INSTRUCCIONES_8086, ER_SIMBOLO
from escaner import fuera_de_comillas
from nombres import error_nombre
from operando import separar_operandos
from reglas_codigo import revisar_instruccion
from tabla_simbolos import TablaSimbolos

Resultado = tuple[bool, str]


def buscar_dos_puntos(texto: str) -> int:
    """Índice del primer ':' fuera de comillas y corchetes, o -1."""
    for ind, caracter, profundidad in fuera_de_comillas(texto, "[", "]"):
        if caracter == ":" and profundidad <= 0:
            return ind
    return -1


def _definir_etiqueta(cabeza: str, num_linea: int, tabla: TablaSimbolos) -> str:
    """Valida y registra la definición de una etiqueta; '' cuando es válida."""
    if re.search(r"\s", cabeza):
        return ("los dos puntos solo se usan al definir una etiqueta ('nombre:'); "
                "no se escriben en los operandos")
    error = error_nombre(cabeza, "etiqueta")
    if error:
        return error
    anterior = tabla.buscar(cabeza)
    if anterior:
        return f"el símbolo '{cabeza}' ya fue definido en la línea {anterior['linea']}"
    tabla.definir(cabeza, "etiqueta", "-", None, num_linea)
    return ""


def _instruccion_desconocida(mnemonico: str, resto: str) -> str:
    """Explica por qué el primer elemento de la línea no es una instrucción válida."""
    mayus = mnemonico.upper()
    segundo = resto.split()[0].upper() if resto.split() else ""
    if mayus in OTRAS_INSTRUCCIONES_8086:
        return f"la instrucción '{mnemonico}' no está soportada por este ensamblador"
    if segundo in ("DB", "DW", "EQU"):
        return "las definiciones de datos van en el segmento de datos, no en el de código"
    if mayus in DIRECTIVAS:
        return f"la pseudoinstrucción '{mnemonico}' no está permitida dentro del segmento de código"
    if ER_SIMBOLO.match(mnemonico) and not resto:
        return f"'{mnemonico}' no es una instrucción; si es una etiqueta debe escribirse '{mnemonico}:'"
    return f"'{mnemonico}' no es una instrucción válida"


def analizar_codigo(limpia: str, num_linea: int, tabla: TablaSimbolos) -> Resultado:
    """Una línea del segmento de código: 'etiqueta:' opcional seguida de una instrucción opcional."""
    texto = limpia
    dos_puntos = buscar_dos_puntos(texto)
    if dos_puntos != -1:
        error = _definir_etiqueta(texto[:dos_puntos].strip(), num_linea, tabla)
        if error:
            return False, error
        texto = texto[dos_puntos + 1:].strip()
        if not texto:
            return True, ""
        if buscar_dos_puntos(texto) != -1:
            return False, "solo se permite una etiqueta por línea y los dos puntos van únicamente tras su nombre"
    coincidencia = re.match(r"(\S+)\s*(.*)$", texto, re.DOTALL)
    mnemonico, resto = coincidencia.group(1), coincidencia.group(2).strip()
    if mnemonico.upper() not in INSTRUCCIONES_SOPORTADAS:
        return False, _instruccion_desconocida(mnemonico, resto)
    error = revisar_instruccion(mnemonico, separar_operandos(resto), tabla)
    return (not error), error
