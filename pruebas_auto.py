"""Pruebas automaticas: compara el resultado del analizador con las marcas ;OK / ;ERR.

Uso:  python pruebas_auto.py        (desde esta carpeta, sin dependencias externas)
"""

import re
import sys
from pathlib import Path

from analizador import Analizador
from analizador import leer_lineas_fuente

MARCA = re.compile(r";\s*(OK|ERR)\b")
AQUI = Path(__file__).resolve().parent
# plantilla.ens (profesor): unicas lineas esperadas como Correcta
PLANTILLA_OK = {1, 3, 7, 10, 12, 13, 16, 17, 21, 24, 25, 26, 29, 31, 40, 56, 67, 74, 75}


def analizar(nombre: str) -> Analizador:
    """Analiza un archivo .ens que está junto a este script."""
    analizador = Analizador(leer_lineas_fuente(AQUI / nombre))
    analizador.ejecutar()
    return analizador


def revisar_marcas(nombre: str) -> int:
    """Compara cada línea marcada; devuelve el número de diferencias."""
    analizador = analizar(nombre)
    malas = revisado = 0
    for numero, cruda, veredicto, causa in analizador.filas:
        encontradas = MARCA.search(cruda)
        if not encontradas or not veredicto:          # sin marca, o linea vacia/solo comentario
            continue
        revisado += 1
        esperado = "Correcta" if encontradas.group(1) == "OK" else "Incorrecta"
        if veredicto != esperado:
            malas += 1
            print(f"  FALLA {nombre}:{numero}: esperado {esperado}, obtenido {veredicto or '-'} "
                  f"| {cruda.strip()[:50]} | {causa}")
    print(f"{nombre}: {revisado} lineas marcadas, {malas} fallas")
    return malas


def revisar_plantilla() -> int:
    """plantilla.ens: solo las líneas acordadas son Correcta."""
    analizador = analizar("plantilla.ens")
    malas = 0
    for numero, cruda, veredicto, causa in analizador.filas:
        if not veredicto:
            continue
        esperado = "Correcta" if numero in PLANTILLA_OK else "Incorrecta"
        if veredicto != esperado:
            malas += 1
            print(f"  FALLA plantilla.ens:{numero}: esperado {esperado}, obtenido {veredicto}")
    print(f"plantilla.ens: {sum(1 for r in analizador.filas if r[2])} lineas, {malas} fallas")
    return malas


def revisar_estructura_y_simbolos() -> int:
    """Identificación de segmentos y contenido de la tabla de símbolos."""
    malas = 0
    ok = analizar("correcto_equipo3.ens")
    filas = {r["nombre"]: (r["tipo"], r["valor"], r["tamano"]) for r in ok.tabla.filas()}
    esperado = {
        "msg": ("Variable byte (db)", '"Hola mundo$"', 11),
        "n_hex": ("Variable byte (db)", "0FFh", 1),
        "n_neg": ("Variable byte (db)", "-5", 1),
        "vw2": ("Variable palabra (dw)", "-2", 2),
        "w_bin": ("Variable palabra (dw)", "1111000011110000b", 2),
        "buf": ("Variable byte (db)", "10 dup('x')", 10),
        "tabla": ("Variable palabra (dw)", "5 dup(1000)", 10),
        "k_hex": ("Constante (equ)", "0Ah", 2),
        "inicio": ("Etiqueta", "-", None),
    }
    for nombre, quiere in esperado.items():
        if filas.get(nombre) != quiere:
            malas += 1
            print(f"  FALLA tabla de simbolos {nombre}: esperado {quiere}, obtenido {filas.get(nombre)}")
    if not ok.completo():
        malas += 1
        print("  FALLA correcto_equipo3.ens: la estructura debia estar completa")
    roto = analizar("estructura_incompleta.ens")
    if roto.completo() or dict(roto.estructura())["código"] != "NO DEFINIDO":
        malas += 1
        print("  FALLA estructura_incompleta.ens: debia detectar segmento de codigo ausente")
    print(f"estructura y tabla de simbolos: {malas} fallas")
    return malas


def principal() -> int:
    """Ejecuta todas las revisiones; termina con código 1 si alguna falla."""
    fallas = revisar_marcas("correcto_equipo3.ens") + revisar_marcas("errores_equipo3.ens")
    fallas += revisar_marcas("estructura_incompleta.ens") + revisar_plantilla()
    fallas += revisar_estructura_y_simbolos()
    print("\nRESULTADO:", "TODO CORRECTO" if fallas == 0 else f"{fallas} FALLAS")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(principal())
