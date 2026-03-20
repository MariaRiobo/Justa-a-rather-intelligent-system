import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓")

# --- CSS: ESTÉTICA STARK ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"] { display: none; }
    
    .orb-container { display: flex; flex-direction: column; align-items: center; padding: 10px; }
    .orb {
        width: 60px; height: 60px;
        background: radial-gradient(circle, #00d4ff 0%, #000 75%);
        border-radius: 50%; box-shadow: 0 0 20px #00d4ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    /* Botón Hablar Ahora */
    .stButton > button {
        background-color: #000 !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 20px !important;
        width: 100% !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }

    .stChatMessage {
        background: rgba(8, 18, 23, 0.9) !important;
        border: 1px solid #00d4ff !important;
    }
    
    audio { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="orb-container"><div class="orb"></div><h2 style="letter-spacing:5px;">E.D.I.T.H.</h2></div>', unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
audio_placeholder = st.empty() # Espacio reservado para inyectar el audio

# --- HISTORIAL ---
for autor, msg in st.session_state.chat_history:
    avatar = "👓" if autor == "EDITH" else "👤"
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar=avatar):
        st.write(f"**{autor}:** {msg}")

# --- CONTROLES ---
st.write("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    audio_data = mic_recorder(
        start_prompt="HABLAR AHORA",
        stop_prompt="ESCUCHANDO...",
        key='recorder',
        just_once=True,
        use_container_width=True
    )

texto_manual = st.chat_input("Ingrese comando táctico...")

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
        # 1. Generar Respuesta
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "Eres EDITH. Responde corto."}, {"role": "user", "content": user_text}],
            model="llama-3.1-8b-instant"
        )
        respuesta = res.choices[0].message.content
        
        # 2. Actualizar Historial
        st.session_state.chat_history.append(("Francis", user_text))
        st.session_state.chat_history.append(("EDITH", respuesta))

        # 3. GENERACIÓN DE AUDIO FORZADA (Tu código integrado)
        tts = gTTS(text=respuesta, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        audio_b64 = base64.b64encode(audio_fp.read()).decode()
        
        st.session_state.audio_key += 1
        
        audio_html = f"""
            <audio autoplay key="{st.session_state.audio_key}">
                <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
            </audio>
        """
        # Inyectamos el audio y refrescamos para mostrar los mensajes
        audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
        st.rerun()
        
    except Exception as e:
        st.error(f"Error: {e}")
