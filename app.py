import gradio as gr
from groq import Groq
import os

# Configuración de la API Key desde las variables de entorno de Render
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def adia_normal_chat(message, history):
    try:
        if not api_key:
            return "❌ Configuración incompleta: Falta la API Key en las variables de entorno de Render."
            
        messages = [{"role": "system", "content": "Eres ADIA, una IA avanzada, experta en tecnología y muy servicial."}]
        for h_user, h_assistant in history:
            messages.append({"role": "user", "content": h_user})
            messages.append({"role": "assistant", "content": h_assistant})
        messages.append({"role": "user", "content": message})
        
        # Modelo actualizado a Llama 3.1
        response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages)
        return response.choices.message.content
    except Exception as e:
        return f"❌ Error en el sistema: {str(e)}"

def adia_canvas_generator(prompt):
    try:
        if not api_key:
            return "<div style='color:red;'>❌ Error: No se detectó la API Key en el servidor.</div>"

        system_prompt = """Eres ADIA, una experta programadora de videojuegos. 
        Tu misión es crear un juego funcional en un solo archivo HTML (incluyendo CSS y JS).
        REGLAS:
        1. Responde EXCLUSIVAMENTE con el código dentro de un bloque ```html.
        2. Usa emojis para representar personajes y objetos (ej: 🏃, 🧱, 🚩).
        3. El juego debe incluir controles de teclado y un diseño visual atractivo."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Crea este juego ahora: {prompt}"}
        ]
        
        # Modelo actualizado a Llama 3.3 para programación compleja
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
        codigo = completion.choices.message.content
        
        if "```html" in codigo:
            codigo = codigo.split("```html")[1].split("```")[0]
        elif "```" in codigo:
            codigo = codigo.split("```")[1].split("```")[0]
            
        return codigo
        
    except Exception as e:
        return f"""
        <div style='color:red; background:#fff0f0; padding:20px; border:2px solid red; border-radius:10px;'>
            <h3>⚠️ Error de Conexión:</h3>
            <p>{str(e)}</p>
        </div>
        """

# Interfaz de Usuario
with gr.Blocks(title="ADIA System", theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("# 🤖 ADIA: Intelligence & Canvas")
    
    with gr.Tabs():
        with gr.TabItem("💬 Modo Chat"):
            gr.ChatInterface(fn=adia_normal_chat)
            
        with gr.TabItem("🎨 Modo Canvas"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🕹️ ¿Qué quieres jugar?")
                    user_input = gr.Textbox(
                        label="Describe el juego", 
                        placeholder="Ej: Un juego de plataformas estilo Mario...",
                        lines=4
                    )
                    btn = gr.Button("🚀 GENERAR EN CANVAS", variant="primary")
                
                with gr.Column(scale=2):
                    canvas_output = gr.HTML(
                        value="<div style='text-align:center; padding:40px; border:2px dashed #ccc;'>El código generado aparecerá aquí...</div>"
                    )

            btn.click(fn=adia_canvas_generator, inputs=[user_input], outputs=[canvas_output])

# Puerto para Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
