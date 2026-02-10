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
            
        # Mensaje de sistema
        messages = [{"role": "system", "content": "Eres ADIA, una IA avanzada y brillante."}]
        
        # Procesar historial limpiando metadatos que Groq rechaza
        for turn in history:
            if isinstance(turn, dict):
                role = turn.get("role")
                content = turn.get("content")
                if role and content:
                    messages.append({"role": role, "content": content})
            elif isinstance(turn, (list, tuple)) and len(turn) == 2:
                messages.append({"role": "user", "content": turn[0]})
                messages.append({"role": "assistant", "content": turn[1]})
            
        # Añadir mensaje actual
        messages.append({"role": "user", "content": message})
        
        # Llamada a la API
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

        system_prompt = "Eres ADIA, experta en código. Responde SOLO con código HTML/JS en un bloque ```html."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=messages
        )
        
        codigo_crudo = completion.choices[0].message.content
        
        # Extraer el código del bloque
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
                    user_input = gr.Textbox(label="Instrucciones", lines=4)
                    btn = gr.Button("🚀 GENERAR JUEGO", variant="primary")
                with gr.Column(scale=2):
                    canvas_output = gr.HTML(value="Esperando instrucciones...")

            btn.click(fn=adia_canvas_generator, inputs=[user_input], outputs=[canvas_output])

# Puerto para Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)

