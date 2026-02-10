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
            
        messages = [{"role": "system", "content": "Eres ADIA, una IA avanzada y brillante."}]
        
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

        # MEJORA AQUÍ: Instrucciones detalladas para que ADIA no haga cuadros estáticos
        system_prompt = """Eres ADIA, una ingeniera de juegos experta. 
        Tus reglas de oro para el código:
        1. NUNCA hagas dibujos estáticos. Usa SIEMPRE requestAnimationFrame para crear un Game Loop.
        2. Usa objetos con funciones update() y draw().
        3. Añade 'Game Feel': usa Math.sin() para que los elementos floten o respiren.
        4. Estética: Usa bordes redondeados (roundRect) y sombras suaves (ctx.shadowBlur o elipses transparentes).
        5. Interactividad: Asegúrate de que el canvas responda a clics o toques.
        6. Responde SOLO con el código HTML/JS completo en un bloque ```html."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Crea un juego o app interactiva con movimiento fluido para: {prompt}"}
        ]
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=messages
        )
        
        codigo_crudo = completion.choices[0].message.content
        
        if "```html" in codigo_crudo:
            codigo = codigo_crudo.split("```html")[1].split("```")[0]
        elif "```" in codigo_crudo:
            codigo = codigo_crudo.split("```")[1].split("```")[0]
        else:
            codigo = codigo_crudo
            
        return codigo
    except Exception as e:
        return f"<div style='color:red;'>⚠️ Error: {str(e)}</div>"

# Construcción de la Interfaz
with gr.Blocks(title="ADIA AI", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA: Intelligence & Canvas")
    
    with gr.Tabs():
        with gr.TabItem("💬 Modo Chat"):
            gr.ChatInterface(fn=adia_normal_chat)
            
        with gr.TabItem("🎨 Modo Canvas"):
            with gr.Row():
                with gr.Column(scale=1):
                    user_input = gr.Textbox(label="Instrucciones para el juego", placeholder="Ej: Un juego de naves espaciales...", lines=4)
                    btn = gr.Button("🚀 GENERAR CÓDIGO VIVO", variant="primary")
                with gr.Column(scale=2):
                    canvas_output = gr.HTML(value="<div style='text-align:center; padding:40px;'>Esperando tus órdenes para programar...</div>")

            btn.click(fn=adia_canvas_generator, inputs=[user_input], outputs=[canvas_output])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
