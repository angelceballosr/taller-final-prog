# ==========================================
# MODULO DE INVENTARIO
# SISTEMA DE GESTION DE SUPERMERCADO
# ==========================================


# 1. FUNCION PARA CONVERTIR Y VALIDAR NUMEROS
def convertir_entero(valor):
    numero = int(valor)

    if numero < 0:
        raise ValueError("El numero no puede ser negativo")

    return numero


# 2. REGISTRAR PRODUCTO
def registrar_producto(productos, codigo, nombre, categoria,
                       precio_compra, precio_venta, stock, stock_minimo):

    try:
        codigo = codigo.strip().upper()
        nombre = nombre.strip()
        categoria = categoria.strip()

        # Validar campos vacios
        if codigo == "" or nombre == "" or categoria == "":
            return False, "Todos los campos son obligatorios"

        # Verificar si el codigo ya existe
        if codigo in productos:
            return False, "El codigo del producto ya existe"

        # Convertir los valores numericos
        precio_compra = convertir_entero(precio_compra)
        precio_venta = convertir_entero(precio_venta)
        stock = convertir_entero(stock)
        stock_minimo = convertir_entero(stock_minimo)

        # Guardar el producto en el diccionario
        productos[codigo] = {
            "nombre": nombre,
            "categoria": categoria,
            "precio_compra": precio_compra,
            "precio_venta": precio_venta,
            "stock": stock,
            "stock_minimo": stock_minimo,
            "activo": True
        }

        return True, "Producto registrado correctamente"

    except (ValueError, TypeError):
        return False, "Ingrese valores numericos enteros y no negativos"


# 3. EDITAR PRODUCTO
def editar_producto(productos, codigo, datos):

    codigo = codigo.strip().upper()

    if codigo not in productos:
        return False, "El producto no existe"

    # Campos que se pueden modificar
    campos_permitidos = [
        "nombre", "categoria",
        "precio_compra", "precio_venta",
        "stock", "stock_minimo"
    ]

    try:
        producto = productos[codigo].copy()

        for campo, valor in datos.items():

            if campo not in campos_permitidos:
                return False, "No se puede modificar ese campo"

            if campo in ["nombre", "categoria"]:

                valor = valor.strip()

                if valor == "":
                    return False, "El campo no puede estar vacio"

                producto[campo] = valor

            else:
                producto[campo] = convertir_entero(valor)

        productos[codigo] = producto

        return True, "Producto actualizado correctamente"

    except (ValueError, TypeError, AttributeError):
        return False, "Ingrese datos validos para actualizar el producto"


# 4. BUSCAR PRODUCTO
def buscar_producto(productos, codigo):

    codigo = codigo.strip().upper()

    if codigo in productos:
        return productos[codigo]

    return None


# 5. DESACTIVAR PRODUCTO
def desactivar_producto(productos, codigo):

    codigo = codigo.strip().upper()

    if codigo not in productos:
        return False, "El producto no existe"

    if not productos[codigo].get("activo", True):
        return False, "El producto ya esta desactivado"

    productos[codigo]["activo"] = False

    return True, "Producto desactivado correctamente"


# 6. CONSULTAR INVENTARIO
def consultar_inventario(productos):

    inventario = {}

    for codigo, datos in productos.items():

        if datos.get("activo", True):
            inventario[codigo] = datos.copy()

    return inventario


# 7. REGISTRAR ENTRADA DE PRODUCTOS
def registrar_entrada(productos, codigo, cantidad):

    try:
        codigo = codigo.strip().upper()
        cantidad = convertir_entero(cantidad)

        if codigo not in productos:
            return False, "El producto no existe"

        if not productos[codigo].get("activo", True):
            return False, "El producto esta desactivado"

        if cantidad == 0:
            return False, "La cantidad debe ser mayor que cero"

        productos[codigo]["stock"] += cantidad

        return True, "Entrada registrada correctamente"

    except (ValueError, TypeError):
        return False, "Ingrese una cantidad numerica valida"


# 8. REGISTRAR SALIDA DE PRODUCTOS
def registrar_salida(productos, codigo, cantidad):

    try:
        codigo = codigo.strip().upper()
        cantidad = convertir_entero(cantidad)

        if codigo not in productos:
            return False, "El producto no existe"

        if not productos[codigo].get("activo", True):
            return False, "El producto esta desactivado"

        if cantidad == 0:
            return False, "La cantidad debe ser mayor que cero"

        if cantidad > productos[codigo]["stock"]:
            return False, "No hay suficiente inventario"

        productos[codigo]["stock"] -= cantidad

        return True, "Salida registrada correctamente"

    except (ValueError, TypeError):
        return False, "Ingrese una cantidad numerica valida"


# 9. VERIFICAR PRODUCTOS CON STOCK BAJO
def verificar_stock(productos):

    productos_bajos = {}

    for codigo, datos in productos.items():

        if datos.get("activo", True):

            if datos["stock"] <= datos["stock_minimo"]:
                productos_bajos[codigo] = datos.copy()

    return productos_bajos
