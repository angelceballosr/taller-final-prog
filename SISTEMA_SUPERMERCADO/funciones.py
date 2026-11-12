"""
funciones.py
Utilidades compartidas por todos los módulos: validar datos, dar formato y fechas.
Todas las validaciones lanzan ValueError con el mensaje que se le muestra al usuario.
"""

import math
from datetime import datetime

# ---- Reglas del negocio (se pueden cambiar aquí) ----
TASA_IMPUESTO = 0.19          # IVA 19 %
UMBRAL_DESCUENTO = 100000     # compras desde este subtotal reciben descuento
PORCENTAJE_DESCUENTO = 5      # % de descuento


def normalizar_codigo(texto):
    """Quita espacios y pone el código en mayúsculas: ' p001 ' -> 'P001'."""
    return str(texto).strip().upper()


def validar_entero_positivo(texto, mensaje="Ingrese una cantidad válida"):
    """Convierte a int y exige que sea mayor que cero (try int() + cantidad > 0)."""
    try:
        valor = int(str(texto).strip())
    except (ValueError, TypeError):
        raise ValueError(mensaje)
    if valor <= 0:
        raise ValueError(mensaje)
    return valor


def validar_entero_no_negativo(texto, mensaje="Ingrese un número entero válido"):
    """Igual que el anterior pero permite el cero (por ejemplo, stock mínimo)."""
    try:
        valor = int(str(texto).strip())
    except (ValueError, TypeError):
        raise ValueError(mensaje)
    if valor < 0:
        raise ValueError(mensaje)
    return valor


def validar_numero(texto, mensaje="Ingrese un valor numérico válido"):
    """Convierte un texto a número (admite '$' y espacios). No acepta NaN ni infinito."""
    try:
        limpio = str(texto).replace("$", "").replace(" ", "").strip()
        valor = float(limpio)
    except (ValueError, TypeError):
        raise ValueError(mensaje)
    if not math.isfinite(valor):
        raise ValueError(mensaje)
    return int(valor) if valor.is_integer() else valor


def validar_precio(texto):
    """Número válido y no negativo."""
    valor = validar_numero(texto, "Ingrese un precio válido")
    if valor < 0:
        raise ValueError("El precio no puede ser negativo")
    return valor


def formatear_moneda(valor):
    """4000 -> '$4.000' (separador de miles con punto, como en Colombia)."""
    entero = int(round(valor))
    signo = "-" if entero < 0 else ""
    return signo + "$" + f"{abs(entero):,}".replace(",", ".")


def fecha_hora_actual():
    """Fecha y hora como texto: '2026-11-11 23:30:00'."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fecha_actual():
    """Solo la fecha: '2026-11-11'."""
    return datetime.now().strftime("%Y-%m-%d")


def validar_fecha(texto):
    """Verifica el formato AAAA-MM-DD y devuelve el texto limpio."""
    texto = str(texto).strip()
    try:
        datetime.strptime(texto, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Escriba la fecha como AAAA-MM-DD, por ejemplo 2026-11-11")
    return texto
