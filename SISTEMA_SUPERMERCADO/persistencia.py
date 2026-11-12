"""
persistencia.py
Único módulo que lee y escribe los archivos JSON.

Funciones (2):
    cargar_datos(nombre_archivo, por_defecto)  -> datos cargados
    guardar_datos(nombre_archivo, datos)       -> True si se guardó, False si falló
"""

import json
import os
import shutil
import tempfile

# Los archivos JSON viven en la misma carpeta que este programa,
# sin importar desde dónde se ejecute (VS Code, terminal, etc.).
CARPETA_DATOS = os.path.dirname(os.path.abspath(__file__))

# Mensajes que la interfaz muestra al usuario (JSON dañado, error al guardar...).
ADVERTENCIAS = []


def cargar_datos(nombre_archivo, por_defecto):
    """Lee un archivo JSON y devuelve su contenido.

    Si el archivo no existe, está vacío o está dañado, no se cierra el programa:
    se devuelve una copia de `por_defecto` (datos vacíos) y se guarda una advertencia.
    """
    ruta = os.path.join(CARPETA_DATOS, nombre_archivo)
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        # El tipo debe coincidir con el esperado (diccionario o lista).
        if not isinstance(datos, type(por_defecto)):
            raise ValueError("estructura inesperada")
        return datos
    except FileNotFoundError:
        ADVERTENCIAS.append(f"{nombre_archivo} no existe; se inició vacío.")
    except (json.JSONDecodeError, ValueError, OSError):
        ADVERTENCIAS.append(f"No se pudo leer {nombre_archivo}; se inició vacío.")
        # Se conserva el archivo dañado para que no se pierda por completo.
        try:
            shutil.copyfile(ruta, ruta + ".danado")
        except OSError:
            pass
    return json.loads(json.dumps(por_defecto))  # copia independiente


def guardar_datos(nombre_archivo, datos):
    """Guarda `datos` en JSON de forma segura.

    Primero escribe en un archivo temporal y solo si todo salió bien lo
    reemplaza con os.replace(). Si algo falla, el archivo anterior queda intacto.
    """
    ruta = os.path.join(CARPETA_DATOS, nombre_archivo)
    ruta_temporal = None
    try:
        descriptor, ruta_temporal = tempfile.mkstemp(
            dir=CARPETA_DATOS, prefix=nombre_archivo + ".", suffix=".tmp"
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
            archivo.flush()
            os.fsync(archivo.fileno())
        os.replace(ruta_temporal, ruta)
        ruta_temporal = None
        return True
    except (OSError, TypeError, ValueError):
        ADVERTENCIAS.append(f"No se guardó {nombre_archivo}; datos anteriores intactos.")
        return False
    finally:
        # Si quedó un temporal sin reemplazar, se elimina.
        if ruta_temporal is not None and os.path.exists(ruta_temporal):
            try:
                os.remove(ruta_temporal)
            except OSError:
                pass
