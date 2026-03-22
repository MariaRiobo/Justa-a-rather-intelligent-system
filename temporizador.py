# temporizador.py
from groq import Groq
import streamlit as st
import re
from datetime import datetime
import pytz

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def extraer_segundos(texto_usuario):
    """Usa el LLM para entender el tiempo pedido y lo convierte a segundos"""
    
    # 1. Le damos a E.D.I.T.H. un reloj sincronizado con tu zona horaria
    zona_horaria = pytz.timezone('America/Argentina/Buenos_Aires')
    hora_actual = datetime.now(zona_horaria).strftime('%H:%M:%S (Formato 24h)')
    
    # 2. Le explicamos cómo calcular las alarmas absolutas
    prompt = f"""
    Actúa como un extractor de tiempo matemático. El usuario quiere poner un temporizador o alarma. 
    RELOJ DEL SISTEMA ACTUAL: Son las {hora_actual}.
    
    Calcula la cantidad total en SEGUNDOS desde AHORA hasta el momento que pide el usuario.
    Ejemplos: 
    - "pon un timer de 5 minutos" -> 300
    - "avísame en 1 hora" -> 3600
    - Si el reloj dice 14:00:00 y pide "avísame a las 15:00" -> 3600
    - Si el reloj dice 16:50:00 y pide "alarma a las 5 de la tarde" -> 600
    
    Texto del usuario: "{texto_usuario}"
    Responde SOLO con el número total de segundos a esperar (ej: 300). Nada de texto.
    """
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", # Rápido y bueno en matemáticas
            temperature=0,
            max_tokens=10
        )
        # Extraemos solo los números
        numeros = re.findall(r'\d+', res.choices[0].message.content)
        if numeros:
            return int(numeros[0])
        return 0
    except Exception:
        return 0
