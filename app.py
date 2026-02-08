import os
import re
import sys
import gradio as gr
from groq import Groq

# ===============================
# CONFIGURACIÓN
# ===============================
PORT = int(os.environ.get("PORT", 7860))
API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    print("ERROR: Falta la GROQ_API_KEY")
    sys.exit(1)

client = Groq(api_key=API_KEY)

# ===============================
# FUNCIONES
# ===============================
def chat_adia(mensaje, historial):
    instrucciones = (
        "Eres ADIA, experta en juegos HTML5 Canvas. "
        "Responde SOLO con el código en un bloque ```html```. "
        "No hables ni expliques nada."
    )

    # Creamos la lista de mensajes (Formato que exige la API)
    mensajes_api = [{"role": "system", "content": instrucciones}]

    # Agregamos el historial correctamente
    if historial:
        for chat in historial:
            # Gradio guarda el historial como [usuario, bot]
            if chat[0]:
                mensajes_api.append({"role": "user", "content": str(chat[0])})
            if chat[1]:
                mensajes_api.append({"role": "assistant", "content": str(chat[1])})

    # Agregamos el mensaje nuevo
    mensajes_api.append({"role": "user", "content": mensaje})

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error en la API: {str(e)}"

def responder(mensaje, historial):
    if not mensaje.strip():
        return "", historial
    
    # Obtenemos respuesta de la IA
    bot_res = chat_adia(mensaje, historial)
    
    # Actualizamos el historial (Lista de listas)
    historial.append([mensaje, bot_res])
    return "", historial

def extraer_juego(historial):
    if not historial:
        return "<p>No hay juego.</p>"
    
    texto = historial[-1][1]
    m = re.search(r"```html([\s\S]*?)```", texto)
    
    if not m:
        return "<p>No se encontró código HTML.</p>"
    
    codigo = m.group(1).replace("'", "&#39;")
    return f"<iframe style='width:100%; height:500px; background:white;' srcdoc='{codigo}'></iframe>"

# ===============================
# INTERFAZ
# ===============================
with gr.Blocks() as demo:
    gr.Markdown("# ADIA SYSTEM")
    
    with gr.Tabs():
        with gr.TabItem("Chat"):
            chatbot = gr.Chatbot()
            texto = gr.Textbox(placeholder="Pide un juego...")
            boton = gr.Button("Enviar")
            
        with gr.TabItem("Juego"):
            ejecutar = gr.Button("Cargar Juego")
            pantalla = gr.HTML("Esperando...")

    boton.click(responder, [texto, chatbot], [texto, chatbot])
    texto.submit(responder, [texto, chatbot], [texto, chatbot])
    ejecutar.click(extraer_juego, chatbot, pantalla)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=PORT)
    
