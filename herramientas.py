import datetime
import requests
from zoneinfo import ZoneInfo # <--- El nuevo módulo para zonas horarias

def obtener_fecha_hora():
    """Devuelve la fecha y hora actual exacta en la base de operaciones."""
    # Aquí le decimos que tu base está en Buenos Aires (Cámbialo si estás en otro país)
    zona_horaria = ZoneInfo("America/Argentina/Buenos_Aires") 
    ahora = datetime.datetime.now(zona_horaria)
    return ahora.strftime("%A, %d de %B de %Y, %H:%M:%S")

def obtener_clima(ciudad="Buenos Aires"):
# ... (El resto del archivo queda igual hacia abajo) ...

def obtener_clima(ciudad="Buenos Aires"):
    """Se conecta a la red para obtener el clima actual de una ciudad."""
    try:
        # Satélite meteorológico de acceso libre
        url = f"https://wttr.in/{ciudad}?format=%C+%t"
        response = requests.get(url)
        if response.status_code == 200:
            return f"El clima en {ciudad} es: {response.text}"
        return "Los sensores meteorológicos no responden."
    except:
        return "Error de conexión con el satélite."

# Aquí le explicamos a E.D.I.T.H. qué herramientas tiene y cómo usarlas
mis_herramientas = [
    {
        "type": "function",
        "function": {
            "name": "obtener_fecha_hora",
            "description": "Obtiene la fecha y la hora actual del sistema en tiempo real. Úsalo si el usuario pregunta qué hora es, qué día es hoy, etc.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_clima",
            "description": "Busca el clima y temperatura actual de una ciudad en internet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {
                        "type": "string",
                        "description": "El nombre de la ciudad solicitada, por ejemplo 'Buenos Aires', 'Madrid'"
                    }
                },
                "required": ["ciudad"]
            }
        }
    }
]
