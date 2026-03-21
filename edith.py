import streamlit as st
from streamlit_mic_recorder import mic_recorder
import herramientas
import cerebro
import voz
import vision 
import re
import youtube
import memoria
from config import CSS_STARK

# --- 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero) ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")
st.markdown(CSS_STARK, unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE ESTADOS ---
if "sistemas_activados" not in st.session_state:
    st.session_state.sistemas_activados = False
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ejecutar_saludo" not in st.session_state:
    st.session_state.ejecutar_saludo = False

# --- 3. SISTEMA DE AUTENTICACIÓN STARK ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD_MAESTRO"]:
            st.session_state["password_correct"] = True
            st.session_state["ejecutar_saludo"] = True  # Gatillo para el saludo
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct"):
        return True

    # Interfaz de Login (Lo único que se ve si no hay acceso)
    st.markdown('<div class="orb"></div>', unsafe_allow_html=True)
    st.text_input("🔑 Código de Acceso Stark:", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("❌ Código incorrecto. Protocolo de defensa activo.")
    st.stop() 

# Ejecutar el bloqueo
check_password()

# --- 4. PROTOCOLO DE BIENVENIDA AUTOMÁTICO ---
# Se ejecuta solo una vez, inmediatamente después del login exitoso
if st.session_state.ejecutar_saludo:
    mensaje_bienvenida = "Sistemas activados. Soy E.D.I.T.H. Bienvenida de vuelta, Jefa."
    try:
        # Audio
        audio_b64 = voz.generar_audio(mensaje_bienvenida)
        st.session_state.audio_key += 1
        audio_html = f'<audio autoplay><source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
        
        # Chat
        st.session_state.chat_history.append({"autor": "EDITH", "msg": mensaje_bienvenida})
        st.session_state.sistemas_activados = True
        st.session_state.ejecutar_saludo = False # Apagar gatillo
    except Exception as e:
        st.error(f"Fallo en el sintetizador inicial: {e}")

# --- 5. INTERFAZ DE USUARIO (Post-Login) ---
st.markdown('<div class="orb"></div><h2 style="text-align: center; color: #00d4ff; letter-spacing: 5px;">E.D.I.T.H.</h2>', unsafe_allow_html=True)
audio_placeholder = st.empty()

# Sensores Ópticos y Archivos
with st.sidebar:
    st.title("🎛️ Panel de Control")
    with st.expander("📷 Sensores Ópticos"):
        opcion_vision = st.radio("Modo:", ["Cámara", "Archivo"], horizontal=True)
        imagen_actual = st.camera_input("Capturar") if opcion_vision == "Cámara" else st.file_uploader("Imagen", type=['png', 'jpg', 'jpeg'])
    
    with st.expander("📄 Escáner de Documentos"):
        archivo_subido = st.file_uploader("PDF o TXT", type=['txt', 'pdf'])
        texto_documento = herramientas.extraer_texto(archivo_subido) if archivo_subido else ""

# Controles de Entrada
audio_data = mic_recorder(start_prompt="🎙️ HABLAR", stop_prompt="⌛ ESCUCHANDO...", key='recorder', just_once=True)
texto_manual = st.chat_input("Escribe una orden...")

# --- 6. PROCESAMIENTO CENTRAL ---
user_text = None
if audio_data:
    user_text = cerebro.transcribir_audio(audio_data['bytes'])
elif texto_manual:
    user_text = texto_manual

if user_text or imagen_actual:
    try:
        texto_log = user_text if user_text else "[Imagen enviada]"
        texto_youtube = ""
        hubo_error_yt = False
        
        # YouTube Detection
        if user_text:
            match_yt = re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^\s]+)', user_text)
            if match_yt:
                st.info("📹 Hackeando base de datos de YouTube...")
                transcripcion = youtube.obtener_transcripcion(match_yt.group(1))
                if transcripcion.startswith("ERROR_INTERN"):
                    st.error("🚨 Falla en extracción.")
                    hubo_error_yt = True
                    respuesta = "No pude acceder a los subtítulos de ese video."
                else:
                    texto_youtube = f"\n\n--- GUION YOUTUBE ---\n{transcripcion}"

        # Memoria y Respuesta
        if not hubo_error_yt:
            prompt_oculto = user_text if user_text else ""
            
            # Comandos de Memoria
            if user_text and "recuerda que" in user_text.lower():
                nuevo = user_text.lower().split("recuerda que")[1].strip()
                memoria.agregar_recuerdo(nuevo)
                prompt_oculto = f"Confirmar que guardaste: {nuevo}"
            
            contexto_historico = memoria.obtener_contexto_memoria()
            contexto_unificado = texto_documento + texto_youtube + contexto_historico
            
            if imagen_actual:
                respuesta = vision.analizar_imagen(imagen_actual.getvalue(), prompt_oculto)
            else:
                respuesta = cerebro.pensar_respuesta(prompt_oculto, st.session_state.chat_history, contexto_unificado)

        # Registro y Voz
        st.session_state.chat_history.append({"autor": "Francis", "msg": texto_log})
        st.session_state.chat_history.append({"autor": "EDITH", "msg": respuesta})
        
        texto_limpio = respuesta.replace("*", "").replace("#", "").replace("_", "")
        audio_res = voz.generar_audio(texto_limpio)
        st.session_state.audio_key += 1
        audio_placeholder.markdown(f'<audio autoplay key="{st.session_state.audio_key}"><source src="data:audio/mpeg;base64,{audio_res}" type="audio/mpeg"></audio>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error general: {e}")

# --- 7. RENDERIZADO DEL CHAT (Invertido para ver lo último arriba) ---
for item in reversed(st.session_state.chat_history):
    with st.chat_message("assistant" if item["autor"] == "EDITH" else "user", avatar="👓" if item["autor"] == "EDITH" else "👤"):
        st.write(f"**{item['autor']}:** {item['msg']}")


