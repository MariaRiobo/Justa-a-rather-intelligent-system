import datetime
import requests
from zoneinfo import ZoneInfo
import wikipedia
from bs4 import BeautifulSoup

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
    """Buscador táctico optimizado para resultados en vivo."""
    try:
        # Forzamos a DuckDuckGo a buscar resultados y marcadores específicos
        query = f"{consulta} resultado marcador final hoy"
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "Error: Interferencia en la señal."

        soup = BeautifulSoup(response.text, 'html.parser')
        resultados = soup.find_all('div', class_='result__body')
        
        if not resultados:
            return "No se detectaron marcadores claros en la zona."

        reporte = "DATOS DE CAMPO DETECTADOS:\n"
        # Tomamos los 5 primeros para darle más chances a la IA de encontrar el número
        for res in resultados[:5]:
            titulo = res.find('a', class_='result__a').text
            snippet = res.find('a', class_='result__snippet').text
            reporte += f"FUENTE: {titulo}\nINFO: {snippet}\n\n"
            
        return reporte

    except Exception as e:
        return f"Fallo en el escáner: {str(e)}"
        
def buscar_en_wikipedia(consulta):
    """Consulta la base de datos histórica."""
    try:
        return f"Archivo Wikipedia: {wikipedia.summary(consulta, sentences=2)}"
    except:
        return f"No hay registros históricos sobre '{consulta}'."
