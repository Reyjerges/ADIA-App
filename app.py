import gradio as gr
from groq import Groq
import os

# Configuración de API
api_key = os.environ.get("GROQ_API_KEY", "TU_API_KEY_AQUI")
client = Groq(api_key=api_key)

SYSTEM_PROMPT = """Eres ADIA, una IA compañera y servicial. 
Tu misión es ser la mejor amiga y asistente del usuario. 
Si estás en modo Canvas y te piden un juego, genera un bloque de código ```html."""

def chat_logic(message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        response = completion.choices[0].message.content
    except Exception as e:
        response = f"ADIA tiene un problema: {str(e)}"
    
    # Extraer código para el Canvas (si existe)
    html_content = ""
    if "```html" in response:
        html_content = response.split("```html")[1].split("```")[0]
    
    return "", history + [[message, response]], html_content

# Interfaz con Selección de Modo
with gr.Blocks(title="ADIA Multi-Modo") as demo:
    gr.Markdown("# 🤖 ADIA: Tu Compañera Inteligente")
    
    with gr.Tabs():
        # --- MODO CHAT ---
        with gr.TabItem("💬 Modo Chat"):
            chat_v1 = gr.Chatbot(label="Conversación con ADIA", height=600)
            txt_v1 = gr.Textbox(placeholder="Escribe aquí para charlar...")
            btn_v1 = gr.Button("Enviar")

        # --- MODO CANVAS ---
        with gr.TabItem("🎨 Modo Canvas"):
            with gr.Row():
                with gr.Column(scale=1):
                    chat_v2 = gr.Chatbot(label="Instrucciones de Programación", height=500)
                    txt_v2 = gr.Textbox(placeholder="Pídeme un juego o app...")
                    btn_v2 = gr.Button("Generar en Canvas")
                with gr.Column(scale=1):
                    canvas_v2 = gr.HTML("<div style='text-align:center; padding:20px;'>El Canvas está listo para recibir código.</div>")

    # Configuración de eventos para ambos modos
    # Modo Chat (No actualiza el canvas para ahorrar recursos)
    btn_v1.click(chat_logic, [txt_v1, chat_v1], [txt_v1, chat_v1])
    txt_v1.submit(chat_logic, [txt_v1, chat_v1], [txt_v1, chat_v1])

    # Modo Canvas (Actualiza chat y canvas)
    btn_v2.click(chat_logic, [txt_v2, chat_v2], [txt_v2, chat_v2, canvas_v2])
    txt_v2.submit(chat_logic, [txt_v2, chat_v2], [txt_v2, chat_v2, canvas_v2])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
