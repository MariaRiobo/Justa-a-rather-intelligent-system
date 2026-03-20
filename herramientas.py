import datetime
import requests
from zoneinfo import ZoneInfo
import wikipedia
from duckduckgo_search import DDGS # <--- El nuevo motor de búsqueda

wikipedia.set_lang("es")

def obtener_fecha_hora():
    zona_horaria = ZoneInfo("America/Argentina/Buenos_Aires") 
    ahora = datetime.datetime.now(zona_horaria)
    return ahora.strftime("%A, %d de %B de %Y, %H:%M:%S")

def obtener_clima(ciudad="Buenos Aires"):
    try:
        ciudad_formateada = ciudad.replace(" ", "+")
        url = f"https://wttr.in/{ciudad_formateada}?format=%C+%t"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        return f"El clima en {ciudad} es: {response.text.strip()}" if response.status_code == 200 else "Error en satélite."
    except:
        return "Fallo de conexión meteorológica."

def buscar_en_wikipedia(consulta):
    try:
        resumen = wikipedia.summary(consulta, sentences=2)
        return f"Según mis registros sobre '{consulta}': {resumen}"
    except:
        return f"No encontré datos específicos en Wikipedia sobre '{consulta}'."

def buscar_en_internet(consulta):
    """Busca en tiempo real cualquier información en la web global."""
    try:
        with DDGS() as ddgs:
            # Buscamos los 3 mejores resultados
            resultados = [r for r in ddgs.text(consulta, max_results=3)]
            if not resultados:
                return "No encontré resultados recientes en la red."
            
            # Construimos un reporte corto
            reporte = f"Resultados de mi escaneo sobre '{consulta}':\n"
            for r in resultados:
                reporte += f"- {r['body'][:200]}...\n"
            return reporte
    except Exception as e:
        return f"Error en el escaneo de red: {str(e)}"

mis_herramientas = [
    {"type": "function", "function": {"name": "obtener_fecha_hora", "description": "Obtiene la fecha y hora actual.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "obtener_clima", "description": "Busca el clima de una ciudad.", "parameters": {"type": "object", "properties": {"ciudad": {"type": "string"}}, "required": ["ciudad"]}}},
    {"type": "function", "function": {"name": "buscar_en_wikipedia", "description": "Información histórica o enciclopédica.", "parameters": {"type": "object", "properties": {"consulta": {"type": "string"}}, "required": ["consulta"]}}},
    {
        "type": "function",
        "function": {
            "name": "buscar_en_internet",
            "description": "Busca noticias actuales, deportes o cualquier dato de último minuto en internet.",
            "parameters": {
                "type": "object",
                "properties": {"consulta": {"type": "string", "description": "La búsqueda a realizar"}},
                "required": ["consulta"]
            }
        }
    }
]
