import gradio as gr
from groq import Groq
import os

# Configuración de la API Key
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def adia_normal_chat(message, history):
    try:
        if not api_key:
            return "❌ Error: Configura GROQ_API_KEY en Render."
            
        messages = [{"role": "system", "content": "Eres ADIA, una IA avanzada, brillante y muy comunicativa."}]
        
        for turn in history:
            if isinstance(turn, dict):
                role = turn.get("role")
                content = turn.get("content")
                if role and content:
                    messages.append({"role": role, "content": content})
            elif isinstance(turn, (list, tuple)) and len(turn) == 2:
                messages.append({"role": "user", "content": turn[0]})
                messages.append({"role": "assistant", "content": turn[1]})
            
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
        if not api_key:
            return "<div style='color:red;'>❌ Falta API Key</div>"

        # INSTRUCCIONES CRÍTICAS PARA EVITAR PANTALLA NEGRA
        system_prompt = """Eres ADIA, experta en desarrollo de juegos. 
        Para evitar que la pantalla se quede negra, sigue estas reglas estrictas:
        1. Todo el código JS debe estar dentro de 'window.onload = () => { ... };'.
        2. Asegúrate de definir el fondo del canvas (ctx.fillRect) al inicio del loop.
        3. Usa requestAnimationFrame para el movimiento.
        4. Si el código es largo, prioriza que sea funcional y esté completo.
        5. Usa estilos visuales modernos (bordes redondeados, sombras, gradientes).
        6. Responde SOLO con el código HTML/JS en un bloque ```html."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Crea un juego interactivo con gráficos avanzados y movimiento fluido para: {prompt}"}
        ]
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=messages
        )
        
        codigo_crudo = completion.choices[0].message.content
        
        # Extracción segura del código
        if "```html" in codigo_crudo:
            codigo = codigo_crudo.split("```html")[1].split("```")[0]
        elif "```" in codigo_crudo:
            codigo = codigo_crudo.split("```")[1].split("```")[0]
        else:
            codigo = codigo_crudo
            
        return codigo
    except Exception as e:
        return f"<div style='color:red;'>⚠️ Error: {str(e)}</div>"

# Interfaz de Usuario
with gr.Blocks(title="ADIA AI", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA: Intelligence & Canvas")
    
    with gr.Tabs():
        with gr.TabItem("💬 Modo Chat"):
            gr.ChatInterface(fn=adia_normal_chat)
            
        with gr.TabItem("🎨 Modo Canvas"):
            with gr.Row():
                with gr.Column(scale=1):
                    user_input = gr.Textbox(label="Instrucciones para ADIA", placeholder="¿Qué juego crearemos hoy?", lines=4)
                    btn = gr.Button("🚀 GENERAR JUEGO (EVITAR PANTALLA NEGRA)", variant="primary")
                with gr.Column(scale=2):
                    # HTML con altura mínima para evitar que parezca vacío
                    canvas_output = gr.HTML(value="<div style='height:400px; display:flex; align-items:center; justify-content:center; background:#f0f2f5; border-radius:15px; color:#888;'>Esperando el código de ADIA...</div>")

            btn.click(fn=adia_canvas_generator, inputs=[user_input], outputs=[canvas_output])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
