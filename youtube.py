import re
import requests
import html

def extraer_id_youtube(url):
    """Extrae el ID del video de cualquier tipo de link."""
    patron = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(patron, url)
    return match.group(1) if match else None

def obtener_transcripcion(url):
    video_id = extraer_id_youtube(url)
    
    if not video_id:
        return "ERROR_INTERNO: No se pudo detectar el ID exacto del video."
        
    try:
        # 🛰️ PROTOCOLO DE EVASIÓN: Nos conectamos al servidor puente
        enlace_puente = f"https://youtubetranscript.com/?server_vid2={video_id}"
        
        # Hacemos la petición fingiendo ser un navegador normal para mayor seguridad
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        respuesta = requests.get(enlace_puente, headers=headers)
        
        if respuesta.status_code != 200:
            return "ERROR_INTERNO: El servidor puente no responde."
            
        contenido = respuesta.text
        
        # Verificamos si el puente nos devolvió un error de YouTube
        if "error" in contenido.lower() and "<text" not in contenido:
            return "ERROR_INTERNO: El video no tiene subtítulos o están fuertemente bloqueados."
            
        # Extraemos solo el texto limpio de las etiquetas XML que nos devuelve el puente
        etiquetas_texto = re.findall(r'<text[^>]*>(.*?)</text>', contenido)
        
        if not etiquetas_texto:
            return "ERROR_INTERNO: El servidor puente no encontró texto."
            
        # Limpiamos códigos raros de HTML (como &quot; o &amp;)
        texto_completo = " ".join([html.unescape(fragmento) for fragmento in etiquetas_texto])
        
        return texto_completo
        
    except Exception as e:
        return f"ERROR_INTERNO: Fallo en el satélite puente. Detalle: {e}"
