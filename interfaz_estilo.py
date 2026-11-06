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
    estilo.configure("Superficie.TRadiobutton", background=COLOR["superficie"])
    estilo.map("Superficie.TRadiobutton", background=[("active", COLOR["superficie"])])

    estilo.configure("TButton", padding=(12, 6), relief="flat", borderwidth=0,
                     background=COLOR["superficie"], foreground=COLOR["texto"])
    estilo.map("TButton", background=[("active", COLOR["borde"])])
    estilo.configure("Acento.TButton", background=COLOR["acento"], foreground="#ffffff",
                     font=(FUENTE, 10, "bold"))
    estilo.map("Acento.TButton", background=[("active", COLOR["acento_hover"])])

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


def crear_par_tablas(padre: tk.Widget, columnas_izq: list[tuple[str, str, int, bool]],
                     columnas_der: list[tuple[str, str, int, bool]]) -> tuple[ttk.Treeview, ttk.Treeview]:
    """Dos tablas lado a lado para comparar fila por fila.

    Comparten la barra de desplazamiento y la selección, así que una fila de la izquierda
    queda siempre frente a la fila de la derecha con el mismo identificador.
    """
    marco = ttk.Frame(padre, style="Superficie.TFrame")
    marco.pack(fill="both", expand=True)
    marco.columnconfigure(0, weight=1, uniform="lados")
    marco.columnconfigure(2, weight=1, uniform="lados")
    marco.rowconfigure(0, weight=1)

    tablas: list[ttk.Treeview] = []
    for col, columnas in enumerate((columnas_izq, columnas_der)):
        tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings", selectmode="browse")
        for ident, texto, ancho, estira in columnas:
            tabla.heading(ident, text=texto, anchor="w")
            tabla.column(ident, width=ancho, minwidth=40, stretch=estira, anchor="w")
        tabla.grid(row=0, column=col * 2, sticky="nsew")
        tabla.tag_configure("zebra", background=COLOR["zebra"])
        tablas.append(tabla)
    tk.Frame(marco, bg=COLOR["borde"], width=2).grid(row=0, column=1, sticky="ns", padx=6)
    barra = ttk.Scrollbar(marco, orient="vertical")
    barra.grid(row=0, column=3, sticky="ns")
    izquierda, derecha = tablas

    def mover(*argumentos: str) -> None:
        izquierda.yview(*argumentos)
        derecha.yview(*argumentos)

    def seguir(otra: ttk.Treeview):
        def actualizar(primero: str, ultimo: str) -> None:
            barra.set(primero, ultimo)
            if abs(otra.yview()[0] - float(primero)) > 1e-9:      # rueda del ratón en una tabla
                otra.yview_moveto(primero)
        return actualizar

    def copiar_seleccion(origen: ttk.Treeview, otra: ttk.Treeview):
        def actualizar(_evento: tk.Event) -> None:
            seleccion = origen.selection()
            if seleccion and otra.selection() != seleccion:
                otra.selection_set(seleccion)
                otra.see(seleccion[0])
        return actualizar

    barra.configure(command=mover)
    izquierda.configure(yscrollcommand=seguir(derecha))
    derecha.configure(yscrollcommand=seguir(izquierda))
    izquierda.bind("<<TreeviewSelect>>", copiar_seleccion(izquierda, derecha), add="+")
    derecha.bind("<<TreeviewSelect>>", copiar_seleccion(derecha, izquierda), add="+")
    return izquierda, derecha


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
