import requests

# --- CREDENCIALES PUSHOVER ---
user_key = "TU_USER_KEY_REAL"
api_token = "TU_API_TOKEN_REAL"

def enviar_pushover(mensaje, titulo="E.D.I.T.H. - Alerta"):
    """Envía una notificación push inmediata al iPhone."""
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": API_TOKEN,
        "user": USER_KEY,
        "message": mensaje,
        "title": titulo,
        "sound": "shimmer",  # Puedes probar con: 'intermission', 'magic', o 'alien'
        "priority": 1        # Prioridad alta para que salte en el iPhone
    }
    
    try:
        response = requests.post(url, data=data, timeout=7)
        return response.ok
    except Exception as e:
        print(f"Fallo en el enlace de Pushover: {e}")
        return False
