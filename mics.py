import speech_recognition as sr

print("Micrófonos detectados por Python:")
for indice, nombre in enumerate(sr.Microphone.list_microphone_names()):
    print(f"[{indice}] {nombre}")