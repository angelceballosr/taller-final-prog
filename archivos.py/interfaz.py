import tkinter as tk
from tkinter import ttk, messagebox

from inventario import (
    cargar_productos,
    registrar_producto,
    consultar_inventario,
    buscar_producto,
    editar_producto,
    desactivar_producto,
    registrar_entrada,
    registrar_salida,
    verificar_stock
)


# Diccionario que contiene todos los productos
productos = cargar_productos()


# Abre la ventana de inventario
def abrir_inventario():
    ventana = tk.Toplevel(ventana_principal)
    ventana.title("Inventario - Supermercado")
    ventana.geometry("1100x700")
    ventana.config(bg="#f2f4f7")

    # Titulo
    titulo = tk.Label(
        ventana,
        text="GESTION DE INVENTARIO",
        font=("Arial", 20, "bold"),
        bg="#f2f4f7",
        fg="#1f2937"
    )
    titulo.pack(pady=12)

    # Marco para los campos del formulario
    marco_formulario = tk.LabelFrame(
        ventana,
        text="Datos del producto",
        font=("Arial", 11, "bold"),
        bg="#f2f4f7",
        padx=10,
        pady=10
    )
    marco_formulario.pack(fill="x", padx=15, pady=8)

    etiquetas = [
        "Codigo", "Nombre", "Categoria", "Precio compra",
        "Precio venta", "Stock", "Stock minimo"
    ]

    entradas = {}

    for i, nombre_campo in enumerate(etiquetas):
        fila = i // 4
        columna = (i % 4) * 2

        etiqueta = tk.Label(
            marco_formulario,
            text=nombre_campo + ":",
            bg="#f2f4f7",
            font=("Arial", 10)
        )
        etiqueta.grid(row=fila, column=columna, padx=5, pady=7, sticky="w")

        entrada = tk.Entry(marco_formulario, width=18)
        entrada.grid(row=fila, column=columna + 1, padx=5, pady=7)

        entradas[nombre_campo] = entrada

    # Marco para la tabla
    marco_tabla = tk.LabelFrame(
        ventana,
        text="Productos registrados",
        font=("Arial", 11, "bold"),
        bg="#f2f4f7",
        padx=8,
        pady=8
    )
    marco_tabla.pack(fill="both", expand=True, padx=15, pady=8)

    columnas = (
        "codigo", "nombre", "categoria", "compra",
        "venta", "stock", "minimo", "estado"
    )

    tabla = ttk.Treeview(
        marco_tabla,
        columns=columnas,
        show="headings",
        height=13
    )

    titulos_columnas = {
        "codigo": "Codigo",
        "nombre": "Nombre",
        "categoria": "Categoria",
        "compra": "Precio compra",
        "venta": "Precio venta",
        "stock": "Stock",
        "minimo": "Stock minimo",
        "estado": "Estado"
    }

    anchos = {
        "codigo": 85, "nombre": 150, "categoria": 120,
        "compra": 110, "venta": 110, "stock": 70,
        "minimo": 90, "estado": 90
    }

    for columna in columnas:
        tabla.heading(columna, text=titulos_columnas[columna])
        tabla.column(columna, width=anchos[columna], anchor="center")

    tabla.pack(side="left", fill="both", expand=True)

    barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")

    tabla.tag_configure("bajo", background="#ffe0e0")
    tabla.tag_configure("desactivado", foreground="gray")

    # Muestra los productos en la tabla
    def actualizar_tabla():
        for elemento in tabla.get_children():
            tabla.delete(elemento)

        for codigo, producto in consultar_inventario(productos).items():
            estado = "Activo" if producto.get("activo", True) else "Inactivo"

            if estado == "Inactivo":
                etiqueta_fila = "desactivado"
            elif producto["stock"] <= producto["stock_minimo"]:
                etiqueta_fila = "bajo"
            else:
                etiqueta_fila = ""

            tabla.insert(
                "",
                "end",
                values=(
                    codigo,
                    producto["nombre"],
                    producto["categoria"],
                    producto["precio_compra"],
                    producto["precio_venta"],
                    producto["stock"],
                    producto["stock_minimo"],
                    estado
                ),
                tags=(etiqueta_fila,)
            )

    # Limpia los campos del formulario
    def limpiar_campos():
        for entrada in entradas.values():
            entrada.delete(0, tk.END)

    # Lee los datos escritos en el formulario
    def leer_datos():
        codigo = entradas["Codigo"].get().strip()
        nombre = entradas["Nombre"].get().strip()
        categoria = entradas["Categoria"].get().strip()

        try:
            precio_compra = float(entradas["Precio compra"].get())
            precio_venta = float(entradas["Precio venta"].get())
            stock = int(entradas["Stock"].get())
            stock_minimo = int(entradas["Stock minimo"].get())

            return (
                codigo, nombre, categoria, precio_compra,
                precio_venta, stock, stock_minimo
            )

        except ValueError:
            messagebox.showerror(
                "Dato incorrecto",
                "Los precios deben ser numeros y las cantidades deben ser enteros."
            )
            return None

    # Registra un producto
    def accion_registrar():
        datos = leer_datos()

        if datos is None:
            return

        resultado, mensaje = registrar_producto(productos, *datos)
        if resultado:
            messagebox.showinfo("Inventario", mensaje)
            actualizar_tabla()
            limpiar_campos()
        else:
            messagebox.showwarning("Inventario", mensaje)

    # Busca un producto por codigo
    def accion_buscar():
        codigo = entradas["Codigo"].get().strip()
        producto = buscar_producto(productos, codigo)

        if producto is None:
            messagebox.showwarning("Busqueda", "No se encontro ese producto.")
            return

        entradas["Nombre"].delete(0, tk.END)
        entradas["Nombre"].insert(0, producto["nombre"])

        entradas["Categoria"].delete(0, tk.END)
        entradas["Categoria"].insert(0, producto["categoria"])

        entradas["Precio compra"].delete(0, tk.END)
        entradas["Precio compra"].insert(0, str(producto["precio_compra"]))

        entradas["Precio venta"].delete(0, tk.END)
        entradas["Precio venta"].insert(0, str(producto["precio_venta"]))

        entradas["Stock"].delete(0, tk.END)
        entradas["Stock"].insert(0, str(producto["stock"]))

        entradas["Stock minimo"].delete(0, tk.END)
        entradas["Stock minimo"].insert(0, str(producto["stock_minimo"]))

    # Carga en el formulario el producto seleccionado en la tabla
    def seleccionar_producto(evento):
        seleccionado = tabla.selection()

        if seleccionado:
            valores = tabla.item(seleccionado[0], "values")
            limpiar_campos()

            entradas["Codigo"].insert(0, valores[0])
            entradas["Nombre"].insert(0, valores[1])
            entradas["Categoria"].insert(0, valores[2])
            entradas["Precio compra"].insert(0, valores[3])
            entradas["Precio venta"].insert(0, valores[4])
            entradas["Stock"].insert(0, valores[5])
            entradas["Stock minimo"].insert(0, valores[6])

    tabla.bind("<<TreeviewSelect>>", seleccionar_producto)

    # Edita el producto que tiene el codigo escrito
    def accion_editar():
        datos = leer_datos()

        if datos is None:
            return

        resultado, mensaje = editar_producto(productos, *datos)
        if resultado:
            messagebox.showinfo("Inventario", mensaje)
            actualizar_tabla()
            limpiar_campos()
        else:
            messagebox.showwarning("Inventario", mensaje)

    # Desactiva el producto indicado
    def accion_desactivar():
        codigo = entradas["Codigo"].get().strip()

        if codigo == "":
            messagebox.showwarning("Inventario", "Escriba o seleccione un codigo.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Desea desactivar el producto " + codigo + "?"
        )

        if confirmar:
            resultado, mensaje = desactivar_producto(productos, codigo)
            if resultado:
                messagebox.showinfo("Inventario", mensaje)
                actualizar_tabla()
                limpiar_campos()
            else:
                messagebox.showwarning("Inventario", mensaje)

    # Registra una entrada o salida de unidades
    def accion_movimiento(tipo):
        codigo = entradas["Codigo"].get().strip()

        if codigo == "":
            messagebox.showwarning("Inventario", "Escriba o seleccione un codigo.")
            return

        ventana_cantidad = tk.Toplevel(ventana)
        ventana_cantidad.title("Cantidad")
        ventana_cantidad.geometry("300x160")
        ventana_cantidad.config(bg="#f2f4f7")
        ventana_cantidad.transient(ventana)
        ventana_cantidad.grab_set()

        texto = "Cantidad que ingresa:" if tipo == "entrada" else "Cantidad que sale:"

        tk.Label(
            ventana_cantidad,
            text=texto,
            bg="#f2f4f7",
            font=("Arial", 11)
        ).pack(pady=12)

        campo_cantidad = tk.Entry(ventana_cantidad)
        campo_cantidad.pack(pady=5)
        campo_cantidad.focus()

        def confirmar_movimiento():
            try:
                cantidad = int(campo_cantidad.get())

                if tipo == "entrada":
                    resultado, mensaje = registrar_entrada(productos, codigo, cantidad)
                else:
                    resultado, mensaje = registrar_salida(productos, codigo, cantidad)

                if resultado:
                    messagebox.showinfo("Inventario", mensaje)
                    actualizar_tabla()
                    limpiar_campos()
                    ventana_cantidad.destroy()
                else:
                    messagebox.showwarning("Inventario", mensaje)

            except ValueError:
                messagebox.showerror("Dato incorrecto", "Ingrese una cantidad entera.")

        tk.Button(
            ventana_cantidad,
            text="Aceptar",
            command=confirmar_movimiento,
            width=15
        ).pack(pady=10)

    # Muestra los productos con stock bajo
    def accion_stock_bajo():
        bajos = verificar_stock(productos)

        if len(bajos) == 0:
            messagebox.showinfo("Stock", "No hay productos con stock bajo.")
        else:
            mensaje = "Productos con existencias bajas:\n\n"

            for codigo, producto in bajos:
                mensaje += (
                    codigo + " - " + producto["nombre"]
                    + " | Stock: " + str(producto["stock"])
                    + " | Minimo: " + str(producto["stock_minimo"])
                    + "\n"
                )

            messagebox.showwarning("Stock bajo", mensaje)

    # Botones de acciones
    marco_botones = tk.Frame(ventana, bg="#f2f4f7")
    marco_botones.pack(pady=10)

    botones = [
        ("Registrar", accion_registrar),
        ("Buscar", accion_buscar),
        ("Editar", accion_editar),
        ("Desactivar", accion_desactivar),
        ("Entrada", lambda: accion_movimiento("entrada")),
        ("Salida", lambda: accion_movimiento("salida")),
        ("Stock bajo", accion_stock_bajo),
        ("Limpiar", limpiar_campos)
    ]

    for i, (texto, comando) in enumerate(botones):
        boton = tk.Button(
            marco_botones,
            text=texto,
            command=comando,
            width=13,
            height=2,
            bg="#dce6f1",
            font=("Arial", 9, "bold")
        )
        boton.grid(row=i // 4, column=i % 4, padx=5, pady=5)

    actualizar_tabla()


# Crea la ventana principal del sistema
def iniciar_interfaz():
    global ventana_principal

    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de Gestion de Supermercado")
    ventana_principal.geometry("800x550")
    ventana_principal.config(bg="#eeeeee")

    titulo = tk.Label(
        ventana_principal,
        text="SISTEMA DE GESTION DE SUPERMERCADO",
        font=("Arial", 20, "bold"),
        bg="#eeeeee"
    )
    titulo.pack(pady=35)

    subtitulo = tk.Label(
        ventana_principal,
        text="Menu Principal",
        font=("Arial", 15),
        bg="#eeeeee"
    )
    subtitulo.pack(pady=10)

    boton_inventario = tk.Button(
        ventana_principal,
        text="Inventario",
        width=25,
        height=2,
        command=abrir_inventario
    )
    boton_inventario.pack(pady=10)

    # Los otros modulos se conectaran en las siguientes etapas
    boton_ventas = tk.Button(
        ventana_principal,
        text="Ventas",
        width=25,
        height=2,
        command=lambda: messagebox.showinfo("Ventas", "Este modulo se conectara despues.")
    )
    boton_ventas.pack(pady=10)

    boton_caja = tk.Button(
        ventana_principal,
        text="Caja",
        width=25,
        height=2,
        command=lambda: messagebox.showinfo("Caja", "Este modulo se conectara despues.")
    )
    boton_caja.pack(pady=10)

    boton_reportes = tk.Button(
        ventana_principal,
        text="Reportes",
        width=25,
        height=2,
        command=lambda: messagebox.showinfo("Reportes", "Este modulo se conectara despues.")
    )
    boton_reportes.pack(pady=10)

    boton_salir = tk.Button(
        ventana_principal,
        text="Salir",
        width=25,
        height=2,
        command=ventana_principal.destroy
    )
    boton_salir.pack(pady=20)

    ventana_principal.mainloop()


if __name__ == "__main__":
    iniciar_interfaz()
