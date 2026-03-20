import datetime
import requests
from zoneinfo import ZoneInfo
import wikipedia
from duckduckgo_search import DDGS

# Configuración básica
wikipedia.set_lang("es")

def obtener_fecha_hora():
    """Retorna la fecha y hora actual en Buenos Aires."""
    zona = ZoneInfo("America/Argentina/Buenos_Aires")
    ahora = datetime.datetime.now(zona)
    return ahora.strftime("%A, %d de %B de %Y, %H:%M:%S")

def obtener_clima(ciudad="Buenos Aires"):
    """Consulta el clima actual por satélite."""
    try:
        ciudad_f = ciudad.replace(" ", "+")
        url = f"https://wttr.in/{ciudad_f}?format=%C+%t"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return f"Clima en {ciudad}: {res.text.strip()}"
        return "Sensores meteorológicos fuera de línea."
    except:
        return "Error de conexión con el satélite climático."

def buscar_en_internet(consulta):
    """Rastreo de red con protocolos de redundancia."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            # Intento 1: Búsqueda específica de resultados
            query_primaria = f"{consulta} ultimo resultado partido"
            resultados = list(ddgs.text(query_primaria, region="ar-es", max_results=3))
            
            # Intento 2: Si el primero falla, buscamos en noticias generales
            if not resultados:
                query_secundaria = f"noticias {consulta} hoy"
                resultados = list(ddgs.text(query_secundaria, region="ar-es", max_results=3))

            if resultados:
                reporte = f"REPORTES DE RED PARA '{consulta}':\n"
                for r in resultados:
                    # Limpiamos el texto para que la IA lo entienda mejor
                    reporte += f"- TITULAR: {r['title']}\n  INFO: {r['body']}\n\n"
                return reporte
            
            return "Error: No se detectaron transmisiones ni datos recientes en la red superficial."
    except Exception as e:
        return f"Fallo en el módulo de búsqueda: {str(e)}"

def buscar_en_wikipedia(consulta):
    """Consulta la base de datos histórica."""
    try:
        return f"Archivo Wikipedia: {wikipedia.summary(consulta, sentences=2)}"
    except:
        return f"No hay registros históricos sobre '{consulta}'."
