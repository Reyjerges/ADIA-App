# ===============================
# IMPORTS
# ===============================
import os
import re
import sys

try:
    import gradio as gr
    from groq import Groq
except Exception as e:
    print(f"ERROR: Falta una librería: {e}")
    sys.exit(1)

# ===============================
# CONFIGURACIÓN
# ===============================
PORT = int(os.environ.get("PORT", 10000))
API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    print("ERROR: GROQ_API_KEY no configurada")
    sys.exit(1)

client = Groq(api_key=API_KEY)

# ===============================
# CHAT ADIA
# ===============================
def chat_adia(mensaje, historial):
    instrucciones = (
        "Eres ADIA, la IA personal creada por Jorge. "
        "Eres experta en juegos HTML5 Canvas. "
        "Si te piden un juego, responde con UN solo bloque ```html``` "
        "que incluya un canvas y todo el JS dentro de <script>. "
        "No expliques nada, solo da el código."
    )

    # Iniciamos la lista de mensajes con el sistema
    mensajes = [{"role": "system", "content": instrucciones}]

    # Añadimos el historial previo a la lista
    for usuario, asistente in historial:
        if usuario:
            mensajes.append({"role": "user", "content": str(usuario)})
        if asistente:
            mensajes.append({"role": "assistant", "content": str(asistente)})

    # Añadimos el mensaje actual
    mensajes.append({"role": "user", "content": mensaje})

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error de ADIA: {e}"

# ===============================
# EXTRAER JUEGO
# ===============================
def extraer_juego(historial):
    if not historial or len(historial) == 0:
        return "<p>No hay juego para mostrar.</p>"

    # Obtenemos la última respuesta del asistente
    ultimo_intercambio = historial[-1]
    texto = ultimo_intercambio[1]

    if not texto:
        return "<p>Esperando respuesta...</p>"

    m = re.search(r"```html([\s\S]*?)```", texto)

    if not m:
        return "<p>ADIA no generó un bloque de código HTML válido.</p>"

    codigo = m.group(1).replace("'", "&#39;")

    return (
        f"<iframe style='width:100%; height:500px; border:2px solid cyan; background: white;' "
        f"sandbox='allow-scripts allow-same-origin' "
        f"srcdoc='{codigo}'></iframe>"
    )

# ===============================
# RESPONDER
# ===============================
def responder(mensaje, historial):
    if not mensaje.strip():
        return "", historial

    respuesta = chat_adia
