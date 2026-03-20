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
    """Rastreo rápido de la red global."""
    try:
        with DDGS() as ddgs:
            # Buscamos noticias y resultados recientes
            resultados = [r for r in ddgs.text(f"{consulta} actualidad", region="ar-es", max_results=3)]
            if not resultados:
                return "No se encontraron transmisiones recientes sobre ese tema."
            
            reporte = ""
            for r in resultados:
                reporte += f"- {r['title']}: {r['body']}\n"
            return reporte
    except Exception as e:
        return f"Interferencia en la red de búsqueda: {str(e)}"

def buscar_en_wikipedia(consulta):
    """Consulta la base de datos histórica."""
    try:
        return f"Archivo Wikipedia: {wikipedia.summary(consulta, sentences=2)}"
    except:
        return f"No hay registros históricos sobre '{consulta}'."
