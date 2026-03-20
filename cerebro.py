import streamlit as st
from groq import Groq
from config import SYSTEM_PROMPT
import herramientas

# Configuración del cliente Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def pensar_respuesta(texto_usuario, historial):
    # --- PASO 1: DETECCIÓN MANUAL DE INTENCIÓN ---
    texto_min = texto_usuario.lower()
    datos_extra = ""

    # RASTREO WEB
    keywords_web = ["boca", "river", "partido", "resultado", "jugó", "dolar", "noticias", "precio", "quien es", "quién es"]
    
    if any(w in texto_min for w in keywords_web):
        with st.spinner("E.D.I.T.H. rastreando la red..."):
            datos_extra = herramientas.buscar_en_internet(texto_usuario)
    
    # RASTREO CLIMÁTICO
    elif any(w in texto_min for w in ["clima", "temperatura", "tiempo"]):
        with st.spinner("Consultando satélites meteorológicos..."):
            datos_extra = herramientas.obtener_clima()

    # --- PASO 2: CONSTRUCCIÓN DEL MENSAJE (INYECCIÓN) ---
    contexto_inyectado = SYSTEM_PROMPT
    
    if datos_extra:
        contexto_inyectado += f"\n\n--- INFORMACIÓN DE CAMPO RECUPERADA ---\n{datos_extra}\n"
        contexto_inyectado += "\nINSTRUCCIÓN DE PRIORIDAD ALTA: Analiza los 'DATOS DE CAMPO' de arriba. "
        contexto_inyectado += "Si en los textos aparece un marcador o un resultado, INFÓRMALO DE INMEDIATO. "
        contexto_inyectado += "No digas que no tienes internet."

    mensajes_api = [{"role": "system", "content": contexto_inyectado}]
    
    # Memoria (últimos 4 mensajes)
    for item in historial[-4:]:
        role = "assistant" if item.get("autor") == "EDITH" else "user"
        mensajes_api.append({"role": role, "content": item.get("msg")})
    
    mensajes_api.append({"role": "user", "content": texto_usuario})

    # --- PASO 3: LLAMADA A LA API ---
    try:
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
    except Exception:
        return None
