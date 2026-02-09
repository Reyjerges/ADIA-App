import gradio as gr
from groq import Groq

client = Groq(api_key="TU_API_KEY")

def adia_generator(prompt, history):
    # Instrucciones para que ADIA solo responda con código funcional
    system_prompt = """Eres ADIA. Si el usuario te pide un juego o app, 
    responde ÚNICAMENTE con el código HTML/CSS/JS necesario dentro de 
    un bloque de código. No des explicaciones, solo el código."""
    
    messages = [{"role": "system", "content": system_prompt}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": prompt})
    
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages
    )
    
    codigo = completion.choices.message.content
    # Limpiamos el código por si la IA pone texto extra
    if "```html" in codigo:
        codigo = codigo.split("```html")[1].split("```")[0]
    
    return codigo

with gr.Blocks(title="ADIA Canvas AI") as demo:
    gr.Markdown("# ADIA: AI Canvas System")
    
    with gr.Tabs():
        with gr.TabItem("Chat"):
            # Modo normal
            gr.ChatInterface(fn=lambda m, h: client.chat.completions.create(
                model="llama3-8b-8192", 
                messages=[{"role":"user", "content":m}]).choices[0].message.content)

        with gr.TabItem("Modo Canvas (Generador)"):
            with gr.Row():
                with gr.Column(scale=1):
                    user_input = gr.Textbox(label="¿Qué juego quieres que ADIA cree?")
                    btn = gr.Button("Generar en Canvas")
                
                with gr.Column(scale=2):
                    # Aquí es donde ocurre la magia (Renderiza el HTML)
                    canvas = gr.HTML(label="Canvas de ADIA")

            btn.click(fn=adia_generator, inputs=[user_input], outputs=[canvas])

demo.launch()

