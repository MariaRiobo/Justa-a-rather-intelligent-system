import json
import os

# Nuestro archivo de disco duro local
ARCHIVO_MEMORIA = "memoria_edith.json"

def cargar_memoria():
    """Lee el disco duro. Si no existe, crea uno en blanco."""
    if os.path.exists(ARCHIVO_MEMORIA):
        with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    else:
        # Estructura inicial del cerebro
        return {"hechos_clave": []}

def guardar_memoria(datos):
    """Escribe los datos en el disco duro para que no se borren al apagar la app."""
    with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

def agregar_recuerdo(nuevo_hecho):
    """Añade un nuevo recuerdo a la base de datos si no existe ya."""
    memoria_actual = cargar_memoria()
    
    if nuevo_hecho not in memoria_actual["hechos_clave"]:
        memoria_actual["hechos_clave"].append(nuevo_hecho)
        guardar_memoria(memoria_actual)
        return True
    return False

def borrar_recuerdo(hecho_a_borrar):
    """Elimina un recuerdo específico."""
    memoria_actual = cargar_memoria()
    
    if hecho_a_borrar in memoria_actual["hechos_clave"]:
        memoria_actual["hechos_clave"].remove(hecho_a_borrar)
        guardar_memoria(memoria_actual)
        return True
    return False

def obtener_contexto_memoria():
    """Empaqueta todos los recuerdos en un texto para inyectarlos en la IA."""
    memoria_actual = cargar_memoria()
    hechos = memoria_actual.get("hechos_clave", [])
    
    if no hechos:
        return ""
        
    texto_memoria = "\n\n--- MEMORIA A LARGO PLAZO DEL USUARIO ---\n"
    texto_memoria += "Ten en cuenta esta información permanentemente en todas tus respuestas:\n"
    for hecho in hechos:
        texto_memoria += f"- {hecho}\n"
        
    return texto_memoria
