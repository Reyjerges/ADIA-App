import os
import gradio as gr
from groq import Groq
import re

# Configuración del Cliente Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def chat_adia(mensaje, historial):
    # Instrucciones maestras
    instrucciones = (
        "Eres ADIA, una IA experta en programación creativa. "
        "Si te piden un juego, genera un código HTML único con CSS y JS. "
        "Usa controles táctiles y de teclado. "
        "El código debe estar dentro de bloques: ```html ... ```"
    )

    # Iniciar lista de mensajes para Groq
    mensajes_groq = [{"role": "system", "content": instrucciones}]
    
    # PROCESAMIENTO DEL HISTORIAL (Corrección para Gradio 5)
    for entrada in historial:
        # Si el historial viene como diccionarios (Gradio 5+)
        if isinstance(entrada, dict):
            rol = entrada.get("role")
            contenido = entrada.get("content")
            if rol and contenido:
                mensajes_groq.append({"role": rol, "content": str(contenido)})
        # Si viene como tuplas/listas [user, bot] (Gradio 4 y anteriores)
        elif isinstance(entrada, (list, tuple)):
            if len(entrada) >= 2:
                if entrada[0]: 
                    mensajes_groq.append({"role": "user", "content": str(entrada[0])})
                if entrada[1]: 
                    mensajes_groq.append({"role": "assistant", "content": str(entrada[1])})
    
    # Añadir el mensaje actual del usuario
    mensajes_groq.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_groq,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en la conexión con Groq: {str(e)}"

def extraer_juego(historial):
    if not historial:
        return "<p style='text-align:center; color:gray;'>Pide un juego para empezar.</p>"
    
    # Obtener el último mensaje del asistente
    ultima_entrada = historial[-1]
    if isinstance(ultima_entrada, dict):
        ultimo_texto = ultima_entrada.get("content", "")
    else:
        ultimo_texto = ultima_entrada[1]
    
    match = re.search(r"```html([\s\S]*?)```", ultimo_texto)
    
    if match:
        codigo = match.group(1).strip()
        codigo_seguro = codigo.replace('"', '&quot;')
        return f"""
        <div style="width:100%; height:500px; background:#000; border-radius:10px; overflow:hidden;">
            <iframe srcdoc="{codigo_seguro}" 
                    style="width:100%; height:100%; border:none;" 
                    sandbox="allow-scripts allow-same-origin">
            </iframe>
        </div>
        """
    return "<p style='text-align:center; color:gray;'>No encontré código de juego en la respuesta.</p>"

def responder(msg, hist):
    if not msg: return "", hist
    bot_res = chat_adia(msg, hist)
    # Gradio 5 prefiere diccionarios en el historial
    hist.append({"role": "user", "content": msg})
    hist.append({"role": "assistant", "content": bot_res})
    return "", hist

# Interfaz optimizada estilo App
with gr.Blocks(theme=gr.themes.Soft(), title="ADIA OS") as demo:
    gr.Markdown("# 🤖 ADIA - Sistema Inteligente")
    
    with gr.Tabs():
        with gr.TabItem("Chat"):
            # Importante: type="messages" para compatibilidad con Gradio 5
            chatbot = gr.Chatbot(height=450, type="messages")
            with gr.Row():
                txt = gr.Textbox(placeholder="Escribe aquí...", show_label=False, scale=4)
                btn = gr.Button("Enviar", variant="primary", scale=1)
        
        with gr.TabItem("Consola de Juego"):
            gr.Markdown("### 🎮 Pantalla")
            visor = gr.HTML("<p style='text-align:center; margin-top:50px;'>Genera un juego en el chat y luego pulsa Cargar.</p>")
            btn_jugar = gr.Button("🚀 Cargar Juego Generado", variant="secondary")

    # Eventos
    txt.submit(responder, [txt, chatbot], [txt, chatbot])
    btn.click(responder, [txt, chatbot], [txt, chatbot])
    btn_jugar.click(extraer_juego, chatbot, visor)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
