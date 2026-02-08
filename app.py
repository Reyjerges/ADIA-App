import os
import re
import sys

# Intentar importar dependencias críticas con manejo de errores para depuración en Render
try:
    import gradio as gr
    from groq import Groq
except ImportError as e:
    print(f"ERROR: Falta una librería crítica: {e}")
    print("Asegúrate de que tu archivo requirements.txt incluya: gradio, groq, googlesearch-python, requests")
    sys.exit(1)

# --- CONFIGURACIÓN DE PUERTO PARA RENDER ---
port = int(os.environ.get("PORT", 10000))

# --- CONFIGURACIÓN DE CLIENTES ---
api_key = os.environ.get("GROQ_API_KEY")
client = None

if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        print(f"Error al inicializar Groq: {e}")
else:
    print("AVISO: La variable GROQ_API_KEY no está configurada.")

def buscar_en_google(consulta):
    """Realiza una búsqueda rápida en Google."""
    try:
        from googlesearch import search
        resultados = []
        for url in search(consulta, num_results=3, lang="es"):
            resultados.append(url)
        if resultados:
            return "\n\n--- INFO WEB RECIENTE ---\n" + "\n".join(resultados)
        return ""
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return ""

def chat_adia(mensaje, historial):
    if not client:
        return "ADIA: Hola. Para que pueda funcionar, por favor configura la clave 'GROQ_API_KEY' en los Environment Variables de tu panel de Render."

    instrucciones = (
        "Eres ADIA, una IA experta en videojuegos y programación creativa. "
        "Si piden un juego, genera un bloque ```html ... ``` único y completo. "
        "Tus respuestas son siempre seguras para menores, educativas y amigables."
    )

    contexto_web = ""
    if any(p in mensaje.lower() for p in ["busca", "quien es", "internet", "noticias", "hoy"]):
        contexto_web = buscar_en_google(mensaje)

    mensajes_api = [{"role": "system", "content": instrucciones}]
    
    # Adaptar historial para que funcione con listas de tuplas (formato estándar de Gradio)
    if historial:
        for usuario, asistente in historial:
            if usuario: mensajes_api.append({"role": "user", "content": str(usuario)})
            if asistente: mensajes_api.append({"role": "assistant", "content": str(asistente)})

    mensajes_api.append({"role": "user", "content": mensaje + contexto_web})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error de conexión con el cerebro de ADIA: {str(e)}"

def extraer_juego(historial):
    """Busca código HTML en el último mensaje y lo prepara para el visor."""
    if not historial or len(historial) == 0:
        return "<p style='text-align:center; padding:20px; color:gray;'>No hay mensajes todavía.</p>"
    
    # En el formato estándar de Gradio, historial[-1] es [usuario, asistente]
    ultima_respuesta_asistente = historial[-1][1]
    
    if not ultima_respuesta_asistente:
        return "<p style='text-align:center; padding:20px; color:gray;'>Esperando respuesta...</p>"

    match = re.search(r"```html([\s\S]*?)```", ultima_respuesta_asistente)
    if match:
        codigo = match.group(1).strip()
        codigo_seguro = codigo.replace('"', '&quot;')
        return f"""
        <div style="width:100%; height:550px; border-radius:15px; overflow:hidden; border:2px solid #00f2ff; background:#000;">
            <iframe srcdoc="{codigo_seguro}" style="width:100%; height:100%; border:none;" sandbox="allow-scripts allow-same-origin"></iframe>
        </div>
        """
    return "<p style='text-align:center; padding:20px; color:gray;'>Pide un juego a ADIA y cuando te lo dé, pulsa este botón.</p>"

def manejar_respuesta(txt, hist):
    if not txt.strip(): return "", hist
    res = chat_adia(txt, hist)
    hist.append((txt, res)) # Formato de tupla estándar [usuario, asistente]
    return "", hist

# --- CONSTRUCCIÓN DE LA INTERFAZ ---
with gr.Blocks(theme=gr.themes.Soft(), title="ADIA OS") as demo:
    gr.Markdown("# 🤖 ADIA SYSTEM - Inteligencia Creativa")
    
    with gr.Tabs():
        with gr.TabItem("💬 Chat con ADIA"):
            # Eliminado type="messages" para máxima compatibilidad
            chat = gr.Chatbot(height=500)
            with gr.Row():
                input_msg = gr.Textbox(
                    placeholder="Escribe aquí tu mensaje o pide un juego...", 
                    show_label=False, 
                    scale=4
                )
                send_btn = gr.Button("Enviar", variant="primary", scale=1)
        
        with gr.TabItem("🎮 Consola de Juegos"):
            gr.Markdown("### Ejecutor de Código en Tiempo Real")
            pantalla = gr.HTML("<div style='text-align:center; padding:50px; color:#aaa;'>Aquí aparecerán los juegos que ADIA programe para ti.</div>")
            run_btn = gr.Button("🚀 Cargar / Actualizar Juego", variant="secondary")

    # Eventos
    input_msg.submit(manejar_respuesta, [input_msg, chat], [input_msg, chat])
    send_btn.click(manejar_respuesta, [input_msg, chat], [input_msg, chat])
    run_btn.click(extraer_juego, chat, pantalla)

if __name__ == "__main__":
    print(f"Iniciando ADIA en el puerto {port}...")
    demo.launch(
        server_name="0.0.0.0", 
        server_port=port,
        share=False,
        show_error=True
    )
