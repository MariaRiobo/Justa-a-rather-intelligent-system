import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- CSS MAESTRO: ESTRUCTURA RÍGIDA STARK ---
st.markdown("""
    <style>
    /* 1. Reset y Fondo */
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"] { display: none; }

    /* 2. HEADER FIJO (Superior) */
    .st-emotion-cache-18ni7ap { padding: 0 !important; } /* Reset padding contenedor */
    
    .fixed-header {
        position: fixed;
        top: 0; left: 0; width: 100%;
        height: 150px;
        background-color: rgba(0, 0, 0, 1);
        z-index: 1000;
        text-align: center;
        padding-top: 20px;
        border-bottom: 2px solid #00d4ff;
        box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
    }
    .orb-glow {
        width: 60px; height: 60px;
        background: radial-gradient(circle, #00d4ff 0%, #000 75%);
        border-radius: 50%; margin: 0 auto;
        box-shadow: 0 0 25px #00d4ff;
        animation: pulse 3s infinite;
    }

    /* 3. SECCIÓN MEDIA (HISTORIAL) */
    .main-content {
        margin-top: 170px !important; /* Espacio para no chocar con header */
        margin-bottom: 200px !important; /* Espacio para no chocar con footer */
        padding: 10px;
    }

    /* 4. FOOTER FIJO (Botón y Teclado) */
    .fixed-footer {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        height: 180px;
        background-color: rgba(0, 0, 0, 1);
        z-index: 1000;
        border-top: 2px solid #00d4ff;
        padding: 20px 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        box-shadow: 0 -5px 20px rgba(0, 212, 255, 0.4);
    }

    /* Botón de Hablar (Estética de la página) */
    .stButton>button {
        background-color: #000000 !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 25px !important;
        width: 250px !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
        box-shadow: 0 0 10px #00d4ff !important;
    }
    
    .stChatInputContainer {
        bottom: 20px !important;
        background: transparent !important;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }
    
    audio { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER FIJO ---
st.markdown("""
    <div class="fixed-header">
        <div class="orb-glow"></div>
        <h1 style='color: #00d4ff; margin: 5px 0; font-size: 1.8em; letter-spacing: 5px;'>E.D.I.T.H.</h1>
        <p style='color: #00d4ff; font-size: 0.8em; opacity: 0.7;'>SISTEMAS ARMÓNICOS ACTIVOS</p>
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- SECCIÓN MEDIA: HISTORIAL ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)
# Iteramos normal para que lo nuevo aparezca ABAJO (estándar de chat)
for autor, msg in st.session_state.chat_history:
    is_edith = (autor == "EDITH")
    with st.chat_message("assistant" if is_edith else "user", avatar="👓" if is_edith else "👤"):
        st.write(f"**{autor}:** {msg}")
st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER FIJO ---
st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1,2,1])
with col2:
    audio_data = mic_recorder(
        start_prompt="HABLAR AHORA",
        stop_prompt="ESCUCHANDO...",
        key='recorder',
        just_once=True,
        use_container_width=True
    )
    # Input de texto manual
    texto_manual = st.chat_input("Ingrese comando táctico...")
st.markdown('</div>', unsafe_allow_html=True)

# --- PROCESAMIENTO ---
user_text = None
if audio_data:
    try:
        transcription = client.audio.transcriptions.create(
            file=("audio.webm", audio_data['bytes']),
            model="whisper-large-v3"
        )
        user_text = transcription.text
    except: pass
elif texto_manual:
    user_text = texto_manual

if user_text:
    try:
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "Eres EDITH. Responde de forma muy concisa y profesional."}, {"role": "user", "content": user_text}],
            model="llama-3.1-8b-instant"
        )
        ans = res.choices[0].message.content
        st.session_state.chat_history.append(("Francis", user_text))
        st.session_state.chat_history.append(("EDITH", ans))

        # Audio
        tts = gTTS(text=ans, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        b64 = base64.b64encode(audio_fp.read()).decode()
        st.session_state.audio_key += 1
        
        audio_html = f'''
            <audio id="v_{st.session_state.audio_key}" autoplay><source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg"></audio>
            <script>document.getElementById("v_{st.session_state.audio_key}").play();</script>
        '''
        st.markdown(audio_html, unsafe_allow_html=True)
        st.rerun()
    except: pass
