import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64
import time

# --- CONFIGURACIÓN DE PÁGINA (Táctico) ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered", initial_sidebar_state="collapsed")

# --- CSS MAESTRO: INTERFAZ HOLOGRÁFICA "STARK CHAT" ---
st.markdown("""
    <style>
    /* 1. Fondo y Texto Base (Dark Mode Absoluto) */
    .stApp {
        background-color: #000000;
        color: #e0f7fa;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* 2. Cabecera Visual (Orbe y Título) */
    [data-testid="stHeader"] { display: none; } /* Ocultar el header de streamlit */
    
    .stMainBlockContainer {
        padding-top: 2rem !important;
        padding-bottom: 200px !important; /* Espacio para el chat input fijo abajo */
    }

    /* Orbe de neón central (Efecto Pulsante de la imagen) */
    .stMainBlockContainer::before {
        content: "";
        display: block;
        margin: 0 auto;
        width: 100px; height: 100px;
        background: radial-gradient(circle, rgba(0,212,255,1) 0%, rgba(0,0,0,0) 70%);
        border-radius: 50%;
        box-shadow: 0 0 30px #00d4ff;
        animation: orb-pulse 3s infinite;
        margin-bottom: 20px;
    }
    
    @keyframes orb-pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 20px #00d4ff; }
        70% { transform: scale(1.05); box-shadow: 0 0 40px #00d4ff; }
        100% { transform: scale(0.95); box-shadow: 0 0 20px #00d4ff; }
    }

    /* Título y subtítulo centrado (Igual a la imagen) */
    .stText { text-align: center !important; }
    
    /* 3. Estilo del Chat (Holográfico y Separado) */
    .stChatMessage {
        border-radius: 15px !important;
        border: 1px solid #00d4ff !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
        margin-bottom: 15px !important;
        padding: 10px !important;
    }
    
    /* Mensajes de EDITH (Izquierda - Cian) */
    .stChatMessage[data-testid="stChatMessage"] {
        background-color: rgba(8, 18, 23, 0.9) !important;
    }
    .stChatMessage[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] {
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
        font-size: 0.95em;
    }

    /* 4. Barra Inferior Táctil (Chat Input & Micrófono) */
    /* Congelar la entrada abajo (Fixed bottom) */
    .stChatInputContainer {
        position: fixed;
        bottom: 20px;
        left: 0;
        width: 100%;
        z-index: 100;
        display: flex;
        flex-direction: column;
        align-items: center;
        background-color: rgba(0,0,0,0.8);
        padding-top: 10px;
        border-top: 2px solid #00d4ff;
        box-shadow: 0 -10px 20px rgba(0, 212, 255, 0.3);
    }
    
    /* Estilo profesional para el Chat Input (Barra de escribir) */
    .stChatInput {
        border-radius: 50px;
        border: 1px solid #00d4ff;
        background-color: #081217;
        color: #e0f7fa;
        margin-top: 10px;
        max-width: 600px; /* Centrar y limitar ancho */
    }

    /* 5. El Micrófono de Neón Táctil (Orbe Pulsante) */
    /* Reemplazamos el estilo del botón de la grabadora */
    .stButton>button { 
        width: 80px; height: 80px;
        border-radius: 50% !important;
        border: none;
        background: radial-gradient(circle, rgba(0,212,255,1) 0%, rgba(8,18,23,1) 70%);
        box-shadow: 0 0 20px #00d4ff, 0 0 40px #00d4ff;
        color: transparent; /* Ocultar el texto */
        animation: pulse 3s infinite;
        cursor: pointer;
        padding: 0;
        margin-top: -40px; /* Subir el orbe para que flote sobre la barra */
    }
    
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 20px #00d4ff; }
        70% { transform: scale(1.05); box-shadow: 0 0 40px #00d4ff, 0 0 15px #e0f7fa; }
        100% { transform: scale(0.95); box-shadow: 0 0 20px #00d4ff; }
    }
    
    .stButton>button:hover {
        background: radial-gradient(circle, rgba(0,212,255,1) 0%, rgba(0,212,255,0.5) 70%);
        box-shadow: 0 0 60px #00d4ff;
    }
    
    /* Ocultar el texto del botón por completo */
    .stButton>button span { display: none !important; }

    /* Reproductor de audio INVISIBLE */
    audio { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA VISUAL (Estilo Imagen) ---
st.markdown("<h2 style='text-align: center; color: #00d4ff; letter-spacing: 2px; font-size: 1.5em; margin-bottom: 0;'>SISTEMAS E.D.I.T.H. OPERATIVOS</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 0.9em; opacity: 0.8; margin-bottom: 30px;'>Francis, te escucho.</p>", unsafe_allow_html=True)

# --- CONEXIÓN GROQ ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception:
    st.error("Error: GROQ_API_KEY no encontrada.")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- HISTORIAL VISUAL (Correcto: Flujo de abajo a arriba) ---
# Usamos un contenedor para que el chat escrolee
chat_container = st.container()
with chat_container:
    # Mostramos el chat en orden cronológico (más nuevo ABAJO)
    for autor, mensaje in st.session_state.chat_history:
        is_edith = (autor == "EDITH")
        # Usamos avatar="👓" para EDITH y "👤" para Francis
        with st.chat_message("assistant" if is_edith else "user", avatar="👓" if is_edith else "👤"):
            st.write(f"**{autor}:** {mensaje}")

# --- ENTRADA TÁCTIL (BARRA FIJA ABAJO) ---
# Usamos columnas para centrar el orbe y la barra
with st.container():
    col1, col2, col3 = st.columns([2,1,2]) # Centramos el orbe
    with col2:
        # El Orbe de Neón ahora es el botón de la grabadora
        audio_data = mic_recorder(
            start_prompt="🔴 INICIAR ESCANEO",
            stop_prompt="🟢 PROCESAR COMANDO",
            key='recorder',
            just_once=True,
            use_container_width=False # El orbe es pequeño
        )
    
    # La barra de escribir (Chat Input) siempre al final y centrada
    texto_manual = st.chat_input("Escribe tu comando o pregunta...")

# --- LÓGICA DE PROCESAMIENTO (VOZ O TEXTO) ---
user_text = None

# Prioridad 1: Audio
if audio_data:
    with st.spinner("Descifrando audio..."):
        try:
            transcription = client.audio.transcriptions.create(
              file=("audio.webm", audio_data['bytes']),
              model="whisper-large-v3"
            )
            user_text = transcription.text
        except Exception: pass

# Prioridad 2: Texto manual
elif texto_manual:
    user_text = texto_manual

# Procesamiento de la IA
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
        
        # Recarga rápida para mover el chat input
        st.rerun()
        
    except Exception as e:
        st.error(f"Error en enlace satelital: {e}")
