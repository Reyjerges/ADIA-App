import os
import gradio as gr
from groq import Groq
import re

# Configuración del Cliente Groq
# Recuerda que la API KEY debe estar en las variables de entorno de Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Instrucciones para que ADIA cree juegos compatibles con móviles y PC
    instrucciones = (
        "Eres ADIA, una IA experta en programación creativa. "
        "Si te piden un juego, genera un código HTML único con CSS y JS. "
        "Usa controles táctiles y de teclado. "
        "El código debe estar dentro de bloques: ```html ... ```"
    )

    # Formatear mensajes correctamente para Groq (Lista de diccionarios)
    mensajes = [{"role": "system", "content": instrucciones}]
    
    # Corregir el historial: Gradio envía [user, bot], Groq necesita roles individuales
    for par in historial:
        if par[0]: # Mensaje del usuario
            mensajes.append({"role": "user", "content": str(par[0])})
        if par[1]: # Respuesta del asistente
            mensajes.append({"role": "assistant", "content": str(par[1])})
    
    # Añadir el mensaje actual
    mensajes.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def extraer_juego(historial):
    if not historial:
        return "<p style='text-align:center; color:gray;'>Pide un juego para empezar.</p>"
    
    # Acceder a la última respuesta del asistente en el historial de Gradio
    ultimo_par = historial[-1]
    ultimo_texto = ultimo_par[1] # El índice 1 es la respuesta del bot
    
    match = re.search(r"```html([\s\S]*?)```", ultimo_texto)
    
    if match:
        codigo = match.group(1).strip()
        # Escapamos las comillas para que el iframe funcione correctamente
        codigo_seguro = codigo.replace('"', '&quot;')
        return f"""
        <div style="width:100%; height:100%; min-height:400px; background:#000; border-radius:10px;">
            <iframe srcdoc="{codigo_seguro}" 
                    style="width:100%; height:500px; border:none;" 
                    sandbox="allow-scripts allow-same-origin">
            </iframe>
        </div>
        """
    return "<p style='text-align:center; color:gray;'>No encontré código de juego en la última respuesta.</p>"

def responder(msg, hist):
    bot_res = chat_adia(msg, hist)
    hist.append((msg, bot_res))
    return "", hist

# Interfaz optimizada para que parezca una App
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA App")
    
    with gr.Tabs():
        with gr.TabItem("Chat"):
            chatbot = gr.Chatbot(height=450)
            with gr.Row():
                txt = gr.Textbox(placeholder="Escribe aquí...", show_label=False, scale=4)
                btn = gr.Button("Enviar", variant="primary", scale=1)
        
        with gr.TabItem("Juego"):
            gr.Markdown("### 🎮 Consola")
            visor = gr.HTML("Dale a 'Cargar' después de que ADIA genere el código.")
            btn_jugar = gr.Button("🚀 Cargar Juego")

    # Eventos
    txt.submit(responder, [txt, chatbot], [txt, chatbot])
    btn.click(responder, [txt, chatbot], [txt, chatbot])
    btn_jugar.click(extraer_juego, chatbot, visor)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
