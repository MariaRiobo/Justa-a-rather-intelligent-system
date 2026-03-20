# app.py
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# Importamos nuestros propios módulos
from config import CSS_STARK
import cerebro
import voz

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

# --- CONTROLES ---
audio_data = mic_recorder(start_prompt="HABLAR AHORA", stop_prompt="ESCUCHANDO...", key='recorder', just_once=True, use_container_width=True)
texto_manual = st.chat_input("Comando...")

# --- PROCESAMIENTO ---
user_text = None
if audio_data:
    user_text = cerebro.transcribir_audio(audio_data['bytes'])
elif texto_manual:
    user_text = texto_manual

if user_text:
    try:
        # 1. EDITH piensa la respuesta
        respuesta = cerebro.pensar_respuesta(user_text, st.session_state.chat_history)
        
        # 2. Guardamos en el historial
        st.session_state.chat_history.append({"autor": "Francis", "msg": user_text})
        st.session_state.chat_history.append({"autor": "EDITH", "msg": respuesta})
        
        # 3. Generamos la voz
        audio_b64 = voz.generar_audio(respuesta)
        st.session_state.audio_key += 1
        
        # 4. Inyectamos al reproductor fantasma
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
