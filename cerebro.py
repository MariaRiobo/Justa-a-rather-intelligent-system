import streamlit as st
from groq import Groq
import json
from config import SYSTEM_PROMPT
import herramientas

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def pensar_respuesta(texto_usuario, historial):
    # Inyectamos una instrucción de formato estricto
    mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for item in historial[-2:]: # Memoria muy corta para máxima velocidad
        role = "assistant" if item.get("autor") == "EDITH" else "user"
        mensajes_api.append({"role": role, "content": item.get("msg")})
    
    mensajes_api.append({"role": "user", "content": texto_usuario})

    try:
        # FASE 1: Solicitud de decisión
        res = client.chat.completions.create(
            messages=mensajes_api,
            model="llama-3.3-70b-versatile",
            tools=herramientas.mis_herramientas,
            tool_choice="auto"
        )
        
        mensaje = res.choices[0].message

        # SI EL MODELO PIDE USAR HERRAMIENTAS
        if mensaje.tool_calls:
            mensajes_api.append(mensaje)
            
            for tool_call in mensaje.tool_calls:
                nombre_f = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                # Ejecución táctica
                if nombre_f == "obtener_fecha_hora": resultado = herramientas.obtener_fecha_hora()
                elif nombre_f == "obtener_clima": resultado = herramientas.obtener_clima(args.get("ciudad", "Buenos Aires"))
                elif nombre_f == "buscar_en_wikipedia": resultado = herramientas.buscar_en_wikipedia(args.get("consulta"))
                elif nombre_f == "buscar_en_internet": resultado = herramientas.buscar_en_internet(args.get("consulta"))
                else: resultado = "Error de enlace."

                mensajes_api.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": nombre_f,
                    "content": str(resultado)
                })
            
            # FASE 2: Respuesta final al usuario
            res_final = client.chat.completions.create(
                messages=mensajes_api,
                model="llama-3.3-70b-versatile"
            )
            return res_final.choices[0].message.content

        return mensaje.content

    except Exception as e:
        return f"Señal inestable, señor. Error: {str(e)}"

def transcribir_audio(audio_bytes):
    try:
        transcription = client.audio.transcriptions.create(
            file=("audio.webm", audio_bytes),
            model="whisper-large-v3",
            language="es"
        )
        return transcription.text
    except:
        return None
