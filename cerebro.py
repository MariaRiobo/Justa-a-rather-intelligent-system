import streamlit as st
from groq import Groq
from config import SYSTEM_PROMPT
import herramientas

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def pensar_respuesta(texto_usuario, historial):
    # --- PASO 1: DETECCIÓN MANUAL DE INTENCIÓN ---
    # Interceptamos la pregunta antes de que llegue al "cerebro"
    texto_min = texto_usuario.lower()
    datos_extra = ""

    # RASTREO WEB: Si pregunta por deportes, economía o noticias
    if any(w in texto_min for w in ["boca", "partido", "resultado", "jugó", "dolar", "noticias", "precio", "quien es"]):
        with st.spinner("E.D.I.T.H. rastreando la red..."):
            datos_extra = herramientas.buscar_en_internet(texto_usuario)
    
    # RASTREO CLIMÁTICO: Si pregunta por el tiempo
    elif any(w in texto_min for w in ["clima", "temperatura", "tiempo"]):
        with st.spinner("Consultando satélites meteorológicos..."):
            datos_extra = herramientas.obtener_clima()

    # --- PASO 2: CONSTRUCCIÓN DEL MENSAJE (INYECCIÓN) ---
    # Creamos un mensaje de sistema dinámico que incluya los hallazgos
    contexto_inyectado = SYSTEM_PROMPT
    
    if datos_extra:
        contexto_inyectado += f"\n\n--- INFORMACIÓN DE CAMPO RECUPERADA ---\n{datos_extra}\n"
        contexto_inyectado += "\nINSTRUCCIÓN CRÍTICA: Responde basándote en los DATOS DE CAMPO de arriba. "
        contexto_inyectado += "Si los datos mencionan un resultado o precio, dalo por cierto. "
        contexto_inyectado += "No digas que no tienes acceso a internet, porque ya te di la información."

    mensajes_api = [{"role": "system", "content": contexto_inyectado}]
    
    # Mantener memoria de los últimos 4 mensajes para contexto
    for item in historial[-4:]:
        role = "assistant" if item.get("autor") == "EDITH" else "user"
        mensajes_api.append({"role": role, "content": item.get("msg")})
    
    mensajes_api.append({"role": "user", "content": texto_usuario})

    try:
        # FASE 3: Generación de respuesta con los datos ya inyectados
        res = client.chat.completions.create(
            messages=mensajes_api,
            model="llama-3.3-70b-versatile"
        )
        return res.choices[0].message.content

    except Exception as e:
        return f"Error en el enlace neuronal: {str(e)}"

def transcribir_audio(audio_bytes):
    try:
        transcription = client.audio.transcriptions.create(
            file=("audio.webm", audio_bytes), 
            model="whisper-large-v3", 
            language="es"
        )
        return transcription.text
    except: return None
