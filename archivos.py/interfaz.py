
import tkinter as tk
from tkinter import messagebox


# Funcion para abrir la ventana principal
def iniciar_interfaz():

    ventana = tk.Tk()
    ventana.title("Sistema de Gestion de Supermercado")
    ventana.geometry("800x600")
    ventana.config(bg="#eeeeee")

    # Titulo del sistema
    titulo = tk.Label(
        ventana,
        text="SISTEMA DE GESTION DE SUPERMERCADO",
        font=("Arial", 20, "bold"),
        bg="#eeeeee"
    )
    titulo.pack(pady=30)

    # Subtitulo
    subtitulo = tk.Label(
        ventana,
        text="Menu Principal",
        font=("Arial", 15),
        bg="#eeeeee"
    )
    subtitulo.pack(pady=10)

    # Botones del menu
    boton_inventario = tk.Button(
        ventana,
        text="Inventario",
        width=25,
        height=2
    )
    boton_inventario.pack(pady=10)

    boton_ventas = tk.Button(
        ventana,
        text="Ventas",
        width=25,
        height=2
    )
    boton_ventas.pack(pady=10)

    boton_caja = tk.Button(
        ventana,
        text="Caja",
        width=25,
        height=2
    )
    boton_caja.pack(pady=10)

    boton_reportes = tk.Button(
        ventana,
        text="Reportes",
        width=25,
        height=2
    )
    boton_reportes.pack(pady=10)

    boton_salir = tk.Button(
        ventana,
        text="Salir",
        width=25,
        height=2,
        command=ventana.destroy
    )
    boton_salir.pack(pady=20)

    ventana.mainloop()


# Funcion principal
if __name__ == "__main__":
    iniciar_interfaz()
