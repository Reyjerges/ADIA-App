from os import environ
import gradio as gr
from groq import Groq

# 1. Configuración de Entorno
PORT = int(environ.get("PORT", 10000))
groq_client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO_OSS = "openai/gpt-oss-120b"

# 2. CSS para que no se vea vacía (Estilo ChatGPT Dark/Light)
custom_css = """
.gradio-container { max-width: 950px !important; margin: auto !important; }
.main-header { text-align: center; padding: 20px; background: linear-gradient(90deg, #2D3748, #4A5568); color: white; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.chatbot { border-radius: 15px !important; overflow: hidden !important; box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important; }
footer { display: none !important; }
"""

def adia_cerebro(mensaje, historial):
    sistema_prompt = (
        "Eres ADIA, una inteligencia de razonamiento superior basada en GPT-OSS 120B. "
        "Tu creador es JORGE. "
        "Sé directa, elegante y usa razonamiento lógico. No uses rellenos innecesarios. "
        "Habla utilizando **negritas** en las cosas importantes y usando emojis 🚀 para que no sea aburrido. "
        "Debes hablar de manera profesional y no inventes cosas cuando no sepas; "
        "es mejor decir que no estás segura y ofrecer ayudar todo de manera profesional. "
        "Usa este orden cuando vayas a escribir: explicar/responder, dar un resumen sencillo "
        "y por último ofrecer explicar cosas relacionadas al tema. "
        "No uses tablas, en su lugar usa **listas**."
    )
    
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Limpieza de historial para evitar el Error 400 (Property metadata unsupported)
    for turno in historial:
        if isinstance(turno, dict):
            mensajes_ia.append({"role": turno.get("role"), "content": turno.get("content")})
        elif isinstance(turno, (list, tuple)) and len(turno) == 2:
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})

    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = groq_client.chat.completions.create(
            model=MODELO_OSS,
            messages=mensajes_ia,
            temperature=0.6,
            max_tokens=2500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA CORE ERROR**: Jorge, hay un problema técnico: {str(e)}"

# 3. Interfaz con diseño de bloques
with gr.Blocks(title="ADIA Intelligence") as demo:
    # Encabezado para llenar espacio visual
    with gr.Column(elem_classes="main-header"):
        gr.Markdown("# ADIA CORE 120B")
        gr.Markdown("### Bienvenida al centro de mando, **Jorge** 🛠️")
    
    # Chat con altura fija para que no baile la pantalla
    gr.ChatInterface(
        fn=adia_cerebro,
        chatbot=gr.Chatbot(
            height=600, 
            elem_id="chatbot", 
            show_label=False,
            placeholder="**ADIA está lista.** ¿En qué proyecto trabajaremos hoy, Jorge?"
        ),
        textbox=gr.Textbox(placeholder="Escribe tu consulta maestra...", container=False, scale=7),
    )

# 4. Lanzamiento para Render
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=PORT,
        css=custom_css
    )
