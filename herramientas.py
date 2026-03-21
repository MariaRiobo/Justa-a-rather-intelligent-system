import datetime
import requests
import pytz
import wikipedia
import PyPDF2
import io

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
    """Retorna la fecha y hora exacta, calculando el día en español para evitar alucinaciones de la IA."""
    try:
        # Consultamos la hora atómica mundial
        url = "http://worldtimeapi.org/api/timezone/America/Argentina/Buenos_Aires"
        res = requests.get(url, timeout=5)
        
        if res.status_code == 200:
            datos = res.json()
            fecha_hora_iso = datos["datetime"]
            # Extraemos el objeto de tiempo exacto
            dt = datetime.datetime.strptime(fecha_hora_iso[:19], "%Y-%m-%dT%H:%M:%S")
        else:
            raise Exception("Fallo API")
            
    except Exception:
        # Plan B (Respaldo local) por si el servidor externo no responde
        import pytz
        zona = pytz.timezone("America/Argentina/Buenos_Aires")
        dt = datetime.datetime.now(zona)

    # Diccionarios blindados en español (Para que el servidor en inglés no afecte)
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    nombre_dia = dias[dt.weekday()]
    nombre_mes = meses[dt.month - 1]

    # Le damos la información a la IA tan clara que es imposible que se equivoque
    reporte_temporal = f"Hoy es {nombre_dia}, {dt.day} de {nombre_mes} de {dt.year}. La hora atómica exacta es {dt.strftime('%H:%M:%S')}."
    
    return reporte_temporal
    
def obtener_clima(ciudad="Buenos Aires"):
    """Consulta el clima actual y el pronóstico de 7 días por satélite."""
    try:
        # 1. Buscamos las coordenadas exactas de la ciudad
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad}&count=1&language=es"
        geo_res = requests.get(geo_url, timeout=5).json()
        
        if not geo_res.get("results"):
            return f"No se encontraron coordenadas en el mapa para {ciudad}."
            
        lat = geo_res["results"][0]["latitude"]
        lon = geo_res["results"][0]["longitude"]
        nombre_oficial = geo_res["results"][0]["name"]
        
        # 2. Descargamos el reporte de los próximos 7 días
        clima_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
        clima_res = requests.get(clima_url, timeout=5).json()
        
        actual_temp = clima_res["current"]["temperature_2m"]
        
        # 3. Armamos el reporte táctico para que la IA lo lea
        reporte = f"REPORTE CLIMÁTICO GLOBAL PARA {nombre_oficial.upper()}:\n"
        reporte += f"[AHORA] Temperatura actual: {actual_temp}°C\n\n"
        reporte += "[PRONÓSTICO 7 DÍAS]:\n"
        
        fechas = clima_res["daily"]["time"]
        max_t = clima_res["daily"]["temperature_2m_max"]
        min_t = clima_res["daily"]["temperature_2m_min"]
        prob_lluvia = clima_res["daily"]["precipitation_probability_max"]
        
        for i in range(len(fechas)):
            reporte += f"- {fechas[i]}: Mín {min_t[i]}°C | Máx {max_t[i]}°C | Prob. Lluvia: {prob_lluvia[i]}%\n"
            
        return reporte
    except Exception as e:
        return "Error de conexión con el satélite Climático"


        
def buscar_en_wikipedia(consulta):
    """Consulta la base de datos histórica."""
    try:
        return f"Archivo Wikipedia: {wikipedia.summary(consulta, sentences=2)}"
    except:
        return f"No hay registros históricos sobre '{consulta}'."

def extraer_texto(archivo):
    """Extrae el texto de archivos PDF o TXT subidos a través de Streamlit."""
    try:
        nombre = archivo.name.lower()
        
        # Si es un archivo de texto plano
        if nombre.endswith('.txt'):
            return archivo.getvalue().decode("utf-8")
        
        # Si es un PDF
        elif nombre.endswith('.pdf'):
            lector = PyPDF2.PdfReader(io.BytesIO(archivo.getvalue()))
            texto = ""
            for pagina in lector.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto += texto_pagina + "\n"
            return texto
            
        else:
            return "Error: Formato de archivo no soportado. Usa PDF o TXT."
            
    except Exception as e:
        return f"Error en el escáner de documentos: {str(e)}"
