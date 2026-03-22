# app.py (Guardado en tu caso como edith.py)
import streamlit as st
from streamlit_mic_recorder import mic_recorder
import herramientas
import extra_streamlit_components as stx

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
    # Intentamos recuperar la memoria a largo plazo
    recuerdos = memoria.obtener_contexto_memoria()
    if recuerdos:
        # Si hay algo guardado, lo cargamos como el primer mensaje de EDITH
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
    
# --- 5. CONFIGURACIÓN UI Y ELEMENTOS VISUALES ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")
st.markdown(CSS_STARK, unsafe_allow_html=True)

# 👇 ESTA ES LA ÚNICA VEZ QUE DIBUJAMOS EL ORBE Y EL TÍTULO 👇
st.markdown("""
    <div class="orb"></div>
    <h1 class="edith_title">E.D.I.T.H.</h1>
""", unsafe_allow_html=True)

audio_placeholder = st.empty()

# --- SISTEMA DE RECONOCIMIENTO DE DISPOSITIVO (COOKIES) ---
def check_password():
    cookie_manager = stx.CookieManager()
    token_recuerdo = cookie_manager.get(cookie="stark_access_token")

    # Si entra directo con la cookie
    if token_recuerdo == st.secrets["PASSWORD_MAESTRO"]:
        st.session_state["password_correct"] = True
        # Agregamos esta regla: Si entró con cookie y aún no ha saludado hoy, que salude.
        if "bienvenida_dicha" not in st.session_state:
            st.session_state.ejecutar_saludo = True
            st.session_state.bienvenida_dicha = True
        return True

    # Si entra escribiendo la contraseña manualmente
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

# Ejecutar el bloqueo
check_password()



# --- 4. PROTOCOLO DE BIENVENIDA AUTOMÁTICO DINÁMICO ---
# --- 4. PROTOCOLO DE BIENVENIDA AUTOMÁTICO ---
if st.session_state.ejecutar_saludo:
    # 1. Generamos el reporte (esto funciona bien)
    with st.spinner("Sincronizando satélites..."):
        prompt_oculto = "La Jefa acaba de iniciar el sistema. Revisa la hora, el clima y dale un reporte de bienvenida estilo Stark. Sé breve, sarcástica y al grano. Máximo 2 oraciones."
        mensaje_bienvenida = cerebro.pensar_respuesta(prompt_oculto, [], "")
    
    try:
        # 2. Preparamos la voz
        texto_limpio = mensaje_bienvenida.replace("*", "").replace("#", "").replace("_", "")
        audio_b64 = voz.generar_audio(texto_limpio)
        st.session_state.audio_key += 1
        
        # 3. GUARDAMOS EN EL HISTORIAL PRIMERO
        st.session_state.chat_history.append({"autor": "EDITH", "msg": mensaje_bienvenida})
        
        # 4. INYECCIÓN DE AUDIO (El truco es el autoplay y el key dinámico)
        audio_html = f"""
            <div style="display:none;">
                <audio autoplay="true" key="welcome_{st.session_state.audio_key}">
                    <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
                </audio>
            </div>
        """
        # Usamos st.write o el placeholder si ya lo tienes definido
        st.components.v1.html(audio_html, height=0)
        
        # 5. Cerramos protocolo
        st.session_state.sistemas_activados = True
        st.session_state.ejecutar_saludo = False 
        
    except Exception as e:
        st.error(f"Fallo en el protocolo de voz: {e}")
        
        
            
                                                     

# --- SENSORES ÓPTICOS ---
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
        st.success(f"Archivo '{archivo_subido.name}' escaneado.")

# --- CONTROLES DE ENTRADA (ESTO ES LO QUE FALTABA) ---
audio_data = mic_recorder(start_prompt="HABLAR", stop_prompt=" ESCUCHANDO...", key='recorder', just_once=True, use_container_width=True)
texto_manual = st.chat_input("Escribe un comando o pega un link de YouTube...")

# --- PROCESAMIENTO CENTRAL UNIFICADO ---
user_text = None
if audio_data:
    user_text = cerebro.transcribir_audio(audio_data['bytes'])
elif texto_manual:
    user_text = texto_manual

if user_text or imagen_actual:
    try:
        respuesta = ""
        es_redaccion = False
        texto_youtube = ""
        hubo_error_yt = False

        # 1. DETECCIÓN DE REDACCIÓN O YOUTUBE
        if user_text:
            # ¿Es redacción?
            palabras_redaccion = ["redacta", "escribe", "mandale", "mail", "correo", "mensaje", "whatsapp"]
            es_redaccion = any(p in user_text.lower() for p in palabras_redaccion)
            
            # ¿Es YouTube?
            match_yt = re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^\s]+)', user_text)
            if match_yt:
                st.info("Enlace detectado. Analizando video...")
                transcripcion = youtube.obtener_transcripcion(match_yt.group(1))
                if transcripcion.startswith("ERROR"):
                    st.error("No pude acceder al guion del video.")
                    hubo_error_yt = True
                else:
                    texto_youtube = f"\n\n--- GUION DE YOUTUBE ---\n{transcripcion}"

        # 2. GENERACIÓN DE RESPUESTA
        with st.spinner("E.D.I.T.H. procesando..."):
            if es_redaccion:
                instruccion = f"Redacta un borrador Stark para esto: {user_text}"
                respuesta = cerebro.pensar_respuesta(instruccion, st.session_state.chat_history, "")
            elif imagen_actual:
                respuesta = cerebro.pensar_respuesta(user_text if user_text else "Analiza esto", st.session_state.chat_history, imagen_actual)
            else:
                # Mezclamos Memoria + Documentos + YouTube
                contexto_total = texto_documento + texto_youtube + memoria.obtener_contexto_memoria()
                respuesta = cerebro.pensar_respuesta(user_text, st.session_state.chat_history, contexto_total)

        # 3. INTERFAZ DE SALIDA
        if respuesta:
           if es_redaccion:
                with st.spinner("E.D.I.T.H. está preparando la pluma..."):
                    # Prompt reforzado para evitar que incluya nombres de usuario o firmas extrañas
                    instruccion = f"""
                    Actúa como redactor. Genera UN BORRADOR para: {user_text}.
                    REGLA DE ORO: Devuelve ÚNICAMENTE el texto del mensaje, sin introducciones, sin comillas iniciales, y sin decir 'Borrador:' o 'Francis:'. 
                    Usa un estilo Stark elegante.
                    """
                    respuesta = cerebro.pensar_respuesta(instruccion, st.session_state.chat_history, "")
                    
                    # Limpieza extra por si la IA se pone creativa
                    respuesta_limpia = respuesta.strip().strip('"').strip("'")
                    
                    st.subheader("📋 Borrador Táctico")
                    # Usamos st.code porque permite copiar manualmente si el botón falla, y se ve más limpio
                    st.code(respuesta_limpia, language=None)
                    
                    # Botón de Copiado con "Safe String" para JavaScript
                    # Usamos json.dumps para que las comillas y saltos de línea no rompan el script
                    import json
                    safe_text = json.dumps(respuesta_limpia)
                    
                    boton_copy_html = f"""
                        <div id="copy_container">
                            <button onclick="copyToClipboard()" id="btn_stark">
                                ⚡ COPIAR MENSAJE
                            </button>
                        </div>

                        <script>
                        function copyToClipboard() {{
                            const text = {safe_text};
                            navigator.clipboard.writeText(text).then(() => {{
                                const btn = document.getElementById('btn_stark');
                                btn.innerText = '✅ ¡COPIADO!';
                                btn.style.background = '#28a745';
                            }}).catch(err => {{
                                console.error('Error al copiar: ', err);
                            }});
                        }}
                        </script>

                        <style>
                            #btn_stark {{
                                background-color: #FF4B4B;
                                color: white;
                                border: none;
                                padding: 15px;
                                border-radius: 10px;
                                width: 100%;
                                cursor: pointer;
                                font-weight: bold;
                                font-family: sans-serif;
                                transition: 0.3s;
                            }}
                            #btn_stark:active {{
                                transform: scale(0.98);
                            }}
                        </style>
                    """
                    st.components.v1.html(boton_copy_html, height=80)
            
           # 1. Guardamos en historial una sola vez
            # Revisa que esta línea tenga los mismos espacios que el 'if es_redaccion' de arriba
            st.session_state.chat_history.append({"autor": "Francis", "msg": user_text if user_text else "[Imagen]"})
            st.session_state.chat_history.append({"autor": "EDITH", "msg": respuesta})
            
            # 2. Guardamos en memoria persistente
            memoria.agregar_recuerdo(f"Usuario: {user_text} | EDITH: {respuesta}")

            # 3. Protocolo de Voz
            if len(respuesta) < 500:
                t_voz = respuesta.replace("*","").replace("#","").replace("_","")
                audio_b64 = voz.generar_audio(t_voz)
                audio_html = f'<audio autoplay><source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg"></audio>'
                audio_placeholder.markdown(audio_html, unsafe_allow_html=True)

            # 4. Rerun condicional
            if not es_redaccion:
                st.rerun()

    except Exception as e:
        st.error(f"Falla crítica: {e}")

# --- MOSTRAR CHAT ---
for item in reversed(st.session_state.chat_history):
    autor = item.get("autor", "Desconocido")
    msg = item.get("msg", "")
    avatar = "👓" if autor == "EDITH" else "👤"
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar=avatar):
        st.write(f"**{autor}:** {msg}")

