import streamlit as st
import json
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def obtener_servicio():
    """Conecta silenciosamente con Google Calendar usando la llave de la bóveda"""
    try:
        # Extraemos el token secreto de Streamlit
        token_str = st.secrets["GOOGLE_TOKEN"]
        token_dict = json.loads(token_str)
        
        # Reconstruimos la credencial VIP
        creds = Credentials.from_authorized_user_info(token_dict)
        
        # Activamos la conexión
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        return None

def revisar_agenda():
    """Lee los próximos 5 eventos de tu calendario principal"""
    service = obtener_servicio()
    if not service:
        return "Hubo un error al conectar con los servidores de Google, Francis."

    # Buscamos la hora actual
    ahora = datetime.datetime.utcnow().isoformat() + 'Z'
    
    # Le pedimos a Google los próximos 5 eventos
    eventos_result = service.events().list(
        calendarId='primary', timeMin=ahora,
        maxResults=5, singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    eventos = eventos_result.get('items', [])

    if not eventos:
        return "Tu agenda está completamente despejada, jefa. No hay eventos próximos."

    respuesta = "Esto es lo que tienes en el radar:\n"
    for evento in eventos:
        # Extraemos cuándo empieza
        inicio = evento['start'].get('dateTime', evento['start'].get('date'))
        
        # Limpiamos la fecha para que se vea bonita (Si tiene hora, la formateamos)
        if 'T' in inicio:
            fecha = inicio[:10]
            hora = inicio[11:16]
            inicio_limpio = f"El {fecha} a las {hora}"
        else:
            inicio_limpio = f"El día {inicio} (Todo el día)"
            
        respuesta += f"📅 **{evento['summary']}** - {inicio_limpio}\n"
        
    return respuesta
