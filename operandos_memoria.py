"""Operandos de memoria: expresiones [..] y referencias a variables."""

import re

from configuracion import REGISTROS_8, REGISTROS_16, REGISTROS_SEG, ER_SIMBOLO, RANGO_PALABRA
from constantes import leer_numero
from operando import Operando
from tabla_simbolos import TablaSimbolos

BASES = ("BX", "BP")
INDICES = ("SI", "DI")
ER_INICIA_NUMERO = re.compile(r"^[+-]?[0-9]")


def revisar_corchete(corchete: str, tabla: TablaSimbolos) -> tuple[int | None, str]:
    """Valida [..] -> (tamaño de una variable interior o None, error)."""
    if not corchete.endswith("]"):
        return None, "falta cerrar el corchete ']'"
    interior = corchete[1:-1]
    if not interior.strip():
        return None, "los corchetes están vacíos"
    if "[" in interior or "]" in interior:
        return None, "no se admiten corchetes anidados"
    trozos = re.split(r"([+-])", interior)
    piezas, signos = trozos[0::2], trozos[1::2]
    bases: list[str] = []
    indices: list[str] = []
    tamano: int | None = None
    for pos, cruda in enumerate(piezas):
        pieza = cruda.strip()
        signo = signos[pos - 1] if pos else "+"
        if not pieza:
            return None, "falta un operando junto a '+' o '-' dentro de los corchetes"
        mayus = pieza.upper()
        if mayus in REGISTROS_16 or mayus in REGISTROS_8 or mayus in REGISTROS_SEG:
            if mayus not in BASES + INDICES:
                return None, f"{mayus} no puede usarse como dirección entre corchetes (solo BX, BP, SI y DI)"
            if signo == "-":
                return None, f"no se puede restar un registro (-{mayus})"
            (bases if mayus in BASES else indices).append(mayus)
        elif ER_INICIA_NUMERO.match(pieza):
            valor, error = leer_numero(pieza)
            if error:
                return None, error
            if not RANGO_PALABRA[0] <= valor <= RANGO_PALABRA[1]:
                return None, f"el desplazamiento {valor} no cabe en 16 bits"
        elif ER_SIMBOLO.match(pieza):
            fila = tabla.buscar(pieza)
            if fila is None:
                return None, f"el símbolo '{pieza}' no está definido"
            if fila["clase"] == "etiqueta":
                return None, f"'{pieza}' es una etiqueta; entre corchetes solo van registros, variables y constantes"
            tamano = tamano or fila["elem"]
        else:
            return None, f"'{pieza}' no es válido dentro de los corchetes"
    if len(bases) > 1:
        return None, f"solo puede haber un registro base (BX o BP), no {' y '.join(bases)}"
    if len(indices) > 1:
        return None, f"solo puede haber un registro índice (SI o DI), no {' y '.join(indices)}"
    return tamano, ""


def leer_memoria(texto: str, tabla: TablaSimbolos) -> tuple[Operando | None, str]:
    """Operando de memoria: variable, variable[..] o [..]."""
    pos = texto.find("[")
    nombre = texto.strip() if pos == -1 else texto[:pos].strip()
    corchete = "" if pos == -1 else texto[pos:].strip()
    tamano: int | None = None
    if nombre:
        fila = tabla.buscar(nombre) if ER_SIMBOLO.match(nombre) else None
        if fila is None:
            return None, f"el símbolo '{nombre}' no está definido (se define antes de usarse)"
        if fila["clase"] not in ("db", "dw"):
            return None, f"'{nombre}' es {fila['tipo'].lower()}, no una variable en memoria"
        tamano = fila["elem"]
    if corchete:
        tam_byte, error = revisar_corchete(corchete, tabla)
        if error:
            return None, error
        tamano = tamano or tam_byte
    return Operando("mem", tamano, None, texto.strip()), ""
