"""
ventas.py
Carrito, cálculo de totales, pago, facturas y devoluciones (8 funciones + 1 auxiliar).

El carrito es una lista de diccionarios:
    {"codigo": "P001", "nombre": "Arroz", "cantidad": 2, "precio": 4000}

`ventas` (lo que se guarda en ventas.json) es:
    {"siguiente_factura": 1, "facturas": [ ... ]}
"""

from funciones import (
    TASA_IMPUESTO,
    UMBRAL_DESCUENTO,
    PORCENTAJE_DESCUENTO,
    normalizar_codigo,
    validar_entero_positivo,
    validar_numero,
    fecha_hora_actual,
    formatear_moneda,
)
from inventario import verificar_stock, registrar_salida


def agregar_carrito(carrito, productos, codigo, cantidad):
    """Agrega un producto al carrito validando existencia, estado y stock."""
    codigo = normalizar_codigo(codigo)
    if codigo not in productos:
        raise ValueError(f"El producto {codigo} no existe")
    cantidad = validar_entero_positivo(cantidad)

    # Si el producto ya está en el carrito, se suma a lo que ya había.
    for linea in carrito:
        if linea["codigo"] == codigo:
            verificar_stock(productos, codigo, linea["cantidad"] + cantidad)
            linea["cantidad"] += cantidad
            return carrito

    verificar_stock(productos, codigo, cantidad)
    carrito.append({
        "codigo": codigo,
        "nombre": productos[codigo]["nombre"],
        "cantidad": cantidad,
        "precio": productos[codigo]["precio_venta"],
    })
    return carrito


def retirar_carrito(carrito, codigo, cantidad=None):
    """Quita un producto del carrito. Sin cantidad, lo quita completo."""
    codigo = normalizar_codigo(codigo)
    for posicion, linea in enumerate(carrito):
        if linea["codigo"] == codigo:
            if cantidad is None:
                del carrito[posicion]
            else:
                cantidad = validar_entero_positivo(cantidad)
                if cantidad >= linea["cantidad"]:
                    del carrito[posicion]
                else:
                    linea["cantidad"] -= cantidad
            return carrito
    raise ValueError(f"El producto {codigo} no está en el carrito")


def calcular_subtotal(carrito):
    """Total de la compra sin descuentos ni impuestos."""
    subtotal = 0
    for linea in carrito:
        subtotal += linea["cantidad"] * linea["precio"]
    return round(subtotal)


def calcular_descuento(subtotal, porcentaje=None):
    """Descuento en pesos. Si no se indica porcentaje, se aplica la regla del negocio
    (PORCENTAJE_DESCUENTO % cuando el subtotal llega a UMBRAL_DESCUENTO)."""
    if porcentaje is None:
        porcentaje = PORCENTAJE_DESCUENTO if subtotal >= UMBRAL_DESCUENTO else 0
    return round(subtotal * porcentaje / 100)


def calcular_impuesto(base, tasa=TASA_IMPUESTO):
    """Impuesto (IVA) sobre el valor ya descontado."""
    return round(base * tasa)


def calcular_totales(carrito):
    """Auxiliar: reúne subtotal, descuento, impuesto y total en un diccionario."""
    subtotal = calcular_subtotal(carrito)
    descuento = calcular_descuento(subtotal)
    impuesto = calcular_impuesto(subtotal - descuento)
    return {
        "subtotal": subtotal,
        "descuento": descuento,
        "impuesto": impuesto,
        "total": subtotal - descuento + impuesto,
    }


def procesar_pago(total, pago):
    """Valida el dinero entregado y devuelve el cambio."""
    pago = validar_numero(pago, "Ingrese un valor de pago válido")
    if pago < total:
        raise ValueError("Falta dinero para completar el pago")
    return round(pago - total)


def generar_factura(carrito, productos, ventas, pago):
    """Cierra la venta: valida todo, descuenta el stock y crea la factura.

    Primero se revisa TODO el carrito y solo después se descuenta el stock,
    así una venta inválida nunca deja el inventario a medias.
    """
    if not carrito:
        raise ValueError("El carrito está vacío")
    for linea in carrito:
        verificar_stock(productos, linea["codigo"], linea["cantidad"])

    totales = calcular_totales(carrito)
    cambio = procesar_pago(totales["total"], pago)

    for linea in carrito:
        registrar_salida(productos, linea["codigo"], linea["cantidad"])

    factura = {
        "numero": ventas["siguiente_factura"],
        "fecha": fecha_hora_actual(),
        "items": [
            {
                "codigo": l["codigo"],
                "nombre": l["nombre"],
                "cantidad": l["cantidad"],
                "precio": l["precio"],
                "subtotal": round(l["cantidad"] * l["precio"]),
            }
            for l in carrito
        ],
        "subtotal": totales["subtotal"],
        "descuento": totales["descuento"],
        "impuesto": totales["impuesto"],
        "total": totales["total"],
        "pago": validar_numero(pago),
        "cambio": cambio,
        "devoluciones": [],
    }
    ventas["facturas"].append(factura)
    ventas["siguiente_factura"] += 1
    return factura


def registrar_devolucion(factura, productos, items):
    """Devolución total o parcial de una factura.

    `items` es un diccionario {código: cantidad a devolver}.
    El stock sube solo en lo devuelto. Devuelve el dinero a reembolsar.
    """
    if not items:
        raise ValueError("Seleccione al menos un producto para devolver")

    ya_devuelto = cantidades_devueltas(factura)
    vendidas = {i["codigo"]: i["cantidad"] for i in factura["items"]}
    precios = {i["codigo"]: i["precio"] for i in factura["items"]}

    # 1) Validar todo antes de modificar nada.
    for codigo, cantidad in items.items():
        if codigo not in vendidas:
            raise ValueError(f"El producto {codigo} no está en la factura {factura['numero']}")
        cantidad = validar_entero_positivo(cantidad)
        disponible = vendidas[codigo] - ya_devuelto.get(codigo, 0)
        if cantidad > disponible:
            raise ValueError(
                f"No se puede devolver {cantidad} de {codigo}: solo quedan {disponible} por devolver")

    # 2) Calcular el reembolso proporcional al descuento e impuesto de la factura.
    valor_items = sum(int(c) * precios[k] for k, c in items.items())
    reembolsado = sum(d["monto"] for d in factura["devoluciones"])
    quedan_total = sum(vendidas[k] - ya_devuelto.get(k, 0) for k in vendidas)
    devuelve_total = sum(int(c) for c in items.values())
    if devuelve_total == quedan_total:
        monto = factura["total"] - reembolsado  # última devolución: cuadra al peso
    else:
        monto = round(valor_items * factura["total"] / factura["subtotal"])

    # 3) Aplicar: subir stock y guardar la devolución en la factura.
    for codigo, cantidad in items.items():
        if codigo in productos:
            productos[codigo]["stock"] += int(cantidad)
    factura["devoluciones"].append({
        "fecha": fecha_hora_actual(),
        "items": {k: int(c) for k, c in items.items()},
        "monto": monto,
    })
    return monto


def cantidades_devueltas(factura):
    """Auxiliar: {código: unidades ya devueltas} de una factura."""
    devuelto = {}
    for devolucion in factura["devoluciones"]:
        for codigo, cantidad in devolucion["items"].items():
            devuelto[codigo] = devuelto.get(codigo, 0) + cantidad
    return devuelto


def buscar_factura(ventas, numero):
    """Auxiliar: devuelve la factura con ese número."""
    try:
        numero = int(str(numero).strip().lstrip("#"))
    except ValueError:
        raise ValueError("Ingrese un número de factura válido")
    for factura in ventas["facturas"]:
        if factura["numero"] == numero:
            return factura
    raise ValueError(f"No existe la factura {numero}")


def formatear_factura(factura):
    """Auxiliar: texto de la factura listo para mostrar o imprimir."""
    linea = "=" * 44
    texto = [
        linea,
        "        SUPERMERCADO - FACTURA DE VENTA",
        linea,
        f"Factura N.º {factura['numero']:05d}",
        f"Fecha: {factura['fecha']}",
        "-" * 44,
    ]
    for item in factura["items"]:
        texto.append(f"{item['nombre'][:22]:<22} {item['cantidad']:>3} x {formatear_moneda(item['precio']):>8}")
        texto.append(f"{'':>34}{formatear_moneda(item['subtotal']):>10}")
    texto += [
        "-" * 44,
        f"{'Subtotal':<30}{formatear_moneda(factura['subtotal']):>14}",
        f"{'Descuento':<30}{'-' + formatear_moneda(factura['descuento']):>14}",
        f"{'Impuesto (IVA)':<30}{formatear_moneda(factura['impuesto']):>14}",
        f"{'TOTAL':<30}{formatear_moneda(factura['total']):>14}",
        f"{'Pago':<30}{formatear_moneda(factura['pago']):>14}",
        f"{'Cambio':<30}{formatear_moneda(factura['cambio']):>14}",
        linea,
        "          ¡Gracias por su compra!",
    ]
    return "\n".join(texto)
