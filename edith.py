import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from gtts import gTTS
from io import BytesIO
import base64

# --- CONFIGURACIÓN DE NÚCLEO ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓")

# --- ESTÉTICA STARK (Limpia y Funcional) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"] { display: none; }
    
    /* El Orbe Holográfico */
    .orb-container {
        display: flex; flex-direction: column; align-items: center; padding: 20px;
    }
    .orb {
        width: 70px; height: 70px;
        background: radial-gradient(circle, #00d4ff 0%, #000 75%);
        border-radius: 50%;
        box-shadow: 0 0 20px #00d4ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    /* Mensajes de Chat */
    .stChatMessage {
        background: rgba(8, 18, 23, 0.95) !important;
        border: 1px solid #00d4ff !important;
        border-radius: 15px !important;
    }

    /* Botón de Hablar */
    .stButton > button {
        background-color: #000 !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 20px !important;
        width: 100%;
        font-weight: bold;
        letter-spacing: 1px;
    }
    
    /* Ocultar reproductores de audio feos */
    audio { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("""
    <div class="orb-container">
        <div class="orb"></div>
        <h1 style='margin: 10px 0; letter-spacing: 5px; font-size: 2rem;'>E.D.I.T.H.</h1>
    </div>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- HISTORIAL DE CHAT ---
# Mostramos el historial. Streamlit mantendrá el scroll automáticamente.
for autor, msg in st.session_state.chat_history:
    avatar = "👓" if autor == "EDITH" else "👤"
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar=avatar):
        st.write(f"**{autor}:** {msg}")

# --- CONTROLES DE ENTRADA (Siempre visibles al final) ---
st.write("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Botón de micrófono
    audio_data = mic_recorder(
        start_prompt="HABLAR AHORA",
        stop_prompt="ESCUCHANDO...",
        key='recorder',
        just_once=True,
        use_container_width=True
    )

# Barra de escritura (Streamlit la pone siempre abajo por defecto)
texto_manual = st.chat_input("Comando para E.D.I.T.H...")

# --- PROCESAMIENTO ---
user_text = None
if audio_data:
    try:
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
        # Generar respuesta de texto
        res = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres EDITH, la IA de Tony Stark. Responde de forma muy concisa y profesional."},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.1-8b-instant"
        )
        ans = res.choices[0].message.content
        
        # Guardar en historial
        st.session_state.chat_history.append(("Francis", user_text))
        st.session_state.chat_history.append(("EDITH", ans))

        # --- GENERAR Y REPRODUCIR VOZ ---
        tts = gTTS(text=ans, lang='es')
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        b64 = base64.b64encode(audio_fp.read()).decode()
        
        st.session_state.audio_key += 1
        
        # Inyectamos el audio con autoplay. Al hacer rerun, se reproduce solo.
        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
        
        # Forzamos recarga para que el historial se actualice y la voz suene
        st.rerun()
        
    except Exception as e:
        st.error(f"Error en los sistemas: {e}")
