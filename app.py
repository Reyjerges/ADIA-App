import gradio as gr
from groq import Groq
import os
import re

# Cliente de Groq - Llama 3
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_html(history):
    if not history or len(history) == 0: return ""
    # El historial en formato antiguo es una lista de listas [[user, bot], ...]
    last_bot_msg = history[-1][1]
    match = re.search(r"```html\n(.*?)\n```", last_bot_msg, re.DOTALL)
    if match: return match.group(1)
    return f"<div style='padding:20px;'>{last_bot_msg}</div>"

def adia_response(message, history):
    # Convertimos el historial al formato que entiende Llama 3
    messages = [{"role": "system", "content": "Eres ADIA. Si el usuario pide un juego, usa bloques ```html"}]
    for user_m, bot_m in history:
        messages.append({"role": "user", "content": user_m})
        messages.append({"role": "assistant", "content": bot_m})
    
    messages.append({"role": "user", "content": message})

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        stream=True
    )

    response = ""
    for chunk in completion:
        if chunk.choices.delta.content:
            response += chunk.choices.delta.content
            yield response

with gr.Blocks(fill_height=True) as demo:
    gr.Markdown("# 🤖 ADIA System")
    
    mode_selector = gr.Radio(
        choices=["Chat Normal", "Modo Canvas"], 
        value="Chat Normal", 
        label="Selector de Interfaz"
    )

    with gr.Row():
        # Chat
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(height=500)
            msg = gr.Textbox(placeholder="Escribe aquí...")
            with gr.Row():
                btn_send = gr.Button("Enviar")
                btn_clear = gr.ClearButton([msg, chatbot])

        # Canvas (Derecha)
        with gr.Column(scale=1, visible=False) as canvas_col:
            gr.Markdown("### 🎨 ADIA Canvas")
            canvas_html = gr.HTML("Escribe algo para generar contenido...")

    # Lógica de Interacción
    def user_msg(message, history):
        return "", history + [[message, ""]]

    def bot_msg(history):
        user_message = history[-1][0]
        # Quitamos el último mensaje vacío para procesar el historial previo
        history_input = history[:-1]
        
        response_gen = adia_response(user_message, history_input)
        
        for part in response_gen:
            history[-1][1] = part
            yield history

    # Eventos
    msg.submit(user_msg, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_msg, chatbot, chatbot
    ).then(lambda h: extract_html(h), chatbot, canvas_html)

    btn_send.click(user_msg, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_msg, chatbot, chatbot
    ).then(lambda h: extract_html(h), chatbot, canvas_html)

    # Mostrar/Ocultar Canvas
    mode_selector.change(lambda x: gr.update(visible=(x == "Modo Canvas")), mode_selector, canvas_col)

if __name__ == "__main__":
    # Importante para el despliegue en Render
    demo.launch(server_name="0.0.0.0", server_port=10000)
