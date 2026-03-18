import warnings
warnings.filterwarnings("ignore") 

import speech_recognition as sr
import pyttsx3
from google import genai
from google.genai import types

# CONFIGURACIÓN DE VOZ
engine = pyttsx3.init()
engine.setProperty('rate', 175) 
voces = engine.getProperty('voices')
for voz in voces:
    if "pablo" in voz.name.lower() or "raul" in voz.name.lower():
        engine.setProperty('voice', voz.id)
        break

# CONFIGURACIÓN DE IA (Pon tu clave nueva aquí)
API_KEY = "TU_NUEVA_API_KEY" 
client = genai.Client(api_key=API_KEY)
instrucciones = "Eres J.A.R.V.I.S., la IA de Tony Stark. Llama al usuario 'Mary'."
configuracion_ia = types.GenerateContentConfig(system_instruction=instrucciones, temperature=0.7)

recognizer = sr.Recognizer()

def hablar(texto):
    texto_limpio = texto.replace("*", "").replace("#", "").replace("```", "")
    engine.say(texto_limpio)
    engine.runAndWait()

def escuchar():
    with sr.Microphone(device_index=23) as source:
        # 1. Acortamos la calibración para que no se pierda en el ruido
        print("\n[J.A.R.V.I.S. Calibrando... Silencio un segundo]")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        # 2. AJUSTE CLAVE: Bajamos el umbral. 
        # Si es 300 y no entiende, probaremos con 100 o 50.
        recognizer.energy_threshold = 150 
        
        # 3. Evitamos que se quede esperando una eternidad
        recognizer.pause_threshold = 0.8 
        
        print("[J.A.R.V.I.S. ESCUCHANDO... Hable ahora]")
        try:
            # Escuchamos (máximo 5 segundos de frase)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("[Procesando...]")
            
            # 4. Probamos con español de España para ver si el servidor responde mejor
            texto = recognizer.recognize_google(audio, language="es-ES")
            print(f"> Mary: {texto}")
            return texto
            
        except sr.UnknownValueError:
            print("[INFO] El audio sigue llegando borroso.")
            return None
        except Exception as e:
            print(f"[ERROR]: {e}")
            return None

def iniciar_jarvis():
    hablar("Sistemas en línea. A su disposición, Mary.")
    while True:
        comando = escuchar()
        if comando:
            comando_min = comando.lower()
            if "apágate" in comando_min or "salir" in comando_min:
                hablar("Desconectando. Hasta pronto, Mary.")
                break
            try:
                respuesta = client.models.generate_content(
                    model='gemini-2.0-flash', contents=comando, config=configuracion_ia
                )
                print(f"J.A.R.V.I.S: {respuesta.text}")
                hablar(respuesta.text)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    iniciar_jarvis()