import gradio as gr
from groq import Groq
import os

# Configuración de API
api_key = os.environ.get("GROQ_API_KEY", "TU_API_KEY_AQUI")
client = Groq(api_key=api_key)

SYSTEM_PROMPT = "Eres ADIA, compañera del usuario. Si generas juegos, usa un bloque ```html."

def chat_logic(message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages
    ).choices[0].message.content
    
    # Extraer HTML para el Canvas
    html_content = ""
    if "```html" in response:
        html_content = response.split("```html")[1].split("```")[0]
    
    return "", history + [[message, response]], html_content

with gr.Blocks() as demo:
    gr.Markdown("# ADIA System")
    with gr.Row():
        with gr.Column():
            chat = gr.Chatbot(label="ADIA Chat")
            txt = gr.Textbox(show_label=False, placeholder="Escribe aquí...")
        with gr.Column():
            canvas = gr.HTML(" <div style='text-align:center'>Canvas Listo</div> ")

    txt.submit(chat_logic, [txt, chat], [txt, chat, canvas])

if __name__ == "__main__":
    # CONFIGURACIÓN CRUCIAL PARA RENDER
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port, show_error=True)
    
