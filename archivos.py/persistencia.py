

import json
import os


# ==========================================
# MODULO DE PERSISTENCIA
# SISTEMA DE GESTION DE SUPERMERCADO
# ==========================================


# 1. CARGAR DATOS DESDE UN ARCHIVO JSON
def cargar_datos(nombre_archivo, datos_iniciales):

    try:

        # Verificar si el archivo existe
        if not os.path.exists(nombre_archivo):

            print("El archivo no existe. Se iniciaran datos vacios.")

            # Crear el archivo con los datos iniciales
            guardar_datos(nombre_archivo, datos_iniciales)

            return datos_iniciales

        # Abrir y leer el archivo
        with open(nombre_archivo, "r", encoding="utf-8") as archivo:

            datos = json.load(archivo)

        print("Datos cargados correctamente desde", nombre_archivo)

        return datos

    except json.JSONDecodeError:

        print("Error: el archivo JSON esta dañado.")

        return datos_iniciales

    except OSError as error:

        print("No se pudo leer el archivo:", error)

        return datos_iniciales


# ==========================================
# 2. GUARDAR DATOS EN UN ARCHIVO JSON
# ==========================================

def guardar_datos(nombre_archivo, datos):

    # Nombre del archivo temporal
    archivo_temporal = nombre_archivo + ".tmp"

    try:

        # Guardar primero la informacion en el archivo temporal
        with open(archivo_temporal, "w", encoding="utf-8") as archivo:

            json.dump(
                datos,
                archivo,
                indent=4,
                ensure_ascii=False
            )

        # Reemplazar el archivo anterior por el nuevo
        os.replace(archivo_temporal, nombre_archivo)

        print("Datos guardados correctamente en", nombre_archivo)

        return True

    except (OSError, TypeError, ValueError) as error:

        print("Error al guardar los datos:", error)

        return False

    finally:

        # Eliminar el archivo temporal si todavia existe
        if os.path.exists(archivo_temporal):

            try:

                os.remove(archivo_temporal)

            except OSError:

                print("No se pudo eliminar el archivo temporal.")
