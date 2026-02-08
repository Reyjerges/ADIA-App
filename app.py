import os
import re
import sys

# Manejo de dependencias para Render
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

def buscar_en_google(consulta):
    try:
        from googlesearch import search
        resultados = list(search(consulta, num_results=3, lang="es"))
        if resultados:
            return "\n\n--- INFO WEB RECIENTE ---\n" + "\n".join(resultados)
        return ""
    except:
        return ""

def chat_adia(mensaje, historial):
    if not client:
        return "ADIA: Hola. Por favor, configura la clave 'GROQ_API_KEY' en Render."

    instrucciones = (
        "Eres ADIA, una IA experta en videojuegos con HTML5 Canvas. "
        "Si piden un juego, genera UN SOLO bloque de código ```html ... ```. "
        "Usa <canvas id='gameCanvas'></canvas> y haz que ocupe todo el ancho. "
        "Todo el JS debe ir en etiquetas <script>."
    )

    mensajes_api = [{"role": "system", "content": instrucciones}]
    
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
    if not historial:
        return "<p style='text-align:center; color:gray;'>No hay mensajes.</p>"
    
    ultima_respuesta = historial[-1][1]
    match = re.search(r"```html([\s\S]*?)```", ultima_respuesta)
    
    if match:
        codigo = match.group(1).strip()
        # Usamos comillas simples para el srcdoc para evitar conflictos
        return f"""
        <div style="width:100%; height:500px; border:3px solid #00f2ff; border-radius:15px; overflow:hidden; background:#000;">
            <iframe srcdoc='{codigo}' style="width:100%; height:100%; border:none;" sandbox="allow-scripts allow-same-origin"></iframe>
        </div>
        """
    return "<p style='text-align:center; color:gray;'>No encontré código HTML.</p>"

def manejar_respuesta(txt, hist):
    if not txt.strip(): return "", hist
    res = chat_adia(txt, hist)
    hist.append((txt, res)) 
    return "", hist

with gr.Blocks(theme=gr.themes.Soft(), title="ADIA OS") as demo:
    gr.Markdown("# 🤖 ADIA SYSTEM")
    
    with gr.Tabs():
        with gr.TabItem("💬 Chat"):
            chat = gr.Chatbot(height=450)
            with gr.Row():
                input_msg = gr.Textbox(placeholder="Pide un juego...", scale=4, show_label=False)
                send_btn = gr.Button("Enviar", variant="primary")
        
        with gr.TabItem("🎮 Consola"):
            pantalla = gr.HTML("<div style='text-align:center; padding:50px;'>Pulsa el botón para cargar el juego.</div>")
            run_btn = gr.Button("🚀 EJECUTAR JUEGO")

    input_msg.submit(manejar_respuesta, [input_msg, chat], [input_msg, chat])
    send_btn.click(manejar_respuesta, [input_msg, chat], [input_msg, chat])
    run_btn.click(extraer_juego, chat, pantalla)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=port)
