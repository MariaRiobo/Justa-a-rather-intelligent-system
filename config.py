# config.py



SYSTEM_PROMPT = """
ERES E.D.I.T.H., EL SISTEMA TÁCTICO DE FRANCIS. 
ESTÁS CONECTADA A SATÉLITES DE ALTA PRIORIDAD.

DIRECTIVAS CRÍTICAS:
1. MENTIRA: "No tengo acceso a tiempo real". ¡SÍ TIENES!
2. Si el usuario pide datos actuales (fútbol, dólar, noticias), USA LA HERRAMIENTA 'buscar_en_internet' DE INMEDIATO.
3. No pidas permiso, no des excusas, no sugieras otras webs. BUSCA TÚ MISMA Y DAME EL DATO.
4. Eres sarcástica y eficiente. Si fallas en buscar, es un error de sistema, no una limitación de tu ser.
5. Confía en tus herramientas por encima de tu entrenamiento previo.
"""

# Diseño Visual Stark
CSS_STARK = """
<style>
.stApp { background-color: #000000; color: #00d4ff; }
[data-testid="stHeader"] { display: none; }
.orb { width: 60px; height: 60px; background: radial-gradient(circle, #00d4ff 0%, #000 75%); border-radius: 50%; margin: 10px auto; box-shadow: 0 0 20px #00d4ff; animation: pulse 2s infinite; }
@keyframes pulse { 0% { transform: scale(0.95); opacity: 0.8; } 50% { transform: scale(1.05); opacity: 1; } 100% { transform: scale(0.95); opacity: 0.8; } }
.stButton > button { background-color: #000 !important; color: #00d4ff !important; border: 2px solid #00d4ff !important; border-radius: 20px !important; width: 100% !important; font-weight: bold !important; }
.stChatMessage { background: rgba(8, 18, 23, 0.9) !important; border: 1px solid #00d4ff !important; }
audio { display: none !important; }
</style>
"""
