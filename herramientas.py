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
    """Rastreo de emergencia usando un motor alternativo si DuckDuckGo falla."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            # Quitamos 'actualidad' y dejamos que el motor decida, pero forzamos tiempo reciente
            resultados = list(ddgs.text(f"{consulta} resultado hoy", region="ar-es", max_results=5))
            
            if not resultados:
                # Intento 2: Búsqueda más amplia
                resultados = list(ddgs.text(f"último partido de {consulta}", region="ar-es", max_results=3))

            if resultados:
                reporte = f"DATOS ENCONTRADOS PARA {consulta.upper()}:\n"
                for r in resultados:
                    reporte += f"- {r['title']}: {r['body']}\n"
                return reporte
            
        return "No se encontraron datos en la red. Intenta reformular la búsqueda, señor."
    except Exception as e:
        # Si falla la librería, intentamos un raspado manual básico (Plan C)
        return f"Error de conexión en el rastreador: {str(e)}"

def buscar_en_wikipedia(consulta):
    """Consulta la base de datos histórica."""
    try:
        return f"Archivo Wikipedia: {wikipedia.summary(consulta, sentences=2)}"
    except:
        return f"No hay registros históricos sobre '{consulta}'."
