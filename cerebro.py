import streamlit as st
from groq import Groq
import json
from config import SYSTEM_PROMPT
import herramientas

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def pensar_respuesta(texto_usuario, historial):
    # Forzamos a que el modelo sepa que DEBE responder con JSON de herramientas
    mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Memoria ultra-corta para evitar errores de contexto
    for item in historial[-2:]:
        role = "assistant" if item.get("autor") == "EDITH" else "user"
        mensajes_api.append({"role": role, "content": item.get("msg")})
    
    mensajes_api.append({"role": "user", "content": texto_usuario})

    try:
        # FASE 1: Llamada al modelo
        res = client.chat.completions.create(
            messages=mensajes_api,
            model="llama-3.3-70b-versatile",
            tools=herramientas.mis_herramientas,
            tool_choice="auto"
        )
        
        mensaje = res.choices[0].message

        # Bloque de ejecución forzada
        if mensaje.tool_calls:
            mensajes_api.append(mensaje)
            
            for tool_call in mensaje.tool_calls:
                nombre_f = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                # Ejecución de herramientas
                if nombre_f == "obtener_fecha_hora":
                    resultado = herramientas.obtener_fecha_hora()
                elif nombre_f == "obtener_clima":
                    resultado = herramientas.obtener_clima(args.get("ciudad", "Buenos Aires"))
                elif nombre_f == "buscar_en_wikipedia":
                    resultado = herramientas.buscar_en_wikipedia(args.get("consulta"))
                elif nombre_f == "buscar_en_internet":
                    resultado = herramientas.buscar_en_internet(args.get("consulta"))
                else:
                    resultado = "Sensor no mapeado."

                mensajes_api.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": nombre_f,
                    "content": str(resultado)
                })
            
            # FASE 2: Generar respuesta final con los datos
            res_final = client.chat.completions.create(
                messages=mensajes_api,
                model="llama-3.3-70b-versatile"
            )
            return res_final.choices[0].message.content

        # Si el modelo "escribe" el código manualmente en vez de usar la tool
        if "<function=" in mensaje.content:
            return "Error de puerto: La IA intentó escribir código en lugar de ejecutarlo. Reintentando enlace..."

        return mensaje.content

    except Exception as e:
        return f"Interferencia detectada: {str(e)}"

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
