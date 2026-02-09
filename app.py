import gradio as gr
from groq import Groq
import os
import re

# Configura tu API KEY en Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_html(history):
    if not history: return "Sin contenido"
    # El historial aquí es una lista de listas: [[user, bot], [user, bot]]
    last_bot_msg = history[-1][1]
    match = re.search(r"```html\n(.*?)\n```", last_bot_msg, re.DOTALL)
    if match: return match.group(1)
    return f"<div style='padding:20px;'>{last_bot_msg}</div>"

def responder(message, history):
    # Convertir historial de listas a formato Groq (dict)
    messages = [{"role": "system", "content": "Eres ADIA. Si creas juegos, usa bloques ```html"}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    
    messages.append({"role": "user", "content": message})

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        stream=True
    )

    full_response = ""
    for chunk in completion:
        if chunk.choices.delta.content:
            full_response += chunk.choices.delta.content
            yield full_response

with gr.Blocks(fill_height=True) as demo:
    gr.Markdown("# 🤖 ADIA System (Core Edition)")
    
    mode = gr.Radio(["Chat Normal", "Modo Canvas"], value="Chat Normal", label="Entorno")

    with gr.Row():
        # COLUMNA CHAT
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(height=500)
            txt = gr.Textbox(show_label=False, placeholder="Escribe un mensaje y presiona Enter...")
            btn_enviar = gr.Button("Enviar")

        # COLUMNA CANVAS
        with gr.Column(scale=1, visible=False) as canvas_col:
            gr.Markdown("### 🎨 Canvas")
            canvas_view = gr.HTML("Carga un juego o código...")

    # Lógica de procesamiento
    def chat_engine(msg, history):
        # 1. Añadir mensaje del usuario al chat
        new_history = history + [[msg, ""]]
        yield "", new_history, gr.update()
        
        # 2. Obtener respuesta de la IA
        response_gen = responder(msg, history)
        for partial_res in response_gen:
            new_history[-1][1] = partial_res
            # Actualizamos chat y canvas en tiempo real
            yield "", new_history, extract_html(new_history)

    # Eventos (Enter y Botón)
    txt.submit(chat_engine, [txt, chatbot], [txt, chatbot, canvas_view])
    btn_enviar.click(chat_engine, [txt, chatbot], [txt, chatbot, canvas_view])

    # Switch de modo
    mode.change(lambda x: gr.update(visible=(x == "Modo Canvas")), mode, canvas_col)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
