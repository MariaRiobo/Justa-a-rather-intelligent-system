from youtube_transcript_api import YouTubeTranscriptApi
import re

def extraer_id_youtube(url):
    patron = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(patron, url)
    return match.group(1) if match else None

def obtener_transcripcion(url):
    video_id = extraer_id_youtube(url)
    
    if not video_id:
        return "ERROR_INTERNO: No se pudo detectar el ID exacto del video."
        
    try:
        # Método clásico a prueba de versiones antiguas (busca en español o inglés)
        transcripcion = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en', 'es-419'])
        
        texto_completo = " ".join([fragmento['text'] for fragmento in transcripcion])
        return texto_completo
        
    except Exception as e:
        return f"ERROR_INTERNO: Video sin subtítulos o bloqueado. Detalle: {e}"
