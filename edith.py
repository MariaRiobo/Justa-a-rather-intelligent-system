# app.py funciona
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
import notificaciones


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
if "alarmas_activas" not in st.session_state:
    st.session_state.alarmas_activas = []
    
# --- 5. CONFIGURACIÓN UI Y ELEMENTOS VISUALES ---
st.set_page_config(page_title="E.D.I.T.H.", page_icon="👓", layout="centered")
st.markdown(CSS_STARK, unsafe_allow_html=True)
# Altavoz de EDITH (Posición fija)
placeholder_audio = st.empty()

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
              
            # --- PROTOCOLO DE VISIÓN REACTIVADO ---
            elif imagen_actual:
                # 1. Definimos la orden visual (lo que el usuario quiere saber de la foto)
                user_text_para_vision = user_text if user_text else "Analiza esta imagen con detalle técnico."
                
                # 2. Extraemos la información real de la imagen (.getvalue() saca los bytes puros)
                # Esto funciona tanto para 'Cámara' como para 'Archivo'.
                image_bytes = imagen_actual.getvalue()
                
                # 3. Activamos los Ojos de EDITH (vision.py) para traducir la imagen a texto
                analisis_visual_texto = vision.analizar_imagen(image_bytes, user_text_para_vision)
                
                # 4. Verificamos si hubo un fallo en los sensores ópticos
                if analisis_visual_texto.startswith("ERROR"):
                    st.error(f"Fallo en sensores ópticos: {analisis_visual_texto}")
                    respuesta = "Jefa, mis sensores ópticos están descalibrados. No puedo procesar la imagen en este momento."
                else:
                    # 5. Mezclamos el análisis visual como contexto para que EDITH responda en el chat
                    prompt_final = user_text if user_text else "Analiza esto"
                    contexto_visual = f"\n\n--- ANÁLISIS VISUAL DE LA CÁMARA ---\n{analisis_visual_texto}"
                    respuesta = cerebro.pensar_respuesta(prompt_final, st.session_state.chat_history, contexto_visual)
         

            else:
                # Mezclamos Memoria + Documentos + YouTube
                contexto_total = texto_documento + texto_youtube + memoria.obtener_contexto_memoria()
                respuesta = cerebro.pensar_respuesta(user_text, st.session_state.chat_history, contexto_total)

           # --- ALARMA NIVEL STARK ---
            match_timer = re.search(r"\[TIMER:(\d+)\]", respuesta)
            
            if match_timer:
                segundos_reales = int(match_timer.group(1))
                respuesta = re.sub(r"\[TIMER:\d+\]", "", respuesta).strip()
                
                # 1. Definimos la función de aviso (Versión Reloj Atómico)
                def aviso_final_iphone(segundos):
                    import time
                    
                    # Calculamos la HORA EXACTA del futuro en la que debe sonar
                    hora_final = time.time() + (segundos - 3)
                    
                    # En lugar de un "sueño profundo", miramos el reloj cada medio segundo
                    while time.time() < hora_final:
                        time.sleep(0.5) 
                        
                    notificaciones.enviar_pushover(
                        mensaje="¡TIEMPO CUMPLIDO, FRANCIS!",
                        titulo="ALERTA CRÍTICA",
                        sonido="siren"
                    )
    
                # 2. Lanzamos el hilo
                import threading
                threading.Thread(target=aviso_final_iphone, args=(segundos_reales,)).start()
    
                # 3. Notificación de inicio inmediata
                notificaciones.enviar_pushover(
                    mensaje=f"Temporizador de {segundos_reales}s iniciado.",
                    sonido="bike"
                )
        
                # 4. VOZ Y RELOJ (PC)
                aviso_final = "Atención Francis, el tiempo ha expirado."
                audio_aviso_b64 = voz.generar_audio(aviso_final)
                
                # ¡ESTE BLOQUE AHORA ESTÁ FIRMEMENTE DENTRO DEL IF!
                st.components.v1.html(f"""
                    <div id="cronometro_stark" style="position:fixed; top:10px; right:10px; background:rgba(0,191,255,0.2); border:1px solid #00fbff; color:#00fbff; padding:10px; border-radius:10px; font-family:monospace; z-index:9999;">
                        T-MINUS: <span id="timer_display">{segundos_reales}</span>s
                    </div>
                    <script>
                        // Ajustamos el tiempo final restando los 3 segundos de "arranque"
                        var compensacion = 3;
                        var endTime = Date.now() + (({segundos_reales} - compensacion) * 1000);
                        var display = document.getElementById('timer_display');
                        
                        var countdown = setInterval(function() {{
                            var now = Date.now();
                            var timeLeft = Math.round((endTime - now) / 1000);
                            
                            if (timeLeft <= 0) {{
                                clearInterval(countdown);
                                display.innerHTML = "0";
                                document.getElementById('cronometro_stark').style.display = 'none';
                                
                                var audio = new Audio("data:audio/mpeg;base64,{audio_aviso_b64}");
                                audio.play();
                            }} else {{
                                display.innerHTML = timeLeft;
                            }}
                        }}, 1000);
                    </script>
                """, height=60)
                
      
           
        # --- 3. INTERFAZ DE SALIDA - PROTOCOLO REESTRUCTURADO ---
        if respuesta:
            # A. GUARDADO (Historial Limpio)
            if not st.session_state.chat_history or st.session_state.chat_history[-1]["msg"] != respuesta:
                st.session_state.chat_history.append({"autor": "Francis", "msg": user_text if user_text else "[Imagen]"})
                st.session_state.chat_history.append({"autor": "EDITH", "msg": respuesta})
                memoria.agregar_recuerdo(f"Usuario: {user_text} | EDITH: {respuesta}")

            # B. CANAL DE REDACCIÓN (Solo si pides un mensaje/correo)
            if es_redaccion:
                with st.spinner("Extrayendo mensaje para enviar..."):
                    # Filtro maestro: separa el mensaje real de la charla de EDITH
                    p_limpieza = f"Actúa como filtro humano. Extrae SOLO el mensaje que el usuario debe enviar. Elimina 'EDITH:', introducciones de IA, reportes de seguridad y análisis táctico. Solo el texto natural: {respuesta}"
                    borrador_limpio = cerebro.pensar_respuesta(p_limpieza, [], "").strip().strip('"').replace("**", "")

                # Mostramos el borrador en un bloque destacado
                st.code(borrador_limpio, language=None, wrap_lines=True)
                st.info("Copia el texto de arriba. EDITH te dará el reporte táctico por voz.")

      # C. PROTOCOLO DE VOZ (Viernes Restaurado - 100% Invisible)
            if len(respuesta) < 800:
                t_voz = respuesta.replace("*","").replace("#","").replace("_","").replace("`","").replace('"',"").replace("'","")
                try:
                    audio_b64 = voz.generar_audio(t_voz)
                    st.session_state.audio_key += 1
                    
                    # Sin 'controls' y con display:none forzado para invisibilidad total
                    audio_html = f"""
                        <audio id="voz_{st.session_state.audio_key}" autoplay="true" style="display: none !important;">
                            <source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">
                        </audio>
                    """
                    # Sobreescribimos el placeholder para evitar repeticiones
                    audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
                    
                except Exception as e_voz:
                    st.error(f"Fallo en enlace de voz: {e_voz}")
                    
    except Exception as e:
        st.error(f"Error en el sistema: {e}")
        
        


# --- MOSTRAR CHAT ---
for item in reversed(st.session_state.chat_history):
    autor = item.get("autor", "Desconocido")
    msg = item.get("msg", "")
    avatar = "👓" if autor == "EDITH" else "👤"
    with st.chat_message("assistant" if autor == "EDITH" else "user", avatar=avatar):
        st.write(f"**{autor}:** {msg}")

# --- MOTOR DE ALARMAS EN SEGUNDO PLANO ---
import time
if st.session_state.alarmas_activas:
    alarmas_restantes = []
    for alarma in st.session_state.alarmas_activas:
        tiempo_restante = alarma["end_time"] - time.time()

        if tiempo_restante > 0:
            # Inyectamos el reloj JavaScript para que corra independientemente en el navegador
            ms_restantes = int(tiempo_restante * 1000)
            js_timer = f"""
                <script>
                    setTimeout(function() {{
                        var audio = new Audio("data:audio/mpeg;base64,{alarma['audio']}");
                        audio.play();
                    }}, {ms_restantes});
                </script>
            """
            st.components.v1.html(js_timer, height=0)
            alarmas_restantes.append(alarma) # Sigue activa
        else:
            # Si el tiempo ya pasó (ej. recargaste la página después de que expiró)
            js_play = f"""
                <script>
                    var audio = new Audio("data:audio/mpeg;base64,{alarma['audio']}");
                    audio.play();
                </script>
            """
            st.components.v1.html(js_play, height=0)

    # Actualizamos la memoria, borrando las alarmas que ya sonaron
    st.session_state.alarmas_activas = alarmas_restantes

