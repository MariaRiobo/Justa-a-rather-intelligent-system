import streamlit as st
from groq import Groq
from config import SYSTEM_PROMPT
import herramientas

# Configuración del cliente Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def pensar_respuesta(texto_usuario, historial, texto_documento=""):
    # --- PASO 1: DETECCIÓN MANUAL DE INTENCIÓN ---
    texto_min = texto_usuario.lower()
    datos_extra = ""

    # PRIORIDAD 1: Sensor de Divisas (Dólar)
    if "dolar" in texto_min or "dólar" in texto_min:
        with st.spinner("Accediendo a la base de datos financiera..."):
            datos_extra = herramientas.obtener_cotizacion_dolar()
            
    # PRIORIDAD 2: Rastreo Meteorológico
    elif any(w in texto_min for w in ["clima", "temperatura", "tiempo", "llover", "lluvia", "pronóstico", "mañana", "semana"]):
        with st.spinner("Consultando satélites meteorológicos..."):
            datos_extra = herramientas.obtener_clima()
            
    # PRIORIDAD NUEVA: Reloj del Sistema (¡AQUÍ ESTÁ EL ARREGLO!)
    elif any(w in texto_min for w in ["hora", "fecha", "día", "dia", "qué hora"]):
        with st.spinner("Sincronizando reloj atómico..."):
            datos_extra = herramientas.obtener_fecha_hora()        

    # PRIORIDAD 3: Rastreo Web General (Boca, noticias, etc.)
    elif any(w in texto_min for w in ["boca", "river", "partido", "resultado", "jugó", "noticias", "precio", "quien es", "quién es"]):
        with st.spinner("E.D.I.T.H. rastreando la red..."):
            datos_extra = herramientas.buscar_en_internet(texto_usuario)

   # --- PASO 2: CONSTRUCCIÓN DEL MENSAJE (INYECCIÓN) ---
    contexto_inyectado = SYSTEM_PROMPT
    
    # Inyección 1: Datos de las herramientas (Clima, Dólar, Reloj)
    if datos_extra:
        contexto_inyectado += f"\n\n--- INFORMACIÓN DE CAMPO RECUPERADA ---\n{datos_extra}\n"
        contexto_inyectado += "\nINSTRUCCIÓN DE PRIORIDAD ALTA: Analiza los 'DATOS DE CAMPO' de arriba. "
        contexto_inyectado += "Si hay precios o resultados, dálos como información oficial de Industrias Stark."
        contexto_inyectado += "No digas que no tienes internet."

    # Inyección 2: Documentos escaneados (¡NUEVO!)
        # Inyección 2: Documentos escaneados
    if texto_documento:
        contexto_inyectado += f"\n\n--- DOCUMENTO ESCANEADO EN MEMORIA ---\n"
        contexto_inyectado += "El usuario ha subido un documento. Úsalo como base de conocimiento principal.\n"
        contexto_inyectado += "REGLA CRÍTICA DE VOZ: Tu respuesta será leída en voz alta por un sintetizador. "
        contexto_inyectado += "DEBES ser extremadamente conciso. Resume de qué trata el archivo en un máximo de 3 oraciones cortas y fluidas. "
        contexto_inyectado += "No hagas listas largas ni viñetas, habla como un asistente real. Si el usuario quiere más detalles, te los pedirá después.\n"
        contexto_inyectado += f"{texto_documento[:10000]}\n"

    # Empaquetamos todo el contexto en el Sistema
    mensajes_api = [{"role": "system", "content": contexto_inyectado}]
    
    # Memoria (últimos 4 mensajes)
    for item in historial[-4:]:
        role = "assistant" if item.get("autor") == "EDITH" else "user"
        mensajes_api.append({"role": role, "content": item.get("msg")})
    
    # Agregamos la instrucción actual del usuario
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
