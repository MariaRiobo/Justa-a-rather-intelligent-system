import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN STARK ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓")

# EL DISEÑO QUE TE ENCANTA (Intacto)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"] { display: none; }
    .orb { width: 60px; height: 60px; background: radial-gradient(circle, #00d4ff 0%, #000 75%); border-radius: 50%; margin: 10px auto; box-shadow: 0 0 20px #00d4ff; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { transform: scale(0.95); opacity: 0.8; } 50% { transform: scale(1.05); opacity: 1; } 100% { transform: scale(0.95); opacity: 0.8; } }
    .stButton > button { background-color: #000 !important; color: #00d4ff !important; border: 2px solid #00d4ff !important; border-radius: 20px !important; width: 100% !important; font-weight: bold !important; }
    .stChatMessage { background: rgba(8, 18, 23, 0.9) !important; border: 1px solid #00d4ff !important; }
    audio { display: none !important; }
    </style>
    <div class="orb"></div>
    <h2 style="text-align: center; color: #00d4ff; letter-spacing: 5px;">E.D.I.T.H.</h2>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Placeholder fantasma para el audio
audio_placeholder = st.empty()

# --- CONTROLES ---
audio_data = mic_recorder(start_prompt="HABLAR AHORA", stop_prompt="ESCUCHANDO...", key='recorder', just_once=True, use_container_width=True)
texto_manual = st.chat_input("Comando...")

# --- PROCESAMIENTO ---
user_text = None
if audio_data:
    try:
        transcription = client.audio.transcriptions.create(
            file=("audio.webm", audio_data['bytes']),
            model="whisper-large-v3",
            language="es" # Obligamos a entender español
        )
        user_text = transcription.text
    except: pass
elif texto_manual:
    user_text = texto_manual

if user_text:
    try:
        # 1. PREPARAR LA MEMORIA (MÓDULO 1 ACTIVADO)
        # Empezamos con la instrucción base del sistema
        mensajes_api = [{"role": "system", "content": "Eres EDITH. Responde corto y profesional."}]
        
        # Leemos los últimos 10 mensajes del historial para no saturar la memoria
        for item in st.session_state.chat_history[-10:]:
            role = "assistant" if item.get("autor") == "EDITH" else "user"
            mensajes_api.append({"role": role, "content": item.get("msg")})
            
        # Añadimos el comando actual que acabas de decir
        mensajes_api.append({"role": "user", "content": user_text})

        # 2. ENVIAR A GROQ CON TODO EL CONTEXTO
        res = client.chat.completions.create(
            messages=mensajes_api,
            model="llama-3.1-8b-instant"
        )
        respuesta = res.choices[0].message.content
        
        # Guardamos en el historial visible
        st.session_state.chat_history.append({"autor": "Francis", "msg": user_text})
        st.session_state.chat_history.append({"autor": "EDITH", "msg": respuesta})
        
        # --- MOTOR DE AUDIO ---
        tts = gTTS(text=respuesta, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_b64 = base64.b64encode(audio_fp.read()).decode()
        
        st.session_state.audio_key += 1
        
        audio_html = f"""
            <audio autoplay key="{st.session_state.audio_key}">
                <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
            </audio>
        """
        audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error: {e}")

# --- MOSTRAR CHAT ---
for item in reversed(st.session_state.chat_history):
    autor = item.get("autor", "Desconocido")
    msg = item.get("msg", "")
    avatar = "👓" if autor == "EDITH" else "👤"
    
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar=avatar):
        st.write(f"**{autor}:** {msg}")
