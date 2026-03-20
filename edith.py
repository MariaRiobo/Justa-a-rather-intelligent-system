import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- CSS STARK ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0f7fa; }
    .edith-orb {
        width: 80px; height: 80px;
        background: radial-gradient(circle, #00d4ff 0%, #081217 70%);
        border-radius: 50%; margin: 10px auto;
        box-shadow: 0 0 20px #00d4ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 40px #00d4ff; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }
    .stButton>button { 
        border-radius: 20px; border: 1px solid #00d4ff; 
        background: #081217; color: #00d4ff; font-weight: bold;
        width: 100%; height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="edith-orb"></div>', unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #00d4ff;'>E.D.I.T.H.</h3>", unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# --- ENTRADA DE COMANDOS ---
audio_data = mic_recorder(
    start_prompt="🔴 INICIAR COMANDO",
    stop_prompt="🟢 ENVIAR",
    key='recorder',
    just_once=True,
    use_container_width=True
)

user_text = None
if audio_data:
    try:
        with st.spinner("Transcribiendo..."):
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
                {"role": "system", "content": "Eres EDITH, la IA de Stark. Tu usuario es Francis. Responde muy corto y profesional."},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.1-8b-instant"
        )
        ans = res.choices[0].message.content
        
        st.session_state.chat_history.append(("Francis", user_text))
        st.session_state.chat_history.append(("EDITH", ans))

        # --- GENERACIÓN DE AUDIO (NUEVA LÓGICA) ---
        tts = gTTS(text=ans, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        b64 = base64.b64encode(audio_fp.read()).decode()
        
        # Guardamos el audio en el estado de la sesión con un ID de tiempo
        st.session_state.last_audio = (b64, time.time())
        
    except Exception as e: st.error(f"Error: {e}")

# --- REPRODUCTOR DE AUDIO DINÁMICO ---
if st.session_state.last_audio:
    b64_data, timestamp = st.session_state.last_audio
    # El ID único del elemento audio fuerza al iPhone a cargarlo siempre
    audio_html = f"""
        <audio autoplay id="player_{timestamp}">
            <source src="data:audio/mpeg;base64,{b64_data}" type="audio/mpeg">
        </audio>
        <script>
            var player = document.getElementById("player_{timestamp}");
            player.play().catch(e => console.log("Bloqueo de Safari"));
        </script>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# --- HISTORIAL ---
for autor, msg in st.session_state.chat_history[::-1]:
    with st.chat_message("assistant" if autor == "EDITH" else "user"):
        st.write(f"**{autor}:** {msg}")
