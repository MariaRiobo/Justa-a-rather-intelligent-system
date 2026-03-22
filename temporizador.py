# temporizador.py
from groq import Groq
import streamlit as st
import re
from datetime import datetime
import pytz

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def extraer_segundos(texto_usuario):
    """Usa el LLM para entender el tiempo pedido y lo convierte a segundos"""
    
    # Sincronizamos el reloj
    zona_horaria = pytz.timezone('America/Argentina/Buenos_Aires')
    hora_actual = datetime.now(zona_horaria)
    hora_str = hora_actual.strftime('%H:%M:%S')
    
    prompt = f"""
    Eres una calculadora de tiempo estricta.
    HORA ACTUAL DEL SISTEMA: {hora_str}
    
    El usuario dice: "{texto_usuario}"
    
    Instrucciones:
    1. Calcula cuántos SEGUNDOS exactos faltan desde la HORA ACTUAL hasta la hora o tiempo que pide el usuario.
    2. Responde ÚNICAMENTE con este formato exacto: [SEGUNDOS: número]
    3. No digas ni una sola palabra más, no expliques tu cálculo.
    
    Ejemplos:
    - "en 5 minutos" -> [SEGUNDOS: 300]
    - "avísame en 1 hora" -> [SEGUNDOS: 3600]
    - Si son las 14:00:00 y pide "a las 15:00" -> [SEGUNDOS: 3600]
    """
    try:
        # Usamos el modelo más inteligente de Groq para que no falle la resta
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", # <--- EL CEREBRO MATEMÁTICO
            temperature=0,
            max_tokens=20
        )
        respuesta = res.choices[0].message.content.strip()
        
        # Cazamos exactamente la etiqueta, ignorando cualquier otro número
        match = re.search(r'\[SEGUNDOS:\s*(\d+)\]', respuesta, re.IGNORECASE)
        if match:
            return int(match.group(1))
        else:
            # Plan de emergencia: si no usa la etiqueta, tomamos el ÚLTIMO número que haya dicho
            numeros = re.findall(r'\d+', respuesta)
            if numeros:
                return int(numeros[-1]) 
        return 0
    except Exception:
        return 0
