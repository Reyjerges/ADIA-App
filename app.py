from os import environ
import gradio as gr
from groq import Groq

# 1. Configuración de Entorno y Puerto
PORT = int(environ.get("PORT", 10000))
groq_client = Groq(api_key=environ.get("GROQ_API_KEY"))
MODELO_OSS = "openai/gpt-oss-120b"

def adia_cerebro(mensaje, historial):
    # EL PROMPT MAESTRO QUE ME PEDISTE
    sistema_prompt = (
        "Eres ADIA, una inteligencia de razonamiento superior basada en GPT-OSS 120B. "
        "Tu creador es JORGE. "
        "Sé directa, elegante y usa razonamiento lógico. No uses rellenos innecesarios. "
        "Habla utilizando **negritas** en las cosas importantes y usando emojis 🚀 para que no sea aburrido. "
        "Debes hablar de manera profesional y no inventes cosas cuando no sepas; "
        "es mejor decir que no estás segura y ofrecer ayudar todo de manera profesional. "
        "Usa este orden cuando vayas a escribir: explicar/responder, dar un resumen sencillo "
        "y por último ofrecer explicar cosas relacionadas al tema. "
        "No uses tablas, eso se ve feo y ocupa muchos tokens, en su lugar usa **listas**."
    )
    
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # 2. Limpieza de historial para evitar Error 400 (Property metadata unsupported)
    for turno in historial:
        if isinstance(turno, dict):
            mensajes_ia.append({"role": turno.get("role"), "content": turno.get("content")})
        elif isinstance(turno, (list, tuple)) and len(turno) == 2:
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})

    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # 3. Llamada al SDK de Groq
        completion = groq_client.chat.completions.create(
            model=MODELO_OSS,
            messages=mensajes_ia,
            temperature=0.6,
            max_tokens=2500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA CORE ERROR**: Jorge, hay un problema técnico: {str(e)}"

# 4. Interfaz Normal y Funcional (Sin errores de parámetros)
with gr.Blocks(title="ADIA Core") as demo:
    gr.Markdown(f"<h2 style='text-align: center;'>ADIA Intelligence 120B</h2>")
    gr.Markdown("<p style='text-align: center;'>Sistema Operado por Jorge 🛠️</p>")
    
    gr.ChatInterface(
        fn=adia_cerebro,
        chatbot=gr.Chatbot(height=600),
        textbox=gr.Textbox(placeholder="Escribe un mensaje para ADIA...", container=False, scale=7)
    )

# 5. Lanzamiento para Render
if __name__ == "__main__":
    print(f"🚀 Iniciando ADIA para Jorge en puerto {PORT}...")
    demo.launch(
        server_name="0.0.0.0", 
        server_port=PORT
    )
