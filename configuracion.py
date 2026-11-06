"""Configuración del ensamblador 8086: palabras reservadas, expresiones regulares y rangos."""

import re

# Las 20 instrucciones que reconoce el ensamblador (únicas clasificadas como 'Instrucción')
INSTRUCCIONES_SOPORTADAS: frozenset[str] = frozenset({
    "CLD", "CLI", "NOP", "POPA", "AAD", "AAM", "MUL", "INC", "IDIV", "SAR",
    "TEST", "RCL", "XCHG", "JB", "JE", "JNLE", "JNP", "JP", "JCXZ", "JZ"
})

# Resto de instrucciones del 8086: son palabras reservadas, pero se clasifican como 'Símbolo'
OTRAS_INSTRUCCIONES_8086: frozenset[str] = frozenset({
    "AAA", "AAS", "ADC", "ADD", "AND", "CALL", "CBW", "CLC", "CMC", "CMP",
    "CMPS", "CMPSB", "CMPSW", "CWD", "DAA", "DAS", "DEC", "DIV", "ESC", "HLT",
    "IN", "INT", "INTO", "IRET", "JA", "JAE", "JBE", "JC", "JG", "JGE", "JL",
    "JLE", "JMP", "JNA", "JNAE", "JNB", "JNBE", "JNC", "JNE", "JNG", "JNGE",
    "JNL", "JNO", "JNS", "JNZ", "JO", "JPE", "JPO", "JS", "LAHF",
    "LDS", "LEA", "LES", "LOCK", "LODS", "LODSB", "LODSW", "LOOP", "LOOPE",
    "LOOPNE", "LOOPNZ", "LOOPZ", "MOV", "MOVS", "MOVSB", "MOVSW", "NEG", "NOT",
    "OR", "OUT", "POP", "POPF", "PUSH", "PUSHA", "PUSHF", "RCR", "REP",
    "REPE", "REPNE", "REPNZ", "REPZ", "RET", "RETF", "RETN", "ROL", "ROR",
    "SAHF", "SAL", "SBB", "SCAS", "SCASB", "SCASW", "SHL", "SHR", "STC",
    "STD", "STI", "STOS", "STOSB", "STOSW", "SUB", "WAIT", "XLAT", "XLATB", "XOR"
})

# Pseudoinstrucciones simples (las compuestas se reconocen con expresiones regulares)
DIRECTIVAS: frozenset[str] = frozenset({
    "SEGMENT", "ENDS", "END", "ASSUME", "ORG", "DB", "DW", "DD", "EQU",
    "PROC", "ENDP", "MACRO", "ENDM", ".MODEL", ".CODE", ".DATA", ".STACK",
    "TITLE", "PAGE", "PUBLIC", "EXTRN", "ALIGN", "OFFSET", "NEAR", "FAR"
})

REGISTROS_16: frozenset[str] = frozenset({"AX", "BX", "CX", "DX", "SP", "BP", "SI", "DI"})
REGISTROS_8: frozenset[str] = frozenset({"AL", "AH", "BL", "BH", "CL", "CH", "DL", "DH"})
REGISTROS_SEG: frozenset[str] = frozenset({"CS", "DS", "SS", "ES"})

# --- Elementos compuestos (indivisibles) ---------------------------------------
# Entre las dos palabras puede haber cualquier cantidad de espacios o tabuladores.
# El límite final evita falsos positivos (p. ej. "byte ptr_x"); un '[' pegado sí es válido.
_FIN_ER = r"(?![\w@?$])"
ER_PALABRA_COMPUESTA: re.Pattern[str] = re.compile(
    r"\.(?:code|data|stack)[ \t]+segment" + _FIN_ER + r"|(?:byte|word)[ \t]+ptr" + _FIN_ER,
    re.IGNORECASE,
)
ER_PTR_COMPUESTO: re.Pattern[str] = re.compile(r"^(?:byte|word)\s+ptr$", re.IGNORECASE)
ER_INICIO_DUP: re.Pattern[str] = re.compile(r"dup[ \t]*\(", re.IGNORECASE)

# --- Constantes y símbolos -----------------------------------------------------
ER_DECIMAL: re.Pattern[str] = re.compile(r"^[0-9]+[dD]?$")
ER_HEX_VALIDO: re.Pattern[str] = re.compile(r"^[0-9][0-9A-Fa-f]*[hH]$")
ER_HEX_INVALIDO: re.Pattern[str] = re.compile(r"^[a-fA-F][0-9a-fA-F]*[hH]$")
ER_BINARIO_VALIDO: re.Pattern[str] = re.compile(r"^[01]+[bB]$")
ER_BINARIO_INVALIDO: re.Pattern[str] = re.compile(r"^[0-9]+[bB]$")
ER_CADENA: re.Pattern[str] = re.compile(r'^(?:"[^"]*"|\'[^\']*\')$')
ER_SIMBOLO: re.Pattern[str] = re.compile(r"^[a-zA-Z_@?][a-zA-Z0-9_@?]*$")

# --- Fases 2 y 3 (sintaxis, semántica y tabla de símbolos) ---------------------
RANGO_BYTE: tuple[int, int] = (-128, 255)          # byte con/sin signo
RANGO_PALABRA: tuple[int, int] = (-32768, 65535)      # palabra con/sin signo
RANGO_CANTIDAD: tuple[int, int] = (0, 65535)          # palabra sin signo (cantidad de dup)
PERMITIR_INTERROGACION: bool = False   # '?' (sin inicializar) no está en la sintaxis pedida
DESPLAZAMIENTO_MAX_INMEDIATO: int = 255      # SAR/RCL con inmediato: contador 0..255 (Inm.byte)

INSTR_SIN_OPERANDOS: frozenset[str] = frozenset({"CLD", "CLI", "NOP", "POPA", "AAD", "AAM"})
INSTR_UN_OPERANDO: frozenset[str] = frozenset({"MUL", "INC", "IDIV"})
INSTR_DESPLAZAMIENTO: frozenset[str] = frozenset({"SAR", "RCL"})
INSTR_SALTO: frozenset[str] = frozenset({"JB", "JE", "JNLE", "JNP", "JP", "JCXZ", "JZ"})

ER_ENCABEZADO_SEGMENTO: re.Pattern[str] = re.compile(
    r"^\.(stack|data|code)[ \t]+segment$", re.IGNORECASE)
ER_PREFIJO_PTR: re.Pattern[str] = re.compile(
    r"^(byte|word)[ \t]+ptr(?![\w@?$])[ \t]*(.*)$", re.IGNORECASE | re.DOTALL)
