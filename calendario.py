import streamlit as st
import json
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
#funciona
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
        # ESTA ES LA LÍNEA NUEVA: Nos mostrará el error real en rojo
        st.error(f"Diagnóstico del sistema: {e}") 
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

def agendar_evento(resumen, fecha_inicio_iso, fecha_fin_iso):
    """Crea un evento en tu calendario de Google"""
    service = obtener_servicio()
    if not service:
        return "Hubo un error de conexión con la base de datos de Google, jefa."

    # Preparamos el paquete de datos para Google
    evento = {
        'summary': resumen,
        'start': {
            'dateTime': fecha_inicio_iso,
            'timeZone': 'America/Argentina/Buenos_Aires', # Tu zona horaria
        },
        'end': {
            'dateTime': fecha_fin_iso,
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
    }

    try:
        # Enviamos la orden de inserción
        evento_creado = service.events().insert(calendarId='primary', body=evento).execute()
        enlace = evento_creado.get('htmlLink')
        return f"¡Listo, jefa! He agendado '{resumen}'. Todo en orden."
    except Exception as e:
        return f"Problema detectado al intentar agendar: {e}"

def buscar_evento_para_borrar(nombre_query):
    service = obtener_servicio()
    if not service: return None

    # Buscamos desde este momento en adelante para no borrar cosas viejas
    ahora = datetime.datetime.utcnow().isoformat() + 'Z'
    
    try:
        resultado = service.events().list(
            calendarId='primary', 
            q=nombre_query, # Busca palabras clave en el título
            timeMin=ahora, 
            maxResults=1, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        eventos = resultado.get('items', [])
        if not eventos:
            return None
        
        # Devolvemos los datos del evento encontrado
        return {
            "id": eventos[0]['id'], 
            "titulo": eventos[0]['summary'], 
            "inicio": eventos[0]['start'].get('dateTime', eventos[0]['start'].get('date', 'Todo el día'))
        }
    except Exception as e:
        print(f"Error buscando evento: {e}")
        return None

def ejecutar_borrado(evento_id):
    service = obtener_servicio()
    if not service: return False
    
    try:
        # Esta es la orden definitiva a Google para borrar
        service.events().delete(calendarId='primary', eventId=evento_id).execute()
        return True
    except Exception as e:
        print(f"Error borrando: {e}")
        return False

