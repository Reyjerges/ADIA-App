import os
import gradio as gr
from groq import Groq
import re
import sys

# --- CONFIGURACIÓN DE PUERTO PARA RENDER ---
# Render asigna un puerto dinámico, si no existe usamos el 10000 por defecto
port = int(os.environ.get("PORT", 10000))

# --- CONFIGURACIÓN DE CLIENTES ---
api_key = os.environ.get("GROQ_API_KEY")
client = None

if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        print(f"Error al inicializar Groq: {e}")

def buscar_en_google(consulta):
    """Realiza una búsqueda rápida en Google."""
    try:
        from googlesearch import search
        resultados = []
        for url in search(consulta, num_results=3, lang="es"):
            resultados.append(url)
        if resultados:
            return "\n\n--- INFO WEB ---\n" + "\n".join(resultados)
        return ""
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return ""

def chat_adia(mensaje, historial):
    if not client:
        return "ADIA: Hola. Por favor, configura la GROQ_API_KEY en Render para que pueda pensar."

    instrucciones = (
        "Eres ADIA, una IA experta en videojuegos y programación creativa. "
        "Si piden un juego, genera un bloque ```html ... ``` único y completo. "
        "Tus respuestas son siempre seguras para menores y educativas."
    )

    contexto_web = ""
    if any(p in mensaje.lower() for p in ["busca", "quien es", "internet", "noticias"]):
        contexto_web = buscar_en_google(mensaje)

    mensajes_api = [{"role": "system", "content": instrucciones}]
    
    if historial:
        for entrada in historial:
            if isinstance(entrada, dict):
                mensajes_api.append(entrada)
            elif isinstance(entrada, (list, tuple)) and len(entrada) >= 2:
                if entrada[0]: mensajes_api.append({"role": "user", "content": str(entrada[0])})
                if entrada[1]: mensajes_api.append({"role": "assistant", "content": str(entrada[1])})

    mensajes_api.append({"role": "user", "content": mensaje + contexto_web})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error de conexión: {str(e)}"

def extraer_juego(historial):
    if not historial:
        return "<p style='text-align:center; padding:20px;'>No hay datos.</p>"
    
    ultima_entrada = historial[-1]
    texto = ultima_entrada["content"] if isinstance(ultima_entrada, dict) else ultima_entrada[1]
    
    match = re.search(r"```html([\s\S]*?)```", texto)
    if match:
        codigo = match.group(1).strip()
        codigo_seguro = codigo.replace('"', '&quot;')
        return f"""
        <div style="width:100%; height:550px; border-radius:15px; overflow:hidden; border:2px solid #00f2ff;">
            <iframe srcdoc="{codigo_seguro}" style="width:100%; height:100%; border:none; background:black;" sandbox="allow-scripts allow-same-origin"></iframe>
        </div>
        """
    return "<p style='text-align:center; padding:20px;'>No se encontró un juego.</p>"

def manejar_respuesta(txt, hist):
    if not txt.strip(): return "", hist
    res = chat_adia(txt, hist)
    hist.append({"role": "user", "content": txt})
    hist.append({"role": "assistant", "content": res})
    return "", hist

# --- INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft(), title="ADIA OS") as demo:
    gr.Markdown("# 🤖 ADIA SYSTEM")
    with gr.Tabs():
        with gr.TabItem("💬 Chat"):
            chat = gr.Chatbot(height=500, type="messages")
            with gr.Row():
                input_msg = gr.Textbox(placeholder="Pide un juego...", show_label=False, scale=4)
                send_btn = gr.Button("Enviar", variant="primary", scale=1)
        with gr.TabItem("🎮 Consola"):
            pantalla = gr.HTML("<div style='text-align:center; padding:50px;'>Genera un juego primero.</div>")
            run_btn = gr.Button("🚀 Ejecutar Juego", variant="secondary")

    input_msg.submit(manejar_respuesta, [input_msg, chat], [input_msg, chat])
    send_btn.click(manejar_respuesta, [input_msg, chat], [input_msg, chat])
    run_btn.click(extraer_juego, chat, pantalla)

if __name__ == "__main__":
    # Crucial para Render: server_name="0.0.0.0" y el puerto de la variable de entorno
    demo.launch(server_name="0.0.0.0", server_port=port)
