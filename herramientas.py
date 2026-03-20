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
    """Rastreo usando Google News (sin API) para evitar bloqueos."""
    try:
        # Simulamos un navegador real para que no nos bloqueen
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Buscamos en Google News que es más rápido para resultados deportivos
        url = f"https://www.google.com/search?q={consulta.replace(' ', '+')}+resultado+reciente&tbm=nws"
        
        respuesta = requests.get(url, headers=headers, timeout=10)
        if respuesta.status_code != 200:
            return "Error: Los servidores de búsqueda no responden (Bloqueo de IP)."

        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # Extraemos los títulos y fragmentos de las noticias
        articulos = soup.find_all('div', {'class': 'n0vP9d'}) # Clase común en Google News
        
        if not articulos:
            # Intento genérico si el de noticias falla
            url_gen = f"https://www.google.com/search?q={consulta.replace(' ', '+')}+resultado"
            respuesta = requests.get(url_gen, headers=headers, timeout=10)
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            resumen = soup.find('div', {'class': 'VwiC3b'}) # Clase de descripción de Google
            return f"Resumen detectado: {resumen.text}" if resumen else "No se hallaron datos legibles."

        reporte = "ÚLTIMOS REPORTES ENCONTRADOS:\n"
        for i, art in enumerate(articulos[:3]): # Tomamos los 3 primeros
            reporte += f"- {art.text}\n"
            
        return reporte

    except Exception as e:
        return f"Fallo en el escaneo de red: {str(e)}"

def buscar_en_wikipedia(consulta):
    """Consulta la base de datos histórica."""
    try:
        return f"Archivo Wikipedia: {wikipedia.summary(consulta, sentences=2)}"
    except:
        return f"No hay registros históricos sobre '{consulta}'."
