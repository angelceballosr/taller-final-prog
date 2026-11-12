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