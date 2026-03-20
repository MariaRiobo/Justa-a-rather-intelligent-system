# app.py (Guardado en tu caso como edith.py)
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# Módulos Stark
from config import CSS_STARK
import cerebro
import voz
import vision # <--- NUEVO MÓDULO

# --- CONFIGURACIÓN UI ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓")
st.markdown(CSS_STARK, unsafe_allow_html=True)
st.markdown('<div class="orb"></div><h2 style="text-align: center; color: #00d4ff; letter-spacing: 5px;">E.D.I.T.H.</h2>', unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

audio_placeholder = st.empty()

# --- SENSORES ÓPTICOS (NUEVO) ---
with st.expander("👁️ Activar Sensores Ópticos"):
    opcion_vision = st.radio("Modo de entrada:", ["Cámara", "Archivo"], horizontal=True)
    imagen_actual = None
    if opcion_vision == "Cámara":
        imagen_actual = st.camera_input("Capturar entorno")
    else:
        imagen_actual = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'])

# --- CONTROLES DE AUDIO / TEXTO ---
audio_data = mic_recorder(start_prompt="HABLAR AHORA", stop_prompt="ESCUCHANDO...", key='recorder', just_once=True, use_container_width=True)
texto_manual = st.chat_input("Comando (o pregunta sobre la foto)...")

# --- PROCESAMIENTO CENTRAL ---
user_text = None
if audio_data:
    user_text = cerebro.transcribir_audio(audio_data['bytes'])
elif texto_manual:
    user_text = texto_manual

# El sistema se activa si hablaste/escribiste, o si simplemente tomaste una foto
if user_text or imagen_actual:
    try:
        texto_log = user_text if user_text else "[Imagen enviada]"
        
        # Enrutamiento: ¿Usamos los ojos o solo el cerebro?
        if imagen_actual:
            # Procesamiento visual
            respuesta = vision.analizar_imagen(imagen_actual.getvalue(), user_text)
        else:
            # Procesamiento lógico normal
            respuesta = cerebro.pensar_respuesta(user_text, st.session_state.chat_history)
        
        # Guardamos en el historial
        st.session_state.chat_history.append({"autor": "Francis", "msg": texto_log})
        st.session_state.chat_history.append({"autor": "EDITH", "msg": respuesta})
        
        # Generamos la voz
        audio_b64 = voz.generar_audio(respuesta)
        st.session_state.audio_key += 1
        
        audio_html = f"""
            <audio autoplay key="{st.session_state.audio_key}">
                <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
            </audio>
        """
        audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error del sistema: {e}")

# --- MOSTRAR CHAT ---
for item in reversed(st.session_state.chat_history):
    autor = item.get("autor", "Desconocido")
    msg = item.get("msg", "")
    avatar = "👓" if autor == "EDITH" else "👤"
    
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar=avatar):
        st.write(f"**{autor}:** {msg}")
