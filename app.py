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

    # Formato de mensajes para la API de Groq
    mensajes_api = [{"role": "system", "content": instrucciones}]
    
    # Procesar historial clásico (lista de listas/tuplas)
    if historial:
        for usuario, asistente in historial:
            if usuario: mensajes_api.append({"role": "user", "content": str(usuario)})
            if asistente: mensajes_api.append({"role": "assistant", "content": str(asistente)})

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
    
    # En el formato clásico, el historial es [(user, bot), (user, bot)]
    # Sacamos el bot de la última entrada
    ultima_respuesta = historial[-1][1]
    
    if not ultima_respuesta:
        return "<p style='text-align:center; color:gray;'>Esperando respuesta...</p>"

    match = re.search(r"```html([\s\S]*?)```", ultima_respuesta)
    
    if match:
        codigo = match.group(1).strip()
        # Limpieza para evitar conflictos de comillas en el iframe
        codigo_limpio = codigo.replace("'", "&#39;")
        return f"""
        <div style="width:100%; height:500px; border:3px solid #00f2ff; border-radius:15px; overflow:hidden; background:#000;">
            <iframe srcdoc='{codigo_limpio}' style="width:100%; height:100%; border:none;" sandbox="allow-scripts allow-same-origin"></iframe>
        </div>
        """
    return "<p style='text-align:center; color:gray;'>Pide un juego y cuando ADIA responda, pulsa este botón.</p>"

def responder(mensaje, historial):
    if not mensaje.strip():
        return "", historial
    bot_message = chat_adia(mensaje, historial)
    historial.append((mensaje, bot_message))
    return "", historial

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft(), title="ADIA OS") as demo:
    gr.Markdown("# 🤖 ADIA SYSTEM")
    
    with gr.Tabs():
        with gr.TabItem("💬 Chat"):
            # Quitamos el type="messages" para máxima compatibilidad
            chatbot = gr.Chatbot(height=450)
            with gr.Row():
                input_msg = gr.Textbox(placeholder="Pide un juego de Canvas...", scale=4, show_label=False)
                send_btn = gr.Button("Enviar", variant="primary")
        
        with gr.TabItem("🎮 Consola"):
            pantalla = gr.HTML("<div style='text-align:center; padding:50px; color:gray;'>Los juegos de Canvas se cargarán aquí.</div>")
            run_btn = gr.Button("🚀 EJECUTAR JUEGO", variant="secondary")

    # Eventos con el formato de historial de lista de tuplas
    input_msg.submit(responder, [input_msg, chatbot], [input_msg, chatbot])
    send_btn.click(responder, [input_msg, chatbot], [input_msg, chatbot])
    run_btn.click(extraer_juego, chatbot, pantalla)

if __name__ == "__main__":
    # Render necesita server_name="0.0.0.0"
    demo.launch(server_name="0.0.0.0", server_port=port)
