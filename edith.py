import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0f7fa; }
    
    /* El Corazón de EDITH */
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
    
    /* Botón Profesional */
    .stButton>button { 
        border-radius: 20px; border: 1px solid #00d4ff; 
        background: #081217; color: #00d4ff; font-weight: bold;
        width: 100%; height: 3.5em; text-transform: uppercase;
    }
    
    /* Mensajes Holográficos */
    .stChatMessage { 
        background: rgba(8, 18, 23, 0.9) !important; 
        border: 1px solid #00d4ff !important; 
        border-radius: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado Visual
st.markdown('<div class="edith-orb"></div>', unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #00d4ff; letter-spacing: 2px;'>SISTEMAS E.D.I.T.H.</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 0.9em; opacity: 0.8;'>Protocolos de comunicación activos, Francis.</p>", unsafe_allow_html=True)

# --- CONEXIÓN ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- ENTRADA DE VOZ ---
audio_data = mic_recorder(
    start_prompt="🔴 INICIAR ESCANEO DE VOZ",
    stop_prompt="🟢 PROCESAR COMANDO",
    key='recorder',
    just_once=True,
    use_container_width=True
)

user_text = None
if audio_data:
    with st.spinner("Descifrando audio..."):
        try:
            transcription = client.audio.transcriptions.create(
                file=("audio.webm", audio_data['bytes']),
                model="whisper-large-v3"
            )
            user_text = transcription.text
        except Exception as e: st.error(f"Error: {e}")

# --- PROCESAMIENTO ---
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
        
    except Exception as e: st.error(f"Error IA: {e}")

# --- MOSTRAR CHAT Y AUDIO ---
for autor, msg in st.session_state.chat_history[::-1]:
    is_edith = (autor == "EDITH")
    with st.chat_message("assistant" if is_edith else "user", avatar="👓" if is_edith else "👤"):
        st.write(f"**{autor}:** {msg}")
        
        # Si es el mensaje más reciente de EDITH, generamos el reproductor
        if is_edith and msg == st.session_state.chat_history[-1][1]:
            tts = gTTS(text=msg, lang='es')
            audio_fp = BytesIO()
            tts.write_to_fp(audio_fp)
            # El reproductor estándar es el que mejor funciona en iPhone
            st.audio(audio_fp, format='audio/mp3')
