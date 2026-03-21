import streamlit as st

from groq import Groq

from config import SYSTEM_PROMPT

import herramientas

import youtube

import busqueda



# Configuración del cliente Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])



def pensar_respuesta(texto_usuario, historial, texto_documento=""):

    # --- PASO 1: DETECCIÓN MANUAL DE INTENCIÓN ---

    texto_min = texto_usuario.lower()

    datos_extra = ""



 # --- NUEVO PASO 1: SENSORES TÁCTICOS ---

    # Sensores Fijos (Directos de herramientas)

    if any(w in texto_min for w in ["dolar", "dólar"]):

        datos_extra = herramientas.obtener_cotizacion_dolar()

    elif any(w in texto_min for w in ["clima", "temperatura", "tiempo", "pronóstico"]):

        datos_extra = herramientas.obtener_clima()

    elif any(w in texto_min for w in ["hora", "fecha", "día"]):

        datos_extra = herramientas.obtener_fecha_hora()

    

    # Sensor de Red (Google a través de busqueda.py)

    # Si no es ninguna de las anteriores pero pregunta algo de actualidad:

    elif any(w in texto_min for w in ["quien", "quién", "noticias", "resultado", "jugó", "partido", "pasó", "precio"]):

        with st.spinner("🌐 E.D.I.T.H. consultando satélites de red..."):

            datos_extra = busqueda.buscar_en_red(texto_usuario)

            

   # --- PASO 2: CONSTRUCCIÓN DEL MENSAJE (INYECCIÓN) ---

    contexto_inyectado = SYSTEM_PROMPT

    

    # Inyección 1: Datos de las herramientas (Clima, Dólar, Reloj)

    if datos_extra:

        contexto_inyectado += f"\n\n--- INFORMACIÓN DE CAMPO RECUPERADA ---\n{datos_extra}\n"

        contexto_inyectado += "\nINSTRUCCIÓN DE PRIORIDAD ALTA: Analiza los 'DATOS DE CAMPO' de arriba. "

        contexto_inyectado += "Si hay precios o resultados, dálos como información oficial de Industrias Stark."

        contexto_inyectado += "No digas que no tienes internet."



    # Inyección 2: Documentos escaneados o Videos de YouTube

    if texto_documento:

        contexto_inyectado += f"\n\n--- BASE DE CONOCIMIENTO (DOCUMENTO O VIDEO) ---\n"

        contexto_inyectado += f"{texto_documento[:8000]}\n"

        contexto_inyectado += "\n[DIRECTIVA DE SISTEMA CRÍTICA]: Acabas de procesar un archivo o la transcripción de un video. "

        contexto_inyectado += "Tu respuesta DEBE ser hablada. Resume el contenido en un MÁXIMO ABSOLUTO de 3 oraciones cortas. "

        contexto_inyectado += "ESTÁ TOTALMENTE PROHIBIDO usar listas, viñetas o textos largos. Ve directo al grano."

        

    # Empaquetamos todo el contexto en el Sistema

    mensajes_api = [{"role": "system", "content": contexto_inyectado}]

    

    # Memoria (últimos 4 mensajes)

    for item in historial[-4:]:

        role = "assistant" if item.get("autor") == "EDITH" else "user"

        mensajes_api.append({"role": role, "content": item.get("msg")})

    

   # Agregamos la instrucción actual del usuario

    mensajes_api.append({"role": "user", "content": texto_usuario})



    # 🔋 LISTA DE REACTORES DE RESPALDO (En orden de potencia)

    modelos_disponibles = [

        "llama-3.3-70b-versatile",  # Reactor Principal

        "llama-3.1-8b-instant",     # Respaldo Rápido

        "gemma2-9b-it",             # Respaldo Google

        "mixtral-8x7b-32768"        # Respaldo de Emergencia

    ]



    # --- PASO 3: LLAMADA A LA API CON PROTOCOLO DE REDUNDANCIA ---

    for modelo_actual in modelos_disponibles:

        try:

            # Intentamos la conexión con el modelo actual de la lista

            res = client.chat.completions.create(

                messages=mensajes_api,

                model=modelo_actual,

                temperature=0.7

            )

            # Si tiene éxito, devolvemos la respuesta y salimos de la función

            return res.choices[0].message.content



        except Exception as e:

            error_str = str(e).lower()

            

            # Verificamos si el error es por falta de tokens (429 o Rate Limit)

            if "rate_limit" in error_str or "429" in error_str or "too many requests" in error_str:

                # Si nos quedamos sin energía, imprimimos aviso y saltamos al siguiente modelo

                print(f"⚠️ Reactor {modelo_actual} agotado. Reenrutando energía...")

                continue 

            else:

                # Si es un error diferente (ej. se cortó el internet), abortamos

                return f"🚨 Error crítico en el enlace neuronal: {str(e)}"



    # Si terminamos el bucle y nada funcionó:

    return "🚨 Comandante, todos los reactores auxiliares están agotados. Sistema en espera de recarga."

    

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
