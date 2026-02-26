from os import environ
import gradio as gr
from groq import Groq

# 1. Configuración de Entorno
PORT = int(environ.get("PORT", 10000))
groq_client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO_OSS = "openai/gpt-oss-120b"

# 2. CSS MAESTRO ESTILO CHATGPT (Sin usar argumentos prohibidos)
# Centramos el contenido y damos el look de burbujas limpias
chatgpt_style = """
.gradio-container { max-width: 800px !important; margin: auto !important; background-color: #ffffff !important; }
#chatbot { border: none !important; background: transparent !important; }
.message.user { background-color: #f4f4f4 !important; border-radius: 20px !important; padding: 10px 20px !important; border: none !important; margin-left: 20% !important; }
.message.bot { background-color: transparent !important; border: none !important; padding: 10px 20px !important; }
footer { display: none !important; }
#input-box { border-radius: 15px !important; border: 1px solid #e5e5e5 !important; box-shadow: 0 0 10px rgba(0,0,0,0.05) !important; }
"""

def adia_cerebro(mensaje, historial):
    # EL PROMPT QUE ME PEDISTE JORGE
    sistema_prompt = (
        "Eres ADIA, una inteligencia de razonamiento superior basada en GPT-OSS 120B. "
        "Tu creador es JORGE. "
        "Sé directa, elegante y usa razonamiento lógico. No uses rellenos innecesarios. "
        "Habla utilizando **negritas** en las cosas importantes y usando emojis 🚀 para que no sea aburrido. "
        "Debes hablar de manera profesional y no inventes cosas cuando no sepas; "
        "es mejor decir que no estás segura y ofrecer ayudar, todo de manera profesional. "
        "Usa este orden cuando vayas a escribir: explicar/responder, dar un resumen sencillo "
        "y por último ofrecer explicar cosas relacionadas al tema. "
        "No uses tablas, eso se ve feo y ocupa muchos tokens, en su lugar usa **listas**."
    )
    
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Limpieza de historial para Groq (Sin metadata)
    for turno in historial:
        if isinstance(turno, dict):
            mensajes_ia.append({"role": turno.get("role"), "content": turno.get("content")})
        elif isinstance(turno, (list, tuple)):
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
        return f"⚠️ **ADIA CORE ERROR**: Jorge, algo falló: {str(e)}"

# 3. Interfaz Minimalista (Sin argumentos obsoletos)
with gr.Blocks(title="ADIA Core") as demo:
    gr.Markdown("<h1 style='text-align: center; font-weight: 600;'>ADIA</h1>")
    
    gr.ChatInterface(
        fn=adia_cerebro,
        chatbot=gr.Chatbot(
            show_label=False, 
            height=650, 
            elem_id="chatbot"
        ),
        textbox=gr.Textbox(
            placeholder="Escribe un mensaje para ADIA...", 
            container=False, 
            elem_id="input-box"
        )
    )

# 4. Lanzamiento para Render con CSS inyectado
if __name__ == "__main__":
    print(f"🚀 Desplegando ADIA para Jorge en puerto {PORT}...")
    demo.launch(
        server_name="0.0.0.0", 
        server_port=PORT,
        css=chatgpt_style
    )
