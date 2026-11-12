
# ==========================================
# MODULO DE INVENTARIO
# SISTEMA DE GESTION DE SUPERMERCADO
# ==========================================

import os
from persistencia import cargar_datos, guardar_datos


# Ruta del archivo JSON
RUTA_PRODUCTOS = os.path.join(
    os.path.dirname(__file__),
    "productos.json"
)


# 1. CARGAR PRODUCTOS
def cargar_productos():

    productos = cargar_datos(RUTA_PRODUCTOS, {})

    if not isinstance(productos, dict):
        print("Error: los datos de productos no son validos.")
        return {}

    return productos


# 2. GUARDAR PRODUCTOS
def guardar_productos(productos):

    return guardar_datos(RUTA_PRODUCTOS, productos)


# 3. CONVERTIR Y VALIDAR NUMEROS
def convertir_entero(valor):

    numero = int(valor)

    if numero < 0:
        raise ValueError("El numero no puede ser negativo")

    return numero


# 4. REGISTRAR PRODUCTO
def registrar_producto(productos, codigo, nombre, categoria,
                       precio_compra, precio_venta, stock, stock_minimo):

    try:
        codigo = codigo.strip().upper()
        nombre = nombre.strip()
        categoria = categoria.strip()

        if codigo == "" or nombre == "" or categoria == "":
            return False, "Todos los campos son obligatorios"

        if codigo in productos:
            return False, "El codigo del producto ya existe"

        precio_compra = convertir_entero(precio_compra)
        precio_venta = convertir_entero(precio_venta)
        stock = convertir_entero(stock)
        stock_minimo = convertir_entero(stock_minimo)

        productos[codigo] = {
            "nombre": nombre,
            "categoria": categoria,
            "precio_compra": precio_compra,
            "precio_venta": precio_venta,
            "stock": stock,
            "stock_minimo": stock_minimo,
            "activo": True
        }

        if not guardar_productos(productos):
            return True, "Producto registrado, pero no se pudo guardar en JSON"

        return True, "Producto registrado correctamente"

    except (ValueError, TypeError, AttributeError):
        return False, "Ingrese valores numericos enteros y no negativos"


# 5. EDITAR PRODUCTO
def editar_producto(productos, codigo, datos):

    try:
        codigo = codigo.strip().upper()

        if codigo not in productos:
            return False, "El producto no existe"

        campos_permitidos = [
            "nombre", "categoria",
            "precio_compra", "precio_venta",
            "stock", "stock_minimo"
        ]

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

        if not guardar_productos(productos):
            return True, "Producto actualizado, pero no se pudo guardar en JSON"

        return True, "Producto actualizado correctamente"

    except (ValueError, TypeError, AttributeError):
        return False, "Ingrese datos validos para actualizar el producto"


# 6. BUSCAR PRODUCTO
def buscar_producto(productos, codigo):

    codigo = codigo.strip().upper()

    if codigo in productos:
        return productos[codigo]

    return None


# 7. DESACTIVAR PRODUCTO
def desactivar_producto(productos, codigo):

    codigo = codigo.strip().upper()

    if codigo not in productos:
        return False, "El producto no existe"

    if not productos[codigo].get("activo", True):
        return False, "El producto ya esta desactivado"

    productos[codigo]["activo"] = False

    if not guardar_productos(productos):
        return True, "Producto desactivado, pero no se pudo guardar en JSON"

    return True, "Producto desactivado correctamente"


# 8. CONSULTAR INVENTARIO
def consultar_inventario(productos):

    inventario = {}

    for codigo, datos in productos.items():

        if datos.get("activo", True):
            inventario[codigo] = datos.copy()

    return inventario


# 9. REGISTRAR ENTRADA DE PRODUCTOS
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

        if not guardar_productos(productos):
            return True, "Entrada registrada, pero no se pudo guardar en JSON"

        return True, "Entrada registrada correctamente"

    except (ValueError, TypeError, AttributeError):
        return False, "Ingrese una cantidad numerica valida"


# 10. REGISTRAR SALIDA DE PRODUCTOS
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

        if not guardar_productos(productos):
            return True, "Salida registrada, pero no se pudo guardar en JSON"

        return True, "Salida registrada correctamente"

    except (ValueError, TypeError, AttributeError):
        return False, "Ingrese una cantidad numerica valida"


# 11. VERIFICAR PRODUCTOS CON STOCK BAJO
def verificar_stock(productos):

    productos_bajos = {}

    for codigo, datos in productos.items():

        if datos.get("activo", True):

            if datos["stock"] <= datos["stock_minimo"]:
                productos_bajos[codigo] = datos.copy()

    return productos_bajos

