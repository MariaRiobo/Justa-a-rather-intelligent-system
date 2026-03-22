# temporizador.py
from groq import Groq
import streamlit as st
import re
from datetime import datetime
import pytz

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def extraer_segundos(texto_usuario):
    zona_horaria = pytz.timezone('America/Argentina/Buenos_Aires')
    hora_actual = datetime.now(zona_horaria)
    hora_str = hora_actual.strftime('%H:%M:%S')
    
    prompt = f"""
    Calcula cuántos SEGUNDOS faltan desde las {hora_str} hasta la hora o tiempo que pide el usuario.
    Usuario: "{texto_usuario}"
    Responde ÚNICAMENTE con el número final entre corchetes. Ejemplo: [300]. Nada más.
    """
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", # <--- Volvemos al reactor rápido que NO se agota
            temperature=0,
            max_tokens=10
        )
        respuesta = res.choices[0].message.content.strip()
        
        # Cazamos el número entre corchetes
        match = re.search(r'\[(\d+)\]', respuesta)
        if match:
            return int(match.group(1))
        
        # Plan de emergencia
        numeros = re.findall(r'\d+', respuesta)
        if numeros:
            return int(numeros[-1]) 
        return 0
    except Exception:
        return 0
