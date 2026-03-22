# temporizador.py
from groq import Groq
import streamlit as st
import re
from datetime import datetime
import pytz

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def extraer_segundos(texto_usuario):
    # 1. Obtenemos la hora exacta de Argentina AHORA
    zona_horaria = pytz.timezone('America/Argentina/Buenos_Aires')
    ahora = datetime.now(zona_horaria)
    hora_actual_str = ahora.strftime("%H:%M")
    
    # 2. Le damos contexto total a la IA
    prompt = f"""
    Eres un calculador de tiempo preciso.
    HORA ACTUAL: {hora_actual_str}
    SOLICITUD DEL USUARIO: "{texto_usuario}"
    
    TAREA: Calcula cuántos SEGUNDOS faltan desde la HORA ACTUAL hasta lo que pide el usuario.
    - Si pide "en 5 minutos", responde [300].
    - Si pide "a las 17:14" y son las 17:10, faltan 4 minutos, responde [240].
    
    RESPONDE ÚNICAMENTE EL NÚMERO ENTRE CORCHETES, EJEMPLO: [60]
    """
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", # Rápido y confiable
            temperature=0
        )
        respuesta = res.choices[0].message.content.strip()
        match = re.search(r'\[(\d+)\]', respuesta)
        return int(match.group(1)) if match else 0
    except:
        return 0
