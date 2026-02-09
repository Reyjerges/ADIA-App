import gradio as gr
from groq import Groq
import os

# 1. Configuración del Cliente
# En Render, es mejor usar variables de entorno para la seguridad
api_key = os.environ.get("GROQ_API_KEY", "TU_API_KEY_AQUI")
client = Groq(api_key=api_key)

SYSTEM_PROMPT = """
Eres ADIA, una IA compañera. Tu misión es ayudar al usuario. 
Si te piden juegos, genera un único bloque de código HTML/JS/CSS.
"""

def chat_with_adia(message, history):
    # Convertimos historial de forma simple
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    
    messages.append({"role": "user", "content": message})

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=0.7
    )
    
    return completion.choices[0].message.content

# 2. Interfaz Limpia (Sin Type Hints)
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 ADIA Canvas")
    
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(label="Chat con ADIA")
            msg = gr.Textbox(label="Instrucciones para el juego")
            btn = gr.Button("Enviar")

        with gr.Column():
            canvas = gr.HTML(" <center> Esperando creación... </center> ")
            code_out = gr.Code(label="Código generado", language="html")

    def process_interaction(message, chat_history):
        response = chat_with_adia(message, chat_history)
        chat_history.append((message, response))
        
        # Extracción simple de código
        html_content = ""
        if "```html" in response:
            html_content = response.split("```html")[1].split("```")[0]
        
        return "", chat_history, html_content, html_content

    btn.click(process_interaction, [msg, chatbot], [msg, chatbot, canvas, code_out])

if __name__ == "__main__":
    demo.launch()
    
