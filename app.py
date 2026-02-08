import os
import re
import sys

# Manejo de dependencias
try:
    import gradio as gr
    from groq import Groq
except ImportError as e:
    print(f"ERROR: Falta una librería: {e}")
    sys.exit(1)

# --- CONFIGURACIÓN ---
port = int(os.environ.get("PORT", 10000))
api_key = os.environ.get("GROQ_API_KEY")
client = None

if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        print(f"Error al inicializar Groq: {e}")

def chat_adia(mensaje, historial):
    if not client:
        return "ADIA: Por favor, configura la clave 'GROQ_API_KEY' en Render."

    instrucciones = (
        "Eres ADIA, una IA experta en videojuegos con HTML5 Canvas. "
        "Si piden un juego, genera UN SOLO bloque de código ```html ... ```. "
        "Usa <canvas id='gameCanvas'></canvas> y haz que ocupe todo el ancho. "
        "Todo el JS debe ir en etiquetas <script>."
    )

    # Convertir el historial al formato que entiende la API de Groq
    mensajes_api = [{"role": "system", "content": instrucciones}]
    
    # En Gradio 5, el historial viene como una lista de objetos de mensaje
    for msg in historial:
        # Detectar si es mensaje de usuario o asistente según el formato de Gradio
        role = "user" if msg["role"] == "user" else "assistant"
        mensajes_api.append({"role": role, "content": msg["content"]})

    mensajes_api.append({"role": "user", "content": mensaje})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def extraer_juego(historial):
    if not historial or len(historial) == 0:
        return "<p style='text-align:center; color:gray;'>No hay mensajes todavía.</p>"
    
    # Obtener el contenido del último mensaje del asistente
    ultima_respuesta = ""
    for msg in reversed(historial):
        if msg["role"] == "assistant":
            ultima_respuesta = msg["content"]
            break
    
    match = re.search(r"```html([\s\S]*?)```", ultima_respuesta)
    
    if match:
        codigo = match.group(1).strip()
        # Escapamos comillas simples para que no rompan el srcdoc
        codigo_limpio = codigo.replace("'", "&#39;")
        return f"""
        <div style="width:100%; height:500px; border:3px solid #00f2ff; border-radius:15px; overflow:hidden; background:#000;">
            <iframe srcdoc='{codigo_limpio}' style="width:100%; height:100%; border:none;" sandbox="allow-scripts allow-same-origin"></iframe>
        </div>
        """
    return "<p style='text-align:center; color:gray;'>No encontré código HTML en la última respuesta.</p>"

# Función para manejar la interacción
def responder(mensaje, historial):
    # El historial en Gradio 5 se actualiza automáticamente si usamos type="messages"
    bot_message = chat_adia(mensaje, historial)
    historial.append({"role": "user", "content": mensaje})
    historial.append({"role": "assistant", "content": bot_message})
    return "", historial

with gr.Blocks(theme=gr.themes.Soft(), title="ADIA OS") as demo:
    gr.Markdown("# 🤖 ADIA SYSTEM")
    
    # Importante: type="messages" es lo que espera Gradio 5
    estado_historial = gr.State([])
    
    with gr.Tabs():
        with gr.TabItem("💬 Chat"):
            chatbot = gr.Chatbot(type="messages", height=450)
            with gr.Row():
                input_msg = gr.Textbox(placeholder="Pide un juego de Canvas...", scale=4, show_label=False)
                send_btn = gr.Button("Enviar", variant="primary")
        
        with gr.TabItem("🎮 Consola"):
            pantalla = gr.HTML("<div style='text-align:center; padding:50px;'>Pulsa el botón para cargar el juego.</div>")
            run_btn = gr.Button("🚀 EJECUTAR JUEGO")

    # Eventos
    input_msg.submit(responder, [input_msg, chatbot], [input_msg, chatbot])
    send_btn.click(responder, [input_msg, chatbot], [input_msg, chatbot])
    run_btn.click(extraer_juego, chatbot, pantalla)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=port)
