import gradio as gr
from groq import Groq
import os
import re

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_html(history):
    if not history or len(history) == 0: return ""
    # En Gradio 5, el historial es una lista de ChatMessage o dicts
    last_msg = history[-1]['content'] if isinstance(history[-1], dict) else history[-1].content
    match = re.search(r"```html\n(.*?)\n```", last_msg, re.DOTALL)
    if match: return match.group(1)
    return f"<div style='padding:20px; font-family:sans-serif;'>{last_msg}</div>"

def adia_chat(message, history):
    messages = [{"role": "system", "content": "Eres ADIA. Si el modo Canvas está activo, genera código en bloques ```html"}]
    for msg in history:
        messages.append(msg)
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

# Interfaz
with gr.Blocks(fill_height=True) as demo:
    gr.Markdown("# 🤖 ADIA System")
    
    # Selector de Modo
    mode_selector = gr.Radio(
        choices=["Chat Normal", "Modo Canvas"], 
        value="Chat Normal", 
        label="Selecciona el entorno de trabajo"
    )

    with gr.Row() as main_row:
        # Columna de Chat
        with gr.Column(scale=1, elem_id="chat_col") as chat_col:
            chatbot = gr.ChatInterface(
                fn=adia_chat,
                type="messages"
            )

        # Columna de Canvas (Se oculta/muestra)
        with gr.Column(scale=1, visible=False) as canvas_col:
            gr.Markdown("### 🎨 ADIA Canvas")
            canvas_area = gr.HTML("Lanza un juego o código para empezar...")
            btn_refresh = gr.Button("Actualizar Canvas 🔄")

    # Lógica para cambiar entre Normal y Canvas
    def toggle_mode(choice):
        if choice == "Modo Canvas":
            return gr.update(visible=True)
        return gr.update(visible=False)

    mode_selector.change(toggle_mode, inputs=mode_selector, outputs=canvas_col)
    
    # Actualizar canvas automáticamente al hacer clic en el botón
    btn_refresh.click(extract_html, inputs=chatbot.chatbot, outputs=canvas_area)

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto
    demo.launch(server_name="0.0.0.0", server_port=10000)
