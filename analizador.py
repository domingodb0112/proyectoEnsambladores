"""Analizador del programa para las Fases 2 y 3: estructura de segmentos, dictamen por línea y símbolos."""

import re

from configuracion import ER_ENCABEZADO_SEGMENTO
from escaner import quitar_comentarios, dividir_linea
from tabla_simbolos import TablaSimbolos
from sintaxis_codigo import analizar_codigo
from sintaxis_datos import analizar_datos, analizar_pila

NOMBRES_SEGMENTO = {"pila": "pila", "datos": "datos", "codigo": "código"}
AYUDA_ENCABEZADO = "debe ser '.stack segment', '.data segment' o '.code segment'"
ER_DEF_ETIQUETA = re.compile(r"^\s*([A-Za-z_@?][\w@?$]*)\s*:")
PALABRA_A_SEGMENTO = {"stack": "pila", "data": "datos", "code": "codigo"}
ANALIZADORES = {"pila": analizar_pila, "datos": analizar_datos, "codigo": analizar_codigo}

# Una fila de resultado: (número de línea, texto original, "Correcta" | "Incorrecta" | "", causa)
Fila = tuple[int, str, str, str]


def prelectura_etiquetas(lineas_crudas: list[str]) -> dict[str, int]:
    """Busca cada definición 'etiqueta:' (nombre -> primera línea) para explicar los saltos hacia adelante."""
    encontradas: dict[str, int] = {}
    for numero, cruda in enumerate(lineas_crudas, 1):
        coincidencia = ER_DEF_ETIQUETA.match(quitar_comentarios(cruda))
        if coincidencia:
            encontradas.setdefault(coincidencia.group(1).upper(), numero)
    return encontradas


def _parece_encabezado(limpia: str, elems: list[str]) -> bool:
    """Líneas que intentan (y fallan) ser un encabezado de segmento."""
    minuscula = [elem.lower() for elem in elems]
    if ":" in limpia or (len(minuscula) >= 2 and minuscula[1] in ("db", "dw", "equ")):
        return False
    return any("segment" in elem for elem in minuscula) or minuscula[0] in (
        "code", "data", "stack", ".code", ".data", ".stack")


class Analizador:
    """Analizador de una sola pasada: cada línea se juzga con lo definido antes de ella."""

    def __init__(self, lineas_crudas: list[str]) -> None:
        self.lineas_crudas = lineas_crudas
        self.tabla = TablaSimbolos()
        self.tabla.etiquetas_futuras = prelectura_etiquetas(lineas_crudas)
        self.segmentos: dict[str, list[dict]] = {"pila": [], "datos": [], "codigo": []}
        self.actual: str | None = None
        self.terminado = False                 # ya apareció 'end'
        self.filas: list[Fila] = []

    def ejecutar(self) -> None:
        """Analiza cada línea del programa."""
        for numero, cruda in enumerate(self.lineas_crudas, 1):
            limpia = quitar_comentarios(cruda).strip()
            if not limpia:
                self.filas.append((numero, cruda, "", ""))
                continue
            ok, causa = self._linea(limpia, numero)
            self.filas.append((numero, cruda, "Correcta" if ok else "Incorrecta", causa))

    def _abrir(self, clase: str, numero: int) -> tuple[bool, str]:
        """Abre el segmento 'clase' (pila, datos o codigo)."""
        causa = ""
        if self.actual:
            causa = (f"falta 'ends' para cerrar el segmento de {NOMBRES_SEGMENTO[self.actual]} "
                     f"antes de abrir el de {NOMBRES_SEGMENTO[clase]}")
        elif self.segmentos[clase]:
            causa = f"el segmento de {NOMBRES_SEGMENTO[clase]} ya fue definido"
        self.segmentos[clase].append({"inicio": numero, "fin": None})
        self.actual = clase
        return (not causa), causa

    def _cerrar_segmento(self, elems: list[str], numero: int) -> tuple[bool, str]:
        """Línea 'ends'."""
        if len(elems) > 1:
            return False, "ends no lleva operandos"
        if not self.actual:
            return False, "ends no corresponde a ningún segmento abierto"
        self.segmentos[self.actual][-1]["fin"] = numero
        self.actual = None
        return True, ""

    def _fin(self, elems: list[str]) -> tuple[bool, str]:
        """Línea 'end' o 'end etiqueta'."""
        codigo = self.segmentos["codigo"]
        if self.actual:
            return False, f"'end' aparece dentro del segmento de {NOMBRES_SEGMENTO[self.actual]}: ciérrelo con 'ends'"
        if not codigo or codigo[-1]["fin"] is None:
            return False, "'end' debe ir después de cerrar el segmento de código con 'ends'"
        if len(elems) > 2:
            return False, "end admite como máximo el nombre de una etiqueta"
        if len(elems) == 2:
            fila = self.tabla.buscar(elems[1])
            if fila is None or fila["clase"] != "etiqueta":
                return False, f"'{elems[1]}' no es una etiqueta definida"
        self.terminado = True
        return True, ""

    def _linea(self, limpia: str, numero: int) -> tuple[bool, str]:
        """Dictamen de una línea sin comentarios -> (correcta, causa)."""
        if self.terminado:
            return False, "no se permiten líneas después de 'end'"
        if ER_ENCABEZADO_SEGMENTO.match(limpia):
            return self._abrir(PALABRA_A_SEGMENTO[limpia.split()[0][1:].lower()], numero)
        elems = dividir_linea(limpia)
        primero = elems[0].lower() if elems else ""
        if primero == "ends":
            return self._cerrar_segmento(elems, numero)
        if primero == "end":
            return self._fin(elems)
        if not elems:                       # solo separadores, p. ej. "," o ":"
            if self.actual == "codigo":
                return analizar_codigo(limpia, numero, self.tabla)
            return False, "la línea solo contiene separadores (',' o ':') y ningún elemento"
        if _parece_encabezado(limpia, elems):
            return False, f"encabezado de segmento no válido: {AYUDA_ENCABEZADO}"
        if not self.actual:
            return False, "línea fuera de un segmento (debe ir entre '.xxx segment' y 'ends')"
        return ANALIZADORES[self.actual](limpia, numero, self.tabla)

    def estructura(self) -> list[tuple[str, str]]:
        """Resumen de segmentos: (nombre del segmento, estado)."""
        salida = []
        for clase, nombre in NOMBRES_SEGMENTO.items():
            tramos = self.segmentos[clase]
            if not tramos:
                salida.append((nombre, "NO DEFINIDO"))
                continue
            textos = []
            for tramo in tramos:
                fin = tramo["fin"]
                textos.append(f"líneas {tramo['inicio']}-{fin}" if fin else
                             f"desde la línea {tramo['inicio']} SIN 'ends'")
            sufijo = "  (definido más de una vez)" if len(tramos) > 1 else ""
            salida.append((nombre, "; ".join(textos) + sufijo))
        return salida

    def completo(self) -> bool:
        """Verdadero cuando los tres segmentos existen exactamente una vez y están cerrados."""
        return all(len(s) == 1 and s[0]["fin"] for s in self.segmentos.values())
