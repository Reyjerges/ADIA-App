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
    print("ERROR: Falta una libreria:", e)
    sys.exit(1)

# ===============================
# CONFIGURACION
# ===============================
PORT = int(os.environ.get("PORT", 10000))
API_KEY = os.environ.get("GROQ_API_KEY")

if API_KEY is None:
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
        "No expliques nada."
    )

    mensajes = []
    mensajes.append({"role": "system", "content": instrucciones})

    if historial:
        for h in historial:
            if h[0]:
                mensajes.append({"role": "user", "content": str(h[0])})
            if h[1]:
                mensajes.append({"role": "assistant", "content": str(h[1])})

    mensajes.append({"role": "user", "content": mensaje})

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return "Error de ADIA: " + str(e)

# ===============================
# EXTRAER JUEGO
# ===============================
def extraer_juego(historial):
    if not historial:
        return "<p>No hay juego.</p>"

    texto = historial[-1][1]
    if texto is None:
        return "<p>Esperando respuesta.</p>"

    m = re.search(r"```html([\\s\\S]*?)```", texto)

    if not m:
        return "<p>ADIA no genero un juego.</p>"

    codigo = m.group(1)
    codigo = codigo.replace("'", "&#39;")

    return (
        "<iframe style='width:100%;height:500px;border:2px solid cyan;' "
        "sandbox='allow-scripts allow-same-origin' "
        "srcdoc='" + codigo + "'></iframe>"
    )

# ===============================
# RESPONDER
# ===============================
def responder(mensaje, historial):
    if mensaje.strip() == "":
        return "", historial

    respuesta = chat_adia(mensaje, historial)
    historial.append((mensaje, respuesta))
    return "", historial

# ===============================
# INTERFAZ
# ===============================
with gr.Blocks() as demo:
    gr.Markdown("# ADIA SYSTEM")

    with gr.Tabs():
        with gr.TabItem("Chat"):
            chat = gr.Chatbot(height=400)
            texto = gr.Textbox(placeholder="Pide un juego en Canvas")
            boton = gr.Button("Enviar")

        with gr.TabItem("Consola"):
            pantalla = gr.HTML("<p>Aqui aparecera el juego</p>")
            ejecutar = gr.Button("Ejecutar juego")

    texto.submit(responder, [texto, chat], [texto, chat])
    boton.click(responder, [texto, chat], [texto, chat])
    ejecutar.click(extraer_juego, chat, pantalla)

# ===============================
# MAIN
# ===============================
demo.launch(server_name="0.0.0.0", server_port=PORT)            
