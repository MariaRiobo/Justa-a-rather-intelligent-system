import streamlit as st
from groq import Groq
from config import SYSTEM_PROMPT
import herramientas
import youtube
import temporizador
import calendario

# Configuración del cliente Groq: funciona
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def pensar_respuesta(texto_usuario, historial, texto_documento=""):
    # --- PASO 1: DETECCIÓN MANUAL DE INTENCIÓN ---
    texto_min = texto_usuario.lower()
    datos_extra = ""
    
                # --- PRIORIDAD 0: INTERCEPTOR DE AGENDA (EJECUCIÓN DIRECTA) ---
    if any(w in texto_min for w in ["agenda", "agendar", "programa", "reunion", "cita", "evento"]):
        import pytz
        from datetime import datetime
        import calendario  # <--- IMPORTANTE: Importamos tu módulo
        
        zona = pytz.timezone('America/Argentina/Buenos_Aires')
        ahora = datetime.now(zona)
        
        # Le pedimos a la IA que solo extraiga los datos
        prompt_agenda = f"FECHA ACTUAL: {ahora.strftime('%Y-%m-%d %H:%M:%S')}. Extrae datos de: '{texto_usuario}'. Responde SOLO el código: $$AGENDAR|Titulo|Inicio_ISO|Fin_ISO$$. No hables."
        
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_agenda}],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        codigo_ia = res.choices[0].message.content.strip()

        # AQUÍ ESTÁ EL TRUCO: Si hay código, el cerebro ejecuta la acción ANTES de responder
        if "$$AGENDAR|" in codigo_ia:
            try:
                partes = codigo_ia.replace("$$", "").split("|")
                if len(partes) >= 4:
                    # ESTA ES LA LLAMADA REAL A GOOGLE
                    resultado_google = calendario.agendar_evento(partes[1], partes[2], partes[3])
                    return f"✅ **SISTEMA ACTUALIZADO:** {resultado_google}"
            except Exception as e:
                return f"🚨 Error en el despliegue de agenda: {e}"
        
        return codigo_ia # Por si la IA no generó el código
 
        # --- PRIORIDAD 0.5: LECTURA DE AGENDA (EL RASTREADOR) ---
    elif any(w in texto_min for w in ["qué tengo", "eventos", "proximos", "calendario", "agenda", "planes"]) and "agendar" not in texto_min:
        with st.spinner("Sincronizando con los servidores de Google..."):
            try:
                import calendario
                # Llamamos a la función que ya tenías escrita
                reporte_eventos = calendario.revisar_agenda()
                return f"👓 **Reporte de Situación - Agenda:**\n\n{reporte_eventos}"
            except Exception as e:
                return f"🚨 Fallo en los sensores de lectura: {str(e)}"


    # PRIORIDAD 1: Sensor de Divisas (Dólar)
    elif "dolar" in texto_min or "dólar" in texto_min:
        with st.spinner("Accediendo a la base de datos financiera..."):
            datos_extra = herramientas.obtener_cotizacion_dolar()
            
              
    # PRIORIDAD 2: Rastreo Meteorológico
    elif any(w in texto_min for w in ["clima", "temperatura", "tiempo", "llover", "lluvia", "pronóstico", "mañana", "semana"]):
        with st.spinner("Consultando satélites meteorológicos..."):
            datos_extra = herramientas.obtener_clima()
            
    # PRIORIDAD 3: Reloj del Sistema (¡AQUÍ ESTÁ EL ARREGLO!)
    elif any(w in texto_min for w in ["hora", "fecha", "día", "dia", "qué hora"]):
        with st.spinner("Sincronizando reloj atómico..."):
            datos_extra = herramientas.obtener_fecha_hora()        

    # PRIORIDAD 4: Rastreo Web General (Boca, noticias, etc.)
    elif any(w in texto_min for w in ["boca", "river", "partido", "resultado", "jugó", "noticias", "precio", "quien es", "quién es"]):
        with st.spinner("E.D.I.T.H. rastreando la red..."):
            datos_extra = herramientas.buscar_en_internet(texto_usuario)
            
  # PRIORIDAD 5: Temporizador Táctico
  
    elif any(w in texto_min for w in ["alarma", "temporizador", "avísame", "avisame", "timer"]):
        import re
        from datetime import datetime
        import pytz
        
        # 1. FORZAMOS la hora actual de Argentina para que la IA sepa dónde está parada
        zona = pytz.timezone('America/Argentina/Buenos_Aires')
        ahora = datetime.now(zona)
        hora_actual_formato = ahora.strftime("%H:%M:%S") # Incluimos segundos para precisión
        
        # 2. Le pasamos la HORA ACTUAL como una orden absoluta
        # PROMPT HÍBRIDO: Entiende horas fijas e intervalos
        prompt_t = f"""
        SISTEMA DE TIEMPO STARK.
        HORA ACTUAL: {hora_actual_formato}
        SOLICITUD: "{texto_usuario}"
        
        INSTRUCCIONES:
        1. Si pide una hora fija (ej: "a las 18:00"), calcula los segundos que faltan desde {hora_actual_formato}.
        2. Si pide un intervalo (ej: "10 segundos" o "5 minutos"), conviértelo directamente a segundos.
        3. Responde SOLO el número entre corchetes. Ejemplo: [10] o [300].
        """
        
        try:
            res_t = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_t}],
                model="llama-3.1-8b-instant",
                temperature=0
            )
            resultado_ia = res_t.choices[0].message.content
            match = re.search(r"\[(\d+)\]", resultado_ia)
            segundos = int(match.group(1)) if match else 0
            
            if segundos > 0:
                return f"[TIMER:{segundos}] Entendido, Francis. Temporizador activo por {segundos} segundos."
            else:
                return "Jefa, no pude procesar el tiempo solicitado."
        except:
            return "Error en los sensores de tiempo."
            
            
      
      # --- PASO 2: CONSTRUCCIÓN DEL MENSAJE (INYECCIÓN) ---
    import pytz
    from datetime import datetime
    zona_ar = pytz.timezone('America/Argentina/Buenos_Aires')
    fecha_hoy = datetime.now(zona_ar).strftime("%Y-%m-%d %H:%M")
    
    # Le pegamos la fecha actual en la frente a E.D.I.T.H. para que no se pierda en el tiempo
    contexto_inyectado = SYSTEM_PROMPT + f"\n\n[RELOJ DEL SISTEMA]: La fecha y hora actual exacta es {fecha_hoy}. Usa esto como tu base estricta para calcular cualquier día u hora del calendario."
    


    
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
