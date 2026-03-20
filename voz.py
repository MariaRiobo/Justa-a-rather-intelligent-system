# voz.py
from gtts import gTTS
from io import BytesIO
import base64

def generar_audio(texto):
    """Convierte texto a audio y devuelve la cadena Base64"""
    tts = gTTS(text=texto, lang='es')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return base64.b64encode(audio_fp.read()).decode()
