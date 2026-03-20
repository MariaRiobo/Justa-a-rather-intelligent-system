import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN ---
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
    .stChatMessage {
        background: rgba(8, 18, 23, 0.9) !important;
        border: 1px solid #00d4ff !important;
    }
    .stButton>button {
        background-color: #000 !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 20px !important;
        width: 100%;
    }
    /* Ocultar reproductores */
    audio { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="orb"></div>', unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #00d4ff; letter-spacing: 3px;'>E.D.I.T.H.</h2>", unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- HISTORIAL ---
for autor, msg in st.session_state.chat_history:
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar="👓" if autor == "EDITH" else "👤"):
        st.write(f"**{autor}:** {msg}")

# --- CONTROLES ---
st.write("---")
audio_data = mic_recorder(start_prompt="HABLAR AHORA", stop_prompt="ESCUCHANDO...", key='recorder', just_once=True, use_container_width=True)
texto_manual = st.chat_input("Comando...")

# --- PROCESAMIENTO Y VOZ ---
user_text = None
if audio_data:
    try:
        transcription = client.audio.transcriptions.create(file=("audio.webm", audio_data['bytes']), model="whisper-large-v3")
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

    # Generar Audio
    tts = gTTS(text=ans, lang='es')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    b64 = base64.b64encode(audio_fp.read()).decode()
    
    st.session_state.audio_key += 1
    
    # SCRIPT DE AUDIO FORZADO (JavaScript)
    # Esto crea el audio y le da a "Play" inmediatamente mediante código
    audio_html = f"""
        <audio id="edith_voice_{st.session_state.audio_key}" src="data:audio/mpeg;base64,{b64}"></audio>
        <script>
            var audio = document.getElementById("edith_voice_{st.session_state.audio_key}");
            audio.play().catch(function(error) {{
                console.log("El navegador bloqueó el autoplay. Haz clic en la pantalla.");
            }});
        </script>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    st.rerun()
