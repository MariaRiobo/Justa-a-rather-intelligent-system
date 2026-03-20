# cerebro.py
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
    except Exception as e:
        return None

def pensar_respuesta(texto_usuario, historial):
    instruccion_critica = "\nIMPORTANTE: Tienes herramientas conectadas. Si el usuario pregunta el CLIMA o la HORA, es OBLIGATORIO que uses las 'tools' (obtener_clima o obtener_fecha_hora). NO inventes ni deduzcas la respuesta."
    
    mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT + instruccion_critica}]
    
    for item in historial[-4:]:
        role = "assistant" if item.get("autor") == "EDITH" else "user"
        mensajes_api.append({"role": role, "content": item.get("msg")})
        
    mensajes_api.append({"role": "user", "content": texto_usuario})

    res = client.chat.completions.create(
        messages=mensajes_api,
        model="llama-3.3-70b-versatile",
        tools=herramientas.mis_herramientas,
        tool_choice="auto"
    )
    
    mensaje_respuesta = res.choices[0].message

  if mensaje_respuesta.tool_calls:
        mensajes_api.append({
            "role": "assistant",
            "content": mensaje_respuesta.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                } for tc in mensaje_respuesta.tool_calls
            ]
        })
        
        for tool_call in mensaje_respuesta.tool_calls:
            nombre_funcion = tool_call.function.name
            argumentos = json.loads(tool_call.function.arguments)
            
            # --- RUTAS DE HERRAMIENTAS ---
            if nombre_funcion == "obtener_fecha_hora":
                resultado = herramientas.obtener_fecha_hora()
            elif nombre_funcion == "obtener_clima":
                resultado = herramientas.obtener_clima(argumentos.get("ciudad", "Buenos Aires"))
            elif nombre_funcion == "buscar_en_wikipedia":
                resultado = herramientas.buscar_en_wikipedia(argumentos.get("consulta"))
            else:
                resultado = "Herramienta no encontrada."
            # -----------------------------
                
            mensajes_api.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": nombre_funcion,
                "content": str(resultado)
            })
            
        res_final = client.chat.completions.create(
            messages=mensajes_api,
            model="llama-3.3-70b-versatile"
        )
        return res_final.choices[0].message.content
