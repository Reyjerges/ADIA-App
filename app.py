import gradio as gr
from groq import Groq
import os
import re

# Cliente Llama 3
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_html(history):
    if not history: return ""
    # Sacamos el contenido del último mensaje del asistente
    last_msg = history[-1][1] 
    match = re.search(r"```html\n(.*?)\n```", last_msg, re.DOTALL)
    if match: return match.group(1)
    return f"<div style='padding:20px;'>{last_msg}</div>"

def responder(message, history):
    # CORRECCIÓN AQUÍ: Convertimos el historial a diccionarios compatibles con Llama 3
    messages = [{"role": "system", "content": "Eres ADIA. Usa bloques ```html para juegos."}]
    
    for user_msg, assistant_msg in history:
        if user_msg: messages.append({"role": "user", "content": user_msg})
        if assistant_msg: messages.append({"role": "assistant", "content": assistant_msg})
    
    messages.append({"role": "user", "content": message})

    # Llamada a la API
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
    gr.Markdown("# 🤖 ADIA System")
    
    with gr.Row():
        mode = gr.Radio(["Chat Normal", "Modo Canvas"], value="Chat Normal", label="Entorno")

    with gr.Row():
        # Chat
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(height=500)
            txt = gr.Textbox(placeholder="Escribe y presiona Enter...")
            btn = gr.Button("Enviar")

        # Canvas
        with gr.Column(scale=1, visible=False) as canvas_col:
            gr.Markdown("### 🎨 Canvas")
            canvas_view = gr.HTML("Esperando código...")

    def chat_engine(msg, history):
        # 1. Agregamos el mensaje del usuario al historial visual
        history = history + [[msg, ""]]
        yield "", history, gr.update()
        
        # 2. Generamos la respuesta
        response_gen = responder(msg, history[:-1]) # Enviamos historial previo
        for partial_res in response_gen:
            history[-1][1] = partial_res
            # 3. Actualizamos chat y canvas al mismo tiempo
            yield "", history, extract_html(history)

    # Eventos
    txt.submit(chat_engine, [txt, chatbot], [txt, chatbot, canvas_view])
    btn.click(chat_engine, [txt, chatbot], [txt, chatbot, canvas_view])
    
    # Toggle Canvas
    mode.change(lambda x: gr.update(visible=(x == "Modo Canvas")), mode, canvas_col)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
