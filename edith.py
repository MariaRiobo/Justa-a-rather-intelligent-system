import streamlit as st
from streamlit_mic_recorder import mic_recorder
import herramientas
import extra_streamlit_components as stx

# Módulos Stark
from config import CSS_STARK
import cerebro
import voz
import vision
import re
import youtube
import memoria
import base64


# --- 🔊 FUNCIÓN UNIVERSAL DE AUDIO (FIX iPHONE) ---
def reproducir_audio_base64(audio_b64, key):
    audio_bytes = base64.b64decode(audio_b64)

    # renderiza audio real (esto sí le gusta a iPhone)
    st.audio(audio_bytes, format="audio/mpeg")

    # JS para intentar autoplay sobre el audio renderizado
    autoplay_js = f"""
    <script>
    const audios = window.parent.document.querySelectorAll("audio");
    const audio = audios[audios.length - 1];

    if (audio) {{
        const playPromise = audio.play();

        if (playPromise !== undefined) {{
            playPromise.catch(() => {{
                const resume = () => {{
                    audio.play();
                    document.removeEventListener("touchstart", resume);
                    document.removeEventListener("click", resume);
                }};
                document.addEventListener("touchstart", resume);
                document.addEventListener("click", resume);
            }});
        }}
    }}
    </script>
    """
    st.components.v1.html(autoplay_js, height=0)


# --- ESTADOS ---
if "sistemas_activados" not in st.session_state:
    st.session_state.sistemas_activados = False
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0
if "chat_history" not in st.session_state:
    recuerdos = memoria.obtener_contexto_memoria()
    if recuerdos:
        st.session_state.chat_history = [{
            "autor": "EDITH", 
            "msg": "Registros recuperados. Estoy al tanto de nuestras sesiones previas, Francis."
        }]
    else:
        st.session_state.chat_history = []
if "ejecutar_saludo" not in st.session_state:
    st.session_state.ejecutar_saludo = False
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

# --- UI ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")
st.markdown(CSS_STARK, unsafe_allow_html=True)

placeholder_audio = st.empty()

st.markdown("""
    <div class="orb"></div>
    <h1 class="edith_title">E.D.I.T.H.</h1>
""", unsafe_allow_html=True)

audio_placeholder = st.empty()

# --- LOGIN ---
def check_password():
    cookie_manager = stx.CookieManager()
    token_recuerdo = cookie_manager.get(cookie="stark_access_token")

    if token_recuerdo == st.secrets["PASSWORD_MAESTRO"]:
        st.session_state["password_correct"] = True
        if "bienvenida_dicha" not in st.session_state:
            st.session_state.ejecutar_saludo = True
            st.session_state.bienvenida_dicha = True
        return True

    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD_MAESTRO"]:
            st.session_state["password_correct"] = True
            st.session_state["ejecutar_saludo"] = True
            st.session_state["bienvenida_dicha"] = True
            cookie_manager.set("stark_access_token", st.secrets["PASSWORD_MAESTRO"], expires_at=None)
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct"):
        return True
   
    st.text_input("Identificación Requerida:", type="password", on_change=password_entered, key="password")
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Acceso denegado. Perfil no reconocido.")
    st.stop()

check_password()

# --- BIENVENIDA ---
if st.session_state.ejecutar_saludo:
    with st.spinner("Sincronizando satélites..."):
        prompt_oculto = "La Jefa acaba de iniciar el sistema. Revisa la hora, el clima y dale un reporte estilo Stark. Máximo 2 oraciones."
        mensaje_bienvenida = cerebro.pensar_respuesta(prompt_oculto, [], "")
    
    try:
        texto_limpio = mensaje_bienvenida.replace("*", "").replace("#", "").replace("_", "")
        audio_b64 = voz.generar_audio(texto_limpio)

        st.session_state.audio_key += 1

        st.session_state.chat_history.append({"autor": "EDITH", "msg": mensaje_bienvenida})

        reproducir_audio_base64(audio_b64, f"welcome_{st.session_state.audio_key}")

        st.session_state.sistemas_activados = True
        st.session_state.ejecutar_saludo = False 
        
    except Exception as e:
        st.error(f"Fallo en voz: {e}")

# --- VISION ---
with st.expander("Activar Sensores Ópticos"):
    opcion_vision = st.radio("Modo:", ["Cámara", "Archivo"], horizontal=True)
    imagen_actual = st.camera_input("Capturar") if opcion_vision == "Cámara" else st.file_uploader("Subir imagen")

# --- DOCUMENTOS ---
with st.expander("Subir archivos"):
    archivo_subido = st.file_uploader("PDF o TXT", type=['txt', 'pdf'])
    texto_documento = herramientas.extraer_texto(archivo_subido) if archivo_subido else ""

# --- INPUT ---
audio_data = mic_recorder(start_prompt="HABLAR", stop_prompt="ESCUCHANDO...", key='recorder', just_once=True)
texto_manual = st.chat_input("Escribe algo...")

user_text = None
if audio_data:
    user_text = cerebro.transcribir_audio(audio_data['bytes'])
elif texto_manual:
    user_text = texto_manual

# --- PROCESAMIENTO ---
if user_text or imagen_actual:
    try:
        respuesta = ""
        texto_youtube = ""

        if user_text:
            match_yt = re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^\s]+)', user_text)
            if match_yt:
                transcripcion = youtube.obtener_transcripcion(match_yt.group(1))
                texto_youtube = transcripcion if not transcripcion.startswith("ERROR") else ""

        with st.spinner("E.D.I.T.H. procesando..."):
            contexto = texto_documento + texto_youtube + memoria.obtener_contexto_memoria()
            respuesta = cerebro.pensar_respuesta(user_text or "Analiza", st.session_state.chat_history, contexto)

        if respuesta:
            st.session_state.chat_history.append({"autor": "Francis", "msg": user_text or "[Imagen]"})
            st.session_state.chat_history.append({"autor": "EDITH", "msg": respuesta})

            memoria.agregar_recuerdo(f"{user_text} | {respuesta}")

            # 🔊 VOZ
            if len(respuesta) < 800:
                try:
                    audio_b64 = voz.generar_audio(respuesta)
                    st.session_state.audio_key += 1

                    audio_placeholder.empty()
                    reproducir_audio_base64(audio_b64, st.session_state.audio_key)

                except Exception as e:
                    st.error(f"Error voz: {e}")

    except Exception as e:
        st.error(f"Error: {e}")

# --- CHAT ---
for item in reversed(st.session_state.chat_history):
    avatar = "👓" if item["autor"] == "EDITH" else "👤"
    with st.chat_message("assistant" if item["autor"] == "EDITH" else "user", avatar=avatar):
        st.write(f"**{item['autor']}:** {item['msg']}")

