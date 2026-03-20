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
    """Se conecta a la red para obtener el clima actual con camuflaje de navegador."""
    try:
        ciudad_formateada = ciudad.replace(" ", "+")
        url = f"https://wttr.in/{ciudad_formateada}?format=%C+%t"
        
        # Le decimos al satélite que somos un navegador real
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Limpiamos espacios raros que a veces manda el satélite
            dato_clima = response.text.strip()
            return f"El clima en {ciudad} es: {dato_clima}"
        
        return f"Error táctico: El satélite respondió con código {response.status_code}."
    except Exception as e:
        return f"Fallo de conexión: {str(e)}"
        
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
