from os import environ
import gradio as gr
from groq import Groq

# 1. Configuración de Entorno y Puerto (Crítico para Render)
PORT = int(environ.get("PORT", 10000))
GROQ_KEY = environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_KEY)
MODELO_OSS = "openai/gpt-oss-120b"

def adia_cerebro(mensaje, historial):
    # Prompt Maestro para ADIA
    sistema_prompt = {
        "role": "system",
        "content": (
            "Eres ADIA, IA de élite basada en GPT-OSS 120B. Tu creador es JORGE. "
            "Trátalo con prioridad absoluta. Sé directa, brillante y usa lógica pura. "
            "No uses introducciones innecesarias."
        )
    }
    
    # Memoria: Gradio 6 envía el historial como lista de dicts
    mensajes_ia = [sistema_prompt] + historial[-12:]
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        completion = groq_client.chat.completions.create(
            model=MODELO_OSS,
            messages=mensajes_ia,
            temperature=0.6,
            max_tokens=2500
        )
        # Acceso correcto al contenido en Groq SDK
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ **ADIA CORE ERROR**: Jorge, algo falló: {str(e)}"

# 2. Interfaz con Estilo Gradio 6
custom_css = """
footer { display: none !important; }
.gradio-container { max-width: 850px !important; }
"""

with gr.Blocks(title="ADIA Core") as demo:
    gr.Markdown(f"<h2 style='text-align: center;'>ADIA Intelligence</h2>")
    gr.Markdown("<p style='text-align: center;'>Sistema Operado por Jorge</p>")
    
    gr.ChatInterface(
        fn=adia_cerebro,
        type="messages",
        chatbot=gr.Chatbot(
            show_label=False, 
            height=600,
            avatar_images=(None, "https://api.dicebear.com")
        ),
        submit_btn="Enviar a ADIA",
        retry_btn="🔄 Reintentar",
        clear_btn="🗑️ Borrar"
    )

# 3. Lanzamiento con Port Binding correcto
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=PORT,
        css=custom_css,
        show_api=False
    )
