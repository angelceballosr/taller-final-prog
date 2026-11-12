"""
caja.py
Apertura, movimientos, cierre de caja y reportes (4 funciones + 1 auxiliar).

`caja` (lo que se guarda en caja.json) es:
    {"abierta": False, "monto_inicial": 0, "fecha_apertura": None,
     "movimientos": [ {fecha, tipo, concepto, monto} ], "historial": [ cierres ]}

Tipos de movimiento: "venta" e "ingreso" suman; "devolucion" y "egreso" restan.
"""

from funciones import validar_numero, fecha_hora_actual, fecha_actual

TIPOS_SUMAN = ("venta", "ingreso")
TIPOS_RESTAN = ("devolucion", "egreso")


def abrir_caja(caja, monto_inicial):
    """Abre la caja con un monto inicial."""
    if caja["abierta"]:
        raise ValueError("La caja ya está abierta")
    monto = validar_numero(monto_inicial, "Ingrese un monto inicial válido")
    if monto < 0:
        raise ValueError("El monto inicial no puede ser negativo")
    caja["abierta"] = True
    caja["monto_inicial"] = monto
    caja["fecha_apertura"] = fecha_hora_actual()
    caja["movimientos"] = []
    return caja


def registrar_movimiento(caja, tipo, concepto, monto):
    """Registra una venta, devolución, ingreso o egreso en la caja abierta."""
    if not caja["abierta"]:
        raise ValueError("La caja está cerrada. Ábrala primero")
    if tipo not in TIPOS_SUMAN + TIPOS_RESTAN:
        raise ValueError(f"Tipo de movimiento no válido: {tipo}")
    monto = validar_numero(monto, "Ingrese un monto válido")
    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero")
    if tipo in TIPOS_RESTAN and monto > calcular_saldo(caja):
        raise ValueError("No hay suficiente dinero en caja para ese movimiento")
    caja["movimientos"].append({
        "fecha": fecha_hora_actual(),
        "tipo": tipo,
        "concepto": str(concepto).strip() or tipo.capitalize(),
        "monto": monto,
    })
    return caja


def calcular_saldo(caja):
    """Auxiliar: dinero que debería haber en caja ahora mismo."""
    saldo = caja["monto_inicial"]
    for mov in caja["movimientos"]:
        if mov["tipo"] in TIPOS_SUMAN:
            saldo += mov["monto"]
        else:
            saldo -= mov["monto"]
    return saldo


def _total_por_tipo(caja, tipo):
    total = 0
    for mov in caja["movimientos"]:
        if mov["tipo"] == tipo:
            total += mov["monto"]
    return total


def cerrar_caja(caja):
    """Cierra la caja, guarda el resumen en el historial y lo devuelve."""
    if not caja["abierta"]:
        raise ValueError("La caja ya está cerrada")
    resumen = {
        "apertura": caja["fecha_apertura"],
        "cierre": fecha_hora_actual(),
        "monto_inicial": caja["monto_inicial"],
        "ventas": _total_por_tipo(caja, "venta"),
        "num_ventas": sum(1 for m in caja["movimientos"] if m["tipo"] == "venta"),
        "devoluciones": _total_por_tipo(caja, "devolucion"),
        "ingresos": _total_por_tipo(caja, "ingreso"),
        "egresos": _total_por_tipo(caja, "egreso"),
        "saldo_final": calcular_saldo(caja),
    }
    caja["historial"].append(resumen)
    caja["abierta"] = False
    caja["monto_inicial"] = 0
    caja["fecha_apertura"] = None
    caja["movimientos"] = []
    return resumen


def generar_reporte(caja, ventas, fecha=None):
    """Reporte de ventas de un día (AAAA-MM-DD). Sin fecha, usa el día de hoy.

    Devuelve un diccionario con totales, las facturas del día, los productos
    más vendidos y el estado actual de la caja.
    """
    fecha = fecha or fecha_actual()
    facturas_dia = [f for f in ventas["facturas"] if f["fecha"][:10] == fecha]

    total_vendido = sum(f["total"] for f in facturas_dia)
    total_devuelto = 0
    for factura in ventas["facturas"]:
        for dev in factura["devoluciones"]:
            if dev["fecha"][:10] == fecha:
                total_devuelto += dev["monto"]

    unidades = {}
    for factura in facturas_dia:
        for item in factura["items"]:
            nombre = item["nombre"]
            unidades[nombre] = unidades.get(nombre, 0) + item["cantidad"]
    top = sorted(unidades.items(), key=lambda par: par[1], reverse=True)[:5]

    return {
        "fecha": fecha,
        "num_facturas": len(facturas_dia),
        "total_vendido": total_vendido,
        "total_devuelto": total_devuelto,
        "neto": total_vendido - total_devuelto,
        "facturas": facturas_dia,
        "top_productos": top,
        "caja_abierta": caja["abierta"],
        "saldo_caja": calcular_saldo(caja) if caja["abierta"] else None,
    }
