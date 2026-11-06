"""Lectura del archivo fuente y ejecución de las tres funciones (léxico, sintaxis y símbolos)."""

from pathlib import Path

from analizador import Analizador
from clasificador import clasificar_elemento
from escaner import dividir_linea


class ElementoLexico:
    """Un elemento separado en la Función 1."""

    __slots__ = ("linea", "texto", "categoria")

    def __init__(self, linea: int, texto: str, categoria: str) -> None:
        self.linea, self.texto, self.categoria = linea, texto, categoria


class Resultado:
    """Todo lo que se muestra de un archivo analizado."""

    def __init__(self, ruta: Path, lineas: list[str], elementos: list[ElementoLexico],
                 analizador: Analizador) -> None:
        self.ruta, self.lineas, self.elementos, self.analizador = ruta, lineas, elementos, analizador
        self.correctas = sum(1 for fila in analizador.filas if fila[2] == "Correcta")
        self.incorrectas = sum(1 for fila in analizador.filas if fila[2] == "Incorrecta")


def leer_lineas_fuente(ruta: Path) -> list[str]:
    """Lee un archivo fuente como UTF-8; si falla, como Windows-1252 o Latin-1."""
    cruda = ruta.read_bytes()
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            return cruda.decode(codificacion).splitlines()
        except UnicodeDecodeError:
            continue
    return cruda.decode("latin-1").splitlines()


def analizar_lexico(lineas: list[str]) -> list[ElementoLexico]:
    """Función 1: separa e identifica los elementos de cada línea."""
    return [ElementoLexico(numero, elemento, clasificar_elemento(elemento))
            for numero, linea in enumerate(lineas, 1)
            for elemento in dividir_linea(linea)]


def analizar_archivo(ruta: Path) -> Resultado:
    """Ejecuta las Funciones 1, 2 y 3 sobre un archivo .ens."""
    lineas = leer_lineas_fuente(ruta)
    analizador = Analizador(lineas)
    analizador.ejecutar()
    return Resultado(ruta, lineas, analizar_lexico(lineas), analizador)
