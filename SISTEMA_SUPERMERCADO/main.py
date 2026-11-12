"""
main.py
Punto de entrada del Sistema de Gestión de Supermercado.
Ejecutar con:  python main.py
"""

from interfaz import AplicacionSupermercado


def main():
    app = AplicacionSupermercado()
    app.mainloop()  # mantiene el programa activo hasta que el usuario cierre la ventana


if __name__ == "__main__":
    main()
