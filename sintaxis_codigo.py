"""Segmento de código: etiquetas, instrucciones y reglas de sus operandos."""

import re

from configuracion import (
    DESPLAZAMIENTO_MAX_INMEDIATO,
    DIRECTIVAS,
    ER_PREFIJO_PTR,
    ER_SIMBOLO,
    INSTR_DESPLAZAMIENTO,
    INSTR_SALTO,
    INSTR_SIN_OPERANDOS,
    INSTR_UN_OPERANDO,
    INSTRUCCIONES_SOPORTADAS,
    OTRAS_INSTRUCCIONES_8086,
    RANGO_BYTE,
    RANGO_PALABRA,
    REGISTROS_8,
    REGISTROS_16,
    REGISTROS_SEG,
)
from constantes import texto_rango
from escaner import fuera_de_comillas
from operandos import Operando, leer_operando, separar_operandos
from tabla_simbolos import TablaSimbolos, error_nombre


AMBIGUO = "no se puede saber el tamaño de {0}: use 'byte ptr' o 'word ptr'"


def descripcion(op: Operando) -> str:
    """Descripción corta del operando con su tamaño, para los mensajes."""
    if op.clase == "reg":
        return f"{op.texto} ({op.tamano} bits)"
    if op.clase == "mem" and op.tamano:
        return f"'{op.texto}' ({op.tamano} bits)"
    return f"'{op.texto}'"


def _cabe(valor: int, tamano: int) -> bool:
    minimo, maximo = RANGO_BYTE if tamano == 8 else RANGO_PALABRA
    return minimo <= valor <= maximo


def _revisar_salto(mayus: str, textos: list[str], tabla: TablaSimbolos) -> str:
    if len(textos) != 1:
        return f"{mayus} requiere 1 operando (una etiqueta) y se encontraron {len(textos)}"
    nombre = textos[0].strip()
    if nombre.upper() in REGISTROS_8 | REGISTROS_16 | REGISTROS_SEG:
        return f"el operando de {mayus} debe ser una etiqueta, no el registro {nombre.upper()}"
    if not ER_SIMBOLO.match(nombre):
        return f"el operando de {mayus} debe ser una etiqueta; '{nombre}' no lo es"
    fila = tabla.buscar(nombre)
    if fila is None:
        linea = tabla.etiquetas_futuras.get(nombre.upper())
        if linea:
            return (f"la etiqueta '{nombre}' se define después (línea {linea}); "
                    "debe definirse antes de usarse en un salto")
        return f"la etiqueta '{nombre}' no está definida"
    if fila["clase"] != "etiqueta":
        return f"'{nombre}' es {fila['tipo'].lower()}, no una etiqueta"
    return ""


def _revisar_uno(mayus: str, op: Operando) -> str:
    if op.clase == "inm":
        return f"{mayus} no admite un valor inmediato: requiere un registro o una variable en memoria"
    if op.clase == "etiqueta":
        return f"'{op.texto}' es una etiqueta; {mayus} requiere un registro o una variable"
    if op.clase == "mem" and op.tamano is None:
        return AMBIGUO.format(f"'{op.texto}'")
    return ""


def _revisar_desplazamiento(mayus: str, destino: Operando, cantidad: Operando) -> str:
    if destino.clase in ("inm", "etiqueta"):
        return f"el destino de {mayus} debe ser un registro o una variable, no {descripcion(destino)}"
    if destino.clase == "mem" and destino.tamano is None:
        return AMBIGUO.format(f"'{destino.texto}'")
    if cantidad.clase == "reg":
        return "" if cantidad.texto == "CL" else f"el contador de {mayus} debe ser CL o un inmediato, no {cantidad.texto}"
    if cantidad.clase == "inm":
        if 0 <= cantidad.valor <= DESPLAZAMIENTO_MAX_INMEDIATO:
            return ""
        return f"el contador {cantidad.valor} está fuera de rango (0 a {DESPLAZAMIENTO_MAX_INMEDIATO})"
    return f"el contador de {mayus} debe ser CL o un inmediato, no {descripcion(cantidad)}"


def _revisar_dos(mayus: str, destino: Operando, fuente: Operando) -> str:
    for pos, op in enumerate((destino, fuente), 1):
        if op.clase == "etiqueta":
            return f"operando {pos}: '{op.texto}' es una etiqueta, no un dato"
    if destino.clase == "inm":
        return f"el primer operando de {mayus} no puede ser un valor inmediato ({destino.texto})"
    if fuente.clase == "inm" and mayus == "XCHG":
        return "XCHG no admite valores inmediatos"
    if destino.clase == "mem" and fuente.clase == "mem":
        return f"{mayus} no admite memoria con memoria: uno de los operandos debe ser un registro"
    if fuente.clase == "inm":
        if destino.tamano is None:
            return AMBIGUO.format(f"'{destino.texto}'")
        if not _cabe(fuente.valor, destino.tamano):
            limites = RANGO_BYTE if destino.tamano == 8 else RANGO_PALABRA
            return f"el valor {fuente.valor} no cabe en {descripcion(destino)} (admite {texto_rango(limites)})"
        return ""
    reg, otro = (destino, fuente) if destino.clase == "reg" else (fuente, destino)
    if otro.tamano is not None and otro.tamano != reg.tamano:
        return f"los operandos deben ser del mismo tamaño: {descripcion(destino)} y {descripcion(fuente)}"
    return ""


def _falta_coma(texto: str) -> bool:
    """Verdadero cuando el texto de un operando contiene dos elementos separados por espacios."""
    nucleo = ER_PREFIJO_PTR.sub(r"\2", texto.strip())
    nucleo = re.sub(r"\[.*?\]", "", nucleo)
    return bool(re.search(r"\S\s+\S", nucleo))


def revisar_instruccion(mnemonico: str, textos: list[str], tabla: TablaSimbolos) -> str:
    """Devuelve la causa del error de una instrucción soportada, '' cuando es válida."""
    mayus = mnemonico.upper()
    if mayus in INSTR_SIN_OPERANDOS:
        return "" if not textos else f"{mayus} no lleva operandos (se encontraron {len(textos)})"
    if mayus in INSTR_SALTO:
        return _revisar_salto(mayus, textos, tabla)
    necesita = 1 if mayus in INSTR_UN_OPERANDO else 2
    if any(not texto.strip() for texto in textos):
        return "hay un operando vacío (coma de más o falta un operando)"
    if len(textos) != necesita:
        palabra = "operando" if necesita == 1 else "operandos"
        pista = " (¿falta una coma entre operandos?)" if necesita == 2 and len(textos) == 1 and _falta_coma(textos[0]) else ""
        return f"{mayus} requiere {necesita} {palabra} y se encontraron {len(textos)}{pista}"
    operandos: list[Operando] = []
    for pos, texto in enumerate(textos, 1):
        op, error = leer_operando(texto, tabla)
        if error:
            return f"operando {pos} ({texto.strip()}): {error}"
        operandos.append(op)
    if mayus in INSTR_UN_OPERANDO:
        return _revisar_uno(mayus, operandos[0])
    if mayus in INSTR_DESPLAZAMIENTO:
        return _revisar_desplazamiento(mayus, operandos[0], operandos[1])
    return _revisar_dos(mayus, operandos[0], operandos[1])          # TEST, XCHG


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
