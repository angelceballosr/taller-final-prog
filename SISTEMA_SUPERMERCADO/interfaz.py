"""
interfaz.py
Pantallas de Tkinter: Menú principal, Inventario, Ventas, Caja y Reportes.

La interfaz NO guarda datos por su cuenta: cuando el usuario actúa, llama a la
función del módulo correspondiente (inventario, ventas, caja) y ese resultado se
guarda a través de persistencia.py.
"""

import copy
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

import persistencia
import inventario as inv
import ventas as vt
import caja as cj
from funciones import (
    formatear_moneda,
    validar_numero,
    validar_fecha,
    fecha_actual,
)

# ---- Colores ----
COLOR_FONDO = "#f3f4f6"
COLOR_LATERAL = "#1f2937"
COLOR_ACENTO = "#16a34a"
COLOR_ALERTA = "#b91c1c"
COLOR_TEXTO = "#111827"
FUENTE = "Segoe UI"


# ======================================================================
#  Utilidades de interfaz
# ======================================================================
def crear_tabla(padre, columnas, alto=12):
    """Crea una tabla (Treeview) con barra de desplazamiento.

    columnas: lista de (id, título, ancho, alineación).
    Devuelve (marco, tabla): se empaqueta el marco y se usa la tabla.
    """
    marco = ttk.Frame(padre)
    tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas],
                         show="headings", height=alto, selectmode="browse")
    for ident, titulo, ancho, ancla in columnas:
        tabla.heading(ident, text=titulo)
        tabla.column(ident, width=ancho, anchor=ancla)
    barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return marco, tabla


def limpiar_tabla(tabla):
    for fila in tabla.get_children():
        tabla.delete(fila)


def avisar(mensaje, parent=None):
    messagebox.showwarning("Revise los datos", str(mensaje), parent=parent)


# ======================================================================
#  Ventana principal
# ======================================================================
class AplicacionSupermercado(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Supermercado")
        self.geometry("1150x700")
        self.minsize(980, 620)

        # Al abrir el programa, cargar_datos() reconstruye todo desde los JSON.
        self.productos = persistencia.cargar_datos("productos.json", {})
        self.ventas = persistencia.cargar_datos(
            "ventas.json", {"siguiente_factura": 1, "facturas": []})
        self.caja = persistencia.cargar_datos("caja.json", {
            "abierta": False, "monto_inicial": 0, "fecha_apertura": None,
            "movimientos": [], "historial": []})
        self._completar_datos()

        self._configurar_estilos()
        self._construir_layout()
        self.mostrar("inicio")

        self.protocol("WM_DELETE_WINDOW", self.salir)
        self.after(300, self._mostrar_advertencias)

    # ---------- datos ----------
    def _completar_datos(self):
        """Agrega los campos que falten por si un JSON viejo está incompleto."""
        self.ventas.setdefault("facturas", [])
        self.ventas.setdefault("siguiente_factura", len(self.ventas["facturas"]) + 1)
        for factura in self.ventas["facturas"]:
            factura.setdefault("devoluciones", [])
        por_defecto_caja = {"abierta": False, "monto_inicial": 0, "fecha_apertura": None,
                            "movimientos": [], "historial": []}
        for clave, valor in por_defecto_caja.items():
            self.caja.setdefault(clave, valor)
        por_defecto_producto = {"nombre": "Sin nombre", "categoria": "Sin categoría",
                                "precio_compra": 0, "precio_venta": 0, "stock": 0,
                                "stock_minimo": 0, "activo": True}
        for datos in self.productos.values():
            for clave, valor in por_defecto_producto.items():
                datos.setdefault(clave, valor)

    def guardar_todo(self):
        """Guarda los tres archivos JSON. Devuelve True si todo se guardó."""
        correcto = persistencia.guardar_datos("productos.json", self.productos)
        correcto = persistencia.guardar_datos("ventas.json", self.ventas) and correcto
        correcto = persistencia.guardar_datos("caja.json", self.caja) and correcto
        if not correcto:
            persistencia.ADVERTENCIAS.clear()
            messagebox.showerror(
                "Error al guardar",
                "No se guardó; datos anteriores intactos.\n"
                "Revise que la carpeta del programa no sea de solo lectura.")
        return correcto

    def ejecutar(self, operacion, parent=None):
        """Ejecuta una operación que modifica los datos.

        Si falla, todo vuelve a como estaba (así nunca queda una venta a medias).
        Si sale bien, se guarda en los JSON y se actualizan las pantallas.
        Devuelve (True, resultado) o (False, None).
        """
        copia = copy.deepcopy((self.productos, self.ventas, self.caja))
        try:
            resultado = operacion()
        except ValueError as error:
            self.productos, self.ventas, self.caja = copia
            avisar(error, parent)
            return False, None
        except Exception as error:  # error inesperado: no dejar datos a medias
            self.productos, self.ventas, self.caja = copia
            messagebox.showerror("Error inesperado", str(error), parent=parent)
            return False, None
        self.guardar_todo()
        self.actualizar_pantallas()
        return True, resultado

    # ---------- apariencia ----------
    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        self.configure(bg=COLOR_FONDO)
        estilo.configure(".", font=(FUENTE, 10))
        estilo.configure("TFrame", background=COLOR_FONDO)
        estilo.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO)
        estilo.configure("TCheckbutton", background=COLOR_FONDO)
        estilo.configure("Titulo.TLabel", font=(FUENTE, 20, "bold"))
        estilo.configure("Subtitulo.TLabel", font=(FUENTE, 11, "bold"))
        estilo.configure("Total.TLabel", font=(FUENTE, 22, "bold"), foreground=COLOR_ACENTO)
        estilo.configure("Alerta.TLabel", font=(FUENTE, 10, "bold"), foreground=COLOR_ALERTA)
        estilo.configure("Tarjeta.TFrame", background="white", relief="solid", borderwidth=1)
        estilo.configure("Tarjeta.TLabel", background="white", foreground="#6b7280")
        estilo.configure("TarjetaValor.TLabel", background="white",
                         font=(FUENTE, 20, "bold"), foreground=COLOR_TEXTO)
        estilo.configure("Lateral.TFrame", background=COLOR_LATERAL)
        estilo.configure("Lateral.TLabel", background=COLOR_LATERAL,
                         foreground="white", font=(FUENTE, 13, "bold"))
        estilo.configure("Nav.TButton", background=COLOR_LATERAL, foreground="white",
                         borderwidth=0, padding=(16, 11), anchor="w")
        estilo.map("Nav.TButton", background=[("active", "#374151")])
        estilo.configure("NavActivo.TButton", background=COLOR_ACENTO, foreground="white",
                         borderwidth=0, padding=(16, 11), anchor="w")
        estilo.map("NavActivo.TButton", background=[("active", COLOR_ACENTO)])
        estilo.configure("Acento.TButton", background=COLOR_ACENTO, foreground="white",
                         padding=(14, 8), font=(FUENTE, 10, "bold"))
        estilo.map("Acento.TButton", background=[("active", "#15803d"), ("disabled", "#9ca3af")])
        estilo.configure("Treeview", rowheight=26, background="white", fieldbackground="white")
        estilo.configure("Treeview.Heading", font=(FUENTE, 10, "bold"))

    def _construir_layout(self):
        lateral = ttk.Frame(self, style="Lateral.TFrame", width=200)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        ttk.Label(lateral, text="🛒 Supermercado", style="Lateral.TLabel").pack(
            anchor="w", padx=16, pady=(20, 18))

        contenido = ttk.Frame(self)
        contenido.pack(side="left", fill="both", expand=True)
        contenido.rowconfigure(0, weight=1)
        contenido.columnconfigure(0, weight=1)

        self.pantallas = {
            "inicio": PantallaInicio(contenido, self),
            "inventario": PantallaInventario(contenido, self),
            "ventas": PantallaVentas(contenido, self),
            "caja": PantallaCaja(contenido, self),
            "reportes": PantallaReportes(contenido, self),
        }
        for pantalla in self.pantallas.values():
            pantalla.grid(row=0, column=0, sticky="nsew")

        self.botones_nav = {}
        etiquetas = [("inicio", "Menú principal"), ("inventario", "Inventario"),
                     ("ventas", "Ventas"), ("caja", "Caja"), ("reportes", "Reportes")]
        for nombre, texto in etiquetas:
            boton = ttk.Button(lateral, text=texto, style="Nav.TButton",
                               command=lambda n=nombre: self.mostrar(n))
            boton.pack(fill="x")
            self.botones_nav[nombre] = boton
        ttk.Button(lateral, text="Salir", style="Nav.TButton", command=self.salir).pack(
            side="bottom", fill="x", pady=(0, 12))

    # ---------- navegación ----------
    def mostrar(self, nombre):
        for clave, boton in self.botones_nav.items():
            boton.configure(style="NavActivo.TButton" if clave == nombre else "Nav.TButton")
        self.pantallas[nombre].actualizar()
        self.pantallas[nombre].tkraise()

    def actualizar_pantallas(self):
        for pantalla in self.pantallas.values():
            pantalla.actualizar()

    def _mostrar_advertencias(self):
        if persistencia.ADVERTENCIAS:
            messagebox.showwarning("Aviso al iniciar", "\n".join(persistencia.ADVERTENCIAS))
            persistencia.ADVERTENCIAS.clear()

    def salir(self):
        if messagebox.askokcancel("Salir", "¿Desea cerrar el sistema?\n"
                                           "Los datos ya están guardados."):
            self.destroy()


# ======================================================================
#  Menú principal
# ======================================================================
class PantallaInicio(ttk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre, padding=24)
        self.app = app
        ttk.Label(self, text="Menú principal", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self, text="Sistema de gestión de supermercado").pack(anchor="w", pady=(0, 18))

        tarjetas = ttk.Frame(self)
        tarjetas.pack(fill="x")
        self.valores = {}
        for columna, (clave, titulo) in enumerate([
                ("productos", "Productos activos"), ("bajo", "Stock bajo"),
                ("caja", "Caja"), ("hoy", "Ventas de hoy")]):
            tarjetas.columnconfigure(columna, weight=1, uniform="t")
            tarjeta = ttk.Frame(tarjetas, style="Tarjeta.TFrame", padding=16)
            tarjeta.grid(row=0, column=columna, sticky="ew", padx=(0 if columna == 0 else 10, 0))
            ttk.Label(tarjeta, text=titulo, style="Tarjeta.TLabel").pack(anchor="w")
            etiqueta = ttk.Label(tarjeta, text="-", style="TarjetaValor.TLabel")
            etiqueta.pack(anchor="w", pady=(6, 0))
            self.valores[clave] = etiqueta

        ttk.Label(self, text="¿Qué desea hacer?", style="Subtitulo.TLabel").pack(
            anchor="w", pady=(28, 8))
        botones = ttk.Frame(self)
        botones.pack(anchor="w")
        for texto, destino in [("Inventario", "inventario"), ("Ventas", "ventas"),
                               ("Caja", "caja"), ("Reportes", "reportes")]:
            ttk.Button(botones, text=texto, style="Acento.TButton", width=16,
                       command=lambda d=destino: app.mostrar(d)).pack(side="left", padx=(0, 10))

    def actualizar(self):
        productos = self.app.productos
        activos = [d for d in productos.values() if d["activo"]]
        bajos = [d for d in activos if inv.es_stock_bajo(d)]
        reporte = cj.generar_reporte(self.app.caja, self.app.ventas)
        self.valores["productos"].configure(text=str(len(activos)))
        self.valores["bajo"].configure(
            text=str(len(bajos)), foreground=COLOR_ALERTA if bajos else COLOR_TEXTO)
        self.valores["caja"].configure(
            text="Abierta" if self.app.caja["abierta"] else "Cerrada",
            foreground=COLOR_ACENTO if self.app.caja["abierta"] else COLOR_ALERTA)
        self.valores["hoy"].configure(text=formatear_moneda(reporte["neto"]))


# ======================================================================
#  Inventario
# ======================================================================
class PantallaInventario(ttk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre, padding=20)
        self.app = app
        ttk.Label(self, text="Inventario", style="Titulo.TLabel").pack(anchor="w")
        self.lbl_alerta = ttk.Label(self, text="", style="Alerta.TLabel")
        self.lbl_alerta.pack(anchor="w", pady=(2, 8))

        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 8))
        self.var_busqueda = tk.StringVar()
        entrada = ttk.Entry(barra, textvariable=self.var_busqueda, width=32)
        entrada.pack(side="left")
        entrada.bind("<Return>", lambda e: self.actualizar())
        ttk.Button(barra, text="Buscar", command=self.actualizar).pack(side="left", padx=6)
        ttk.Button(barra, text="Mostrar todo", command=self.mostrar_todo).pack(side="left")
        self.var_inactivos = tk.BooleanVar(value=False)
        ttk.Checkbutton(barra, text="Mostrar desactivados", variable=self.var_inactivos,
                        command=self.actualizar).pack(side="left", padx=14)

        marco, self.tabla = crear_tabla(self, [
            ("codigo", "Código", 80, "center"), ("nombre", "Nombre", 230, "w"),
            ("categoria", "Categoría", 120, "w"), ("compra", "P. compra", 90, "e"),
            ("venta", "P. venta", 90, "e"), ("stock", "Stock", 70, "center"),
            ("minimo", "Mínimo", 70, "center"), ("estado", "Estado", 100, "center")], alto=16)
        marco.pack(fill="both", expand=True)
        self.tabla.tag_configure("bajo", foreground=COLOR_ALERTA)
        self.tabla.tag_configure("inactivo", foreground="#9ca3af")

        botones = ttk.Frame(self)
        botones.pack(fill="x", pady=(10, 0))
        ttk.Button(botones, text="Agregar producto", style="Acento.TButton",
                   command=self.agregar).pack(side="left")
        for texto, comando in [("Editar", self.editar), ("Registrar entrada (+)", self.entrada),
                               ("Registrar salida (−)", self.salida),
                               ("Desactivar", self.desactivar)]:
            ttk.Button(botones, text=texto, command=comando).pack(side="left", padx=(8, 0))

    def actualizar(self):
        productos = self.app.productos
        texto = self.var_busqueda.get().strip()
        incluir = self.var_inactivos.get()
        if texto:
            filas = sorted(inv.buscar_producto(productos, texto, incluir), key=lambda f: f[0])
        else:
            filas = inv.consultar_inventario(productos, incluir)

        limpiar_tabla(self.tabla)
        for codigo, d in filas:
            if not d["activo"]:
                estado, etiqueta = "Desactivado", "inactivo"
            elif inv.es_stock_bajo(d):
                estado, etiqueta = "Stock bajo", "bajo"
            else:
                estado, etiqueta = "OK", ""
            self.tabla.insert("", "end", iid=codigo, tags=(etiqueta,) if etiqueta else (), values=(
                codigo, d["nombre"], d["categoria"], formatear_moneda(d["precio_compra"]),
                formatear_moneda(d["precio_venta"]), d["stock"], d["stock_minimo"], estado))

        bajos = [c for c, d in productos.items() if d["activo"] and inv.es_stock_bajo(d)]
        if bajos:
            self.lbl_alerta.configure(text=f"⚠ {len(bajos)} producto(s) con stock bajo: " + ", ".join(sorted(bajos)))
        else:
            self.lbl_alerta.configure(text="")

    def mostrar_todo(self):
        self.var_busqueda.set("")
        self.actualizar()

    def _seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Seleccione un producto", "Haga clic en un producto de la tabla primero.")
            return None
        return seleccion[0]

    def agregar(self):
        DialogoProducto(self.app)

    def editar(self):
        codigo = self._seleccionado()
        if codigo:
            DialogoProducto(self.app, codigo)

    def _pedir_cantidad(self, titulo, codigo):
        nombre = self.app.productos[codigo]["nombre"]
        return simpledialog.askstring(titulo, f"{nombre} ({codigo})\nCantidad:", parent=self)

    def entrada(self):
        codigo = self._seleccionado()
        if codigo:
            cantidad = self._pedir_cantidad("Registrar entrada", codigo)
            if cantidad is not None:
                self.app.ejecutar(lambda: inv.registrar_entrada(self.app.productos, codigo, cantidad))

    def salida(self):
        codigo = self._seleccionado()
        if codigo:
            cantidad = self._pedir_cantidad("Registrar salida", codigo)
            if cantidad is not None:
                self.app.ejecutar(lambda: inv.registrar_salida(self.app.productos, codigo, cantidad))

    def desactivar(self):
        codigo = self._seleccionado()
        if codigo and messagebox.askyesno(
                "Desactivar producto",
                f"¿Desactivar {self.app.productos[codigo]['nombre']}?\n"
                "No se borra: solo deja de aparecer en las ventas."):
            self.app.ejecutar(lambda: inv.desactivar_producto(self.app.productos, codigo))


class DialogoProducto(tk.Toplevel):
    """Ventana para agregar un producto nuevo o editar uno existente."""

    def __init__(self, app, codigo=None):
        super().__init__(app)
        self.app = app
        self.codigo = codigo
        self.title("Editar producto" if codigo else "Agregar producto")
        self.configure(bg=COLOR_FONDO)
        self.resizable(False, False)
        self.transient(app)

        marco = ttk.Frame(self, padding=16)
        marco.pack(fill="both", expand=True)
        campos = [("Código", "codigo"), ("Nombre", "nombre"), ("Categoría", "categoria"),
                  ("Precio de compra", "precio_compra"), ("Precio de venta", "precio_venta"),
                  ("Stock inicial" if not codigo else "Stock actual", "stock"),
                  ("Stock mínimo", "stock_minimo")]
        self.vars = {}
        primera = None
        for fila, (etiqueta, clave) in enumerate(campos):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="e", padx=(0, 8), pady=4)
            var = tk.StringVar()
            entrada = ttk.Entry(marco, textvariable=var, width=30)
            entrada.grid(row=fila, column=1, pady=4)
            self.vars[clave] = var
            if codigo and clave in ("codigo", "stock"):
                entrada.configure(state="disabled")  # no se editan aquí
            elif primera is None:
                primera = entrada

        self.var_activo = tk.BooleanVar(value=True)
        if codigo:
            d = app.productos[codigo]
            valores = {"codigo": codigo, "nombre": d["nombre"], "categoria": d["categoria"],
                       "precio_compra": d["precio_compra"], "precio_venta": d["precio_venta"],
                       "stock": d["stock"], "stock_minimo": d["stock_minimo"]}
            for clave, valor in valores.items():
                self.vars[clave].set(str(valor))
            self.var_activo.set(d["activo"])
            ttk.Checkbutton(marco, text="Producto activo", variable=self.var_activo).grid(
                row=len(campos), column=1, sticky="w", pady=4)
        else:
            self.vars["stock"].set("0")
            self.vars["stock_minimo"].set("5")

        botones = ttk.Frame(marco)
        botones.grid(row=len(campos) + 1, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(botones, text="Cancelar", command=self.destroy).pack(side="right")
        ttk.Button(botones, text="Guardar", style="Acento.TButton",
                   command=self.guardar).pack(side="right", padx=8)
        self.bind("<Return>", lambda e: self.guardar())
        self.bind("<Escape>", lambda e: self.destroy())
        if primera is not None:
            primera.focus_set()
        self.grab_set()

    def guardar(self):
        v = {clave: var.get() for clave, var in self.vars.items()}
        productos = self.app.productos

        def operacion():
            if self.codigo is None:
                inv.registrar_producto(productos, v["codigo"], v["nombre"], v["categoria"],
                                       v["precio_compra"], v["precio_venta"], v["stock"],
                                       v["stock_minimo"])
            else:
                inv.editar_producto(
                    self.app.productos, self.codigo, nombre=v["nombre"], categoria=v["categoria"],
                    precio_compra=v["precio_compra"], precio_venta=v["precio_venta"],
                    stock_minimo=v["stock_minimo"], activo=self.var_activo.get())

        correcto, _ = self.app.ejecutar(operacion, parent=self)
        if correcto:
            self.destroy()


# ======================================================================
#  Ventas
# ======================================================================
class PantallaVentas(ttk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre, padding=20)
        self.app = app
        self.carrito = []

        ttk.Label(self, text="Ventas", style="Titulo.TLabel").pack(anchor="w")
        self.lbl_caja = ttk.Label(self, text="")
        self.lbl_caja.pack(anchor="w", pady=(2, 8))

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(0, weight=1)

        # ---------- Izquierda: carrito ----------
        izq = ttk.Frame(cuerpo)
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        captura = ttk.Frame(izq)
        captura.pack(fill="x")
        ttk.Label(captura, text="Código:").pack(side="left")
        self.var_codigo = tk.StringVar()
        self.entrada_codigo = ttk.Entry(captura, textvariable=self.var_codigo, width=12)
        self.entrada_codigo.pack(side="left", padx=(4, 12))
        self.entrada_codigo.bind("<Return>", lambda e: self.agregar())
        ttk.Label(captura, text="Cantidad:").pack(side="left")
        self.var_cantidad = tk.StringVar(value="1")
        entrada_cantidad = ttk.Entry(captura, textvariable=self.var_cantidad, width=6)
        entrada_cantidad.pack(side="left", padx=(4, 12))
        entrada_cantidad.bind("<Return>", lambda e: self.agregar())
        ttk.Button(captura, text="Agregar al carrito", style="Acento.TButton",
                   command=self.agregar).pack(side="left")

        marco, self.tabla_carrito = crear_tabla(izq, [
            ("codigo", "Código", 70, "center"), ("nombre", "Producto", 190, "w"),
            ("cantidad", "Cant.", 55, "center"), ("precio", "Precio", 85, "e"),
            ("subtotal", "Subtotal", 95, "e")], alto=9)
        marco.pack(fill="both", expand=True, pady=10)

        acciones = ttk.Frame(izq)
        acciones.pack(fill="x")
        ttk.Button(acciones, text="Retirar seleccionado", command=self.retirar).pack(side="left")
        ttk.Button(acciones, text="Vaciar carrito", command=self.vaciar).pack(side="left", padx=8)
        ttk.Button(acciones, text="Devolución…", command=self.devolucion).pack(side="right")

        totales = ttk.Frame(izq)
        totales.pack(fill="x", pady=(12, 0))
        totales.columnconfigure(1, weight=1)
        self.lbl_subtotal = self._fila_total(totales, 0, "Subtotal")
        self.lbl_descuento = self._fila_total(totales, 1, "Descuento")
        self.lbl_impuesto = self._fila_total(totales, 2, "Impuesto (IVA)")
        ttk.Label(totales, text="TOTAL", style="Subtitulo.TLabel").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self.lbl_total = ttk.Label(totales, text="$0", style="Total.TLabel")
        self.lbl_total.grid(row=3, column=1, sticky="e", pady=(6, 0))

        pago = ttk.Frame(izq)
        pago.pack(fill="x", pady=(10, 0))
        ttk.Label(pago, text="Paga con: $").pack(side="left")
        self.var_pago = tk.StringVar()
        self.var_pago.trace_add("write", lambda *a: self._mostrar_cambio())
        entrada_pago = ttk.Entry(pago, textvariable=self.var_pago, width=14)
        entrada_pago.pack(side="left", padx=(0, 10))
        entrada_pago.bind("<Return>", lambda e: self.cobrar())
        ttk.Button(pago, text="Cobrar", style="Acento.TButton", command=self.cobrar).pack(side="left")
        self.lbl_cambio = ttk.Label(pago, text="", style="Subtitulo.TLabel")
        self.lbl_cambio.pack(side="left", padx=12)

        # ---------- Derecha: catálogo ----------
        der = ttk.Frame(cuerpo)
        der.grid(row=0, column=1, sticky="nsew")
        ttk.Label(der, text="Catálogo de productos", style="Subtitulo.TLabel").pack(anchor="w")
        self.var_buscar = tk.StringVar()
        buscar = ttk.Entry(der, textvariable=self.var_buscar)
        buscar.pack(fill="x", pady=6)
        buscar.bind("<KeyRelease>", lambda e: self.actualizar_catalogo())
        marco, self.tabla_catalogo = crear_tabla(der, [
            ("codigo", "Código", 60, "center"), ("nombre", "Producto", 150, "w"),
            ("precio", "Precio", 75, "e"), ("stock", "Stock", 50, "center")], alto=18)
        marco.pack(fill="both", expand=True)
        self.tabla_catalogo.bind("<<TreeviewSelect>>", self._elegir_catalogo)
        self.tabla_catalogo.bind("<Double-1>", lambda e: self.agregar())
        ttk.Label(der, text="Clic: elegir · Doble clic: agregar").pack(anchor="w", pady=(4, 0))

    def _fila_total(self, marco, fila, texto):
        ttk.Label(marco, text=texto).grid(row=fila, column=0, sticky="w")
        etiqueta = ttk.Label(marco, text="$0")
        etiqueta.grid(row=fila, column=1, sticky="e")
        return etiqueta

    # ---------- actualización ----------
    def actualizar(self):
        if self.app.caja["abierta"]:
            self.lbl_caja.configure(text="Caja abierta: listo para vender", foreground=COLOR_ACENTO)
        else:
            self.lbl_caja.configure(text="Caja cerrada: abra la caja para poder vender",
                                    foreground=COLOR_ALERTA)
        self._quitar_lineas_invalidas()
        self.actualizar_catalogo()
        self.actualizar_carrito()

    def _quitar_lineas_invalidas(self):
        """Si cambió el inventario, ajusta el carrito a lo que realmente hay."""
        for linea in list(self.carrito):
            d = self.app.productos.get(linea["codigo"])
            if d is None or not d["activo"] or d["stock"] <= 0:
                self.carrito.remove(linea)
            elif linea["cantidad"] > d["stock"]:
                linea["cantidad"] = d["stock"]

    def actualizar_catalogo(self):
        texto = self.var_buscar.get().strip()
        filas = sorted(inv.buscar_producto(self.app.productos, texto), key=lambda f: f[0])
        limpiar_tabla(self.tabla_catalogo)
        for codigo, d in filas:
            self.tabla_catalogo.insert("", "end", iid=codigo, values=(
                codigo, d["nombre"], formatear_moneda(d["precio_venta"]), d["stock"]))

    def actualizar_carrito(self):
        limpiar_tabla(self.tabla_carrito)
        for linea in self.carrito:
            self.tabla_carrito.insert("", "end", iid=linea["codigo"], values=(
                linea["codigo"], linea["nombre"], linea["cantidad"],
                formatear_moneda(linea["precio"]),
                formatear_moneda(linea["cantidad"] * linea["precio"])))
        totales = vt.calcular_totales(self.carrito)
        self.lbl_subtotal.configure(text=formatear_moneda(totales["subtotal"]))
        self.lbl_descuento.configure(text="-" + formatear_moneda(totales["descuento"]))
        self.lbl_impuesto.configure(text=formatear_moneda(totales["impuesto"]))
        self.lbl_total.configure(text=formatear_moneda(totales["total"]))
        self._mostrar_cambio()

    def _mostrar_cambio(self):
        try:
            pago = validar_numero(self.var_pago.get())
        except ValueError:
            self.lbl_cambio.configure(text="", foreground=COLOR_TEXTO)
            return
        total = vt.calcular_totales(self.carrito)["total"]
        if self.carrito and pago >= total:
            self.lbl_cambio.configure(text="Cambio: " + formatear_moneda(pago - total),
                                      foreground=COLOR_ACENTO)
        elif self.carrito:
            self.lbl_cambio.configure(text="Faltan " + formatear_moneda(total - pago),
                                      foreground=COLOR_ALERTA)
        else:
            self.lbl_cambio.configure(text="")

    # ---------- acciones ----------
    def _elegir_catalogo(self, evento=None):
        seleccion = self.tabla_catalogo.selection()
        if seleccion:
            self.var_codigo.set(seleccion[0])

    def agregar(self):
        try:
            vt.agregar_carrito(self.carrito, self.app.productos,
                               self.var_codigo.get(), self.var_cantidad.get())
        except ValueError as error:
            avisar(error)
            return
        self.var_codigo.set("")
        self.var_cantidad.set("1")
        self.actualizar_carrito()
        self.entrada_codigo.focus_set()

    def retirar(self):
        seleccion = self.tabla_carrito.selection()
        if not seleccion:
            messagebox.showinfo("Retirar", "Seleccione una línea del carrito.")
            return
        codigo = seleccion[0]
        actual = next(l["cantidad"] for l in self.carrito if l["codigo"] == codigo)
        cantidad = simpledialog.askstring(
            "Retirar del carrito", f"¿Cuántas unidades de {codigo} retirar?",
            initialvalue=str(actual), parent=self)
        if cantidad is None:
            return
        try:
            vt.retirar_carrito(self.carrito, codigo, cantidad)
        except ValueError as error:
            avisar(error)
            return
        self.actualizar_carrito()

    def vaciar(self):
        if self.carrito and messagebox.askyesno("Vaciar carrito", "¿Quitar todos los productos del carrito?"):
            self.carrito.clear()
            self.actualizar_carrito()

    def cobrar(self):
        if not self.app.caja["abierta"]:
            avisar("La caja está cerrada. Ábrala en la pantalla Caja antes de vender.")
            return
        pago = self.var_pago.get()

        def operacion():
            factura = vt.generar_factura(self.carrito, self.app.productos, self.app.ventas, pago)
            cj.registrar_movimiento(self.app.caja, "venta",
                                    f"Factura {factura['numero']:05d}", factura["total"])
            return factura

        correcto, factura = self.app.ejecutar(operacion)
        if correcto:
            self.carrito.clear()
            self.var_pago.set("")
            self.actualizar_carrito()
            VentanaFactura(self.app, factura)

    def devolucion(self):
        DialogoDevolucion(self.app)


class VentanaFactura(tk.Toplevel):
    """Muestra la factura generada y permite guardarla como archivo de texto."""

    def __init__(self, app, factura):
        super().__init__(app)
        self.title(f"Factura {factura['numero']:05d}")
        self.configure(bg=COLOR_FONDO)
        self.transient(app)
        self.texto = vt.formatear_factura(factura)
        self.numero = factura["numero"]

        marco = ttk.Frame(self, padding=14)
        marco.pack(fill="both", expand=True)
        caja_texto = tk.Text(marco, width=46, height=26, font=("Courier", 10), relief="solid", borderwidth=1)
        caja_texto.insert("1.0", self.texto)
        caja_texto.configure(state="disabled")
        caja_texto.pack()
        botones = ttk.Frame(marco)
        botones.pack(fill="x", pady=(10, 0))
        ttk.Button(botones, text="Cerrar", style="Acento.TButton", command=self.destroy).pack(side="right")
        ttk.Button(botones, text="Guardar como .txt", command=self.guardar).pack(side="right", padx=8)
        self.bind("<Escape>", lambda e: self.destroy())

    def guardar(self):
        ruta = filedialog.asksaveasfilename(
            parent=self, defaultextension=".txt", initialfile=f"factura_{self.numero:05d}.txt",
            filetypes=[("Texto", "*.txt")])
        if not ruta:
            return
        try:
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(self.texto)
        except OSError as error:
            messagebox.showerror("No se pudo guardar", str(error), parent=self)


class DialogoDevolucion(tk.Toplevel):
    """Devolución total o parcial de una factura."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.numero = None
        self.entradas = {}
        self.title("Devolución")
        self.configure(bg=COLOR_FONDO)
        self.transient(app)

        marco = ttk.Frame(self, padding=16)
        marco.pack(fill="both", expand=True)
        arriba = ttk.Frame(marco)
        arriba.pack(fill="x")
        ttk.Label(arriba, text="N.º de factura:").pack(side="left")
        self.var_numero = tk.StringVar()
        entrada = ttk.Entry(arriba, textvariable=self.var_numero, width=10)
        entrada.pack(side="left", padx=6)
        entrada.bind("<Return>", lambda e: self.buscar())
        entrada.focus_set()
        ttk.Button(arriba, text="Buscar", command=self.buscar).pack(side="left")

        self.lbl_info = ttk.Label(marco, text="Escriba el número de la factura y pulse Buscar.")
        self.lbl_info.pack(anchor="w", pady=(10, 4))
        self.zona = ttk.Frame(marco)
        self.zona.pack(fill="both", expand=True)

        botones = ttk.Frame(marco)
        botones.pack(fill="x", pady=(12, 0))
        ttk.Button(botones, text="Cerrar", command=self.destroy).pack(side="right")
        ttk.Button(botones, text="Registrar devolución", style="Acento.TButton",
                   command=self.registrar).pack(side="right", padx=8)
        ttk.Button(botones, text="Devolución total", command=self.llenar_total).pack(side="left")
        self.bind("<Escape>", lambda e: self.destroy())
        self.grab_set()

    def buscar(self):
        try:
            factura = vt.buscar_factura(self.app.ventas, self.var_numero.get())
        except ValueError as error:
            avisar(error, self)
            return
        self.numero = factura["numero"]
        self.lbl_info.configure(
            text=f"Factura {factura['numero']:05d} · {factura['fecha']} · "
                 f"Total {formatear_moneda(factura['total'])}")
        for hijo in self.zona.winfo_children():
            hijo.destroy()
        self.entradas = {}
        for columna, titulo in enumerate(["Producto", "Vendidas", "Ya devueltas", "Devolver ahora"]):
            ttk.Label(self.zona, text=titulo, style="Subtitulo.TLabel").grid(
                row=0, column=columna, padx=8, pady=(0, 4), sticky="w")
        devueltas = vt.cantidades_devueltas(factura)
        for fila, item in enumerate(factura["items"], start=1):
            ya = devueltas.get(item["codigo"], 0)
            pendiente = item["cantidad"] - ya
            ttk.Label(self.zona, text=f"{item['codigo']} · {item['nombre']}").grid(
                row=fila, column=0, padx=8, pady=3, sticky="w")
            ttk.Label(self.zona, text=str(item["cantidad"])).grid(row=fila, column=1)
            ttk.Label(self.zona, text=str(ya)).grid(row=fila, column=2)
            var = tk.StringVar(value="0")
            ttk.Entry(self.zona, textvariable=var, width=8,
                      state="normal" if pendiente > 0 else "disabled").grid(row=fila, column=3, padx=8)
            self.entradas[item["codigo"]] = (var, pendiente)

    def llenar_total(self):
        if self.numero is None:
            avisar("Busque primero una factura.", self)
            return
        for var, pendiente in self.entradas.values():
            var.set(str(pendiente))

    def registrar(self):
        if self.numero is None:
            avisar("Busque primero una factura.", self)
            return
        if not self.app.caja["abierta"]:
            avisar("La caja está cerrada. Ábrala para devolver dinero al cliente.", self)
            return
        items = {}
        for codigo, (var, _pendiente) in self.entradas.items():
            texto = var.get().strip()
            if texto not in ("", "0"):
                items[codigo] = texto

        def operacion():
            # Se busca la factura de nuevo por si los datos fueron restaurados.
            factura = vt.buscar_factura(self.app.ventas, self.numero)
            monto = vt.registrar_devolucion(factura, self.app.productos, items)
            cj.registrar_movimiento(self.app.caja, "devolucion",
                                    f"Devolución factura {factura['numero']:05d}", monto)
            return monto

        correcto, monto = self.app.ejecutar(operacion, parent=self)
        if correcto:
            messagebox.showinfo("Devolución registrada",
                                f"Devuelva al cliente {formatear_moneda(monto)}.", parent=self)
            self.buscar()


# ======================================================================
#  Caja
# ======================================================================
class PantallaCaja(ttk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre, padding=20)
        self.app = app
        ttk.Label(self, text="Caja", style="Titulo.TLabel").pack(anchor="w")
        self.lbl_estado = ttk.Label(self, text="", style="Subtitulo.TLabel")
        self.lbl_estado.pack(anchor="w", pady=(2, 10))

        apertura = ttk.Frame(self)
        apertura.pack(fill="x")
        ttk.Label(apertura, text="Monto inicial: $").pack(side="left")
        self.var_inicial = tk.StringVar(value="100000")
        entrada = ttk.Entry(apertura, textvariable=self.var_inicial, width=14)
        entrada.pack(side="left", padx=(0, 10))
        entrada.bind("<Return>", lambda e: self.abrir())
        self.btn_abrir = ttk.Button(apertura, text="Abrir caja", style="Acento.TButton", command=self.abrir)
        self.btn_abrir.pack(side="left")
        self.btn_cerrar = ttk.Button(apertura, text="Cerrar caja", command=self.cerrar)
        self.btn_cerrar.pack(side="left", padx=8)
        self.btn_ingreso = ttk.Button(apertura, text="Registrar ingreso", command=lambda: self.movimiento("ingreso"))
        self.btn_ingreso.pack(side="left", padx=(24, 0))
        self.btn_egreso = ttk.Button(apertura, text="Registrar egreso", command=lambda: self.movimiento("egreso"))
        self.btn_egreso.pack(side="left", padx=8)

        resumen = ttk.Frame(self)
        resumen.pack(fill="x", pady=16)
        self.valores = {}
        claves = [("inicial", "Monto inicial"), ("ventas", "Ventas"), ("devoluciones", "Devoluciones"),
                  ("otros", "Ingresos / egresos"), ("saldo", "Saldo en caja")]
        for columna, (clave, titulo) in enumerate(claves):
            resumen.columnconfigure(columna, weight=1, uniform="r")
            tarjeta = ttk.Frame(resumen, style="Tarjeta.TFrame", padding=12)
            tarjeta.grid(row=0, column=columna, sticky="ew", padx=(0 if columna == 0 else 8, 0))
            ttk.Label(tarjeta, text=titulo, style="Tarjeta.TLabel").pack(anchor="w")
            etiqueta = ttk.Label(tarjeta, text="-", style="TarjetaValor.TLabel", font=(FUENTE, 15, "bold"))
            etiqueta.pack(anchor="w", pady=(4, 0))
            self.valores[clave] = etiqueta

        ttk.Label(self, text="Movimientos de la sesión", style="Subtitulo.TLabel").pack(anchor="w", pady=(0, 4))
        marco, self.tabla = crear_tabla(self, [
            ("fecha", "Fecha", 150, "center"), ("tipo", "Tipo", 100, "center"),
            ("concepto", "Concepto", 300, "w"), ("monto", "Monto", 110, "e")], alto=12)
        marco.pack(fill="both", expand=True)

    def actualizar(self):
        caja = self.app.caja
        abierta = caja["abierta"]
        if abierta:
            self.lbl_estado.configure(text=f"● Caja ABIERTA desde {caja['fecha_apertura']}", foreground=COLOR_ACENTO)
        else:
            self.lbl_estado.configure(text="● Caja CERRADA", foreground=COLOR_ALERTA)
        self.btn_abrir.configure(state="disabled" if abierta else "normal")
        for boton in (self.btn_cerrar, self.btn_ingreso, self.btn_egreso):
            boton.configure(state="normal" if abierta else "disabled")

        limpiar_tabla(self.tabla)
        ventas = devoluciones = ingresos = egresos = 0
        for mov in reversed(caja["movimientos"]):
            self.tabla.insert("", "end", values=(
                mov["fecha"], mov["tipo"].capitalize(), mov["concepto"], formatear_moneda(mov["monto"])))
        for mov in caja["movimientos"]:
            if mov["tipo"] == "venta":
                ventas += mov["monto"]
            elif mov["tipo"] == "devolucion":
                devoluciones += mov["monto"]
            elif mov["tipo"] == "ingreso":
                ingresos += mov["monto"]
            else:
                egresos += mov["monto"]
        self.valores["inicial"].configure(text=formatear_moneda(caja["monto_inicial"]) if abierta else "-")
        self.valores["ventas"].configure(text=formatear_moneda(ventas))
        self.valores["devoluciones"].configure(text=formatear_moneda(devoluciones))
        self.valores["otros"].configure(text=f"{formatear_moneda(ingresos)} / {formatear_moneda(egresos)}")
        self.valores["saldo"].configure(text=formatear_moneda(cj.calcular_saldo(caja)) if abierta else "-")

    def abrir(self):
        monto = self.var_inicial.get()
        self.app.ejecutar(lambda: cj.abrir_caja(self.app.caja, monto))

    def movimiento(self, tipo):
        concepto = simpledialog.askstring(f"Registrar {tipo}", "Concepto (descripción):", parent=self)
        if concepto is None:
            return
        monto = simpledialog.askstring(f"Registrar {tipo}", "Monto: $", parent=self)
        if monto is None:
            return
        self.app.ejecutar(lambda: cj.registrar_movimiento(self.app.caja, tipo, concepto, monto))

    def cerrar(self):
        if not messagebox.askyesno("Cerrar caja", "¿Cerrar la caja y generar el resumen del turno?"):
            return
        correcto, r = self.app.ejecutar(lambda: cj.cerrar_caja(self.app.caja))
        if correcto:
            messagebox.showinfo("Caja cerrada", (
                f"Apertura: {r['apertura']}\nCierre: {r['cierre']}\n\n"
                f"Monto inicial: {formatear_moneda(r['monto_inicial'])}\n"
                f"Ventas ({r['num_ventas']}): {formatear_moneda(r['ventas'])}\n"
                f"Devoluciones: {formatear_moneda(r['devoluciones'])}\n"
                f"Ingresos: {formatear_moneda(r['ingresos'])}\n"
                f"Egresos: {formatear_moneda(r['egresos'])}\n\n"
                f"SALDO FINAL: {formatear_moneda(r['saldo_final'])}"))


# ======================================================================
#  Reportes
# ======================================================================
class PantallaReportes(ttk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre, padding=20)
        self.app = app
        self.top = []
        ttk.Label(self, text="Reportes", style="Titulo.TLabel").pack(anchor="w")

        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(6, 10))
        ttk.Label(barra, text="Ventas del día (AAAA-MM-DD):").pack(side="left")
        self.var_fecha = tk.StringVar(value=fecha_actual())
        entrada = ttk.Entry(barra, textvariable=self.var_fecha, width=14)
        entrada.pack(side="left", padx=6)
        entrada.bind("<Return>", lambda e: self.consultar())
        ttk.Button(barra, text="Consultar", style="Acento.TButton", command=self.consultar).pack(side="left")
        ttk.Button(barra, text="Hoy", command=self.hoy).pack(side="left", padx=6)

        resumen = ttk.Frame(self)
        resumen.pack(fill="x")
        self.valores = {}
        for columna, (clave, titulo) in enumerate([
                ("facturas", "Facturas"), ("vendido", "Vendido"),
                ("devuelto", "Devuelto"), ("neto", "Neto del día")]):
            resumen.columnconfigure(columna, weight=1, uniform="r")
            tarjeta = ttk.Frame(resumen, style="Tarjeta.TFrame", padding=12)
            tarjeta.grid(row=0, column=columna, sticky="ew", padx=(0 if columna == 0 else 8, 0))
            ttk.Label(tarjeta, text=titulo, style="Tarjeta.TLabel").pack(anchor="w")
            etiqueta = ttk.Label(tarjeta, text="-", style="TarjetaValor.TLabel", font=(FUENTE, 16, "bold"))
            etiqueta.pack(anchor="w", pady=(4, 0))
            self.valores[clave] = etiqueta

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True, pady=(14, 0))
        cuerpo.columnconfigure(0, weight=1)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(1, weight=1)

        ttk.Label(cuerpo, text="Facturas del día", style="Subtitulo.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(cuerpo, text="Productos más vendidos (unidades)", style="Subtitulo.TLabel").grid(
            row=0, column=1, sticky="w", padx=(14, 0))
        marco, self.tabla = crear_tabla(cuerpo, [
            ("numero", "N.º", 70, "center"), ("hora", "Hora", 80, "center"),
            ("items", "Artículos", 80, "center"), ("total", "Total", 110, "e")], alto=12)
        marco.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.lienzo = tk.Canvas(cuerpo, bg="white", highlightthickness=1, highlightbackground="#d1d5db")
        self.lienzo.grid(row=1, column=1, sticky="nsew", padx=(14, 0), pady=(4, 0))
        self.lienzo.bind("<Configure>", lambda e: self.dibujar_grafico())

    def hoy(self):
        self.var_fecha.set(fecha_actual())
        self.consultar()

    def actualizar(self):
        self.consultar(silencioso=True)

    def consultar(self, silencioso=False):
        try:
            fecha = validar_fecha(self.var_fecha.get())
        except ValueError as error:
            if not silencioso:
                avisar(error)
            return
        reporte = cj.generar_reporte(self.app.caja, self.app.ventas, fecha)
        self.valores["facturas"].configure(text=str(reporte["num_facturas"]))
        self.valores["vendido"].configure(text=formatear_moneda(reporte["total_vendido"]))
        self.valores["devuelto"].configure(text=formatear_moneda(reporte["total_devuelto"]))
        self.valores["neto"].configure(text=formatear_moneda(reporte["neto"]))
        limpiar_tabla(self.tabla)
        for factura in reporte["facturas"]:
            articulos = sum(i["cantidad"] for i in factura["items"])
            self.tabla.insert("", "end", values=(
                f"{factura['numero']:05d}", factura["fecha"][11:], articulos,
                formatear_moneda(factura["total"])))
        self.top = reporte["top_productos"]
        self.dibujar_grafico()

    def dibujar_grafico(self):
        """Gráfico de barras horizontales sencillo dibujado en un Canvas."""
        lienzo = self.lienzo
        lienzo.delete("all")
        ancho = max(lienzo.winfo_width(), 300)
        if not self.top:
            lienzo.create_text(ancho / 2, 60, text="Sin ventas en esta fecha", fill="#6b7280")
            return
        maximo = max(unidades for _, unidades in self.top)
        x_barra, x_fin = 150, ancho - 50
        for posicion, (nombre, unidades) in enumerate(self.top):
            y = 28 + posicion * 38
            lienzo.create_text(10, y, text=nombre[:20], anchor="w", fill=COLOR_TEXTO)
            largo = (x_fin - x_barra) * unidades / maximo
            lienzo.create_rectangle(x_barra, y - 12, x_barra + largo, y + 12, fill=COLOR_ACENTO, outline="")
            lienzo.create_text(x_barra + largo + 6, y, text=str(unidades), anchor="w", fill=COLOR_TEXTO)
