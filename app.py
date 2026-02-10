import gradio as gr
from groq import Groq
import os

# Configuración de la API Key
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def adia_normal_chat(message, history):
    try:
        if not api_key:
            return "❌ Falta la API Key en Render (Environment Variables)."
            
        messages = [{"role": "system", "content": "Eres ADIA, una IA avanzada y brillante."}]
        
        # Gradio envía el historial como objetos con 'role' y 'content' o tuplas
        for turn in history:
            if isinstance(turn, dict):
                messages.append(turn)
            else:
                messages.append({"role": "user", "content": turn[0]})
                messages.append({"role": "assistant", "content": turn[1]})
            
        messages.append({"role": "user", "content": message})
        
        # Modelo oficial Llama 3.1
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=messages
        )
        
        # CORRECCIÓN: Acceso al primer elemento de la lista 'choices'
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error en el sistema: {str(e)}"

def adia_canvas_generator(prompt):
    try:
        if not api_key:
            return "<div style='color:red;'>❌ Error: No hay API Key.</div>"

        system_prompt = """Eres ADIA, experta en código. 
        Responde SOLO con código HTML/CSS/JS dentro de un bloque ```html.
        Crea un juego completo, con emojis y controles de teclado."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Crea este juego: {prompt}"}
        ]
        
        # Modelo oficial Llama 3.3
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=messages
        )
        
        # CORRECCIÓN: Acceso al primer elemento de la lista 'choices'
        codigo_crudo = completion.choices[0].message.content
        
        # Limpieza de etiquetas de bloque de código
        if "```html" in codigo_crudo:
            codigo = codigo_crudo.split("```html")[1].split("```")[0]
        elif "```" in codigo_crudo:
            codigo = codigo_crudo.split("```")[1].split("```")[0]
        else:
            codigo = codigo_crudo
            
        return codigo
        
    except Exception as e:
        return f"<div style='color:red; padding:20px; border:1px solid red;'>⚠️ Error: {str(e)}</div>"

# Interfaz Visual
with gr.Blocks(title="ADIA AI", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA: Intelligence & Canvas")
    
    with gr.Tabs():
        with gr.TabItem("💬 Modo Chat"):
            gr.ChatInterface(fn=adia_normal_chat, type="messages")
            
        with gr.TabItem("🎨 Modo Canvas"):
            with gr.Row():
                with gr.Column(scale=1):
                    user_input = gr.Textbox(label="Instrucciones para el juego", lines=4)
                    btn = gr.Button("🚀 GENERAR JUEGO", variant="primary")
                
                with gr.Column(scale=2):
                    canvas_output = gr.HTML(value="<div style='text-align:center; padding:40px;'>Esperando instrucciones...</div>")

            btn.click(fn=adia_canvas_generator, inputs=[user_input], outputs=[canvas_output])

if __name__ == "__main__":
    # Configuración de puerto dinámica para Render
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
