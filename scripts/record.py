import json
import os

ARCHIVO_RECORDS = "scripts/records.json"

#Cargamos los records existentes desde el archivo
def cargar_records():
    if os.path.exists(ARCHIVO_RECORDS):
        with open(ARCHIVO_RECORDS, "r") as f:
            return json.load(f)
    return []  #Si no existe se crea una lista vacia

#Guardar la lista de records en el archivo
def guardar_records(records):
    with open(ARCHIVO_RECORDS, "w") as f:
        json.dump(records, f, indent=4)

#Se añade el record si es mayor a alguno en el top
def agregar_record(nombre, puntos):
    records = cargar_records()
    
    # Agregar nuevo record
    records.append({"nombre": nombre, "puntos": puntos})
    
    #Ordenamos los records de mayor a menor
    records.sort(key=lambda r: r["puntos"], reverse=True)

    #Solo tomamos los 5 primeros y los guardamos
    records = records[:5]
    
    guardar_records(records)

#Pedimos los 5 records
def obtener_top5():
    records = cargar_records()
    return sorted(records, key=lambda r: r["puntos"], reverse=True)[:5]