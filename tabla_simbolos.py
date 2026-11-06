"""Tabla de símbolos de la Fase 3 (campos: símbolo, tipo, valor inicial, tamaño)."""

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
