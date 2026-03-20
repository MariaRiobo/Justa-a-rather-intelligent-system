import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- CSS MAESTRO: ANCLAJE TOTAL Y SCROLL INTERNO ---
st.markdown("""
    <style>
    /* Fondo General */
    .stApp { background-color: #000000; color: #00d4ff; overflow: hidden; }
    [data-testid="stHeader"] { display: none; }

    /* 1. ENCABEZADO FIJO */
    .fixed-header {
        position: fixed;
        top: 0; left: 0; width: 100%;
        height: 140px;
        background-color: black;
        z-index: 1000;
        text-align: center;
        padding-top: 20px;
        border-bottom: 1px solid rgba(0, 212, 255, 0.4);
    }
    .orb {
        width: 45px; height: 45px;
        background: radial-gradient(circle, #00d4ff 0%, #000 70%);
        border-radius: 50%; margin: 0 auto;
        box-shadow: 0 0 15px #00d4ff;
        animation: pulse 3s infinite;
    }

    /* 2. CONTENEDOR DE HISTORIAL (EL ÚNICO QUE SE MUEVE) */
    .main-chat-container {
        position: fixed;
        top: 140px; /* Debajo del header */
        bottom: 160px; /* Encima del footer */
        left: 0; width: 100%;
        overflow-y: auto; /* Scroll solo aquí */
        padding: 20px;
        display: flex;
        flex-direction: column;
    }

    /* 3. PIE DE PÁGINA FIJO (CONTROL) */
    .fixed-footer {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        height: 160px;
        background: black;
        z-index: 1000;
        border-top: 1px solid rgba(0, 212, 255, 0.4);
        padding: 10px 0;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* Estilo del Botón "Hablar Ahora" */
    .stButton>button {
        background-color: transparent !important;
        border: 2px solid #00d4ff !important;
        color: #00d4ff !important;
        border-radius: 30px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    }
    
    /* Input de Texto */
    .stChatInputContainer {
        padding-bottom: 20px !important;
    }

    /* Animación del Orbe */
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }
    
    audio { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ANCLADA ---
st.markdown("""
    <div class="fixed-header">
        <div class="orb"></div>
        <h2 style='margin: 5px 0; letter-spacing: 5px;'>E.D.I.T.H.</h2>
        <p style='font-size: 0.7em; opacity: 0.8;'>SISTEMAS ARMÓNICOS</p>
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- HISTORIAL (ZONA DE SCROLL) ---
# Usamos un div contenedor con la clase CSS para el scroll
st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)
for autor, msg in st.session_state.chat_history:
    is_edith = (autor == "EDITH")
    with st.chat_message("assistant" if is_edith else "user", avatar="👓" if is_edith else "👤"):
        st.write(f"**{autor}:** {msg}")
st.markdown('</div>', unsafe_allow_html=True)

# --- PIE DE PÁGINA ANCLADO ---
st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1,3,1])
with col2:
    audio_data = mic_recorder(
        start_prompt="HABLAR AHORA",
        stop_prompt="ESCUCHANDO...",
        key='recorder',
        just_once=True,
        use_container_width=True
    )
    # Chat input nativo ( Streamlit lo posiciona relativo al contenedor, pero con CSS lo fijamos)
    texto_manual = st.chat_input("Escribe un comando...")
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
            messages=[{"role": "system", "content": "Eres EDITH. Responde muy corto."}, {"role": "user", "content": user_text}],
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
