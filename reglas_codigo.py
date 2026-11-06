"""Reglas de operandos de las instrucciones soportadas (tamaños, clases, etiquetas de salto)."""

import re

from configuracion import (
    RANGO_BYTE,
    INSTR_SALTO,
    INSTR_SIN_OPERANDOS,
    INSTR_UN_OPERANDO,
    REGISTROS_8,
    REGISTROS_16,
    REGISTROS_SEG,
    ER_PREFIJO_PTR,
    ER_SIMBOLO,
    INSTR_DESPLAZAMIENTO,
    DESPLAZAMIENTO_MAX_INMEDIATO,
    RANGO_PALABRA,
)
from constantes import texto_rango
from analisis_operandos import Operando, leer_operando
from tabla_simbolos import TablaSimbolos

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
