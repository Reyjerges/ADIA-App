# ===============================
# IMPORTS
# ===============================
import os
import re
import sys

try:
    import gradio as gr
    from groq import Groq
except Exception as e:
    print(f"ERROR: Falta una libreria: {e}")
    sys.exit(1)

# ===============================
# CONFIGURACION
# ===============================
# Las plataformas de deploy suelen pasar el puerto como variable de entorno
PORT = int(os.environ.get("PORT", 7860))
API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    print("ERROR: La variable GROQ_API_KEY no esta configurada")
    # No salimos con sys.exit para que Gradio pueda al menos mostrar un error en consola
    client = None
else:
    client = Groq(api_key=API_KEY)

# ===============================
# LÓGICA DE ADIA
# ===============================
def chat_adia(mensaje, historial):
    if client is None:
        return "Error: No se encontro la API KEY de Groq."

    instrucciones = (
        "Eres ADIA, la IA personal creada por Jorge. "
        "Experta en juegos HTML5 Canvas. "
        "Responde SOLO con un bloque ```html``` que incluya el canvas "
        "y el script necesario. No des explicaciones."
    )

    # Construcción del historial de mensajes para la API
    mensajes = [{"role": "system", "content": instrucciones}]

    for usuario, asistente in historial:
        if usuario:
            mensajes.append({"role": "user", "content": str(usuario)})
        if asistente:
            mensajes.append({"role": "assistant", "content": str(asistente)})

    mensajes.append({"role": "user", "content": mensaje})

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes,
            temperature=0.7
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error de ADIA: {str(e)}"

def extraer_juego(historial):
    if not historial:
        return "<div style='color:white'>No hay ningun juego generado aun.</div>"

    # Buscamos en el último mensaje del asistente
    texto = historial[-1][1]
    m = re.search(r"```html([\s\S]*?)```", texto)

    if not m:
        return "<div style='color:white'>ADIA no envio un bloque HTML valido.</div>"

    codigo = m.group(1).replace("'", "&#39;")
    
    # Retornamos el iframe con el juego
    return (
        f"<iframe style='width:100%; height:500px; border:2px solid #00f2ff; background:white;' "
        f"sandbox='allow-scripts allow-same-origin' "
        f"srcdoc='{codigo}'></iframe>"
    )

def responder(mensaje, historial):
    if not mensaje.strip():
        return "", historial
    
    bot_res = chat_adia(mensaje, historial)
    historial.append((mensaje, bot_res))
    return "", historial

# ===============================
# INTERFAZ GRADIO
# ===============================
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 ADIA SYSTEM")
    
    with gr.Tabs():
        with gr.TabItem("💬 Chat"):
            chatbot = gr.Chatbot(height=450)
            with gr.Row():
                txt = gr.Textbox(
                    show_label=False,
                    placeholder="Escribe tu mensaje o pide un juego...",
                    scale=4
                )
                btn = gr.Button("Enviar", variant="primary", scale=1)

        with gr.TabItem("🎮 Consola"):
            ejecutar_btn = gr.Button("EJECUTAR JUEGO", variant="secondary")
            visor_html = gr.HTML("<div style='text-align:center; padding:20px;'>Presiona el boton para cargar el juego</div>")

    # Acciones
    txt.submit(responder, [txt, chatbot], [txt, chatbot])
    btn.click(responder, [txt, chatbot], [txt, chatbot])
    ejecutar_btn.click(extraer_juego, chatbot, visor_html)

# ===============================
# LANZAMIENTO
# ===============================
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=PORT)
