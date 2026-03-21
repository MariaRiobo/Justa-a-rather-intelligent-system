import re
import requests

def extraer_id_youtube(url):
    """Extrae el ID del video de cualquier link de YouTube."""
    patron = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(patron, url)
    return match.group(1) if match else None

def obtener_transcripcion(url):
    video_id = extraer_id_youtube(url)
    
    if not video_id:
        return "ERROR_INTERNO: No se pudo detectar el ID exacto del video."
        
    try:
        # 🛰️ PLAN C: Conexión directa a la API REST gratuita de TubeText
        api_url = f"https://tubetext.vercel.app/youtube/transcript?video_id={video_id}"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        respuesta = requests.get(api_url, headers=headers)
        
        if respuesta.status_code != 200:
            return f"ERROR_INTERNO: La API satelital no responde (Código {respuesta.status_code})."
            
        datos = respuesta.json()
        
        # Validamos estrictamente si la API nos devolvió éxito (nada de falsos positivos)
        if not datos.get("success"):
            return "ERROR_INTERNO: La API satelital no pudo extraer los subtítulos de este video."
            
        data_block = datos.get("data", {})
        
        # Intentamos obtener el texto unificado
        texto_completo = data_block.get("full_text")
        
        # Si el texto unificado no viene, lo ensamblamos desde los fragmentos
        if not texto_completo:
            fragmentos = data_block.get("transcript", [])
            if isinstance(fragmentos, list):
                # Unimos todos los pedazos de texto en un solo párrafo
                texto_completo = " ".join(str(f) for f in fragmentos)
        
        if not texto_completo:
            return "ERROR_INTERNO: La API satelital devolvió un archivo vacío."
            
        return texto_completo
        
    except Exception as e:
        return f"ERROR_INTERNO: Fallo general de conexión. Detalle: {e}"
