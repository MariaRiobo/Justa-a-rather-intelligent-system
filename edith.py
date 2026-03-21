# app.py (Guardado en tu caso como edith.py)
import streamlit as st
from streamlit_mic_recorder import mic_recorder
import herramientas

# Módulos Stark
from config import CSS_STARK
import cerebro
import voz
import vision # <--- NUEVO MÓDULO
import re
import youtube
import memoria

if "sistemas_activados" not in st.session_state:
    st.session_state.sistemas_activados = False
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ejecutar_saludo" not in st.session_state:
    st.session_state.ejecutar_saludo = False
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False
    
 # --- CONFIGURACIÓN UI ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓")
st.markdown(CSS_STARK, unsafe_allow_html=True)
st.markdown('<div class="orb"></div><h2 style="text-align: center; color: #00d4ff; letter-spacing: 5px;">E.D.I.T.H.</h2>', unsafe_allow_html=True)
st.markdown('<div class="orb"></div>', unsafe_allow_html=True)
audio_placeholder = st.empty()   

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
    st.text_input("Código de Acceso Stark:", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Código incorrecto. Protocolo de defensa activo.")
    st.stop() 

# Ejecutar el bloqueo
check_password()

# --- 4. PROTOCOLO DE BIENVENIDA AUTOMÁTICO ---
if st.session_state.ejecutar_saludo:
    mensaje_bienvenida = "Sistemas activados. Soy E.D.I.T.H. Bienvenida de vuelta, Jefa."
    try:
        audio_b64 = voz.generar_audio(mensaje_bienvenida)
        st.session_state.audio_key += 1
        
        # Inyección directa con markdown para asegurar el autoplay
        st.markdown(f'<audio autoplay><source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg"></audio>', unsafe_allow_html=True)
        
        # Registro en chat
        st.session_state.chat_history.append({"autor": "EDITH", "msg": mensaje_bienvenida})
        st.session_state.sistemas_activados = True
        st.session_state.ejecutar_saludo = False 
    except Exception as e:
        st.error(f"Fallo en el saludo inicial: {e}")
    



# --- SENSORES ÓPTICOS (NUEVO) ---
with st.expander("Activar Sensores Ópticos"):
    opcion_vision = st.radio("Modo de entrada:", ["Cámara", "Archivo"], horizontal=True)
    imagen_actual = None
    if opcion_vision == "Cámara":
        imagen_actual = st.camera_input("Capturar entorno")
    else:
        imagen_actual = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'])

# --- ESCÁNER DE DOCUMENTOS ---
with st.expander("Subir archivos"):
    archivo_subido = st.file_uploader("Subir documento (PDF o TXT)", type=['txt', 'pdf'])
    texto_documento = ""
    if archivo_subido is not None:
        texto_documento = herramientas.extraer_texto(archivo_subido)
        st.success(f"Archivo '{archivo_subido.name}' escaneado en memoria temporal.")

# --- CONTROLES DE AUDIO / TEXTO ---
audio_data = mic_recorder(start_prompt="HABLAR AHORA", stop_prompt="ESCUCHANDO...", key='recorder', just_once=True, use_container_width=True)
texto_manual = st.chat_input("Escribe...")

# --- PROCESAMIENTO CENTRAL ---
user_text = None
if audio_data:
    user_text = cerebro.transcribir_audio(audio_data['bytes'])
elif texto_manual:
    user_text = texto_manual

# El sistema se activa si hablaste/escribiste, o si simplemente tomaste una foto
if user_text or imagen_actual:
    try:
        texto_log = user_text if user_text else "[Imagen enviada]"
        
        # --- 1. DETECCIÓN AUTOMÁTICA DE YOUTUBE ---
        texto_youtube = ""
        hubo_error_yt = False # Bandera de seguridad activada
        
        if user_text:
            match_yt = re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^\s]+)', user_text)
            if match_yt:
                url_encontrada = match_yt.group(1)
                st.info("📹 Enlace detectado. Hackeando base de datos de YouTube...")
                
                transcripcion = youtube.obtener_transcripcion(url_encontrada)
                
                # Si falló, mostramos el error y activamos el protocolo de emergencia
                if transcripcion.startswith("ERROR_INTERNO"):
                    st.error(f"🚨 Falla en extracción de video: {transcripcion}")
                    hubo_error_yt = True
                    # Salvavidas: Definimos la respuesta para que la app no explote
                    respuesta = "Señor, no pude acceder a los subtítulos de ese video. Es probable que estén bloqueados o no existan."
                else:
                    # Si funcionó, le pasamos el guion a la IA
                    st.success("✅ Guion extraído con éxito. Procesando...")
                    texto_youtube = f"\n\n--- GUION DEL VIDEO DE YOUTUBE ---\n{transcripcion}"
        
      # --- 1.5 INTERCEPTOR DE MEMORIA A LARGO PLAZO ---
        prompt_oculto = user_text
        if user_text:
            comando_min = user_text.lower()
            if "recuerda que" in comando_min:
                # Extraemos el recuerdo y lo guardamos en el JSON
                nuevo_recuerdo = comando_min.split("recuerda que")[1].strip()
                memoria.agregar_recuerdo(nuevo_recuerdo)
                # Hackeamos el prompt para que la IA sepa que ya lo guardamos
                prompt_oculto = f"El usuario te ordenó guardar este recuerdo: '{nuevo_recuerdo}'. Ya lo guardé en el disco duro local. Confirma brevemente por voz que lo recordarás para siempre."
            
            elif "olvida que" in comando_min:
                # Extraemos y borramos del JSON
                recuerdo_a_borrar = comando_min.split("olvida que")[1].strip()
                memoria.borrar_recuerdo(recuerdo_a_borrar)
                prompt_oculto = f"El usuario te pidió olvidar esto: '{recuerdo_a_borrar}'. Ya lo borré de tu disco duro. Confirma brevemente que lo has eliminado de tu base de datos."

        # --- 2. ENRUTAMIENTO (Cerebro vs Visión) ---
        # Si NO hubo error con YouTube, dejamos que la IA piense normalmente
        if not hubo_error_yt:
            # Traemos todos los recuerdos pasados
            contexto_historico = memoria.obtener_contexto_memoria()
            
            # Juntamos documentos + YouTube + MEMORIA PROFUNDA
            contexto_unificado = texto_documento + texto_youtube + contexto_historico
            
            if imagen_actual:
                # Procesamiento visual (le pasamos el prompt oculto por si acaso)
                respuesta = vision.analizar_imagen(imagen_actual.getvalue(), prompt_oculto)
            else:
                # Procesamiento lógico normal usando el prompt hackeado
                respuesta = cerebro.pensar_respuesta(prompt_oculto, st.session_state.chat_history, contexto_unificado)
                
        # Guardamos en el historial visual (usamos texto_log para que en pantalla salga lo que dijiste, no el hackeo)
        st.session_state.chat_history.append({"autor": "Francis", "msg": texto_log})
        st.session_state.chat_history.append({"autor": "EDITH", "msg": respuesta})
        
        
        # --- FILTRO PURIFICADOR DE VOZ ---
        # Le quitamos asteriscos, numerales y guiones que traban al sintetizador
        texto_limpio = respuesta.replace("*", "").replace("#", "").replace("_", "")
        
        try:
            # Generamos la voz con el texto LIMPIO
            audio_b64 = voz.generar_audio(texto_limpio)
            st.session_state.audio_key += 1
            
            audio_html = f"""
                <audio autoplay key="audio_{st.session_state.audio_key}">
                    <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
                </audio>
            """
            audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
            
        except Exception as error_voz:
            # Si la voz falla, ahora nos avisará con un cartel amarillo sin romper la app
            st.warning(f"🔇 Módulo de voz saturado: {error_voz}")
            
    except Exception as e:
        st.error(f"Error general del sistema: {e}")

# --- MOSTRAR CHAT ---
for item in reversed(st.session_state.chat_history):
    autor = item.get("autor", "Desconocido")
    msg = item.get("msg", "")
    avatar = "👓" if autor == "EDITH" else "👤"
    
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar=avatar):
        st.write(f"**{autor}:** {msg}")

