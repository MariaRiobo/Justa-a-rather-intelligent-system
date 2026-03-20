import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- CSS: ANCLAJE TÁCTICO STARK ---
st.markdown("""
    <style>
    /* Fondo y Reset */
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"] { display: none; }

    /* HEADER FIJO */
    .header-stark {
        position: fixed;
        top: 0; left: 0; width: 100%;
        height: 120px;
        background-color: black;
        z-index: 1000;
        text-align: center;
        border-bottom: 1px solid #00d4ff;
        padding-top: 15px;
    }
    .orb-stark {
        width: 45px; height: 45px;
        background: radial-gradient(circle, #00d4ff 0%, #000 75%);
        border-radius: 50%; margin: 0 auto;
        box-shadow: 0 0 15px #00d4ff;
    }

    /* FOOTER FIJO (Para el Micrófono) */
    .footer-stark {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        height: 160px;
        background-color: black;
        z-index: 999;
        border-top: 1px solid #00d4ff;
        padding: 15px 0;
    }

    /* ÁREA DE CHAT (Margen para no chocar) */
    .stChatMessageContainer {
        padding-top: 130px !important;
        padding-bottom: 180px !important;
    }

    /* BOTÓN HABLAR */
    .stButton > button {
        width: 100% !important;
        background-color: #000 !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 30px !important;
        font-weight: bold !important;
        letter-spacing: 2px;
    }

    /* BARRA DE ESCRITURA (Anclaje nativo forzado) */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 20px !important;
        z-index: 1001 !important;
    }

    /* Burbujas de Chat */
    .stChatMessage {
        background: rgba(8, 18, 23, 0.9) !important;
        border: 1px solid #00d4ff !important;
    }

    audio { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ELEMENTOS FIJOS: CABECERA ---
st.markdown("""
    <div class="header-stark">
        <div class="orb-stark"></div>
        <h2 style='margin: 0; letter-spacing: 5px;'>E.D.I.T.H.</h2>
        <p style='font-size: 0.7em; opacity: 0.6;'>PROTOCOLOS DE SEGURIDAD ACTIVOS</p>
    </div>
    """, unsafe_allow_html=True)

# --- CONEXIÓN GROQ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- HISTORIAL (Solo el medio se mueve) ---
for autor, msg in st.session_state.chat_history:
    avatar = "👓" if autor == "EDITH" else "👤"
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar=avatar):
        st.write(f"**{autor}:** {msg}")

# --- ELEMENTOS FIJOS: PIE DE PÁGINA ---
st.markdown('<div class="footer-stark">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1,2,1])
with c2:
    audio_data = mic_recorder(
        start_prompt="HABLAR AHORA",
        stop_prompt="ESCUCHANDO...",
        key='recorder',
        just_once=True,
        use_container_width=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# Barra de escritura (Streamlit la ancla sola, pero con el CSS aseguramos su lugar)
texto_manual = st.chat_input("Escribe tu comando...")

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
            messages=[{"role": "system", "content": "Eres EDITH. Responde de forma ejecutiva y breve."}, {"role": "user", "content": user_text}],
            model="llama-3.1-8b-instant"
        )
        ans = res.choices[0].message.content
        st.session_state.chat_history.append(("Francis", user_text))
        st.session_state.chat_history.append(("EDITH", ans))

        # Sistema de Voz
        tts = gTTS(text=ans, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        b64 = base64.b64encode(audio_fp.read()).decode()
        st.session_state.audio_key += 1
        
        # Audio autoplay
        audio_html = f'<audio autoplay><source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
        st.rerun()
    except Exception as e:
        st.error(f"Error de enlace: {e}")
