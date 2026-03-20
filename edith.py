import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN ESTÉTICA (Protocolo Sigilo) ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0f7fa; }
    
    /* El Corazón de EDITH */
    .edith-orb {
        width: 100px; height: 100px;
        background: radial-gradient(circle, #00d4ff 0%, #081217 70%);
        border-radius: 50%; margin: 20px auto;
        box-shadow: 0 0 30px #00d4ff;
        animation: pulse 3s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 50px #00d4ff, 0 0 20px #e0f7fa; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }
    
    /* Botón Profesional y Chat */
    .stButton>button { 
        border-radius: 50px; border: 2px solid #00d4ff; 
        background: #081217; color: #00d4ff; font-weight: bold;
        width: 100%; height: 3.5em; text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stChatMessage { 
        background: rgba(8, 18, 23, 0.9) !important; 
        border: 1px solid #00d4ff !important; 
        border-radius: 15px !important;
    }
    
    /* --- EL TRUCO: Reproductor de Audio Invisible --- */
    audio {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0px !important; height: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado Visual
st.markdown('<div class="edith-orb"></div>', unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #00d4ff; letter-spacing: 2px;'>SISTEMAS E.D.I.T.H.</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.1em; opacity: 0.8;'>Francis, te escucho.</p>", unsafe_allow_html=True)

# --- CONEXIÓN ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- ENTRADA DE VOZ ---
st.write("### Control de Voz")
col1, col2, col3 = st.columns([1,3,1])
with col2:
    audio_data = mic_recorder(
        start_prompt="🔴 INICIAR ESCANEO",
        stop_prompt="🟢 PROCESAR",
        key='recorder',
        just_once=True,
        use_container_width=True
    )

# --- PROCESAMIENTO ---
user_text = None
if audio_data:
    with st.spinner("Descifrando audio..."):
        try:
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
        
        # Guardar en historial
        st.session_state.chat_history.append(("Francis", user_text))
        st.session_state.chat_history.append(("EDITH", ans))
        
        # --- GENERACIÓN DE AUDIO INVISIBLE Y FORZADA ---
        tts = gTTS(text=ans, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        # Truco Base64 para iOS
        audio_b64 = base64.b64encode(audio_fp.read()).decode()
        
        # Incrementamos la llave para forzar el reinicio del audio
        st.session_state.audio_key += 1
        
        # Inyectamos el reproductor y lo obligamos a reproducirse por Script
        # Pero el CSS de arriba ya lo hizo invisible
        audio_html = f'''
            <audio id="audio_{st.session_state.audio_key}" controls autoplay class="audio-oculto">
                <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
            </audio>
            <script>
                var audio = document.getElementById("audio_{st.session_state.audio_key}");
                if (audio) {{ audio.play(); }}
            </script>
        '''
        st.markdown(audio_html, unsafe_allow_html=True)
        
    except Exception as e: st.error(f"Error IA: {e}")

# --- MOSTRAR CHAT ---
st.write("---")
st.write("### Historial")
for autor, msg in st.session_state.chat_history[::-1]:
    is_edith = (autor == "EDITH")
    with st.chat_message("assistant" if is_edith else "user", avatar="👓" if is_edith else "👤"):
        st.write(f"**{autor}:** {msg}")
