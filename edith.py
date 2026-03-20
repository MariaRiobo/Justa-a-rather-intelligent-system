import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- CSS MAESTRO: INTERFAZ STARK & MICRÓFONO HOLOGRÁFICO ---
st.markdown("""
    <style>
    /* 1. Fondo y Texto Base (Dark Mode Stark) */
    .stApp {
        background-color: #050a0e;
        color: #e0f7fa;
    }

    /* 2. Chat y Mensajes (Separado y Fluyente) */
    .stChatMessage {
        border-radius: 15px !important;
        border: 1px solid #00d4ff !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
        margin-bottom: 20px !important;
        padding: 15px !important;
        background-color: rgba(8, 18, 23, 0.9) !important;
    }
    .stChatMessage [data-testid="stChatMessageAvatar"] {
        border: 2px solid #00d4ff;
    }

    /* Mensajes de Francis (Derecha - Cyan Suave) */
    .stChatMessageOther {
        background-color: rgba(0, 212, 255, 0.1) !important;
        border-color: rgba(0, 212, 255, 0.5) !important;
    }
    
    .stChatMessageOther [data-testid="stChatMessageAvatar"] {
        border: 2px solid rgba(0, 212, 255, 0.5);
    }
    
    .stChatMessage [data-testid="stMarkdownContainer"] p {
        color: #e0f7fa !important;
        font-weight: 300;
    }

    /* 3. El Micrófono de Neón Táctil (Central y Fluyente) */
    .stButton>button { 
        width: 100px; height: 100px;
        border-radius: 50% !important;
        border: none;
        background-color: #081217;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.5), inset 0 0 10px rgba(0, 212, 255, 0.3);
        animation: pulse 3s infinite;
        cursor: pointer;
        padding: 0;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    /* Efecto Pulsante */
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 20px rgba(0, 212, 255, 0.5); }
        70% { transform: scale(1.05); box-shadow: 0 0 40px rgba(0, 212, 255, 1), 0 0 15px #e0f7fa; }
        100% { transform: scale(0.95); box-shadow: 0 0 20px rgba(0, 212, 255, 0.5); }
    }
    
    /* Cambiar a micrófono de neón cian al pulsar/mantener */
    .stButton>button:active {
        background-color: #00d4ff !important;
        box-shadow: 0 0 60px #00d4ff !important;
    }
    
    /* Ocultar el texto por completo */
    .stButton>button span { display: none !important; }

    /* Ocultar elementos innecesarios */
    audio { display: none !important; }
    [data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA VISUAL ---
st.write("<div style='text-align: center; color: #00d4ff; font-weight: 200;'>SISTEMAS E.D.I.T.H.</div>", unsafe_allow_html=True)
st.write("<div style='text-align: center; font-size: 0.9em; margin-bottom: 30px;'>Francis, te escucho.</div>", unsafe_allow_html=True)

# --- CONEXIÓN GROQ ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Error: GROQ_API_KEY no encontrada.")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- HISTORIAL VISUAL (Fluyente y Separado) ---
chat_container = st.container()
with chat_container:
    # Mostramos el chat en orden inverso (más nuevo arriba)
    for autor, mensaje in st.session_state.chat_history[::-1]:
        is_edith = (autor == "EDITH")
        # Usamos avatar="👓" para EDITH y "👤" para Francis
        with st.chat_message("assistant" if is_edith else "user", avatar="👓" if is_edith else "👤"):
            st.write(f"**{autor}:** {mensaje}")

# --- ENTRADA DE VOZ (Micrófono Táctil Central) ---
st.write("---") # Separador visual
st.write("<p style='text-align:center; font-size:0.8em; opacity:0.6; margin-bottom:0;'>Habla ahora</p>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([2,1,2]) # Centramos el orbe
with col2:
    # El Botón de la grabadora es ahora el micrófono de neón
    audio_data = mic_recorder(
        # Usamos el orbe de neón *como* el botón táctil del micrófono
        start_prompt="🔴 INICIAR ESCANEO",
        stop_prompt="🟢 PROCESAR COMANDO",
        key='recorder',
        just_once=True,
        use_container_width=False # El orbe es pequeño
    )

# --- LÓGICA DE PROCESAMIENTO ---
user_text = None
if audio_data:
    with st.spinner("Analizando frecuencia..."):
        try:
            transcription = client.audio.transcriptions.create(
              file=("audio.webm", audio_data['bytes']),
              model="whisper-large-v3"
            )
            user_text = transcription.text
        except Exception: pass

if user_text:
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres EDITH, la IA de Stark. Tu usuario es Francis. Responde corto y ejecutivo."},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.1-8b-instant",
        )
        respuesta_texto = chat_completion.choices[0].message.content
        
        st.session_state.chat_history.append(("Francis", user_text))
        st.session_state.chat_history.append(("EDITH", respuesta_texto))
        
        # --- SISTEMA DE VOZ INVISIBLE (CON LLAVE ÚNICA) ---
        tts = gTTS(text=respuesta_texto, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_b64 = base64.b64encode(audio_fp.read()).decode()
        
        st.session_state.audio_key += 1
        
        # Inyectamos el audio invisible con autoplay y script forzado
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
        
        # Recarga rápida para mover el historial
        st.rerun()
        
    except Exception as e:
        st.error(f"Error en enlace satelital: {e}")
