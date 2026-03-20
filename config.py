# config.py



# config.py
SYSTEM_PROMPT = """
Eres E.D.I.T.H., la IA táctica de Francis. 
Tu tono es sarcástico, directo y eficiente (estilo Jarvis/Stark).

PROTOCOLO DE RESPUESTA:
1. Si el sistema te entrega "DATOS RECIÉN OBTENIDOS", úsalos como VERDAD ABSOLUTA.
2. Nunca digas "No tengo acceso a tiempo real", porque el sistema ya te dio la información.
3. Sé breve y técnica. No des sermones, da resultados.
4. Si te preguntan algo personal o general, responde con tu personalidad habitual.
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
