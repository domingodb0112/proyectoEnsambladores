"""Contenedor de operando y separación de la lista de operandos del segmento de código."""

from escaner import dividir_nivel_superior


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
