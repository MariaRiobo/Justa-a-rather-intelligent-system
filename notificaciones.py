import requests
import streamlit as st

def enviar_pushover(mensaje, titulo="E.D.I.T.H. - Alerta"):
    """Envía una notificación push usando credenciales seguras."""
    
    # Extraemos las llaves de forma segura desde los Secrets de Streamlit
    user_key = st.secrets["pushover"]["user_key"]
    api_token = st.secrets["pushover"]["api_token"]
    
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": api_token,
        "user": user_key,
        "message": mensaje,
        "title": titulo,
        "sound": "shimmer",
        "priority": 1
    }
    
    try:
        response = requests.post(url, data=data, timeout=7)
        return response.ok
    except Exception as e:
        print(f"Fallo en el enlace de seguridad: {e}")
        return False
