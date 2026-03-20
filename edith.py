import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN TÁCTICA ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- CSS DE BLOQUEO QUIRÚRGICO ---
st.markdown("""
    <style>
    /* Fondo y Reset */
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"], [data-testid="stSidebar"] { display: none; }

    /* 1. HEADER FIJO REAL */
    .header-box {
        position: fixed;
        top: 0; left: 0; width: 100%;
        height: 130px;
        background-color: black;
        z-index: 9999;
        text-align: center;
        border-bottom: 2px solid #00d4ff;
        padding-top: 10px;
    }
    .orb {
        width: 40px; height: 40px;
        background: radial-gradient(circle, #00d4ff 0%, #000 70%);
        border-radius: 50%; margin: 0 auto;
        box-shadow: 0 0 15px #00d4ff;
        animation: pulse 3s infinite;
    }

    /* 2. ESPACIADO DEL HISTORIAL */
    /* Forzamos al contenedor de mensajes a tener margen para no ser tapado */
    [data-testid="stVerticalBlock"] {
        padding-top: 140px !important;
        padding-bottom: 220px !important;
    }

    /* 3. FOOTER FIJO (Botón de voz) */
    .footer-box {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        height: 200px;
        background-color: black;
        z-index: 9998;
        border-top: 2px solid #00d4ff;
        padding: 20px 0;
    }

    /* Estilo del botón "Hablar Ahora" */
    .stButton > button {
        width: 100% !important;
        background-color: black !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 30px !important;
        font-weight: bold !important;
        letter-spacing: 2px;
        text-transform: uppercase;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.4);
    }
    
    /* 4. ANCLAJE DE BARRA DE ESCRITURA */
    /* Forzamos la barra nativa de Streamlit a quedarse abajo */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 30px !important;
        z-index: 10000 !important;
        padding: 0 5% !important;
    }

    /* Animaciones */
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }
    
    /* Ocultar reproductores */
    audio { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- COMPONENTES VISUALES FIJOS ---
st.markdown("""
    <div class="header-box">
        <div class="orb"></div>
        <h2 style='margin: 5px 0; letter-spacing: 4px;'>E.D.I.T.H.</h2>
        <p style='font-size: 0.7em; opacity: 0.8;'>SISTEMAS ARMÓNICOS V8.0</p>
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# --- HISTORIAL (Zona Central con Scroll Nativo) ---
for autor, msg in st.session_state.chat_history:
    role = "assistant" if autor == "EDITH" else "user"
    avatar = "👓" if autor == "EDITH" else "👤"
    with st.chat_message(role, avatar=avatar):
        st.write(f"**{autor}:** {msg}")

# --- CONTROLES INFERIORES ---
# El botón de voz vive en el "footer" visual
st.markdown('<div class="footer-box">', unsafe_allow_html=True)
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    audio_data = mic_recorder(
        start_prompt="HABLAR AHORA",
        stop_prompt="ESCUCHANDO...",
        key='recorder',
        just_once=True,
        use_container_width=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# La barra de texto se anclará sola por el CSS
texto_manual = st.chat_input("Escribe un comando...")

# --- PROCESAMIENTO ---
user_text = None
if audio_data:
    try:
        with st.spinner("Descifrando..."):
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
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "Eres EDITH. Responde muy corto."}, {"role": "user", "content": user_text}],
            model="llama-3.1-8b-instant"
        )
        ans = res.choices[0].message.content
        st.session_state.chat_history.append(("Francis", user_text))
        st.session_state.chat_history.append(("EDITH", ans))

        # --- ARREGLO DE VOZ (Persistente) ---
        tts = gTTS(text=ans, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        b64 = base64.b64encode(audio_fp.read()).decode()
        
        st.session_state.audio_key += 1
        
        # Inyectamos el audio con una llave única para forzar el Play
        audio_html = f'''
            <audio id="v_{st.session_state.audio_key}" autoplay>
                <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
            </audio>
            <script>
                var audio = document.getElementById("v_{st.session_state.audio_key}");
                audio.play();
            </script>
        '''
        st.markdown(audio_html, unsafe_allow_html=True)
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
