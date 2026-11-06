# Guía rápida — cómo ejecutar y probar el programa

## 1. Ejecutarlo
**Con Python (3.10 o superior)**, en PowerShell o en la terminal de VS Code, dentro de la carpeta del proyecto:
```powershell
python principal.py
```
**Con el ejecutable:** doble clic en `compilar_exe.bat` (genera `ensamblador.exe`), copiar el `.exe` junto a los `.ens` y abrirlo.

## 2. Usar la ventana
1. A la izquierda aparecen los `.ens` de la carpeta del programa: un clic abre el archivo. **Abrir archivo… (Ctrl+O)** busca uno en otra carpeta y **Recargar (F5)** lo vuelve a analizar después de editarlo.
2. Arriba, las tarjetas de resumen: líneas con código, correctas, incorrectas, símbolos y estado de los segmentos.
3. Pestañas:
   - **Código fuente:** el programa con cada línea marcada en verde (✔ Correcta) o rojo (✘ Incorrecta); los comentarios en gris.
   - **Análisis léxico (Función 1):** cada elemento con su clasificación; se puede filtrar por categoría o buscar texto.
   - **Análisis sintáctico (Función 2):** cada línea con Correcta/Incorrecta y su causa; filtro Todas/Correctas/Incorrectas. Al seleccionar una línea se ve la causa completa abajo; doble clic la muestra en el código fuente.
   - **Tabla de símbolos (Función 3):** símbolo, tipo, valor inicial (tal como se escribió) y tamaño, con el resumen de los tres segmentos a la derecha.

## 3. Qué probar y qué esperar
| Archivo | Qué demuestra | Resultado esperado |
|---|---|---|
| `correcto_equipo3.ens` | Las 20 instrucciones soportadas con todas las combinaciones válidas | 99 líneas, todas **Correcta**; 23 símbolos en la tabla; segmentos COMPLETA |
| `errores_equipo3.ens` | 159 líneas marcadas con `;OK` / `;ERR` | Cada línea coincide con su marca; cada incorrecta muestra su causa |
| `estructura_incompleta.ens` | Segmentos mal cerrados, repetidos y faltantes | Segmento de código **NO DEFINIDO**; identificación INCOMPLETA |
| `plantilla.ens` | La plantilla del profesor | 66 líneas con código: 19 Correctas, 47 Incorrectas; 11 símbolos |

Para la exposición, un recorrido corto: `plantilla.ens` (muestra encabezados, duplicados, `jz fin:`, `mov` fuera de las 20) → `correcto_equipo3.ens` → una parte de `errores_equipo3.ens`.

## 4. Prueba automática (sin abrir la ventana)
```powershell
python pruebas_auto.py
```
Compara cada línea marcada con `;OK` / `;ERR` contra el resultado del analizador, revisa la plantilla, la tabla de símbolos y la identificación de segmentos. Debe terminar con `RESULTADO: TODO CORRECTO`.

## 5. Probar con un archivo propio
Cree un `.ens` en la misma carpeta con tres segmentos:
```
.stack segment
    dw 128 dup(0)
ends

.data segment
    cont db 0
ends

.code segment
inicio:
    inc cont
    jz inicio
ends
end inicio
```
Resultado esperado: 12 líneas con código, todas Correcta; tabla con `cont` (Variable byte, 0, 1 byte) e `inicio` (Etiqueta).
