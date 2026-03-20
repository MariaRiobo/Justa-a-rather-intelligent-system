import streamlit as st
from groq import Groq
import json
from config import SYSTEM_PROMPT
import herramientas

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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

def pensar_respuesta(texto_usuario, historial):
    # Simplificamos los mensajes al máximo para evitar el error 400
    mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Solo mandamos el último mensaje para que no se maree con fallos anteriores
    mensajes_api.append({"role": "user", "content": texto_usuario})

    try:
        # FASE 1: Llamada a la herramienta
        res = client.chat.completions.create(
            messages=mensajes_api,
            model="llama-3.3-70b-versatile",
            tools=herramientas.mis_herramientas,
            tool_choice="auto"
        )
        
        mensaje_respuesta = res.choices[0].message

        # Si el modelo decide usar una herramienta
        if mensaje_respuesta.tool_calls:
            # Agregamos la respuesta del asistente (la intención de usar la tool)
            mensajes_api.append(mensaje_respuesta)
            
            for tool_call in mensaje_respuesta.tool_calls:
                nombre_f = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                # Ejecución de la lógica
                if nombre_f == "obtener_fecha_hora":
                    resultado = herramientas.obtener_fecha_hora()
                elif nombre_f == "obtener_clima":
                    resultado = herramientas.obtener_clima(args.get("ciudad", "Buenos Aires"))
                elif nombre_f == "buscar_en_wikipedia":
                    resultado = herramientas.buscar_en_wikipedia(args.get("consulta"))
                elif nombre_f == "buscar_en_internet":
                    resultado = herramientas.buscar_en_internet(args.get("consulta"))
                else:
                    resultado = "Error de sistema."

                # Agregamos el resultado de la herramienta al flujo
                mensajes_api.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": nombre_f,
                    "content": str(resultado)
                })
            
            # FASE 2: Generar respuesta final basada en los datos obtenidos
            res_final = client.chat.completions.create(
                messages=mensajes_api,
                model="llama-3.3-70b-versatile"
            )
            return res_final.choices[0].message.content

        return mensaje_respuesta.content

    except Exception as e:
        # Si vuelve a fallar el formato, intentamos una respuesta directa sin herramientas
        return f"Error en los sistemas de búsqueda, señor. Detalle: {str(e)}"
