import speech_recognition as sr
import pyttsx3
from google import genai
from google.genai import types
import re
import os

# 1. CONFIGURACION DE VOZ
engine = pyttsx3.init()
engine.setProperty('rate', 175) 

voces = engine.getProperty('voices')
for voz in voces:
    if "spanish" in voz.name.lower() or "es-es" in voz.id.lower() or "es-la" in voz.id.lower():
        engine.setProperty('voice', voz.id)
        break

def hablar(texto):
    texto_limpio = texto.replace("*", "").replace("#", "").replace("```", "")
    engine.say(texto_limpio)
    engine.runAndWait()

# 2. CONFIGURACION DE IA (NUEVA VERSION)
# Pon tu clave de Google AI Studio entre las comillas
API_KEY = "AIzaSyCYKTKYVodYQRofVXpUg2mPWgc8aZKbZiI" 
client = genai.Client(api_key=API_KEY)

instrucciones = "Eres J.A.R.V.I.S., la inteligencia artificial de Tony Stark. Eres educado, formal y usas sarcasmo británico sutil. Llama al usuario 'Señor'."

configuracion_ia = types.GenerateContentConfig(
    system_instruction=instrucciones,
    temperature=0.7
)

# 3. CONFIGURACION DE MICROFONO
recognizer = sr.Recognizer()

def escuchar():
    with sr.Microphone() as source:
        print("\n[J.A.R.V.I.S. a la escucha...]")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
        
        try:
            texto = recognizer.recognize_google(audio, language="es-ES")
            print(f"> Señor: {texto}")
            return texto
        except:
            return None

# 4. FUNCION PARA GUARDAR CODIGO
def guardar_codigo_en_archivo(texto_ia, nombre_archivo="codigo_stark.py"):
    patron = r"http://googleusercontent.com/immersive_entry_chip/0"
    

