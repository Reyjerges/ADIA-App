import gradio as gr
from groq import Groq
import os

# Configuración del cliente Groq (Asegúrate de poner tu API Key en Render)
client = Groq(api_key=os.environ.get("GROQ_API_KEY", "TU_API_KEY_AQUI"))

def adia_normal_chat(message, history):
    # Chat normal de ADIA
    messages = [{"role": "system", "content": "Eres ADIA, una IA experta y divertida."}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})
    
    response = client.chat.completions.create(model="llama3-8b-8192", messages=messages)
    return response.choices.message.content

def adia_canvas_generator(prompt):
    # Prompt maestro para que ADIA actúe como programadora experta de juegos
    system_prompt = """Eres ADIA, experta en desarrollo de videojuegos. 
    Tu objetivo es crear un juego en HTML, CSS y JS basado en la petición del usuario.
    REGLAS:
    1. Responde ÚNICAMENTE con el código dentro de un bloque ```html ... ```.
    2. El juego debe ser responsivo y ocupar todo el ancho del contenedor.
    3. Usa emojis para los personajes (ej. 🏃 para Mario, 🚩 para meta).
    4. Incluye controles por teclado y un botón de 'Reiniciar' dentro del HTML."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Crea este juego: {prompt}"}
    ]
    
    completion = client.chat.completions.create(model="llama3-70b-8192", messages=messages)
    codigo = completion.choices.message.content
    
    # Extraer el código HTML del bloque de código
    if "```html" in codigo:
        codigo = codigo.split("```html")[1].split("```")[0]
    elif "```" in codigo:
        codigo = codigo.split("```")[1].split("```")[0]
        
    return codigo

# Interfaz de ADIA
with gr.Blocks(title="ADIA System", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA: Intelligence & Canvas")
    
    with gr.Tabs():
        # MODO 1: NORMAL
        with gr.TabItem("Modo Chat"):
            gr.ChatInterface(fn=adia_normal_chat)
            
        # MODO 2: CANVAS (Generador de Juegos)
        with gr.TabItem("Modo Canvas"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🕹️ Generador de Juegos")
                    user_input = gr.Textbox(
                        label="Describe tu juego (ej: Un Mario 2D con niveles)", 
                        placeholder="Haz un juego de plataformas donde...",
                        lines=4
                    )
                    btn = gr.Button("¡ADIA, CREA EL JUEGO!", variant="primary")
                
                with gr.Column(scale=2):
                    # El canvas donde se renderiza el juego
                    canvas_output = gr.HTML(
                        value="<div style='text-align:center; padding:40px;'>El juego aparecerá aquí...</div>",
                        label="Canvas de ADIA"
                    )

            btn.click(fn=adia_canvas_generator, inputs=[user_input], outputs=[canvas_output])

# Configuración de puerto para Render
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
