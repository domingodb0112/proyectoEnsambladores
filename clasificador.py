"""Clasificación léxica de los elementos (Fase 1)."""

import re

from configuracion import (
    INSTRUCCIONES_SOPORTADAS,
    OTRAS_INSTRUCCIONES_8086,
    DIRECTIVAS,
    REGISTROS_16,
    REGISTROS_8,
    REGISTROS_SEG,
    ER_DECIMAL,
    ER_HEX_VALIDO,
    ER_HEX_INVALIDO,
    ER_BINARIO_VALIDO,
    ER_BINARIO_INVALIDO,
    ER_CADENA,
    ER_SIMBOLO,
    ER_ENCABEZADO_SEGMENTO,
    ER_PTR_COMPUESTO,
    ER_INICIO_DUP,
)
from escaner import dividir_nivel_superior

INVALIDO = "Elemento no identificado"
NUMERICO = {"Constante Decimal", "Constante Hexadecimal", "Constante Binaria"}
REGISTROS = {"Registro (16 bits)", "Registro (8 bits)", "Registro de Segmento"}
PARTES_CORCHETE = NUMERICO | REGISTROS | {"Símbolo"}                # dentro de [xxx]
ELEMENTOS_DUP = NUMERICO | {"Constante Carácter", "Símbolo"}          # dentro de dup(xxx)
ER_DUP_ANIDADO = re.compile(r"^(\S+)\s+(dup\s*\(.*\))$", re.IGNORECASE | re.DOTALL)


def _parentesis_balanceados(texto: str) -> bool:
    """Paréntesis balanceados y comillas cerradas."""
    profundidad, comilla = 0, None
    for caracter in texto:
        if comilla:
            comilla = None if caracter == comilla else comilla
        elif caracter in "\"'":
            comilla = caracter
        elif caracter == "(":
            profundidad += 1
        elif caracter == ")":
            profundidad -= 1
            if profundidad < 0:
                return False
    return profundidad == 0 and comilla is None


def _dup_valido(elemento: str) -> bool:
    """dup(xxx): xxx es '?', constantes, símbolos o 'n dup(...)', separados por coma."""
    inicio = ER_INICIO_DUP.match(elemento)
    if not inicio or not elemento.endswith(")"):
        return False
    interior = elemento[inicio.end():-1]
    if not _parentesis_balanceados(interior):
        return False
    for pieza in dividir_nivel_superior(interior, ",", "(", ")"):
        pieza = pieza.strip()
        anidado = ER_DUP_ANIDADO.match(pieza)
        if pieza == "?":
            continue
        if anidado:
            if clasificar_elemento(anidado.group(1)) in NUMERICO and _dup_valido(anidado.group(2)):
                continue
            return False
        if clasificar_elemento(pieza) not in ELEMENTOS_DUP:
            return False
    return True


def _corchete_valido(elemento: str) -> bool:
    """[xxx]: registros, símbolos y constantes numéricas unidos por '+' o '-'."""
    if not elemento.endswith("]"):
        return False
    interior = elemento[1:-1]
    if "[" in interior or "]" in interior:
        return False
    return all(clasificar_elemento(parte.strip()) in PARTES_CORCHETE for parte in re.split(r"[+\-]", interior))


def clasificar_elemento(elemento: str) -> str:
    """Clasifica un elemento de una línea de ensamblador 8086."""
    recortada: str = elemento.strip()
    if not recortada:
        return INVALIDO
    elemento_mayus: str = recortada.upper()

    # 1. Elementos compuestos
    if recortada[0] == "[":
        return "Símbolo" if _corchete_valido(recortada) else INVALIDO
    if recortada[0] in "\"'":
        return "Constante Carácter" if ER_CADENA.match(recortada) else INVALIDO
    if ER_INICIO_DUP.match(recortada):
        return "Pseudoinstrucción" if _dup_valido(recortada) else INVALIDO
    if ER_ENCABEZADO_SEGMENTO.match(recortada) or ER_PTR_COMPUESTO.match(recortada):
        return "Pseudoinstrucción"

    # 2. Pseudoinstrucción / Directiva
    if elemento_mayus in DIRECTIVAS:
        return "Pseudoinstrucción"

    # 3. Instrucciones soportadas
    if elemento_mayus in INSTRUCCIONES_SOPORTADAS:
        return "Instrucción"

    # 4. Registros del 8086
    if elemento_mayus in REGISTROS_16:
        return "Registro (16 bits)"
    if elemento_mayus in REGISTROS_8:
        return "Registro (8 bits)"
    if elemento_mayus in REGISTROS_SEG:
        return "Registro de Segmento"

    # 5. Constantes y números mal formados
    if ER_HEX_VALIDO.match(elemento_mayus):
        return "Constante Hexadecimal"
    if ER_HEX_INVALIDO.match(elemento_mayus):
        return INVALIDO
    if ER_BINARIO_VALIDO.match(elemento_mayus):
        return "Constante Binaria"
    if ER_BINARIO_INVALIDO.match(elemento_mayus):
        return INVALIDO
    if ER_DECIMAL.match(elemento_mayus):
        return "Constante Decimal"

    # 6. Símbolo (otras instrucciones del 8086 o identificadores del usuario)
    if elemento_mayus in OTRAS_INSTRUCCIONES_8086 or ER_SIMBOLO.match(recortada):
        return "Símbolo"

    # 7. No identificado / inválido
    return INVALIDO
