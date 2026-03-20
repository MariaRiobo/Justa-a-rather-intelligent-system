# vision.py
import streamlit as st
from groq import Groq
import base64
from config import SYSTEM_PROMPT

# Inicializamos el cliente de Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def analizar_imagen(imagen_bytes, texto_usuario):
    """Codifica la imagen y la envía al modelo de visión de Groq"""
    # 1. Convertimos la imagen a Base64
    imagen_b64 = base64.b64encode(imagen_bytes).decode('utf-8')
    
    # Si el usuario no dice nada al subir la foto, le ponemos un comando por defecto
    comando = texto_usuario if texto_usuario else "¿Qué ves en esta imagen? Sé concisa."
    
    # 2. Formateamos el mensaje multimodal (Texto + Imagen)
    mensajes_api = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": comando},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagen_b64}"}}
            ]
        }
    ]
    
  # 3. Llamada al modelo Llama 4 Vision (El nuevo lente de última generación)
    try:
        res = client.chat.completions.create(
            messages=mensajes_api,
            model="meta-llama/llama-4-scout-17b-16e-instruct", # <--- EL NUEVO LENTE LLAMA 4
            temperature=0.6,
            max_tokens=512
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error en el sensor óptico: {e}"
