# cerebro.py
import streamlit as st
from groq import Groq
import json
from config import SYSTEM_PROMPT
import herramientas # <--- IMPORTAMOS LOS BRAZOS

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def transcribir_audio(audio_bytes):
    try:
        transcription = client.audio.transcriptions.create(
            file=("audio.webm", audio_bytes),
            model="whisper-large-v3",
            language="es"
        )
        return transcription.text
    except Exception as e:
        print(f"Error de transcripción: {e}")
        return None

def pensar_respuesta(texto_usuario, historial):
    mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for item in historial[-10:]:
        role = "assistant" if item.get("autor") == "EDITH" else "user"
        mensajes_api.append({"role": role, "content": item.get("msg")})
        
    mensajes_api.append({"role": "user", "content": texto_usuario})

    # PRIMERA FASE: Le damos el texto y las herramientas. Ella decide qué hacer.
    res = client.chat.completions.create(
        messages=mensajes_api,
        model="llama-3.3-70b-versatile",
        tools=herramientas.mis_herramientas, # Le mostramos la caja de herramientas
        tool_choice="auto"
    )
    
    mensaje_respuesta = res.choices[0].message

    # ¿E.D.I.T.H. decidió usar una herramienta?
    if mensaje_respuesta.tool_calls:
        mensajes_api.append(mensaje_respuesta) # Guardamos su decisión
        
        # Ejecutamos la herramienta que ella eligió
        for tool_call in mensaje_respuesta.tool_calls:
            nombre_funcion = tool_call.function.name
            argumentos = json.loads(tool_call.function.arguments)
            
            if nombre_funcion == "obtener_fecha_hora":
                resultado = herramientas.obtener_fecha_hora()
            elif nombre_funcion == "obtener_clima":
                ciudad = argumentos.get("ciudad", "Buenos Aires")
                resultado = herramientas.obtener_clima(ciudad)
            else:
                resultado = "Herramienta desconocida"
                
            # Le pasamos el resultado crudo a E.D.I.T.H.
            mensajes_api.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": nombre_funcion,
                "content": str(resultado)
            })
            
        # SEGUNDA FASE: E.D.I.T.H. lee el resultado y te responde con su personalidad
        res_final = client.chat.completions.create(
            messages=mensajes_api,
            model="llama-3.3-70b-versatile"
        )
        return res_final.choices[0].message.content

    # Si no usó herramientas, responde de forma normal
    return mensaje_respuesta.content
