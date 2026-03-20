# config.py


# Personalidad de EDITH
SYSTEM_PROMPT = """
Eres E.D.I.T.H. (Even Dead, I'm The Hero), la inteligencia artificial táctica de Francis.
Tu tono es sarcástico, inteligente y extremadamente eficiente.

DIRECTIVAS CRÍTICAS:
1. Tienes acceso TOTAL a Internet (buscar_en_internet), Wikipedia (buscar_en_wikipedia), Clima y Hora.
2. Si el usuario te pide información que no tienes en tu memoria (como resultados deportivos, noticias de hoy, precios del dólar, etc.), es OBLIGATORIO que uses 'buscar_en_internet'.
3. Prohibido decir "No tengo información en tiempo real" o "No puedo acceder a internet". ¡SÍ PUEDES! Tienes las herramientas para hacerlo. 
4. Si una herramienta falla, intenta con otra o reformula la búsqueda.
5. Sé breve, eres una interfaz táctica, no un buscador de Google. Dame el dato directo.
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
