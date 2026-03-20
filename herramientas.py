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
    """Busca en tiempo real con un motor de búsqueda más agresivo."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            # Forzamos la búsqueda en una región específica (Argentina) para mayor precisión
            resultados = [r for r in ddgs.text(f"{consulta} actualidad resultados", region="ar-es", max_results=5)]
            
            if not resultados:
                return "Escaneo fallido: No hay datos recientes en la red superficial."
            
            # Consolidamos un reporte más robusto
            reporte = f"REPORTE TÁCTICO SOBRE: {consulta}\n"
            for i, r in enumerate(resultados, 1):
                reporte += f"Fuentes {i}: {r['title']} - {r['body']}\n"
            
            return reporte
    except Exception as e:
        return f"Error en los servidores de búsqueda: {str(e)}"
        
mis_herramientas = [
    {"type": "function", "function": {"name": "obtener_fecha_hora", "description": "Obtiene la fecha y hora actual.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "obtener_clima", "description": "Busca el clima de una ciudad.", "parameters": {"type": "object", "properties": {"ciudad": {"type": "string"}}, "required": ["ciudad"]}}},
    {"type": "function", "function": {"name": "buscar_en_wikipedia", "description": "Información histórica o enciclopédica.", "parameters": {"type": "object", "properties": {"consulta": {"type": "string"}}, "required": ["consulta"]}}},
    {
        "type": "function",
        "function": {
            "name": "google", # <--- Le cambiamos el nombre a algo más simple
            "description": "ACCESO TOTAL A INTERNET. Úsalo para noticias, deportes y datos de hoy.",
            "parameters": {
                "type": "object",
                "properties": {"consulta": {"type": "string"}},
                "required": ["consulta"]
            }
        }
    }
]
