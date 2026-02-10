import gradio as gr
from groq import Groq
import os

# Configuración segura de la API Key
# En Render, debes crear la variable GROQ_API_KEY en la pestaña Environment
api_key = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

def adia_normal_chat(message, history):
    try:
        if not api_key:
            return "❌ Error: No se encontró la API Key de Groq en las variables de entorno de Render."
            
        messages = [{"role": "system", "content": "Eres ADIA, una IA experta y útil."}]
        for h_user, h_assistant in history:
            messages.append({"role": "user", "content": h_user})
            messages.append({"role": "assistant", "content": h_assistant})
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(model="llama3-8b-8192", messages=messages)
        return response.choices.message.content
    except Exception as e:
        return f"❌ Error en el Chat: {str(e)}"

def adia_canvas_generator(prompt):
    try:
        if not api_key:
            return "<div style='color:red;'>❌ Error: Falta la API Key en Render.</div>"

        system_prompt = """Eres ADIA, experta en videojuegos. 
        Responde ÚNICAMENTE con código HTML/CSS/JS dentro de un bloque ```html.
        Usa emojis para los personajes y crea una lógica de juego completa."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Crea este juego: {prompt}"}
        ]
        
        completion = client.chat.completions.create(model="llama3-70b-8192", messages=messages)
        codigo = completion.choices.message.content
        
        # Limpieza del código para que el navegador lo entienda
        if "```html" in codigo:
            codigo = codigo.split("```html")[1].split("```")[0]
        elif "```" in codigo:
            codigo = codigo.split("```")[1].split("```")[0]
            
        return codigo
        
    except Exception as e:
        # Esto te dirá exactamente qué está fallando en el Modo Canvas
        return f"""
        <div style='color:red; background:#fee; padding:20px; border:1px solid red; border-radius:10px;'>
            <h3>⚠️ Error detectado por ADIA:</h3>
            <p><b>Detalle:</b> {str(e)}</p>
            <p><i>Verifica que tu API KEY sea válida y que tengas créditos en Groq.</i></p>
        </div>
        """

# Interfaz Visual
with gr.Blocks(title="ADIA System", theme=gr.themes.Default()) as demo:
    gr.Markdown("# 🤖 ADIA: Intelligence & Canvas")
    
    with gr.Tabs():
        with gr.TabItem("Modo Chat"):
            gr.ChatInterface(fn=adia_normal_chat)
            
        with gr.TabItem("Modo Canvas (Juegos)"):
            with gr.Row():
                with gr.Column(scale=1):
                    user_input = gr.Textbox(
                        label="¿Qué juego quieres que ADIA cree?", 
                        placeholder="Ej: Un clon de Mario con emojis...",
                        lines=3
                    )
                    btn = gr.Button("🚀 GENERAR JUEGO EN CANVAS", variant="primary")
                
                with gr.Column(scale=2):
                    canvas_output = gr.HTML(
                        value="<div style='text-align:center; padding:40px;'>El juego aparecerá aquí...</div>"
                    )

            btn.click(fn=adia_canvas_generator, inputs=[user_input], outputs=[canvas_output])

# Inicio del servidor con el puerto dinámico de Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
