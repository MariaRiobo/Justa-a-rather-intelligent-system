import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- CSS PROFESIONAL (Sin bloqueos) ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0f7fa; }
    
    /* El Corazón de EDITH */
    .edith-orb {
        width: 80px; height: 80px;
        background: radial-gradient(circle, #00d4ff 0%, #081217 70%);
        border-radius: 50%;
        margin: 10px auto;
        box-shadow: 0 0 20px #00d4ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 40px #00d4ff; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }
    
    /* Botones y Chat */
    .stButton>button { 
        border-radius: 20px; border: 1px solid #00d4ff; 
        background: #081217; color: #00d4ff; font-weight: bold;
        width: 100%; height: 3em;
    }
    .stChatMessage { 
        background: rgba(8, 18, 23, 0.9) !important; 
        border: 1px solid #00d4ff !important; 
        border-radius: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# UI Principal
st.markdown('<div class="edith-orb"></div>', unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #00d4ff;'>E.D.I.T.H.</h3>", unsafe_allow_html=True)

# --- LÓGICA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- ENTRADA (Ubicación segura) ---
audio_data = mic_recorder(
    start_prompt="🔴 INICIAR COMANDO",
    stop_prompt="🟢 PROCESAR",
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
    except Exception as e: st.error(f"Error audio: {e}")

if user_text:
    try:
        # IA Response
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

        # Audio de respuesta
        tts = gTTS(text=ans, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        b64 = base64.b64encode(audio_fp.read()).decode()
        
        # Reproductor invisible que se activa solo
        md = f"""
            <audio autoplay>
            <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
        
    except Exception as e: st.error(f"Error IA: {e}")

# --- CHAT ---
for autor, msg in st.session_state.chat_history[::-1]:
    with st.chat_message("assistant" if autor == "EDITH" else "user"):
        st.write(f"**{autor}:** {msg}")
