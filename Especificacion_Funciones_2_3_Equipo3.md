# UAEMex — Ensambladores (Semestre 2026B)
## Proyecto Funciones 2 y 3: Análisis sintáctico y semántico + Tabla de símbolos — Equipo 3

**Valor:** 33% = 30% identificación de líneas correctas/incorrectas (Función 2) + 3% llenado de la tabla de símbolos (Función 3).
**Referencia de sintaxis:** ayuda de Emu8086 versión 4.08 y la tabla de codificación del profesor (Tablas definitivas 2020A).
**Entrega:** código fuente y ejecutable en `.zip` menor a 5 MB; todos los integrantes lo envían.

---

### 1. Qué hace el programa
En una ventana de escritorio, para cada línea del programa fuente (`.ens`) muestra el texto original y, frente a él, **Correcta** o **Incorrecta**; si es incorrecta, agrega la **causa** en lenguaje claro. En otra pestaña muestra la **tabla de símbolos** (símbolo, tipo, valor inicial, tamaño) y la identificación de los tres segmentos.

El análisis es de **una sola pasada**: cada línea se juzga con lo que ya se definió antes de ella.

### 2. Estructura de segmentos
- Encabezados válidos: `.stack segment`, `.data segment`, `.code segment`. Cada uno se cierra con `ends`.
- Un encabezado mal escrito (`.stacks segment`, `data segment`, `datasegment`, `code`) es Incorrecto y no abre segmento.
- Una línea fuera de un segmento es Incorrecta.
- Si falta `ends`, el segmento se repite o falta alguno de los tres, se reporta en el resumen de segmentos: *Identificación de segmentos: INCOMPLETA*.
- `end` (o `end etiqueta`) es válido una sola vez, después de cerrar el segmento de código; después de `end` no se permiten más líneas.

### 3. Segmento de pila
Única forma válida: `dw <cantidad> dup(<constante>)`
- `cantidad`: constante numérica de palabra **sin signo** (0 a 65535).
- `constante`: numérica de palabra **con/sin signo** (−32768 a 65535).

### 4. Segmento de datos
| Forma | Reglas |
|---|---|
| `símbolo db 'A'` / `"texto"` | Carácter o cadena entre comillas. Tamaño = número de caracteres. |
| `símbolo db <byte>` | Numérica con/sin signo: −128 a 255. |
| `símbolo db n dup('c')` | `n` palabra sin signo; dentro de `dup`, un solo carácter. |
| `símbolo db n dup(<byte>)` | Numérica con/sin signo. |
| `símbolo dw <palabra>` | Numérica con/sin signo: −32768 a 65535. |
| `símbolo dw n dup(<palabra>)` | `n` palabra sin signo. |
| `símbolo equ <palabra>` | Numérica con/sin signo. |

Constantes numéricas: decimal (`25`, `45d`), hexadecimal (inicia con dígito y termina en `h`: `0FFh`; `FFh` es inválida), binaria (`1010b`; `102b` es inválida), todas con signo opcional.
Nombres: inician con letra, `_`, `@` o `?`; no pueden ser instrucciones, registros ni pseudoinstrucciones; no se repiten (sin distinguir mayúsculas).

### 5. Segmento de código — las 20 instrucciones
| Instrucciones | Sintaxis aceptada |
|---|---|
| `CLD CLI NOP POPA AAD AAM` | Sin operandos |
| `MUL INC IDIV` | `registro` \| `memoria` |
| `SAR RCL` | `registro\|memoria , 1` \| `, CL` \| `, inmediato (0 a 255)` |
| `TEST` | `reg,reg` \| `reg,mem` \| `mem,reg` \| `reg,inm` \| `mem,inm` |
| `XCHG` | `reg,reg` \| `reg,mem` \| `mem,reg` |
| `JB JE JNLE JNP JP JCXZ JZ` | Una etiqueta **definida previamente** |

Verificaciones semánticas:
1. **Número de operandos** correcto (y sin comas de más o de menos).
2. **Elementos correctos:** registros válidos, constantes bien formadas, variables y constantes definidas, corchetes con combinaciones válidas del 8086 (BX o BP con SI o DI, más desplazamiento).
3. **Mismo tamaño** de operandos (8 contra 16 bits); el inmediato debe caber en el tamaño del destino; no hay memoria con memoria.
4. **Etiquetas de salto definidas previamente.**
5. **Tamaño de memoria:** sale del tipo de la variable (`db` = 8 bits, `dw` = 16) o de `byte ptr` / `word ptr`; un `[bx]` sin tamaño y sin registro que lo fije es ambiguo → Incorrecto.
6. Cualquier instrucción fuera de las 20 (`MOV`, `INT`, `RET`, `JMP`…) es **Incorrecta**.
7. Etiquetas: `nombre:` solo o seguido de una instrucción; los dos puntos no se escriben en operandos (`jz fin:` es incorrecto).

### 6. Tabla de símbolos
| Campo | Contenido |
|---|---|
| Símbolo | Nombre como se escribió la primera vez |
| Tipo | Variable byte (db), Variable palabra (dw), Constante (equ) o Etiqueta |
| Valor | Valor inicial **tal como se escribió** en el fuente, sin convertir de base (`045H`, `10101010b`, `"texto"`, `n dup(valor)`); `-` en etiquetas |
| Tamaño | Bytes que ocupa (`dup` y cadenas: el total); `equ` = 2; `-` en etiquetas |

Solo se agregan símbolos de **líneas correctas**. No se registra dirección de memoria en esta entrega.

### 7. Decisiones de diseño y su justificación
1. **Salto a etiqueta no definida previamente = Incorrecto** (también si se define más adelante).
   - Lo exige el enunciado (regla 4) y la plantilla del profesor lo prueba (`jz fin`, `jmp nex`).
   - Permite analizar en una sola pasada y llenar la tabla en orden.
   - Atrapa etiquetas mal escritas en el momento.
   - Costo: los ensambladores reales sí aceptan saltos hacia adelante (resuelven en una segunda pasada), así que es una restricción del proyecto, no del lenguaje. El mensaje distingue "se define después (línea N)" de "no existe".
2. **Instrucciones fuera de las 20 = Incorrectas**, porque la sintaxis a verificar es la de las instrucciones asignadas al equipo.
3. **Constantes con signo** se validan en esta fase aunque la Fase 1 las marcaba como no identificadas (`-1`): el signo se interpreta en el análisis sintáctico y la Fase 1 no cambia.
4. **Valor = valor inicial literal** (no se convierte a decimal), sin dirección de memoria.
5. **Una sola causa por línea** (la primera, de izquierda a derecha).

### 8. Supuestos a confirmar en Emu8086 4.08
Estos puntos se tomaron de la ayuda del emulador y de la tabla del profesor, pero **no se probaron compilando en Emu8086**. Si alguno difiere, se cambia en `configuracion.py`:

| Supuesto | Dónde ajustarlo |
|---|---|
| `SAR/RCL registro, inmediato` con valores 0 a 255 es válido | `DESPLAZAMIENTO_MAX_INMEDIATO` (poner 1 para aceptar solo el 1) |
| `?` (sin inicializar) no está en la sintaxis pedida | `PERMITIR_INTERROGACION` (poner `True` para aceptarlo) |
| `[bx]` sin `byte ptr`/`word ptr` y sin registro que fije el tamaño es error | `reglas_codigo.py` (`AMBIGUO`) |
| `end` / `end etiqueta` es válido al final | `analizador.py` (`_fin`) |
