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
    """Buscador táctico de bajo consumo (Sin API, sin límites)."""
    try:
        # Usamos la versión 'html' de DuckDuckGo que es más fácil de raspar
        url = f"https://html.duckduckgo.com/html/?q={consulta.replace(' ', '+')}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9"
        }

        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return "Error: Interferencia en la señal de red (Bloqueo de servidor)."

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscamos los resultados orgánicos
        resultados = soup.find_all('div', class_='result__body')
        
        if not resultados:
            return "No se detectaron transmisiones claras. Intente reformular, señor."

        reporte = "DATOS RECUPERADOS DE LA RED:\n"
        # Tomamos los 4 primeros resultados para no saturar a la IA
        for i, res in enumerate(resultados[:4]):
            titulo = res.find('a', class_='result__a').text
            snippet = res.find('a', class_='result__snippet').text
            reporte += f"- {titulo}: {snippet}\n\n"
            
        return reporte

    except Exception as e:
        return f"Fallo en el escáner: {str(e)}"

def buscar_en_wikipedia(consulta):
    """Consulta la base de datos histórica."""
    try:
        return f"Archivo Wikipedia: {wikipedia.summary(consulta, sentences=2)}"
    except:
        return f"No hay registros históricos sobre '{consulta}'."
