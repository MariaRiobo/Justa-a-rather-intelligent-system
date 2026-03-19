import streamlit as st
from streamlit_mic_recorder import mic_recorder
from google import genai

# --- CONFIGURACIÓN DE PÁGINA PARA MÓVIL ---
st.set_page_config(
    page_title="E.D.I.T.H.", 
    page_icon="👓", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# CSS para que parezca una App nativa de iPhone (Dark Mode Stark)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00d4ff; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .stButton>button { 
        border-radius: 50px; 
        height: 3em; 
        border: 2px solid #00d4ff; 
        background-color: #081217; 
        color: white; 
        font-weight: bold;
        box-shadow: 0px 0px 15px #00d4ff;
    }
    .stChatInput { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👓 E.D.I.T.H.")
st.write("Even Dead, I'm The Hero. Lista para operar, Francis.")

# --- API Y LÓGICA ---
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- ENTRADA DE AUDIO (Micrófono del iPhone) ---
# En iOS, el navegador pedirá permiso la primera vez. 
st.write("### Control por Voz")
audio_data = mic_recorder(
    start_prompt="🔴 INICIAR ESCANEO DE VOZ",
    stop_prompt="🟢 PROCESAR COMANDO",
    key='recorder',
    just_once=True,
    use_container_width=True
)

# --- CONSOLA DE TEXTO ALTERNATIVA ---
# Si el micro falla o hay ruido, usa esto:
texto_manual = st.chat_input("Consola de mando manual...")

# --- PROCESAMIENTO ---
user_input = None
es_voz = False

if audio_data:
    user_input = audio_data['bytes']
    es_voz = True
elif texto_manual:
    user_input = texto_manual

if user_input:
    with st.spinner("Analizando..."):
        try:
            # Enviamos a Gemini (E.D.I.T.H.)
            prompt_sistema = "Eres E.D.I.T.H., la IA de los lentes de Tony Stark. Tu usuaria es Francis. Eres ejecutiva, inteligente y rápida. Responde corto."
            
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[prompt_sistema, user_input]
            )
            
            respuesta_texto = response.text
            
            # Guardamos y mostramos
            st.session_state.chat_history.append(("Francis", "🎙️ Audio" if es_voz else texto_manual))
            st.session_state.chat_history.append(("EDITH", respuesta_texto))
            
            # VOZ DE RETORNO: Esto activará el altavoz del iPhone
            st.tts(respuesta_texto)
            
        except Exception as e:
            st.error(f"Error en enlace satelital: {e}")

# --- HISTORIAL VISUAL ---
for autor, mensaje in st.session_state.chat_history[::-1]: # Lo más nuevo arriba
    with st.chat_message("assistant" if autor == "EDITH" else "user"):
        st.write(f"**{autor}:** {mensaje}")
