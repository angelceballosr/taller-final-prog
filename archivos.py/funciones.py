
# ==========================================
# MODULO DE FUNCIONES GENERALES
# SISTEMA DE GESTION DE SUPERMERCADO
# ==========================================


# 1. VALIDAR CAMPOS DE TEXTO
def validar_texto(texto):

    texto = str(texto).strip()

    if texto == "":
        return False

    return True


# 2. VALIDAR NUMEROS ENTEROS
def validar_numero(valor):

    try:
        numero = int(valor)

        if numero < 0:
            return False

        return True

    except (ValueError, TypeError):
        return False


# 3. FORMATEAR PRECIOS
def formatear_precio(precio):

    return "$ {:,}".format(precio).replace(",", ".")


# 4. CALCULAR SUBTOTAL
def calcular_subtotal(precio, cantidad):

    try:
        precio = float(precio)
        cantidad = int(cantidad)

        if precio < 0 or cantidad < 0:
            return 0

        subtotal = precio * cantidad

        return subtotal

    except (ValueError, TypeError):
        return 0


# 5. CALCULAR DESCUENTO
def calcular_descuento(subtotal, porcentaje):

    try:
        subtotal = float(subtotal)
        porcentaje = float(porcentaje)

        if subtotal < 0 or porcentaje < 0 or porcentaje > 100:
            return 0

        descuento = subtotal * porcentaje / 100

        return descuento

    except (ValueError, TypeError):
        return 0


# 6. CALCULAR IMPUESTO
def calcular_impuesto(subtotal, porcentaje):

    try:
        subtotal = float(subtotal)
        porcentaje = float(porcentaje)

        if subtotal < 0 or porcentaje < 0:
            return 0

        impuesto = subtotal * porcentaje / 100

        return impuesto

    except (ValueError, TypeError):
        return 0


# 7. CALCULAR TOTAL DE UNA VENTA
def calcular_total(subtotal, descuento, impuesto):

    total = subtotal - descuento + impuesto

    if total < 0:
        return 0

    return total


# 8. GENERAR CODIGO AUTOMATICO
def generar_codigo(prefijo, numero):

    codigo = prefijo + str(numero).zfill(4)

    return codigo


# 9. BUSCAR PRODUCTO POR NOMBRE
def buscar_por_nombre(productos, nombre):

    encontrados = {}

    nombre = nombre.strip().lower()

    for codigo, datos in productos.items():

        if nombre in datos["nombre"].lower():
            encontrados[codigo] = datos.copy()

    return encontrados


# 10. CONTAR PRODUCTOS ACTIVOS
def contar_productos(productos):

    cantidad = 0

    for codigo, datos in productos.items():

        if datos.get("activo", True):
            cantidad += 1

    return cantidad

