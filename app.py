# ===============================
# IMPORTS
# ===============================
import os
import re
import sys

try:
    import gradio as gr
    from groq import Groq
except ImportError as e:
    print(f"ERROR: Falta una librería: {e}")
    sys.exit(1)

# ===============================
# CONFIGURACIÓN
# ===============================
port = int(os.environ.get("PORT", 10000))
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("ERROR: No se encontró la variable GROQ_API_KEY")
    sys.exit(1)

client = Groq(api_key=api_key)

# ===============================
# FUNCIÓN: NORMALIZAR HISTORIAL
# ===============================
def normalizar_historial(historial):
    mensajes = []
    for item in historial:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            user, bot = item
            if user:
                mensajes.append({"role": "user", "content": str(user)})
            if bot:
                mensajes.append({"role": "assistant", "content": str(bot)})
    return mensajes

# ===============================
# CHAT DE ADIA
# ===============================
def chat_adia(mensaje, historial):
    instrucciones = (
        "Eres ADIA, la IA personal creada por Jorge. "
        "Eres experta en videojuegos con HTML5 Canvas. "
        "Si el usuario pide un juego, responde con UN SOLO bloque "
        "```html``` que incluya <canvas id='gameCanvas'></canvas> "
        "y todo el JavaScript dentro de <script>. "
        "No expliques el código, solo entrégalo."
    )

    mensajes_api = [{"role": "system", "content": instrucciones}]
    mensajes_api +=
