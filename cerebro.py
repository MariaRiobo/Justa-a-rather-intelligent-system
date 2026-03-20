import streamlit as st
from groq import Groq
from config import SYSTEM_PROMPT
import herramientas

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def pensar_respuesta(texto_usuario, historial):
    # --- PASO 1: DETECCIÓN MANUAL DE INTENCIÓN ---
    # No le preguntamos a la IA, nosotros decidimos si necesita datos.
    texto_min = texto_usuario.lower()
    datos_extra = ""

    if any(w in texto_min for w in ["boca", "partido", "resultado", "dolar", "noticias", "precio", "quien es"]):
        # Buscamos en internet ANTES de que la IA hable
        with st.spinner("E.D.I.T.H. rastreando la red..."):
            datos_extra = herramientas.buscar_en_internet(texto_usuario)
    
    elif any(w in texto_min for w in ["clima", "temperatura", "tiempo"]):
        with st.spinner("Consultando satélites meteorológicos..."):
            datos_extra = herramientas.obtener_clima()

    # --- PASO 2: CONSTRUCCIÓN DEL MENSAJE ---
    # Si conseguimos datos, se los inyectamos como una "notificación del sistema"
    contexto_inyectado = SYSTEM_PROMPT
    if datos_extra:
        contexto_inyectado += f"\n\nDATOS DE RECIÉN OBTENIDOS DEL SISTEMA:\n{datos_extra}\n"
        contexto_inyectado += "\nUSA ESTOS DATOS PARA RESPONDER. NO DIGAS QUE NO TIENES INTERNET."

    mensajes_api = [{"role": "system", "content": contexto_inyectado}]
    
    # Memoria de la conversación
    for item in historial[-4:]:
        role = "assistant" if item.get("autor") == "EDITH" else "user"
        mensajes_api.append({"role": role, "content": item.get("msg")})
    
    mensajes_api.append({"role": "user", "content": texto_usuario})

    try:
        # FASE 3: Respuesta final (Aquí la IA ya tiene la información en su mensaje de sistema)
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
