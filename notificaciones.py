import requests
import streamlit as st

def enviar_pushover(mensaje, titulo="E.D.I.T.H.", sonido="shimmer"):
    """Envía una notificación con sonido personalizado."""
    import streamlit as st
    import requests

    user_key = st.secrets["pushover"]["user_key"]
    api_token = st.secrets["pushover"]["api_token"]
    
    
    url = "https://api.pushover.net/1/messages.json"
    
    data = {
        "token": api_token,
        "user": user_key,
        "message": mensaje,
        "title": titulo,
        "sound": siren, # Aquí va el nombre del sonido
        "priority": 1
    }
    
    requests.post(url, data=data, timeout=7)
