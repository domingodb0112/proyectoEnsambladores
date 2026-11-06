"""Operandos del segmento de código: separación, registros, inmediatos y memoria."""

import re

from configuracion import ER_PREFIJO_PTR, ER_SIMBOLO, RANGO_PALABRA, REGISTROS_8, REGISTROS_16, REGISTROS_SEG
from constantes import leer_caracter, leer_numero
from escaner import dividir_nivel_superior
from tabla_simbolos import TablaSimbolos


class Operando:
    """Operando analizado. clase: reg | inm | mem | etiqueta. tamano en bits (8/16) o None."""

    __slots__ = ("clase", "tamano", "valor", "texto")

    def __init__(self, clase: str, tamano: int | None = None,
                 valor: int | None = None, texto: str = "") -> None:
        self.clase, self.tamano, self.valor, self.texto = clase, tamano, valor, texto


def separar_operandos(texto: str) -> list[str]:
    """Separa por comas de nivel superior (ignora las comas dentro de [], () o comillas)."""
    if not texto.strip():
        return []
    return [parte.strip() for parte in dividir_nivel_superior(texto, ",")]


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
