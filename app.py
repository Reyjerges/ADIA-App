import gradio as gr
from groq import Groq
import os

# Configuración de la API Key
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def adia_normal_chat(message, history):
    try:
        if not api_key:
            return "❌ Falta la API Key en Render."
            
        messages = [{"role": "system", "content": "Eres ADIA, una IA avanzada."}]
        
        # Historial compatible con versiones antiguas de Gradio
        for h_user, h_bot in history:
            messages.append({"role": "user", "content": h_user})
            messages.append({"role": "assistant", "content": h_bot})
            
        messages.append({"role": "user", "content": message})
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=messages
        )
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

def adia_canvas_generator(prompt):
    try:
        system_prompt = "Eres ADIA, experta en código. Responde SOLO con código HTML/JS en un bloque ```html."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=messages
        )
        codigo = completion.choices[0].message.content
        if "```html" in codigo:
            codigo = codigo.split("```html")[1].split("```")[0]
        return codigo
    except Exception as e:
        return f"<div style='color:red;'>⚠️ Error: {str(e)}</div>"

with gr.Blocks(title="ADIA AI", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA: Intelligence & Canvas")
    
    with gr.Tabs():
        with gr.TabItem("💬 Modo Chat"):
            # AQUÍ EL CAMBIO: Quitamos el type="messages"
            gr.ChatInterface(fn=adia_normal_chat)
            
        with gr.TabItem("🎨 Modo Canvas"):
            with gr.Row():
                with gr.Column(scale=1):
                    user_input = gr.Textbox(label="Instrucciones", lines=4)
                    btn = gr.Button("🚀 GENERAR JUEGO", variant="primary")
                with gr.Column(scale=2):
                    canvas_output = gr.HTML(value="Esperando...")

            btn.click(fn=adia_canvas_generator, inputs=[user_input], outputs=[canvas_output])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
