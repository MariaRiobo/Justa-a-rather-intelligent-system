import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- CSS MAESTRO: ESTRUCTURA FIJA STARK ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #e0f7fa; }
    [data-testid="stHeader"] { display: none; }

    /* 1. CABECERA FIJA (ORBE Y SIGLAS) */
    .st-emotion-cache-18ni7ap { /* Contenedor principal */
        padding-top: 170px !important; 
    }
    
    .fixed-header {
        position: fixed;
        top: 0; left: 0; width: 100%;
        background-color: black;
        z-index: 1000;
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid rgba(0, 212, 255, 0.3);
    }
    
    .edith-orb-top {
        width: 60px; height: 60px;
        background: radial-gradient(circle, #00d4ff 0%, #000 70%);
        border-radius: 50%; margin: 0 auto;
        box-shadow: 0 0 20px #00d4ff;
        animation: pulse 3s infinite;
    }

    /* 2. CONTROL INFERIOR FIJO (MIC Y INPUT) */
    .fixed-footer {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background: linear-gradient(to top, black 80%, transparent);
        z-index: 1000;
        padding: 10px 0 30px 0;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* Estilo del Micrófono (Orbe pequeño) */
    .stButton>button {
        width: 70px !important; height: 70px !important;
        border-radius: 50% !important;
        border: 2px solid #00d4ff !important;
        background: #081217 !important;
        box-shadow: 0 0 15px #00d4ff !important;
        color: #00d4ff !important;
        font-size: 25px !important;
        margin-bottom: 10px;
    }

    /* 3. CHAT (Holograma) */
    .stChatMessage {
        background: rgba(8, 18, 23, 0.8) !important;
        border: 1px solid #00d4ff !important;
        border-radius: 15px !important;
        margin-bottom: 10px !important;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }
    
    audio { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ELEMENTOS FIJOS: CABECERA ---
st.markdown("""
    <div class="fixed-header">
        <div class="edith-orb-top"></div>
        <h2 style='color: #00d4ff; margin: 5px 0; letter-spacing: 3px;'>E.D.I.T.H.</h2>
        <p style='font-size: 0.8em; opacity: 0.6;'>SISTEMAS ACTIVOS</p>
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- HISTORIAL (Actualización de abajo hacia arriba) ---
# Al iterar normalmente, el más nuevo queda al final (abajo)
for autor, msg in st.session_state.chat_history:
    is_edith = (autor == "EDITH")
    with st.chat_message("assistant" if is_edith else "user", avatar="👓" if is_edith else "👤"):
        st.write(f"**{autor}:** {msg}")

# --- ELEMENTOS FIJOS: PIE DE PÁGINA (Micrófono y Barra) ---
st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2,1,2])
with col2:
    audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⌛", key='recorder', just_once=True)

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
    res = client.chat.completions.create(
        messages=[{"role": "system", "content": "Eres EDITH. Responde corto."}, {"role": "user", "content": user_text}],
        model="llama-3.1-8b-instant"
    )
    ans = res.choices[0].message.content
    
    st.session_state.chat_history.append(("Francis", user_text))
    st.session_state.chat_history.append(("EDITH", ans))

    # Voz
    tts = gTTS(text=ans, lang='es')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    b64 = base64.b64encode(audio_fp.read()).decode()
    st.session_state.audio_key += 1
    
    audio_html = f'''
        <audio id="a_{st.session_state.audio_key}" autoplay><source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg"></audio>
        <script>document.getElementById("a_{st.session_state.audio_key}").play();</script>
    '''
    st.markdown(audio_html, unsafe_allow_html=True)
    st.rerun()
