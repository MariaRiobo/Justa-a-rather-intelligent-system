# cerebro.py
import streamlit as st
from groq import Groq
from config import SYSTEM_PROMPT

# Inicializamos el cliente de Groq aquí
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def transcribir_audio(audio_bytes):
    """Convierte el audio del micrófono a texto usando Whisper"""
    try:
        transcription = client.audio.transcriptions.create(
            file=("audio.webm", audio_bytes),
            model="whisper-large-v3",
            language="es"
        )
        return transcription.text
    except Exception as e:
        print(f"Error al transcribir: {e}")
        return None

def pensar_respuesta(texto_usuario, historial):
    """Envía el historial y el nuevo mensaje a Llama 3 para obtener una respuesta"""
    mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Cargamos la memoria reciente
    for item in historial[-10:]:
        role = "assistant" if item.get("autor") == "EDITH" else "user"
        mensajes_api.append({"role": role, "content": item.get("msg")})
        
    mensajes_api.append({"role": "user", "content": texto_usuario})

    res = client.chat.completions.create(
        messages=mensajes_api,
        model="llama-3.1-8b-instant"
    )
    return res.choices[0].message.content
