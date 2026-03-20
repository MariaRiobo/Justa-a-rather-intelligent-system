import datetime
import requests
from zoneinfo import ZoneInfo
import wikipedia

# Configuramos Wikipedia en español
wikipedia.set_lang("es")

def obtener_fecha_hora():
    """Devuelve la fecha y hora actual exacta."""
    zona_horaria = ZoneInfo("America/Argentina/Buenos_Aires") 
    ahora = datetime.datetime.now(zona_horaria)
    return ahora.strftime("%A, %d de %B de %Y, %H:%M:%S")

def obtener_clima(ciudad="Buenos Aires"):
    """Busca el clima actual de una ciudad."""
    try:
        ciudad_formateada = ciudad.replace(" ", "+")
        url = f"https://wttr.in/{ciudad_formateada}?format=%C+%t"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        return f"El clima en {ciudad} es: {response.text.strip()}" if response.status_code == 200 else "Error en satélite."
    except:
        return "Fallo de conexión meteorológica."

def buscar_en_wikipedia(consulta):
    """Busca un resumen de cualquier tema en Wikipedia."""
    try:
        # Buscamos solo el resumen (2 oraciones) para que EDITH no hable media hora
        resumen = wikipedia.summary(consulta, sentences=2)
        return f"Según mis registros sobre '{consulta}': {resumen}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Hay varios resultados para '{consulta}'. ¿Podrías ser más específico?"
    except wikipedia.exceptions.PageError:
        return f"No encontré información sobre '{consulta}' en mis archivos."
    except:
        return "Error al acceder a la base de datos de Wikipedia."

mis_herramientas = [
    {
        "type": "function",
        "function": {
            "name": "obtener_fecha_hora",
            "description": "Obtiene la fecha y hora actual.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_clima",
            "description": "Busca el clima de una ciudad.",
            "parameters": {
                "type": "object",
                "properties": {"ciudad": {"type": "string", "description": "Ciudad, ej: 'Madrid'"}},
                "required": ["ciudad"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_en_wikipedia",
            "description": "Busca información general sobre personas, lugares, historia o conceptos.",
            "parameters": {
                "type": "object",
                "properties": {"consulta": {"type": "string", "description": "El tema a buscar"}},
                "required": ["consulta"]
            }
        }
    }
]
