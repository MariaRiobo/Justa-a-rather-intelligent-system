import datetime
import requests
import pytz
import wikipedia
from bs4 import BeautifulSoup

# Configuración básica
wikipedia.set_lang("es")

def obtener_cotizacion_dolar():
    """Consulta las cotizaciones exactas del dólar en Argentina."""
    try:
        # Usamos una API especializada en el peso argentino
        url = "https://dolarapi.com/v1/dolares"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            datos = res.json()
            reporte = "COTIZACIONES TÁCTICAS (USD/ARS):\n"
            for d in datos:
                # Solo tomamos los más importantes para no marear a la IA
                if d['casa'] in ['oficial', 'blue', 'mep']:
                    reporte += f"- Dólar {d['casa'].capitalize()}: Compra ${d['compra']} | Venta ${d['venta']}\n"
            return reporte
        return "Error: Los mercados financieros están cerrados o inaccesibles."
    except:
        return "Error de conexión con el sensor de divisas."

def obtener_fecha_hora():
    """Retorna la fecha y hora exacta consultando un reloj atómico externo."""
    try:
        # Consultamos la hora exacta a un servidor mundial independiente
        url = "http://worldtimeapi.org/api/timezone/America/Argentina/Buenos_Aires"
        res = requests.get(url, timeout=5)
        
        if res.status_code == 200:
            datos = res.json()
            # La API nos devuelve un formato ISO, lo acomodamos
            fecha_hora_iso = datos["datetime"]
            # Cortamos los microsegundos para que quede limpio: YYYY-MM-DDTHH:MM:SS
            fecha_hora_limpia = fecha_hora_iso.split(".")[0].replace("T", " ")
            return fecha_hora_limpia
        else:
            # Plan B (Respaldo): Si el servidor externo cae, usamos pytz
            import pytz
            zona = pytz.timezone("America/Argentina/Buenos_Aires")
            ahora = datetime.datetime.now(zona)
            return ahora.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return f"Error en el enlace temporal: {str(e)}"
        

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
