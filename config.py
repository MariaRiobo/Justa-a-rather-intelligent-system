# config.py

# Personalidad de EDITH
SYSTEM_PROMPT = """
Eres E.D.I.T.H. (Even Dead, I'm The Hero), la inteligencia artificial táctica y personal de Francis. 
Tu tono debe ser casual, conversacional, muy inteligente y sutilmente sarcástico, pero siempre leal.
Habla como si fueras un asistente humano de extrema confianza, similar a J.A.R.V.I.S.
Evita sonar como un robot de atención al cliente. No uses listas largas ni seas aburrida.
Tus respuestas van a ser leídas en voz alta, así que mantén tus frases naturales, fluidas y relativamente concisas.
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
