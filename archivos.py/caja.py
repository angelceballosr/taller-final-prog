
# ==========================================
# MODULO DE CAJA
# SISTEMA DE GESTION DE SUPERMERCADO
# ==========================================


# 1. ABRIR CAJA
def abrir_caja(caja, dinero_inicial):

    try:
        dinero_inicial = float(dinero_inicial)

        if dinero_inicial < 0:
            return False, "El dinero inicial no puede ser negativo"

        if caja.get("abierta", False):
            return False, "La caja ya se encuentra abierta"

        caja["abierta"] = True
        caja["dinero_inicial"] = dinero_inicial
        caja["dinero_actual"] = dinero_inicial
        caja["movimientos"] = []

        return True, "Caja abierta correctamente"

    except (ValueError, TypeError):
        return False, "Ingrese un valor numerico valido"


# 2. REGISTRAR MOVIMIENTO DE CAJA
def registrar_movimiento(caja, tipo, valor, descripcion):

    try:
        valor = float(valor)
        tipo = tipo.strip().lower()
        descripcion = descripcion.strip()

        if not caja.get("abierta", False):
            return False, "Primero debe abrir la caja"

        if valor <= 0:
            return False, "El valor debe ser mayor que cero"

        if descripcion == "":
            return False, "Debe ingresar una descripcion"

        if tipo not in ["entrada", "salida"]:
            return False, "Tipo de movimiento no valido"

        if tipo == "salida":

            if valor > caja["dinero_actual"]:
                return False, "No hay suficiente dinero en caja"

            caja["dinero_actual"] -= valor

        elif tipo == "entrada":

            caja["dinero_actual"] += valor

        movimiento = {
            "tipo": tipo,
            "valor": valor,
            "descripcion": descripcion
        }

        caja["movimientos"].append(movimiento)

        return True, "Movimiento registrado correctamente"

    except (ValueError, TypeError, KeyError):
        return False, "No se pudo registrar el movimiento"


# 3. REGISTRAR UNA VENTA EN CAJA
def registrar_venta_caja(caja, total):

    try:
        total = float(total)

        if not caja.get("abierta", False):
            return False, "La caja se encuentra cerrada"

        if total <= 0:
            return False, "El total de la venta debe ser mayor que cero"

        caja["dinero_actual"] += total

        movimiento = {
            "tipo": "entrada",
            "valor": total,
            "descripcion": "Venta de productos"
        }

        caja["movimientos"].append(movimiento)

        return True, "Venta registrada en caja correctamente"

    except (ValueError, TypeError, KeyError):
        return False, "Error al registrar la venta"


# 4. CONSULTAR DINERO ACTUAL
def consultar_dinero(caja):

    if not caja.get("abierta", False):
        return 0

    return caja.get("dinero_actual", 0)


# 5. CONSULTAR MOVIMIENTOS
def consultar_movimientos(caja):

    movimientos = []

    for movimiento in caja.get("movimientos", []):
        movimientos.append(movimiento.copy())

    return movimientos


# 6. CALCULAR TOTAL DE ENTRADAS
def calcular_entradas(caja):

    total = 0

    for movimiento in caja.get("movimientos", []):

        if movimiento["tipo"] == "entrada":
            total += movimiento["valor"]

    return total


# 7. CALCULAR TOTAL DE SALIDAS
def calcular_salidas(caja):

    total = 0

    for movimiento in caja.get("movimientos", []):

        if movimiento["tipo"] == "salida":
            total += movimiento["valor"]

    return total


# 8. GENERAR REPORTE DE CAJA
def generar_reporte(caja):

    if not caja.get("abierta", False):
        return None

    entradas = calcular_entradas(caja)
    salidas = calcular_salidas(caja)

    reporte = {
        "dinero_inicial": caja["dinero_inicial"],
        "total_entradas": entradas,
        "total_salidas": salidas,
        "dinero_actual": caja["dinero_actual"],
        "cantidad_movimientos": len(caja["movimientos"])
    }

    return reporte


# 9. CERRAR CAJA
def cerrar_caja(caja, dinero_contado=None):

    if not caja.get("abierta", False):
        return False, "La caja ya se encuentra cerrada"

    try:
        dinero_esperado = caja["dinero_actual"]

        if dinero_contado is None:
            dinero_contado = dinero_esperado

        dinero_contado = float(dinero_contado)

        if dinero_contado < 0:
            return False, "El dinero contado no puede ser negativo"

        diferencia = dinero_contado - dinero_esperado

        reporte = {
            "dinero_inicial": caja["dinero_inicial"],
            "dinero_esperado": dinero_esperado,
            "dinero_contado": dinero_contado,
            "diferencia": diferencia,
            "total_entradas": calcular_entradas(caja),
            "total_salidas": calcular_salidas(caja),
            "cantidad_movimientos": len(caja["movimientos"])
        }

        caja["abierta"] = False
        caja["ultimo_cierre"] = reporte.copy()

        return True, reporte

    except (ValueError, TypeError, KeyError):
        return False, "Error al cerrar la caja"
