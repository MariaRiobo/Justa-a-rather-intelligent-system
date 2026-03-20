# herramientas.py
import datetime
import requests
from zoneinfo import ZoneInfo

def obtener_fecha_hora():
    """Devuelve la fecha y hora actual exacta."""
    zona_horaria = ZoneInfo("America/Argentina/Buenos_Aires") 
    ahora = datetime.datetime.now(zona_horaria)
    return ahora.strftime("%A, %d de %B de %Y, %H:%M:%S")

def obtener_clima(ciudad="Buenos Aires"):
    """Se conecta a la red para obtener el clima actual de una ciudad."""
    try:
        # El satélite requiere que los espacios sean signos "+"
        ciudad_formateada = ciudad.replace(" ", "+")
        
        url = f"https://wttr.in/{ciudad_formateada}?format=%C+%t"
        response = requests.get(url, timeout=5) # Le damos 5 segundos máximo
        
        if response.status_code == 200:
            return f"El clima en {ciudad} es: {response.text}"
        return f"Los sensores fallaron. Código de error del satélite: {response.status_code}"
    except Exception as e:
        return f"Error de conexión con el satélite: {e}"
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
