from youtube_transcript_api import YouTubeTranscriptApi
import re

def extraer_id_youtube(url):
    """Regex nivel Stark para capturar cualquier tipo de link (Shorts, mobile, web)"""
    patron = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(patron, url)
    return match.group(1) if match else None

def obtener_transcripcion(url):
    video_id = extraer_id_youtube(url)
    
    if not video_id:
        return "ERROR_INTERNO: No se pudo detectar el ID exacto del video en el enlace."
        
    try:
        # Obtenemos la lista de todas las pistas de subtítulos del video
        lista_transcripciones = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            # Buscamos primero en español o inglés
            transcripcion = lista_transcripciones.find_transcript(['es', 'en'])
        except:
            # Si no hay, agarramos la primera que exista en la lista a la fuerza
            transcripcion = [t for t in lista_transcripciones][0]
            
        datos = transcripcion.fetch()
        texto_completo = " ".join([fragmento['text'] for fragmento in datos])
        return texto_completo
        
    except Exception as e:
        return f"ERROR_INTERNO: Este video no tiene subtítulos (ni siquiera automáticos) o están bloqueados. Detalle: {e}"
