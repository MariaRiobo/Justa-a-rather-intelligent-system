import requests
from bs4 import BeautifulSoup

def buscar_en_red(consulta):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    # Usamos la versión de búsqueda de Google que devuelve texto plano más fácil de leer
    url = f"https://www.google.com/search?q={consulta.replace(' ', '+')}&hl=es"
    
    try:
        respuesta = requests.get(url, headers=headers, timeout=10)
        if respuesta.status_code != 200:
            return "Error: No pude saltar el firewall del buscador."
            
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        # Buscamos los fragmentos de texto (snippets) de los resultados
        resultados = soup.find_all('div', class_='VwiC3b') 
        
        if not resultados:
            return "No hay datos recientes disponibles en este momento."
        
        # Consolidamos los 3 mejores resultados
        texto_busqueda = "\n".join([r.get_text() for r in resultados[:3]])
        return f"\n--- REPORTE DE INTELIGENCIA (RED EXTERNA) ---\n{texto_busqueda}"
        
    except Exception as e:
        return f"Falla en el sensor de red: {e}"
