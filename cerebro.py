import streamlit as st
from groq import Groq
import json
from config import SYSTEM_PROMPT
import herramientas

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def pensar_respuesta(texto_usuario, historial):
    # --- DETECTOR DE NECESIDAD DE INFORMACIÓN ---
    # Si el usuario pregunta algo que requiere datos externos, forzamos el uso de la tool.
    palabras_clima = ["clima", "tiempo", "temperatura"]
    palabras_internet = ["boca", "dolar", "partido", "resultado", "noticias", "precio", "quien es", "que paso"]
    
    mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in historial[-2:]:
        role = "assistant" if item.get("autor") == "EDITH" else "user"
        mensajes_api.append({"role": role, "content": item.get("msg")})
    mensajes_api.append({"role": "user", "content": texto_usuario})

    try:
        # CONFIGURACIÓN DE HERRAMIENTA FORZADA
        t_choice = "auto"
        # Si hablas de Boca o noticias, la obligamos a usar "google"
        if any(w in texto_usuario.lower() for w in palabras_internet):
            t_choice = {"type": "function", "function": {"name": "google"}}
        # Si hablas del clima, la obligamos a usar "obtener_clima"
        elif any(w in texto_usuario.lower() for w in palabras_clima):
            t_choice = {"type": "function", "function": {"name": "obtener_clima"}}

        # FASE 1: Ejecución
        res = client.chat.completions.create(
            messages=mensajes_api,
            model="llama-3.3-70b-versatile",
            tools=herramientas.mis_herramientas,
            tool_choice=t_choice # <--- EL GRILLETE DIGITAL
        )
        
        mensaje = res.choices[0].message

        if mensaje.tool_calls:
            mensajes_api.append(mensaje)
            for tool_call in mensaje.tool_calls:
                nombre_f = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                # Ejecución de la lógica real
                if nombre_f == "google": 
                    resultado = herramientas.buscar_en_internet(args.get("consulta", texto_usuario))
                elif nombre_f == "obtener_clima": 
                    resultado = herramientas.obtener_clima(args.get("ciudad", "Buenos Aires"))
                elif nombre_f == "obtener_fecha_hora": 
                    resultado = herramientas.obtener_fecha_hora()
                elif nombre_f == "buscar_en_wikipedia": 
                    resultado = herramientas.buscar_en_wikipedia(args.get("consulta"))
                else: 
                    resultado = "Error de mapeo."

                mensajes_api.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": nombre_f,
                    "content": str(resultado)
                })
            
            # FASE 2: Respuesta final con los datos en la mano
            res_final = client.chat.completions.create(
                messages=mensajes_api,
                model="llama-3.3-70b-versatile"
            )
            return res_final.choices[0].message.content

        return mensaje.content

    except Exception as e:
        # Si falla el forzado (ej: el modelo no sabe qué argumentos poner), volvemos al modo auto
        return f"Error de protocolo táctico: {str(e)}"

def transcribir_audio(audio_bytes):
    try:
        transcription = client.audio.transcriptions.create(file=("audio.webm", audio_bytes), model="whisper-large-v3", language="es")
        return transcription.text
    except: return None
