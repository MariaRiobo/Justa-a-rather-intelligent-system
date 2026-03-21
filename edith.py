# app.py (Guardado como edith.py)
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

# --- 1. CONFIGURACIÓN UI (Debe ir primero) ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")

# --- 2. INICIALIZACIÓN DE ESTADOS ---
if "sistemas_activados" not in st.session_state:
    st.session_state.sistemas_activados = False
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0
if "chat_history" not in st.session_state:
    recuerdos = memoria.obtener_contexto_memoria()
    if recuerdos:
        st.session_state.chat_history = [{"autor": "EDITH", "msg": "Registros recuperados. Estoy al tanto de nuestras sesiones previas, Comandante."}]
    else:
        st.session_state.chat_history = []
if "ejecutar_saludo" not in st.session_state:
    st.session_state.ejecutar_saludo = False
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

# --- 3. SISTEMA DE SEGURIDAD (COOKIES) ---
def check_password():
    cookie_manager = stx.CookieManager()
    token_recuerdo = cookie_manager.get(cookie="stark_access_token")

    if token_recuerdo == st.secrets["PASSWORD_MAESTRO"]:
        st.session_state["password_correct"] = True
        return True

    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD_MAESTRO"]:
            st.session_state["password_correct"] = True
            st.session_state["ejecutar_saludo"] = True
            cookie_manager.set("stark_access_token", st.secrets["PASSWORD_MAESTRO"], expires_at=None)
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct"):
        return True

    # Interfaz de Login
    st.markdown(CSS_STARK, unsafe_allow_html=True)
    st.markdown('<div class="orb"></div><h1 class="edith_title">E.D.I.T.H.</h1>', unsafe_allow_html=True)
    st.text_input("Identificación Requerida:", type="password", on_change=password_entered, key="password")
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Acceso denegado. Perfil no reconocido.")
    st.stop()

# Ejecutar el bloqueo de seguridad
check_password()

# --- 4. INTERFAZ PRINCIPAL (Si el acceso es correcto) ---
st.markdown(CSS_STARK, unsafe_allow_html=True)
st.markdown('<div class="orb"></div><h1 class="edith_title">E.D.I.T.H.</h1>', unsafe_allow_html=True)

audio_placeholder = st.empty()

# --- 5. PROTOCOLO DE BIENVENIDA ---
if st.session_state.ejecutar_saludo:
    mensaje_bienvenida = "Sistemas activados. Soy E.D.I.T.H. Bienvenida de vuelta, Jefa."
    try:
        audio_b64 = voz.generar_audio(mensaje_bienvenida)
        st.session_state.audio_key += 1
        st.markdown(f'<audio autoplay><source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg"></audio>', unsafe_allow_html=True)
        st.session_state.chat_history.append({"autor": "EDITH", "msg": mensaje_bienvenida})
        st.session_state.sistemas_activados = True
        st.session_state.ejecutar_saludo = False 
    except Exception as e:
        st.error(f"Fallo en el saludo inicial: {e}")


# --- 6. CONTROLES DE AUDIO / TEXTO ---
audio_data = mic_recorder(
    start_prompt="HABLAR AHORA", 
    stop_prompt="ESCUCHANDO...", 
    key='mic_definitivo'
)
texto_manual = st.chat_input("Escribe...")

# --- PROCESAMIENTO CENTRAL ---
user_text = None
if audio_data:
    user_text = cerebro.transcribir_audio(audio_data['bytes'])
elif texto_manual:
    user_text = texto_manual
# --- 7. SENSORES ÓPTICOS Y ESCÁNER ---
with st.expander(" Activar Sensores Ópticos"):
    opcion_vision = st.radio("Modo de entrada:", ["Cámara", "Archivo"], horizontal=True)
    imagen_actual = None
    if opcion_vision == "Cámara":
        imagen_actual = st.camera_input("Capturar entorno")
    else:
        imagen_actual = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'])

with st.expander("Escáner de Documentos"):
    archivo_subido = st.file_uploader("Subir documento (PDF o TXT)", type=['txt', 'pdf'])
    texto_documento = ""
    if archivo_subido is not None:
        texto_documento = herramientas.extraer_texto(archivo_subido)
        st.success(f"Archivo '{archivo_subido.name}' escaneado en memoria temporal.")

# --- 8. PROCESAMIENTO CENTRAL ---
user_text = None
if audio_data:
    user_text = cerebro.transcribir_audio(audio_data['bytes'])
elif texto_manual:
    user_text = texto_manual

if user_text or imagen_actual:
    try:
        texto_log = user_text if user_text else "[Imagen enviada]"
        
        # YouTube
        texto_youtube = ""
        hubo_error_yt = False 
        
        if user_text:
            match_yt = re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^\s]+)', user_text)
            if match_yt:
                url_encontrada = match_yt.group(1)
                st.info("📹 Enlace detectado. Hackeando base de datos de YouTube...")
                transcripcion = youtube.obtener_transcripcion(url_encontrada)
                if transcripcion.startswith("ERROR_INTERNO"):
                    st.error(f"🚨 Falla en extracción de video: {transcripcion}")
                    hubo_error_yt = True
                    respuesta = "Señor, no pude acceder a los subtítulos de ese video."
                else:
                    st.success("✅ Guion extraído con éxito. Procesando...")
                    texto_youtube = f"\n\n--- GUION DEL VIDEO DE YOUTUBE ---\n{transcripcion}"
        
        # Memoria
        prompt_oculto = user_text
        if user_text:
            comando_min = user_text.lower()
            if "recuerda que" in comando_min:
                nuevo_recuerdo = comando_min.split("recuerda que")[1].strip()
                memoria.agregar_recuerdo(nuevo_recuerdo)
                prompt_oculto = f"El usuario te ordenó guardar este recuerdo: '{nuevo_recuerdo}'. Confirma brevemente por voz."
            elif "olvida que" in comando_min:
                recuerdo_a_borrar = comando_min.split("olvida que")[1].strip()
                memoria.borrar_recuerdo(recuerdo_a_borrar)
                prompt_oculto = f"El usuario te pidió olvidar esto: '{recuerdo_a_borrar}'. Confirma brevemente."

        # Enrutamiento (Cerebro vs Visión)
        if not hubo_error_yt:
            contexto_historico = memoria.obtener_contexto_memoria()
            contexto_unificado = texto_documento + texto_youtube + contexto_historico
            
            if imagen_actual:
                respuesta = vision.analizar_imagen(imagen_actual.getvalue(), prompt_oculto)
            else:
                respuesta = cerebro.pensar_respuesta(prompt_oculto, st.session_state.chat_history, contexto_unificado)
                
        st.session_state.chat_history.append({"autor": "Francis", "msg": texto_log})
        st.session_state.chat_history.append({"autor": "EDITH", "msg": respuesta})
        
        registro_memoria = f"Usuario dijo: {texto_log} | EDITH respondió: {respuesta}"
        memoria.agregar_recuerdo(registro_memoria)
        
        # Filtro de Voz y Escudo Anti-Saturación
        texto_limpio = respuesta.replace("*", "").replace("#", "").replace("_", "").strip()
        
        # Si la IA devuelve algo vacío, forzamos un texto para que la voz no se rompa
        if not texto_limpio:
            texto_limpio = "Procedimiento completado, Comandante. No tengo más detalles para agregar."
            
        try:
            audio_b64 = voz.generar_audio(texto_limpio)
            st.session_state.audio_key += 1
            audio_html = f"""
                <audio autoplay key="audio_{st.session_state.audio_key}">
                    <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
                </audio>
            """
            audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
            
        except Exception as error_voz:
            st.warning(f"🔇 Módulo de voz en enfriamiento. Puedes leer mi respuesta abajo.")
            
    except Exception as e:
        st.error(f"Error general del sistema: {e}")

# --- 9. MOSTRAR CHAT ---
for item in reversed(st.session_state.chat_history):
    autor = item.get("autor", "Desconocido")
    msg = item.get("msg", "")
    avatar = "👓" if autor == "EDITH" else "👤"
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar=avatar):
        st.write(f"**{autor}:** {msg}")
