# UAEMex · Ensambladores (Semestre 2026B) — Proyecto Ensamblador · Equipo 3

Analizador con interfaz de escritorio para ensamblador 8086 con sintaxis de **Emu8086 4.08**.

| Función | Qué hace | Valor |
|---|---|---|
| 1 | Análisis lexicográfico: separa e identifica los elementos del `.ens` | 20% |
| 2 | Análisis sintáctico y semántico: cada línea **Correcta** / **Incorrecta** con su causa | 30% |
| 3 | Tabla de símbolos (símbolo, tipo, valor inicial, tamaño) | 3% |

Instrucciones soportadas (únicas que se aceptan como instrucción):
`CLD`, `CLI`, `NOP`, `POPA`, `AAD`, `AAM`, `MUL`, `INC`, `IDIV`, `SAR`, `TEST`, `RCL`, `XCHG`, `JB`, `JE`, `JNLE`, `JNP`, `JP`, `JCXZ`, `JZ`.

## Ejecución
Requiere Python 3.10 o superior (tkinter viene incluido):
```powershell
python principal.py
```
Se abre una ventana. O con el ejecutable `ensamblador.exe` (se genera con `compilar_exe.bat` y se coloca junto a los `.ens`).
Pasos detallados y qué esperar en cada archivo: **`GUIA_RAPIDA.md`**. Reglas completas y decisiones: **`Especificacion_Funciones_2_3_Equipo3.md`**.

## Archivos
| Archivo | Función |
|---|---|
| `principal.py` | Punto de entrada: abre la ventana |
| `interfaz.py`, `interfaz_estilo.py` | Ventana (pestañas, tablas, filtros) y sus colores/estilos |
| `analisis.py` | Lee el `.ens` y ejecuta las Funciones 1, 2 y 3 para la ventana |
| `analizador.py` | Estructura de segmentos y dictamen por línea |
| `sintaxis_datos.py` | Líneas de pila y de datos |
| `sintaxis_codigo.py`, `reglas_codigo.py` | Línea de código: etiquetas, instrucciones y reglas de operandos |
| `analisis_operandos.py`, `operandos_memoria.py`, `operando.py` | Operandos: registros, inmediatos, memoria y corchetes |
| `constantes.py`, `nombres.py`, `tabla_simbolos.py` | Constantes con signo y rangos, nombres reservados, tabla de símbolos |
| `configuracion.py`, `escaner.py`, `clasificador.py` | Léxico (Función 1), configuración y utilidades de texto |
| `pruebas_auto.py` | Pruebas automáticas contra las marcas `;OK` / `;ERR` |
| `ensamblador.spec`, `compilar_exe.bat` | Generación del `.exe` con PyInstaller |

Archivos de prueba `.ens`: `correcto_equipo3.ens`, `errores_equipo3.ens`, `estructura_incompleta.ens`, `plantilla.ens` (profesor), `demo_equipo3.ens` (19 de las 20 instrucciones y errores léxicos; `JNP` se ve en `prueba_compuestos.ens`), `sum5.ens`, `prueba_compuestos.ens`.

## Lo que no se verificó
No se ejecutó Emu8086 4.08. Las reglas siguen su ayuda y la tabla del profesor; los cuatro supuestos que conviene confirmar compilando están en la sección 8 de la especificación y se ajustan en `configuracion.py`.
