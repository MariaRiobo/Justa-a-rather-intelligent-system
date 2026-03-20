import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓")

# --- CSS ESTABLE (Sin bloqueos de pantalla) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"] { display: none; }
    
    /* El Orbe de E.D.I.T.H. */
    .orb {
        width: 80px; height: 80px;
        background: radial-gradient(circle, #00d4ff 0%, #000 70%);
        border-radius: 50%; margin: 20px auto;
        box-shadow: 0 0 20px #00d4ff;
    }
    
    /* Estilo de los mensajes */
    .stChatMessage {
        background: rgba(8, 18, 23, 0.9) !important;
        border: 1px solid #00d4ff !important;
        border-radius: 15px !important;
        color: #e0f7fa !important;
    }

    /* Botón de Hablar con estilo de la página */
    .stButton>button {
        background-color: #000 !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 20px !important;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER VISUAL ---
st.markdown('<div class="orb"></div>', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #00d4ff; letter-spacing: 5px;'>E.D.I.T.H.</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.7;'>SISTEMAS OPERATIVOS</p>", unsafe_allow_html=True)

# --- CONEXIÓN ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- HISTORIAL (Orden Natural) ---
for autor, msg in st.session_state.chat_history:
    avatar = "👓" if autor == "EDITH" else "👤"
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar=avatar):
        st.write(f"**{autor}:** {msg}")

# --- CONTROLES (Al final de la página) ---
st.write("---") # Una línea divisoria sutil
audio_data = mic_recorder(
    start_prompt="HABLAR AHORA",
    stop_prompt="ESCUCHANDO...",
    key='recorder',
    just_once=True,
    use_container_width=True
)

texto_manual = st.chat_input("Escribe tu comando aquí...")

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

        # Voz
        tts = gTTS(text=ans, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        b64 = base64.b64encode(audio_fp.read()).decode()
        st.session_state.audio_key += 1
        
        # Audio HTML simple (el más fiable)
        audio_html = f'<audio autoplay><source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
        
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
