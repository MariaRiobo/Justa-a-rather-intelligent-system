# youtube.py
from youtube_transcript_api import YouTubeTranscriptApi
import re

def extraer_id_youtube(url):
    """Extrae el ID único del video de cualquier tipo de enlace de YouTube."""
    patron = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(patron, url)
    return match.group(1) if match else None

def obtener_transcripcion(url):
    """Descarga los subtítulos del video para que E.D.I.T.H. los lea."""
    video_id = extraer_id_youtube(url)
    
    if not video_id:
        return "Error: Formato de enlace de YouTube no reconocido."
        
    try:
        # Intentamos descargar subtítulos en español o inglés
        transcripcion = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
        
        # Unimos todas las frases en un solo texto gigante
        texto_completo = " ".join([fragmento['text'] for fragmento in transcripcion])
        
        return texto_completo
        
    except Exception as e:
        return f"Error al extraer datos. Es posible que el video no tenga subtítulos automáticos o manuales. Detalle: {e}"
