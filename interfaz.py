"""Ventana principal."""

import sys
import tkinter as tk
from collections import Counter
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from analizador import Resultado, analizar_archivo
from clasificador import INVALIDO
from escaner import quitar_comentarios
from interfaz_estilo import (
    COLOR, COLOR_CATEGORIA, FUENTE, FUENTE_CODIGO, configurar_estilos, crear_par_tablas, crear_tabla, tarjeta,
)

TODAS = "Todas las categorías"


def carpeta_inicial() -> Path:
    """Carpeta del programa (junto al .exe cuando está empaquetado)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def _tamano(tamano: int | None) -> str:
    if tamano is None:
        return "—"
    return f"{tamano} byte" if tamano == 1 else f"{tamano} bytes"


class Ventana:
    """Ventana de la aplicación."""

    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.resultado: Resultado | None = None
        self.carpeta = carpeta_inicial()
        self.archivos: list[Path] = []

        raiz.title("Ensamblador")
        raiz.geometry("1280x800")
        raiz.minsize(1050, 640)
        configurar_estilos(raiz)

        self._crear_barra_superior()
        cuerpo = tk.Frame(raiz, bg=COLOR["fondo"])
        cuerpo.pack(fill="both", expand=True, padx=16)
        self._crear_panel_archivos(cuerpo)
        self.principal = tk.Frame(cuerpo, bg=COLOR["fondo"])
        self.principal.pack(side="left", fill="both", expand=True)
        self._crear_vacio()
        self._crear_contenido()

        raiz.bind("<Control-o>", lambda _evento: self.abrir_dialogo())
        raiz.bind("<F5>", lambda _evento: self.recargar())
        self._listar_carpeta(self.carpeta)
        self._mostrar(self.vacio)


    def _crear_barra_superior(self) -> None:
        barra = tk.Frame(self.raiz, bg=COLOR["fondo"], padx=16, pady=10)
        barra.pack(fill="x")
        ttk.Button(barra, text="Abrir…", style="Acento.TButton", command=self.abrir_dialogo).pack(side="left")
        self.boton_recargar = ttk.Button(barra, text="Recargar", command=self.recargar, state="disabled")
        self.boton_recargar.pack(side="left", padx=8)
        self.nombre_archivo = tk.Label(barra, bg=COLOR["fondo"], fg=COLOR["texto"], font=(FUENTE, 11, "bold"))
        self.nombre_archivo.pack(side="left", padx=8)

    def _crear_panel_archivos(self, padre: tk.Frame) -> None:
        panel = tk.Frame(padre, bg=COLOR["superficie"], width=230, highlightthickness=1,
                         highlightbackground=COLOR["borde"])
        panel.pack(side="left", fill="y", padx=(0, 12), pady=(0, 12))
        panel.pack_propagate(False)
        self.lista = tk.Listbox(panel, activestyle="none", borderwidth=0, highlightthickness=0,
                                bg=COLOR["superficie"], fg=COLOR["texto"], font=(FUENTE, 10),
                                selectbackground=COLOR["acento_suave"], selectforeground=COLOR["texto"])
        self.lista.pack(fill="both", expand=True, padx=6, pady=6)
        self.lista.bind("<<ListboxSelect>>", self._al_elegir_archivo)
        ttk.Button(panel, text="Cambiar carpeta…", command=self._elegir_carpeta).pack(
            fill="x", padx=12, pady=(0, 12))

    def _crear_vacio(self) -> None:
        self.vacio = tk.Frame(self.principal, bg=COLOR["superficie"], highlightthickness=1,
                              highlightbackground=COLOR["borde"])
        centro = tk.Frame(self.vacio, bg=COLOR["superficie"])
        centro.place(relx=0.5, rely=0.45, anchor="center")
        ttk.Button(centro, text="Abrir archivo .ens", style="Acento.TButton",
                   command=self.abrir_dialogo).pack()

    def _crear_contenido(self) -> None:
        self.contenido = tk.Frame(self.principal, bg=COLOR["fondo"])
        tarjetas = tk.Frame(self.contenido, bg=COLOR["fondo"])
        tarjetas.pack(fill="x", pady=(0, 12))
        self.valor_lineas = tarjeta(tarjetas, "Líneas con código")
        self.valor_correctas = tarjeta(tarjetas, "Correctas")
        self.valor_incorrectas = tarjeta(tarjetas, "Incorrectas")
        self.valor_simbolos = tarjeta(tarjetas, "Símbolos")
        self.valor_segmentos = tarjeta(tarjetas, "Segmentos")

        self.pestanas = ttk.Notebook(self.contenido)
        self.pestanas.pack(fill="both", expand=True, pady=(0, 12))
        self._crear_pestana_fuente()
        self._crear_pestana_lexico()
        self._crear_pestana_sintaxis()
        self._crear_pestana_simbolos()

    def _nueva_pestana(self, titulo: str) -> ttk.Frame:
        marco = ttk.Frame(self.pestanas, style="Superficie.TFrame", padding=14)
        self.pestanas.add(marco, text=titulo)
        return marco

    def _crear_pestana_fuente(self) -> None:
        marco = self._nueva_pestana("Código fuente")
        self.pestana_fuente = marco
        contenedor = ttk.Frame(marco, style="Superficie.TFrame")
        contenedor.pack(fill="both", expand=True)
        self.codigo = tk.Text(contenedor, wrap="none", borderwidth=0, highlightthickness=0,
                              font=(FUENTE_CODIGO, 11), bg=COLOR["superficie"], fg=COLOR["texto"],
                              padx=8, pady=6, spacing1=2, spacing3=2, cursor="arrow")
        vertical = ttk.Scrollbar(contenedor, orient="vertical", command=self.codigo.yview)
        horizontal = ttk.Scrollbar(contenedor, orient="horizontal", command=self.codigo.xview)
        self.codigo.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        vertical.pack(side="right", fill="y")
        horizontal.pack(side="bottom", fill="x")
        self.codigo.pack(fill="both", expand=True)
        self.codigo.tag_configure("numero", foreground="#9ca3af")
        self.codigo.tag_configure("comentario", foreground=COLOR["tenue"],
                                  font=(FUENTE_CODIGO, 11, "italic"))
        self.codigo.tag_configure("Correcta", background=COLOR["ok_fondo"])
        self.codigo.tag_configure("Incorrecta", background=COLOR["error_fondo"])
        self.codigo.tag_configure("marca_ok", foreground=COLOR["ok"])
        self.codigo.tag_configure("marca_error", foreground=COLOR["error"])
        self.codigo.tag_configure("resaltada", background="#fde68a")
        self.codigo.tag_raise("resaltada")

    def _crear_pestana_lexico(self) -> None:
        marco = self._nueva_pestana("Comparativa léxica")
        filtros = ttk.Frame(marco, style="Superficie.TFrame")
        filtros.pack(fill="x", pady=(0, 10))
        ttk.Label(filtros, text="Categoría", style="Superficie.TLabel").pack(side="left")
        self.filtro_categoria = tk.StringVar(value=TODAS)
        self.combo_categoria = ttk.Combobox(filtros, textvariable=self.filtro_categoria,
                                            state="readonly", width=26)
        self.combo_categoria.pack(side="left", padx=(8, 18))
        self.combo_categoria.bind("<<ComboboxSelected>>", lambda _evento: self._llenar_lexico())
        ttk.Label(filtros, text="Buscar", style="Superficie.TLabel").pack(side="left")
        self.filtro_texto = tk.StringVar()
        self.filtro_texto.trace_add("write", lambda *_: self._llenar_lexico())
        ttk.Entry(filtros, textvariable=self.filtro_texto, width=24).pack(side="left", padx=8)
        self.cuenta_lexico = ttk.Label(filtros, style="Tenue.TLabel")
        self.cuenta_lexico.pack(side="right")

        self.fuente_lexico, self.tabla_lexico = crear_par_tablas(
            marco,
            [("linea", "Línea", 60, False), ("codigo", "Código fuente", 300, True)],
            [("numero", "No.", 60, False), ("elemento", "Elemento", 150, True),
                                  ("categoria", "Clasificación", 215, False)])
        for categoria, color in COLOR_CATEGORIA.items():
            self.tabla_lexico.tag_configure(categoria, foreground=color)
        self.tabla_lexico.tag_configure("Elemento no identificado", background=COLOR["error_fondo"])
        for tabla in (self.fuente_lexico, self.tabla_lexico):
            tabla.bind("<Double-1>", lambda _evento, t=tabla: self._ir_a_linea(t))
        self.resumen_lexico = ttk.Label(marco, style="Tenue.TLabel", wraplength=600, justify="left")
        self.resumen_lexico.pack(fill="x", pady=(10, 0))
        # El ajuste de línea se calcula con el ancho de las tablas (que no dependen de la
        # etiqueta); si se calculara con el panel que la contiene, la ventana crecería sin parar.
        self.fuente_lexico.bind("<Configure>", lambda evento: self.resumen_lexico.configure(
            wraplength=max(evento.width * 2 - 20, 200)), add="+")

    def _crear_pestana_sintaxis(self) -> None:
        marco = self._nueva_pestana("Comparativa sintáctica")
        filtros = ttk.Frame(marco, style="Superficie.TFrame")
        filtros.pack(fill="x", pady=(0, 10))
        ttk.Label(filtros, text="Mostrar", style="Superficie.TLabel").pack(side="left", padx=(0, 8))
        self.filtro_veredicto = tk.StringVar(value="todas")
        for texto, valor in (("Todas", "todas"), ("Correctas", "Correcta"), ("Incorrectas", "Incorrecta")):
            ttk.Radiobutton(filtros, text=texto, value=valor, variable=self.filtro_veredicto,
                            style="Superficie.TRadiobutton",
                            command=self._llenar_sintaxis).pack(side="left", padx=(0, 10))

        self.fuente_sintaxis, self.tabla_sintaxis = crear_par_tablas(
            marco,
            [("linea", "Línea", 60, False), ("codigo", "Código fuente", 300, True)],
            [("resultado", "Resultado", 110, False), ("causa", "Causa", 340, True)])
        for tabla in (self.fuente_sintaxis, self.tabla_sintaxis):
            tabla.tag_configure("Incorrecta", background=COLOR["error_fondo"])
            tabla.bind("<Double-1>", lambda _evento, t=tabla: self._ir_a_linea(t))
        self.tabla_sintaxis.tag_configure("Correcta", foreground=COLOR["ok"])
        self.tabla_sintaxis.tag_configure("Incorrecta", foreground=COLOR["error"])
        self.tabla_sintaxis.bind("<<TreeviewSelect>>", self._mostrar_detalle, add="+")

        detalle = tk.Frame(marco, bg=COLOR["fondo"], padx=14, pady=10)
        detalle.pack(fill="x", pady=(10, 0))
        self.detalle_codigo = tk.Label(detalle, bg=COLOR["fondo"], fg=COLOR["texto"], anchor="w",
                                       justify="left", font=(FUENTE_CODIGO, 11),
                                       text="Seleccione una línea para ver el detalle.")
        self.detalle_codigo.pack(fill="x")
        self.detalle_causa = tk.Label(detalle, bg=COLOR["fondo"], fg=COLOR["error"], anchor="w",
                                      justify="left", font=(FUENTE, 10))
        self.detalle_causa.pack(fill="x")
        self.fuente_sintaxis.bind("<Configure>", lambda evento: [
            etiqueta.configure(wraplength=max(evento.width * 2 - 40, 200))
            for etiqueta in (self.detalle_codigo, self.detalle_causa)], add="+")

    def _crear_pestana_simbolos(self) -> None:
        marco = self._nueva_pestana("Tabla de símbolos")
        izquierda = ttk.Frame(marco, style="Superficie.TFrame")
        izquierda.pack(side="left", fill="both", expand=True)
        self.tabla_simbolos = crear_tabla(izquierda, [
            ("simbolo", "Símbolo", 180, True), ("tipo", "Tipo", 200, False),
            ("valor", "Valor inicial", 260, True), ("tamano", "Tamaño", 100, False)])

        derecha = tk.Frame(marco, bg=COLOR["fondo"], width=290, padx=16, pady=14)
        derecha.pack(side="right", fill="y", padx=(14, 0))
        derecha.pack_propagate(False)
        tk.Label(derecha, text="SEGMENTOS DEL PROGRAMA", bg=COLOR["fondo"], fg=COLOR["tenue"],
                 font=(FUENTE, 8, "bold")).pack(anchor="w", pady=(0, 10))
        self.filas_segmento: dict[str, tk.Label] = {}
        for nombre in ("pila", "datos", "código"):
            tk.Label(derecha, text=f"Segmento de {nombre}", bg=COLOR["fondo"], fg=COLOR["texto"],
                     font=(FUENTE, 10, "bold")).pack(anchor="w")
            estado = tk.Label(derecha, bg=COLOR["fondo"], fg=COLOR["tenue"], anchor="w",
                              justify="left", wraplength=250)
            estado.pack(anchor="w", pady=(0, 10))
            self.filas_segmento[nombre] = estado
        self.estado_segmentos = tk.Label(derecha, bg=COLOR["fondo"], font=(FUENTE, 11, "bold"), pady=6)
        self.estado_segmentos.pack(anchor="w", pady=(6, 0))


    def _listar_carpeta(self, carpeta: Path) -> None:
        self.carpeta = carpeta
        self.archivos = sorted(carpeta.glob("*.ens"), key=lambda ruta: ruta.name.lower())
        self.lista.delete(0, "end")
        for ruta in self.archivos:
            self.lista.insert("end", f"  {ruta.name}")
        if not self.archivos:
            self.lista.insert("end", "  (sin archivos .ens)")
        self._marcar_en_lista()

    def _marcar_en_lista(self) -> None:
        self.lista.selection_clear(0, "end")
        if self.resultado and self.resultado.ruta in self.archivos:
            ind = self.archivos.index(self.resultado.ruta)
            self.lista.selection_set(ind)
            self.lista.see(ind)

    def _al_elegir_archivo(self, _evento: tk.Event) -> None:
        seleccion = self.lista.curselection()
        if seleccion and seleccion[0] < len(self.archivos):
            ruta = self.archivos[seleccion[0]]
            if not self.resultado or ruta != self.resultado.ruta:
                self.cargar(ruta)

    def _elegir_carpeta(self) -> None:
        carpeta = filedialog.askdirectory(initialdir=self.carpeta, title="Carpeta con archivos .ens")
        if carpeta:
            self._listar_carpeta(Path(carpeta))

    def abrir_dialogo(self) -> None:
        """Pide un archivo .ens con el explorador de archivos."""
        nombre = filedialog.askopenfilename(
            initialdir=self.carpeta, title="Abrir programa en ensamblador",
            filetypes=[("Programa en ensamblador", "*.ens"), ("Todos los archivos", "*.*")])
        if not nombre:
            return
        ruta = Path(nombre).resolve()
        if ruta.suffix.lower() != ".ens":
            messagebox.showwarning("Archivo no válido", "El archivo debe tener la extensión .ens.")
            return
        self.cargar(ruta)
        self._listar_carpeta(ruta.parent)

    def recargar(self) -> None:
        """Vuelve a analizar el archivo abierto (por si se editó)."""
        if self.resultado:
            self.cargar(self.resultado.ruta)

    def cargar(self, ruta: Path) -> None:
        """Analiza un archivo y muestra sus resultados."""
        try:
            self.resultado = analizar_archivo(ruta.resolve())
        except OSError as error:
            messagebox.showerror("No se pudo leer el archivo", str(error))
            return
        self.raiz.title(f"{ruta.name} — Ensamblador")
        self.nombre_archivo.configure(text=ruta.name)
        self.boton_recargar.configure(state="normal")
        self._mostrar(self.contenido)
        self._llenar_tarjetas()
        self._llenar_fuente()
        self._preparar_filtros_lexico()
        self._llenar_lexico()
        self._llenar_sintaxis()
        self._llenar_simbolos()
        self._marcar_en_lista()

    def _mostrar(self, marco: tk.Frame) -> None:
        for hijo in (self.vacio, self.contenido):
            hijo.pack_forget()
        marco.pack(fill="both", expand=True, pady=(0, 12) if marco is self.vacio else 0)


    def _llenar_tarjetas(self) -> None:
        resultado = self.resultado
        self.valor_lineas.configure(text=resultado.correctas + resultado.incorrectas)
        self.valor_correctas.configure(text=resultado.correctas, fg=COLOR["ok"])
        self.valor_incorrectas.configure(text=resultado.incorrectas,
                                         fg=COLOR["error"] if resultado.incorrectas else COLOR["texto"])
        self.valor_simbolos.configure(text=len(resultado.analizador.tabla.filas()))
        completo = resultado.analizador.completo()
        self.valor_segmentos.configure(text="Completos" if completo else "Incompletos",
                                       fg=COLOR["ok"] if completo else COLOR["error"])

    def _llenar_fuente(self) -> None:
        texto = self.codigo
        texto.configure(state="normal")
        texto.delete("1.0", "end")
        for numero, cruda, veredicto, _causa in self.resultado.analizador.filas:
            linea = cruda.expandtabs(4)
            codigo = quitar_comentarios(linea)
            marca = {"Correcta": ("✔ ", "marca_ok"), "Incorrecta": ("✘ ", "marca_error")}.get(
                veredicto, ("  ", "numero"))
            inicio = texto.index("end-1c")
            texto.insert("end", f"{numero:>4}  ", "numero")
            texto.insert("end", *marca)
            texto.insert("end", codigo)
            texto.insert("end", linea[len(codigo):], "comentario")
            texto.insert("end", "\n")
            if veredicto:
                texto.tag_add(veredicto, inicio, texto.index("end-1c"))
        texto.configure(state="disabled")

    def _preparar_filtros_lexico(self) -> None:
        cuenta = Counter(elemento.categoria for elemento in self.resultado.elementos)
        self.combo_categoria.configure(values=[TODAS, *sorted(cuenta)])
        if self.filtro_categoria.get() not in cuenta:
            self.filtro_categoria.set(TODAS)
        self.resumen_lexico.configure(text="   ·   ".join(
            f"{categoria}: {cantidad}" for categoria, cantidad in sorted(cuenta.items())))

    def _llenar_lexico(self) -> None:
        """Una fila por elemento; el código de la línea aparece frente a su primer elemento."""
        if not self.resultado:
            return
        fuente, tabla = self.fuente_lexico, self.tabla_lexico
        fuente.delete(*fuente.get_children())
        tabla.delete(*tabla.get_children())
        categoria = self.filtro_categoria.get()
        buscado = self.filtro_texto.get().strip().lower()
        lineas = self.resultado.lineas
        mostrados, linea_anterior, grupo = 0, 0, 0
        for numero, elemento in enumerate(self.resultado.elementos, 1):
            if categoria != TODAS and elemento.categoria != categoria:
                continue
            if buscado and buscado not in elemento.texto.lower():
                continue
            nueva_linea = elemento.linea != linea_anterior
            if nueva_linea:
                grupo += 1
                linea_anterior = elemento.linea
            rayada = ("zebra",) if grupo % 2 == 0 else ()           # una franja por línea
            codigo = quitar_comentarios(lineas[elemento.linea - 1]).expandtabs(4).strip()
            iid = f"{elemento.linea}-{numero}"
            fuente.insert("", "end", iid=iid, tags=rayada, values=(
                elemento.linea if nueva_linea else "", codigo if nueva_linea else ""))
            etiquetas = (elemento.categoria,) if elemento.categoria == INVALIDO else (elemento.categoria, *rayada)
            tabla.insert("", "end", iid=iid, tags=etiquetas,
                         values=(f"{numero:03d}", elemento.texto, elemento.categoria))
            mostrados += 1
        self.cuenta_lexico.configure(
            text=f"{mostrados} de {len(self.resultado.elementos)} elementos")

    def _llenar_sintaxis(self) -> None:
        """Una fila por línea con código: el código a la izquierda y el dictamen a la derecha."""
        if not self.resultado:
            return
        fuente, tabla = self.fuente_sintaxis, self.tabla_sintaxis
        fuente.delete(*fuente.get_children())
        tabla.delete(*tabla.get_children())
        filtro = self.filtro_veredicto.get()
        for numero, cruda, veredicto, causa in self.resultado.analizador.filas:
            if not veredicto or filtro not in ("todas", veredicto):
                continue
            codigo = quitar_comentarios(cruda).expandtabs(4).strip()
            fuente.insert("", "end", iid=str(numero), values=(numero, codigo), tags=(veredicto,))
            tabla.insert("", "end", iid=str(numero), values=(veredicto, causa), tags=(veredicto,))
        self.detalle_codigo.configure(text="Seleccione una línea para ver el detalle.")
        self.detalle_causa.configure(text="")

    def _llenar_simbolos(self) -> None:
        tabla = self.tabla_simbolos
        tabla.delete(*tabla.get_children())
        for ind, simbolo in enumerate(self.resultado.analizador.tabla.filas()):
            tabla.insert("", "end", tags=("zebra",) if ind % 2 else (), values=(
                simbolo["nombre"], simbolo["tipo"], simbolo["valor"], _tamano(simbolo["tamano"])))
        for nombre, estado in self.resultado.analizador.estructura():
            definido = estado != "NO DEFINIDO" and "SIN" not in estado and "más de una" not in estado
            self.filas_segmento[nombre].configure(
                text=estado.capitalize() if estado == "NO DEFINIDO" else estado,
                fg=COLOR["tenue"] if definido else COLOR["error"])
        completo = self.resultado.analizador.completo()
        self.estado_segmentos.configure(
            text="✔ Identificación COMPLETA" if completo else "✘ Identificación INCOMPLETA",
            fg=COLOR["ok"] if completo else COLOR["error"])


    def _mostrar_detalle(self, _evento: tk.Event) -> None:
        seleccion = self.tabla_sintaxis.selection()
        if not seleccion:
            return
        numero, codigo = self.fuente_sintaxis.item(seleccion[0], "values")
        veredicto, causa = self.tabla_sintaxis.item(seleccion[0], "values")
        self.detalle_codigo.configure(text=f"Línea {numero}:   {codigo}")
        self.detalle_causa.configure(
            text=f"Causa: {causa}" if veredicto == "Incorrecta" else "✔ Línea correcta",
            fg=COLOR["error"] if veredicto == "Incorrecta" else COLOR["ok"])

    def _ir_a_linea(self, tabla: ttk.Treeview) -> None:
        """Abre la pestaña del código fuente y resalta la línea de la fila elegida."""
        seleccion = tabla.selection()
        if not seleccion:
            return
        numero = int(seleccion[0].split("-")[0])          # el identificador empieza con la línea
        self.pestanas.select(self.pestana_fuente)
        self.codigo.tag_remove("resaltada", "1.0", "end")
        self.codigo.tag_add("resaltada", f"{numero}.0", f"{numero}.end")
        self.codigo.see(f"{numero}.0")


def iniciar() -> None:
    """Crea y ejecuta la ventana."""
    if sys.platform == "win32":
        try:                                   # texto nítido en pantallas con escala
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (ImportError, AttributeError, OSError):
            pass
    raiz = tk.Tk()
    Ventana(raiz)
    raiz.mainloop()
