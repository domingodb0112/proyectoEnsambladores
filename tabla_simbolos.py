"""Tabla de símbolos (símbolo, tipo, valor inicial, tamaño) y validación de nombres."""

from configuracion import (
    DIRECTIVAS,
    ER_SIMBOLO,
    INSTRUCCIONES_SOPORTADAS,
    OTRAS_INSTRUCCIONES_8086,
    REGISTROS_8,
    REGISTROS_16,
    REGISTROS_SEG,
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


NOMBRES_TIPO: dict[str, str] = {
    "db": "Variable byte (db)",
    "dw": "Variable palabra (dw)",
    "equ": "Constante (equ)",
    "etiqueta": "Etiqueta",
}


class TablaSimbolos:
    """Tabla de símbolos sin distinguir mayúsculas, llenada en el orden del fuente."""

    def __init__(self) -> None:
        self._filas: dict[str, dict] = {}
        self.etiquetas_futuras: dict[str, int] = {}     # prelectura: etiqueta -> línea

    def buscar(self, nombre: str) -> dict | None:
        """Devuelve la fila de un símbolo definido, o None."""
        return self._filas.get(nombre.upper())

    def definir(self, nombre: str, clase: str, valor: str, tamano: int | None, linea: int,
               numero: int | None = None, elem: int | None = None) -> None:
        """Agrega un símbolo. 'numero' es el valor numérico (equ), 'elem' los bits del elemento."""
        self._filas[nombre.upper()] = {
            "nombre": nombre, "clase": clase, "tipo": NOMBRES_TIPO[clase], "valor": valor,
            "tamano": tamano, "linea": linea, "numero": numero, "elem": elem,
        }

    def filas(self) -> list[dict]:
        """Todos los símbolos en el orden de definición."""
        return list(self._filas.values())
