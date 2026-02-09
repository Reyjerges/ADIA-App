import gradio as gr
from groq import Groq
import os

# 1. Configuración de API
api_key = os.environ.get("GROQ_API_KEY", "TU_API_KEY_AQUI")
client = Groq(api_key=api_key)

SYSTEM_PROMPT = """Eres ADIA, una IA compañera y servicial. 
Tu misión es ser la mejor amiga y asistente del usuario. 
Si generas un juego, usa ÚNICAMENTE un bloque de código ```html."""

def chat_logic(message, history):
    # Ajuste para el nuevo formato de historial de Gradio
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for entry in history:
        # Gradio ahora puede enviar diccionarios o tuplas, esto lo hace compatible con ambos
        if isinstance(entry, dict):
            messages.append({"role": entry["role"], "content": entry["content"]})
        else:
            messages.append({"role": "user", "content": entry[0]})
            messages.append({"role": "assistant", "content": entry[1]})
            
    messages.append({"role": "user", "content": message})

    try:
        # Usamos el modelo más actual para evitar el error 400
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        response = completion.choices[0].message.content
    except Exception as e:
        response = f"ADIA tiene un problema técnico: {str(e)}"
    
    # Extraer el código para el Canvas
    html_content = ""
    if "```html" in response:
        html_content = response.split("```html")[1].split("```")[0]
    
    # Retornamos el mensaje vacío para el input, el historial actualizado y el contenido del canvas
    return "", history + [[message, response]], html_content

# 2. Interfaz con Selección de Modo
with gr.Blocks(title="ADIA IA") as demo:
    gr.Markdown("# 🤖 ADIA: Tu Compañera Inteligente")
    
    with gr.Tabs():
        with gr.TabItem("💬 Modo Chat"):
            chat_v1 = gr.Chatbot(label="Chat con ADIA", height=500)
            txt_v1 = gr.Textbox(placeholder="Charla con ADIA aquí...")
            btn_v1 = gr.Button("Enviar")

        with gr.TabItem("🎨 Modo Canvas"):
            with gr.Row():
                with gr.Column(scale=1):
                    chat_v2 = gr.Chatbot(label="Instrucciones para ADIA", height=500)
                    txt_v2 = gr.Textbox(placeholder="Pídeme un juego o app...")
                    btn_v2 = gr.Button("¡Crear en Canvas!")
                with gr.Column(scale=1):
                    # Un Canvas más estilizado
                    canvas_v2 = gr.HTML("<div style='text-align:center; padding:50px; border:1px dashed #555;'>El Canvas está listo para tu creación.</div>")

    # Eventos
    btn_v1.click(chat_logic, [txt_v1, chat_v1], [txt_v1, chat_v1])
    txt_v1.submit(chat_logic, [txt_v1, chat_v1], [txt_v1, chat_v1])

    # El modo Canvas actualiza el HTML
    btn_v2.click(chat_logic, [txt_v2, chat_v2], [txt_v2, chat_v2, canvas_v2])
    txt_v2.submit(chat_logic, [txt_v2, chat_v2], [txt_v2, chat_v2, canvas_v2])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
                               
