"""
inventario.py
Lógica de productos e inventario (8 funciones).

`productos` es un diccionario:  código -> {nombre, categoria, precio_compra,
precio_venta, stock, stock_minimo, activo}

Las funciones modifican el diccionario recibido y lo devuelven.
Cuando algo no es válido lanzan ValueError con el mensaje para el usuario.
"""

from funciones import (
    normalizar_codigo,
    validar_entero_positivo,
    validar_entero_no_negativo,
    validar_precio,
)


def registrar_producto(productos, codigo, nombre, categoria, precio_compra,
                       precio_venta, stock, stock_minimo):
    """Agrega un producto nuevo. Rechaza códigos duplicados y precios negativos."""
    codigo = normalizar_codigo(codigo)
    if not codigo:
        raise ValueError("Ingrese el código del producto")
    if codigo in productos:
        raise ValueError(f"El código {codigo} ya existe")
    nombre = str(nombre).strip()
    if not nombre:
        raise ValueError("Ingrese el nombre del producto")

    precio_compra = validar_precio(precio_compra)
    precio_venta = validar_precio(precio_venta)
    stock = validar_entero_no_negativo(stock, "El stock debe ser un entero mayor o igual a 0")
    stock_minimo = validar_entero_no_negativo(
        stock_minimo, "El stock mínimo debe ser un entero mayor o igual a 0")

    productos[codigo] = {
        "nombre": nombre,
        "categoria": str(categoria).strip() or "Sin categoría",
        "precio_compra": precio_compra,
        "precio_venta": precio_venta,
        "stock": stock,
        "stock_minimo": stock_minimo,
        "activo": True,
    }
    return productos


def editar_producto(productos, codigo, **cambios):
    """Modifica los datos de un producto existente.

    Campos permitidos: nombre, categoria, precio_compra, precio_venta,
    stock_minimo, activo. (El stock cambia solo con entradas, salidas y ventas.)
    """
    codigo = normalizar_codigo(codigo)
    if codigo not in productos:
        raise ValueError(f"El producto {codigo} no existe")

    nuevo = dict(productos[codigo])  # se trabaja en una copia por si algo falla
    for campo, valor in cambios.items():
        if campo == "nombre":
            valor = str(valor).strip()
            if not valor:
                raise ValueError("Ingrese el nombre del producto")
            nuevo["nombre"] = valor
        elif campo == "categoria":
            nuevo["categoria"] = str(valor).strip() or "Sin categoría"
        elif campo in ("precio_compra", "precio_venta"):
            nuevo[campo] = validar_precio(valor)
        elif campo == "stock_minimo":
            nuevo[campo] = validar_entero_no_negativo(
                valor, "El stock mínimo debe ser un entero mayor o igual a 0")
        elif campo == "activo":
            nuevo["activo"] = bool(valor)
        else:
            raise ValueError(f"No se puede editar el campo {campo}")

    productos[codigo] = nuevo
    return productos


def buscar_producto(productos, texto, incluir_inactivos=False):
    """Busca por código, nombre o categoría. Devuelve una lista de (código, datos)."""
    texto = str(texto).strip().lower()
    resultados = []
    for codigo, datos in productos.items():
        if not incluir_inactivos and not datos.get("activo", True):
            continue
        if (texto in codigo.lower() or texto in datos["nombre"].lower()
                or texto in datos["categoria"].lower()):
            resultados.append((codigo, datos))
    return resultados


def desactivar_producto(productos, codigo):
    """Oculta el producto de las ventas sin borrar su historial."""
    codigo = normalizar_codigo(codigo)
    if codigo not in productos:
        raise ValueError(f"El producto {codigo} no existe")
    productos[codigo]["activo"] = False
    return productos


def consultar_inventario(productos, incluir_inactivos=False):
    """Devuelve la lista ordenada de (código, datos) con el stock actual."""
    lista = []
    for codigo in sorted(productos):  # for: recorre todos los productos
        datos = productos[codigo]
        if datos.get("activo", True) or incluir_inactivos:
            lista.append((codigo, datos))
    return lista


def registrar_entrada(productos, codigo, cantidad):
    """Suma unidades al stock (compra a proveedor, reposición)."""
    codigo = normalizar_codigo(codigo)
    if codigo not in productos:
        raise ValueError(f"El producto {codigo} no existe")
    cantidad = validar_entero_positivo(cantidad)
    productos[codigo]["stock"] += cantidad
    return productos


def registrar_salida(productos, codigo, cantidad):
    """Resta unidades del stock (venta, merma, producto dañado)."""
    codigo = normalizar_codigo(codigo)
    if codigo not in productos:
        raise ValueError(f"El producto {codigo} no existe")
    cantidad = validar_entero_positivo(cantidad)
    verificar_stock(productos, codigo, cantidad, exigir_activo=False)
    productos[codigo]["stock"] -= cantidad
    return productos


def verificar_stock(productos, codigo, cantidad, exigir_activo=True):
    """Comprueba que haya unidades suficientes. Lanza ValueError si no.

    Devuelve True si la cantidad solicitada está disponible.
    """
    codigo = normalizar_codigo(codigo)
    if codigo not in productos:
        raise ValueError(f"El producto {codigo} no existe")
    datos = productos[codigo]
    if exigir_activo and not datos.get("activo", True):
        raise ValueError(f"El producto {codigo} está desactivado")
    if cantidad > datos["stock"]:
        raise ValueError(f"Stock insuficiente: quedan {datos['stock']}")
    return True


def es_stock_bajo(datos):
    """Auxiliar: True si el stock llegó al mínimo o está por debajo (alerta de existencias bajas)."""
    return datos["stock"] <= datos["stock_minimo"]
