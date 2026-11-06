# Informe Técnico de Hallazgos y Correcciones — Fases 1, 2 y 3 (Equipo 3)

Este documento recopila y analiza las observaciones, discrepancias y errores detectados a partir de las 5 capturas de pantalla y los mensajes de revisión proporcionados.

---

## 1. Mapeo y Contexto de las Capturas

| Captura | Contenido en Pantalla | Mensajes de Revisión Asociados |
|---|---|---|
| **Imagen 1** | Líneas 0022–0034 (`MOV AX, BX` y `ADD CX, DX` marcadas como error por no ser de las 20 instrucciones asignadas). | — |
| **Imagen 2** | • Arriba: Tabla de símbolos con `mascara_hex` (`dw`).<br>• Abajo: Elementos léxicos iniciales (`[001] .stack segment` como Pseudoinstrucción). | • *"Máscara hex no considerar por tamaño"* (2:12 p.m.)<br>• *"Segment incorrecto"* (2:16 p.m.)<br>• *"Solo en .data."* (2:16 p.m.) |
| **Imagen 3** | Elementos léxicos 015 a 044 (`[029]` comillas abiertas, `[039] 0` como Pseudoinstrucción, `BD`/`Wd` como Símbolos). | • *"No separa binarias ni hexa"* (2:16 p.m.)<br>• *"Comillas"* (2:16 p.m.) |
| **Imagen 4** | • Arriba: Elementos léxicos 045 a 066 (`45H` como Símbolo, binarios).<br>• Abajo: Tabla de símbolos con valores `69`, `31`, `170`. | • *"No hay 170 69 31"* (2:21 p.m.) |
| **Imagen 5** | Análisis sintáctico de líneas 0017–0027 (`tecla`, `simbolo`, `ss1`, `ss2`, `ss3`). | • *"Que los valores iniciales no cambien en la tabla de símbolos"* (2:22 p.m.) |

---

## 2. Detalle de Hallazgos y Causas Raíz

### Hallazgo 1: Alteración de valores iniciales en la Tabla de Símbolos ("No hay 170 69 31")
* **Evidencia:** En la Imagen 4 (abajo) la tabla muestra valores iniciales `69`, `31` y `170`. El revisor señala: *"No hay 170 69 31"* y *"Que los valores iniciales no cambien en la tabla de símbolos"*.
* **Causa Raíz:** En `constantes.py` (`leer_elemento`), los números son analizados con `leer_numero` (que los transforma a tipo `int` en Python) y al guardarlos en la tabla se hace `str(valor)`.
  * `045H` (hexadecimal) se convirtió en `69`.
  * `000011111b` (o `00001111b`) se convirtió en `31`.
  * `10101010b` (binario) se convirtió en `170`.
* **Criterio Correcto:** La tabla de símbolos debe preservar el **literal crudo** tal como el usuario lo escribió en el código fuente (`"045H"`, `"000011111b"`, `"10101010b"`), sin transformarlo a base decimal.

---

### Hallazgo 2: Directivas de Segmento Inválidas ("Segment incorrecto", "Solo en .data.")
* **Evidencia:** En la Imagen 2 (abajo), el elemento `[001]` clasifica `.stack segment` como `Pseudoinstrucción`. El revisor anota: *"Segment incorrecto"* y *"Solo en .data."*.
* **Causa Raíz:** En `configuracion.py`, la expresión regular `ER_PALABRA_COMPUESTA` y `ER_SEGMENTO_COMPUESTO` reconoce de forma unificada:
  ```python
  r"\.(?:code|data|stack)[ \t]+segment"
  ```
  En la sintaxis simplificada del 8086:
  * `.stack` no se acompaña de la palabra `segment` (es simplemente `.stack [tam]`, o en sintaxis completa `pila segment`).
  * Al fusionar `.stack segment` como un token indivisible válido, el analizador sintáctico no puede señalar el error sintáctico de haber escrito `segment` después de `.stack`.
* **Criterio Correcto:** La palabra `segment` solo debe ser admitida después de nombres de segmento de datos (o `.data segment` / `data segment` según especificación), rechazando `.stack segment`.

---

### Hallazgo 3: Máscara Hexadecimal y Validación de Tamaño ("Máscara hex no considerar por tamaño")
* **Evidencia:** En la Imagen 2 (arriba), la tabla de símbolos contiene `mascara_hex | Variable palabra (dw)`. El revisor indica: *"Máscara hex no considerar por tamaño"*.
* **Causa Raíz:** En `demo_equipo3.ens`, la definición es:
  ```asm
  mascara_hex dw 0FFh
  ```
  `0FFh` ocupa 1 byte (2 dígitos hex). Aunque numéricamente 255 cabe en una palabra (16 bits), en ensamblador estricto o según la regla de la cátedra:
  * Si una variable se define como `dw`, un valor de 8 bits sin rellenar a 16 bits (`00FFh`) o con tamaño dispar debe ser rechazado, o bien no debe agregarse a la tabla de símbolos si no cumple con la correspondencia de tamaño exacta de la directiva.

---

### Hallazgo 4: Clasificación Anómala de Constante `0` como `Pseudoinstrucción` (Elemento [039])
* **Evidencia:** En la Imagen 3, el elemento `[039] | 0` aparece clasificado como `Pseudoinstrucción`, mientras que `[036] | 0` y `[042] | 0` aparecen correctamente como `Constante Decimal`.
* **Causa Raíz:** Inconsistencia en la separación léxica o en el clasificador de elementos tras líneas con errores sintácticos o espacios anómalos en `plantilla.ens` (`tecla db 0`). Debe garantizarse que cualquier dígito aislado siempre se resuelva como `Constante Decimal`.

---

### Hallazgo 5: Clasificación y Separación de Constantes Hexadecimales y Binarias ("No separa binarias ni hexa")
* **Evidencia:** En la Imagen 4 (arriba), el elemento `[054] | 45H` es clasificado como `Símbolo` en lugar de marcarse como número hexadecimal o número mal formado. El revisor comenta: *"No separa binarias ni hexa"*.
* **Causa Raíz:**
  * Las expresiones regulares actuales exigen que un hexadecimal inicie con un cero cuando contiene letras (`045H`), pero si no lleva letras (`45H`) o no cumple la regla de inicio, el motor caía en `ER_SIMBOLO` o no separaba correctamente tokens numéricos pegados o delimitados.
  * El escáner y el clasificador deben distinguir explícitamente constantes numéricas inválidas (e.g., `45H`, `FFh`, `102b`) y no catalogarlas erróneamente como identificadores (`Símbolo`).

---

### Hallazgo 6: Tratamiento de Cadenas sin Cerrar ("Comillas")
* **Evidencia:** En la Imagen 3, el elemento `[029] | "presiona key...$" una vez` se agrupa en un único bloque clasificado como `Elemento no identificado`. El revisor comenta: *"Comillas"*.
* **Causa Raíz:** Al no encontrar la comilla de cierre (`"`), el escáner absorbe todo el resto de la línea (`una vez`). Debe aislarse la constante cadena abierta para que el reporte de error indique con precisión la falta de comillas de cierre de la cadena antes de analizar los elementos subsecuentes.

---

### Hallazgo 7: Rechazo de Instrucciones Básicas del 8086 en Código (`MOV`, `ADD`)
* **Evidencia:** En la Imagen 1, `MOV AX, BX` y `ADD CX, DX` son reportadas como:
  `>> Causa: 'MOV' no es una de las 20 instrucciones asignadas`
* **Causa Raíz:** El archivo `demo_equipo3.ens` y `plantilla.ens` utilizan instrucciones esenciales del 8086 (`MOV`, `ADD`, `INT`) que no forman parte de las 20 instrucciones particulares asignadas al Equipo 3. Al aplicar la regla estricta de la Fase 2, todas estas líneas se marcan como `Incorrecta`. Debe evaluarse si la especificación exige rechazar toda instrucción ajena a las 20 o si debe existir un modo compatible para ensamblar programas reales de prueba.

---

## 3. Plan de Acción Propuesto (Pendiente de Aprobación)

1. **Ajuste en `constantes.py` / `sintaxis_datos.py`:**
   * Modificar `leer_elemento` para retornar el valor original en formato de cadena (literal exacto del código fuente) para el campo `valor` de la tabla de símbolos, manteniendo la validación de rango numérico en paralelo.
2. **Ajuste en `configuracion.py` / `escaner.py`:**
   * Desvincular `.stack segment` de las pseudoinstrucciones compuestas válidas para que `.stack` sea evaluado individualmente y marque error sintáctico si se le agrega `segment`.
   * Refinar las expresiones regulares de binarios y hexadecimales para que constantes como `45H` no sean clasificadas como `Símbolo`.
3. **Ajuste en `clasificador.py`:**
   * Auditar la prioridad de clasificación para garantizar que `'0'` nunca pueda clasificarse como `Pseudoinstrucción`.
4. **Verificación de pruebas:**
   * Generar pruebas unitarias específicas con pytest para cada uno de los 7 casos identificados.
