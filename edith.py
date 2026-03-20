import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN TÁCTICA ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- CSS DEFINITIVO (EL "CHASQUIDO" DE STARK) ---
st.markdown("""
    <style>
    /* 1. Fondo y Base */
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"] { display: none; }

    /* 2. HEADER FIJO (CSS Puro sobre el contenedor de Streamlit) */
    .stMainBlockContainer::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%;
        height: 140px;
        background: black;
        border-bottom: 2px solid #00d4ff;
        z-index: 1000;
    }

    /* 3. TEXTO DEL HEADER (Simulado con CSS para que no se mueva) */
    .stMainBlockContainer::after {
        content: "E.D.I.T.H.\\A SISTEMAS ACTIVOS";
        white-space: pre;
        position: fixed;
        top: 40px; left: 0; width: 100%;
        text-align: center;
        color: #00d4ff;
        font-family: sans-serif;
        font-weight: bold;
        letter-spacing: 5px;
        font-size: 1.5rem;
        z-index: 1001;
    }

    /* 4. AJUSTE DE LA ZONA DE CHAT (El Scroll) */
    [data-testid="stVerticalBlock"] {
        padding-top: 150px !important;
        padding-bottom: 180px !important;
    }

    /* 5. FOOTER Y BARRA DE ESCRITURA */
    /* Estilizamos la barra nativa de Streamlit para que sea Stark */
    [data-testid="stChatInput"] {
        border: 2px solid #00d4ff !important;
        background-color: #081217 !important;
        border-radius: 20px !important;
        bottom: 20px !important;
    }
    
    /* Botón de Hablar (Lo dejamos flotando sobre el input) */
    .stButton > button {
        position: fixed;
        bottom: 100px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1002;
        background-color: black !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 50px !important;
        width: 200px !important;
        box-shadow: 0 0 15px #00d4ff;
    }

    /* Ocultar audio */
    audio { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Falta la API Key en Secrets.")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- HISTORIAL (Solo esto hace scroll) ---
for autor, msg in st.session_state.chat_history:
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar="👓" if autor == "EDITH" else "👤"):
        st.markdown(f"**{autor}:** {msg}")

# --- CONTROLES (FIJOS POR CSS) ---
audio_data = mic_recorder(
    start_prompt="HABLAR AHORA",
    stop_prompt="ESCUCHANDO...",
    key='recorder',
    just_once=True
)

texto_manual = st.chat_input("Comando táctico...")

# --- PROCESAMIENTO ---
user_text = None
if audio_data:
    try:
        with st.spinner("Descifrando..."):
            transcription = client.audio.transcriptions.create(
                file=("audio.webm", audio_data['bytes']),
                model="whisper-large-v3"
            )
            user_text = transcription.text
    except: pass
elif texto_manual:
    user_text = texto_manual

if user_text:
    res = client.chat.completions.create(
        messages=[{"role": "system", "content": "Eres EDITH. Responde corto."}, {"role": "user", "content": user_text}],
        model="llama-3.1-8b-instant"
    )
    ans = res.choices[0].message.content
    st.session_state.chat_history.append(("Francis", user_text))
    st.session_state.chat_history.append(("EDITH", ans))

    # --- MOTOR DE VOZ (Rehecho para que no falle) ---
    tts = gTTS(text=ans, lang='es')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    b64 = base64.b64encode(audio_fp.read()).decode()
    
    st.session_state.audio_key += 1
    
    # Inyección directa de JS para forzar el audio
    audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    st.rerun()
