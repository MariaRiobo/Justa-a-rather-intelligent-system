import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00d4ff; }
    .stButton>button { 
        border-radius: 50px; border: 2px solid #00d4ff; 
        background-color: #081217; color: white; box-shadow: 0px 0px 15px #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👓 E.D.I.T.H.")
st.write("Sistemas en línea. Francis, te escucho.")

# --- CONEXIÓN ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- LUGAR PARA EL AUDIO (Súper importante) ---
audio_placeholder = st.empty()

# --- ENTRADA ---
audio_data = mic_recorder(start_prompt="🔴 HABLAR", stop_prompt="🟢 ENVIAR", key='recorder', just_once=True)
texto_manual = st.chat_input("Escribe aquí...")

user_text = None
if audio_data:
    try:
        transcription = client.audio.transcriptions.create(file=("audio.webm", audio_data['bytes']), model="whisper-large-v3")
        user_text = transcription.text
    except: pass
elif texto_manual:
    user_text = texto_manual

if user_text:
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres EDITH, la IA de Stark. Tu usuario es Francis. Responde corto y ejecutivo."},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.1-8b-instant",
        )
        respuesta = chat_completion.choices[0].message.content
        
        st.session_state.chat_history.append(("Francis", user_text))
        st.session_state.chat_history.append(("EDITH", respuesta))

        # --- GENERACIÓN DE AUDIO FORZADA ---
        tts = gTTS(text=respuesta, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        audio_b64 = base64.b64encode(audio_fp.read()).decode()
        
        # Incrementamos la llave para que Streamlit crea que es un objeto nuevo
        st.session_state.audio_key += 1
        
        # Inyectamos el HTML con una ID única cada vez
        audio_html = f"""
            <audio autoplay key="{st.session_state.audio_key}">
                <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
            </audio>
        """
        audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error: {e}")

# --- HISTORIAL ---
for autor, mensaje in st.session_state.chat_history[::-1]:
    with st.chat_message("assistant" if autor == "EDITH" else "user"):
        st.write(f"**{autor}:** {mensaje}")
