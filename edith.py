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

# --- CONFIGURACIÓN UI ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓")
st.markdown(CSS_STARK, unsafe_allow_html=True)
st.markdown('<div class="orb"></div><h2 style="text-align: center; color: #00d4ff; letter-spacing: 5px;">E.D.I.T.H.</h2>', unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0
if "sistemas_activados" not in st.session_state:
    st.session_state.sistemas_activados = False

audio_placeholder = st.empty()

# --- PROTOCOLO DE ENCENDIDO (NUEVO) ---
if not st.session_state.sistemas_activados:
    st.info("🛡️ Sistemas en espera. El navegador requiere autorización manual para habilitar el audio.")
    
    # Este botón le da al navegador el "clic" que necesita para permitir el sonido
    if st.button("🔌 INICIAR E.D.I.T.H. (Autorizar Audio)"):
        mensaje_bienvenida = "Sistemas activados. Soy EDITH. Even dead I'm the hero. Estoy lista para servirte."
        
        try:
            # Generamos el audio de bienvenida
            audio_b64 = voz.generar_audio(mensaje_bienvenida)
            st.session_state.audio_key += 1
            
            audio_html = f"""
                <audio autoplay key="init_{st.session_state.audio_key}">
                    <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
                </audio>
            """
            # Usamos st.markdown directo para que el audio se inyecte en este mismo instante
            st.markdown(audio_html, unsafe_allow_html=True)
            
            # Agregamos el mensaje al chat visual
            st.session_state.chat_history.append({"autor": "EDITH", "msg": mensaje_bienvenida})
            
        except Exception as e:
            st.error(f"Fallo en el sintetizador de voz inicial: {e}")
            
        # Marcamos como activado para que el botón desaparezca y no lo repita
        st.session_state.sistemas_activados = True
        
# --- SENSORES ÓPTICOS (NUEVO) ---
with st.expander("👁️ Activar Sensores Ópticos"):
    opcion_vision = st.radio("Modo de entrada:", ["Cámara", "Archivo"], horizontal=True)
    imagen_actual = None
    if opcion_vision == "Cámara":
        imagen_actual = st.camera_input("Capturar entorno")
    else:
        imagen_actual = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'])

# --- ESCÁNER DE DOCUMENTOS ---
with st.expander("📂 Escáner de Archivos"):
    archivo_subido = st.file_uploader("Subir documento (PDF o TXT)", type=['txt', 'pdf'])
    texto_documento = ""
    if archivo_subido is not None:
        texto_documento = herramientas.extraer_texto(archivo_subido)
        st.success(f"Archivo '{archivo_subido.name}' escaneado en memoria temporal.")

# --- CONTROLES DE AUDIO / TEXTO ---
audio_data = mic_recorder(start_prompt="HABLAR AHORA", stop_prompt="ESCUCHANDO...", key='recorder', just_once=True, use_container_width=True)
texto_manual = st.chat_input("Comando (o pregunta sobre la foto)...")

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
        
      # --- NUEVO: DETECCIÓN AUTOMÁTICA DE YOUTUBE ---
        texto_youtube = ""
        if user_text:
            match_yt = re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^\s]+)', user_text)
            if match_yt:
                url_encontrada = match_yt.group(1)
                st.info("📹 Enlace detectado. Hackeando base de datos de YouTube...")
                
                transcripcion = youtube.obtener_transcripcion(url_encontrada)
                
                # Si falló, mostramos el error en rojo en la pantalla
                if transcripcion.startswith("ERROR_INTERNO"):
                    st.error(f"🚨 Falla en extracción de video: {transcripcion}")
                else:
                    # Si funcionó, le pasamos el guion a la IA
                    st.success("✅ Guion extraído con éxito. Procesando...")
                    texto_youtube = f"\n\n--- GUION DEL VIDEO DE YOUTUBE ---\n{transcripcion}"
                    
        
               # Guardamos en el historial visual
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

