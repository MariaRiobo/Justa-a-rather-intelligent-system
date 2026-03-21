import yt_dlp
import requests
import re

def extraer_id_youtube(url):
    patron = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(patron, url)
    return match.group(1) if match else None

def obtener_transcripcion(url):
    video_id = extraer_id_youtube(url)
    if not video_id: 
        return "ERROR_INTERNO: URL inválida."
    
    # Configuramos el extractor sigiloso
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['es', 'en'],
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraemos la metadata engañando a los escudos de YouTube
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            
            # Juntamos subtítulos manuales y automáticos
            subs = info.get('subtitles', {})
            auto_subs = info.get('automatic_captions', {})
            all_subs = {**auto_subs, **subs}
            
            if not all_subs:
                return "ERROR_INTERNO: El video no tiene subtítulos disponibles."
                
            # Prioridad de infiltración: Español, luego Inglés, luego lo que haya
            lang_to_use = None
            for lang in ['es', 'en']:
                if lang in all_subs:
                    lang_to_use = lang
                    break
            
            if not lang_to_use:
                lang_to_use = list(all_subs.keys())[0]
                
            # Buscamos el formato json3 (el formato de datos puro de YouTube)
            sub_url = None
            for formato in all_subs[lang_to_use]:
                if formato.get('ext') == 'json3':
                    sub_url = formato.get('url')
                    break
            
            if not sub_url:
                return "ERROR_INTERNO: Formato de subtítulo no descifrable."
                
            # Descargamos el archivo directamente del servidor interno de YouTube
            resp = requests.get(sub_url)
            if resp.status_code != 200:
                return "ERROR_INTERNO: No se pudo descargar el archivo de subtítulos."
                
            datos = resp.json()
            
            # Limpiamos el texto de códigos y marcas de tiempo
            texto = []
            for evento in datos.get('events', []):
                for seg in evento.get('segs', []):
                    if 'utf8' in seg:
                        texto.append(seg['utf8'])
                        
            texto_completo = "".join(texto).replace('\n', ' ')
            texto_completo = re.sub(r'\s+', ' ', texto_completo).strip()
            
            if not texto_completo:
                return "ERROR_INTERNO: Archivo de subtítulos vacío."
                
            return texto_completo
            
    except Exception as e:
        # Si algo falla, atrapamos solo la primera línea del error para no saturar
        error_msg = str(e).split('\n')[0] 
        return f"ERROR_INTERNO: El extractor blindado falló. Detalle: {error_msg}"
