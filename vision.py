# vision.py
import streamlit as st
from groq import Groq
import base64

# Inicializamos el cliente de Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def analizar_imagen(imagen_bytes, texto_usuario):
    """Codifica la imagen y la envía al modelo de visión de Groq"""
    # 1. Convertimos la imagen a Base64
    imagen_b64 = base64.b64encode(imagen_bytes).decode('utf-8')
    
    # Si la Jefa no dice nada, pedimos un escaneo detallado por defecto
    comando = texto_usuario if texto_usuario else "Analiza esta imagen con extremo detalle técnico. Describe todo lo que ves, lee cualquier texto visible e identifica objetos clave."
    
    # 2. Formateamos el mensaje multimodal (Texto + Imagen) SIN el System Prompt
    mensajes_api = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": comando},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagen_b64}"}}
            ]
        }
    ]
    
    # 3. Llamada al lente óptico oficial de visión
    try:
        res = client.chat.completions.create(
            messages=mensajes_api,
            model="llama-3.2-11b-vision-preview", # <--- EL LENTE CORRECTO PARA VER IMÁGENES
            temperature=0.4,
            max_tokens=1024 
        )
        return res.choices[0].message.content
        
    except Exception as e:
        return f"ERROR: Fallo en el motor de visión Llama 3.2: {str(e)}"
