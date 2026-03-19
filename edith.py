import streamlit as st
from streamlit_mic_recorder import mic_recorder
from google import genai
from google.genai import types # <-- NUEVA HERRAMIENTA PARA EL AUDIO

# --- CONFIGURACIÓN DE PÁGINA PARA MÓVIL ---
st.set_page_config(
    page_title="E.D.I.T.H.", 
    page_icon="👓", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# CSS para Dark Mode Stark
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
st.write("Even Dead, I'm The Hero. Lista para operar, Mary.")

# --- API Y LÓGICA ---
# Leemos tu llave secreta desde la bóveda de Streamlit
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- ENTRADA DE AUDIO ---
st.write("### Control por Voz")
audio_data = mic_recorder(
    start_prompt="🔴 INICIAR ESCANEO DE VOZ",
    stop_prompt="🟢 PROCESAR COMANDO",
    key='recorder',
    just_once=True,
    use_container_width=True
)

# --- CONSOLA DE TEXTO ALTERNATIVA ---
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
            prompt_sistema = "Eres E.D.I.T.H., la IA de los lentes de Tony Stark. Tu usuaria es Mary. Eres ejecutiva, inteligente y rápida. Responde corto."
            
            # --- EL ARREGLO MÁGICO ESTÁ AQUÍ ---
            if es_voz:
                # Metemos el audio crudo en el "sobre" que exige Google
                contenido_a_enviar = [
                    prompt_sistema,
                    types.Part.from_bytes(data=user_input, mime_type='audio/webm')
                ]
                mensaje_mostrar = "🎙️ [Mensaje de Audio]"
            else:
                # Si es texto, va normal
                contenido_a_enviar = [prompt_sistema, user_input]
                mensaje_mostrar = texto_manual
            
            # Usamos el modelo 1.5 flash para evitar el bloqueo del Free Tier
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=contenido_a_enviar
            )
            
            respuesta_texto = response.text
            
            # Guardamos y mostramos
            st.session_state.chat_history.append(("Mary", mensaje_mostrar))
            st.session_state.chat_history.append(("EDITH", respuesta_texto))
            
            # VOZ DE RETORNO
            st.tts(respuesta_texto)
            
        except Exception as e:
            st.error(f"Error en enlace satelital: {e}")

# --- HISTORIAL VISUAL ---
for autor, mensaje in st.session_state.chat_history[::-1]:
    with st.chat_message("assistant" if autor == "EDITH" else "user"):
        st.write(f"**{autor}:** {mensaje}")
