"""Colores, fuentes y componentes reutilizables de la interfaz gráfica."""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

COLOR = {
    "fondo": "#f3f4f6",
    "superficie": "#ffffff",
    "borde": "#e5e7eb",
    "texto": "#111827",
    "tenue": "#6b7280",
    "barra": "#1e293b",
    "barra_texto": "#f8fafc",
    "barra_tenue": "#94a3b8",
    "acento": "#2563eb",
    "acento_hover": "#1d4ed8",
    "acento_suave": "#dbeafe",
    "ok": "#15803d",
    "ok_fondo": "#ecfdf3",
    "error": "#b91c1c",
    "error_fondo": "#fef2f2",
    "zebra": "#f9fafb",
}

# Color del texto de cada categoría léxica
COLOR_CATEGORIA = {
    "Instrucción": "#1d4ed8",
    "Pseudoinstrucción": "#7c3aed",
    "Registro (16 bits)": "#0f766e",
    "Registro (8 bits)": "#0f766e",
    "Registro de Segmento": "#0f766e",
    "Constante Decimal": "#b45309",
    "Constante Hexadecimal": "#b45309",
    "Constante Binaria": "#b45309",
    "Constante Carácter": "#a16207",
    "Símbolo": "#374151",
    "Elemento no identificado": "#b91c1c",
}

FUENTE = "Segoe UI"
FUENTE_CODIGO = "Consolas"


def configurar_estilos(raiz: tk.Tk) -> None:
    """Aplica la fuente y el tema visual a todos los widgets ttk."""
    for nombre in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
        tkfont.nametofont(nombre).configure(family=FUENTE, size=10)
    raiz.configure(bg=COLOR["fondo"])

    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    estilo.configure(".", background=COLOR["fondo"], foreground=COLOR["texto"], font=(FUENTE, 10))
    estilo.configure("Superficie.TFrame", background=COLOR["superficie"])
    estilo.configure("Superficie.TLabel", background=COLOR["superficie"])
    estilo.configure("Tenue.TLabel", background=COLOR["superficie"], foreground=COLOR["tenue"])
    estilo.configure("Titulo.TLabel", background=COLOR["superficie"], font=(FUENTE, 11, "bold"))
    estilo.configure("Superficie.TRadiobutton", background=COLOR["superficie"])
    estilo.map("Superficie.TRadiobutton", background=[("active", COLOR["superficie"])])

    estilo.configure("TButton", padding=(12, 6), relief="flat", borderwidth=0,
                     background=COLOR["superficie"], foreground=COLOR["texto"])
    estilo.map("TButton", background=[("active", COLOR["borde"])])
    estilo.configure("Acento.TButton", background=COLOR["acento"], foreground="#ffffff",
                     font=(FUENTE, 10, "bold"))
    estilo.map("Acento.TButton", background=[("active", COLOR["acento_hover"])])
    estilo.configure("Barra.TButton", background="#334155", foreground=COLOR["barra_texto"])
    estilo.map("Barra.TButton", background=[("active", "#475569"), ("disabled", "#273449")],
               foreground=[("disabled", COLOR["barra_tenue"])])

    estilo.configure("TNotebook", background=COLOR["fondo"], borderwidth=0, tabmargins=(0, 0, 0, 0))
    estilo.configure("TNotebook.Tab", padding=(18, 8), background=COLOR["fondo"],
                     foreground=COLOR["tenue"], borderwidth=0, font=(FUENTE, 10, "bold"))
    estilo.map("TNotebook.Tab",
               background=[("selected", COLOR["superficie"])],
               foreground=[("selected", COLOR["acento"])])

    estilo.configure("Treeview", background=COLOR["superficie"], fieldbackground=COLOR["superficie"],
                     foreground=COLOR["texto"], rowheight=28, borderwidth=0, font=(FUENTE, 10))
    estilo.map("Treeview", background=[("selected", COLOR["acento_suave"])],
               foreground=[("selected", COLOR["texto"])])
    estilo.configure("Treeview.Heading", background=COLOR["fondo"], foreground=COLOR["tenue"],
                     font=(FUENTE, 9, "bold"), relief="flat", padding=(8, 6))
    estilo.map("Treeview.Heading", background=[("active", COLOR["borde"])])
    estilo.configure("TCombobox", padding=4)
    estilo.configure("TEntry", padding=4)
    estilo.configure("Vertical.TScrollbar", background=COLOR["fondo"], troughcolor=COLOR["superficie"],
                     borderwidth=0, arrowsize=12)


def crear_tabla(padre: tk.Widget, columnas: list[tuple[str, str, int, bool]]) -> ttk.Treeview:
    """Tabla con barra de desplazamiento. columnas: (id, título, ancho, se estira)."""
    marco = ttk.Frame(padre, style="Superficie.TFrame")
    marco.pack(fill="both", expand=True)
    tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings", selectmode="browse")
    for ident, titulo, ancho, estira in columnas:
        tabla.heading(ident, text=titulo, anchor="w")
        tabla.column(ident, width=ancho, minwidth=40, stretch=estira, anchor="w")
    barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    tabla.tag_configure("zebra", background=COLOR["zebra"])
    return tabla


def tarjeta(padre: tk.Widget, titulo: str) -> tk.Label:
    """Tarjeta de resumen (título pequeño y valor grande); devuelve la etiqueta del valor."""
    marco = tk.Frame(padre, bg=COLOR["superficie"], highlightthickness=1,
                     highlightbackground=COLOR["borde"], padx=16, pady=10)
    marco.pack(side="left", fill="x", expand=True, padx=(0, 10))
    tk.Label(marco, text=titulo.upper(), bg=COLOR["superficie"], fg=COLOR["tenue"],
             font=(FUENTE, 8, "bold")).pack(anchor="w")
    valor = tk.Label(marco, text="—", bg=COLOR["superficie"], fg=COLOR["texto"], font=(FUENTE, 18, "bold"))
    valor.pack(anchor="w")
    return valor
