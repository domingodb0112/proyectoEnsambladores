# Ensamblador 8086

Analiza programas `.ens` (sintaxis de Emu8086 4.08):

1. **Léxico:** separa y clasifica cada elemento.
2. **Sintáctico y semántico:** marca cada línea como Correcta o Incorrecta, con su causa.
3. **Tabla de símbolos:** símbolo, tipo, valor inicial y tamaño.

Instrucciones soportadas: `CLD CLI NOP POPA AAD AAM MUL INC IDIV SAR TEST RCL XCHG JB JE JNLE JNP JP JCXZ JZ`.

## Uso
```powershell
python principal.py        # abre la ventana (Python 3.10+)
python pruebas_auto.py     # pruebas automáticas
compilar_exe.bat           # genera ensamblador.exe (usa Python 3.10 si lo tiene, pesa menos)
```

## Archivos de prueba
- `correcto_equipo3.ens`: todas las líneas son correctas.
- `errores_equipo3.ens`: cada línea marcada con `;OK` o `;ERR`.
- `estructura_incompleta.ens`: segmentos mal cerrados o faltantes.
- `plantilla.ens`: plantilla del profesor.
