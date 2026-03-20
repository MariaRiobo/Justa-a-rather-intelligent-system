import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN STARK ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"] { display: none; }
    .orb {
        width: 60px; height: 60px;
        background: radial-gradient(circle, #00d4ff 0%, #000 75%);
        border-radius: 50%; margin: 10px auto;
        box-shadow: 0 0 20px #00d4ff;
    }
    .stButton>button {
        background-color: #000 !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 20px !important;
        width: 100%;
        font-weight: bold;
    }
    /* Mantenemos el reproductor visible pero pequeño para forzar la carga */
    audio { width: 100%; height: 30px; filter: invert(1); opacity: 0.5; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="orb"></div>', unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #00d4ff; letter-spacing: 3px;'>E.D.I.T.H.</h2>", unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- CONTROLES DE ENTRADA ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    audio_data = mic_recorder(
        start_prompt="HABLAR AHORA",
        stop_prompt="ESCUCHANDO...",
        key='recorder',
        just_once=True,
        use_container_width=True
    )

texto_manual = st.chat_input("Comando...")

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
        messages=[{"role": "system", "content": "Eres EDITH. Responde muy corto."}, {"role": "user", "content": user_text}],
        model="llama-3.1-8b-instant"
    )
    ans = res.choices[0].message.content
    st.session_state.chat_history.append(("Francis", user_text))
    st.session_state.chat_history.append(("EDITH", ans))

    # --- GENERAR VOZ ---
    tts = gTTS(text=ans, lang='es')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    st.session_state.last_audio = audio_fp.getvalue()
    st.rerun()

# --- RENDERIZADO DE HISTORIAL Y AUDIO ---
for autor, msg in reversed(st.session_state.chat_history):
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar="👓" if autor == "EDITH" else "👤"):
        st.write(f"**{autor}:** {msg}")
        # Si es el último mensaje de EDITH, ponemos el audio justo debajo
        if autor == "EDITH" and st.session_state.last_audio:
            st.audio(st.session_state.last_audio, format="audio/mpeg", autoplay=True)
            # Limpiamos para que no se repita infinitamente al recargar
            st.session_state.last_audio = None
