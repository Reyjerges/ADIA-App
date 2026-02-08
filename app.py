import os
import gradio as gr
from groq import Groq
import re

# --- CONFIGURACIÓN DE CLIENTES ---
# Se obtiene la API Key de las variables de entorno de Render
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def buscar_en_google(consulta):
    """
    Realiza una búsqueda rápida en Google utilizando la librería googlesearch.
    """
    try:
        from googlesearch import search
        # Buscamos los 3 primeros resultados relevantes
        resultados = []
        for url in search(consulta, num_results=3, lang="es"):
            resultados.append(url)
        
        if resultados:
            return "\n\n--- INFORMACIÓN ADICIONAL DE LA WEB ---\n" + "\n".join(resultados)
        return ""
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return ""

def chat_adia(mensaje, historial):
    if not client:
        return "Error: La variable GROQ_API_KEY no está configurada en el panel de Render."

    # Instrucciones de comportamiento para ADIA
    instrucciones = (
        "Actúas como ADIA (Advanced Digital Intelligence Assistant). "
        "Eres una experta programadora de videojuegos educativos y divertidos. "
        "Si el usuario te pide un juego, genera un código HTML único dentro de un bloque ```html ... ``` "
        "que incluya CSS y JavaScript. El código debe ser autocontenido. "
        "Tus respuestas deben ser seguras, limpias y aptas para menores de 18 años. "
        "Evita cualquier tema violento, de apuestas o inapropiado."
    )

    # Lógica para decidir si se busca en la web
    contexto_web = ""
    palabras_clave = ["busca", "quien es", "precio", "noticias", "clima", "hoy", "internet"]
    if any(p in mensaje.lower() for p in palabras_clave):
        contexto_web = buscar_en_google(mensaje)

    # Construir historial compatible con Gradio 5 y Groq
    mensajes_api = [{"role": "system", "content": instrucciones}]
    
    if historial:
        for entrada in historial:
            if isinstance(entrada, dict):
                mensajes_api.append({"role": entrada["role"], "content": str(entrada["content"])})
            elif isinstance(entrada, (list, tuple)) and len(entrada) >= 2:
                if entrada[0]: mensajes_api.append({"role": "user", "content": str(entrada[0])})
                if entrada[1]: mensajes_api.append({"role": "assistant", "content": str(entrada[1])})

    # Mensaje actual combinado con contexto de búsqueda
    contenido_final = mensaje + contexto_web
    mensajes_api.append({"role": "user", "content": contenido_final})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en la conexión con la IA: {str(e)}"

def extraer_juego(historial):
    """Función para encontrar y ejecutar el código HTML en el visor"""
    if not historial:
        return "<p style='text-align:center; padding:20px; color:gray;'>No hay mensajes en el chat.</p>"
    
    ultima_entrada = historial[-1]
    texto = ultima_entrada["content"] if isinstance(ultima_entrada, dict) else ultima_entrada[1]
    
    match = re.search(r"```html([\s\S]*?)```", texto)
    if match:
        codigo = match.group(1).strip()
        codigo_seguro = codigo.replace('"', '&quot;')
        return f"""
        <div style="width:100%; height:100%; min-height:500px; border-radius:15px; overflow:hidden; border:2px solid #00f2ff;">
            <iframe srcdoc="{codigo_seguro}" 
                    style="width:100%; height:600px; border:none; background:black;"
                    sandbox="allow-scripts allow-same-origin">
            </iframe>
        </div>
        """
    return "<p style='text-align:center; padding:20px; color:gray;'>ADIA aún no ha generado un juego en esta conversación.</p>"

def manejar_respuesta(txt, hist):
    if not txt.strip(): return "", hist
    res = chat_adia(txt, hist)
    hist.append({"role": "user", "content": txt})
    hist.append({"role": "assistant", "content": res})
    return "", hist

# --- DEFINICIÓN DE LA INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft(), title="ADIA OS") as demo:
    gr.Markdown("# 🤖 ADIA - Sistema de Inteligencia y Juegos")
    
    with gr.Tabs():
        with gr.TabItem("💬 Conversación"):
            chat = gr.Chatbot(height=500, type="messages", label="Chat con ADIA")
            with gr.Row():
                input_msg = gr.Textbox(
                    placeholder="Escribe un mensaje o pide que cree un juego...", 
                    show_label=False, 
                    scale=4
                )
                send_btn = gr.Button("Enviar", variant="primary", scale=1)
        
        with gr.TabItem("🎮 Consola de Juegos"):
            gr.Markdown("### Pantalla de Ejecución")
            pantalla = gr.HTML("<div style='text-align:center; padding:50px; color:#666;'>Genera un juego en el chat y pulsa el botón para jugar.</div>")
            run_btn = gr.Button("🚀 Cargar Juego de ADIA", variant="secondary")

    input_msg.submit(manejar_respuesta, [input_msg, chat], [input_msg, chat])
    send_btn.click(manejar_respuesta, [input_msg, chat], [input_msg, chat])
    run_btn.click(extraer_juego, chat, pantalla)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)                
