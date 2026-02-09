import gradio as gr
from groq import Groq
import os
import re

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_html(text):
    match = re.search(r"```html\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1)
    if "<html>" in text.lower():
        return text
    return f"<div style='padding:20px; font-family:sans-serif;'>{text}</div>"

def adia_chat(message, history):
    # Convertimos el historial de tuplas a formato Groq
    messages = [{"role": "system", "content": "Eres ADIA. Si creas juegos, usa bloques ```html ... ```"}]
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    
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
    gr.Markdown("# 🤖 ADIA Canvas")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Usamos el formato clásico de Gradio (lista de listas)
            chatbot = gr.Chatbot(height=500)
            msg = gr.Textbox(placeholder="Pídeme un juego en HTML...")
            
            def respond(message, chat_history):
                # Inicializamos la respuesta de la IA
                chat_history.append([message, ""])
                
                # Llamamos a la IA pasándole el historial previo
                # (excluimos el último par que acabamos de añadir)
                response_gen = adia_chat(message, chat_history[:-1])
                
                for part in response_gen:
                    chat_history[-1][1] = part
                    yield "", chat_history, extract_html(part)

            msg.submit(respond, [msg, chatbot], [msg, chatbot, canvas := gr.HTML(visible=False)])

        with gr.Column(scale=2):
            gr.Markdown("### 🎨 Canvas")
            canvas = gr.HTML("<div style='padding:20px;'>El contenido interactivo aparecerá aquí.</div>")

    # Vinculamos de nuevo el canvas para que se actualice en la función respond
    msg.submit(respond, [msg, chatbot], [msg, chatbot, canvas])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0") # Recomendado para Render
