# temporizador.py
from groq import Groq
import streamlit as st
import re

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def extraer_segundos(texto_usuario):
    """Usa el LLM para entender el tiempo pedido por la Jefa y lo convierte a segundos"""
    prompt = f"""
    Actúa como un extractor de tiempo matemático. El usuario quiere poner un temporizador. 
    Analiza el texto y extrae SOLO la cantidad total en SEGUNDOS.
    Ejemplos: 
    - "pon un timer de 5 minutos" -> 300
    - "avísame en 1 hora y media" -> 5400
    - "alarma en 10 segundos" -> 10
    - "en un minuto" -> 60
    Texto del usuario: "{texto_usuario}"
    Responde SOLO con el número (ej: 300).
    """
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", # Usamos el modelo más rápido posible
            temperature=0,
            max_tokens=10
        )
        # Extraemos solo los números por si la IA añade texto extra por error
        numeros = re.findall(r'\d+', res.choices[0].message.content)
        if numeros:
            return int(numeros[0])
        return 0
    except Exception:
        return 0
