import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- CSS MAESTRO: ESTRUCTURA DE BLOQUEO TOTAL ---
st.markdown("""
    <style>
    /* 1. Reset de la aplicación */
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebar"] { display: none; }

    /* 2. HEADER FIJO (Superior) */
    .fixed-header {
        position: fixed;
        top: 0; left: 0; width: 100%;
        height: 140px;
        background-color: black;
        z-index: 999;
        text-align: center;
        padding-top: 15px;
        border-bottom: 2px solid #00d4ff;
    }
    .orb-glow {
        width: 50px; height: 50px;
        background: radial-gradient(circle, #00d4ff 0%, #000 70%);
        border-radius: 50%; margin: 0 auto;
        box-shadow: 0 0 20px #00d4ff;
        animation: pulse 3s infinite;
    }

    /* 3. ZONA DE CHAT (Scrollable) */
    .main-chat-content {
        margin-top: 150px !important; /* Espacio para el header */
        margin-bottom: 220px !important; /* Espacio para el footer */
        padding: 20px;
    }

    /* 4. FOOTER FIJO (Inferior) */
    .fixed-footer {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        height: 200px;
        background-color: black;
        z-index: 999;
        border-top: 2px solid #00d4ff;
        padding: 20px 0;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* 5. BOTÓN "HABLAR AHORA" (Estilo Stark) */
    .stButton > button {
        background-color: #000000 !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 50px !important;
        width: 100% !important;
        max-width: 300px;
        font-weight: bold !important;
        letter-spacing: 2px;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.4);
        margin-bottom: 10px;
    }
    
    .stButton > button:active {
        background-color: #00d4ff !important;
        color: black !important;
    }

    /* 6. CORRECCIÓN BARRA DE ESCRITURA */
    /* Forzamos a la barra de Streamlit a vivir dentro de nuestro footer */
    .stChatInputContainer {
        position: fixed !important;
        bottom: 30px !important;
        z-index: 1000 !important;
        background: transparent !important;
        padding: 0 10% !important;
    }
    
    .stChatInputContainer textarea {
        background-color: rgba(8, 18, 23, 0.9) !important;
        border: 1px solid #00d4ff !important;
        color: #e0f7fa !important;
    }

    /* Estilo Burbujas */
    .stChatMessage {
        background: rgba(8, 18, 23, 0.8) !important;
        border: 1px solid #00d4ff !important;
        border-radius: 15px !important;
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
        <h1 style='color: #00d4ff; margin: 5px 0; font-size: 1.5em; letter-spacing: 5px;'>E.D.I.T.H.</h1>
        <p style='color: #00d4ff; font-size: 0.75em; opacity: 0.8;'>SISTEMAS TÁCTICOS ACTIVOS</p>
    </div>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- CUERPO: HISTORIAL ---
st.markdown('<div class="main-chat-content">', unsafe_allow_html=True)
# Historial de abajo hacia arriba (nuevo abajo)
for autor, msg in st.session_state.chat_history:
    is_edith = (autor == "EDITH")
    with st.chat_message("assistant" if is_edith else "user", avatar="👓" if is_edith else "👤"):
        st.write(f"**{autor}:** {msg}")
st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER FIJO (Botón de voz) ---
st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    audio_data = mic_recorder(
        start_prompt="HABLAR AHORA",
        stop_prompt="ESCUCHANDO...",
        key='recorder',
        just_once=True,
        use_container_width=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# --- INPUT DE TEXTO (Fuera del div para que Streamlit lo detecte) ---
texto_manual = st.chat_input("Escriba un comando para E.D.I.T.H.")

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
            messages=[
                {"role": "system", "content": "Eres EDITH. Responde muy corto y profesional."},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.1-8b-instant"
        )
        ans = res.choices[0].message.content
        st.session_state.chat_history.append(("Francis", user_text))
        st.session_state.chat_history.append(("EDITH", ans))

        # Generar audio
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
    except Exception as e:
        st.error(f"Error de conexión: {e}")
