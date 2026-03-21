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
        # Obtenemos la lista de todas las pistas disponibles en el video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            # Intentamos buscar español o inglés primero
            transcript = transcript_list.find_transcript(['es', 'es-419', 'es-ES', 'en', 'en-US'])
        except:
            # Si no encuentra esos idiomas, agarra EL PRIMERO que exista en la lista a la fuerza
            transcript = next(iter(transcript_list))
            
        # Descargamos el texto
        datos = transcript.fetch()
        texto_completo = " ".join([fragmento['text'] for fragmento in datos])
        
        return texto_completo
        
    except Exception as e:
        return f"ERROR_INTERNO: Video sin subtítulos o bloqueado. Detalle: {e}"
