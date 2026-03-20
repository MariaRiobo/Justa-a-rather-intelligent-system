import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="E.D.I.T.H. - Stark Industries", page_icon="👓", layout="centered", initial_sidebar_state="collapsed")

# --- CSS MAESTRO: ESTILO STARK & INTERFAZ FIJA ---
st.markdown("""
    <style>
    /* 1. Fondo y Texto Base (Dark Mode Stark) */
    .stApp {
        background-color: #050a0e;
        color: #e0f7fa;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* 2. Avatar Animado (El Corazón de EDITH) */
    .edith-avatar {
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

    /* 3. Estilo del Chat (Holográfico Professional) */
    .stChatMessage {
        background-color: rgba(8, 18, 23, 0.8) !important;
        border-radius: 15px !important;
        border: 1px solid #00d4ff !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
        margin-bottom: 10px !important;
        padding: 10px !important;
    }
    
    .stChatMessage [data-testid="stChatMessageAvatar"] {
        background-color: #050a0e !important;
        border: 2px solid #00d4ff;
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
    
    /* 5. Espacio para que el chat no quede tapado por el botón */
    [data-testid="stVerticalBlock"] {
        padding-bottom: 150px !important;
    }

    /* 6. Estilo Profesional del Botón */
    .stButton>button { 
        border-radius: 50px; 
        height: 3.5em; 
        width: 100%;
        border: 2px solid #00d4ff; 
        background-color: #081217; 
        color: #00d4ff; 
        font-weight: bold;
        text-transform: uppercase;
        font-size: 1.1em;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0px 0px 15px rgba(0, 212, 255, 0.5);
    }
    
    .stButton>button:hover {
        background-color: #00d4ff;
        color: #081217;
        box-shadow: 0px 0px 30px #00d4ff;
    }

    /* Ocultar elementos innecesarios */
    [data-testid="stHeader"], [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- AVATAR ANIMADO (El Corazón del Sistema) ---
st.markdown('<div class="edith-avatar"></div>', unsafe_allow_html=True)
st.write("<div style='text-align: center; color: #00d4ff; font-weight: 200;'>SISTEMAS E.D.I.T.H. OPERATIVOS</div>", unsafe_allow_html=True)
st.write("<div style='text-align: center; font-size: 0.9em; margin-bottom: 20px;'>Francis, te escucho.</div>", unsafe_allow_html=True)

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

# --- HISTORIAL VISUAL (Holográfico Profesional) ---
# Usamos un contenedor para que el chat escrolee por detrás de la barra fija
chat_container = st.container()
with chat_container:
    for autor, mensaje in st.session_state.chat_history[::-1]:
        # Personalizamos los avatares y estilos de mensaje
        avatar_icon = "👓" if autor == "EDITH" else "👤"
        with st.chat_message("assistant" if autor == "EDITH" else "user", avatar=avatar_icon):
            st.write(f"**{autor}:** {mensaje}")

# --- BARRA INFERIOR FIJA CON EL BOTÓN ---
# Todo lo que esté aquí adentro se quedará congelado abajo
with st.container():
    # Usamos columnas para centrar el botón
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        audio_data = mic_recorder(
            start_prompt="🔴 INICIAR ESCANEO",
            stop_prompt="🟢 ENVIAR COMANDO",
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
        except Exception as e:
            st.error(f"Error de audio: {e}")

if user_text:
    with st.spinner("Procesando..."):
        try:
            prompt_sistema = "Eres E.D.I.T.H., la IA de los lentes de Tony Stark. Tu usuario es Francis. Eres ejecutiva, inteligente y muy rápida. Responde corto."
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": user_text}
                ],
                model="llama-3.1-8b-instant",
            )
            respuesta_texto = chat_completion.choices[0].message.content
            
            # Guardamos e invertimos para que el chat suba
            st.session_state.chat_history.append(("Francis", user_text))
            st.session_state.chat_history.append(("EDITH", respuesta_texto))
            
            # --- SISTEMA DE VOZ (IPHONE FIX CON LLAVE ÚNICA) ---
            tts = gTTS(text=respuesta_texto, lang='es')
            audio_fp = BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            # Truco Base64 para iOS
            audio_b64 = base64.b64encode(audio_fp.read()).decode()
            
            # Incrementamos la llave para forzar el reinicio del audio
            st.session_state.audio_key += 1
            
            audio_html = f'''
                <audio id="audio_{st.session_state.audio_key}" controls autoplay style="display:none;">
                    <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
                </audio>
                <script>
                    var audio = document.getElementById("audio_{st.session_state.audio_key}");
                    if (audio) {{ audio.play(); }}
                </script>
            '''
            # Inyectamos el audio invisiblemente
            st.markdown(audio_html, unsafe_allow_html=True)
            
            # Forzamos una recarga rápida para mover el chat
            st.rerun()
            
        except Exception as e:
            st.error(f"Error en enlace satelital: {e}")
