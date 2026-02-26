from os import environ
import gradio as gr
from groq import Groq

# 1. Configuración de Puerto y Cliente
PORT = int(environ.get("PORT", 10000))
groq_client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO_OSS = "openai/gpt-oss-120b"

# 2. CSS Maestro "ChatGPT Clone"
# Centramos el contenido, quitamos bordes y suavizamos las burbujas
chatgpt_css = """
footer { display: none !important; }
.gradio-container { background-color: #ffffff !important; font-family: -apple-system, system-ui, sans-serif !important; }
#chatbot { border: none !important; background: transparent !important; }
.message-wrap { max-width: 800px !important; margin: auto !important; }
.user { background-color: #f4f4f4 !important; border-radius: 20px !important; padding: 12px 20px !important; border: none !important; }
.bot { background-color: transparent !important; padding: 12px 20px !important; border: none !important; }
.styler { border: none !important; box-shadow: none !important; }
#input-box { border: 1px solid #e5e5e5 !important; border-radius: 15px !important; box-shadow: 0 0 15px rgba(0,0,0,0.05) !important; max-width: 800px !important; margin: auto !important; }
h1 { font-weight: 600 !important; letter-spacing: -1px !important; color: #1a1a1a !important; }
"""

def adia_cerebro(mensaje, historial):
    sistema_prompt = (
        "Eres ADIA, una inteligencia de razonamiento superior basada en GPT-OSS 120B. Tu creador es JORGE. "
        "Sé directa, elegante y usa razonamiento lógico. No uses rellenos innecesarios. "
        "Habla utilizando **negritas** en las cosas importantes y usando emojis 🚀 para que no sea aburrido. "
        "Usa este orden: explicar/responder, resumen sencillo y ofrecer temas relacionados. "
        "No uses tablas, usa **listas**."
    )
    
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Limpieza de historial para evitar Error 400 en Groq
    for turno in historial:
        role = "user" if turno.get("role") == "user" else "assistant"
        mensajes_ia.append({"role": role, "content": turno.get("content")})

    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = groq_client.chat.completions.create(
            model=MODELO_OSS,
            messages=mensajes_ia,
            temperature=0.6,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA ERROR**: {str(e)}"

# 3. Interfaz Estructurada Estilo ChatGPT
with gr.Blocks(fill_height=True) as demo:
    gr.Markdown("<h1 style='text-align: center; margin-top: 5vh;'>ADIA</h1>")
    
    chatbot = gr.Chatbot(
        elem_id="chatbot",
        show_label=False,
        bubble_full_width=False,
        type="messages",
        render=False # Lo renderizamos dentro del Interface
    )
    
    gr.ChatInterface(
        fn=adia_cerebro,
        chatbot=chatbot,
        textbox=gr.Textbox(
            placeholder="Escribe un mensaje...",
            container=True,
            elem_id="input-box"
        ),
        type="messages"
    )

# 4. Lanzamiento
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=PORT,
        css=chatgpt_css
    )
