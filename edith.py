import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- CSS STARK V5 (EL REGRESO DEL ORBE) ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0f7fa; }
    
    /* El Orbe que contiene al Micrófono */
    .mic-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px auto;
        width: 120px;
        height: 120px;
        background: radial-gradient(circle, rgba(0,212,255,0.2) 0%, rgba(8,18,23,1) 70%);
        border: 2px solid #00d4ff;
        border-radius: 50%;
        box-shadow: 0 0 20px #00d4ff, inset 0 0 15px #00d4ff;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.98); box-shadow: 0 0 20px #00d4ff; }
        50% { transform: scale(1.05); box-shadow: 0 0 40px #00d4ff; }
        100% { transform: scale(0.98); box-shadow: 0 0 20px #00d4ff; }
    }

    /* Estilo del botón interno de la librería */
    .stButton>button {
        background-color: transparent !important;
        border: none !important;
        color: #00d4ff !important;
        font-weight: bold !important;
        text-shadow: 0 0 10px #00d4ff;
    }

    /* Chat Holográfico */
    .stChatMessage {
        background: rgba(8, 18, 23, 0.8) !important;
        border: 1px solid #00d4ff !important;
        border-radius: 15px !important;
        margin-bottom: 15px !important;
    }

    /* Ocultar basura visual */
    audio { display: none !important; }
    [data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h2 style='text-align: center; color: #00d4ff; text-shadow: 0 0 15px #00d4ff;'>E.D.I.T.H.</h2>", unsafe_allow_html=True)
st.write("<p style='text-align: center; opacity: 0.7;'>Protocolos tácticos activos.</p>", unsafe_allow_html=True)

# --- CONEXIÓN ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- EL MICRÓFONO DENTRO DEL ORBE ---
# Creamos el efecto visual del orbe y metemos el grabador dentro
st.markdown('<div class="mic-container">', unsafe_allow_html=True)
audio_data = mic_recorder(
    start_prompt="🎙️",
    stop_prompt="⚡",
    key='recorder',
    just_once=True
)
st.markdown('</div>', unsafe_allow_html=True)
st.write("<p style='text-align: center; font-size: 0.8em;'>Toca el micro para hablar</p>", unsafe_allow_html=True)

# --- LÓGICA ---
user_text = None
if audio_data:
    try:
        with st.spinner(""):
            transcription = client.audio.transcriptions.create(
                file=("audio.webm", audio_data['bytes']),
                model="whisper-large-v3"
            )
            user_text = transcription.text
    except: pass

if user_text:
    try:
        res = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres EDITH. Responde corto y ejecutivo a Francis."},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.1-8b-instant"
        )
        ans = res.choices[0].message.content
        st.session_state.chat_history.append(("Francis", user_text))
        st.session_state.chat_history.append(("EDITH", ans))

        # Audio invisible
        tts = gTTS(text=ans, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        b64 = base64.b64encode(audio_fp.read()).decode()
        
        id_audio = int(time.time())
        audio_html = f'''
            <audio autoplay id="{id_audio}"><source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg"></audio>
            <script>document.getElementById("{id_audio}").play();</script>
        '''
        st.markdown(audio_html, unsafe_allow_html=True)
        st.rerun()
    except: pass

# --- HISTORIAL ---
for autor, msg in st.session_state.chat_history[::-1]:
    is_edith = (autor == "EDITH")
    with st.chat_message("assistant" if is_edith else "user", avatar="👓" if is_edith else "👤"):
        st.write(f"**{autor}:** {msg}")
