import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="E.D.I.T.H. - Interfaz Táctica", page_icon="👓", layout="centered", initial_sidebar_state="collapsed")

# --- CSS MAESTRO: ESTILO HOLOGRÁFICO CON SEPARACIÓN ---
st.markdown("""
    <style>
    /* 1. Fondo y Texto Base (Dark Mode Stark) */
    .stApp {
        background-color: #050a0e;
        color: #e0f7fa;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* 2. Avatar Animado (El Corazón de EDITH) */
    .edith-orb {
        display: block;
        margin: 20px auto;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(0,212,255,1) 0%, rgba(8,18,23,1) 70%);
        border-radius: 50%;
        box-shadow: 0 0 30px #00d4ff, 0 0 60px #00d4ff;
        animation: pulse 3s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 30px #00d4ff; }
        70% { transform: scale(1.05); box-shadow: 0 0 50px #00d4ff, 0 0 20px #e0f7fa; }
        100% { transform: scale(0.95); box-shadow: 0 0 30px #00d4ff; }
    }

    /* 3. Estilo del Chat (Holográfico y Separado) */
    .stChatMessage {
        border-radius: 15px !important;
        border: 1px solid #00d4ff !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
        margin-bottom: 20px !important;
        padding: 15px !important;
    }
    
    /* Mensajes de EDITH (Izquierda - Cian) */
    .stChatMessage[data-testid="stChatMessage"] {
        background-color: rgba(8, 18, 23, 0.9) !important;
    }
    .stChatMessage[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] {
        border: 2px solid #00d4ff;
    }

    /* Mensajes de Francis (Derecha - Cyan Suave) */
    .stChatMessage[data-testid="stChatMessageOther"] {
        background-color: rgba(0, 212, 255, 0.1) !important;
        border-color: rgba(0, 212, 255, 0.5) !important;
    }
    .stChatMessage[data-testid="stChatMessageOther"] [data-testid="stChatMessageAvatar"] {
        border: 2px solid rgba(0, 212, 255, 0.5);
    }
    
    .stChatMessage [data-testid="stMarkdownContainer"] p {
        color: #e0f7fa !important;
        font-weight: 300;
    }

    /* 4. Barra Inferior Fija (Donde vive el botón) */
    [data-testid="stVerticalBlock"] > div:last-child {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(5, 10, 14, 0.95);
        border-top: 2px solid #00d4ff;
        padding: 15px 10px 30px 10px;
        z-index: 100;
        box-shadow: 0 -10px 20px rgba(0, 212, 255, 0.3);
    }
    
    /* Espacio para que el chat no quede tapado */
    [data-testid="stVerticalBlock"] {
        padding-bottom: 150px !important;
    }

    /* 5. Estilo Profesional del Botón */
    .stButton>button { 
        border-radius: 50px; 
        height: 3.5em; 
        width: 100%;
        border: 2px solid #00d4ff; 
        background-color: #081217; 
        color: #00d4ff; 
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0px 0px 15px rgba(0, 212, 255, 0.5);
    }
    
    .stButton>button:hover {
        background-color: #00d4ff;
        color: #081217;
        box-shadow: 0px 0px 30px #00d4ff;
    }
    
    /* Reproductor de audio INVISIBLE */
    audio { display: none !important; }

    /* Ocultar elementos innecesarios de Streamlit */
    [data-testid="stHeader"], [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA VISUAL ---
st.markdown('<div class="edith-orb"></div>', unsafe_allow_html=True)
st.write("<div style='text-align: center; color: #00d4ff; font-weight: 200;'>SISTEMAS E.D.I.T.H. OPERATIVOS</div>", unsafe_allow_html=True)
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

# --- HISTORIAL VISUAL (Con Separación Stark) ---
# Usamos un contenedor para que el chat escrolee por detrás de la barra fija
chat_container = st.container()
with chat_container:
    # Mostramos el chat en orden inverso (más nuevo arriba)
    for autor, mensaje in st.session_state.chat_history[::-1]:
        is_edith = (autor == "EDITH")
        # Usamos avatar="👓" para EDITH y "👤" para Francis
        with st.chat_message("assistant" if is_edith else "user", avatar="👓" if is_edith else "👤"):
            st.write(f"**{autor}:** {mensaje}")

# --- BARRA INFERIOR FIJA CON EL BOTÓN ---
with st.container():
    # Usamos columnas para centrar el botón
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        audio_data = mic_recorder(
            start_prompt="🔴 INICIAR ESCANEO",
            stop_prompt="🟢 PROCESAR COMANDO",
            key='recorder',
            just_once=True,
            use_container_width=True
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
