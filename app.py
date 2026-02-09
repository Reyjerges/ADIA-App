import gradio as gr
from groq import Groq
import os
import requests

# 1. CONFIGURACIÓN DEL CEREBRO
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generar_imagen(prompt_visual):
    # Usamos Pollinations para generar la imagen de forma gratuita y rápida
    url_limpia = prompt_visual.replace(" ", "%20")
    return f"https://image.pollinations.ai/prompt/{url_limpia}?width=1024&height=1024&nologo=true"

def adia_v12_logic(mensaje, historial):
    # Instrucciones para que ADIA sepa cuándo debe "imaginar"
    sistema = """Eres ADIA v1.2. Si Jorge te pide que 'dibujes', 'imagines' o 'creas una imagen', 
    debes responder confirmando la creación y describir brevemente qué estás visualizando."""
    
    mensajes_ia = [{"role": "system", "content": sistema}]
    for h in historial:
        if h[0]: mensajes_ia.append({"role": "user", "content": str(h[0])})
        if h[1]: mensajes_ia.append({"role": "assistant", "content": str(h[1])})
    
    mensajes_ia.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_ia
        )
        respuesta_texto = completion.choices[0].message.content
        
        # Lógica de detección de imagen
        img_url = None
        palabras_clave = ["dibuja", "imagina", "crea una imagen", "visualiza", "muestrame"]
        if any(palabra in mensaje.lower() for palabra in palabras_clave):
            img_url = generar_imagen(mensaje)
            
        return respuesta_texto, img_url
    except Exception as e:
        return f"Error: {str(e)}", None

# 2. INTERFAZ "VISUAL FORGE"
with gr.Blocks(theme=gr.themes.Monochrome()) as app:
    gr.Markdown("# 🦾 ADIA v1.2 | VISUAL GENERATION ENGINE")
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Terminal Jarvis", height=500)
            msg = gr.Textbox(placeholder="Ej: ADIA, imagina un reactor Ark azul sobre una mesa de metal...")
            btn = gr.Button("EJECUTAR PROTOCOLO", variant="primary")
            
        with gr.Column(scale=1):
            gr.Markdown("### 🖼️ SALIDA VISUAL")
            output_img = gr.Image(label="Última Generación", interactive=False)
            gr.HTML("<div style='color:#00f2ff; font-family:monospace; font-size:12px;'>ESTADO: LISTO PARA RENDERIZAR</div>")

    def responder(m, h):
        if not m: return "", h, None
        texto, imagen = adia_v12_logic(m, h)
        h.append((m, texto))
        return "", h, imagen

    msg.submit(responder, [msg, chatbot], [msg, chatbot, output_img])
    btn.click(responder, [msg, chatbot], [msg, chatbot, output_img])

# 3. LANZAMIENTO (Puerto Render)
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=10000)
