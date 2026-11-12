# Sistema de Gestión de Supermercado

Proyecto final de Programación I · Python + Tkinter + JSON

## Cómo ejecutarlo en VS Code

1. Descomprima la carpeta `SISTEMA_SUPERMERCADO` y ábrala en VS Code (*Archivo → Abrir carpeta*).
2. Abra `main.py` y pulse **Run Python File** (▶), o en la terminal: `python main.py`
   (en Linux/Mac: `python3 main.py`).
3. No necesita instalar nada: Tkinter viene con Python.
   (En Ubuntu/Debian, si falta: `sudo apt install python3-tk`.)

Para ver las pruebas documentadas P01 a P15: `python pruebas.py`
(usan una carpeta temporal y **no** modifican sus datos).

## Primer uso

1. **Caja → Abrir caja** (monto inicial). Sin caja abierta no se puede vender.
2. **Ventas**: escriba el código (o doble clic en el catálogo), cantidad y *Agregar*. Escriba con cuánto paga y *Cobrar*.
3. **Inventario**: agregar, editar, buscar, entradas/salidas y desactivar productos. Los productos con stock bajo salen en rojo.
4. **Reportes**: ventas por día, productos más vendidos y gráfico.
5. **Caja → Cerrar caja** muestra el resumen del turno.

## Archivos

| Archivo | Qué hace |
|---|---|
| `main.py` | Inicia el programa |
| `interfaz.py` | Pantallas de Tkinter |
| `funciones.py` | Utilidades compartidas y reglas del negocio (IVA, descuento) |
| `inventario.py` | 8 funciones de productos e inventario |
| `ventas.py` | 8 funciones de carrito, pago, factura y devoluciones |
| `caja.py` | 4 funciones de caja y reportes |
| `persistencia.py` | `cargar_datos` y `guardar_datos` (guardado seguro con `os.replace`) |
| `productos.json`, `ventas.json`, `caja.json` | Datos |
| `pruebas.py` | Pruebas P01–P15 |

## Reglas del negocio (se cambian en `funciones.py`)

- IVA: 19 % (`TASA_IMPUESTO`)
- Descuento: 5 % en compras con subtotal desde $100.000 (`UMBRAL_DESCUENTO`, `PORCENTAJE_DESCUENTO`)

Para empezar con datos vacíos, borre los tres `.json`: el programa los crea solo.
