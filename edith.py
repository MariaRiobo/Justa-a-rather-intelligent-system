import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered", initial_sidebar_state="collapsed")

# CSS para Estilo Stark (Dark Mode & Neón)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .stButton>button { 
        border-radius: 50px; height: 3em; border: 2px solid #00d4ff; 
        background-color: #081217; color: white; font-weight: bold;
        box-shadow: 0px 0px 15px #00d4ff;
    }
    .stChatInput { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👓 E.D.I.T.H.")
st.write("Sistemas en línea. Lista para operar, Francis.")

# --- CONEXIÓN SEGURA CON GROQ ---
# Asegúrate de tener GROQ_API_KEY en los Secrets de Streamlit
API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- INTERFAZ DE ENTRADA ---
st.write("### Control por Voz")
audio_data = mic_recorder(
    start_prompt="🔴 INICIAR ESCANEO DE VOZ",
    stop_prompt="🟢 PROCESAR COMANDO",
    key='recorder',
    just_once=True,
    use_container_width=True
)

texto_manual = st.chat_input("O escribe tu comando aquí...")

# --- LÓGICA DE PROCESAMIENTO ---
user_text = None

# 1. Captura de Audio (Whisper)
if audio_data:
    with st.spinner("Descifrando audio..."):
        try:
            transcription = client.audio.transcriptions.create(
              file=("audio.webm", audio_data['bytes']),
              model="whisper-large-v3"
            )
            user_text = transcription.text
        except Exception as e:
            st.error(f"Error de audio: {e}")
            
# 2. Captura de Texto
elif texto_manual:
    user_text = texto_manual

# 3. Respuesta de la IA y Voz
if user_text:
    with st.spinner("Procesando..."):
        try:
            # Personalidad de E.D.I.T.H.
            prompt_sistema = "Eres E.D.I.T.H., la IA de los lentes de Tony Stark. Tu usuario es Francis. Eres ejecutiva, inteligente y muy rápida. Responde de forma concisa."
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": user_text}
                ],
                model="llama-3.1-8b-instant",
            )
            respuesta_texto = chat_completion.choices[0].message.content
            
            # Guardar en historial
            st.session_state.chat_history.append(("Francis", user_text))
            st.session_state.chat_history.append(("EDITH", respuesta_texto))
            
            # --- GENERACIÓN DE VOZ (FIX IPHONE + CONTINUIDAD) ---
            tts = gTTS(text=respuesta_texto, lang='es')
            audio_fp = BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            # Convertimos a Base64 y generamos un ID único basado en el tiempo 
            # Esto obliga al navegador a reproducir cada mensaje nuevo.
            audio_b64 = base64.b64encode(audio_fp.read()).decode()
            unique_id = int(time.time())
            audio_html = f'''
                <audio id="audio_{unique_id}" controls autoplay>
                    <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
                </audio>
                <script>
                    var audio = document.getElementById("audio_{unique_id}");
                    audio.play();
                </script>
            '''
            st.markdown(audio_html, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error en enlace satelital: {e}")

# --- HISTORIAL VISUAL (Orden Inverso) ---
for autor, mensaje in st.session_state.chat_history[::-1]:
    with st.chat_message("assistant" if autor == "EDITH" else "user"):
        st.write(f"**{autor}:** {mensaje}")
